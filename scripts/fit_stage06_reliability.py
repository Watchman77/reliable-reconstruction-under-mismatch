#!/usr/bin/env python3
"""Fit and evaluate Stage 06 continuous/severity reliability models.

The script enforces source-disjoint fit, early-stop, calibration and evaluation
roles. Independent evaluation is opt-in so it cannot be opened accidentally.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROLE_ORDER = (
    "development_fit",
    "development_early_stop",
    "development_calibration",
    "external_pilot",
    "independent_test",
)
RAISE_ELIGIBLE_MANIFEST_SHA256 = "a989e066ab5c66bec753719b3a3006c15a0635504f63977750a9192aa2995426"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def source_macro_mae(frame: pd.DataFrame, observed: str, predicted: str) -> float:
    per_source = frame.assign(_ae=(frame[observed] - frame[predicted]).abs()).groupby("source_id")["_ae"].mean()
    return float(per_source.mean())


def validate_source_roles(frame: pd.DataFrame) -> None:
    required = {"source_id", "role", "observed_detail_rmse"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Input table missing columns: {sorted(missing)}")
    role_counts = frame.groupby("source_id")["role"].nunique()
    leaking = role_counts[role_counts > 1]
    if not leaking.empty:
        raise ValueError(f"Sources cross roles: {leaking.index.astype(str).tolist()}")
    unknown = sorted(set(frame["role"].astype(str)) - set(ROLE_ORDER))
    if unknown:
        raise ValueError(f"Unknown roles: {unknown}")


def validate_eligible_sources(frame: pd.DataFrame, manifest_path: Path) -> str:
    """Reject excluded/unknown sources and role changes before using target values."""
    digest = sha256_file(manifest_path)
    if digest != RAISE_ELIGIBLE_MANIFEST_SHA256:
        raise ValueError("Stage 06B eligible manifest differs from the reviewed v1 receipt")
    allowed = pd.read_csv(manifest_path, dtype=str, keep_default_na=False)
    if not {"source_id", "role"} <= set(allowed.columns) or allowed.source_id.duplicated().any():
        raise ValueError("Malformed Stage 06B eligible manifest")
    roles = allowed.set_index("source_id")["role"]
    unknown = sorted(set(frame.source_id) - set(roles.index))
    if unknown:
        raise ValueError(f"Feature table contains excluded or unknown sources: {unknown[:20]}")
    mismatched = frame.loc[frame.role != frame.source_id.map(roles), "source_id"].unique().tolist()
    if mismatched:
        raise ValueError(f"Feature table changes frozen source roles: {mismatched[:20]}")
    return digest


def ridge_candidates(seed: int) -> list[tuple[dict[str, Any], Any]]:
    del seed
    return [
        (
            {"family": "standardised_ridge", "alpha": alpha},
            make_pipeline(StandardScaler(), Ridge(alpha=alpha)),
        )
        for alpha in (0.01, 0.1, 1.0, 10.0, 100.0)
    ]


def boosting_candidates(seed: int) -> list[tuple[dict[str, Any], Any]]:
    candidates = []
    for depth in (1, 2, 3):
        for estimators in (100, 200):
            settings = {
                "family": "gradient_boosting",
                "max_depth": depth,
                "n_estimators": estimators,
                "learning_rate": 0.03,
            }
            candidates.append(
                (
                    settings,
                    GradientBoostingRegressor(
                        max_depth=depth,
                        n_estimators=estimators,
                        learning_rate=0.03,
                        loss="huber",
                        random_state=seed,
                    ),
                )
            )
    return candidates


def select_and_fit(
    family: str,
    features: list[str],
    fit: pd.DataFrame,
    early: pd.DataFrame,
    seed: int,
) -> tuple[Any, dict[str, Any]]:
    candidates = ridge_candidates(seed) if family == "ridge" else boosting_candidates(seed)
    scored: list[tuple[float, dict[str, Any], Any]] = []
    for settings, model in candidates:
        model.fit(fit[features], fit["observed_detail_rmse"])
        trial = early[["source_id", "observed_detail_rmse"]].copy()
        trial["prediction"] = model.predict(early[features])
        scored.append((source_macro_mae(trial, "observed_detail_rmse", "prediction"), settings, model))
    scored.sort(key=lambda item: (item[0], json.dumps(item[1], sort_keys=True)))
    best_mae, best_settings, best_model = scored[0]
    combined = pd.concat([fit, early], ignore_index=True)
    if family == "ridge":
        final = make_pipeline(StandardScaler(), Ridge(alpha=float(best_settings["alpha"])))
    else:
        final = GradientBoostingRegressor(
            max_depth=int(best_settings["max_depth"]),
            n_estimators=int(best_settings["n_estimators"]),
            learning_rate=float(best_settings["learning_rate"]),
            loss="huber",
            random_state=seed,
        )
    final.fit(combined[features], combined["observed_detail_rmse"])
    return final, {"selected": best_settings, "early_stop_source_macro_mae": best_mae}


def fit_probability_calibrator(raw_prediction: np.ndarray, target: np.ndarray) -> IsotonicRegression | None:
    if np.unique(target).size < 2:
        return None
    calibrator = IsotonicRegression(y_min=0.0, y_max=1.0, out_of_bounds="clip")
    calibrator.fit(raw_prediction, target)
    return calibrator


def clustered_bootstrap_difference(
    frame: pd.DataFrame,
    left: str,
    right: str,
    repetitions: int,
    seed: int,
) -> dict[str, float]:
    per_source = (
        frame.assign(
            _left=(frame["observed_detail_rmse"] - frame[left]).abs(),
            _right=(frame["observed_detail_rmse"] - frame[right]).abs(),
        )
        .groupby("source_id")[["_left", "_right"]]
        .mean()
    )
    differences = (per_source["_left"] - per_source["_right"]).to_numpy(float)
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(differences), size=(repetitions, len(differences)))
    boot = differences[draws].mean(axis=1)
    return {
        "source_count": int(len(differences)),
        "mae_difference_left_minus_right": float(differences.mean()),
        "bootstrap_ci_low": float(np.quantile(boot, 0.025)),
        "bootstrap_ci_high": float(np.quantile(boot, 0.975)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--table", type=Path, required=True)
    parser.add_argument("--eligible-source-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--chain-aware-features", required=True)
    parser.add_argument("--image-only-features", required=True)
    parser.add_argument("--forward-residual-feature", default="forward_consistency_residual")
    parser.add_argument("--evaluation-role", choices=("external_pilot", "independent_test"), default="external_pilot")
    parser.add_argument("--permit-independent-evaluation", action="store_true")
    parser.add_argument("--thresholds", default="0.03,0.05,0.075")
    parser.add_argument("--seed", type=int, default=20260925)
    parser.add_argument("--bootstrap-repetitions", type=int, default=10000)
    args = parser.parse_args()

    if args.evaluation_role == "independent_test" and not args.permit_independent_evaluation:
        parser.error("Independent evaluation requires --permit-independent-evaluation after the Stage 06 freeze")
    frame = pd.read_csv(args.table)
    frame["source_id"] = frame["source_id"].astype(str)
    frame["role"] = frame["role"].astype(str)
    validate_source_roles(frame)
    eligible_manifest_sha256 = validate_eligible_sources(frame, args.eligible_source_manifest)
    if args.evaluation_role == "external_pilot" and (frame.role == "independent_test").any():
        raise ValueError("Pilot input must contain no independent-test rows or outcomes")
    chain_features = parse_csv_list(args.chain_aware_features)
    image_features = parse_csv_list(args.image_only_features)
    thresholds = [float(value) for value in parse_csv_list(args.thresholds)]
    requested = sorted(set(chain_features + image_features + [args.forward_residual_feature]))
    missing = [column for column in requested if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing feature columns: {missing}")
    numeric = requested + ["observed_detail_rmse"]
    if not np.isfinite(frame[numeric].to_numpy(float)).all():
        raise ValueError("Feature table contains non-finite model inputs or targets")

    partitions = {role: frame.loc[frame["role"] == role].copy() for role in ROLE_ORDER}
    for role in ("development_fit", "development_early_stop", "development_calibration", args.evaluation_role):
        if partitions[role].empty:
            raise ValueError(f"Required role is empty: {role}")
    fit = partitions["development_fit"]
    early = partitions["development_early_stop"]
    calibration = partitions["development_calibration"]
    evaluation = partitions[args.evaluation_role].copy()

    model_specs: dict[str, tuple[str, list[str]]] = {
        "residual_only": ("ridge", [args.forward_residual_feature]),
        "strong_chain_agnostic": ("boosting", image_features),
        "proposed_chain_aware": ("ridge", chain_features),
    }
    for feature in chain_features:
        retained = [value for value in chain_features if value != feature]
        if retained:
            model_specs[f"ablation_without_{feature}"] = ("ridge", retained)

    fitted: dict[str, Any] = {}
    selection_receipts: dict[str, Any] = {}
    raw_calibration: dict[str, np.ndarray] = {}
    raw_evaluation: dict[str, np.ndarray] = {}
    combined_fit = pd.concat([fit, early], ignore_index=True)
    constant = float(combined_fit["observed_detail_rmse"].median())
    raw_calibration["constant"] = np.full(len(calibration), constant)
    raw_evaluation["constant"] = np.full(len(evaluation), constant)
    selection_receipts["constant"] = {"family": "development_median", "value": constant}

    for name, (family, features) in model_specs.items():
        model, receipt = select_and_fit(family, features, fit, early, args.seed)
        fitted[name] = {"model": model, "features": features}
        selection_receipts[name] = {"features": features, **receipt}
        raw_calibration[name] = model.predict(calibration[features])
        raw_evaluation[name] = model.predict(evaluation[features])

    continuous_calibrators: dict[str, IsotonicRegression] = {}
    probability_calibrators: dict[str, dict[str, IsotonicRegression | None]] = {}
    prediction_table = evaluation[["source_id", "role", "observed_detail_rmse"]].copy()
    metrics: list[dict[str, Any]] = []
    calibration_target = calibration["observed_detail_rmse"].to_numpy(float)
    evaluation_target = evaluation["observed_detail_rmse"].to_numpy(float)
    for name in raw_evaluation:
        continuous = IsotonicRegression(y_min=0.0, out_of_bounds="clip")
        continuous.fit(raw_calibration[name], calibration_target)
        continuous_calibrators[name] = continuous
        calibrated = np.asarray(continuous.predict(raw_evaluation[name]), dtype=float)
        prediction_table[f"predicted_rmse__{name}"] = calibrated
        absolute = np.abs(evaluation_target - calibrated)
        squared = (evaluation_target - calibrated) ** 2
        metrics.append(
            {
                "model": name,
                "metric": "source_macro_mae",
                "threshold": np.nan,
                "value": source_macro_mae(
                    prediction_table[["source_id", "observed_detail_rmse", f"predicted_rmse__{name}"]],
                    "observed_detail_rmse",
                    f"predicted_rmse__{name}",
                ),
            }
        )
        metrics.append({"model": name, "metric": "patch_rmse", "threshold": np.nan, "value": float(np.sqrt(squared.mean()))})
        probability_calibrators[name] = {}
        for threshold in thresholds:
            key = f"{threshold:.6g}"
            calibration_binary = (calibration_target > threshold).astype(float)
            probability = fit_probability_calibrator(raw_calibration[name], calibration_binary)
            probability_calibrators[name][key] = probability
            observed_binary = (evaluation_target > threshold).astype(float)
            if probability is None:
                predicted_probability = np.full(len(evaluation), np.nan)
                brier = np.nan
                status = "non_estimable_in_development_calibration"
            else:
                predicted_probability = np.asarray(probability.predict(raw_evaluation[name]), dtype=float)
                brier = float(np.mean((predicted_probability - observed_binary) ** 2))
                status = "estimated"
            prediction_table[f"event_probability_{key}__{name}"] = predicted_probability
            metrics.append(
                {"model": name, "metric": "brier", "threshold": threshold, "value": brier, "status": status}
            )

    comparisons = []
    comparator_column = "predicted_rmse__strong_chain_agnostic"
    for name in raw_evaluation:
        if name == "strong_chain_agnostic":
            continue
        result = clustered_bootstrap_difference(
            prediction_table,
            f"predicted_rmse__{name}",
            comparator_column,
            args.bootstrap_repetitions,
            args.seed + len(comparisons),
        )
        comparisons.append({"left": name, "right": "strong_chain_agnostic", **result})

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    predictions_path = output_dir / "reliability_predictions.csv"
    metrics_path = output_dir / "reliability_metrics.csv"
    comparisons_path = output_dir / "source_bootstrap_comparisons.csv"
    models_path = output_dir / "frozen_reliability_models.joblib"
    receipt_path = output_dir / "model_training_receipt.json"
    prediction_table.to_csv(predictions_path, index=False)
    pd.DataFrame.from_records(metrics).to_csv(metrics_path, index=False)
    pd.DataFrame.from_records(comparisons).to_csv(comparisons_path, index=False)
    joblib.dump(
        {
            "models": fitted,
            "continuous_calibrators": continuous_calibrators,
            "probability_calibrators": probability_calibrators,
            "constant": constant,
            "thresholds": thresholds,
            "seed": args.seed,
        },
        models_path,
    )
    receipt = {
        "schema_version": "stage06-reliability-v1",
        "evaluation_role": args.evaluation_role,
        "source_counts": {role: int(partitions[role]["source_id"].nunique()) for role in ROLE_ORDER},
        "row_counts": {role: int(len(partitions[role])) for role in ROLE_ORDER},
        "thresholds_rmse": thresholds,
        "selection": selection_receipts,
        "bootstrap_repetitions": args.bootstrap_repetitions,
        "seed": args.seed,
        "independent_evaluation_permitted": bool(args.permit_independent_evaluation),
        "eligible_source_manifest_sha256": eligible_manifest_sha256,
    }
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    exported = []
    for path in (predictions_path, metrics_path, comparisons_path, models_path, receipt_path):
        exported.append({"path": path.name, "byte_count": path.stat().st_size, "sha256": sha256_file(path)})
    (output_dir / "export_manifest.json").write_text(
        json.dumps({"stage": "06D_reliability", "files": exported}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "completed", "evaluation_role": args.evaluation_role, "output_dir": str(output_dir)}, indent=2))


if __name__ == "__main__":
    main()
