#!/usr/bin/env python3
"""Validate a Stage-05F result directory or ZIP without inspecting raw shards."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import tempfile
import zipfile
from pathlib import Path


EXPECTED_STAGE = "05F_locked_literature_and_experimental_synthesis"
EXPECTED_STATUS = "completed_locked_synthesis"
EXPECTED_H1 = 0.901305584214458
EXPECTED_H2 = 0.044640422584371585
PRACTICAL_GATE = 0.05


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def locate_result_root(root: Path) -> Path:
    direct = root / "export_manifest.json"
    if direct.is_file():
        return root
    matches = sorted(root.rglob("export_manifest.json"))
    matches = [p for p in matches if p.parent.name == "independent_05f_locked_synthesis"]
    if len(matches) != 1:
        raise AssertionError(
            "Expected exactly one independent_05f_locked_synthesis/export_manifest.json; "
            f"found {len(matches)}"
        )
    return matches[0].parent


def validate_directory(root: Path) -> dict:
    manifest = load_json(root / "export_manifest.json")
    assert manifest["stage"] == EXPECTED_STAGE
    assert manifest["status"] == EXPECTED_STATUS

    tracked = manifest["files"]
    assert len(tracked) == 12, f"Expected 12 tracked files, found {len(tracked)}"
    tracked_paths = {row["path"] for row in tracked}
    assert len(tracked_paths) == len(tracked), "Duplicate paths in export manifest"

    for row in tracked:
        path = root / row["path"]
        assert path.is_file(), f"Missing tracked file: {row['path']}"
        payload = path.read_bytes()
        assert len(payload) == row["byte_count"], f"Byte-count mismatch: {row['path']}"
        assert sha256_bytes(payload) == row["sha256"], f"SHA-256 mismatch: {row['path']}"

    status = load_json(root / "status.json")
    decision = load_json(root / "synthesis_decision.json")
    checks = load_json(root / "checks.json")

    assert status["stage"] == EXPECTED_STAGE
    assert status["status"] == EXPECTED_STATUS
    assert status["final_literature_novelty_claim_established"] is False
    assert status["original_unified_claim_retained"] is False
    assert status["narrow_acquisition_chain_contribution_supported"] is True
    assert status["next_stage"] == "manuscript_and_repository_checkpoint"

    h1 = decision["h1_reconstruction"]
    h2 = decision["h2_selection"]
    assert math.isclose(h1["relative_reduction"], EXPECTED_H1, rel_tol=0, abs_tol=1e-15)
    assert math.isclose(h2["relative_reduction"], EXPECTED_H2, rel_tol=0, abs_tol=1e-15)
    assert h1["confirmatory_gate_passed"] is True
    assert h2["statistical_gate_passed"] is True
    assert h2["practical_gate_passed"] is False
    assert h2["relative_reduction"] < PRACTICAL_GATE
    assert decision["experimental_novelty_gate_passed"] is False
    assert decision["final_literature_novelty_claim_established"] is False
    assert decision["calibration_boundary"]["observed_positive_events_in_reliability_bins"] == 0
    assert decision["calibration_boundary"]["positive_event_calibration_estimable"] is False

    assert checks["stage_05e_archive_crc_passed"] is True
    assert checks["stage_05e_manifest_files_checked"] == 13
    assert checks["stage_05e_sources"] == 40
    assert checks["stage_05e_chains"] == 7
    assert checks["literature_rows"] == 90
    assert checks["literature_closest_competitors"] == 62
    assert checks["h1_gate_passed"] is True
    assert checks["h2_statistical_gate_passed"] is True
    assert checks["h2_practical_gate_passed"] is False
    assert checks["zero_positive_calibration_events"] is True

    return {
        "stage": status["stage"],
        "status": status["status"],
        "manifest_files_verified": len(tracked),
        "h1_relative_reduction_percent": 100 * h1["relative_reduction"],
        "h1_gate_passed": h1["confirmatory_gate_passed"],
        "h2_relative_reduction_percent": 100 * h2["relative_reduction"],
        "h2_practical_gate_percent": 100 * PRACTICAL_GATE,
        "h2_practical_gate_passed": h2["practical_gate_passed"],
        "positive_calibration_events": 0,
        "unified_claim_established": False,
        "narrow_contribution_supported": True,
    }


def validate_target(target: Path) -> dict:
    if target.is_dir():
        return validate_directory(locate_result_root(target))
    assert target.is_file(), f"Target does not exist: {target}"
    assert zipfile.is_zipfile(target), f"Target is not a ZIP archive: {target}"
    with zipfile.ZipFile(target) as archive:
        bad_member = archive.testzip()
        assert bad_member is None, f"ZIP CRC failure: {bad_member}"
        with tempfile.TemporaryDirectory(prefix="validate_05f_") as temp_dir:
            archive.extractall(temp_dir)
            result = validate_directory(locate_result_root(Path(temp_dir)))
    result["archive_sha256"] = sha256_bytes(target.read_bytes())
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="Stage-05F directory or ZIP")
    args = parser.parse_args()
    result = validate_target(args.target.resolve())
    print(json.dumps({"validation": "PASS", **result}, indent=2))


if __name__ == "__main__":
    main()
