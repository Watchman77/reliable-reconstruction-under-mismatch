#!/usr/bin/env python3
"""Validate outcome-blind stage-05C data and canary-preparation artifacts."""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
from pathlib import Path


PUBLISHER_SHA256 = "987e6a5208206b51bb556e808ea052aa588f373124bd0f571888a4754c6afa89"
DIV2K_SHA256 = "20dd31fd84d777bc1cf5d6b7654a3f569c0aec74458ae094122ad1d0489900fc"
CANARY_IDS = ("0805", "0806")
CANARY_CHAINS = ("q8_b16_n2", "j75_b16_n2")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(root: Path) -> dict[str, object]:
    protocol_path = root / "experiments/independent_05/protocol_freeze.json"
    receipt_path = root / "experiments/independent_05/data_receipt.json"
    duplicate_path = root / "experiments/independent_05/duplicate_audit.csv"
    status_path = root / "experiments/independent_05/stage_05c_status.json"
    canary_path = root / "experiments/independent_05/canary.py"
    notebook_path = root / "notebooks/05C_Independent_Validation_Engineering_Canary.ipynb"
    test_archive = root / "inputs/SAMPLING_8BIT_RGB_2400x2400.tar.bz2"
    div2k_archive = root / "inputs/DIV2K_valid_HR.zip"

    protocol = load_json(protocol_path)
    receipt = load_json(receipt_path)
    status = load_json(status_path)
    assert protocol["independent_test_run_authorized"] is False
    assert protocol["test_results_inspected"] is False
    assert tuple(protocol["development_partitions"]["engineering_canary_sources"]) == CANARY_IDS
    assert receipt["receipt_status"] == "pass"
    assert receipt["test_inference_performed"] is False
    assert receipt["test_performance_inspected"] is False
    assert receipt["test_archive"]["observed_sha256"] == PUBLISHER_SHA256
    assert receipt["test_archive"]["publisher_digest_match"] is True
    assert receipt["test_archive"]["eligible_source_count"] == 40
    assert len(receipt["test_archive"]["sources"]) == 40
    assert all(
        (row["width"], row["height"], row["mode"]) == (2400, 2400, "RGB")
        for row in receipt["test_archive"]["sources"]
    )
    assert receipt["development_archive"]["observed_sha256"] == DIV2K_SHA256
    assert receipt["development_archive"]["audited_source_count"] == 96
    assert len(receipt["development_archive"]["sources"]) == 96
    assert tuple(receipt["development_archive"]["canary_sources_extracted"]) == CANARY_IDS
    assert sha256(test_archive) == PUBLISHER_SHA256
    assert sha256(div2k_archive) == DIV2K_SHA256

    with duplicate_path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 40 * 96
    pairs = {(row["test_source_id"], row["development_source_id"]) for row in rows}
    assert len(pairs) == len(rows)
    assert not any(row["exact_sha256_match"] == "true" for row in rows)
    assert not any(row["near_duplicate_candidate"] == "true" for row in rows)
    assert all(row["manual_adjudication"] == "not_required" for row in rows)
    assert all(row["decision"] == "retain" for row in rows)
    assert receipt["duplicate_audit"]["sha256"] == sha256(duplicate_path)
    assert receipt["duplicate_audit"]["pair_count"] == len(rows)

    canary_source = canary_path.read_text(encoding="utf-8")
    tree = ast.parse(canary_source)
    top_level = {node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    required = {
        "derive_config",
        "validate_canary_scope",
        "load_canary_sources",
        "acquire",
        "PatchErrorNet",
        "run_canary",
    }
    assert required <= top_level
    for source_id in CANARY_IDS:
        assert source_id in canary_source
    for chain_id in CANARY_CHAINS:
        assert chain_id in canary_source
    assert "independent_test_run_authorized\"] is False" in canary_source
    assert "device.type == \"cuda\"" in canary_source

    notebook = load_json(notebook_path)
    assert notebook["nbformat"] == 4
    assert len(notebook["cells"]) == 15
    code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    for cell in code_cells:
        assert cell.get("execution_count") is None
        assert cell.get("outputs") == []
        compile("".join(cell["source"]), f"{notebook_path.name}:cell", "exec")
    notebook_source = "\n".join("".join(cell["source"]) for cell in notebook["cells"])
    assert hashlib.sha256(canary_source.encode("utf-8")).hexdigest() in notebook_source
    assert sha256(protocol_path) in notebook_source
    assert sha256(receipt_path) in notebook_source
    assert "TESTIMAGES inference performed: false" in notebook_source
    assert "Independent test run authorized: false" in notebook_source

    assert status["protocol_frozen"] is True
    assert status["dataset_downloaded_and_hashed"] is True
    assert status["test_archive_publisher_digest_match"] is True
    assert status["test_source_decode_check_complete"] is True
    assert status["near_duplicate_audit_complete"] is True
    assert status["canary_inputs_ready"] is True
    assert status["development_canary_passed"] is False
    assert status["independent_test_run_authorized"] is False
    assert status["test_inference_performed"] is False
    assert status["test_performance_inspected"] is False
    assert status["data_receipt"]["sha256"] == sha256(receipt_path)

    return {
        "status": "pass",
        "test_archive_sha256": PUBLISHER_SHA256,
        "test_sources": 40,
        "development_sources": 96,
        "duplicate_pairs": len(rows),
        "duplicate_candidates": 0,
        "canary_source_ids": list(CANARY_IDS),
        "canary_chain_ids": list(CANARY_CHAINS),
        "canary_notebook_cells": len(notebook["cells"]),
        "canary_notebook_execution": "not_run_requires_cuda",
        "test_inference_performed": False,
        "independent_test_run_authorized": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(json.dumps(validate(args.root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
