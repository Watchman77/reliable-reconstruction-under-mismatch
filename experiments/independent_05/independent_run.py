"""Locked, sharded independent inference for Experiment 05.

This module is intentionally outcome-blind.  It verifies the frozen protocol,
the versioned Stage-05D transition, the test archive, the development-fitted
reliability archive, and every selected source before running inference.  It
writes resumable per-observation evidence but never prints or interprets a test
metric.  Aggregate analysis is a separate Stage-05E action after all five
shards have passed independent readback.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import tarfile
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

import numpy as np
import pandas as pd
from PIL import Image
import torch


C05 = None
RT05 = None

EXPERIMENT_ID = "independent_05"
STAGE = "05D_locked_independent_inference"
ROLE = "sealed_independent_test"
PROTOCOL_SHA256 = "b92c6cf73e05f60dc1edb3a31d88d91623e9ae0cf63d6265e6398e335928794c"
DATA_RECEIPT_SHA256 = "ad48eb7a65b043173f1012035b4a4c95d0299420614311bdfc6611ef840169cb"
TEST_ARCHIVE_SHA256 = "987e6a5208206b51bb556e808ea052aa588f373124bd0f571888a4754c6afa89"
TEST_ARCHIVE_BYTES = 198_924_536
RELIABILITY_ARCHIVE_SHA256 = "a77f409016070ac799133502c3b24f9603e918b85a3069e539d70fbd8d8cad12"
CALIBRATION_MAPPINGS_SHA256 = "c1ae8757ca6c11762de46a1ac9e38f28637a56609f634ee8c69353df0ac8a788"
MODEL_SHA256 = (
    "0aca65c4251bd313cec1085f63100dcb8f6b12bd84782992f80961b25f8289a5",
    "ffdb1884339569a3eab3ff55b002e06a9f9a0d56368762e429b054847d9d13de",
    "418e48ea270dc624c046ce13114e2b38eb54751d77258326b997bb2afdcd5c62",
    "219893ff1d5f2edbe46f37ed1f67f7f84db4f4c1f3174639f4aefdd514e2a001",
    "dc3a6ce2aa0d72f99cd2c201657c56060ccadd91445990209c910e9114ee081c",
)
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
SHARD_COUNT = 5
SOURCES_PER_SHARD = 8
PATCHES_PER_OBSERVATION = 1024


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
    temporary = path.with_suffix(path.suffix + f".{uuid.uuid4().hex}.partial")
    frame.to_csv(temporary, index=False)
    temporary.replace(path)


def _write_npz_atomic(path: Path, arrays: dict[str, np.ndarray]) -> None:
    path = Path(path)
    temporary = path.with_suffix(path.suffix + f".{uuid.uuid4().hex}.partial")
    with temporary.open("wb") as stream:
        np.savez_compressed(stream, **arrays)
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
    assert prefix.count("/") == 1, "unexpected ZIP wrapper depth"
    return prefix


def validate_frozen_inputs(
    protocol_text: str,
    receipt_text: str,
    transition_text: str,
    run_code_sha256: str,
) -> tuple[dict, dict, dict]:
    """Verify the exact pre-inference lock and return parsed documents."""

    assert sha256_bytes(protocol_text.encode()) == PROTOCOL_SHA256, "unknown protocol bytes"
    assert sha256_bytes(receipt_text.encode()) == DATA_RECEIPT_SHA256, "unknown data receipt"
    protocol = json.loads(protocol_text)
    receipt = json.loads(receipt_text)
    transition = json.loads(transition_text)

    assert protocol["experiment_id"] == receipt["experiment_id"] == EXPERIMENT_ID
    assert protocol["independent_test_run_authorized"] is False
    assert protocol["test_results_inspected"] is False
    assert receipt["outcome_blind"] is True
    assert receipt["test_inference_performed"] is False
    assert receipt["test_performance_inspected"] is False

    assert transition["experiment_id"] == EXPERIMENT_ID
    assert transition["stage"] == STAGE
    assert transition["outcome_blind"] is True
    assert transition["independent_test_run_authorized"] is True
    assert transition["test_inference_performed_at_transition"] is False
    assert transition["test_performance_inspected_at_transition"] is False
    assert transition["all_readiness_requirements_passed"] is True
    assert transition["protocol_sha256"] == PROTOCOL_SHA256
    assert transition["data_receipt_sha256"] == DATA_RECEIPT_SHA256
    assert transition["run_code_sha256"] == run_code_sha256
    assert transition["test_archive"]["sha256"] == TEST_ARCHIVE_SHA256
    assert transition["test_archive"]["byte_count"] == TEST_ARCHIVE_BYTES
    assert transition["reliability_archive"]["sha256"] == RELIABILITY_ARCHIVE_SHA256
    assert tuple(transition["reliability_archive"]["model_sha256"]) == MODEL_SHA256
    assert transition["reliability_archive"]["calibration_mappings_sha256"] == (
        CALIBRATION_MAPPINGS_SHA256
    )
    assert transition["sharding"]["shard_count"] == SHARD_COUNT
    assert transition["sharding"]["sources_per_shard"] == SOURCES_PER_SHARD
    assert transition["analysis_resolutions"]["h2_region"] == "all"
    assert transition["analysis_resolutions"]["score_tie_break"] == (
        "ascending zero-based patch index"
    )
    assert len(transition["readiness_assertions"]) == len(
        protocol["readiness_requirements_before_independent_inference"]
    )
    assert all(row["passed"] is True for row in transition["readiness_assertions"])

    test = receipt["test_archive"]
    assert test["byte_count"] == TEST_ARCHIVE_BYTES
    assert test["observed_sha256"] == test["publisher_sha256"] == TEST_ARCHIVE_SHA256
    assert test["publisher_digest_match"] is True
    assert len(test["sources"]) == test["eligible_source_count"] == 40
    assert len({row["source_id"] for row in test["sources"]}) == 40
    assert all(
        row["mode"] == "RGB" and row["width"] == row["height"] == 2400
        for row in test["sources"]
    )
    duplicate = receipt["duplicate_audit"]
    assert duplicate["complete"] is True
    assert duplicate["pair_count"] == 3840
    assert duplicate["candidate_count"] == duplicate["exact_match_count"] == 0
    return protocol, receipt, transition


def ordered_test_sources(receipt: dict) -> tuple[str, ...]:
    source_ids = tuple(sorted(row["source_id"] for row in receipt["test_archive"]["sources"]))
    assert len(source_ids) == 40 and len(set(source_ids)) == 40
    return source_ids


def sources_for_shard(receipt: dict, shard_index: int) -> tuple[str, ...]:
    assert 0 <= int(shard_index) < SHARD_COUNT
    source_ids = ordered_test_sources(receipt)
    start = int(shard_index) * SOURCES_PER_SHARD
    selected = source_ids[start : start + SOURCES_PER_SHARD]
    assert len(selected) == SOURCES_PER_SHARD
    return selected


def derive_config(protocol: dict, selected_sources: tuple[str, ...], shard_index: int) -> dict:
    config = C05.derive_config(protocol)
    config.update(
        experiment=EXPERIMENT_ID,
        stage=STAGE,
        role=ROLE,
        source_ids=list(selected_sources),
        chain_ids=list(CHAIN_IDS),
        shard_index=int(shard_index),
        shard_count=SHARD_COUNT,
        test_inference_authorized=True,
        test_performance_inspection_authorized=False,
    )
    return config


def inspect_reliability_archive(archive_path: Path, cache_dir: Path) -> dict:
    """Verify every manifested byte, then extract only the frozen inference assets."""

    archive_path, cache_dir = Path(archive_path), Path(cache_dir)
    assert archive_path.is_file(), f"missing reliability archive: {archive_path}"
    assert sha256_file(archive_path) == RELIABILITY_ARCHIVE_SHA256
    cache_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        prefix = _archive_prefix(names)
        manifest_payload = archive.read(prefix + "export_manifest.json")
        manifest = json.loads(manifest_payload)
        assert manifest["experiment_id"] == EXPERIMENT_ID
        assert manifest["stage"] == "05C2_development_reliability_training_and_calibration"
        assert manifest["role"] == "development_only"
        assert manifest["test_inference_performed"] is False
        assert manifest["independent_test_run_authorized"] is False
        expected_names = {prefix + "export_manifest.json"}
        for row in manifest["files"]:
            name = prefix + row["path"]
            expected_names.add(name)
            payload = archive.read(name)
            assert len(payload) == row["byte_count"], name
            assert sha256_bytes(payload) == row["sha256"], name
        assert set(names) == expected_names

        required = [f"models/member_{index:02d}_best.pt" for index in range(5)]
        required.append("calibration_mappings.json")
        for relative in required:
            payload = archive.read(prefix + relative)
            destination = cache_dir / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                assert sha256_bytes(destination.read_bytes()) == sha256_bytes(payload)
            else:
                destination.write_bytes(payload)

    for index, expected_hash in enumerate(MODEL_SHA256):
        path = cache_dir / "models" / f"member_{index:02d}_best.pt"
        assert sha256_file(path) == expected_hash
    mappings_path = cache_dir / "calibration_mappings.json"
    assert sha256_file(mappings_path) == CALIBRATION_MAPPINGS_SHA256
    mappings = json.loads(mappings_path.read_text(encoding="utf-8"))
    assert mappings["fit_partition"] == "DIV2K 0869-0900 only"
    assert mappings["test_inference_performed"] is False
    assert mappings["independent_test_run_authorized"] is False
    assert len(mappings["mappings"]) == 11
    return {
        "archive_sha256": RELIABILITY_ARCHIVE_SHA256,
        "manifested_files": len(manifest["files"]),
        "model_sha256": list(MODEL_SHA256),
        "calibration_mappings_sha256": CALIBRATION_MAPPINGS_SHA256,
        "cache_dir": str(cache_dir),
    }


def load_test_sources(
    archive_path: Path, receipt: dict, selected_sources: tuple[str, ...], config: dict
) -> tuple[dict[str, np.ndarray], pd.DataFrame]:
    """Verify the sealed archive and load only the fixed shard's source bytes."""

    archive_path = Path(archive_path)
    assert archive_path.is_file(), f"missing test archive: {archive_path}"
    assert archive_path.stat().st_size == TEST_ARCHIVE_BYTES
    assert sha256_file(archive_path) == TEST_ARCHIVE_SHA256
    expected_rows = {row["source_id"]: row for row in receipt["test_archive"]["sources"]}
    assert tuple(selected_sources) == tuple(sorted(selected_sources))
    assert set(selected_sources) <= set(expected_rows)
    extent = config["crop_size"] + 2 * config["context_border"]
    sources, rows = {}, []
    with tarfile.open(archive_path, mode="r:bz2") as archive:
        file_members = {member.name: member for member in archive.getmembers() if member.isfile()}
        expected_members = {row["member_path"] for row in expected_rows.values()}
        assert expected_members <= set(file_members), "test archive member set changed"
        for source_id in selected_sources:
            expected = expected_rows[source_id]
            member = file_members[expected["member_path"]]
            assert member.size == expected["byte_count"]
            stream = archive.extractfile(member)
            assert stream is not None
            payload = stream.read()
            assert len(payload) == expected["byte_count"]
            assert sha256_bytes(payload) == expected["sha256"]
            with Image.open(io.BytesIO(payload)) as image:
                image.load()
                assert image.format == "PNG" and image.mode == "RGB"
                width, height = image.size
                rgb = np.asarray(image, dtype=np.uint8)
            assert (width, height) == (expected["width"], expected["height"]) == (2400, 2400)
            left, top = (width - extent) // 2, (height - extent) // 2
            crop = rgb[top : top + extent, left : left + extent].astype(np.float64) / 255.0
            assert crop.shape == (extent, extent, 3)
            sources[source_id] = crop
            rows.append(
                {
                    "source_id": source_id,
                    "filename": PurePosixPath(expected["member_path"]).name,
                    "member_path": expected["member_path"],
                    "file_byte_count": len(payload),
                    "file_sha256": expected["sha256"],
                    "decoded_rgb_sha256": sha256_bytes(rgb.tobytes()),
                    "width": width,
                    "height": height,
                    "crop_left": left,
                    "crop_top": top,
                    "crop_extent": extent,
                    "role": ROLE,
                }
            )
    return sources, pd.DataFrame(rows)


