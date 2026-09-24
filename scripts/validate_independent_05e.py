#!/usr/bin/env python3
"""Validate the precommitted Stage-05E analysis and notebook without test data."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments" / "independent_05"
ANALYSIS = BASE / "independent_analysis.py"
LOCK = BASE / "stage_05e_analysis_lock.json"
RUNNER = BASE / "independent_run.py"
TRANSITION = BASE / "stage_05d_transition.json"
NOTEBOOK = ROOT / "notebooks" / "05E_One_Time_Locked_Independent_Analysis.ipynb"


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_analysis():
    specification = importlib.util.spec_from_file_location("independent_05e", ANALYSIS)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def literal_assignments(source: str) -> dict:
    result = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                result[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                pass
    return result


def validate_lock(module) -> dict:
    lock_text = LOCK.read_text(encoding="utf-8")
    lock = module.validate_analysis_lock(lock_text, sha256(ANALYSIS))
    assert lock["stage_05d_run_code_sha256"] == sha256(RUNNER)
    assert lock["stage_05d_transition_sha256"] == sha256(TRANSITION)
    transition = json.loads(TRANSITION.read_text(encoding="utf-8"))
    assert transition["run_code_sha256"] == sha256(RUNNER)
    assert transition["analysis_resolutions"]["h2_region"] == lock["h2_region"] == "all"
    transition_sources = transition["sharding"]["source_ids_by_shard"]
    assert lock["source_ids_by_shard"] == transition_sources
    flattened = [source for index in range(5) for source in transition_sources[str(index)]]
    assert len(flattened) == len(set(flattened)) == 40
    return {
        "analysis_code_sha256": sha256(ANALYSIS),
        "analysis_lock_sha256": sha256(LOCK),
        "stage_05d_run_code_sha256": sha256(RUNNER),
        "stage_05d_transition_sha256": sha256(TRANSITION),
        "locked_sources": len(flattened),
        "independent_results_existed_when_locked": False,
    }


def validate_structure() -> dict:
    source = ANALYSIS.read_text(encoding="utf-8")
    tree = ast.parse(source)
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    required = {
        "validate_analysis_lock",
        "inspect_shard",
        "bootstrap_multiplicities",
        "one_sided_sign_flip_pvalue",
        "holm_adjust",
        "primary_analysis",
        "calibration_assessment",
        "source_group_summary",
        "load_unsealed_data",
        "build_figures",
        "run_analysis",
    }
    assert required <= set(functions)
    assert "TO_BE_FINALIZED" not in source
    run_source = ast.get_source_segment(source, functions["run_analysis"])
    assert run_source.index("verified = [inspect_shard") < run_source.index("output_dir.mkdir")
    assert "assert not final_output_dir.exists()" in run_source
    assert "output_dir.replace(final_output_dir)" in run_source
    assert "final_literature_novelty_claim_established\": False" in source
    return {
        "functions": len(functions),
        "five_shards_verified_before_unsealing": True,
        "atomic_final_output": True,
        "one_time_guard": True,
    }


def validate_statistics(module) -> dict:
    multiplicities = module.bootstrap_multiplicities(40)
    assert np.array_equal(multiplicities, module.bootstrap_multiplicities(40))
    source_ids = [f"source_{index:02d}" for index in range(40)]
    quality, risk = [], []
    for index, source_id in enumerate(source_ids):
        comparator = 1.0 + index / 100.0
        favorable = 0.9 * comparator
        quality.extend(
            [
                {
                    "source_id": source_id,
                    "chain_id": module.PRIMARY_CHAIN,
                    "method": "dpir_nominal",
                    "detail_mse": comparator,
                },
                {
                    "source_id": source_id,
                    "chain_id": module.PRIMARY_CHAIN,
                    "method": "fbcnn_dpir_nominal",
                    "detail_mse": favorable,
                },
            ]
        )
        risk.extend(
            [
                {
                    "source_id": source_id,
                    "chain_id": module.PRIMARY_CHAIN,
                    "pipeline": "fbcnn_dpir_nominal",
                    "region": "all",
                    "coverage": 0.5,
                    "score": "image_transform_spread_detail",
                    "detail_mse": comparator,
                },
                {
                    "source_id": source_id,
                    "chain_id": module.PRIMARY_CHAIN,
                    "pipeline": "fbcnn_dpir_nominal",
                    "region": "all",
                    "coverage": 0.5,
                    "score": "operator_spread_detail",
                    "detail_mse": favorable,
                },
            ]
        )
    primary, contrasts = module.primary_analysis(
        pd.DataFrame(quality), pd.DataFrame(risk), source_ids, multiplicities
    )
    assert primary["both_confirmatory_gates_passed"] is True
    assert contrasts.shape == (40, 7)
    for result in primary["hypotheses"].values():
        assert np.isclose(result["relative_reduction"], 0.1)
        assert result["holm_adjusted_p_value"] < 0.05
        assert result["paired_source_bootstrap_95_ci"][1] < 0

    source_mass = np.full((40, 3), 1 / 3, dtype=np.float64)
    source_positive = source_mass * np.asarray([0.1, 0.5, 0.9])[None, :]
    logits = np.log(np.asarray([0.1, 0.5, 0.9]) / np.asarray([0.9, 0.5, 0.1]))
    slopes = module._logistic_slopes(
        source_mass,
        source_positive,
        logits,
        np.ones((1, 40), dtype=np.int16),
    )
    assert slopes.shape == (1,) and np.isclose(slopes[0], 1.0, atol=1e-8)
    assert module.holm_adjust({"H1": 0.01, "H2": 0.04}) == {"H1": 0.02, "H2": 0.04}
    return {
        "bootstrap_shape": list(multiplicities.shape),
        "bootstrap_deterministic": True,
        "synthetic_confirmatory_pass": True,
        "holm_check": True,
        "calibration_slope_check": float(slopes[0]),
    }


def validate_notebook() -> dict:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    metadata = notebook["metadata"]["experiment"]
    assert metadata["stage"] == "05E_one_time_locked_analysis"
    assert metadata["outcome_blind_analysis_locked"] is True
    code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    assert len(code_cells) == 6
    assert all(cell["execution_count"] is None and not cell["outputs"] for cell in code_cells)
    for index, cell in enumerate(code_cells):
        compile("".join(cell["source"]), f"<05E code cell {index}>", "exec")
    embedded = literal_assignments("".join(code_cells[1]["source"]))
    assert embedded["ANALYSIS_SOURCE"] == ANALYSIS.read_text(encoding="utf-8")
    assert embedded["ANALYSIS_LOCK_TEXT"] == LOCK.read_text(encoding="utf-8")
    assert embedded["EXPECTED_DIGESTS"]["analysis"] == sha256(ANALYSIS)
    assert embedded["EXPECTED_DIGESTS"]["lock"] == sha256(LOCK)
    return {
        "notebook_sha256": sha256(NOTEBOOK),
        "cells": len(notebook["cells"]),
        "code_cells": len(code_cells),
        "embedded_analysis_exact": True,
        "embedded_lock_exact": True,
        "outputs_present": False,
    }


def main() -> None:
    module = load_analysis()
    report = {
        "status": "pass",
        "experiment_id": "independent_05",
        "stage": "05E_one_time_locked_analysis",
        "lock": validate_lock(module),
        "structure": validate_structure(),
        "statistics": validate_statistics(module),
        "notebook": validate_notebook(),
        "test_inference_performed": False,
        "test_performance_inspected": False,
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
