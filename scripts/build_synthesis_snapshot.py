#!/usr/bin/env python3
"""Build a provenance-preserving inventory of the existing AI full-text records.

This does not screen papers, amend feature codes, or author the workbook.
Only fields explicitly extracted in full_text_*.json enter feature counts.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "literature/synthesis"
FEATURES = {
    "O": "Joint image/operator inference",
    "P": "Image uncertainty",
    "Q": "Operator uncertainty",
    "R": "Calibration evaluated",
    "S": "Out-of-distribution test",
    "T": "Real measurements/hardware",
    "U": "Compound degradation",
    "V": "Time variation (legacy scope; see caveat)",
    "W": "Hallucination/support assessment",
    "X": "Abstention/selection",
}
VALUES = ("Yes", "Partial", "No", "Not extracted")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    reference_file = ROOT / "literature/references/forward_model_mismatch_90_references.csv"
    with reference_file.open(newline="", encoding="utf-8") as handle:
        references = list(csv.DictReader(handle))
    metadata = {row["Study ID"]: row for row in references}
    expected = {f"P{i:03}" for i in range(1, 91)}
    if len(references) != 90 or set(metadata) != expected:
        raise ValueError("Expected the preserved 90 unique seed identifiers")
    # Snapshot 01 is pinned to checkpoint 11; later screening must not silently
    # rewrite this historical synthesis. Create a new snapshot for a new basis.
    paths = [ROOT / f"literature/screening/full_text_{i:02}.json" for i in range(1, 12)]
    if not all(path.is_file() for path in paths):
        raise ValueError("Snapshot 01 requires full-text checkpoints 01 through 11")
    records, history, features = {}, {}, {}
    sources = []
    for path in paths:
        register = json.loads(path.read_text(encoding="utf-8"))
        rel = path.relative_to(ROOT).as_posix()
        sources.append({"path": rel, "sha256": digest(path)})
        for record in register["records"]:
            sid = record["study_id"]
            if sid not in expected:
                raise ValueError(f"Unrecognized identifier: {sid}")
            if not record["assessment_complete"] or record["decision"] not in ("include", "exclude"):
                raise ValueError(f"Incomplete/invalid assessment in records: {sid}")
            history.setdefault(sid, []).append(rel)
            for field, value in record.get("feature_codes", {}).items():
                if field not in FEATURES or value not in VALUES[:3]:
                    raise ValueError(f"Invalid extracted feature: {sid} {field}={value}")
                features.setdefault(sid, {})[field] = {
                    "value": value,
                    "register": rel,
                    "source_url": record["source_url"],
                    "locator": record.get("feature_locator", record.get("read_extent", "")),
                }
            records[sid] = {**record, "register": rel}
    latest = json.loads(paths[-1].read_text(encoding="utf-8"))
    included = sorted(sid for sid, r in records.items() if r["decision"] == "include")
    excluded = sorted(sid for sid, r in records.items() if r["decision"] == "exclude")
    pending = sorted(expected - records.keys())
    counts = {
        "seed_records": len(metadata),
        "ai_full_text_assessed": len(records),
        "ai_include": len(included),
        "ai_exclude": len(excluded),
        "remaining_ai_full_text": len(pending),
        "formal_included": latest["counts"]["formal_included"],
        "formal_excluded": latest["counts"]["formal_excluded"],
    }
    for key, value in counts.items():
        if value != latest["counts"][key]:
            raise ValueError(f"Count disagreement with latest register: {key}")
    coverage = {}
    for field, label in FEATURES.items():
        members = {v: [] for v in VALUES}
        for sid in included:
            value = features.get(sid, {}).get(field, {}).get("value", "Not extracted")
            members[value].append(sid)
        assert sum(map(len, members.values())) == len(included)
        coverage[field] = {
            "label": label,
            "denominator": len(included),
            "counts": {value: len(ids) for value, ids in members.items()},
            "record_ids": members,
        }
    inventory = []
    for sid in sorted(expected):
        row = metadata[sid]
        r = records.get(sid)
        inventory.append({
            "study_id": sid,
            "title": row["Title"],
            "metadata_status": "Draft reference metadata; not reverified by this aggregation",
            "doi": row["DOI"] or None,
            "primary_metadata_url": row["Primary source URL"],
            "synthesis_role": "main provisional synthesis" if sid in included else "ancillary excluded record" if sid in excluded else "pending; no full-text inference",
            "decision": r["decision"] if r else "pending",
            "assessment_history": history.get(sid, []),
            "evidence": {k: r[k] for k in ("register", "source_url", "version", "read_extent", "technical", "applicability") if k in r} if r else None,
            "feature_evidence": features.get(sid, {}),
        })
    return {
        "snapshot": "provisional_synthesis_01",
        "as_of": latest["checked_on"],
        "source_checkpoint": latest["checkpoint"],
        "protocol_version": latest["protocol_version"],
        "search_window": latest["search_window"],
        "counts": counts,
        "included_record_ids": included,
        "excluded_record_ids": excluded,
        "pending_record_ids": pending,
        "interpretation": [
            "AI include recommendations support provisional synthesis; they are not final formal inclusions.",
            "Counts describe records, not independent studies or field-wide prevalence; lineages remain unresolved.",
            "Only explicit full-text feature extractions are counted; missing fields remain Not extracted.",
            "No means not demonstrated in the inspected version/extent, not proven absence from every version.",
            "Yes means evaluated/present within the recorded scope, not successful calibration or a transferable guarantee.",
            "No meta-analysis or novelty inference is calculated from feature intersections.",
        ],
        "known_scope_caveats": [
            {"record_ids": ["P026", "P053"], "note": "Predecessor relationship confirmed in checkpoint 11; study-level grouping/shared experiments pending. Earlier P026 wording is historical."},
            {"record_ids": ["P064"], "field": "V", "note": "Legacy Yes describes projection-dependent tomography motion, whereas the dictionary says video-sequence variation. Preserve the extraction; do not interpret this count as a homogeneous video count. Adjudication pending."},
            {"record_ids": ["P071", "P073"], "field": "Q", "note": "Partial denotes categorical degradation weights, not a calibrated physical-parameter posterior."},
            {"record_ids": ["P042", "P063", "P073", "P077"], "field": "X", "note": "Certificate fallback, acquisition stopping, clean-class stopping and rollback are different decisions; no pooled selective-risk performance follows."},
        ],
        "source_files": sources + [{"path": reference_file.relative_to(ROOT).as_posix(), "sha256": digest(reference_file)}],
        "feature_coverage": coverage,
        "records": inventory,
    }


def render(snapshot: dict) -> str:
    c = snapshot["counts"]
    lines = [
        "# Evidence inventory for provisional synthesis 01", "",
        f"As of {snapshot['as_of']}; generated from {snapshot['source_checkpoint']} and earlier full-text registers.", "",
        f"**{c['seed_records']} seed records; {c['ai_full_text_assessed']} assessed; {c['ai_include']} AI include recommendations; {c['ai_exclude']} AI exclude recommendation; {c['remaining_ai_full_text']} pending. Formal included/excluded: {c['formal_included']}/{c['formal_excluded']}.**", "",
        "The main provisional synthesis uses the 88 include recommendations. P060 is ancillary; P035 contributes no full-text claims. These are record counts, not final PRISMA counts or independent-study counts.", "",
        "## Extraction coverage", "",
        "Every row has denominator 88. Missing extraction is not a negative finding. Yes indicates recorded evidence within its stated scope; calibration tested does not mean calibration succeeded. No means not demonstrated in the inspected evidence. Do not treat these counts as prevalence estimates.", "",
        "| Field | Yes | Partial | No | Not extracted |",
        "|---|---:|---:|---:|---:|",
    ]
    for info in snapshot["feature_coverage"].values():
        counts = info["counts"]
        lines.append(f"| {info['label']} | " + " | ".join(str(counts[v]) for v in VALUES) + " |")
    lines += ["", "## Interpretation limits", ""]
    for caveat in snapshot["known_scope_caveats"]:
        lines.append(f"- {', '.join(caveat['record_ids'])}: {caveat['note']}")
    lines += ["", "Only three extracted records have Q=Yes: P018 (BlindDPS), P019 (GibbsDDRM), and P038 (PRISM). That observation identifies comparators; it does not establish that only three such methods exist. The JSON snapshot contains every counted ID and its evidence locator.", "",
        "## Record index", "",
        "Titles are carried from the draft reference export. The linked register is authoritative for the inspected source/version, reading extent and limitations. Unassessed P035 is linked to its metadata page only.", "",
        "| ID | Title | AI decision | Evidence register |", "|---|---|---|---|",
    ]
    for r in snapshot["records"]:
        source = r["evidence"]["source_url"] if r["evidence"] else r["primary_metadata_url"]
        title = r["title"].replace("|", "\\|")
        evidence = r["evidence"]
        link = f"[{Path(evidence['register']).stem}](../screening/{Path(evidence['register']).name})" if evidence else "Full text pending"
        lines.append(f"| {r['study_id']} | [{title}]({source}) | {r['decision']} | {link} |")
    lines += ["", "## Reproduce", "", "```bash", "python scripts/build_synthesis_snapshot.py --check", "```", "",
        "Run without `--check` to regenerate this inventory and `evidence_snapshot_01.json`. The script verifies cumulative counts against the latest assessment checkpoint and retains per-field provenance. It does not update screening decisions or the workbook.", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the checked-in snapshot without writing")
    args = parser.parse_args()
    snapshot = build()
    files = {
        OUT / "evidence_snapshot_01.json": json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n",
        OUT / "evidence_inventory_01.md": render(snapshot),
    }
    if args.check:
        stale = [str(p.relative_to(ROOT)) for p, text in files.items() if not p.exists() or p.read_text(encoding="utf-8") != text]
        if stale:
            raise SystemExit("Missing/stale output: " + ", ".join(stale))
    else:
        OUT.mkdir(parents=True, exist_ok=True)
        for path, content in files.items():
            path.write_text(content, encoding="utf-8")
    print(json.dumps({"mode": "check" if args.check else "build", "counts": snapshot["counts"], "pending": snapshot["pending_record_ids"]}))


if __name__ == "__main__":
    main()
