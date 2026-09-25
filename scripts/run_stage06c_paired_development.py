#!/usr/bin/env python3
"""Stage 06C development-only paired DPIR/DiffPIR reconstruction.

Reads only 06B-audited development-fit or early-stop RAISE NEFs. This is an
unfrozen development runner; no independent or pilot inference is possible.
The supplied image is the same for both solvers in each method arm.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import numpy as np

from smoke_stage06c_raise_chains import authorize_inputs, decode_verified, sha256_file

ROOT = Path(__file__).resolve().parents[1]
DIFFPIR_COMMIT = "2a9898129a1b274131b98746e5b364bc20adc1e1"
DIFFPIR_MODEL = "256x256_diffusion_uncond.pt"
MODEL_URL = "https://openaipublic.blob.core.windows.net/diffusion/jul-2021/256x256_diffusion_uncond.pt"
STAGE05_NOTEBOOK = ROOT / "notebooks/04_DIV2K_JPEG_Aware_Baseline.ipynb"
CHAINS = ("srgb_j75_b16_n2", "linear_j75_b16_n2")
METHODS = ("nominal", "chain_aware")
SOLVERS = ("DPIR", "DiffPIR")


def ensure_diffpir_source(path: Path) -> str:
    if not (path / "guided_diffusion/script_util.py").is_file():
        raise FileNotFoundError(f"Missing DiffPIR checkout: {path}")
    actual = subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
    if actual != DIFFPIR_COMMIT:
        raise ValueError(f"DiffPIR source is not the reviewed commit: {actual}")
    if subprocess.check_output(["git", "-C", str(path), "status", "--porcelain"], text=True).strip():
        raise ValueError("DiffPIR checkout has uncommitted modifications")
    return actual


def check_inputs(args: argparse.Namespace) -> tuple[list[dict[str, str]], str]:
    names = args.source_ids
    if not names or len(names) != len(set(names)):
        raise ValueError("Supply distinct development source IDs explicitly")
    paths = [args.nef_dir / f"{source_id}.NEF" for source_id in names]
    return authorize_inputs(paths, args.eligible_manifest, args.audit_csv)


def load_stage05_components(cache: Path, device):
    """Reuse the SHA-checked Stage 05 implementation, never its test outputs."""
    import torch

    nb = json.loads(STAGE05_NOTEBOOK.read_text(encoding="utf-8"))
    namespace = {"__name__": "stage06c_stage05_component_import"}
    source = "".join(nb["cells"][1]["source"])
    exec(compile(source, str(STAGE05_NOTEBOOK), "exec"), namespace)
    provenance, vendors = namespace["PROVENANCE"], namespace["VENDORS"]
    B01, L02, J04 = (namespace[key] for key in ("B01", "L02", "J04"))
    settings = dict(seed=20260925, cpu_threads=4, nominal_noise_std=2 / 255,
                    iterations=8, model_sigma_start_255=49, model_sigma_end_255=2,
                    prior_tradeoff=0.23, periodic_x8=True, outer_rotations=(0,))
    for key in ("dpir", "fbcnn"):
        destination = cache / f"{key}_{provenance[key]['upstream_commit'][:7]}"
        for relative, vendor_source in vendors[key].items():
            path = destination / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_bytes(vendor_source.encode())
            if sha256_file(path) != provenance[key]["files"][relative]:
                raise ValueError(f"Pinned {key} source changed: {relative}")
    dpir_weights, fbcnn_weights = cache / "drunet_color.pth", cache / "fbcnn_color.pth"
    for key, path in (("dpir", dpir_weights), ("fbcnn", fbcnn_weights)):
        if not path.is_file() or sha256_file(path) != provenance[key]["weight_sha256"]:
            raise ValueError(f"Missing or unverified {key} weights: {path}")
    dpir, actual_device = L02.load_model(cache / f"dpir_{provenance['dpir']['upstream_commit'][:7]}",
                                         dpir_weights, provenance["dpir"], settings)
    assert actual_device == device
    fbcnn, _ = J04.load_fbcnn(cache / f"fbcnn_{provenance['fbcnn']['upstream_commit'][:7]}",
                              fbcnn_weights, provenance["fbcnn"], device)
    return B01, L02, J04, dpir, fbcnn, settings, provenance


def load_diffpir(root: Path, checkpoint: Path, device):
    import torch

    if checkpoint.name != DIFFPIR_MODEL:
        raise ValueError("The selected DiffPIR weight is not the ImageNet 256px model")
    sys.path.insert(0, str(root))
    from guided_diffusion.script_util import (  # type: ignore
        args_to_dict, create_model_and_diffusion, model_and_diffusion_defaults,
    )
    from utils import utils_model  # type: ignore

    config = dict(model_path=str(checkpoint), num_channels=256, num_res_blocks=2,
                  attention_resolutions="8,16,32")
    parsed = utils_model.create_argparser(config).parse_args([])
    network, diffusion = create_model_and_diffusion(
        **args_to_dict(parsed, model_and_diffusion_defaults().keys()))
    weights = torch.load(checkpoint, map_location="cpu", weights_only=True)
    if not isinstance(weights, dict) or not weights:
        raise ValueError("DiffPIR checkpoint did not contain a model state dictionary")
    network.load_state_dict(weights, strict=True)
    network.eval().requires_grad_(False).to(device)
    return network, diffusion


def diffpir_reconstruct(observation: np.ndarray, blur_sigma: float, bundle, seed: int,
                        nfe: int, noise_std: float = 2 / 255,
                        lam: float = 1.0, zeta: float = 0.1) -> np.ndarray:
    """Upstream DiffPIR deblur loop with the *same* Gaussian transfer as DPIR.

    The data step uses the exact Stage 05 periodic Fourier transfer, rather
    than DiffPIR demo's separately sampled 61x61 Gaussian PSF.
    """
    import torch

    network, diffusion, B01 = bundle
    if nfe < 2 or nfe > 100 or not 0 <= zeta <= 1:
        raise ValueError("Development NFE must be 2..100 and zeta in [0,1]")
    device = next(network.parameters()).device
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    beta = torch.linspace(0.0001, 0.02, 1000, dtype=torch.float32, device=device)
    alpha_bar = torch.cumprod(1 - beta, dim=0)
    a = torch.sqrt(alpha_bar)
    b = torch.sqrt(1 - alpha_bar)
    reduced = b / a
    y = torch.as_tensor(np.ascontiguousarray(observation.transpose(2, 0, 1)),
                        dtype=torch.float32, device=device).unsqueeze(0)
    transfer = torch.as_tensor(B01.transfer(observation.shape[:2], blur_sigma),
                               dtype=torch.float32, device=device)[None, None]
    fy = torch.fft.fft2(y)
    ty = int(torch.argmin(torch.abs(reduced - 2 * noise_std)).item())
    start = 999
    effective = a[start] / a[ty]
    variance = (b[start] ** 2 - effective ** 2 * b[ty] ** 2).clamp(min=0)
    x = effective * (2 * y - 1) + torch.sqrt(variance) * torch.randn_like(y)
    seq = np.sqrt(np.linspace(0, 1000**2, nfe)).astype(int).tolist()
    seq[-1] = 999
    with torch.inference_mode():
        for index, slot in enumerate(seq):
            # Reverse-step mapping follows upstream sigmas[i]=reduced[999-i].
            # Use the explicit timestep to keep the schedule on GPU; the
            # upstream helper converts its schedule through np.asarray.
            ti = 999 - slot
            timestep = torch.full((x.shape[0],), ti, dtype=torch.long, device=device)
            x0 = diffusion.p_sample(network, x, timestep, clip_denoised=True,
                    denoised_fn=None, cond_fn=None, model_kwargs={})["pred_xstart"]
            if index < len(seq) - 1:
                rho = lam * noise_std**2 / float(reduced[ti] ** 2)
                candidate = (x0 + 1) / 2
                solved = torch.fft.ifft2(
                    (transfer.conj() * fy + rho * torch.fft.fft2(candidate)) /
                    (transfer.abs().square() + rho)).real
                x0 = x0 + (solved * 2 - 1 - x0)  # upstream guidance_scale = 1
                next_t = 999 - seq[index + 1]
                eps = (x - a[ti] * x0) / b[ti]
                x = a[next_t] * x0 + b[next_t] * (
                    np.sqrt(1 - zeta) * eps + np.sqrt(zeta) * torch.randn_like(x))
            else:
                x = x0
    result = ((x / 2 + 0.5).clamp(0, 1)[0].permute(1, 2, 0).cpu().numpy())
    if result.shape != observation.shape or not np.isfinite(result).all():
        raise ValueError("DiffPIR returned a malformed reconstruction")
    return result.astype(np.float64)


def acquire(reference: np.ndarray, chain: str, seed: int, B01) -> np.ndarray:
    """Periodic forward blur matches the Fourier likelihood in both inverses."""
    from experiments.stage06.acquisition_chains import jpeg_roundtrip, linear_to_srgb, srgb_to_linear

    working = srgb_to_linear(reference) if chain.startswith("linear_") else reference
    noise = np.random.default_rng(seed).standard_normal(reference.shape)
    degraded = np.clip(B01.apply(working, 1.6) + (2 / 255) * noise, 0, 1)
    encoded = linear_to_srgb(degraded) if chain.startswith("linear_") else degraded
    return jpeg_roundtrip(encoded, 75, 0)


def quality(reference: np.ndarray, reconstruction: np.ndarray, B01,
            margin: int = 32, patch: int = 16) -> tuple[dict, list[float]]:
    view = (slice(margin, -margin), slice(margin, -margin))
    truth, estimate = reference[view], reconstruction[view]
    detail_true = (reference - B01.apply(reference, 1.0))[view]
    detail_est = (reconstruction - B01.apply(reconstruction, 1.0))[view]
    sq = np.mean((detail_true - detail_est) ** 2, axis=2)
    n, m = sq.shape
    if n % patch or m % patch:
        raise ValueError("Interior dimensions must be multiples of the patch size")
    values = sq.reshape(n // patch, patch, m // patch, patch).mean(axis=(1, 3)).ravel()
    return ({"rgb_mse": float(np.mean((truth - estimate) ** 2)),
             "detail_mse": float(sq.mean()), "detail_rmse": float(np.sqrt(sq.mean())),
             "patches": int(values.size)}, values.tolist())


def store_json(path: Path, value: dict) -> None:
    tmp = path.with_name(path.name + ".partial")
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def run(args: argparse.Namespace, selected: list[dict[str, str]], audit_sha: str) -> None:
    import torch
    from experiments.stage06.acquisition_chains import linear_to_srgb, srgb_to_linear

    if not torch.cuda.is_available():
        raise RuntimeError("Stage 06C solver run requires a GPU runtime")
    commit = ensure_diffpir_source(args.diffpir_root)
    if not args.diffpir_checkpoint.is_file():
        raise FileNotFoundError(args.diffpir_checkpoint)
    weight_hash = sha256_file(args.diffpir_checkpoint)
    if args.checkpoint_sha256 and weight_hash != args.checkpoint_sha256:
        raise ValueError("DiffPIR checkpoint hash differs from the approved candidate")
    device = torch.device("cuda")
    B01, L02, J04, dpir, fbcnn, settings, provenance = load_stage05_components(args.model_cache, device)
    network, diffusion = load_diffpir(args.diffpir_root, args.diffpir_checkpoint, device)
    receipt = {"schema": "stage06c-paired-development-v1", "status": "running",
        "claim_scope": "development engineering only; not frozen or independent evidence",
        "source_ids": [s["source_id"] for s in selected], "roles": [s["role"] for s in selected],
        "eligible_manifest_sha256": sha256_file(args.eligible_manifest), "audit_sha256": audit_sha,
        "stage05_component_notebook_sha256": sha256_file(STAGE05_NOTEBOOK),
        "checkpoint_sha256": {"DiffPIR": weight_hash,
            "DPIR": provenance["dpir"]["weight_sha256"],
            "FBCNN": provenance["fbcnn"]["weight_sha256"]},
        "diffpir_commit": commit, "diffpir_checkpoint_source": MODEL_URL,
        "config": {"crop_size": 256, "margin": 32, "patch_size": 16,
                   "true_blur_sigma": 1.6, "nominal_blur_sigma": 1.0,
                   "noise_std": 2 / 255, "jpeg_quality": 75,
                   "chain_names": CHAINS, "methods": METHODS,
                   "dpir": settings, "diffpir_nfe": args.nfe,
                   "diffpir_lambda": args.diffpir_lambda, "diffpir_zeta": args.diffpir_zeta,
                   "base_seed": args.seed,
                   "forward_boundary": "periodic; Stage 05 Gaussian Fourier transfer"},
        "runtime": {"torch": torch.__version__, "numpy": np.__version__,
                    "cuda_device": torch.cuda.get_device_name(device)},
        "independent_test_inference": False, "completed": [], "failures": []}
    output = args.output_dir
    if output.exists():
        raise FileExistsError(f"Preserving existing experiment output: {output}")
    output.mkdir(parents=True)
    store_json(output / "status.json", receipt)
    rows = []
    try:
        for item in selected:
            rgb = decode_verified(Path(item["nef"]), item["decoded_rgb_sha256"])
            height, width = rgb.shape[:2]
            y0, x0 = (height - 256) // 2, (width - 256) // 2
            reference = rgb[y0:y0 + 256, x0:x0 + 256].astype(np.float64) / 255
            for chain in CHAINS:
                # Reuse the same noise field across both chains for this source.
                identity = int(hashlib.sha256(item["source_id"].encode()).hexdigest()[:8], 16)
                seed = args.seed + identity
                obs = acquire(reference, chain, seed, B01)
                deblocked, _, diag = J04.deblock(obs, fbcnn, device)
                for solver in SOLVERS:
                    for method in METHODS:
                        input_srgb = obs if method == "nominal" else deblocked
                        data = (srgb_to_linear(input_srgb) if chain.startswith("linear_") and method == "chain_aware"
                                else input_srgb)
                        started = time.perf_counter()
                        if solver == "DPIR":
                            estimate, _, _ = L02.reconstruct(data, 1.0, dpir, device, settings)
                        else:
                            estimate = diffpir_reconstruct(data, 1.0,
                                (network, diffusion, B01), seed,
                                args.nfe, lam=args.diffpir_lambda, zeta=args.diffpir_zeta)
                        if chain.startswith("linear_") and method == "chain_aware":
                            estimate = linear_to_srgb(estimate)
                        metrics, patch_values = quality(reference, estimate, B01)
                        rows.append({"source_id": item["source_id"], "role": item["role"],
                            "chain_id": chain, "solver": solver, "method": method,
                            "noise_seed": seed, "predicted_jpeg_degradation": diag["predicted_degradation"],
                            "observation_sha256": hashlib.sha256(np.ascontiguousarray(obs).tobytes()).hexdigest(),
                            "reconstruction_sha256": hashlib.sha256(np.ascontiguousarray(estimate).tobytes()).hexdigest(),
                            "elapsed_seconds": time.perf_counter() - started,
                            **metrics, "patch_detail_mse": patch_values})
                        receipt["completed"].append([item["source_id"], chain, solver, method])
                        store_json(output / "source_method_rows.json", {"rows": rows})
                        store_json(output / "status.json", receipt)
        receipt["status"] = "completed_development_only"
    except Exception as exc:
        receipt["status"] = "failed_development_run"
        receipt["failures"].append({"type": type(exc).__name__, "message": str(exc),
                                    "completed_rows": len(rows)})
        store_json(output / "status.json", receipt)
        raise
    receipt["source_method_rows_sha256"] = sha256_file(output / "source_method_rows.json")
    receipt["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    store_json(output / "status.json", receipt)
    print(json.dumps({"status": receipt["status"], "rows": len(rows),
                      "results": str(output), "diffpir_checkpoint_sha256": weight_hash}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("preflight", "run"), default="preflight")
    parser.add_argument("--source-ids", nargs="+", required=True)
    parser.add_argument("--nef-dir", required=True, type=Path)
    parser.add_argument("--audit-csv", required=True, type=Path)
    parser.add_argument("--eligible-manifest", type=Path, default=ROOT /
        "experiments/stage06/manifests/RAISE_1k_eligible_roles_v1_20260925.csv")
    parser.add_argument("--model-cache", type=Path)
    parser.add_argument("--diffpir-root", type=Path)
    parser.add_argument("--diffpir-checkpoint", type=Path)
    parser.add_argument("--checkpoint-sha256", default="")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--nfe", type=int, default=20)
    parser.add_argument("--diffpir-lambda", type=float, default=1.0)
    parser.add_argument("--diffpir-zeta", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=20260925)
    args = parser.parse_args()
    selected, audit_sha = check_inputs(args)
    if args.mode == "preflight":
        for row in selected:
            decode_verified(Path(row["nef"]), row["decoded_rgb_sha256"])
        print(json.dumps({"status": "preflight_passed", "source_ids": args.source_ids,
                          "roles": [x["role"] for x in selected], "audit_sha256": audit_sha,
                          "independent_test_inference": False}, indent=2))
        return
    for name in ("model_cache", "diffpir_root", "diffpir_checkpoint", "output_dir"):
        if getattr(args, name) is None:
            parser.error(f"--{name.replace('_', '-')} is required for --mode run")
    if args.nfe < 2 or args.nfe > 100 or args.diffpir_lambda <= 0 or not 0 <= args.diffpir_zeta <= 1:
        parser.error("Invalid development-only DiffPIR settings")
    run(args, selected, audit_sha)


if __name__ == "__main__":
    main()
