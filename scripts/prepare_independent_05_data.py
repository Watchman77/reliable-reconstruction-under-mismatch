#!/usr/bin/env python3
"""Prepare the outcome-blind data receipt for independent experiment 05.

This utility performs integrity, decode, and near-duplicate checks only. It never
generates corruptions, runs a reconstruction model, or computes performance.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import tarfile
import tempfile
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO, Iterable

import numpy as np
from PIL import Image


TEST_ARCHIVE_NAME = "SAMPLING_8BIT_RGB_2400x2400.tar.bz2"
TEST_ARCHIVE_URL = (
    "https://sourceforge.net/projects/testimages/files/SAMPLING/8BIT/RGB/"
    "SAMPLING_8BIT_RGB_2400x2400.tar.bz2/download"
)
TEST_ARCHIVE_PUBLISHER_SHA256 = (
    "987e6a5208206b51bb556e808ea052aa588f373124bd0f571888a4754c6afa89"
)
EXPECTED_TEST_SOURCES = 40
EXPECTED_TEST_SIZE = (2400, 2400)
DEVELOPMENT_IDS = tuple(f"{number:04d}" for number in range(805, 901))
CANARY_IDS = ("0805", "0806")
NEAR_DUPLICATE_MAX_DISTANCE = 4


@dataclass(frozen=True)
class ImageFingerprint:
    source_id: str
    member_path: str
    byte_count: int
    sha256: str
    width: int
    height: int
    mode: str
    phash64: str
    dhash64: str


def sha256_stream(stream: BinaryIO, chunk_size: int = 1024 * 1024) -> tuple[str, int]:
    digest = hashlib.sha256()
    total = 0
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        digest.update(chunk)
        total += len(chunk)
    return digest.hexdigest(), total


def sha256_file(path: Path) -> tuple[str, int]:
    with path.open("rb") as stream:
        return sha256_stream(stream)


def _bits_to_hex(bits: np.ndarray) -> str:
    flat = np.asarray(bits, dtype=np.uint8).reshape(-1)
    if flat.size != 64:
        raise ValueError(f"expected 64 hash bits, received {flat.size}")
    value = 0
    for bit in flat:
        value = (value << 1) | int(bit)
    return f"{value:016x}"


def _dct_matrix(size: int) -> np.ndarray:
    indices = np.arange(size, dtype=np.float64)
    matrix = np.cos(np.pi * (2.0 * indices[None, :] + 1.0) * indices[:, None] / (2.0 * size))
    matrix[0, :] *= np.sqrt(1.0 / size)
    matrix[1:, :] *= np.sqrt(2.0 / size)
    return matrix


DCT32 = _dct_matrix(32)


def perceptual_hashes(image: Image.Image) -> tuple[str, str]:
    gray = image.convert("L")

    phash_image = np.asarray(gray.resize((32, 32), Image.Resampling.LANCZOS), dtype=np.float64)
    coefficients = DCT32 @ phash_image @ DCT32.T
    low = coefficients[:8, :8]
    threshold = np.median(low.reshape(-1)[1:])
    phash = _bits_to_hex(low >= threshold)

    dhash_image = np.asarray(gray.resize((9, 8), Image.Resampling.LANCZOS), dtype=np.int16)
    dhash = _bits_to_hex(dhash_image[:, 1:] > dhash_image[:, :-1])
    return phash, dhash


def fingerprint_bytes(source_id: str, member_path: str, payload: bytes) -> ImageFingerprint:
    with Image.open(io.BytesIO(payload)) as image:
        image.load()
        width, height = image.size
        mode = image.mode
        phash, dhash = perceptual_hashes(image)
    return ImageFingerprint(
        source_id=source_id,
        member_path=member_path,
        byte_count=len(payload),
        sha256=hashlib.sha256(payload).hexdigest(),
        width=width,
        height=height,
        mode=mode,
        phash64=phash,
        dhash64=dhash,
    )


def _source_id_from_member(member_path: str) -> str:
    return Path(member_path).stem


def read_test_archive(path: Path) -> list[ImageFingerprint]:
    fingerprints: list[ImageFingerprint] = []
    with tarfile.open(path, "r:bz2") as archive:
        members = sorted(
            (member for member in archive.getmembers() if member.isfile() and member.name.lower().endswith(".png")),
            key=lambda member: member.name,
        )
        for member in members:
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError(f"unable to read archive member: {member.name}")
            payload = stream.read()
            fingerprint = fingerprint_bytes(_source_id_from_member(member.name), member.name, payload)
            if (fingerprint.width, fingerprint.height) != EXPECTED_TEST_SIZE or fingerprint.mode != "RGB":
                continue
            fingerprints.append(fingerprint)

    ids = [fingerprint.source_id for fingerprint in fingerprints]
    if len(fingerprints) != EXPECTED_TEST_SOURCES:
        raise ValueError(
            f"expected {EXPECTED_TEST_SOURCES} RGB {EXPECTED_TEST_SIZE[0]}x{EXPECTED_TEST_SIZE[1]} PNG files; "
            f"received {len(fingerprints)}"
        )
    if len(set(ids)) != len(ids):
        raise ValueError("test archive contains duplicate source identifiers")
    return fingerprints


def _development_member_map(archive: zipfile.ZipFile) -> dict[str, str]:
    mapping: dict[str, str] = {}
    pattern = re.compile(r"^(080[5-9]|08[1-9][0-9]|0900)\.png$", re.IGNORECASE)
    for member_path in archive.namelist():
        basename = Path(member_path).name
        if not pattern.match(basename):
            continue
        source_id = Path(basename).stem
        if source_id in mapping:
            raise ValueError(f"duplicate DIV2K source identifier in archive: {source_id}")
        mapping[source_id] = member_path
    missing = sorted(set(DEVELOPMENT_IDS) - set(mapping))
    unexpected = sorted(set(mapping) - set(DEVELOPMENT_IDS))
    if missing or unexpected:
        raise ValueError(f"DIV2K development membership mismatch; missing={missing}, unexpected={unexpected}")
    return mapping


def read_development_archive(path: Path, canary_dir: Path) -> list[ImageFingerprint]:
    fingerprints: list[ImageFingerprint] = []
    canary_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "r") as archive:
        mapping = _development_member_map(archive)
        for source_id in DEVELOPMENT_IDS:
            member_path = mapping[source_id]
            payload = archive.read(member_path)
            fingerprint = fingerprint_bytes(source_id, member_path, payload)
            if fingerprint.mode != "RGB":
                raise ValueError(f"DIV2K {source_id} decoded as {fingerprint.mode}, expected RGB")
            fingerprints.append(fingerprint)
            if source_id in CANARY_IDS:
                destination = canary_dir / f"{source_id}.png"
                atomic_write_bytes(destination, payload)
    return fingerprints


def hamming_distance(hex_left: str, hex_right: str) -> int:
    return (int(hex_left, 16) ^ int(hex_right, 16)).bit_count()


def build_duplicate_rows(
    test_images: Iterable[ImageFingerprint], development_images: Iterable[ImageFingerprint]
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for test_image in test_images:
        for development_image in development_images:
            exact = test_image.sha256 == development_image.sha256
            phash_distance = hamming_distance(test_image.phash64, development_image.phash64)
            dhash_distance = hamming_distance(test_image.dhash64, development_image.dhash64)
            candidate = exact or (
                phash_distance <= NEAR_DUPLICATE_MAX_DISTANCE
                and dhash_distance <= NEAR_DUPLICATE_MAX_DISTANCE
            )
            rows.append(
                {
                    "test_source_id": test_image.source_id,
                    "test_member_path": test_image.member_path,
                    "development_source_id": development_image.source_id,
                    "development_member_path": development_image.member_path,
                    "exact_sha256_match": str(exact).lower(),
                    "phash64_hamming": phash_distance,
                    "dhash64_hamming": dhash_distance,
                    "near_duplicate_candidate": str(candidate).lower(),
                    "manual_adjudication": "pending" if candidate else "not_required",
                    "decision": "pending" if candidate else "retain",
                }
            )
    return rows


def atomic_write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        temporary_path.replace(path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    atomic_write_bytes(path, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def atomic_write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("duplicate-audit table is unexpectedly empty")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    atomic_write_bytes(path, output.getvalue().encode("utf-8"))


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--test-archive", type=Path, required=True)
    parser.add_argument("--div2k-archive", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--duplicate-audit", type=Path, required=True)
    parser.add_argument("--stage-status", type=Path, required=True)
    parser.add_argument("--canary-dir", type=Path, required=True)
    parser.add_argument("--receipt-time-utc", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    with args.protocol.open("r", encoding="utf-8") as stream:
        protocol = json.load(stream)

    frozen = protocol["sealed_primary_dataset"]
    if frozen["archive_name"] != TEST_ARCHIVE_NAME or frozen["archive_url"] != TEST_ARCHIVE_URL:
        raise ValueError("protocol archive identity does not match the locked receipt implementation")
    if protocol["independent_test_run_authorized"] is not False:
        raise ValueError("stage 05C requires independent_test_run_authorized=false")

    protocol_sha256, protocol_bytes = sha256_file(args.protocol)
    test_sha256, test_bytes = sha256_file(args.test_archive)
    if test_sha256 != TEST_ARCHIVE_PUBLISHER_SHA256:
        raise ValueError(
            f"TESTIMAGES archive SHA-256 mismatch: expected {TEST_ARCHIVE_PUBLISHER_SHA256}, observed {test_sha256}"
        )
    div2k_sha256, div2k_bytes = sha256_file(args.div2k_archive)

    test_images = read_test_archive(args.test_archive)
    development_images = read_development_archive(args.div2k_archive, args.canary_dir)
    duplicate_rows = build_duplicate_rows(test_images, development_images)
    candidates = [row for row in duplicate_rows if row["near_duplicate_candidate"] == "true"]
    exact_matches = [row for row in duplicate_rows if row["exact_sha256_match"] == "true"]
    audit_complete = not candidates

    atomic_write_csv(args.duplicate_audit, duplicate_rows)
    duplicate_audit_sha256, duplicate_audit_bytes = sha256_file(args.duplicate_audit)
    receipt_time = args.receipt_time_utc or utc_now()
    receipt = {
        "schema_version": "1.0.0",
        "experiment_id": "independent_05",
        "stage": "05C_data_receipt",
        "created_at_utc": receipt_time,
        "outcome_blind": True,
        "test_inference_performed": False,
        "test_performance_inspected": False,
        "protocol": {
            "path": str(args.protocol),
            "byte_count": protocol_bytes,
            "sha256": protocol_sha256,
            "independent_test_run_authorized": False,
        },
        "test_archive": {
            "path": str(args.test_archive),
            "archive_name": TEST_ARCHIVE_NAME,
            "archive_url": TEST_ARCHIVE_URL,
            "publisher_sha256": TEST_ARCHIVE_PUBLISHER_SHA256,
            "publisher_sha256_source": "SourceForge download page",
            "observed_sha256": test_sha256,
            "byte_count": test_bytes,
            "publisher_digest_match": True,
            "eligible_source_count": len(test_images),
            "sources": [asdict(fingerprint) for fingerprint in test_images],
        },
        "development_archive": {
            "path": str(args.div2k_archive),
            "observed_sha256": div2k_sha256,
            "byte_count": div2k_bytes,
            "audited_source_count": len(development_images),
            "source_range": "0805-0900",
            "canary_sources_extracted": list(CANARY_IDS),
            "sources": [asdict(fingerprint) for fingerprint in development_images],
        },
        "duplicate_audit": {
            "path": str(args.duplicate_audit),
            "sha256": duplicate_audit_sha256,
            "byte_count": duplicate_audit_bytes,
            "pair_count": len(duplicate_rows),
            "exact_match_count": len(exact_matches),
            "candidate_count": len(candidates),
            "phash64_hamming_threshold": NEAR_DUPLICATE_MAX_DISTANCE,
            "dhash64_hamming_threshold": NEAR_DUPLICATE_MAX_DISTANCE,
            "manual_adjudication_required": bool(candidates),
            "complete": audit_complete,
        },
        "receipt_status": "pass" if audit_complete else "manual_adjudication_required",
    }
    atomic_write_json(args.receipt, receipt)
    receipt_sha256, receipt_bytes = sha256_file(args.receipt)

    stage_status = {
        "schema_version": "1.0.0",
        "experiment_id": "independent_05",
        "stage": "05C",
        "updated_at_utc": receipt_time,
        "protocol_frozen": True,
        "dataset_downloaded_and_hashed": True,
        "test_archive_publisher_digest_match": True,
        "test_source_decode_check_complete": True,
        "near_duplicate_audit_complete": audit_complete,
        "canary_inputs_ready": True,
        "implementation_ready": False,
        "development_canary_passed": False,
        "comparator_fitted": False,
        "calibration_fitted": False,
        "independent_test_run_authorized": False,
        "test_inference_performed": False,
        "test_performance_inspected": False,
        "data_receipt": {
            "path": str(args.receipt),
            "sha256": receipt_sha256,
            "byte_count": receipt_bytes,
        },
        "blockers": [] if audit_complete else ["near_duplicate_candidates_require_manual_adjudication"],
        "next_permitted_action": "Implement and run the development-only 0805-0806 engineering canary.",
    }
    atomic_write_json(args.stage_status, stage_status)

    summary = {
        "status": receipt["receipt_status"],
        "test_archive_sha256": test_sha256,
        "test_sources": len(test_images),
        "development_sources": len(development_images),
        "duplicate_pairs": len(duplicate_rows),
        "duplicate_candidates": len(candidates),
        "test_inference_performed": False,
        "independent_test_run_authorized": False,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if audit_complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
