#!/usr/bin/env python3
"""Stage 06C acquisition-chain smoke test on audited RAISE development NEFs.

This is an engineering diagnostic. It neither runs a reconstruction solver nor
reads calibration, pilot, or independent-test sources.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from importlib import metadata
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from experiments.stage06.acquisition_chains import (  # noqa: E402
    STAGE06_DEVELOPMENT_CHAINS,
    simulate_observation,
)

ELIGIBLE_SHA256 = "a989e066ab5c66bec753719b3a3006c15a0635504f63977750a9192aa2995426"
AUDIT_SHA256 = "b33e76252c40c14416e8dfbe944404413cdd76e8d5696df566596ffa80335dec"
ALLOWED_ROLES = {"development_fit", "development_early_stop"}
RENDERER = {
    "use_camera_wb": False,
    "use_auto_wb": False,
    "no_auto_bright": True,
    "output_bps": 8,
    "gamma": (2.222, 4.5),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_unique_rows(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        required = {"source_id", "relative_path", "role"}
        if not required <= set(reader.fieldnames or ()):
            raise ValueError(f"Missing required columns in {path}")
        rows = {}
        for row in reader:
            source_id = row["source_id"]
            if source_id in rows:
                raise ValueError(f"Duplicate source ID in {path}: {source_id}")
            rows[source_id] = row
    return rows


def authorize_inputs(
    nefs: list[Path], manifest: Path, audit: Path
) -> tuple[list[dict[str, str]], str]:
    if sha256_file(manifest) != ELIGIBLE_SHA256:
        raise ValueError("The eligible-source manifest does not match the reviewed 06B v1 receipt")
    if sha256_file(audit) != AUDIT_SHA256:
        raise ValueError("The source audit CSV does not match the reviewed 06B v1 receipt")
    eligible = load_unique_rows(manifest)
    if len(eligible) != 994:
        raise ValueError("Expected exactly 994 eligible source identities")
    audited = load_unique_rows(audit)
    if len({p.name for p in nefs}) != len(nefs) or not nefs:
        raise ValueError("Specify one or more distinct NEF files")
    selected = []
    for nef in nefs:
        if nef.suffix.lower() != ".nef" or nef.name != f"{nef.stem}.NEF":
            raise ValueError(f"Expected a canonical .NEF filename: {nef.name}")
        source_id = nef.stem
        role = eligible.get(source_id)
        if role is None or role["role"] not in ALLOWED_ROLES:
            raise ValueError(f"Source is excluded or its role cannot be used in 06C: {source_id}")
        check = audited.get(source_id)
        if check is None or not {"file_sha256", "decoded_rgb_sha256", "byte_count"} <= set(check):
            raise ValueError(f"Missing 06B RAW and rendering audit for: {source_id}")
        if (role["relative_path"] != nef.name or check["relative_path"] != nef.name
                or check["role"] != role["role"]):
            raise ValueError(f"Source identity/role mismatch in 06B records: {source_id}")
        if not nef.is_file() or nef.stat().st_size != int(check["byte_count"]):
            raise ValueError(f"Missing file or unexpected byte count for: {source_id}")
        digest = sha256_file(nef)
        if digest != check["file_sha256"]:
            raise ValueError(f"RAW digest differs from independently reviewed audit: {source_id}")
        selected.append({"source_id": source_id, "role": role["role"],
                         "nef": str(nef.resolve()), "raw_sha256": digest,
                         "decoded_rgb_sha256": check["decoded_rgb_sha256"]})
    return sorted(selected, key=lambda row: row["source_id"]), AUDIT_SHA256


def decode_verified(nef: Path, expected_hash: str) -> np.ndarray:
    import rawpy

    with rawpy.imread(str(nef)) as raw:
        rgb = raw.postprocess(**RENDERER)
    if rgb.dtype != np.uint8 or rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError(f"Unexpected RAW rendering dimensions/type for: {nef.name}")
    header = np.asarray(rgb.shape, dtype=np.int64).tobytes()
    digest = hashlib.sha256(header + np.ascontiguousarray(rgb).tobytes()).hexdigest()
    if digest != expected_hash:
        raise ValueError(f"Decoded RGB differs from 06B renderer audit: {nef.stem}")
    return rgb


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nef", type=Path, nargs="+", required=True)
    parser.add_argument("--audit-csv", type=Path, required=True,
                        help="06B independently audited external_source_audit.csv")
    parser.add_argument("--eligible-manifest", type=Path, default=REPO_ROOT /
                        "experiments/stage06/manifests/RAISE_1k_eligible_roles_v1_20260925.csv")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--crop-size", type=int, default=512)
    parser.add_argument("--seed", type=int, default=20260925)
    args = parser.parse_args()
    if args.crop_size < 32 or args.crop_size % 8:
        parser.error("Crop size must be at least 32 and divisible by 8")
    selected, audit_hash = authorize_inputs(args.nef, args.eligible_manifest, args.audit_csv)
    measurements = []
    source_receipts = []
    for item in selected:
        rgb = decode_verified(Path(item["nef"]), item["decoded_rgb_sha256"])
        h, w, _ = rgb.shape
        if args.crop_size > min(h, w):
            raise ValueError(f"Crop exceeds rendered source dimensions: {item['source_id']}")
        y, x = (h - args.crop_size) // 2, (w - args.crop_size) // 2
        reference = rgb[y:y + args.crop_size, x:x + args.crop_size].astype(np.float64) / 255
        # The same seed for both chains isolates the changed operator domain.
        source_seed = args.seed + int.from_bytes(
            hashlib.sha256(item["source_id"].encode()).digest()[:4], "big"
        )
        observations = {}
        for chain_id, config in STAGE06_DEVELOPMENT_CHAINS.items():
            observation, chain_receipt = simulate_observation(reference, config, source_seed)
            observations[chain_id] = observation
            measurements.append({"source_id": item["source_id"], "role": item["role"],
                "chain_id": chain_id, "reference_mse": float(np.mean((observation - reference) ** 2)),
                "mean_observation": float(observation.mean()),
                "observation_u8_sha256": hashlib.sha256(np.rint(observation * 255).astype(np.uint8).tobytes()).hexdigest(),
                "seed": source_seed})
        first, second = observations.values()
        source_receipts.append({"source_id": item["source_id"], "role": item["role"],
            "raw_sha256": item["raw_sha256"], "decoded_rgb_sha256": item["decoded_rgb_sha256"],
            "rendered_shape": list(rgb.shape), "crop_xywh": [x, y, args.crop_size, args.crop_size],
            "between_chain_mse": float(np.mean((first - second) ** 2))})
        if source_receipts[-1]["between_chain_mse"] <= 0:
            raise ValueError(f"Alternate acquisition chain had no effect: {item['source_id']}")
        del rgb
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    csv_path = output / "source_chain_smoke.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(measurements[0]))
        writer.writeheader()
        writer.writerows(measurements)
    receipt = {"schema_version": "stage06c-real-raise-acquisition-smoke-v1",
        "scope": "engineering smoke test only; no solver or reliability result",
        "eligible_manifest_sha256": ELIGIBLE_SHA256, "audit_csv_sha256": audit_hash,
        "renderer": RENDERER, "working_rgb_interpretation": "06B rendered RGB treated as sRGB",
        "crop_size": args.crop_size, "seed_base": args.seed,
        "chain_configs": {name: vars(config) for name, config in STAGE06_DEVELOPMENT_CHAINS.items()},
        "versions": {name: metadata.version(name) for name in ("rawpy", "numpy", "pillow", "scipy")},
        "sources": source_receipts, "metric_csv_sha256": sha256_file(csv_path)}
    (output / "summary.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"source_count": len(selected), "roles": sorted({x["role"] for x in selected}),
        "between_chain_mse": {x["source_id"]: x["between_chain_mse"] for x in source_receipts},
        "output_dir": str(output)}, indent=2))


if __name__ == "__main__":
    main()
