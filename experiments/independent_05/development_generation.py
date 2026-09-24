"""Sharded development-data generation for Experiment 05.

This module reuses the independently audited reconstruction adapters from the
stage-05C canary, but it can only load the locked DIV2K development range
0805-0900. It writes compact training/calibration bundles and resumable
per-observation records. It has no code path for TESTIMAGES.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
import torch


C05 = None

DEVELOPMENT_SOURCE_IDS = tuple(f"{value:04d}" for value in range(805, 901))
FIT_SOURCE_IDS = tuple(f"{value:04d}" for value in range(805, 857))
EARLY_STOP_SOURCE_IDS = tuple(f"{value:04d}" for value in range(857, 869))
CALIBRATION_SOURCE_IDS = tuple(f"{value:04d}" for value in range(869, 901))
CHAIN_IDS = (
    "q8_b16_n2",
    "j90_b16_n2",
    "j75_b16_n2",
    "j50_b16_n2",
    "j75_b12_n2",
    "j75_b20_n2",
    "j75_b16_n5",
)
COMPACT_PIPELINES = ("dpir_nominal", "fbcnn_dpir_nominal")
COMPACT_HEURISTIC_SCORES = (
    "operator_spread_detail",
    "operator_spread_rgb",
    "image_transform_spread_detail",
    "original_measurement_residual",
    "reconstruction_gradient",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def dump_json(path: Path, value) -> None:
    def normalize(item):
        if isinstance(item, dict):
            return {str(key): normalize(val) for key, val in item.items()}
        if isinstance(item, (list, tuple)):
            return [normalize(val) for val in item]
        if isinstance(item, np.generic):
            return item.item()
        return item

    Path(path).write_text(
        json.dumps(normalize(value), indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def source_partition(source_id: str) -> str:
    if source_id in FIT_SOURCE_IDS:
        return "fit"
    if source_id in EARLY_STOP_SOURCE_IDS:
        return "early_stop"
    if source_id in CALIBRATION_SOURCE_IDS:
        return "calibration"
    raise ValueError(f"source outside frozen development partitions: {source_id}")


def shard_sources(shard_index: int, shard_size: int = 8) -> tuple[str, ...]:
    assert shard_size > 0
    shard_count = int(np.ceil(len(DEVELOPMENT_SOURCE_IDS) / shard_size))
    assert 0 <= shard_index < shard_count, (shard_index, shard_count)
    start = shard_index * shard_size
    return DEVELOPMENT_SOURCE_IDS[start : start + shard_size]


def derive_config(protocol: dict, selected_sources: tuple[str, ...]) -> dict:
    assert selected_sources
    assert len(selected_sources) == len(set(selected_sources))
    assert set(selected_sources) <= set(DEVELOPMENT_SOURCE_IDS)
    config = C05.derive_config(protocol)
    config["experiment"] = "independent_05_development_generation"
    config["stage"] = "05C_development_generation"
    config["source_ids"] = list(selected_sources)
    config["chain_ids"] = list(CHAIN_IDS)
    config["compact_storage"] = {
        "observation": "uint8 exact decoded observation",
        "fbcnn_dpir_nominal": "float32 exact network-output precision",
        "patch_errors_and_scores": "float32",
        "target": "uint8(detail RMSE > 0.05)",
    }
    return config


def validate_scope(protocol: dict, receipt: dict, config: dict, provenance: dict) -> list[dict]:
    assert protocol["independent_test_run_authorized"] is False
    assert protocol["test_results_inspected"] is False
    assert receipt["test_inference_performed"] is False
    assert provenance["experiment"] == "independent_05"
    assert provenance["stage"] == "05C_development_generation"
    assert provenance["role"] == "development_only"
    assert set(config["source_ids"]) <= set(DEVELOPMENT_SOURCE_IDS)
    assert tuple(config["chain_ids"]) == CHAIN_IDS
    assert not set(config["source_ids"]) & {
        row["source_id"] for row in receipt["test_archive"]["sources"]
    }
    frozen = {row["id"]: row for row in protocol["simulation"]["acquisition_chains"]}
    assert tuple(frozen) == CHAIN_IDS
    return [frozen[chain_id] for chain_id in CHAIN_IDS]


def load_sources(data_dir: Path, receipt: dict, config: dict) -> tuple[dict, pd.DataFrame]:
    data_dir = Path(data_dir)
    receipt_map = {row["source_id"]: row for row in receipt["development_archive"]["sources"]}
    extent = config["crop_size"] + 2 * config["context_border"]
    sources, rows = {}, []
    for source_id in config["source_ids"]:
        assert source_id in DEVELOPMENT_SOURCE_IDS
        path = data_dir / f"{source_id}.png"
        assert path.is_file(), f"missing development source: {path}"
        expected = receipt_map[source_id]
        assert sha256_file(path) == expected["sha256"], f"changed source bytes: {source_id}"
        with Image.open(path) as image:
            image.load()
            assert image.format == "PNG" and image.mode == "RGB"
            width, height = image.size
            rgb = np.asarray(image, dtype=np.uint8)
        assert (width, height) == (expected["width"], expected["height"])
        left, top = (width - extent) // 2, (height - extent) // 2
        crop = rgb[top : top + extent, left : left + extent].astype(np.float64) / 255.0
        assert crop.shape == (extent, extent, 3)
        sources[source_id] = crop
        rows.append(
            {
                "source_id": source_id,
                "partition": source_partition(source_id),
                "filename": path.name,
                "file_sha256": expected["sha256"],
                "decoded_rgb_sha256": hashlib.sha256(rgb.tobytes()).hexdigest(),
                "width": width,
                "height": height,
                "crop_left": left,
                "crop_top": top,
                "crop_extent": extent,
                "role": "development_only",
            }
        )
    return sources, pd.DataFrame(rows)


def compact_arrays(observation: np.ndarray, estimates: dict, score_arrays: dict) -> dict:
    observation_uint8 = np.rint(observation * 255.0).astype(np.uint8)
    assert np.array_equal(observation_uint8.astype(np.float64) / 255.0, observation)
    detail_error = estimates["fbcnn_dpir_nominal__detail_patch_error"]
    result = {
        "observation_uint8": observation_uint8,
        "fbcnn_dpir_nominal": estimates["fbcnn_dpir_nominal"].astype(np.float32),
        "detail_patch_error": detail_error.astype(np.float32),
        "target_bad_detail_0p05": (np.sqrt(detail_error) > 0.05).astype(np.uint8),
    }
    for pipeline in COMPACT_PIPELINES:
        for score in COMPACT_HEURISTIC_SCORES:
            key = f"{pipeline}__score__{score}"
            value = score_arrays[key]
            assert value.shape == (1024,) and np.isfinite(value).all()
            result[key] = value.astype(np.float32)
    assert result["target_bad_detail_0p05"].shape == (1024,)
    return result


def _write_npz_atomic(path: Path, arrays: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".partial")
    with temporary.open("wb") as stream:
        np.savez_compressed(stream, **arrays)
    temporary.replace(path)


def _load_completed_record(record_path: Path, compact_path: Path) -> dict | None:
    if not record_path.exists() and not compact_path.exists():
        return None
    assert record_path.is_file() and compact_path.is_file(), (
        "partial observation preserved; inspect before retry",
        record_path,
        compact_path,
    )
    record = json.loads(record_path.read_text(encoding="utf-8"))
    assert record["compact_file"]["byte_count"] == compact_path.stat().st_size
    assert record["compact_file"]["sha256"] == sha256_file(compact_path)
    return record


def _write_record_atomic(path: Path, record: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".partial")
    dump_json(temporary, record)
    temporary.replace(path)


def _write_status(output_dir: Path, config: dict, state: str, complete: int, total: int) -> None:
    dump_json(
        output_dir / "status.json",
        {
            "experiment_id": "independent_05",
            "stage": "05C_development_generation",
            "role": "development_only",
            "status": state,
            "source_ids": config["source_ids"],
            "chain_ids": config["chain_ids"],
            "completed_observations": complete,
            "expected_observations": total,
            "test_inference_performed": False,
            "test_performance_inspected": False,
            "independent_test_run_authorized": False,
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
    )


def run_shard(
    data_dir,
    output_dir,
    protocol,
    receipt,
    provenance,
    vendor_dirs,
    dpir_weights,
    fbcnn_weights,
    selected_sources,
):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    compact_dir, record_dir = output_dir / "compact", output_dir / "records"
    compact_dir.mkdir(exist_ok=True)
    record_dir.mkdir(exist_ok=True)

    config = derive_config(protocol, tuple(selected_sources))
    chains = validate_scope(protocol, receipt, config, provenance)
    sources, source_manifest = load_sources(Path(data_dir), receipt, config)
    repeat = C05.verify_acquisition_determinism(sources, chains, config)
    assert len(repeat) == len(selected_sources) * len(CHAIN_IDS)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    assert device.type == "cuda", "development generation requires a CUDA GPU"
    C05.L02.download_weights(dpir_weights, provenance["dpir"])
    drunet, device = C05.L02.load_model(vendor_dirs["dpir"], dpir_weights, provenance["dpir"], config)
    dpir_checks = C05.L02.validate_adapter(drunet, device, vendor_dirs["dpir"], config)
    fbcnn, fbcnn_parameters = C05.J04.load_fbcnn(
        vendor_dirs["fbcnn"], fbcnn_weights, provenance["fbcnn"], device
    )
    fbcnn_checks = C05.J04.validate_fbcnn(fbcnn, device)

    expected = len(selected_sources) * len(CHAIN_IDS)
    completed = 0
    _write_status(output_dir, config, "running", completed, expected)
    for source_id in selected_sources:
        reference = sources[source_id]
        for chain in chains:
            observation_id = f"{source_id}_{chain['id']}"
            compact_path = compact_dir / f"{observation_id}.npz"
            record_path = record_dir / f"{observation_id}.json"
            record = _load_completed_record(record_path, compact_path)
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
                risk_rows, score_arrays = C05._score_rows(
                    reference, observation, estimates, config
                )
                arrays = compact_arrays(observation, estimates, score_arrays)
                _write_npz_atomic(compact_path, arrays)
                record = {
                    "source_id": source_id,
                    "partition": source_partition(source_id),
                    "chain_id": chain["id"],
                    "acquisition": acquisition,
                    "acquisition_repeat": repeat[
                        (repeat.source_id == source_id) & (repeat.chain_id == chain["id"])
                    ].iloc[0].to_dict(),
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
                    "jpeg_sha256": hashlib.sha256(jpeg_payload).hexdigest()
                    if jpeg_payload
                    else "",
                    "compact_file": {
                        "path": str(compact_path.relative_to(output_dir)),
                        "byte_count": compact_path.stat().st_size,
                        "sha256": sha256_file(compact_path),
                        "arrays": sorted(arrays),
                    },
                }
                _write_record_atomic(record_path, record)
            completed += 1
            _write_status(output_dir, config, "running", completed, expected)
            print(f"[{completed}/{expected}] {observation_id}", flush=True)

    records = []
    for source_id in selected_sources:
        for chain_id in CHAIN_IDS:
            compact_path = compact_dir / f"{source_id}_{chain_id}.npz"
            record_path = record_dir / f"{source_id}_{chain_id}.json"
            record = _load_completed_record(record_path, compact_path)
            assert record is not None
            records.append(record)

    def rows(name):
        result = []
        for record in records:
            value = record[name]
            result.extend(value if isinstance(value, list) else [value])
        return result

    source_manifest.to_csv(output_dir / "source_manifest.csv", index=False)
    repeat.to_csv(output_dir / "acquisition_repeat_check.csv", index=False)
    pd.DataFrame(rows("acquisition")).to_csv(output_dir / "acquisition.csv", index=False)
    pd.DataFrame(rows("quality")).to_csv(output_dir / "quality.csv", index=False)
    pd.DataFrame(rows("risk")).to_csv(output_dir / "risk.csv", index=False)
    pd.DataFrame(rows("compute")).to_csv(output_dir / "compute.csv", index=False)
    pd.DataFrame(rows("trajectories")).to_csv(output_dir / "trajectories.csv", index=False)
    pd.DataFrame(rows("fbcnn_diagnostics")).to_csv(
        output_dir / "fbcnn_diagnostics.csv", index=False
    )
    dump_json(output_dir / "config.json", config)
    dump_json(output_dir / "provenance.json", provenance)
    checks = {
        "scope_guard_passed": True,
        "sources": len(selected_sources),
        "chains": len(CHAIN_IDS),
        "observations": expected,
        "quality_rows": expected * len(C05.PRIMARY_METHODS),
        "risk_rows": expected * 112,
        "drunet_experiment_calls": expected * 80,
        "fbcnn_experiment_calls": expected * 3,
        "compact_bundles": expected,
        "dpir": dpir_checks,
        "fbcnn": {**fbcnn_checks, "parameter_count": fbcnn_parameters},
        "patcherrornet_fit_performed": False,
        "calibration_fit_performed": False,
        "test_inference_performed": False,
    }
    assert len(rows("quality")) == checks["quality_rows"]
    assert len(rows("risk")) == checks["risk_rows"]
    assert int(pd.DataFrame(rows("compute")).denoiser_calls.sum()) == checks[
        "drunet_experiment_calls"
    ]
    assert int(pd.DataFrame(rows("compute")).fbcnn_calls.sum()) == checks[
        "fbcnn_experiment_calls"
    ]
    dump_json(output_dir / "checks.json", checks)
    _write_status(output_dir, config, "passed_development_shard", expected, expected)

    manifest = []
    for path in sorted(output_dir.rglob("*")):
        if path.is_file() and path.name != "export_manifest.json":
            manifest.append(
                {
                    "path": str(path.relative_to(output_dir)),
                    "byte_count": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    dump_json(
        output_dir / "export_manifest.json",
        {
            "experiment_id": "independent_05",
            "stage": "05C_development_generation",
            "role": "development_only",
            "source_ids": list(selected_sources),
            "chain_ids": list(CHAIN_IDS),
            "test_inference_performed": False,
            "files": manifest,
        },
    )
    return {"output_dir": output_dir, "checks": checks, "status": "passed_development_shard"}
