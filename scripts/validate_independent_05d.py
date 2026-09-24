#!/usr/bin/env python3
"""Static and synthetic validation for the locked Stage-05D implementation."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import sys
import types
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments" / "independent_05"
RUNNER = BASE / "independent_run.py"
PROTOCOL = BASE / "protocol_freeze.json"
RECEIPT = BASE / "data_receipt.json"
TRANSITION = BASE / "stage_05d_transition.json"
AMENDMENT = BASE / "amendments" / "0002_stage_05d_execution_clarifications.json"
NOTEBOOK = ROOT / "notebooks" / "05D_Locked_Independent_Evaluation_Shards.ipynb"
EXPECTED_PROTOCOL_SHA256 = "b92c6cf73e05f60dc1edb3a31d88d91623e9ae0cf63d6265e6398e335928794c"
EXPECTED_RECEIPT_SHA256 = "ad48eb7a65b043173f1012035b4a4c95d0299420614311bdfc6611ef840169cb"


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_runner():
    original = sys.modules.get("torch")
    sys.modules["torch"] = types.ModuleType("torch")
    try:
        specification = importlib.util.spec_from_file_location("independent_05d", RUNNER)
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)
        return module
    finally:
        if original is None:
            del sys.modules["torch"]
        else:
            sys.modules["torch"] = original


def literal_assignments(source: str) -> dict:
    result = {}
    for node in ast.parse(source).body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name):
            try:
                result[target.id] = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                pass
    return result


def validate_lock(module) -> dict:
    assert sha256(PROTOCOL) == EXPECTED_PROTOCOL_SHA256
    assert sha256(RECEIPT) == EXPECTED_RECEIPT_SHA256
    run_hash = sha256(RUNNER)
    protocol_text = PROTOCOL.read_text(encoding="utf-8")
    receipt_text = RECEIPT.read_text(encoding="utf-8")
    transition_text = TRANSITION.read_text(encoding="utf-8")
    protocol, receipt, transition = module.validate_frozen_inputs(
        protocol_text, receipt_text, transition_text, run_hash
    )
    amendment = json.loads(AMENDMENT.read_text(encoding="utf-8"))
    assert amendment["outcome_blind"] is True
    assert amendment["independent_test_output_existed"] is False
    assert amendment["independent_test_inference_performed"] is False
    assert amendment["scientific_design_changed"] is False
    assert transition["amendment_path"].endswith(AMENDMENT.name)
    assert [row["requirement"] for row in transition["readiness_assertions"]] == protocol[
        "readiness_requirements_before_independent_inference"
    ]
    shards = [module.sources_for_shard(receipt, index) for index in range(5)]
    flattened = [source for shard in shards for source in shard]
    assert len(flattened) == len(set(flattened)) == 40
    assert tuple(flattened) == module.ordered_test_sources(receipt)
    for index, shard in enumerate(shards):
        assert list(shard) == transition["sharding"]["source_ids_by_shard"][str(index)]
    return {
        "protocol_sha256": EXPECTED_PROTOCOL_SHA256,
        "data_receipt_sha256": EXPECTED_RECEIPT_SHA256,
        "run_code_sha256": run_hash,
        "transition_sha256": sha256(TRANSITION),
        "amendment_sha256": sha256(AMENDMENT),
        "readiness_assertions": len(transition["readiness_assertions"]),
        "fixed_shards": len(shards),
        "fixed_sources": len(flattened),
    }


def validate_runner_structure() -> dict:
    source = RUNNER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    required = {
        "validate_frozen_inputs",
        "sources_for_shard",
        "inspect_reliability_archive",
        "load_test_sources",
        "_risk_rows",
        "compact_arrays",
        "run_shard",
        "static_self_check",
    }
    assert required <= set(functions)
    assert "matplotlib" not in source
    assert ".plot(" not in source and "display(" not in source
    assert "test_performance_inspected\": False" in source
    assert "aggregate_analysis_performed\": False" in source
    assert "unsealed\": False" in source

    run_calls = {
        node.func.id
        for node in ast.walk(functions["run_shard"])
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert {
        "validate_frozen_inputs",
        "sources_for_shard",
        "inspect_reliability_archive",
        "load_test_sources",
        "compact_arrays",
        "_risk_rows",
    } <= run_calls
    attributes = {
        node.attr
        for node in ast.walk(functions["run_shard"])
        if isinstance(node, ast.Attribute)
    }
    assert {"load_frozen_ensemble", "ensemble_probabilities"} <= attributes
    run_segment = ast.get_source_segment(source, functions["run_shard"])
    assert '"target_bad_detail_0p05"' in run_segment
    assert "configure_determinism" in run_segment

    printed_source = "\n".join(
        ast.get_source_segment(source, node) or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "print"
    )
    for forbidden in ("detail_mse", "rgb_mse", "psnr", "brier", "ece", "p_value"):
        assert forbidden not in printed_source.lower()
    return {
        "functions": len(functions),
        "required_guards_present": True,
        "plotting_code_present": False,
        "metric_print_code_present": False,
    }


def validate_synthetic_risk(module) -> dict:
    patch_count = module.PATCHES_PER_OBSERVATION
    base = np.linspace(0.0, 1.0, patch_count, dtype=np.float64)
    estimates = {}
    scores = {}
    for pipeline_index, pipeline in enumerate(module.PIPELINES):
        estimates[f"{pipeline}__rgb_patch_error"] = 0.1 + base + pipeline_index
        estimates[f"{pipeline}__detail_patch_error"] = 0.2 + base[::-1] + pipeline_index
        for score_index, score in enumerate(module.HEURISTIC_SCORES):
            scores[f"{pipeline}__score__{score}"] = np.roll(base, score_index)
    scores["fbcnn_dpir_nominal__score__reference_texture"] = base
    ensemble = base.copy()
    rows = module._risk_rows(
        estimates,
        scores,
        ensemble,
        {"coverages": [0.5, 0.75, 0.9, 1.0], "detail_rmse_tolerances": [0.025, 0.05, 0.1]},
    )
    assert len(rows) == 120
    keys = {
        (row["pipeline"], row["region"], row["score_key"], row["coverage"])
        for row in rows
    }
    assert len(keys) == 120
    h2 = [
        row
        for row in rows
        if row["pipeline"] == "fbcnn_dpir_nominal"
        and row["region"] == "all"
        and row["coverage"] == 0.5
        and row["score"] in {"operator_spread_detail", "image_transform_spread_detail"}
    ]
    assert len(h2) == 2
    ensemble_rows = [
        row
        for row in rows
        if row["pipeline"] == "fbcnn_dpir_nominal"
        and row["score"] == "trained_image_only_patcherrornet_ensemble"
    ]
    assert len(ensemble_rows) == 8
    random_rows = [
        row
        for row in rows
        if row["pipeline"] == "dpir_nominal"
        and row["region"] == "all"
        and row["score"] == "expected_random"
    ]
    assert len(random_rows) == 4
    assert len({row["detail_mse"] for row in random_rows}) == 1
    assert [row["retained_patches"] for row in random_rows] == [512, 768, 922, 1024]
    return {
        "synthetic_risk_rows": len(rows),
        "unique_risk_cells": len(keys),
        "h2_primary_rows": len(h2),
        "ensemble_risk_rows": len(ensemble_rows),
        "expected_random_exact_expectation": True,
    }


def validate_notebook() -> dict:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert notebook["nbformat"] == 4
    metadata = notebook["metadata"]["experiment"]
    assert metadata["stage"] == "05D_locked_independent_inference"
    assert metadata["test_inference_authorized"] is True
    assert metadata["performance_inspection_authorized"] is False
    code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    assert len(code_cells) == 7
    assert all(cell["execution_count"] is None and not cell["outputs"] for cell in code_cells)
    for index, cell in enumerate(code_cells):
        compile("".join(cell["source"]), f"<05D code cell {index}>", "exec")

    embedded = literal_assignments("".join(code_cells[1]["source"]))
    expected = {
        "CANARY_SOURCE": BASE / "canary.py",
        "RELIABILITY_SOURCE": BASE / "reliability_training.py",
        "INDEPENDENT_SOURCE": RUNNER,
        "PROTOCOL_TEXT": PROTOCOL,
        "DATA_RECEIPT_TEXT": RECEIPT,
        "TRANSITION_TEXT": TRANSITION,
        "AMENDMENT_TEXT": AMENDMENT,
    }
    for variable, path in expected.items():
        assert embedded[variable] == path.read_text(encoding="utf-8"), variable

    visible_code = "\n".join("".join(cell["source"]) for cell in code_cells[2:])
    assert "SHARD_INDEX = 0" in visible_code
    assert "quality.csv" not in visible_code and "risk.csv" not in visible_code
    assert "display(" not in visible_code and ".plot(" not in visible_code
    assert "Performance values displayed: false" in visible_code
    assert "DO NOT OPEN THE RESULT FILES" in visible_code
    return {
        "notebook_sha256": sha256(NOTEBOOK),
        "cells": len(notebook["cells"]),
        "code_cells": len(code_cells),
        "embedded_sources_exact": len(expected),
        "outputs_present": False,
    }


def main() -> None:
    module = load_runner()
    report = {
        "status": "pass",
        "experiment_id": "independent_05",
        "stage": "05D_locked_independent_inference",
        "lock": validate_lock(module),
        "runner": validate_runner_structure(),
        "synthetic": validate_synthetic_risk(module),
        "notebook": validate_notebook(),
        "test_inference_performed": False,
        "test_performance_inspected": False,
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
