#!/usr/bin/env python3
"""Independently validate a returned Stage 05C2 result ZIP and notebook.

This validator checks the full export manifest, model/history receipts,
development partitions, calibration arrays and mappings, reproduced diagnostic
metrics, the sealed-test firewall, and (when supplied) the executed notebook.
It does not authorize independent-test inference or treat development-fit
diagnostics as independent calibration evidence.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import math
import re
import zipfile
from pathlib import Path, PurePosixPath

import numpy as np


PROTOCOL_SHA256 = "b92c6cf73e05f60dc1edb3a31d88d91623e9ae0cf63d6265e6398e335928794c"
ENSEMBLE_SEEDS = tuple(range(2026092101, 2026092106))
FIT_SOURCES = tuple(f"{value:04d}" for value in range(805, 857))
EARLY_STOP_SOURCES = tuple(f"{value:04d}" for value in range(857, 869))
CALIBRATION_SOURCES = tuple(f"{value:04d}" for value in range(869, 901))
CHAIN_IDS = (
    "q8_b16_n2",
    "j90_b16_n2",
    "j75_b16_n2",
    "j50_b16_n2",
    "j75_b12_n2",
    "j75_b20_n2",
    "j75_b16_n5",
)
PIPELINES = ("dpir_nominal", "fbcnn_dpir_nominal")
HEURISTIC_SCORES = (
    "operator_spread_detail",
    "operator_spread_rgb",
    "image_transform_spread_detail",
    "original_measurement_residual",
    "reconstruction_gradient",
)
ENSEMBLE_SCORE = "fbcnn_dpir_nominal__trained_image_only_patcherrornet_ensemble"
ENSEMBLE_VARIANCE = "fbcnn_dpir_nominal__patcherrornet_ensemble_variance"
SCORE_KEYS = tuple(
    f"{pipeline}__score__{score}"
    for pipeline in PIPELINES
    for score in HEURISTIC_SCORES
) + (ENSEMBLE_SCORE,)
EXPECTED_ARRAYS = {
    "source_id",
    "chain_index",
    "patch_index",
    "target_bad_detail_0p05",
    *SCORE_KEYS,
    ENSEMBLE_VARIANCE,
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json(payload: bytes):
    return json.loads(payload.decode("utf-8"))


def _rows(payload: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(payload.decode("utf-8"))))


def _source_equal_weights(source_ids: np.ndarray) -> np.ndarray:
    unique, counts = np.unique(source_ids, return_counts=True)
    count_map = dict(zip(unique.tolist(), counts.tolist()))
    weights = np.asarray(
        [1.0 / count_map[int(source)] for source in source_ids], dtype=np.float64
    )
    for source in unique:
        assert math.isclose(float(weights[source_ids == source].sum()), 1.0, abs_tol=1e-12)
    return weights


def _source_macro_brier(
    probability: np.ndarray, target: np.ndarray, source_ids: np.ndarray
) -> float:
    return float(
        np.mean(
            [
                np.mean((probability[source_ids == source] - target[source_ids == source]) ** 2)
                for source in np.unique(source_ids)
            ]
        )
    )


def _equal_mass_ece(
    probability: np.ndarray, target: np.ndarray, weights: np.ndarray, bins: int = 10
) -> float:
    order = np.argsort(probability, kind="mergesort")
    p, y, w = probability[order], target[order], weights[order]
    cumulative = np.cumsum(w) - 0.5 * w
    assignments = np.minimum((cumulative / w.sum() * bins).astype(int), bins - 1)
    result = 0.0
    for bin_index in range(bins):
        selected = assignments == bin_index
        if selected.any():
            mass = float(w[selected].sum())
            confidence = float(np.average(p[selected], weights=w[selected]))
            frequency = float(np.average(y[selected], weights=w[selected]))
            result += mass / float(w.sum()) * abs(confidence - frequency)
    return result


def _mapped(values: np.ndarray, mapping: dict) -> np.ndarray:
    x = np.asarray(mapping["x_thresholds"], dtype=np.float64)
    y = np.asarray(mapping["y_thresholds"], dtype=np.float64)
    oriented = np.asarray(values, dtype=np.float64) * float(mapping["orientation"])
    return np.interp(oriented, x, y, left=y[0], right=y[-1])


def _validate_notebook(
    notebook_path: Path,
    canonical_notebook_path: Path,
    archive_sha256: str,
    archive_filename: str,
    figure_hashes: set[str],
) -> dict[str, object]:
    notebook_bytes = notebook_path.read_bytes()
    notebook = json.loads(notebook_bytes)
    canonical = json.loads(canonical_notebook_path.read_text(encoding="utf-8"))
    assert notebook["nbformat"] == canonical["nbformat"] == 4
    assert len(notebook["cells"]) == len(canonical["cells"]) == 14

    def normalized_source(cell: dict) -> str:
        source = "".join(cell.get("source", []))
        return re.sub(
            r"(?m)^SHARD_ARCHIVE_DIR_TEXT\s*=\s*.*$",
            "SHARD_ARCHIVE_DIR_TEXT = '<RUNTIME_PATH>'",
            source,
        )

    for returned_cell, canonical_cell in zip(notebook["cells"], canonical["cells"]):
        assert returned_cell["cell_type"] == canonical_cell["cell_type"]
        assert normalized_source(returned_cell) == normalized_source(canonical_cell)

    code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    assert len(code_cells) == 6
    execution_counts = [cell.get("execution_count") for cell in code_cells]
    assert all(isinstance(value, int) for value in execution_counts)
    assert execution_counts == sorted(execution_counts)
    assert len(set(execution_counts)) == len(execution_counts)
    outputs = [output for cell in code_cells for output in cell.get("outputs", [])]
    assert not any(output.get("output_type") == "error" for output in outputs)

    output_text_parts: list[str] = []
    embedded_png_hashes: set[str] = set()
    for output in outputs:
        text = output.get("text")
        if isinstance(text, list):
            output_text_parts.extend(text)
        elif isinstance(text, str):
            output_text_parts.append(text)
        data = output.get("data", {})
        plain = data.get("text/plain")
        if isinstance(plain, list):
            output_text_parts.extend(plain)
        elif isinstance(plain, str):
            output_text_parts.append(plain)
        encoded_png = data.get("image/png")
        if isinstance(encoded_png, list):
            encoded_png = "".join(encoded_png)
        if isinstance(encoded_png, str):
            embedded_png_hashes.add(sha256_bytes(base64.b64decode(encoded_png)))
    output_text = "".join(output_text_parts)
    assert archive_sha256 in output_text
    assert archive_filename in output_text
    assert figure_hashes <= embedded_png_hashes

    return {
        "filename": notebook_path.name,
        "byte_count": len(notebook_bytes),
        "sha256": sha256_bytes(notebook_bytes),
        "cells": len(notebook["cells"]),
        "code_cells": len(code_cells),
        "execution_counts": execution_counts,
        "error_outputs": 0,
        "source_match": "canonical_except_runtime_archive_directory",
        "reported_archive_sha256_match": True,
        "embedded_figure_hashes_match": True,
    }


def validate(
    archive_path: Path,
    notebook_path: Path | None = None,
    canonical_notebook_path: Path | None = None,
) -> dict[str, object]:
    archive_path = Path(archive_path)
    archive_sha256 = sha256_file(archive_path)
    archive_byte_count = archive_path.stat().st_size

    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        assert names and len(names) == len(set(names))
        assert archive.testzip() is None
        assert not any(
            name.startswith("/") or ".." in PurePosixPath(name).parts for name in names
        )
        assert "export_manifest.json" in names

        manifest_payload = archive.read("export_manifest.json")
        manifest = _json(manifest_payload)
        listed = {row["path"]: row for row in manifest["files"]}
        actual = {
            name for name in names if name != "export_manifest.json" and not name.endswith("/")
        }
        assert actual == set(listed)
        assert len(listed) == 27
        for relative, row in listed.items():
            payload = archive.read(relative)
            assert len(payload) == int(row["byte_count"]), relative
            assert sha256_bytes(payload) == row["sha256"], relative

        for guard in (manifest,):
            assert guard["role"] == "development_only"
            assert guard["test_inference_performed"] is False
            assert guard["independent_test_run_authorized"] is False

        status = _json(archive.read("status.json"))
        checks = _json(archive.read("checks.json"))
        ensemble = _json(archive.read("ensemble_training_receipt.json"))
        calibration = _json(archive.read("calibration_receipt.json"))
        prediction_receipt = _json(archive.read("calibration_prediction_receipt.json"))
        cache_receipt = _json(archive.read("input_receipts/development_cache_receipt.json"))
        mappings_artifact = _json(archive.read("calibration_mappings.json"))

        guarded_documents = (
            status,
            checks,
            ensemble,
            calibration,
            prediction_receipt,
            cache_receipt,
            mappings_artifact,
        )
        for document in guarded_documents:
            assert document["test_inference_performed"] is False
            assert document["independent_test_run_authorized"] is False

        assert status["status"] == "passed_development_reliability_fit"
        assert status["comparator_fitted"] is True
        assert status["calibration_fitted"] is True
        assert status["test_performance_inspected"] is False
        assert status["ensemble_members"] == 5
        assert status["calibration_mappings"] == 11
        assert (status["fit_sources"], status["early_stop_sources"], status["calibration_sources"]) == (
            52,
            12,
            32,
        )

        assert checks == {
            "calibration_mapping_count": 11,
            "development_source_union": 96,
            "ensemble_members": 5,
            "independent_test_run_authorized": False,
            "member_history_files": 5,
            "member_model_files": 5,
            "partitions_disjoint": True,
            "protocol_sha256": PROTOCOL_SHA256,
            "test_inference_performed": False,
            "test_loader_present": False,
        }
        assert cache_receipt["archives_verified"] == 12
        assert cache_receipt["manifest_files_checked"] == 1488
        assert cache_receipt["manifest_mismatches"] == 0
        assert cache_receipt["sources"] == 96
        assert cache_receipt["observations"] == 672
        assert cache_receipt["partition_sources"] == {
            "fit": 52,
            "early_stop": 12,
            "calibration": 32,
        }
        assert sorted(row["shard_index"] for row in cache_receipt["shards"]) == list(range(12))

        index_rows = _rows(archive.read("input_receipts/development_compact_index.csv"))
        assert len(index_rows) == 672
        assert len({row["observation_id"] for row in index_rows}) == 672
        assert {row["source_id"].zfill(4) for row in index_rows} == set(
            FIT_SOURCES + EARLY_STOP_SOURCES + CALIBRATION_SOURCES
        )
        assert {row["chain_id"] for row in index_rows} == set(CHAIN_IDS)
        per_source: dict[str, int] = {}
        for row in index_rows:
            source_id = row["source_id"].zfill(4)
            per_source[source_id] = per_source.get(source_id, 0) + 1
        assert set(per_source.values()) == {7}

        assert ensemble["ensemble_complete"] is True
        assert ensemble["comparator_fitted"] is True
        assert ensemble["calibration_fitted"] is False
        assert ensemble["ensemble_members"] == 5
        assert tuple(ensemble["member_seeds"]) == ENSEMBLE_SEEDS
        assert len(ensemble["members"]) == 5

        member_summary = []
        for member_index, expected_seed in enumerate(ENSEMBLE_SEEDS):
            receipt_path = f"models/member_{member_index:02d}_receipt.json"
            history_path = f"models/member_{member_index:02d}_history.csv"
            model_path = f"models/member_{member_index:02d}_best.pt"
            member = _json(archive.read(receipt_path))
            assert member == ensemble["members"][member_index]
            assert member["member_index"] == member_index
            assert member["member_seed"] == expected_seed
            assert tuple(member["fit_sources"]) == FIT_SOURCES
            assert tuple(member["early_stop_sources"]) == EARLY_STOP_SOURCES
            assert member["calibration_sources_used"] is False
            assert member["class_balance"] == {
                "fit_negative_patches": 297310,
                "fit_patches": 372736,
                "fit_positive_patches": 75426,
                "positive_weight": 3.9417442261289213,
            }
            environment = member["environment_history"]
            assert len(environment) == 1
            assert environment[0]["device_type"] == "cuda"
            assert environment[0]["deterministic_algorithms"] is True

            model_payload = archive.read(model_path)
            assert len(model_payload) == member["model_byte_count"]
            assert sha256_bytes(model_payload) == member["model_sha256"]
            with zipfile.ZipFile(io.BytesIO(model_payload)) as model_archive:
                model_names = model_archive.namelist()
                assert any(name.endswith("/data.pkl") for name in model_names)
                assert any("/data/" in name for name in model_names)

            history = _rows(archive.read(history_path))
            assert len(history) == member["epochs_completed"]
            assert all(int(row["member_index"]) == member_index for row in history)
            assert all(int(row["member_seed"]) == expected_seed for row in history)
            best_rows = [row for row in history if row["best_so_far"].lower() == "true"]
            best = min(history, key=lambda row: float(row["early_stop_source_macro_brier"]))
            assert int(best["epoch"]) == member["best_epoch"]
            assert math.isclose(
                float(best["early_stop_source_macro_brier"]),
                member["best_early_stop_source_macro_brier"],
                rel_tol=0,
                abs_tol=1e-15,
            )
            assert best_rows[-1] == best
            assert member["epochs_completed"] - member["best_epoch"] == 5
            member_summary.append(
                {
                    "member_index": member_index,
                    "seed": expected_seed,
                    "epochs_completed": member["epochs_completed"],
                    "best_epoch": member["best_epoch"],
                    "best_early_stop_source_macro_brier": member[
                        "best_early_stop_source_macro_brier"
                    ],
                    "model_sha256": member["model_sha256"],
                }
            )

        prediction_payload = archive.read("calibration_predictions.npz")
        assert len(prediction_payload) == prediction_receipt["byte_count"]
        assert sha256_bytes(prediction_payload) == prediction_receipt["sha256"]
        with np.load(io.BytesIO(prediction_payload), allow_pickle=False) as stored:
            assert set(stored.files) == EXPECTED_ARRAYS
            arrays = {name: stored[name] for name in stored.files}
        lengths = {name: len(array) for name, array in arrays.items()}
        assert set(lengths.values()) == {229376}
        source_ids = arrays["source_id"].astype(np.int16)
        target = arrays["target_bad_detail_0p05"].astype(np.float64)
        assert tuple(f"{value:04d}" for value in sorted(np.unique(source_ids))) == CALIBRATION_SOURCES
        assert set(np.unique(arrays["chain_index"]).tolist()) == set(range(7))
        assert set(np.unique(target).tolist()) <= {0.0, 1.0}
        for name, array in arrays.items():
            if np.issubdtype(array.dtype, np.number):
                assert np.isfinite(array).all(), name
        assert prediction_receipt["sources"] == 32
        assert prediction_receipt["observations"] == 224
        assert prediction_receipt["patch_rows"] == 229376
        assert prediction_receipt["operational_scores"] == 11
        assert prediction_receipt["ensemble_members"] == 5

        assert mappings_artifact["protocol_sha256"] == PROTOCOL_SHA256
        assert mappings_artifact["fit_partition"] == "DIV2K 0869-0900 only"
        assert mappings_artifact["method"] == "isotonic_regression"
        mappings = mappings_artifact["mappings"]
        assert set(mappings) == set(SCORE_KEYS)
        assert calibration["calibration_fitted"] is True
        assert calibration["mapping_count"] == 11
        assert calibration["calibration_source_count"] == 32
        assert calibration["calibration_patch_rows"] == 229376
        assert calibration["mappings_sha256"] == listed["calibration_mappings.json"]["sha256"]
        assert calibration["diagnostics_sha256"] == listed["calibration_fit_diagnostics.csv"]["sha256"]

        diagnostics = {
            row["score"]: row for row in _rows(archive.read("calibration_fit_diagnostics.csv"))
        }
        assert set(diagnostics) == set(SCORE_KEYS)
        weights = _source_equal_weights(source_ids)
        maximum_diagnostic_error = 0.0
        for score_key in SCORE_KEYS:
            mapping = mappings[score_key]
            x = np.asarray(mapping["x_thresholds"], dtype=np.float64)
            y = np.asarray(mapping["y_thresholds"], dtype=np.float64)
            assert mapping["score"] == score_key
            assert mapping["orientation"] == 1.0
            assert mapping["out_of_bounds"] == "clip"
            assert len(x) == len(y) >= 2
            assert np.all(np.diff(x) > 0)
            assert np.all(np.diff(y) >= 0)
            assert 0 <= float(y.min()) <= float(y.max()) <= 1
            probability = _mapped(arrays[score_key], mapping)
            calculated = {
                "source_macro_brier_in_sample": _source_macro_brier(
                    probability, target, source_ids
                ),
                "equal_mass_ece_10bin_in_sample": _equal_mass_ece(
                    probability, target, weights
                ),
                "calibration_in_the_large_in_sample": float(
                    np.average(target - probability, weights=weights)
                ),
            }
            row = diagnostics[score_key]
            assert int(row["calibration_sources"]) == 32
            assert int(row["calibration_patch_rows"]) == 229376
            assert int(row["mapping_knots"]) == len(x)
            for field, value in calculated.items():
                error = abs(value - float(row[field]))
                maximum_diagnostic_error = max(maximum_diagnostic_error, error)
                assert error <= 1e-12, (score_key, field, error)

        figure_hashes = {
            listed["figures/development_calibration_reliability.png"]["sha256"],
            listed["figures/patcherrornet_early_stop_history.png"]["sha256"],
        }

    notebook_report = None
    if notebook_path is not None:
        assert canonical_notebook_path is not None
        notebook_report = _validate_notebook(
            Path(notebook_path),
            Path(canonical_notebook_path),
            archive_sha256,
            archive_path.name,
            figure_hashes,
        )

    return {
        "status": "pass_development_reliability_readback_verified",
        "validator": "scripts/validate_independent_05c2_result.py",
        "archive": {
            "filename": archive_path.name,
            "byte_count": archive_byte_count,
            "sha256": archive_sha256,
            "manifest_sha256": sha256_bytes(manifest_payload),
            "manifested_files": 27,
            "manifest_mismatches": 0,
        },
        "development_inputs": {
            "shard_archives": 12,
            "manifest_files_checked": 1488,
            "sources": 96,
            "observations": 672,
            "fit_sources": 52,
            "early_stop_sources": 12,
            "calibration_sources": 32,
        },
        "ensemble": {
            "members": 5,
            "member_summary": member_summary,
            "fit_patches_per_member": 372736,
            "calibration_sources_used_for_training": False,
        },
        "calibration": {
            "mappings": 11,
            "patch_rows": 229376,
            "source_count": 32,
            "target_bad_rate": float(target.mean()),
            "maximum_recalculation_error": maximum_diagnostic_error,
            "diagnostics_scope": "development_fit_only",
        },
        "notebook": notebook_report,
        "claim_boundary": (
            "Development fitting and serialization are verified; independent calibration, "
            "held-out performance, and the final novelty claim remain unestablished."
        ),
        "test_loader_present": False,
        "test_inference_performed": False,
        "test_performance_inspected": False,
        "independent_test_run_authorized": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--executed-notebook", type=Path)
    parser.add_argument(
        "--canonical-notebook",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "notebooks/05C2_Development_Reliability_Training_and_Calibration.ipynb",
    )
    args = parser.parse_args()
    report = validate(
        args.archive,
        notebook_path=args.executed_notebook,
        canonical_notebook_path=args.canonical_notebook,
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
