#!/usr/bin/env python3
"""Independently validate a returned stage-05C development-canary ZIP.

The validator does not require PyTorch. It checks the ZIP container, every
export-manifest hash, source crops, prediction-array schemas, acquisition
receipts, quality metrics, selection-risk tables, compute accounting, and the
sealed-test guard. Known outcome-blind metadata findings are reported
separately from scientific-payload integrity.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


CANARY_SOURCES = ("0805", "0806")
CANARY_CHAINS = ("q8_b16_n2", "j75_b16_n2")
METHODS = (
    "observed",
    "gradient_nominal",
    "dpir_nominal",
    "fbcnn",
    "fbcnn_gradient_nominal",
    "fbcnn_dpir_nominal",
)
OPERATIONAL_SCORES_WITHOUT_TRAINED_COMPARATOR = {
    "operator_spread_detail",
    "operator_spread_rgb",
    "image_transform_spread_detail",
    "original_measurement_residual",
    "reconstruction_gradient",
}
SCORE_RENAMES = {
    "measurement_residual": "original_measurement_residual",
    "image_gradient": "reconstruction_gradient",
    "random_expected": "expected_random",
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_array(value: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest()


def transfer(shape: tuple[int, int], sigma: float) -> np.ndarray:
    fy = np.fft.fftfreq(shape[0])[:, None]
    fx = np.fft.fftfreq(shape[1])[None, :]
    return np.exp(-2 * np.pi**2 * sigma**2 * (fx**2 + fy**2))


def blur(image: np.ndarray, sigma: float) -> np.ndarray:
    return np.fft.ifft2(
        np.fft.fft2(image, axes=(0, 1)) * transfer(image.shape[:2], sigma)[..., None],
        axes=(0, 1),
    ).real


def interior(value: np.ndarray, config: dict) -> np.ndarray:
    border = config["context_border"]
    return value[border:-border, border:-border] if border else value


def patch_mean(value: np.ndarray, patch_size: int) -> np.ndarray:
    height, width = value.shape
    assert height % patch_size == width % patch_size == 0
    return value.reshape(
        height // patch_size,
        patch_size,
        width // patch_size,
        patch_size,
    ).mean(axis=(1, 3))


def detail(value: np.ndarray, config: dict) -> np.ndarray:
    return value - blur(value, config["detail_blur_sigma"])


def evaluate_scores(
    truth: np.ndarray,
    nominal: np.ndarray,
    observation: np.ndarray,
    operators: list[np.ndarray],
    transforms: list[np.ndarray],
    config: dict,
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    pool = lambda value: patch_mean(value, config["patch_size"]).ravel()
    rgb_error = pool(np.mean((interior(nominal, config) - interior(truth, config)) ** 2, axis=-1))
    detail_error = pool(
        np.mean(interior(detail(nominal, config) - detail(truth, config), config) ** 2, axis=-1)
    )
    gy, gx = np.gradient(nominal.mean(axis=-1))
    raw_scores = {
        "operator_spread_detail": np.sqrt(
            np.var([detail(value, config) for value in operators], axis=0).mean(axis=-1)
        ),
        "image_transform_spread_detail": np.sqrt(
            np.var([detail(value, config) for value in transforms], axis=0).mean(axis=-1)
        ),
        "operator_spread_rgb": np.sqrt(np.var(operators, axis=0).mean(axis=-1)),
        "measurement_residual": np.sqrt(
            np.mean((blur(nominal, config["nominal_sigma"]) - observation) ** 2, axis=-1)
        ),
        "image_gradient": np.hypot(gx, gy),
    }
    scores = {name: pool(interior(value, config)) for name, value in raw_scores.items()}
    gy, gx = np.gradient(interior(truth, config).mean(axis=-1))
    texture = pool(np.hypot(gx, gy))
    textured = np.argsort(texture, kind="stable")[-int(np.ceil(len(texture) / 4)) :]
    rows = []
    for region, indices in (("all", np.arange(len(rgb_error))), ("textured_quartile", textured)):
        region_rgb, region_detail = rgb_error[indices], detail_error[indices]
        score_items = list(scores.items()) + [
            ("random_expected", None),
            ("oracle_detail_error", detail_error),
        ]
        for name, score in score_items:
            order = None
            if score is not None:
                ties = np.random.default_rng(82).random(len(indices))
                order = np.lexsort((ties, score[indices]))
            for coverage in config["coverages"]:
                count = int(np.ceil(coverage * len(indices)))
                chosen = np.arange(len(indices)) if order is None else order[:count]
                row = {
                    "region": region,
                    "score": SCORE_RENAMES.get(name, name),
                    "coverage": coverage,
                    "available_patches": len(indices),
                    "retained_patches": count,
                    "rgb_mse": float(region_rgb[chosen].mean()),
                    "detail_mse": float(region_detail[chosen].mean()),
                }
                for threshold in config["detail_rmse_tolerances"]:
                    row[f"bad_detail_rate_{threshold:g}"] = float(
                        (np.sqrt(region_detail[chosen]) > threshold).mean()
                    )
                rows.append(row)
    arrays = {
        "rgb_patch_error": rgb_error,
        "detail_patch_error": detail_error,
        "reference_texture": texture,
        **{SCORE_RENAMES.get(name, name): value for name, value in scores.items()},
    }
    return pd.DataFrame(rows), arrays


def validate(root: Path, archive_path: Path, expected_outer_sha256: str | None) -> dict:
    archive_bytes = archive_path.read_bytes()
    report: dict[str, object] = {
        "archive_path": str(archive_path),
        "archive_byte_count": len(archive_bytes),
        "received_outer_sha256": sha256_bytes(archive_bytes),
        "notebook_reported_outer_sha256": expected_outer_sha256,
    }
    report["outer_sha256_match"] = (
        expected_outer_sha256 is None or report["received_outer_sha256"] == expected_outer_sha256
    )

    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        names = archive.namelist()
        assert names and len(names) == len(set(names))
        assert not any(name.startswith("/") or ".." in name.split("/") for name in names)
        assert archive.testzip() is None
        roots = {name.split("/", 1)[0] for name in names}
        assert len(roots) == 1
        archive_root = roots.pop()
        read = lambda relative: archive.read(f"{archive_root}/{relative}")

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
            assert len(payload) == row["byte_count"]
            assert sha256_bytes(payload) == row["sha256"]

        config = json.loads(read("config.json"))
        checks = json.loads(read("checks.json"))
        status = json.loads(read("status.json"))
        provenance = json.loads(read("provenance.json"))
        csv_names = (
            "source_manifest.csv",
            "acquisition_repeat_check.csv",
            "acquisition.csv",
            "quality.csv",
            "risk.csv",
            "compute.csv",
            "trajectories.csv",
            "fbcnn_diagnostics.csv",
        )
        frames = {name: pd.read_csv(io.BytesIO(read(name))) for name in csv_names}
        for frame in frames.values():
            if "source_id" in frame:
                frame["source_id"] = frame["source_id"].astype(str).str.zfill(4)

        assert tuple(config["source_ids"]) == CANARY_SOURCES
        assert tuple(config["chain_ids"]) == CANARY_CHAINS
        assert len(frames["source_manifest.csv"]) == 2
        assert len(frames["acquisition.csv"]) == 4
        assert len(frames["acquisition_repeat_check.csv"]) == 4
        assert len(frames["quality.csv"]) == 24
        assert len(frames["risk.csv"]) == 448
        assert len(frames["compute.csv"]) == 60
        assert len(frames["trajectories.csv"]) == 320
        assert len(frames["fbcnn_diagnostics.csv"]) == 12
        assert not frames["quality.csv"].duplicated(["source_id", "chain_id", "method"]).any()
        assert not frames["risk.csv"].duplicated(
            ["source_id", "chain_id", "pipeline", "region", "score", "coverage"]
        ).any()

        source_manifest = frames["source_manifest.csv"].set_index("source_id")
        references: dict[str, np.ndarray] = {}
        for source_id in CANARY_SOURCES:
            source_path = root / "inputs" / "div2k_canary" / f"{source_id}.png"
            source_bytes = source_path.read_bytes()
            with Image.open(source_path) as image:
                image.load()
                rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
                width, height = image.size
            row = source_manifest.loc[source_id]
            assert sha256_bytes(source_bytes) == row.file_sha256
            assert sha256_bytes(rgb.tobytes()) == row.decoded_rgb_sha256
            assert (width, height) == (int(row.width), int(row.height))
            extent, left, top = int(row.crop_extent), int(row.crop_left), int(row.crop_top)
            references[source_id] = rgb[top : top + extent, left : left + extent].astype(np.float64) / 255

        quality = frames["quality.csv"]
        risk = frames["risk.csv"]
        acquisition = frames["acquisition.csv"]
        repeat = frames["acquisition_repeat_check.csv"]
        max_errors = {"quality": 0.0, "patch_arrays": 0.0, "risk": 0.0, "score_arrays": 0.0}
        seen_references: dict[str, np.ndarray] = {}

        for source_id in CANARY_SOURCES:
            for chain_id in CANARY_CHAINS:
                relative = f"predictions/{source_id}_{chain_id}.npz"
                with np.load(io.BytesIO(read(relative)), allow_pickle=False) as arrays:
                    assert len(arrays.files) == 44
                    assert all(np.isfinite(arrays[name]).all() for name in arrays.files)
                    assert np.array_equal(arrays["reference"], references[source_id])
                    if source_id in seen_references:
                        assert np.array_equal(arrays["reference"], seen_references[source_id])
                    seen_references[source_id] = arrays["reference"].copy()
                    assert np.array_equal(arrays["supplied_observation"], arrays["observed"])

                    acq = acquisition[
                        (acquisition.source_id == source_id) & (acquisition.chain_id == chain_id)
                    ].iloc[0]
                    rep = repeat[(repeat.source_id == source_id) & (repeat.chain_id == chain_id)].iloc[0]
                    observed_hash = sha256_array(arrays["supplied_observation"])
                    assert observed_hash == acq.observation_sha256 == rep.observation_sha256
                    assert bool(rep.repeat_identical)
                    if chain_id.startswith("j75"):
                        jpeg = read(f"codec_inputs/{source_id}_{chain_id}.jpg")
                        with Image.open(io.BytesIO(jpeg)) as image:
                            decoded = np.asarray(image.convert("RGB"), dtype=np.float64) / 255
                        assert np.array_equal(decoded, arrays["supplied_observation"])
                        assert len(jpeg) == int(acq.jpeg_byte_count)
                        assert sha256_bytes(jpeg) == acq.jpeg_sha256 == rep.jpeg_sha256

                    for method in METHODS:
                        estimate, truth = arrays[method], arrays["reference"]
                        rgb_error = np.mean(
                            (interior(estimate, config) - interior(truth, config)) ** 2,
                            axis=-1,
                        )
                        detail_error = np.mean(
                            interior(detail(estimate, config) - detail(truth, config), config) ** 2,
                            axis=-1,
                        )
                        rgb_patch = patch_mean(rgb_error, config["patch_size"]).ravel()
                        detail_patch = patch_mean(detail_error, config["patch_size"]).ravel()
                        max_errors["patch_arrays"] = max(
                            max_errors["patch_arrays"],
                            float(np.max(np.abs(rgb_patch - arrays[f"{method}__rgb_patch_error"]))),
                            float(np.max(np.abs(detail_patch - arrays[f"{method}__detail_patch_error"]))),
                        )
                        row = quality[
                            (quality.source_id == source_id)
                            & (quality.chain_id == chain_id)
                            & (quality.method == method)
                        ].iloc[0]
                        mse = float(rgb_error.mean())
                        values = {
                            "mse": mse,
                            "psnr_db": float(-10 * np.log10(mse)),
                            "detail_mse": float(detail_error.mean()),
                        }
                        for threshold in config["detail_rmse_tolerances"]:
                            values[f"bad_detail_rate_{threshold:g}"] = float(
                                (np.sqrt(detail_patch) > threshold).mean()
                            )
                        max_errors["quality"] = max(
                            max_errors["quality"],
                            max(abs(value - float(row[key])) for key, value in values.items()),
                        )

                    for pipeline in ("dpir_nominal", "fbcnn_dpir_nominal"):
                        operators = [
                            arrays[f"{pipeline}__sigma08"],
                            arrays[pipeline],
                            arrays[f"{pipeline}__sigma12"],
                        ]
                        transforms = [
                            arrays[pipeline],
                            arrays[f"{pipeline}__rot90"],
                            arrays[f"{pipeline}__rot180"],
                        ]
                        expected, score_arrays = evaluate_scores(
                            arrays["reference"],
                            arrays[pipeline],
                            arrays["supplied_observation"],
                            operators,
                            transforms,
                            config,
                        )
                        observed = risk[
                            (risk.source_id == source_id)
                            & (risk.chain_id == chain_id)
                            & (risk.pipeline == pipeline)
                        ].copy()
                        # The returned pre-amendment canary used random_expected. Normalize
                        # it for numerical readback while retaining the finding below.
                        observed["score"] = observed["score"].replace(
                            {"random_expected": "expected_random"}
                        )
                        keys = ["region", "score", "coverage"]
                        numeric = [
                            "available_patches",
                            "retained_patches",
                            "rgb_mse",
                            "detail_mse",
                            "bad_detail_rate_0.025",
                            "bad_detail_rate_0.05",
                            "bad_detail_rate_0.1",
                        ]
                        expected = expected.sort_values(keys).reset_index(drop=True)
                        observed = observed.sort_values(keys).reset_index(drop=True)
                        assert expected[keys].astype(str).equals(observed[keys].astype(str))
                        max_errors["risk"] = max(
                            max_errors["risk"],
                            float(
                                np.max(
                                    np.abs(
                                        expected[numeric].to_numpy(float)
                                        - observed[numeric].to_numpy(float)
                                    )
                                )
                            ),
                        )
                        for name, expected_array in score_arrays.items():
                            stored_name = name
                            if name == "expected_random":
                                continue
                            key = f"{pipeline}__score__{stored_name}"
                            max_errors["score_arrays"] = max(
                                max_errors["score_arrays"],
                                float(np.max(np.abs(expected_array - arrays[key]))),
                            )

        assert max_errors["quality"] < 1e-12
        assert max_errors["patch_arrays"] == 0
        assert max_errors["risk"] < 1e-12
        assert max_errors["score_arrays"] == 0
        assert int(frames["compute.csv"].denoiser_calls.sum()) == 320
        assert int(frames["compute.csv"].fbcnn_calls.sum()) == 12
        assert checks["drunet_experiment_calls"] == 320
        assert checks["fbcnn_experiment_calls"] == 12
        assert status["status"] == "passed_development_canary"
        assert manifest["role"] == "development_only"
        assert manifest["test_inference_performed"] is False
        assert status["independent_test_run_authorized"] is False
        assert status["test_inference_performed"] is False
        assert status["test_performance_inspected"] is False
        assert config["test_inference_authorized"] is False

        observed_scores = set(risk.score)
        findings = []
        if not report["outer_sha256_match"]:
            findings.append("received_outer_zip_repackaged")
        if "random_expected" in observed_scores:
            findings.append("evaluation_score_alias_random_expected")
        if provenance.get("experiment") == "jpeg_aware_04":
            findings.append("inherited_parent_experiment_provenance")

        report.update(
            {
                "status": "pass_with_recorded_outcome_blind_metadata_corrections"
                if findings
                else "pass",
                "scientific_payload_accepted": True,
                "archive_crc_test_passed": True,
                "archive_entries": len(names),
                "manifest_files_checked": len(listed),
                "manifest_mismatches": 0,
                "source_ids": list(CANARY_SOURCES),
                "chain_ids": list(CANARY_CHAINS),
                "row_counts": {name: len(frame) for name, frame in frames.items()},
                "maximum_recalculation_errors": max_errors,
                "drunet_calls": 320,
                "fbcnn_calls": 12,
                "metadata_findings": findings,
                "requires_canary_rerun": False,
                "test_inference_performed": False,
                "independent_test_run_authorized": False,
            }
        )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--expected-outer-sha256")
    args = parser.parse_args()
    print(
        json.dumps(
            validate(args.root, args.archive, args.expected_outer_sha256),
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
