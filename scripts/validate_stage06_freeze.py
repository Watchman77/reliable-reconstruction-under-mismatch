#!/usr/bin/env python3
"""Validate a Stage 06 freeze specification without inspecting test outcomes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REQUIRED_ROLES = (
    "development_fit",
    "development_early_stop",
    "development_calibration",
    "external_pilot",
    "independent_test",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_frozen(value: Any, label: str, errors: list[str]) -> None:
    text = str(value).strip()
    if not text or "REPLACE" in text:
        errors.append(f"Unfrozen field: {label}")


def validate(spec_path: Path) -> list[str]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    errors: list[str] = []

    if spec.get("schema_version") != "stage06-freeze-v1":
        errors.append("schema_version must equal stage06-freeze-v1")
    if spec.get("stage05_immutable") is not True:
        errors.append("stage05_immutable must be true")
    if spec.get("source_unit") != "image_source":
        errors.append("source_unit must be image_source")

    for field in (
        "frozen_at_utc",
        "multiplicity_rule",
        "primary_operational_threshold_rmse",
    ):
        require_frozen(spec.get(field), field, errors)

    dataset = spec.get("external_dataset", {})
    for field in ("name", "version", "license", "source_url", "archive_sha256", "training_overlap_risk"):
        require_frozen(dataset.get(field), f"external_dataset.{field}", errors)

    solvers = spec.get("solvers", [])
    if len(solvers) < 2:
        errors.append("At least two solvers must be frozen")
    for index, solver in enumerate(solvers):
        require_frozen(solver.get("name"), f"solvers[{index}].name", errors)
        require_frozen(solver.get("checkpoint_id"), f"solvers[{index}].checkpoint_id", errors)

    chains = spec.get("acquisition_chains", [])
    if len(chains) < 2:
        errors.append("At least two acquisition-chain definitions are required")
    for index, chain in enumerate(chains):
        require_frozen(chain, f"acquisition_chains[{index}]", errors)

    roles = spec.get("source_roles", {})
    seen: dict[str, str] = {}
    for role in REQUIRED_ROLES:
        values = roles.get(role)
        if not isinstance(values, list) or not values:
            errors.append(f"source_roles.{role} must be a non-empty list")
            continue
        for source_id in values:
            source_key = str(source_id)
            if source_key in seen:
                errors.append(f"Source {source_key!r} appears in both {seen[source_key]} and {role}")
            else:
                seen[source_key] = role

    sample_size = spec.get("sample_size", {})
    require_frozen(sample_size.get("independent_source_count"), "sample_size.independent_source_count", errors)
    require_frozen(sample_size.get("design_basis"), "sample_size.design_basis", errors)

    for key, value in spec.get("random_seeds", {}).items():
        require_frozen(value, f"random_seeds.{key}", errors)

    root = spec_path.parent
    artifacts = spec.get("artifacts", [])
    if not artifacts:
        errors.append("artifacts must contain at least one frozen file")
    for index, record in enumerate(artifacts):
        rel = str(record.get("path", ""))
        require_frozen(rel, f"artifacts[{index}].path", errors)
        if not rel or "REPLACE" in rel:
            continue
        path = (root / rel).resolve()
        try:
            path.relative_to(root.resolve())
        except ValueError:
            errors.append(f"Artifact leaves freeze root: {rel}")
            continue
        if not path.is_file():
            errors.append(f"Missing artifact: {rel}")
            continue
        if path.stat().st_size != record.get("byte_count"):
            errors.append(f"Byte-count mismatch: {rel}")
        if sha256_file(path) != record.get("sha256"):
            errors.append(f"SHA-256 mismatch: {rel}")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    args = parser.parse_args()
    errors = validate(args.spec.resolve())
    if errors:
        print(json.dumps({"status": "failed", "errors": errors}, indent=2))
        raise SystemExit(1)
    print(json.dumps({"status": "passed", "spec": str(args.spec.resolve())}, indent=2))


if __name__ == "__main__":
    main()

