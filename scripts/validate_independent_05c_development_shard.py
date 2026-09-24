#!/usr/bin/env python3
"""Validate a returned stage-05C development-generation shard ZIP.

The validator is deliberately outcome-blind. It verifies container integrity,
the complete export manifest, table/record consistency, compact-array schemas,
selected metric recalculations, compute accounting, and the sealed-test guard.
It does not interpret reconstruction performance or authorize test inference.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path, PurePosixPath

import numpy as np
import pandas as pd


METHODS = (
    "observed",
    "gradient_nominal",
    "dpir_nominal",
    "fbcnn",
    "fbcnn_gradient_nominal",
    "fbcnn_dpir_nominal",
)
PIPELINES = ("dpir_nominal", "fbcnn_dpir_nominal")
SCORES = (
    "expected_random",
    "image_transform_spread_detail",
    "operator_spread_detail",
    "operator_spread_rgb",
    "oracle_detail_error",
    "original_measurement_residual",
    "reconstruction_gradient",
)
COMPACT_SCORES = tuple(
    score for score in SCORES if score not in {"expected_random", "oracle_detail_error"}
)
REGIONS = ("all", "textured_quartile")
CSV_NAMES = (
    "source_manifest.csv",
    "acquisition_repeat_check.csv",
    "acquisition.csv",
    "quality.csv",
    "risk.csv",
    "compute.csv",
    "trajectories.csv",
    "fbcnn_diagnostics.csv",
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _normalise_frame(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    result = frame.loc[:, columns].copy()
    if "source_id" in result:
        result["source_id"] = result["source_id"].astype(str).str.zfill(4)
    return result


def _assert_record_rows(
    frame: pd.DataFrame,
    record_rows: list[dict],
    source_id: str,
    chain_id: str,
    sort_columns: list[str],
) -> None:
    expected = frame[
        (frame.source_id == source_id) & (frame.chain_id == chain_id)
    ].copy()
    observed = pd.DataFrame(record_rows)
    observed["source_id"] = observed["source_id"].astype(str).str.zfill(4)
    observed = _normalise_frame(observed, list(expected.columns))
    expected = expected.sort_values(sort_columns).reset_index(drop=True)
    observed = observed.sort_values(sort_columns).reset_index(drop=True)
    assert len(expected) == len(observed)
    for column in expected.columns:
        left, right = expected[column], observed[column]
        left_nonempty = left.fillna("").astype(str).ne("")
        right_nonempty = right.fillna("").astype(str).ne("")
        left_numeric = pd.to_numeric(left.astype(object).where(left_nonempty), errors="coerce")
        right_numeric = pd.to_numeric(right.astype(object).where(right_nonempty), errors="coerce")
        numeric_compatible = (
            left_numeric[left_nonempty].notna().all()
            and right_numeric[right_nonempty].notna().all()
        )
        if pd.api.types.is_numeric_dtype(left) or numeric_compatible:
            assert np.allclose(
                left_numeric,
                right_numeric,
                rtol=0,
                atol=1e-12,
                equal_nan=True,
            ), column
        else:
            assert left.fillna("").astype(str).equals(right.fillna("").astype(str)), column


def validate(archive_path: Path, expected_outer_sha256: str | None = None) -> dict:
    archive_bytes = archive_path.read_bytes()
    outer_sha256 = sha256_bytes(archive_bytes)
    report: dict[str, object] = {
        "schema_version": "1.0.0",
        "validator": "scripts/validate_independent_05c_development_shard.py",
        "archive_filename": archive_path.name,
        "archive_byte_count": len(archive_bytes),
        "received_outer_sha256": outer_sha256,
        "expected_outer_sha256": expected_outer_sha256,
        "outer_sha256_match": None
        if expected_outer_sha256 is None
        else outer_sha256 == expected_outer_sha256,
    }

    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        names = archive.namelist()
        assert names and len(names) == len(set(names))
        assert archive.testzip() is None
        assert not any(
            name.startswith("/") or ".." in PurePosixPath(name).parts for name in names
        )
        roots = {name.split("/", 1)[0] for name in names}
        assert len(roots) == 1
        archive_root = roots.pop()

        def read(relative: str) -> bytes:
            return archive.read(f"{archive_root}/{relative}")

        manifest = json.loads(read("export_manifest.json"))
        listed = {row["path"]: row for row in manifest["files"]}
        actual = {
            name[len(archive_root) + 1 :]
            for name in names
            if name != f"{archive_root}/export_manifest.json" and not name.endswith("/")
        }
        assert actual == set(listed)
        for relative, row in listed.items():
            payload = read(relative)
            assert len(payload) == int(row["byte_count"])
            assert sha256_bytes(payload) == row["sha256"]

        config = json.loads(read("config.json"))
        checks = json.loads(read("checks.json"))
        status = json.loads(read("status.json"))
        provenance = json.loads(read("provenance.json"))
        frames = {
            name: pd.read_csv(io.BytesIO(read(name)), keep_default_na=False)
            for name in CSV_NAMES
        }
        for frame in frames.values():
            if "source_id" in frame:
                frame["source_id"] = frame["source_id"].astype(str).str.zfill(4)

        source_ids = tuple(config["source_ids"])
        chain_ids = tuple(config["chain_ids"])
        observations = len(source_ids) * len(chain_ids)
        assert 1 <= len(source_ids) <= 8
        assert len(chain_ids) == 7
        assert all(source_id.isdigit() and "0805" <= source_id <= "0900" for source_id in source_ids)
        assert len(set(source_ids)) == len(source_ids)
        assert len(set(chain_ids)) == len(chain_ids)
        assert tuple(status["source_ids"]) == source_ids
        assert tuple(status["chain_ids"]) == chain_ids
        assert tuple(manifest["source_ids"]) == source_ids
        assert tuple(manifest["chain_ids"]) == chain_ids

        expected_counts = {
            "source_manifest.csv": len(source_ids),
            "acquisition_repeat_check.csv": observations,
            "acquisition.csv": observations,
            "quality.csv": observations * len(METHODS),
            "risk.csv": observations * len(PIPELINES) * len(REGIONS) * len(SCORES) * 4,
            "compute.csv": observations * 15,
            "trajectories.csv": observations * 10 * 8,
            "fbcnn_diagnostics.csv": observations * 3,
        }
        assert {name: len(frame) for name, frame in frames.items()} == expected_counts

        acquisition = frames["acquisition.csv"]
        repeat = frames["acquisition_repeat_check.csv"]
        quality = frames["quality.csv"]
        risk = frames["risk.csv"]
        compute = frames["compute.csv"]
        trajectories = frames["trajectories.csv"]
        fbcnn = frames["fbcnn_diagnostics.csv"]
        assert not acquisition.duplicated(["source_id", "chain_id"]).any()
        assert not repeat.duplicated(["source_id", "chain_id"]).any()
        assert not quality.duplicated(["source_id", "chain_id", "method"]).any()
        assert not risk.duplicated(
            ["source_id", "chain_id", "pipeline", "region", "score", "coverage"]
        ).any()
        assert not compute.duplicated(["source_id", "chain_id", "component"]).any()
        assert not trajectories.duplicated(
            ["source_id", "chain_id", "component", "iteration"]
        ).any()
        assert not fbcnn.duplicated(
            ["source_id", "chain_id", "rotation_quarter_turns"]
        ).any()
        assert set(quality.method) == set(METHODS)
        assert set(risk.pipeline) == set(PIPELINES)
        assert set(risk.region) == set(REGIONS)
        assert set(risk.score) == set(SCORES)
        assert set(pd.to_numeric(risk.coverage)) == set(config["coverages"])
        assert repeat.repeat_identical.astype(str).str.lower().eq("true").all()

        record_paths = {PurePosixPath(path).stem: path for path in actual if path.startswith("records/")}
        compact_paths = {PurePosixPath(path).stem: path for path in actual if path.startswith("compact/")}
        expected_ids = {f"{source_id}_{chain_id}" for source_id in source_ids for chain_id in chain_ids}
        assert set(record_paths) == expected_ids
        assert set(compact_paths) == expected_ids

        required_arrays = {
            "observation_uint8",
            "fbcnn_dpir_nominal",
            "detail_patch_error",
            "target_bad_detail_0p05",
            *{
                f"{pipeline}__score__{score}"
                for pipeline in PIPELINES
                for score in COMPACT_SCORES
            },
        }
        max_quality_error = 0.0
        max_risk_error = 0.0
        recalculated_risk_rows = 0

        for observation_id in sorted(expected_ids):
            source_id = observation_id[:4]
            chain_id = observation_id[5:]
            record = json.loads(read(record_paths[observation_id]))
            assert record["source_id"] == source_id
            assert record["chain_id"] == chain_id

            compact_relative = compact_paths[observation_id]
            compact_payload = read(compact_relative)
            assert record["compact_file"]["path"] == compact_relative
            assert record["compact_file"]["byte_count"] == len(compact_payload)
            assert record["compact_file"]["sha256"] == sha256_bytes(compact_payload)
            assert set(record["compact_file"]["arrays"]) == required_arrays

            _assert_record_rows(
                acquisition,
                [record["acquisition"]],
                source_id,
                chain_id,
                ["source_id", "chain_id"],
            )
            _assert_record_rows(
                repeat,
                [record["acquisition_repeat"]],
                source_id,
                chain_id,
                ["source_id", "chain_id"],
            )
            _assert_record_rows(quality, record["quality"], source_id, chain_id, ["method"])
            _assert_record_rows(
                risk,
                record["risk"],
                source_id,
                chain_id,
                ["pipeline", "region", "score", "coverage"],
            )
            _assert_record_rows(compute, record["compute"], source_id, chain_id, ["component"])
            _assert_record_rows(
                trajectories,
                record["trajectories"],
                source_id,
                chain_id,
                ["component", "iteration"],
            )
            _assert_record_rows(
                fbcnn,
                record["fbcnn_diagnostics"],
                source_id,
                chain_id,
                ["rotation_quarter_turns"],
            )

            with np.load(io.BytesIO(compact_payload), allow_pickle=False) as arrays:
                assert set(arrays.files) == required_arrays
                assert arrays["observation_uint8"].shape == (576, 576, 3)
                assert arrays["observation_uint8"].dtype == np.uint8
                assert arrays["fbcnn_dpir_nominal"].shape == (576, 576, 3)
                assert arrays["fbcnn_dpir_nominal"].dtype == np.float32
                assert np.isfinite(arrays["fbcnn_dpir_nominal"]).all()
                assert 0 <= float(arrays["fbcnn_dpir_nominal"].min())
                assert float(arrays["fbcnn_dpir_nominal"].max()) <= 1
                detail_error = arrays["detail_patch_error"].astype(np.float64)
                target = arrays["target_bad_detail_0p05"]
                assert detail_error.shape == target.shape == (1024,)
                assert np.isfinite(detail_error).all() and (detail_error >= 0).all()
                assert target.dtype == np.uint8 and set(np.unique(target)).issubset({0, 1})
                assert np.array_equal(target, (np.sqrt(detail_error) > 0.05).astype(np.uint8))
                for pipeline in PIPELINES:
                    for score in COMPACT_SCORES:
                        values = arrays[f"{pipeline}__score__{score}"]
                        assert values.shape == (1024,) and values.dtype == np.float32
                        assert np.isfinite(values).all()

                observed_quality = quality[
                    (quality.source_id == source_id)
                    & (quality.chain_id == chain_id)
                    & (quality.method == "fbcnn_dpir_nominal")
                ].iloc[0]
                quality_values = {
                    "detail_mse": float(detail_error.mean()),
                    **{
                        f"bad_detail_rate_{threshold:g}": float(
                            (np.sqrt(detail_error) > threshold).mean()
                        )
                        for threshold in config["detail_rmse_tolerances"]
                    },
                }
                max_quality_error = max(
                    max_quality_error,
                    max(
                        abs(value - float(observed_quality[key]))
                        for key, value in quality_values.items()
                    ),
                )

                for score in SCORES:
                    if score == "expected_random":
                        order = None
                    else:
                        values = (
                            detail_error
                            if score == "oracle_detail_error"
                            else arrays[f"fbcnn_dpir_nominal__score__{score}"].astype(np.float64)
                        )
                        ties = np.random.default_rng(82).random(len(values))
                        order = np.lexsort((ties, values))
                    for coverage in config["coverages"]:
                        count = int(np.ceil(coverage * len(detail_error)))
                        chosen = np.arange(len(detail_error)) if order is None else order[:count]
                        observed = risk[
                            (risk.source_id == source_id)
                            & (risk.chain_id == chain_id)
                            & (risk.pipeline == "fbcnn_dpir_nominal")
                            & (risk.region == "all")
                            & (risk.score == score)
                            & np.isclose(pd.to_numeric(risk.coverage), coverage)
                        ].iloc[0]
                        values = {
                            "detail_mse": float(detail_error[chosen].mean()),
                            **{
                                f"bad_detail_rate_{threshold:g}": float(
                                    (np.sqrt(detail_error[chosen]) > threshold).mean()
                                )
                                for threshold in config["detail_rmse_tolerances"]
                            },
                        }
                        max_risk_error = max(
                            max_risk_error,
                            max(abs(value - float(observed[key])) for key, value in values.items()),
                        )
                        recalculated_risk_rows += 1

        assert max_quality_error < 1e-8
        assert max_risk_error < 1e-8
        assert int(pd.to_numeric(compute.denoiser_calls).sum()) == observations * 80
        assert int(pd.to_numeric(compute.fbcnn_calls).sum()) == observations * 3
        assert checks["drunet_experiment_calls"] == observations * 80
        assert checks["fbcnn_experiment_calls"] == observations * 3
        assert checks["compact_bundles"] == observations
        assert checks["patcherrornet_fit_performed"] is False
        assert checks["calibration_fit_performed"] is False
        assert checks["test_inference_performed"] is False
        assert status["status"] == "passed_development_shard"
        assert status["completed_observations"] == observations
        assert status["expected_observations"] == observations
        assert status["independent_test_run_authorized"] is False
        assert status["test_inference_performed"] is False
        assert status["test_performance_inspected"] is False
        assert config["test_inference_authorized"] is False
        assert manifest["role"] == provenance["role"] == config["role"] == status["role"] == "development_only"
        assert manifest["test_inference_performed"] is False

        report.update(
            {
                "status": "pass",
                "scientific_payload_accepted": True,
                "audit_scope": "development-payload integrity and compact-metric consistency",
                "archive_crc_test_passed": True,
                "archive_root": archive_root,
                "archive_entries": len(names),
                "manifest_files_checked": len(listed),
                "manifest_mismatches": 0,
                "source_ids": list(source_ids),
                "chain_ids": list(chain_ids),
                "row_counts": expected_counts,
                "records_checked": len(record_paths),
                "compact_bundles_checked": len(compact_paths),
                "compact_arrays_per_bundle": len(required_arrays),
                "maximum_recalculation_errors": {
                    "fbcnn_dpir_quality_compact_metrics": max_quality_error,
                    "fbcnn_dpir_all_region_risk_compact_metrics": max_risk_error,
                },
                "recalculated_risk_rows": recalculated_risk_rows,
                "drunet_calls": int(pd.to_numeric(compute.denoiser_calls).sum()),
                "fbcnn_calls": int(pd.to_numeric(compute.fbcnn_calls).sum()),
                "development_only": True,
                "test_inference_performed": False,
                "test_performance_inspected": False,
                "independent_test_run_authorized": False,
                "limitations": [
                    "The compact shard does not retain every reconstruction or the reference crops, so the validator does not independently recompute every quality and risk value.",
                    "Acceptance records engineering integrity only; it is not an independent-test result or a final novelty claim.",
                ],
            }
        )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("--expected-outer-sha256")
    args = parser.parse_args()
    print(json.dumps(validate(args.archive, args.expected_outer_sha256), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
