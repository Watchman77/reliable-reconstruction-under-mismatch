#!/usr/bin/env python3
"""Statically validate the Stage 05C2 development reliability package."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
import tempfile
import types
from pathlib import Path

import numpy as np
from sklearn.isotonic import IsotonicRegression  # noqa: F401 - preload before torch stub


PROTOCOL_SHA256 = "b92c6cf73e05f60dc1edb3a31d88d91623e9ae0cf63d6265e6398e335928794c"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_with_torch_stubs(source: str):
    """Load pure helpers without installing the CUDA-only notebook dependencies."""

    original = {name: sys.modules.get(name) for name in ("torch", "torchvision")}
    torch_stub = types.ModuleType("torch")
    torch_stub.nn = types.SimpleNamespace(Module=object)
    torchvision_stub = types.ModuleType("torchvision")
    sys.modules["torch"] = torch_stub
    sys.modules["torchvision"] = torchvision_stub
    module = types.ModuleType("independent_05_reliability_training_static")
    try:
        exec(compile(source, "<reliability_training_static>", "exec"), module.__dict__)
    finally:
        for name, value in original.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value
    return module


def exercise_calibration_helpers(module) -> dict:
    rng = np.random.default_rng(20260924)
    source_ids = np.repeat(np.arange(869, 901, dtype=np.int16), 32)
    latent = rng.uniform(0.0, 1.0, size=len(source_ids))
    target = (rng.uniform(size=len(source_ids)) < latent).astype(np.uint8)
    arrays = {
        "source_id": source_ids,
        "chain_index": np.tile(np.arange(len(source_ids), dtype=np.uint8) % 7, 1),
        "patch_index": np.tile(np.arange(32, dtype=np.int16), 32),
        "target_bad_detail_0p05": target,
    }
    for pipeline in module.PIPELINES:
        for score in module.HEURISTIC_SCORES:
            arrays[f"{pipeline}__score__{score}"] = np.clip(
                latent + rng.normal(0.0, 0.08, size=len(latent)), 0.0, 1.0
            ).astype(np.float32)
    arrays[module.ENSEMBLE_SCORE] = np.clip(
        latent + rng.normal(0.0, 0.04, size=len(latent)), 0.0, 1.0
    ).astype(np.float32)
    arrays[module.ENSEMBLE_VARIANCE] = rng.uniform(0.0, 0.02, size=len(latent)).astype(
        np.float32
    )
    with tempfile.TemporaryDirectory() as temporary:
        output_dir = Path(temporary)
        np.savez_compressed(output_dir / "calibration_predictions.npz", **arrays)
        receipt = module.fit_calibration_mappings(output_dir)
        artifact = load_json(output_dir / "calibration_mappings.json")
        diagnostics = (output_dir / "calibration_fit_diagnostics.csv").read_text(
            encoding="utf-8"
        )
        assert receipt["mapping_count"] == 11
        assert len(artifact["mappings"]) == 11
        assert "source_macro_brier_in_sample" in diagnostics
        assert artifact["test_inference_performed"] is False
    return {"synthetic_mapping_count": 11, "synthetic_sources": 32}


def validate(root: Path) -> dict[str, object]:
    implementation_path = root / "experiments/independent_05/reliability_training.py"
    protocol_path = root / "experiments/independent_05/protocol_freeze.json"
    registry_path = root / "experiments/independent_05/development_shard_registry.json"
    status_path = root / "experiments/independent_05/stage_05c_status.json"
    notebook_path = root / "notebooks/05C2_Development_Reliability_Training_and_Calibration.ipynb"
    builder_path = root / "build/build_notebook_05c2.py"
    verification_path = root / "experiments/independent_05/notebook_05c2_verification.json"

    assert sha256(protocol_path) == PROTOCOL_SHA256
    protocol = load_json(protocol_path)
    registry = load_json(registry_path)
    status = load_json(status_path)
    verification = load_json(verification_path)
    assert protocol["independent_test_run_authorized"] is False
    assert protocol["test_results_inspected"] is False
    assert registry["verified_shards"] == 12
    assert registry["next_expected_shard_index"] is None
    assert len(registry["shards"]) == 12
    assert sum(len(row["source_ids"]) for row in registry["shards"]) == 96
    assert registry["independent_test_run_authorized"] is False
    assert status["development_generation_complete"] is True
    assert status["development_reliability_notebook_prepared"] is True
    assert status["comparator_fitted"] is False
    assert status["calibration_fitted"] is False
    assert status["independent_test_run_authorized"] is False
    assert status["test_inference_performed"] is False

    source = implementation_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    top_level = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.ClassDef))
    }
    required = {
        "prepare_development_cache",
        "archive_shard_index",
        "persist_input_receipts",
        "PatchErrorNet",
        "fit_positive_weight",
        "train_member",
        "fit_ensemble",
        "collect_calibration_predictions",
        "fit_calibration_mappings",
        "build_diagnostic_figures",
        "finalize_development_bundle",
        "static_self_check",
    }
    assert required <= top_level
    assert "SAMPLING_8BIT_RGB_2400x2400" not in source
    assert "testimages.org" not in source.lower()
    assert "independent_test_run_authorized\": False" in source
    assert "device.type == \"cuda\"" in source

    module = load_with_torch_stubs(source)
    self_check = module.static_self_check()
    assert self_check == {
        "development_sources": 96,
        "fit_sources": 52,
        "early_stop_sources": 12,
        "calibration_sources": 32,
        "ensemble_members": 5,
        "calibration_mappings": 11,
        "test_loader_present": False,
        "test_inference_performed": False,
        "independent_test_run_authorized": False,
    }
    assert module.validate_frozen_protocol(protocol_path.read_text(encoding="utf-8")) == protocol
    calibration_check = exercise_calibration_helpers(module)

    notebook = load_json(notebook_path)
    assert notebook["nbformat"] == 4
    assert len(notebook["cells"]) == 14
    assert notebook["metadata"]["accelerator"] == "GPU"
    assert notebook["metadata"]["experiment"]["test_inference_authorized"] is False
    code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    assert len(code_cells) == 6
    hidden_cells = 0
    for cell_index, cell in enumerate(code_cells):
        assert cell.get("execution_count") is None
        assert cell.get("outputs") == []
        compile("".join(cell["source"]), f"{notebook_path.name}:cell-{cell_index}", "exec")
        if cell.get("metadata", {}).get("jupyter", {}).get("source_hidden") is True:
            hidden_cells += 1
    assert hidden_cells == 1
    notebook_source = "\n".join("".join(cell["source"]) for cell in notebook["cells"])
    assert sha256(implementation_path) in notebook_source
    assert PROTOCOL_SHA256 in notebook_source
    assert sha256(registry_path) in notebook_source
    assert sha256(status_path) in notebook_source
    assert "MEMBER_INDICES_TEXT = '0,1,2,3,4'" in notebook_source
    assert "Calibration skipped until all five ensemble members are complete." in notebook_source
    assert "Independent test run authorized: false" in notebook_source

    compile(builder_path.read_text(encoding="utf-8"), str(builder_path), "exec")
    assert verification["status"] == "pass_static_requires_cuda_execution"
    assert verification["notebook"]["sha256"] == sha256(notebook_path)
    assert verification["notebook"]["cell_count"] == 14
    assert verification["notebook"]["code_cell_count"] == 6
    assert verification["implementation"]["sha256"] == sha256(implementation_path)
    assert verification["protocol_sha256"] == PROTOCOL_SHA256
    assert verification["development_inputs"]["verified_shards"] == 12
    assert verification["frozen_scope"]["test_inference_performed"] is False
    assert verification["frozen_scope"]["independent_test_run_authorized"] is False

    return {
        "status": "pass_static_requires_cuda_execution",
        "notebook": notebook_path.name,
        "notebook_sha256": sha256(notebook_path),
        "notebook_cells": 14,
        "code_cells": 6,
        "hidden_code_cells": hidden_cells,
        "implementation_sha256": sha256(implementation_path),
        "protocol_sha256": PROTOCOL_SHA256,
        "development_shards": 12,
        "development_observations": 672,
        **calibration_check,
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