def _operational_score_arrays(score_arrays: dict, ensemble_mean: np.ndarray) -> dict:
    result = {}
    for pipeline in PIPELINES:
        for score in HEURISTIC_SCORES:
            key = f"{pipeline}__score__{score}"
            value = np.asarray(score_arrays[key], dtype=np.float64)
            assert value.shape == (PATCHES_PER_OBSERVATION,) and np.isfinite(value).all()
            result[key] = value
    assert ensemble_mean.shape == (PATCHES_PER_OBSERVATION,)
    result[ENSEMBLE_SCORE] = np.asarray(ensemble_mean, dtype=np.float64)
    return result


def _risk_rows(
    estimates: dict,
    score_arrays: dict,
    ensemble_mean: np.ndarray,
    config: dict,
) -> list[dict]:
    """Apply the frozen raw-score ranking with deterministic index tie-breaking."""

    operational = _operational_score_arrays(score_arrays, ensemble_mean)
    texture = np.asarray(
        score_arrays["fbcnn_dpir_nominal__score__reference_texture"], dtype=np.float64
    )
    assert texture.shape == (PATCHES_PER_OBSERVATION,)
    textured = np.argsort(texture, kind="stable")[-int(math.ceil(len(texture) / 4)) :]
    rows = []
    for pipeline in PIPELINES:
        rgb = np.asarray(estimates[f"{pipeline}__rgb_patch_error"], dtype=np.float64)
        detail = np.asarray(estimates[f"{pipeline}__detail_patch_error"], dtype=np.float64)
        assert rgb.shape == detail.shape == (PATCHES_PER_OBSERVATION,)
        score_keys = [f"{pipeline}__score__{score}" for score in HEURISTIC_SCORES]
        if pipeline == "fbcnn_dpir_nominal":
            score_keys.append(ENSEMBLE_SCORE)
        score_specs = [(key, "operational", operational[key]) for key in score_keys]
        score_specs.extend(
            [
                (f"{pipeline}__expected_random", "evaluation_only", None),
                (f"{pipeline}__oracle_detail_error", "evaluation_only", detail),
            ]
        )
        for region, ids in (
            ("all", np.arange(PATCHES_PER_OBSERVATION, dtype=np.int16)),
            ("textured_quartile", textured),
        ):
            region_rgb, region_detail = rgb[ids], detail[ids]
            for score_key, score_role, score in score_specs:
                if score is None:
                    order = None
                else:
                    order = np.lexsort((ids, np.asarray(score)[ids]))
                for coverage in config["coverages"]:
                    count = int(math.ceil(float(coverage) * len(ids)))
                    chosen = np.arange(len(ids)) if order is None else order[:count]
                    selected_rgb, selected_detail = region_rgb[chosen], region_detail[chosen]
                    short_score = score_key.split("__score__", 1)[-1]
                    if score_key == ENSEMBLE_SCORE:
                        short_score = "trained_image_only_patcherrornet_ensemble"
                    elif score_key.endswith("__expected_random"):
                        short_score = "expected_random"
                    elif score_key.endswith("__oracle_detail_error"):
                        short_score = "oracle_detail_error"
                    row = {
                        "pipeline": pipeline,
                        "region": region,
                        "score": short_score,
                        "score_key": score_key,
                        "score_role": score_role,
                        "coverage": float(coverage),
                        "available_patches": len(ids),
                        "retained_patches": count,
                        "rgb_mse": float(selected_rgb.mean()),
                        "detail_mse": float(selected_detail.mean()),
                    }
                    for threshold in config["detail_rmse_tolerances"]:
                        row[f"bad_detail_rate_{threshold:g}"] = float(
                            (np.sqrt(selected_detail) > threshold).mean()
                        )
                    rows.append(row)
    assert len(rows) == 120
    return rows


