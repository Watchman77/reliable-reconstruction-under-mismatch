#!/usr/bin/env python3
"""Validate the frozen Experiment 05 protocol without touching test data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments" / "independent_05"
PROTOCOL = EXPERIMENT / "protocol_freeze.json"
AUDIT = EXPERIMENT / "dataset_exposure_audit.csv"
DOCUMENT = ROOT / "docs" / "experiment_05_independent_validation_protocol.md"
RECEIPT = EXPERIMENT / "freeze_receipt.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise AssertionError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def expand_range(text: str) -> set[str]:
    left, right = text.split(" inclusive")[0].split("-")
    return {f"{number:04d}" for number in range(int(left), int(right) + 1)}


def load_audit() -> list[dict[str, str]]:
    with AUDIT.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate() -> dict[str, object]:
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    audit = load_audit()

    require(protocol["schema_version"] == "1.0.0", "Unexpected schema version")
    require(protocol["experiment_id"] == "independent_05", "Wrong experiment ID")
    require(protocol["test_results_inspected"] is False, "Protocol says test results were inspected")
    require(protocol["independent_test_run_authorized"] is False, "Independent run must remain locked")

    status = protocol["current_status"]
    require(status["protocol_frozen"] is True, "Protocol freeze not recorded")
    require(status["documented_exposure_audit_complete"] is True, "Exposure audit incomplete")
    for field in (
        "independent_dataset_downloaded_and_hashed",
        "near_duplicate_audit_complete",
        "trained_comparator_ready",
        "calibration_mappings_ready",
        "engineering_canary_passed",
        "independent_test_run",
    ):
        require(status[field] is False, f"Stage 05A/05B cannot mark {field} complete")

    dataset = protocol["sealed_primary_dataset"]
    require(dataset["name"] == "TESTIMAGES/SAMPLING", "Unexpected primary dataset")
    require(dataset["archive_name"] == "SAMPLING_8BIT_RGB_2400x2400.tar.bz2", "Archive changed")
    require(dataset["expected_sources"] == 40, "Expected source count changed")
    require(dataset["expected_mode"] == "RGB", "Expected image mode changed")
    require(dataset["expected_bit_depth_per_channel"] == 8, "Bit depth changed")
    require((dataset["expected_width"], dataset["expected_height"]) == (2400, 2400), "Dimensions changed")
    require(dataset["archive_sha256"] is None, "Archive hash must be supplied only by the later byte receipt")

    chains = protocol["simulation"]["acquisition_chains"]
    require(len(chains) == 7, "Acquisition ladder must contain seven chains")
    require(len({row["id"] for row in chains}) == len(chains), "Duplicate acquisition-chain ID")
    anchors = [row for row in chains if row["role"] == "primary_anchor"]
    require(len(anchors) == 1 and anchors[0]["id"] == "j75_b16_n2", "Primary anchor changed")
    require(any(row["codec"] == "quantized_8bit" for row in chains), "Missing no-JPEG negative control")
    require({50, 75, 90}.issubset({row["jpeg_quality"] for row in chains}), "JPEG ladder incomplete")

    methods = protocol["reconstruction_methods"]
    require(len(methods) == 6 and len(set(methods)) == 6, "Six unique reconstruction methods required")
    require({"dpir_nominal", "fbcnn_dpir_nominal"}.issubset(methods), "Primary reconstruction contrast missing")

    components = protocol["component_lock"]
    for component in ("dpir", "fbcnn"):
        require(len(components[component]["commit"]) == 40, f"{component} commit is not a full SHA")
        require(len(components[component]["checkpoint_sha256"]) == 64, f"{component} checkpoint digest invalid")

    partitions = protocol["development_partitions"]
    fit = expand_range(partitions["trained_comparator_fit_sources"])
    early = expand_range(partitions["trained_comparator_early_stop_sources"])
    calibration = expand_range(partitions["score_calibration_sources"])
    excluded = set(partitions["excluded_prior_development_sources"])
    require((len(fit), len(early), len(calibration)) == (52, 12, 32), "Development split counts changed")
    require(not (fit & early or fit & calibration or early & calibration), "Development partitions overlap")
    require(not ((fit | early | calibration) & excluded), "Prior development sources leaked into new partitions")
    require(set(partitions["engineering_canary_sources"]).issubset(fit), "Canary must use fit sources only")

    comparator = protocol["trained_image_only_comparator"]
    require(comparator["ensemble_members"] == 5, "Comparator ensemble size changed")
    require(len(set(comparator["seeds"])) == 5, "Comparator seeds must be unique")
    require(comparator["input_channels"] == 6, "Comparator input changed")
    require("no operator variants" in comparator["information"], "Image-only information boundary missing")

    hypotheses = protocol["primary_hypotheses"]
    require([row["id"] for row in hypotheses] == ["H1_reconstruction", "H2_selection"], "Primary hypotheses changed")
    require(all(row["condition"] == "j75_b16_n2" for row in hypotheses), "Primary condition changed")
    require(hypotheses[1]["coverage"] == 0.5, "Primary selection coverage changed")
    require(protocol["statistical_plan"]["patches_as_independent_replicates"] is False, "Patch pseudoreplication allowed")
    require(protocol["statistical_plan"]["multiplicity"] == "Holm correction across H1 and H2 only", "Multiplicity rule changed")

    eligible = [row for row in audit if row["primary_test_eligibility"] == "eligible with caveat"]
    require(len(eligible) == 1, "Audit must contain exactly one eligible primary cohort")
    require(eligible[0]["dataset_or_family"] == "TESTIMAGES/SAMPLING", "Eligible audit row does not match protocol")
    excluded_rows = [row for row in audit if row["primary_test_eligibility"] == "exclude"]
    require(len(excluded_rows) >= 10, "Exposure audit is unexpectedly short")
    required_families = {"DIV2K", "Flickr2K", "Waterloo Exploration Database", "LIVE1", "Kodak24", "McMaster18"}
    require(required_families.issubset({row["dataset_or_family"] for row in audit}), "Required audit families missing")

    forbidden = []
    independent_results = ROOT / "results" / "independent_05"
    if independent_results.exists():
        forbidden_names = {"quality.csv", "risk.csv", "summary.csv", "decisions.json", "risk_coverage.png"}
        forbidden = [str(path.relative_to(ROOT)) for path in independent_results.rglob("*") if path.name in forbidden_names]
    require(not forbidden, f"Independent performance artifacts already exist: {forbidden}")

    document = DOCUMENT.read_text(encoding="utf-8")
    for phrase in (
        "no documented exposure found",
        "not **proven unseen**",
        "not yet authorized",
        "at least 100 held-out natural images",
        "05C, next",
    ):
        require(phrase in document, f"Protocol document lost required boundary: {phrase}")

    return {
        "status": "pass",
        "experiment_id": protocol["experiment_id"],
        "validated_stage": protocol["stage"],
        "protocol_sha256": sha256(PROTOCOL),
        "audit_sha256": sha256(AUDIT),
        "document_sha256": sha256(DOCUMENT),
        "validator_sha256": sha256(Path(__file__)),
        "audit_rows": len(audit),
        "excluded_audit_rows": len(excluded_rows),
        "eligible_primary_cohort": eligible[0]["dataset_or_family"],
        "expected_primary_sources": dataset["expected_sources"],
        "acquisition_chains": len(chains),
        "reconstruction_methods": len(methods),
        "primary_hypotheses": len(hypotheses),
        "independent_performance_artifacts_found": 0,
        "independent_run_authorized": protocol["independent_test_run_authorized"],
        "next_stage": status["next_stage"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", action="store_true", help="Write experiments/independent_05/freeze_receipt.json")
    args = parser.parse_args()
    result = validate()
    if args.write_receipt:
        receipt = dict(result)
        receipt["validated_at_utc"] = datetime.now(timezone.utc).isoformat()
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result["receipt_path"] = str(RECEIPT.relative_to(ROOT))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
