"""Development-only engineering canary for independent experiment 05.

The canary exercises the frozen reconstruction and score paths on DIV2K 0805
and 0806. It is structurally unable to accept the sealed TESTIMAGES source IDs.
PatchErrorNet fitting, calibration fitting, and independent inference are later
stage-05C/05D actions and are intentionally absent here.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import PIL
from PIL import Image, features
import torch
import torchvision


B01 = None
L02 = None
J04 = None

CANARY_SOURCE_IDS = ("0805", "0806")
CANARY_CHAIN_IDS = ("q8_b16_n2", "j75_b16_n2")
PRIMARY_METHODS = (
    "observed",
    "gradient_nominal",
    "dpir_nominal",
    "fbcnn",
    "fbcnn_gradient_nominal",
    "fbcnn_dpir_nominal",
)
SCORE_RENAMES = {
    "measurement_residual": "original_measurement_residual",
    "image_gradient": "reconstruction_gradient",
    "random_expected": "expected_random",
}
EXPECTED_OPERATIONAL_SCORES = (
    "operator_spread_detail",
    "operator_spread_rgb",
    "image_transform_spread_detail",
    "original_measurement_residual",
    "reconstruction_gradient",
    "trained_image_only_patcherrornet_ensemble",
)
EXPECTED_EVALUATION_ONLY_SCORES = (
    "expected_random",
    "oracle_detail_error",
)


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_array(array):
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def dump_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def derive_config(protocol):
    simulation = protocol["simulation"]
    settings = protocol["fixed_reconstruction_settings"]
    scores = protocol["selection_scores"]
    return {
        "experiment": "independent_05_engineering_canary",
        "role": "development_only",
        "source_ids": list(CANARY_SOURCE_IDS),
        "chain_ids": list(CANARY_CHAIN_IDS),
        "seed": simulation["seed"],
        "crop_size": simulation["crop_size"],
        "context_border": simulation["context_border"],
        "nominal_sigma": simulation["nominal_blur_sigma"],
        "nominal_noise_std": simulation["nominal_noise_std"],
        "gradient_lambda": settings["gradient_lambda"],
        "iterations": settings["dpir_iterations"],
        "model_sigma_start_255": settings["model_sigma_start_255"],
        "model_sigma_end_255": settings["model_sigma_end_255"],
        "prior_tradeoff": settings["prior_tradeoff"],
        "periodic_x8": settings["periodic_x8"],
        "operator_sigmas": scores["operator_sigmas"],
        "outer_rotations": scores["outer_rotations_quarter_turns"],
        "patch_size": scores["patch_size"],
        "coverages": scores["coverages"],
        "detail_blur_sigma": 1.0,
        "detail_rmse_tolerances": scores["detail_rmse_tolerances"],
        "jpeg_subsampling": simulation["jpeg_subsampling"],
        "jpeg_optimize": simulation["jpeg_optimize"],
        "cpu_threads": 4,
        "test_inference_authorized": False,
    }


def validate_canary_scope(protocol, config):
    assert protocol["independent_test_run_authorized"] is False
    assert protocol["test_results_inspected"] is False
    assert tuple(config["source_ids"]) == CANARY_SOURCE_IDS
    assert tuple(config["chain_ids"]) == CANARY_CHAIN_IDS
    assert tuple(protocol["development_partitions"]["engineering_canary_sources"]) == CANARY_SOURCE_IDS
    frozen_chains = {row["id"]: row for row in protocol["simulation"]["acquisition_chains"]}
    assert set(config["chain_ids"]) <= set(frozen_chains)
    assert frozen_chains["q8_b16_n2"]["role"] == "uncompressed_negative_control"
    assert frozen_chains["j75_b16_n2"]["role"] == "primary_anchor"
    return [frozen_chains[chain_id] for chain_id in config["chain_ids"]]


def _receipt_development_map(receipt):
    return {row["source_id"]: row for row in receipt["development_archive"]["sources"]}


def load_canary_sources(data_dir, receipt, config):
    data_dir = Path(data_dir)
    assert tuple(config["source_ids"]) == CANARY_SOURCE_IDS
    receipt_map = _receipt_development_map(receipt)
    extent = config["crop_size"] + 2 * config["context_border"]
    records, sources = [], {}
    for source_id in config["source_ids"]:
        assert source_id.isdigit(), "canary accepts DIV2K numeric identifiers only"
        path = data_dir / f"{source_id}.png"
        assert path.is_file(), f"missing canary source: {path}"
        expected = receipt_map[source_id]
        assert sha256_file(path) == expected["sha256"], f"changed source bytes: {source_id}"
        with Image.open(path) as image:
            image.load()
            assert image.format == "PNG" and image.mode == "RGB"
            width, height = image.size
            rgb = np.asarray(image, dtype=np.uint8)
        assert (width, height) == (expected["width"], expected["height"])
        assert min(width, height) >= extent
        left, top = (width - extent) // 2, (height - extent) // 2
        crop = rgb[top : top + extent, left : left + extent].astype(np.float64) / 255.0
        assert crop.shape == (extent, extent, 3)
        sources[source_id] = crop
        records.append(
            {
                "source_id": source_id,
                "filename": path.name,
                "file_sha256": expected["sha256"],
                "decoded_rgb_sha256": hashlib.sha256(rgb.tobytes()).hexdigest(),
                "width": width,
                "height": height,
                "crop_left": left,
                "crop_top": top,
                "crop_extent": extent,
                "role": "engineering_canary_only",
            }
        )
    return sources, pd.DataFrame(records)


def source_noise(source_id, shape, config):
    identity = int(hashlib.sha256(source_id.encode("utf-8")).hexdigest()[:8], 16)
    rng = np.random.default_rng(np.random.SeedSequence([config["seed"], identity]))
    return rng.standard_normal(shape)


def acquire(reference, source_id, chain, config):
    noise = source_noise(source_id, reference.shape, config)
    linear = B01.apply(reference, chain["true_blur_sigma"]) + chain["noise_std"] * noise
    integers = np.rint(np.clip(linear, 0, 1) * 255.0).astype(np.uint8)
    jpeg_payload = b""
    if chain["codec"] == "quantized_8bit":
        observation = integers.astype(np.float64) / 255.0
    elif chain["codec"] == "jpeg":
        stream = io.BytesIO()
        Image.fromarray(integers, mode="RGB").save(
            stream,
            format="JPEG",
            quality=chain["jpeg_quality"],
            subsampling=config["jpeg_subsampling"],
            optimize=config["jpeg_optimize"],
        )
        jpeg_payload = stream.getvalue()
        with Image.open(io.BytesIO(jpeg_payload)) as decoded:
            observation = np.asarray(decoded.convert("RGB"), dtype=np.float64) / 255.0
    else:
        raise ValueError(f"unsupported frozen codec: {chain['codec']}")
    assert observation.shape == reference.shape and observation.dtype == np.float64
    assert np.isfinite(observation).all() and 0 <= observation.min() <= observation.max() <= 1
    metadata = {
        "source_id": source_id,
        "chain_id": chain["id"],
        "true_blur_sigma": chain["true_blur_sigma"],
        "noise_std": chain["noise_std"],
        "codec": chain["codec"],
        "jpeg_quality": chain["jpeg_quality"],
        "observation_sha256": sha256_array(observation),
        "observation_minimum": float(observation.min()),
        "observation_maximum": float(observation.max()),
        "jpeg_byte_count": len(jpeg_payload),
        "jpeg_sha256": hashlib.sha256(jpeg_payload).hexdigest() if jpeg_payload else "",
    }
    return observation, jpeg_payload, metadata


def verify_acquisition_determinism(sources, chains, config):
    rows = []
    for source_id, reference in sources.items():
        expected_noise = source_noise(source_id, reference.shape, config)
        repeated_noise = source_noise(source_id, reference.shape, config)
        assert np.array_equal(expected_noise, repeated_noise)
        for chain in chains:
            first, first_jpeg, first_meta = acquire(reference, source_id, chain, config)
            second, second_jpeg, second_meta = acquire(reference, source_id, chain, config)
            assert np.array_equal(first, second)
            assert first_jpeg == second_jpeg
            assert first_meta == second_meta
            rows.append(
                {
                    "source_id": source_id,
                    "chain_id": chain["id"],
                    "repeat_identical": True,
                    "observation_sha256": first_meta["observation_sha256"],
                    "jpeg_sha256": first_meta["jpeg_sha256"],
                }
            )
    return pd.DataFrame(rows)


class PatchErrorNet(torch.nn.Module):
    """Frozen six-channel ResNet-18 scalar-logit architecture."""

    def __init__(self):
        super().__init__()
        network = torchvision.models.resnet18(weights=None)
        network.conv1 = torch.nn.Conv2d(6, 64, kernel_size=7, stride=2, padding=3, bias=False)
        network.fc = torch.nn.Linear(network.fc.in_features, 1)
        self.network = network

    def forward(self, observation_and_reconstruction):
        assert observation_and_reconstruction.ndim == 4
        assert observation_and_reconstruction.shape[1] == 6
        return self.network(observation_and_reconstruction).reshape(-1)


def validate_patcherrornet_architecture(device):
    torch.manual_seed(2026092101)
    model = PatchErrorNet().to(device).eval()
    sample = torch.linspace(0, 1, 2 * 6 * 64 * 64, device=device).reshape(2, 6, 64, 64)
    with torch.inference_mode():
        first = model(sample)
        second = model(sample)
    assert first.shape == (2,) and bool(first.isfinite().all()) and torch.equal(first, second)
    return {
        "architecture": "ResNet-18",
        "input_channels": 6,
        "output_logits": 1,
        "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        "repeat_identical": True,
        "fit_performed": False,
        "calibration_performed": False,
    }


def _error_rows(reference, estimates, source_id, chain_id, config):
    rows = []
    for method in PRIMARY_METHODS:
        metrics, rgb_patch, detail_patch = _errors(reference, estimates[method], config)
        rows.append({"source_id": source_id, "chain_id": chain_id, "method": method, **metrics})
        estimates[f"{method}__rgb_patch_error"] = rgb_patch
        estimates[f"{method}__detail_patch_error"] = detail_patch
    return rows


def _errors(reference, estimate, config):
    inside = lambda value: B01.interior(value, config)
    rgb_error = np.mean((inside(estimate) - inside(reference)) ** 2, axis=-1)
    detail_difference = inside(L02.detail(estimate, config) - L02.detail(reference, config))
    detail_error = np.mean(detail_difference**2, axis=-1)
    rgb_patch = B01.patch_mean(rgb_error, config["patch_size"]).ravel()
    detail_patch = B01.patch_mean(detail_error, config["patch_size"]).ravel()
    metrics = {
        "mse": float(rgb_error.mean()),
        "psnr_db": B01.psnr(float(rgb_error.mean())),
        "detail_mse": float(detail_error.mean()),
    }
    for tolerance in config["detail_rmse_tolerances"]:
        metrics[f"bad_detail_rate_{tolerance:g}"] = float((np.sqrt(detail_patch) > tolerance).mean())
    return metrics, rgb_patch, detail_patch


def _reconstruct_observation(observation, fbcnn, drunet, device, config):
    estimates = {"observed": observation}
    compute_rows, traces, fbcnn_rows = [], [], []

    start = time.perf_counter()
    estimates["gradient_nominal"] = B01.inverse_spectrum(
        np.fft.fft2(observation, axes=(0, 1)),
        config["nominal_sigma"],
        "gradient",
        config["gradient_lambda"],
    )
    compute_rows.append(
        {"component": "gradient_nominal", "elapsed_seconds": time.perf_counter() - start, "denoiser_calls": 0, "fbcnn_calls": 0}
    )

    fbcnn_inputs = {}
    for rotation in config["outer_rotations"]:
        restored, timing, diagnostics = J04.deblock(np.rot90(observation, rotation).copy(), fbcnn, device)
        restored = np.rot90(restored, -rotation).copy()
        fbcnn_inputs[rotation] = restored
        component = "fbcnn" if rotation == 0 else f"fbcnn_rot{rotation * 90}"
        compute_rows.append({"component": component, **timing})
        fbcnn_rows.append({"rotation_quarter_turns": rotation, **diagnostics})
    estimates["fbcnn"] = fbcnn_inputs[0]

    start = time.perf_counter()
    estimates["fbcnn_gradient_nominal"] = B01.inverse_spectrum(
        np.fft.fft2(estimates["fbcnn"], axes=(0, 1)),
        config["nominal_sigma"],
        "gradient",
        config["gradient_lambda"],
    )
    compute_rows.append(
        {
            "component": "fbcnn_gradient_nominal_inverse_only",
            "elapsed_seconds": time.perf_counter() - start,
            "denoiser_calls": 0,
            "fbcnn_calls": 0,
        }
    )

    variants = (
        ("nominal", 1.0, 0),
        ("sigma08", 0.8, 0),
        ("sigma12", 1.2, 0),
        ("rot90", 1.0, 1),
        ("rot180", 1.0, 2),
    )
    variant_outputs = {}
    for pipeline in ("dpir_nominal", "fbcnn_dpir_nominal"):
        for variant, blur_sigma, rotation in variants:
            if pipeline == "dpir_nominal":
                model_input = np.rot90(observation, rotation).copy()
            else:
                model_input = np.rot90(fbcnn_inputs[rotation], rotation).copy() if rotation else fbcnn_inputs[0]
            restored, timing, trace = L02.reconstruct(model_input, blur_sigma, drunet, device, config)
            restored = np.rot90(restored, -rotation).copy()
            key = pipeline if variant == "nominal" else f"{pipeline}__{variant}"
            variant_outputs[key] = restored
            compute_rows.append({"component": key, **timing, "fbcnn_calls": 0})
            traces.extend({"component": key, **row} for row in trace)
    estimates["dpir_nominal"] = variant_outputs["dpir_nominal"]
    estimates["fbcnn_dpir_nominal"] = variant_outputs["fbcnn_dpir_nominal"]
    estimates.update(variant_outputs)
    return estimates, compute_rows, traces, fbcnn_rows


def _score_rows(reference, observation, estimates, config):
    rows = []
    arrays = {}
    for pipeline in ("dpir_nominal", "fbcnn_dpir_nominal"):
        operators = [
            estimates[f"{pipeline}__sigma08"],
            estimates[pipeline],
            estimates[f"{pipeline}__sigma12"],
        ]
        transforms = [
            estimates[pipeline],
            estimates[f"{pipeline}__rot90"],
            estimates[f"{pipeline}__rot180"],
        ]
        frame, score_arrays = L02.evaluate_scores(
            reference, estimates[pipeline], observation, operators, transforms, config
        )
        frame["score"] = frame["score"].replace(SCORE_RENAMES)
        frame.insert(0, "pipeline", pipeline)
        rows.extend(frame.to_dict("records"))
        arrays.update({f"{pipeline}__score__{SCORE_RENAMES.get(name, name)}": value for name, value in score_arrays.items()})
    return rows, arrays


def _snapshot(output_dir, frames, payloads, state, error=None):
    output_dir = Path(output_dir)
    for name, frame in frames.items():
        frame.to_csv(output_dir / f"{name}.csv", index=False)
    for name, payload in payloads.items():
        dump_json(output_dir / f"{name}.json", payload)
    status = {
        "status": state,
        "stage": "05C_development_canary",
        "source_ids": list(CANARY_SOURCE_IDS),
        "chain_ids": list(CANARY_CHAIN_IDS),
        "test_inference_performed": False,
        "test_performance_inspected": False,
        "independent_test_run_authorized": False,
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    if error is not None:
        status["error"] = str(error)
    dump_json(output_dir / "status.json", status)


def run_canary(data_dir, output_dir, protocol, receipt, provenance, vendor_dirs, dpir_weights, fbcnn_weights):
    output_dir = Path(output_dir)
    assert not output_dir.exists(), f"existing output preserved: {output_dir}"
    output_dir.mkdir(parents=True)
    (output_dir / "predictions").mkdir()
    (output_dir / "codec_inputs").mkdir()

    config = derive_config(protocol)
    chains = validate_canary_scope(protocol, config)
    assert provenance["experiment"] == "independent_05"
    assert provenance["stage"] == "05C_development_canary"
    assert provenance["role"] == "development_only"
    frames = {}
    payloads = {"config": config, "provenance": provenance}
    _snapshot(output_dir, frames, payloads, "initializing")

    try:
        sources, frames["source_manifest"] = load_canary_sources(data_dir, receipt, config)
        frames["acquisition_repeat_check"] = verify_acquisition_determinism(sources, chains, config)
        assert not any(row["source_id"] in {x["source_id"] for x in receipt["test_archive"]["sources"]} for row in frames["source_manifest"].to_dict("records"))

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        assert device.type == "cuda", "full canary requires a CUDA GPU; use the notebook preflight locally"
        L02.download_weights(dpir_weights, provenance["dpir"])
        drunet, device = L02.load_model(vendor_dirs["dpir"], dpir_weights, provenance["dpir"], config)
        dpir_checks = L02.validate_adapter(drunet, device, vendor_dirs["dpir"], config)
        fbcnn, fbcnn_parameters = J04.load_fbcnn(
            vendor_dirs["fbcnn"], fbcnn_weights, provenance["fbcnn"], device
        )
        fbcnn_checks = J04.validate_fbcnn(fbcnn, device)
        comparator_checks = validate_patcherrornet_architecture(device)
        payloads["checks"] = {
            "scope_guard_passed": True,
            "acquisition_repeat_checks": len(frames["acquisition_repeat_check"]),
            "dpir": dpir_checks,
            "fbcnn": {**fbcnn_checks, "parameter_count": fbcnn_parameters},
            "patcherrornet": comparator_checks,
        }
        payloads["environment"] = {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "pillow": PIL.__version__,
            "torch": str(torch.__version__),
            "torchvision": str(torchvision.__version__),
            "jpeg_codec": features.version_codec("jpg"),
            "libjpeg_turbo": features.version_feature("libjpeg_turbo"),
            "device": str(device),
            "cuda_name": torch.cuda.get_device_name(device),
        }
        _snapshot(output_dir, frames, payloads, "running")

        acquisition_rows, quality_rows, risk_rows = [], [], []
        compute_rows, trace_rows, fbcnn_rows = [], [], []
        for source_id, reference in sources.items():
            for chain in chains:
                observation, jpeg_payload, acquisition = acquire(reference, source_id, chain, config)
                acquisition_rows.append(acquisition)
                if jpeg_payload:
                    (output_dir / "codec_inputs" / f"{source_id}_{chain['id']}.jpg").write_bytes(jpeg_payload)
                estimates, local_compute, local_traces, local_fbcnn = _reconstruct_observation(
                    observation, fbcnn, drunet, device, config
                )
                quality_rows.extend(_error_rows(reference, estimates, source_id, chain["id"], config))
                local_risk, score_arrays = _score_rows(reference, observation, estimates, config)
                risk_rows.extend({"source_id": source_id, "chain_id": chain["id"], **row} for row in local_risk)
                compute_rows.extend({"source_id": source_id, "chain_id": chain["id"], **row} for row in local_compute)
                trace_rows.extend({"source_id": source_id, "chain_id": chain["id"], **row} for row in local_traces)
                fbcnn_rows.extend({"source_id": source_id, "chain_id": chain["id"], **row} for row in local_fbcnn)
                arrays = {"reference": reference, "supplied_observation": observation, **estimates, **score_arrays}
                np.savez_compressed(output_dir / "predictions" / f"{source_id}_{chain['id']}.npz", **arrays)

                frames.update(
                    acquisition=pd.DataFrame(acquisition_rows),
                    quality=pd.DataFrame(quality_rows),
                    risk=pd.DataFrame(risk_rows),
                    compute=pd.DataFrame(compute_rows),
                    trajectories=pd.DataFrame(trace_rows),
                    fbcnn_diagnostics=pd.DataFrame(fbcnn_rows),
                )
                _snapshot(output_dir, frames, payloads, "running")

        observations = len(CANARY_SOURCE_IDS) * len(CANARY_CHAIN_IDS)
        assert len(frames["acquisition"]) == observations
        assert len(frames["quality"]) == observations * len(PRIMARY_METHODS)
        assert not frames["quality"].duplicated(["source_id", "chain_id", "method"]).any()
        assert not frames["risk"].duplicated(
            ["source_id", "chain_id", "pipeline", "region", "score", "coverage"]
        ).any()
        expected_untrained = set(EXPECTED_OPERATIONAL_SCORES) - {"trained_image_only_patcherrornet_ensemble"}
        expected_scores = expected_untrained | set(EXPECTED_EVALUATION_ONLY_SCORES)
        assert set(frames["risk"].score) == expected_scores
        assert int(frames["compute"].denoiser_calls.sum()) == observations * 80
        assert int(frames["compute"].fbcnn_calls.sum()) == observations * 3
        payloads["checks"].update(
            observations=observations,
            quality_rows=len(frames["quality"]),
            risk_rows=len(frames["risk"]),
            drunet_experiment_calls=observations * 80,
            fbcnn_experiment_calls=observations * 3,
            reconstruction_and_untrained_score_paths_passed=True,
            patcherrornet_fit_performed=False,
            calibration_fit_performed=False,
            test_inference_performed=False,
        )
        _snapshot(output_dir, frames, payloads, "passed_development_canary")
        manifest = []
        for path in sorted(output_dir.rglob("*")):
            if path.is_file() and path.name != "export_manifest.json":
                manifest.append(
                    {
                        "path": str(path.relative_to(output_dir)),
                        "byte_count": path.stat().st_size,
                        "sha256": sha256_file(path),
                    }
                )
        dump_json(
            output_dir / "export_manifest.json",
            {
                "experiment_id": "independent_05",
                "stage": "05C_development_canary",
                "role": "development_only",
                "test_inference_performed": False,
                "files": manifest,
            },
        )
        return {"frames": frames, "payloads": payloads, "output_dir": output_dir}
    except Exception as error:
        _snapshot(output_dir, frames, payloads, "failed", error)
        raise
