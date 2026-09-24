"""Pre-locked one-time unsealing and analysis for Experiment 05.

The implementation is committed before any Stage-05D result exists.  It accepts
exactly the five fixed sealed shards, verifies every manifested byte and lock,
then performs the frozen H1/H2 tests, source bootstrap, Holm correction,
calibration assessment, secondary summaries, and diagnostic figures.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

import numpy as np
import pandas as pd


EXPERIMENT_ID = "independent_05"
STAGE = "05E_one_time_locked_analysis"
PROTOCOL_SHA256 = "b92c6cf73e05f60dc1edb3a31d88d91623e9ae0cf63d6265e6398e335928794c"
DATA_RECEIPT_SHA256 = "ad48eb7a65b043173f1012035b4a4c95d0299420614311bdfc6611ef840169cb"
RUN_CODE_SHA256 = "3fb930119c0e386051765159970234a92a20455d1c3b91615db3c4dddbc87727"
TRANSITION_SHA256 = "b32ec998761aa4ba4ebe06503aaca3ebe5bba4ddc1c1ec94be4c7a1f0fa84ae2"
SHARD_COUNT = 5
SOURCES_PER_SHARD = 8
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
OPERATIONAL_SCORE_KEYS = tuple(
    f"{pipeline}__score__{score}"
    for pipeline in PIPELINES
    for score in HEURISTIC_SCORES
) + (ENSEMBLE_SCORE,)
BOOTSTRAP_SEED = 20260921
BOOTSTRAP_REPLICATES = 10_000
SIGN_FLIP_SEED = 20260921
SIGN_FLIP_REPLICATES = 100_000
PRIMARY_CHAIN = "j75_b16_n2"
PRIMARY_COVERAGE = 0.5
PRACTICAL_REDUCTION = 0.05
PATCHES_PER_OBSERVATION = 1024
CALIBRATION_BINS = 10


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _normalize(value):
    if isinstance(value, dict):
        return {str(key): _normalize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def dump_json(path: Path, value) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".{uuid.uuid4().hex}.partial")
    temporary.write_text(
        json.dumps(_normalize(value), indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def dump_csv(path: Path, frame: pd.DataFrame) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".{uuid.uuid4().hex}.partial")
    frame.to_csv(temporary, index=False)
    temporary.replace(path)


def _archive_prefix(names: list[str]) -> str:
    assert names and len(names) == len(set(names)), "duplicate ZIP entries"
    assert not any(
        name.startswith("/") or ".." in PurePosixPath(name).parts for name in names
    ), "unsafe ZIP path"
    if "export_manifest.json" in names:
        return ""
    candidates = [name for name in names if name.endswith("/export_manifest.json")]
    assert len(candidates) == 1, "missing or ambiguous export manifest"
    prefix = candidates[0][: -len("export_manifest.json")]
    assert prefix.count("/") == 1
    return prefix


def validate_analysis_lock(lock_text: str, analysis_code_sha256: str) -> dict:
    lock = json.loads(lock_text)
    assert lock["experiment_id"] == EXPERIMENT_ID
    assert lock["stage"] == STAGE
    assert lock["outcome_blind"] is True
    assert lock["independent_results_existed_when_locked"] is False
    assert lock["analysis_code_sha256"] == analysis_code_sha256
    assert lock["protocol_sha256"] == PROTOCOL_SHA256
    assert lock["data_receipt_sha256"] == DATA_RECEIPT_SHA256
    assert lock["stage_05d_run_code_sha256"] == RUN_CODE_SHA256
    assert lock["stage_05d_transition_sha256"] == TRANSITION_SHA256
    assert lock["bootstrap"]["replicates"] == BOOTSTRAP_REPLICATES
    assert lock["bootstrap"]["seed"] == BOOTSTRAP_SEED
    assert lock["sign_flip"]["replicates"] == SIGN_FLIP_REPLICATES
    assert lock["sign_flip"]["seed"] == SIGN_FLIP_SEED
    assert lock["h2_region"] == "all"
    assert lock["calibration"]["bins"] == CALIBRATION_BINS
    return lock


def shard_identity(path: Path) -> int:
    with zipfile.ZipFile(path) as archive:
        prefix = _archive_prefix(archive.namelist())
        manifest = json.loads(archive.read(prefix + "export_manifest.json"))
    assert manifest["stage"] == "05D_locked_independent_inference"
    return int(manifest["shard_index"])


def _expected_shard_files(source_ids: list[str]) -> set[str]:
    observation_ids = [f"{source}_{chain}" for source in source_ids for chain in CHAIN_IDS]
    result = {
        "config.json",
        "lock.json",
        "provenance.json",
        "source_manifest.csv",
        "acquisition_repeat_check.csv",
        "acquisition.csv",
        "quality.csv",
        "risk.csv",
        "compute.csv",
        "trajectories.csv",
        "fbcnn_diagnostics.csv",
        "checks.json",
        "status.json",
    }
    result.update(f"compact/{observation_id}.npz" for observation_id in observation_ids)
    result.update(f"records/{observation_id}.json" for observation_id in observation_ids)
    assert len(result) == 125
    return result


def inspect_shard(path: Path, analysis_lock: dict) -> dict:
    """Verify one sealed shard completely before returning any outcome payload."""

    path = Path(path)
    assert path.is_file()
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        prefix = _archive_prefix(names)

        def read(relative: str) -> bytes:
            return archive.read(prefix + relative)

        manifest_payload = read("export_manifest.json")
        manifest = json.loads(manifest_payload)
        index = int(manifest["shard_index"])
        assert 0 <= index < SHARD_COUNT
        expected_sources = analysis_lock["source_ids_by_shard"][str(index)]
        assert manifest["experiment_id"] == EXPERIMENT_ID
        assert manifest["stage"] == "05D_locked_independent_inference"
        assert manifest["role"] == "sealed_independent_test"
        assert manifest["status"] == "passed_locked_independent_shard"
        assert manifest["shard_count"] == SHARD_COUNT
        assert manifest["source_ids"] == expected_sources
        assert tuple(manifest["chain_ids"]) == CHAIN_IDS
        assert manifest["independent_test_run_authorized"] is True
        assert manifest["test_inference_performed"] is True
        assert manifest["test_performance_inspected"] is False
        assert manifest["aggregate_analysis_performed"] is False
        assert manifest["unsealed"] is False
        expected_lock = {
            "protocol_sha256": PROTOCOL_SHA256,
            "data_receipt_sha256": DATA_RECEIPT_SHA256,
            "transition_sha256": TRANSITION_SHA256,
            "run_code_sha256": RUN_CODE_SHA256,
            "test_archive_sha256": analysis_lock["test_archive_sha256"],
            "reliability_archive_sha256": analysis_lock["reliability_archive_sha256"],
        }
        assert manifest["lock"] == expected_lock
        listed = {row["path"]: row for row in manifest["files"]}
        assert len(listed) == len(manifest["files"])
        assert set(listed) == _expected_shard_files(expected_sources)
        actual = {
            name[len(prefix) :]
            for name in names
            if not name.endswith("/") and name != prefix + "export_manifest.json"
        }
        assert actual == set(listed)
        for relative, row in listed.items():
            payload = read(relative)
            assert len(payload) == int(row["byte_count"]), relative
            assert sha256_bytes(payload) == row["sha256"], relative

        config = json.loads(read("config.json"))
        lock = json.loads(read("lock.json"))
        status = json.loads(read("status.json"))
        checks = json.loads(read("checks.json"))
        assert config["source_ids"] == expected_sources
        assert config["shard_index"] == index and config["shard_count"] == SHARD_COUNT
        assert config["test_inference_authorized"] is True
        assert config["test_performance_inspection_authorized"] is False
        assert lock == expected_lock
        assert status["status"] == "passed_locked_independent_shard"
        assert status["completed_observations"] == status["expected_observations"] == 56
        assert status["test_performance_inspected"] is False and status["unsealed"] is False
        assert checks["observations"] == 56 and checks["compact_bundles"] == 56
        assert checks["ensemble_members"] == 5 and checks["calibration_mappings"] == 11
        assert checks["test_performance_inspected"] is False and checks["unsealed"] is False

    return {
        "shard_index": index,
        "path": str(path),
        "archive_filename": path.name,
        "archive_byte_count": path.stat().st_size,
        "archive_sha256": sha256_file(path),
        "archive_prefix": prefix,
        "export_manifest_sha256": sha256_bytes(manifest_payload),
        "manifest_files_checked": len(listed),
        "source_ids": expected_sources,
        "status": "pass_sealed_integrity",
    }


def _read_verified_payload(path: Path, prefix: str, relative: str) -> bytes:
    with zipfile.ZipFile(path) as archive:
        return archive.read(prefix + relative)


def bootstrap_multiplicities(source_count: int) -> np.ndarray:
    assert source_count == 40
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    result = rng.multinomial(
        source_count,
        np.full(source_count, 1.0 / source_count),
        size=BOOTSTRAP_REPLICATES,
    ).astype(np.int16)
    assert result.shape == (BOOTSTRAP_REPLICATES, source_count)
    assert np.all(result.sum(axis=1) == source_count)
    return result


def percentile_interval(replicates: np.ndarray) -> tuple[float, float]:
    values = np.asarray(replicates, dtype=np.float64)
    values = values[np.isfinite(values)]
    assert len(values) >= int(0.99 * BOOTSTRAP_REPLICATES)
    low, high = np.quantile(values, [0.025, 0.975], method="linear")
    return float(low), float(high)


def source_mean_bootstrap(values: np.ndarray, multiplicities: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    assert values.shape == (multiplicities.shape[1],) and np.isfinite(values).all()
    return multiplicities @ values / multiplicities.shape[1]


def one_sided_sign_flip_pvalue(differences: np.ndarray) -> dict:
    differences = np.asarray(differences, dtype=np.float64)
    assert differences.ndim == 1 and np.isfinite(differences).all()
    observed = float(differences.mean())
    rng = np.random.default_rng(SIGN_FLIP_SEED)
    extreme = 0
    generated = 0
    batch_size = 5_000
    while generated < SIGN_FLIP_REPLICATES:
        count = min(batch_size, SIGN_FLIP_REPLICATES - generated)
        signs = rng.integers(0, 2, size=(count, len(differences)), dtype=np.int8)
        signs = signs.astype(np.float64) * 2.0 - 1.0
        randomized = signs @ differences / len(differences)
        extreme += int(np.count_nonzero(randomized <= observed))
        generated += count
    p_value = (extreme + 1.0) / (SIGN_FLIP_REPLICATES + 1.0)
    return {
        "observed_mean_difference": observed,
        "extreme_randomizations": extreme,
        "randomizations": SIGN_FLIP_REPLICATES,
        "p_value_one_sided": float(p_value),
        "continuity_correction": "(extreme + 1) / (randomizations + 1)",
    }


def holm_adjust(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values, key=lambda key: (p_values[key], key))
    adjusted, running = {}, 0.0
    total = len(ordered)
    for rank, key in enumerate(ordered):
        running = max(running, min(1.0, (total - rank) * float(p_values[key])))
        adjusted[key] = running
    return adjusted


def primary_analysis(
    quality: pd.DataFrame,
    risk: pd.DataFrame,
    source_ids: list[str],
    multiplicities: np.ndarray,
) -> tuple[dict, pd.DataFrame]:
    h1_rows = quality[
        (quality.chain_id == PRIMARY_CHAIN)
        & quality.method.isin(["dpir_nominal", "fbcnn_dpir_nominal"])
    ]
    h1 = h1_rows.pivot(index="source_id", columns="method", values="detail_mse").reindex(
        source_ids
    )
    assert h1.notna().all().all() and h1.shape == (40, 2)
    h1_difference = (
        h1["fbcnn_dpir_nominal"] - h1["dpir_nominal"]
    ).to_numpy(dtype=np.float64)

    h2_rows = risk[
        (risk.chain_id == PRIMARY_CHAIN)
        & (risk.pipeline == "fbcnn_dpir_nominal")
        & (risk.region == "all")
        & np.isclose(risk.coverage.astype(float), PRIMARY_COVERAGE)
        & risk.score.isin(["operator_spread_detail", "image_transform_spread_detail"])
    ]
    h2 = h2_rows.pivot(index="source_id", columns="score", values="detail_mse").reindex(
        source_ids
    )
    assert h2.notna().all().all() and h2.shape == (40, 2)
    h2_difference = (
        h2["operator_spread_detail"] - h2["image_transform_spread_detail"]
    ).to_numpy(dtype=np.float64)

    contrasts = pd.DataFrame(
        {
            "source_id": source_ids,
            "h1_dpir_detail_mse": h1["dpir_nominal"].to_numpy(),
            "h1_fbcnn_dpir_detail_mse": h1["fbcnn_dpir_nominal"].to_numpy(),
            "h1_difference": h1_difference,
            "h2_image_transform_detail_risk": h2[
                "image_transform_spread_detail"
            ].to_numpy(),
            "h2_operator_spread_detail_risk": h2["operator_spread_detail"].to_numpy(),
            "h2_difference": h2_difference,
        }
    )

    definitions = {
        "H1_reconstruction": {
            "difference": h1_difference,
            "comparator": h1["dpir_nominal"].to_numpy(dtype=np.float64),
            "contrast": "fbcnn_dpir_nominal minus dpir_nominal",
            "endpoint": "source detail MSE at j75_b16_n2",
        },
        "H2_selection": {
            "difference": h2_difference,
            "comparator": h2["image_transform_spread_detail"].to_numpy(dtype=np.float64),
            "contrast": "operator_spread_detail risk minus image_transform_spread_detail risk",
            "endpoint": "source retained-patch detail MSE at j75_b16_n2, coverage 0.5, region all",
        },
    }
    results = {}
    raw_p = {}
    for hypothesis, definition in definitions.items():
        differences = definition["difference"]
        bootstrap = source_mean_bootstrap(differences, multiplicities)
        ci_low, ci_high = percentile_interval(bootstrap)
        sign_flip = one_sided_sign_flip_pvalue(differences)
        comparator_mean = float(np.mean(definition["comparator"]))
        favorable_reduction = float(-differences.mean() / comparator_mean)
        raw_p[hypothesis] = sign_flip["p_value_one_sided"]
        results[hypothesis] = {
            "unit": "source",
            "sources": len(source_ids),
            "contrast": definition["contrast"],
            "endpoint": definition["endpoint"],
            "mean_difference": float(differences.mean()),
            "paired_source_bootstrap_95_ci": [ci_low, ci_high],
            "comparator_mean": comparator_mean,
            "relative_reduction": favorable_reduction,
            "practical_gate_threshold": PRACTICAL_REDUCTION,
            "practical_gate_passed": favorable_reduction >= PRACTICAL_REDUCTION,
            **sign_flip,
        }
    adjusted = holm_adjust(raw_p)
    for hypothesis, result in results.items():
        result["holm_adjusted_p_value"] = adjusted[hypothesis]
        result["statistical_gate_passed"] = bool(
            adjusted[hypothesis] < 0.05
            and result["paired_source_bootstrap_95_ci"][1] < 0.0
        )
        result["confirmatory_gate_passed"] = bool(
            result["practical_gate_passed"] and result["statistical_gate_passed"]
        )
    overall = bool(all(row["confirmatory_gate_passed"] for row in results.values()))
    return {
        "experiment_id": EXPERIMENT_ID,
        "stage": STAGE,
        "multiplicity": "Holm across H1 and H2",
        "hypotheses": results,
        "both_confirmatory_gates_passed": overall,
        "experimental_novelty_gate_passed": overall,
        "final_literature_novelty_claim_established": False,
        "claim_boundary": (
            "Passing both gates establishes the predeclared independent experimental gate only. "
            "The final novelty claim still requires Stage-05F synthesis against the locked literature boundary."
        ),
    }, contrasts


def _equal_mass_assignments(probability: np.ndarray, weights: np.ndarray) -> np.ndarray:
    order = np.argsort(probability, kind="mergesort")
    cumulative = np.cumsum(weights[order]) - 0.5 * weights[order]
    ordered_bins = np.minimum(
        (cumulative / weights.sum() * CALIBRATION_BINS).astype(np.int8),
        CALIBRATION_BINS - 1,
    )
    assignments = np.empty(len(order), dtype=np.int8)
    assignments[order] = ordered_bins
    return assignments


def _logistic_slopes(
    source_mass: np.ndarray,
    source_positive: np.ndarray,
    logit_probability: np.ndarray,
    multiplicities: np.ndarray,
) -> np.ndarray:
    mass = multiplicities @ source_mass
    positive = multiplicities @ source_positive
    beta = np.zeros((len(multiplicities), 2), dtype=np.float64)
    x = logit_probability[None, :]
    for _ in range(30):
        eta = np.clip(beta[:, :1] + beta[:, 1:] * x, -30.0, 30.0)
        mu = 1.0 / (1.0 + np.exp(-eta))
        residual = positive - mass * mu
        variance = mass * mu * (1.0 - mu)
        g0 = residual.sum(axis=1)
        g1 = (residual * x).sum(axis=1)
        h00 = variance.sum(axis=1)
        h01 = (variance * x).sum(axis=1)
        h11 = (variance * x * x).sum(axis=1)
        determinant = h00 * h11 - h01 * h01
        valid = determinant > 1e-14
        delta0 = np.zeros(len(beta), dtype=np.float64)
        delta1 = np.zeros(len(beta), dtype=np.float64)
        delta0[valid] = (h11[valid] * g0[valid] - h01[valid] * g1[valid]) / determinant[valid]
        delta1[valid] = (-h01[valid] * g0[valid] + h00[valid] * g1[valid]) / determinant[valid]
        beta[:, 0] += delta0
        beta[:, 1] += delta1
        if float(np.max(np.abs(np.column_stack([delta0, delta1])))) < 1e-9:
            break
    beta[~np.isfinite(beta)] = np.nan
    return beta[:, 1]


def calibration_assessment(
    probabilities: dict[str, np.ndarray],
    target: np.ndarray,
    source_index: np.ndarray,
    chain_index: np.ndarray,
    source_ids: list[str],
    multiplicities: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    target = np.asarray(target, dtype=np.float64)
    assert len(target) == 40 * len(CHAIN_IDS) * PATCHES_PER_OBSERVATION
    source_counts = np.bincount(source_index, minlength=40)
    assert np.all(source_counts == len(CHAIN_IDS) * PATCHES_PER_OBSERVATION)
    weights = 1.0 / source_counts[source_index]
    metric_rows, bin_rows = [], []

    for score_key in OPERATIONAL_SCORE_KEYS:
        probability = np.asarray(probabilities[score_key], dtype=np.float64)
        assert probability.shape == target.shape
        assert np.isfinite(probability).all() and 0 <= probability.min() <= probability.max() <= 1
        assignments = _equal_mass_assignments(probability, weights)
        source_brier = np.zeros(40, dtype=np.float64)
        source_citl = np.zeros(40, dtype=np.float64)
        source_bin_mass = np.zeros((40, CALIBRATION_BINS), dtype=np.float64)
        source_bin_probability = np.zeros_like(source_bin_mass)
        source_bin_target = np.zeros_like(source_bin_mass)
        for source in range(40):
            selected_source = source_index == source
            source_brier[source] = np.mean((probability[selected_source] - target[selected_source]) ** 2)
            source_citl[source] = np.mean(target[selected_source] - probability[selected_source])
            for bin_index in range(CALIBRATION_BINS):
                selected = selected_source & (assignments == bin_index)
                source_bin_mass[source, bin_index] = weights[selected].sum()
                source_bin_probability[source, bin_index] = np.sum(weights[selected] * probability[selected])
                source_bin_target[source, bin_index] = np.sum(weights[selected] * target[selected])

        point_mass = source_bin_mass.sum(axis=0)
        point_probability = source_bin_probability.sum(axis=0)
        point_target = source_bin_target.sum(axis=0)
        ece = float(np.abs(point_target - point_probability).sum() / 40.0)
        for bin_index in range(CALIBRATION_BINS):
            mass = point_mass[bin_index]
            bin_rows.append(
                {
                    "scope": "all_chains",
                    "score_key": score_key,
                    "bin": bin_index,
                    "weight_mass": float(mass),
                    "mean_probability": float(point_probability[bin_index] / mass),
                    "observed_bad_detail_rate": float(point_target[bin_index] / mass),
                }
            )

        unique_probability, inverse = np.unique(np.clip(probability, 1e-6, 1 - 1e-6), return_inverse=True)
        source_unique_mass = np.zeros((40, len(unique_probability)), dtype=np.float64)
        source_unique_positive = np.zeros_like(source_unique_mass)
        for source in range(40):
            selected = source_index == source
            np.add.at(source_unique_mass[source], inverse[selected], weights[selected])
            np.add.at(
                source_unique_positive[source],
                inverse[selected],
                weights[selected] * target[selected],
            )
        logit = np.log(unique_probability / (1.0 - unique_probability))
        point_multiplicity = np.ones((1, 40), dtype=np.int16)
        slope = float(
            _logistic_slopes(
                source_unique_mass, source_unique_positive, logit, point_multiplicity
            )[0]
        )

        bootstrap_brier = multiplicities @ source_brier / 40.0
        bootstrap_citl = multiplicities @ source_citl / 40.0
        bootstrap_probability = multiplicities @ source_bin_probability
        bootstrap_target = multiplicities @ source_bin_target
        bootstrap_ece = np.abs(bootstrap_target - bootstrap_probability).sum(axis=1) / 40.0
        bootstrap_slope = _logistic_slopes(
            source_unique_mass, source_unique_positive, logit, multiplicities
        )
        metrics = {
            "source_macro_brier": (float(source_brier.mean()), bootstrap_brier),
            "equal_mass_ece_10bin": (ece, bootstrap_ece),
            "calibration_in_the_large": (float(source_citl.mean()), bootstrap_citl),
            "calibration_slope": (slope, bootstrap_slope),
        }
        for metric, (estimate, replicates) in metrics.items():
            ci_low, ci_high = percentile_interval(replicates)
            metric_rows.append(
                {
                    "scope": "all_chains",
                    "score_key": score_key,
                    "metric": metric,
                    "estimate": estimate,
                    "bootstrap_ci_low": ci_low,
                    "bootstrap_ci_high": ci_high,
                    "sources": 40,
                    "patches": len(target),
                }
            )

        for chain_number, chain_id in enumerate(CHAIN_IDS):
            selected = chain_index == chain_number
            local_probability, local_target = probability[selected], target[selected]
            local_source = source_index[selected]
            local_counts = np.bincount(local_source, minlength=40)
            local_weights = 1.0 / local_counts[local_source]
            local_assignments = _equal_mass_assignments(local_probability, local_weights)
            local_brier = np.mean(
                [
                    np.mean((local_probability[local_source == source] - local_target[local_source == source]) ** 2)
                    for source in range(40)
                ]
            )
            local_citl = np.mean(
                [
                    np.mean(local_target[local_source == source] - local_probability[local_source == source])
                    for source in range(40)
                ]
            )
            local_ece = 0.0
            for bin_index in range(CALIBRATION_BINS):
                in_bin = local_assignments == bin_index
                local_ece += abs(
                    float(np.sum(local_weights[in_bin] * (local_target[in_bin] - local_probability[in_bin])))
                ) / 40.0
            for metric, estimate in (
                ("source_macro_brier", local_brier),
                ("equal_mass_ece_10bin", local_ece),
                ("calibration_in_the_large", local_citl),
            ):
                metric_rows.append(
                    {
                        "scope": chain_id,
                        "score_key": score_key,
                        "metric": metric,
                        "estimate": float(estimate),
                        "bootstrap_ci_low": np.nan,
                        "bootstrap_ci_high": np.nan,
                        "sources": 40,
                        "patches": int(selected.sum()),
                    }
                )
    return pd.DataFrame(metric_rows), pd.DataFrame(bin_rows)


def source_group_summary(
    frame: pd.DataFrame,
    group_columns: list[str],
    metric_columns: list[str],
    source_ids: list[str],
    multiplicities: np.ndarray,
) -> pd.DataFrame:
    rows = []
    for keys, group in frame.groupby(group_columns, sort=True, dropna=False):
        keys = keys if isinstance(keys, tuple) else (keys,)
        group = group.set_index("source_id").reindex(source_ids)
        assert group[metric_columns].notna().all().all()
        row = dict(zip(group_columns, keys))
        row["sources"] = len(source_ids)
        for metric in metric_columns:
            values = group[metric].to_numpy(dtype=np.float64)
            replicates = source_mean_bootstrap(values, multiplicities)
            low, high = percentile_interval(replicates)
            row[f"mean_{metric}"] = float(values.mean())
            row[f"{metric}_bootstrap_ci_low"] = low
            row[f"{metric}_bootstrap_ci_high"] = high
        rows.append(row)
    return pd.DataFrame(rows)


def _compact_expected_arrays() -> set[str]:
    result = {
        "observation_uint8",
        "fbcnn_dpir_nominal",
        "dpir_nominal__rgb_patch_error",
        "dpir_nominal__detail_patch_error",
        "fbcnn_dpir_nominal__rgb_patch_error",
        "fbcnn_dpir_nominal__detail_patch_error",
        "target_bad_detail_0p05",
        "reference_texture",
        ENSEMBLE_VARIANCE,
    }
    result.update(OPERATIONAL_SCORE_KEYS)
    result.update(f"{key}__calibrated_probability" for key in OPERATIONAL_SCORE_KEYS)
    assert len(result) == 31
    return result


def load_unsealed_data(verified: list[dict]) -> dict:
    quality_frames, risk_frames, source_frames = [], [], []
    probabilities = {key: [] for key in OPERATIONAL_SCORE_KEYS}
    targets, sources, chains = [], [], []
    all_source_ids = sorted(source for report in verified for source in report["source_ids"])
    assert len(all_source_ids) == len(set(all_source_ids)) == 40
    source_number = {source: index for index, source in enumerate(all_source_ids)}

    for report in sorted(verified, key=lambda row: row["shard_index"]):
        path, prefix = Path(report["path"]), report["archive_prefix"]
        quality_frames.append(
            pd.read_csv(io.BytesIO(_read_verified_payload(path, prefix, "quality.csv")))
        )
        risk_frames.append(pd.read_csv(io.BytesIO(_read_verified_payload(path, prefix, "risk.csv"))))
        source_frames.append(
            pd.read_csv(io.BytesIO(_read_verified_payload(path, prefix, "source_manifest.csv")))
        )
        with zipfile.ZipFile(path) as archive:
            for source_id in report["source_ids"]:
                for chain_index, chain_id in enumerate(CHAIN_IDS):
                    relative = f"compact/{source_id}_{chain_id}.npz"
                    payload = archive.read(prefix + relative)
                    with np.load(io.BytesIO(payload), allow_pickle=False) as stored:
                        assert set(stored.files) == _compact_expected_arrays()
                        target = stored["target_bad_detail_0p05"].astype(np.uint8)
                        assert target.shape == (PATCHES_PER_OBSERVATION,)
                        assert set(np.unique(target)).issubset({0, 1})
                        targets.append(target)
                        sources.append(
                            np.full(PATCHES_PER_OBSERVATION, source_number[source_id], dtype=np.uint8)
                        )
                        chains.append(
                            np.full(PATCHES_PER_OBSERVATION, chain_index, dtype=np.uint8)
                        )
                        for score_key in OPERATIONAL_SCORE_KEYS:
                            values = stored[f"{score_key}__calibrated_probability"].astype(
                                np.float32
                            )
                            assert values.shape == (PATCHES_PER_OBSERVATION,)
                            assert np.isfinite(values).all() and 0 <= values.min() <= values.max() <= 1
                            probabilities[score_key].append(values)

    quality = pd.concat(quality_frames, ignore_index=True)
    risk = pd.concat(risk_frames, ignore_index=True)
    source_manifest = pd.concat(source_frames, ignore_index=True)
    assert len(source_manifest) == 40 and source_manifest.source_id.nunique() == 40
    assert len(quality) == 40 * len(CHAIN_IDS) * 6
    assert not quality.duplicated(["source_id", "chain_id", "method"]).any()
    assert len(risk) == 40 * len(CHAIN_IDS) * 120
    assert not risk.duplicated(
        ["source_id", "chain_id", "pipeline", "region", "score_key", "coverage"]
    ).any()
    return {
        "source_ids": all_source_ids,
        "source_manifest": source_manifest.sort_values("source_id").reset_index(drop=True),
        "quality": quality,
        "risk": risk,
        "probabilities": {key: np.concatenate(value) for key, value in probabilities.items()},
        "target": np.concatenate(targets),
        "source_index": np.concatenate(sources),
        "chain_index": np.concatenate(chains),
    }


def build_figures(
    primary: dict,
    risk_summary: pd.DataFrame,
    calibration_bins: pd.DataFrame,
    output_dir: Path,
) -> list[str]:
    import matplotlib.pyplot as plt

    figure_dir = Path(output_dir) / "figures"
    figure_dir.mkdir(exist_ok=True)
    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.2,
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )
    paths = []

    names = ["H1 reconstruction", "H2 selection"]
    records = [primary["hypotheses"]["H1_reconstruction"], primary["hypotheses"]["H2_selection"]]
    estimates = [row["mean_difference"] for row in records]
    low = [row["paired_source_bootstrap_95_ci"][0] for row in records]
    high = [row["paired_source_bootstrap_95_ci"][1] for row in records]
    fig, axis = plt.subplots(figsize=(7.2, 3.8))
    y = np.arange(2)
    axis.errorbar(
        estimates,
        y,
        xerr=[np.asarray(estimates) - np.asarray(low), np.asarray(high) - np.asarray(estimates)],
        fmt="o",
        color="#1f4e79",
        capsize=4,
    )
    axis.axvline(0, color="#444444", linestyle="--", linewidth=1)
    axis.set_yticks(y, names)
    axis.invert_yaxis()
    axis.set_xlabel("Paired source-mean difference (negative is favorable)")
    axis.set_title("Independent confirmatory contrasts with 95% source-bootstrap intervals")
    fig.tight_layout()
    path = figure_dir / "primary_contrasts.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    paths.append(str(path))

    selected = risk_summary[
        (risk_summary.chain_id == PRIMARY_CHAIN)
        & (risk_summary.pipeline == "fbcnn_dpir_nominal")
        & (risk_summary.region == "all")
        & risk_summary.score.isin(
            [
                "operator_spread_detail",
                "image_transform_spread_detail",
                "trained_image_only_patcherrornet_ensemble",
                "expected_random",
                "oracle_detail_error",
            ]
        )
    ]
    fig, axis = plt.subplots(figsize=(7.2, 4.5))
    for score, frame in selected.groupby("score"):
        frame = frame.sort_values("coverage")
        axis.plot(100 * frame.coverage, frame.mean_detail_mse, marker="o", label=score)
    axis.set_xlabel("Retained coverage (%)")
    axis.set_ylabel("Source-mean retained detail MSE")
    axis.set_title("Primary-chain independent risk–coverage")
    axis.legend(fontsize=7)
    fig.tight_layout()
    path = figure_dir / "primary_risk_coverage.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    paths.append(str(path))

    fig, axes = plt.subplots(3, 4, figsize=(13, 9), sharex=True, sharey=True)
    for axis, score_key in zip(axes.ravel(), OPERATIONAL_SCORE_KEYS):
        frame = calibration_bins[calibration_bins.score_key == score_key].sort_values("bin")
        axis.plot([0, 1], [0, 1], color="#555555", linestyle="--", linewidth=0.8)
        axis.plot(
            frame.mean_probability,
            frame.observed_bad_detail_rate,
            marker="o",
            color="#1f4e79",
        )
        axis.set_title(score_key.replace("__score__", " · ").replace("_", " "), fontsize=7)
    axes.ravel()[-1].axis("off")
    fig.supxlabel("Mapped probability")
    fig.supylabel("Observed bad-detail rate")
    fig.suptitle("Independent reliability diagrams · all acquisition chains")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    path = figure_dir / "independent_calibration_reliability.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    paths.append(str(path))
    return paths


def run_analysis(archive_paths, output_dir, lock_text: str, analysis_code_sha256: str) -> dict:
    analysis_lock = validate_analysis_lock(lock_text, analysis_code_sha256)
    paths = [Path(path) for path in archive_paths]
    assert len(paths) == SHARD_COUNT
    by_index = {}
    for path in paths:
        index = shard_identity(path)
        assert index not in by_index, f"duplicate shard index: {index}"
        by_index[index] = path
    assert sorted(by_index) == list(range(SHARD_COUNT))

    verified = [inspect_shard(by_index[index], analysis_lock) for index in range(SHARD_COUNT)]
    all_sources = [source for report in verified for source in report["source_ids"]]
    assert len(all_sources) == len(set(all_sources)) == 40

    final_output_dir = Path(output_dir)
    assert not final_output_dir.exists(), (
        f"one-time unsealing output already exists: {final_output_dir}"
    )
    final_output_dir.parent.mkdir(parents=True, exist_ok=True)
    output_dir = final_output_dir.with_name(
        final_output_dir.name + f".building.{uuid.uuid4().hex}"
    )
    output_dir.mkdir()
    dump_json(
        output_dir / "unsealing_receipt.json",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": STAGE,
            "unsealed_at_utc": datetime.now(timezone.utc).isoformat(),
            "analysis_lock_sha256": sha256_bytes(lock_text.encode()),
            "analysis_code_sha256": analysis_code_sha256,
            "shards": verified,
            "sealed_shards_verified_before_unsealing": True,
            "test_performance_inspected_before_unsealing": False,
            "unsealed": True,
        },
    )

    data = load_unsealed_data(verified)
    multiplicities = bootstrap_multiplicities(len(data["source_ids"]))
    primary, contrasts = primary_analysis(
        data["quality"], data["risk"], data["source_ids"], multiplicities
    )
    calibration_metrics, calibration_bins = calibration_assessment(
        data["probabilities"],
        data["target"],
        data["source_index"],
        data["chain_index"],
        data["source_ids"],
        multiplicities,
    )
    quality_metrics = [
        "mse",
        "psnr_db",
        "detail_mse",
        "bad_detail_rate_0.025",
        "bad_detail_rate_0.05",
        "bad_detail_rate_0.1",
    ]
    risk_metrics = [
        "rgb_mse",
        "detail_mse",
        "bad_detail_rate_0.025",
        "bad_detail_rate_0.05",
        "bad_detail_rate_0.1",
    ]
    quality_summary = source_group_summary(
        data["quality"], ["chain_id", "method"], quality_metrics, data["source_ids"], multiplicities
    )
    risk_summary = source_group_summary(
        data["risk"],
        ["chain_id", "pipeline", "region", "score", "score_key", "score_role", "coverage"],
        risk_metrics,
        data["source_ids"],
        multiplicities,
    )

    dump_csv(output_dir / "source_manifest.csv", data["source_manifest"])
    dump_csv(output_dir / "primary_source_contrasts.csv", contrasts)
    dump_json(output_dir / "primary_hypotheses.json", primary)
    dump_csv(output_dir / "quality_summary.csv", quality_summary)
    dump_csv(output_dir / "risk_summary.csv", risk_summary)
    dump_csv(output_dir / "calibration_metrics.csv", calibration_metrics)
    dump_csv(output_dir / "calibration_bins.csv", calibration_bins)
    figures = build_figures(primary, risk_summary, calibration_bins, output_dir)

    checks = {
        "sealed_shards": 5,
        "manifest_files_checked": sum(row["manifest_files_checked"] for row in verified),
        "sources": 40,
        "chains": 7,
        "observations": 280,
        "quality_rows": len(data["quality"]),
        "risk_rows": len(data["risk"]),
        "calibration_patch_rows": len(data["target"]),
        "calibration_scores": len(OPERATIONAL_SCORE_KEYS),
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "sign_flip_replicates_per_hypothesis": SIGN_FLIP_REPLICATES,
        "holm_hypotheses": 2,
        "figures": [str(Path(path).relative_to(output_dir)) for path in figures],
        "unsealed": True,
    }
    assert checks["quality_rows"] == 1680
    assert checks["risk_rows"] == 33600
    assert checks["calibration_patch_rows"] == 286720
    dump_json(output_dir / "checks.json", checks)
    dump_json(
        output_dir / "status.json",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": STAGE,
            "status": "passed_one_time_locked_analysis",
            "independent_test_run_complete": True,
            "independent_test_performance_inspected": True,
            "unsealed": True,
            "both_confirmatory_gates_passed": primary["both_confirmatory_gates_passed"],
            "experimental_novelty_gate_passed": primary["experimental_novelty_gate_passed"],
            "final_literature_novelty_claim_established": False,
            "next_stage": "05F_locked_literature_and_experimental_synthesis",
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
    )

    manifest_files = []
    for path in sorted(output_dir.rglob("*")):
        if path.is_file() and path.name != "export_manifest.json" and ".partial" not in path.name:
            manifest_files.append(
                {
                    "path": str(path.relative_to(output_dir)),
                    "byte_count": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    dump_json(
        output_dir / "export_manifest.json",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": STAGE,
            "status": "passed_one_time_locked_analysis",
            "unsealed": True,
            "files": manifest_files,
        },
    )
    output_dir.replace(final_output_dir)
    output_dir = final_output_dir
    archive_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    archive_path = output_dir.parent / f"{output_dir.name}_{archive_stamp}.zip"
    temporary = archive_path.with_suffix(f".{uuid.uuid4().hex}.partial")
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for row in manifest_files:
            archive.write(output_dir / row["path"], arcname=row["path"])
        archive.write(output_dir / "export_manifest.json", arcname="export_manifest.json")
    temporary.replace(archive_path)
    return {
        "status": "passed_one_time_locked_analysis",
        "output_dir": str(output_dir),
        "archive_path": str(archive_path),
        "archive_sha256": sha256_file(archive_path),
        "both_confirmatory_gates_passed": primary["both_confirmatory_gates_passed"],
        "experimental_novelty_gate_passed": primary["experimental_novelty_gate_passed"],
        "final_literature_novelty_claim_established": False,
        "primary_hypotheses": primary["hypotheses"],
    }


def static_self_check() -> dict:
    assert SHARD_COUNT * SOURCES_PER_SHARD == 40
    assert len(CHAIN_IDS) == 7
    assert len(OPERATIONAL_SCORE_KEYS) == 11
    assert BOOTSTRAP_REPLICATES == 10_000 and SIGN_FLIP_REPLICATES == 100_000
    sample = np.asarray([-2.0, -1.0, 1.0, 2.0])
    adjusted = holm_adjust({"a": 0.01, "b": 0.04})
    assert adjusted == {"a": 0.02, "b": 0.04}
    assert math.isclose(float(sample.mean()), 0.0)
    return {
        "experiment_id": EXPERIMENT_ID,
        "stage": STAGE,
        "required_shards": SHARD_COUNT,
        "sources": 40,
        "operational_scores": len(OPERATIONAL_SCORE_KEYS),
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "sign_flip_replicates": SIGN_FLIP_REPLICATES,
        "primary_hypotheses": 2,
    }
