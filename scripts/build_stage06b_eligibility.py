#!/usr/bin/env python3
"""Build a versioned Stage 06B eligible-source manifest from source-only evidence.

This script never opens reconstruction results. It preserves the original roles
and excludes one recorded member of each exact-duplicate group.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


EXPECTED_ORIGINAL_SHA256 = "fa4fe1272edae7f18e6d831d4e5878433413e26afe38997c15b4a7cd7ff77bf7"
EXPECTED_AUDIT_SHA256 = "b33e76252c40c14416e8dfbe944404413cdd76e8d5696df566596ffa80335dec"
EXPECTED_OVERLAP_SHA256 = "7a54f41c976e686b1c206175b477fa0593af4917ad310fd14bb0bb3dfded2416"
EXPECTED_COUNTS = {
    "development_fit": 495,
    "development_early_stop": 150,
    "development_calibration": 149,
    "external_pilot": 50,
    "independent_test": 150,
}
ROLE_PRIORITY = {
    "development_fit": 1,
    "development_early_stop": 2,
    "development_calibration": 3,
    "external_pilot": 4,
    "independent_test": 5,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def unordered_pair(left: str, right: str) -> frozenset[str]:
    require(left != right, "A source cannot be paired with itself")
    return frozenset((left, right))


def build(original: Path, audited: Path, overlaps: Path, decisions: Path,
          eligible_path: Path, receipt_path: Path) -> dict:
    for name, path, expected in (
        ("original roles", original, EXPECTED_ORIGINAL_SHA256),
        ("source audit", audited, EXPECTED_AUDIT_SHA256),
        ("overlap pairs", overlaps, EXPECTED_OVERLAP_SHA256),
    ):
        require(sha256(path) == expected, f"{name} changed from reviewed input: {path}")

    original_cols, roles = load_csv(original)
    _, audit = load_csv(audited)
    _, pairs = load_csv(overlaps)
    _, ledger = load_csv(decisions)
    require(len(roles) == len(audit) == 1000, "Expected 1,000 original and audited sources")
    role_by_id = {row["source_id"]: row for row in roles}
    audit_by_id = {row["source_id"]: row for row in audit}
    require(len(role_by_id) == len(audit_by_id) == 1000, "Duplicate source ID")
    require(set(role_by_id) == set(audit_by_id), "Audit and original manifest source IDs differ")
    require(all(role_by_id[sid]["role"] == audit_by_id[sid]["role"] for sid in role_by_id),
            "Original source roles changed in the audit")

    detected = defaultdict(set)
    for row in pairs:
        kind = row["overlap_type"]
        require(kind in {"within_file_exact", "within_rgb_exact", "within_perceptual_candidate"},
                f"Unreviewed overlap category: {kind}")
        pair = unordered_pair(row["candidate_source_id"], row["reference_source_id"])
        require(pair <= set(role_by_id), "Overlap includes a source outside original manifest")
        detected[pair].add(kind)
    require(len(detected) == 8, "Unexpected number of unique overlap pairs")

    decisions_by_pair = {}
    excluded = set()
    for row in ledger:
        pair = unordered_pair(row["candidate_source_id"], row["reference_source_id"])
        require(pair not in decisions_by_pair, "Repeated decision for an overlap pair")
        require(pair in detected, "Decision does not match the observed overlap list")
        for side in ("candidate", "reference"):
            sid = row[f"{side}_source_id"]
            require(role_by_id[sid]["role"] == row[f"{side}_role"], "Decision role mismatch")
        kinds = detected[pair]
        if kinds == {"within_file_exact", "within_rgb_exact"}:
            require(row["decision"] == "exclude_one_exact" and row["distance"] == "0",
                    "Exact pair must exclude one member")
            retained, removed = row["retained_source_id"], row["excluded_source_id"]
            require({retained, removed} == pair, "Wrong retained/excluded source in exact pair")
            priority = max(ROLE_PRIORITY[role_by_id[sid]["role"]] for sid in pair)
            preferred = min(sid for sid in pair if ROLE_PRIORITY[role_by_id[sid]["role"]] == priority)
            require(retained == preferred, "Exact duplicate retention policy was not followed")
            require(audit_by_id[retained]["file_sha256"] == audit_by_id[removed]["file_sha256"]
                    and audit_by_id[retained]["decoded_rgb_sha256"] == audit_by_id[removed]["decoded_rgb_sha256"],
                    "Pair does not have matching audited file and RGB hashes")
            require(removed not in excluded, "Same source excluded twice")
            excluded.add(removed)
        elif kinds == {"within_perceptual_candidate"}:
            require(row["decision"] == "retain_both_visual_false_positive"
                    and row["review_evidence"].strip()
                    and row["retained_source_id"] == "" and row["excluded_source_id"] == "",
                    "Perceptual pair requires a recorded manual decision")
            require(row["distance"] == next(p["distance"] for p in pairs
                    if unordered_pair(p["candidate_source_id"], p["reference_source_id"]) == pair),
                    "Perceptual distance changed")
        else:
            raise ValueError(f"Unhandled overlap evidence for {sorted(pair)}: {kinds}")
        decisions_by_pair[pair] = row
    require(set(decisions_by_pair) == set(detected), "Every detected pair needs one decision")
    require(len(excluded) == 6, "Expected six exact duplicate exclusions")

    eligible = [row for row in roles if row["source_id"] not in excluded]
    require(len(eligible) == 994 and len({r["source_id"] for r in eligible}) == 994,
            "Eligible set must contain 994 distinct sources")
    counts = dict(Counter(row["role"] for row in eligible))
    require(counts == EXPECTED_COUNTS, f"Eligible role counts changed: {counts}")
    for field in ("file_sha256", "decoded_rgb_sha256"):
        require(len({audit_by_id[r["source_id"]][field] for r in eligible}) == 994,
                f"Eligible sources have repeated {field}")
    require(all(row["role"] not in {"external_pilot", "independent_test"}
                for row in roles if row["source_id"] in excluded),
            "An external pilot or independent-test source was excluded")

    eligible_path.parent.mkdir(parents=True, exist_ok=True)
    with eligible_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=original_cols, lineterminator="\n")
        writer.writeheader()
        writer.writerows(eligible)
    receipt = {
        "schema_version": "stage06b-raise-eligibility-v1",
        "decision_status": "source_identity_resolved_provenance_gate_pending",
        "original_source_count": 1000,
        "eligible_source_count": 994,
        "excluded_exact_duplicate_source_ids": sorted(excluded),
        "false_positive_perceptual_pair_count": 2,
        "eligible_role_counts": counts,
        "original_roles_sha256": sha256(original),
        "source_audit_sha256": sha256(audited),
        "overlap_pairs_sha256": sha256(overlaps),
        "decision_ledger_sha256": sha256(decisions),
        "eligible_roles_sha256": sha256(eligible_path),
        "pretrained_model_training_overlap_review": "pending",
        "stage06b_provenance_gate_passed": False,
        "independent_reconstruction_outcomes_inspected": False,
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    for name in ("original", "audited", "overlaps", "decisions", "eligible", "receipt"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.original, args.audited, args.overlaps, args.decisions,
                           args.eligible, args.receipt), indent=2))


if __name__ == "__main__":
    main()