def compact_arrays(
    observation: np.ndarray,
    estimates: dict,
    score_arrays: dict,
    ensemble_mean: np.ndarray,
    ensemble_variance: np.ndarray,
    mappings: dict,
) -> dict[str, np.ndarray]:
    observation_uint8 = np.rint(observation * 255.0).astype(np.uint8)
    assert np.array_equal(observation_uint8.astype(np.float64) / 255.0, observation)
    operational = _operational_score_arrays(score_arrays, ensemble_mean)
    target_detail = np.asarray(
        estimates["fbcnn_dpir_nominal__detail_patch_error"], dtype=np.float64
    )
    result = {
        "observation_uint8": observation_uint8,
        "fbcnn_dpir_nominal": estimates["fbcnn_dpir_nominal"].astype(np.float32),
        "dpir_nominal__rgb_patch_error": estimates["dpir_nominal__rgb_patch_error"].astype(
            np.float32
        ),
        "dpir_nominal__detail_patch_error": estimates[
            "dpir_nominal__detail_patch_error"
        ].astype(np.float32),
        "fbcnn_dpir_nominal__rgb_patch_error": estimates[
            "fbcnn_dpir_nominal__rgb_patch_error"
        ].astype(np.float32),
        "fbcnn_dpir_nominal__detail_patch_error": target_detail.astype(np.float32),
        "target_bad_detail_0p05": (np.sqrt(target_detail) > 0.05).astype(np.uint8),
        "reference_texture": np.asarray(
            score_arrays["fbcnn_dpir_nominal__score__reference_texture"], dtype=np.float32
        ),
        ENSEMBLE_VARIANCE: ensemble_variance.astype(np.float32),
    }
    for key, values in operational.items():
        result[key] = values.astype(np.float32)
        result[f"{key}__calibrated_probability"] = RT05.apply_isotonic_mapping(
            values, mappings[key]
        ).astype(np.float32)
    assert len(mappings) == 11
    assert all(np.isfinite(value).all() for value in result.values())
    assert result["target_bad_detail_0p05"].shape == (PATCHES_PER_OBSERVATION,)
    return result


