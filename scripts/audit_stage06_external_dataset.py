#!/usr/bin/env python3
"""Create a source-level provenance and overlap audit for Stage 06 images."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


VALID_ROLES = {
    "development_fit",
    "development_early_stop",
    "development_calibration",
    "external_pilot",
    "independent_test",
}
RAW_SUFFIXES = {".arw", ".cr2", ".cr3", ".dng", ".nef", ".nrw", ".orf", ".raf", ".rw2"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_rgb8(path: Path) -> np.ndarray:
    if path.suffix.lower() in RAW_SUFFIXES:
        try:
            import rawpy  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                f"{path.name} is RAW; install the pinned Stage 06 rawpy dependency before auditing"
            ) from exc
        with rawpy.imread(str(path)) as raw:
            return raw.postprocess(
                use_camera_wb=False,
                use_auto_wb=False,
                no_auto_bright=True,
                output_bps=8,
                gamma=(2.222, 4.5),
            )
    with Image.open(path) as image:
        image.load()
        return np.asarray(image.convert("RGB"), dtype=np.uint8)


def rgb_sha256(rgb: np.ndarray) -> str:
    header = np.asarray(rgb.shape, dtype=np.int64).tobytes()
    return hashlib.sha256(header + np.ascontiguousarray(rgb).tobytes()).hexdigest()


def dhash64(rgb: np.ndarray) -> str:
    grey = Image.fromarray(rgb, mode="RGB").convert("L").resize((9, 8), Image.Resampling.LANCZOS)
    values = np.asarray(grey, dtype=np.int16)
    bits = values[:, 1:] > values[:, :-1]
    packed = 0
    for bit in bits.ravel():
        packed = (packed << 1) | int(bit)
    return f"{packed:016x}"


def hamming_hex(left: str, right: str) -> int:
    return (int(left, 16) ^ int(right, 16)).bit_count()


def validate_roles(table: pd.DataFrame) -> None:
    required = {"source_id", "relative_path", "role"}
    missing = required - set(table.columns)
    if missing:
        raise ValueError(f"Role manifest missing columns: {sorted(missing)}")
    if table["source_id"].astype(str).duplicated().any():
        values = table.loc[table["source_id"].astype(str).duplicated(False), "source_id"].tolist()
        raise ValueError(f"Duplicate source IDs: {values}")
    if table["relative_path"].astype(str).duplicated().any():
        values = table.loc[table["relative_path"].astype(str).duplicated(False), "relative_path"].tolist()
        raise ValueError(f"Duplicate relative paths: {values}")
    unknown = sorted(set(table["role"].astype(str)) - VALID_ROLES)
    if unknown:
        raise ValueError(f"Unknown source roles: {unknown}")
    absent = sorted(VALID_ROLES - set(table["role"].astype(str)))
    if absent:
        raise ValueError(f"Every Stage 06 role must be represented before freeze; missing: {absent}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--roles-csv", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--reference-manifest", type=Path)
    parser.add_argument("--perceptual-hamming-threshold", type=int, default=4)
    args = parser.parse_args()

    candidate_dir = args.candidate_dir.resolve()
    roles = pd.read_csv(args.roles_csv, dtype=str, keep_default_na=False)
    validate_roles(roles)
    records: list[dict[str, object]] = []
    for row in roles.to_dict("records"):
        relative = Path(str(row["relative_path"]))
        path = (candidate_dir / relative).resolve()
        try:
            path.relative_to(candidate_dir)
        except ValueError as exc:
            raise ValueError(f"Path leaves candidate directory: {relative}") from exc
        if not path.is_file():
            raise FileNotFoundError(path)
        rgb = load_rgb8(path)
        records.append(
            {
                "source_id": str(row["source_id"]),
                "role": str(row["role"]),
                "relative_path": relative.as_posix(),
                "byte_count": path.stat().st_size,
                "file_sha256": sha256_file(path),
                "decoded_rgb_sha256": rgb_sha256(rgb),
                "dhash64": dhash64(rgb),
                "width": int(rgb.shape[1]),
                "height": int(rgb.shape[0]),
            }
        )
    audit = pd.DataFrame.from_records(records).sort_values(["role", "source_id"]).reset_index(drop=True)

    overlap_rows: list[dict[str, object]] = []
    for column, overlap_type in (("file_sha256", "within_file_exact"), ("decoded_rgb_sha256", "within_rgb_exact")):
        for value, group in audit.groupby(column, sort=False):
            if len(group) > 1:
                ids = group["source_id"].astype(str).tolist()
                for left_index, left in enumerate(ids):
                    for right in ids[left_index + 1 :]:
                        overlap_rows.append(
                            {"candidate_source_id": left, "reference_source_id": right, "overlap_type": overlap_type, "distance": 0}
                        )

    if args.reference_manifest:
        reference = pd.read_csv(args.reference_manifest, dtype=str, keep_default_na=False)
        required = {"source_id", "decoded_rgb_sha256", "dhash64"}
        missing = required - set(reference.columns)
        if missing:
            raise ValueError(f"Reference manifest missing columns: {sorted(missing)}")
        exact_map: dict[str, list[str]] = {}
        for row in reference.to_dict("records"):
            exact_map.setdefault(str(row["decoded_rgb_sha256"]), []).append(str(row["source_id"]))
        for row in audit.to_dict("records"):
            for reference_id in exact_map.get(str(row["decoded_rgb_sha256"]), []):
                overlap_rows.append(
                    {"candidate_source_id": row["source_id"], "reference_source_id": reference_id, "overlap_type": "cross_rgb_exact", "distance": 0}
                )
            for ref in reference.to_dict("records"):
                distance = hamming_hex(str(row["dhash64"]), str(ref["dhash64"]))
                if distance <= args.perceptual_hamming_threshold and str(row["decoded_rgb_sha256"]) != str(ref["decoded_rgb_sha256"]):
                    overlap_rows.append(
                        {
                            "candidate_source_id": row["source_id"],
                            "reference_source_id": ref["source_id"],
                            "overlap_type": "cross_perceptual_candidate",
                            "distance": distance,
                        }
                    )

    overlaps = pd.DataFrame.from_records(
        overlap_rows,
        columns=["candidate_source_id", "reference_source_id", "overlap_type", "distance"],
    ).drop_duplicates()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    audit_path = output_dir / "external_source_audit.csv"
    overlap_path = output_dir / "external_overlap_pairs.csv"
    audit.to_csv(audit_path, index=False)
    overlaps.to_csv(overlap_path, index=False)
    summary = {
        "schema_version": "stage06-external-audit-v1",
        "source_count": int(len(audit)),
        "role_counts": {str(k): int(v) for k, v in audit.groupby("role").size().items()},
        "overlap_pair_count": int(len(overlaps)),
        "freeze_gate_passed": bool(overlaps.empty),
        "perceptual_hamming_threshold": int(args.perceptual_hamming_threshold),
        "note": "Perceptual candidates require manual image-pair review; a zero count is necessary but not sufficient for provenance clearance.",
    }
    summary_path = output_dir / "external_audit_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    manifest_records = []
    for path in (audit_path, overlap_path, summary_path):
        manifest_records.append(
            {"path": path.name, "byte_count": path.stat().st_size, "sha256": sha256_file(path)}
        )
    (output_dir / "export_manifest.json").write_text(
        json.dumps({"stage": "06B_external_source_audit", "files": manifest_records}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    if not overlaps.empty:
        raise SystemExit(2)


if __name__ == "__main__":
    main()