def _completed_record(record_path: Path, compact_path: Path, lock: dict) -> dict | None:
    if not record_path.exists() and not compact_path.exists():
        return None
    assert record_path.is_file() and compact_path.is_file(), (
        "partial observation preserved; inspect before retry",
        record_path,
        compact_path,
    )
    record = json.loads(record_path.read_text(encoding="utf-8"))
    assert record["lock"] == lock
    assert record["compact_file"]["byte_count"] == compact_path.stat().st_size
    assert record["compact_file"]["sha256"] == sha256_file(compact_path)
    return record


def _write_status(
    output_dir: Path,
    config: dict,
    state: str,
    completed: int,
    expected: int,
) -> None:
    dump_json(
        output_dir / "status.json",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": STAGE,
            "role": ROLE,
            "status": state,
            "shard_index": config["shard_index"],
            "shard_count": SHARD_COUNT,
            "source_ids": config["source_ids"],
            "chain_ids": list(CHAIN_IDS),
            "completed_observations": completed,
            "expected_observations": expected,
            "independent_test_run_authorized": True,
            "test_inference_performed": completed > 0,
            "test_performance_inspected": False,
            "aggregate_analysis_performed": False,
            "unsealed": False,
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
    )


def _write_locked_metadata(path: Path, value) -> None:
    if path.exists():
        assert json.loads(path.read_text(encoding="utf-8")) == _normalize(value)
    else:
        dump_json(path, value)


def run_shard(
    test_archive,
    reliability_archive,
    reliability_cache,
    output_dir,
    protocol_text,
    receipt_text,
    transition_text,
    run_code_sha256,
    provenance,
    vendor_dirs,
    dpir_weights,
    fbcnn_weights,
    shard_index,
):
    """Run one fixed eight-source independent shard without displaying outcomes."""

    protocol, receipt, transition = validate_frozen_inputs(
        protocol_text, receipt_text, transition_text, run_code_sha256
    )
    selected_sources = sources_for_shard(receipt, int(shard_index))
    assert transition["sharding"]["source_ids_by_shard"][str(int(shard_index))] == list(
        selected_sources
    )
    config = derive_config(protocol, selected_sources, int(shard_index))
    chains_by_id = {row["id"]: row for row in protocol["simulation"]["acquisition_chains"]}
    assert tuple(chains_by_id) == CHAIN_IDS
    chains = [chains_by_id[chain_id] for chain_id in CHAIN_IDS]

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    compact_dir, record_dir = output_dir / "compact", output_dir / "records"
    compact_dir.mkdir(exist_ok=True)
    record_dir.mkdir(exist_ok=True)
    lock = {
        "protocol_sha256": PROTOCOL_SHA256,
        "data_receipt_sha256": DATA_RECEIPT_SHA256,
        "transition_sha256": sha256_bytes(transition_text.encode()),
        "run_code_sha256": run_code_sha256,
        "test_archive_sha256": TEST_ARCHIVE_SHA256,
        "reliability_archive_sha256": RELIABILITY_ARCHIVE_SHA256,
    }
    _write_locked_metadata(output_dir / "config.json", config)
    _write_locked_metadata(output_dir / "lock.json", lock)
    _write_locked_metadata(output_dir / "provenance.json", provenance)

    reliability_check = inspect_reliability_archive(
        Path(reliability_archive), Path(reliability_cache)
    )
    mappings_document = json.loads(
        (Path(reliability_cache) / "calibration_mappings.json").read_text(encoding="utf-8")
    )
    mappings = mappings_document["mappings"]
    sources, source_manifest = load_test_sources(
        Path(test_archive), receipt, selected_sources, config
    )
    repeat = C05.verify_acquisition_determinism(sources, chains, config)
    assert len(repeat) == SOURCES_PER_SHARD * len(CHAIN_IDS)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    assert device.type == "cuda", "locked independent inference requires a CUDA GPU"
    RT05.configure_determinism(protocol["simulation"]["seed"])
    C05.L02.download_weights(dpir_weights, provenance["dpir"])
    drunet, device = C05.L02.load_model(
        vendor_dirs["dpir"], dpir_weights, provenance["dpir"], config
    )
    dpir_checks = C05.L02.validate_adapter(drunet, device, vendor_dirs["dpir"], config)
    fbcnn, fbcnn_parameters = C05.J04.load_fbcnn(
        vendor_dirs["fbcnn"], fbcnn_weights, provenance["fbcnn"], device
    )
    fbcnn_checks = C05.J04.validate_fbcnn(fbcnn, device)
    models = RT05.load_frozen_ensemble(Path(reliability_cache), device)
    assert len(models) == 5

    expected = SOURCES_PER_SHARD * len(CHAIN_IDS)
    completed = 0
    _write_status(output_dir, config, "running_sealed", completed, expected)
    for source_id in selected_sources:
        reference = sources[source_id]
        for chain in chains:
            observation_id = f"{source_id}_{chain['id']}"
            compact_path = compact_dir / f"{observation_id}.npz"
            record_path = record_dir / f"{observation_id}.json"
            record = _completed_record(record_path, compact_path, lock)
            if record is None:
                observation, jpeg_payload, acquisition = C05.acquire(
                    reference, source_id, chain, config
                )
                estimates, compute_rows, trace_rows, fbcnn_rows = C05._reconstruct_observation(
                    observation, fbcnn, drunet, device, config
                )
                quality_rows = C05._error_rows(
                    reference, estimates, source_id, chain["id"], config
                )
                _, score_arrays = C05._score_rows(
                    reference, observation, estimates, config
                )
                reliability_inputs = {
                    "observation_uint8": np.rint(observation * 255.0).astype(np.uint8),
                    "fbcnn_dpir_nominal": estimates["fbcnn_dpir_nominal"].astype(np.float32),
                    "target_bad_detail_0p05": (
                        np.sqrt(estimates["fbcnn_dpir_nominal__detail_patch_error"]) > 0.05
                    ).astype(np.uint8),
                }
                ensemble_mean, ensemble_variance = RT05.ensemble_probabilities(
                    reliability_inputs, observation_id, models, device
                )
                risk_rows = _risk_rows(
                    estimates, score_arrays, ensemble_mean, config
                )
                arrays = compact_arrays(
                    observation,
                    estimates,
                    score_arrays,
                    ensemble_mean,
                    ensemble_variance,
                    mappings,
                )
                _write_npz_atomic(compact_path, arrays)
                repeat_row = repeat[
                    (repeat.source_id == source_id) & (repeat.chain_id == chain["id"])
                ].iloc[0]
                record = {
                    "source_id": source_id,
                    "chain_id": chain["id"],
                    "role": ROLE,
                    "lock": lock,
                    "acquisition": acquisition,
                    "acquisition_repeat": repeat_row.to_dict(),
                    "quality": quality_rows,
                    "risk": [
                        {"source_id": source_id, "chain_id": chain["id"], **row}
                        for row in risk_rows
                    ],
                    "compute": [
                        {"source_id": source_id, "chain_id": chain["id"], **row}
                        for row in compute_rows
                    ],
                    "trajectories": [
                        {"source_id": source_id, "chain_id": chain["id"], **row}
                        for row in trace_rows
                    ],
                    "fbcnn_diagnostics": [
                        {"source_id": source_id, "chain_id": chain["id"], **row}
                        for row in fbcnn_rows
                    ],
                    "jpeg_byte_count": len(jpeg_payload),
                    "jpeg_sha256": sha256_bytes(jpeg_payload) if jpeg_payload else "",
                    "compact_file": {
                        "path": str(compact_path.relative_to(output_dir)),
                        "byte_count": compact_path.stat().st_size,
                        "sha256": sha256_file(compact_path),
                        "arrays": sorted(arrays),
                    },
                    "test_inference_performed": True,
                    "test_performance_inspected": False,
                    "unsealed": False,
                }
                dump_json(record_path, record)
            completed += 1
            _write_status(output_dir, config, "running_sealed", completed, expected)
            print(f"[{completed}/{expected}] sealed observation complete: {observation_id}", flush=True)

    records = []
    for source_id in selected_sources:
        for chain_id in CHAIN_IDS:
            observation_id = f"{source_id}_{chain_id}"
            record = _completed_record(
                record_dir / f"{observation_id}.json",
                compact_dir / f"{observation_id}.npz",
                lock,
            )
            assert record is not None
            records.append(record)

    def rows(name: str) -> list[dict]:
        result = []
        for record in records:
            value = record[name]
            result.extend(value if isinstance(value, list) else [value])
        return result

    source_manifest = source_manifest.sort_values("source_id").reset_index(drop=True)
    dump_csv(output_dir / "source_manifest.csv", source_manifest)
    dump_csv(output_dir / "acquisition_repeat_check.csv", repeat)
    dump_csv(output_dir / "acquisition.csv", pd.DataFrame(rows("acquisition")))
    dump_csv(output_dir / "quality.csv", pd.DataFrame(rows("quality")))
    dump_csv(output_dir / "risk.csv", pd.DataFrame(rows("risk")))
    dump_csv(output_dir / "compute.csv", pd.DataFrame(rows("compute")))
    dump_csv(output_dir / "trajectories.csv", pd.DataFrame(rows("trajectories")))
    dump_csv(output_dir / "fbcnn_diagnostics.csv", pd.DataFrame(rows("fbcnn_diagnostics")))

    compute = pd.DataFrame(rows("compute"))
    checks = {
        "scope_guard_passed": True,
        "authorization_transition_verified": True,
        "sources": SOURCES_PER_SHARD,
        "chains": len(CHAIN_IDS),
        "observations": expected,
        "quality_rows": expected * len(C05.PRIMARY_METHODS),
        "risk_rows": expected * 120,
        "drunet_experiment_calls": expected * 80,
        "fbcnn_experiment_calls": expected * 3,
        "compact_bundles": expected,
        "ensemble_members": 5,
        "calibration_mappings": 11,
        "dpir": dpir_checks,
        "fbcnn": {**fbcnn_checks, "parameter_count": fbcnn_parameters},
        "reliability": reliability_check,
        "test_inference_performed": True,
        "test_performance_inspected": False,
        "aggregate_analysis_performed": False,
        "unsealed": False,
    }
    assert len(rows("quality")) == checks["quality_rows"]
    assert len(rows("risk")) == checks["risk_rows"]
    assert int(compute.denoiser_calls.sum()) == checks["drunet_experiment_calls"]
    assert int(compute.fbcnn_calls.sum()) == checks["fbcnn_experiment_calls"]
    dump_json(output_dir / "checks.json", checks)
    _write_status(output_dir, config, "passed_locked_independent_shard", expected, expected)

    manifest_files = []
    for path in sorted(output_dir.rglob("*")):
        if (
            path.is_file()
            and path.name != "export_manifest.json"
            and ".partial" not in path.name
        ):
            manifest_files.append(
                {
                    "path": str(path.relative_to(output_dir)),
                    "byte_count": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    manifest = {
        "experiment_id": EXPERIMENT_ID,
        "stage": STAGE,
        "role": ROLE,
        "status": "passed_locked_independent_shard",
        "shard_index": int(shard_index),
        "shard_count": SHARD_COUNT,
        "source_ids": list(selected_sources),
        "chain_ids": list(CHAIN_IDS),
        "lock": lock,
        "independent_test_run_authorized": True,
        "test_inference_performed": True,
        "test_performance_inspected": False,
        "aggregate_analysis_performed": False,
        "unsealed": False,
        "files": manifest_files,
    }
    dump_json(output_dir / "export_manifest.json", manifest)
    return {
        "status": "passed_locked_independent_shard",
        "shard_index": int(shard_index),
        "completed_observations": expected,
        "export_manifest_sha256": sha256_file(output_dir / "export_manifest.json"),
        "output_dir": str(output_dir),
        "test_performance_inspected": False,
        "unsealed": False,
    }


def static_self_check() -> dict:
    assert SHARD_COUNT * SOURCES_PER_SHARD == 40
    assert len(CHAIN_IDS) == 7
    assert len(PIPELINES) == 2 and len(HEURISTIC_SCORES) == 5
    assert len(MODEL_SHA256) == 5 and len(set(MODEL_SHA256)) == 5
    assert all(len(value) == 64 for value in MODEL_SHA256)
    return {
        "experiment_id": EXPERIMENT_ID,
        "stage": STAGE,
        "shards": SHARD_COUNT,
        "sources_per_shard": SOURCES_PER_SHARD,
        "observations_per_shard": SOURCES_PER_SHARD * len(CHAIN_IDS),
        "operational_scores": 11,
        "performance_display_code_present": False,
        "aggregate_analysis_code_present": False,
    }
