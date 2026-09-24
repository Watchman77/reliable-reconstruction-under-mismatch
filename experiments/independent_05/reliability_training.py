"""Development-only PatchErrorNet training and calibration for Experiment 05.

This module consumes only the 12 verified DIV2K development shard archives. It
has no loader for TESTIMAGES and cannot authorize independent inference.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import os
import platform
import random
import re
import uuid
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

import numpy as np
import pandas as pd
import torch
import torchvision
import sklearn
from sklearn.isotonic import IsotonicRegression


EXPERIMENT_ID = "independent_05"
STAGE = "05C2_development_reliability_training_and_calibration"
ROLE = "development_only"
PROTOCOL_SHA256 = "b92c6cf73e05f60dc1edb3a31d88d91623e9ae0cf63d6265e6398e335928794c"
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
ENSEMBLE_SEEDS = (2026092101, 2026092102, 2026092103, 2026092104, 2026092105)
PATCH_SIZE = 16
CONTEXT_SIZE = 64
CONTEXT_BORDER = 32
GRID_SIDE = 32
PATCHES_PER_OBSERVATION = GRID_SIDE * GRID_SIDE
SAMPLED_PATCHES_PER_OBSERVATION = 256
BATCH_SIZE = 128
MAXIMUM_EPOCHS = 50
EARLY_STOPPING_PATIENCE = 5
LEARNING_RATE = 1e-3
WEIGHT_DECAY = 1e-4
PRIMARY_BAD_DETAIL_THRESHOLD = 0.05
REQUIRED_COMPACT_ARRAYS = {
    "observation_uint8",
    "fbcnn_dpir_nominal",
    "detail_patch_error",
    "target_bad_detail_0p05",
    *{
        f"{pipeline}__score__{score}"
        for pipeline in PIPELINES
        for score in HEURISTIC_SCORES
    },
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
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

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".{uuid.uuid4().hex}.partial")
    temporary.write_text(
        json.dumps(normalize(value), indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def dump_csv(path: Path, frame: pd.DataFrame) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".{uuid.uuid4().hex}.partial")
    frame.to_csv(temporary, index=False)
    temporary.replace(path)


def source_partition(source_id: str) -> str:
    if source_id in FIT_SOURCE_IDS:
        return "fit"
    if source_id in EARLY_STOP_SOURCE_IDS:
        return "early_stop"
    if source_id in CALIBRATION_SOURCE_IDS:
        return "calibration"
    raise ValueError(f"source outside frozen development partitions: {source_id}")


def expected_sources_for_shard(shard_index: int) -> tuple[str, ...]:
    assert 0 <= shard_index < 12
    start = shard_index * 8
    return DEVELOPMENT_SOURCE_IDS[start : start + 8]


def validate_frozen_protocol(protocol_text: str) -> dict:
    assert sha256_bytes(protocol_text.encode()) == PROTOCOL_SHA256, "unknown protocol bytes"
    protocol = json.loads(protocol_text)
    assert protocol["experiment_id"] == EXPERIMENT_ID
    assert protocol["independent_test_run_authorized"] is False
    assert protocol["test_results_inspected"] is False
    partitions = protocol["development_partitions"]
    assert partitions["trained_comparator_fit_sources"] == "0805-0856 inclusive (52 sources)"
    assert partitions["trained_comparator_early_stop_sources"] == "0857-0868 inclusive (12 sources)"
    assert partitions["score_calibration_sources"] == "0869-0900 inclusive (32 sources)"
    comparator = protocol["trained_image_only_comparator"]
    assert comparator["ensemble_members"] == len(ENSEMBLE_SEEDS) == 5
    assert tuple(comparator["seeds"]) == ENSEMBLE_SEEDS
    assert comparator["batch_size"] == BATCH_SIZE
    assert comparator["maximum_epochs"] == MAXIMUM_EPOCHS
    assert protocol["selection_scores"]["primary_bad_detail_event"] == (
        "centre 16x16 patch detail RMSE > 0.05"
    )
    return protocol


def _archive_root_and_index(names: list[str]) -> tuple[str, int]:
    assert names and len(names) == len(set(names))
    assert not any(
        name.startswith("/") or ".." in PurePosixPath(name).parts for name in names
    )
    roots = {name.split("/", 1)[0] for name in names}
    assert len(roots) == 1
    root = roots.pop()
    match = re.fullmatch(r"independent_05c_development_shard_(\d{2})_of_12", root)
    assert match, root
    return root, int(match.group(1))


def inspect_and_extract_shard(archive_path: Path, compact_dir: Path) -> tuple[dict, list[dict]]:
    """Verify one full manifest and extract only the compact bundles."""

    archive_path = Path(archive_path)
    compact_dir = Path(compact_dir)
    compact_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        root, shard_index = _archive_root_and_index(names)

        def read(relative: str) -> bytes:
            return archive.read(f"{root}/{relative}")

        manifest_payload = read("export_manifest.json")
        manifest = json.loads(manifest_payload)
        config = json.loads(read("config.json"))
        status = json.loads(read("status.json"))
        provenance = json.loads(read("provenance.json"))
        expected_sources = expected_sources_for_shard(shard_index)
        assert tuple(manifest["source_ids"]) == expected_sources
        assert tuple(config["source_ids"]) == expected_sources
        assert tuple(status["source_ids"]) == expected_sources
        assert tuple(config["chain_ids"]) == CHAIN_IDS
        assert tuple(status["chain_ids"]) == CHAIN_IDS
        assert manifest["role"] == config["role"] == status["role"] == provenance["role"] == ROLE
        assert manifest["test_inference_performed"] is False
        assert status["test_inference_performed"] is False
        assert status["test_performance_inspected"] is False
        assert status["independent_test_run_authorized"] is False
        assert config["test_inference_authorized"] is False

        listed = {row["path"]: row for row in manifest["files"]}
        actual = {
            name[len(root) + 1 :]
            for name in names
            if name != f"{root}/export_manifest.json" and not name.endswith("/")
        }
        assert actual == set(listed)
        assert len(listed) == 124
        compact_rows = []
        for relative, row in sorted(listed.items()):
            payload = read(relative)
            assert len(payload) == int(row["byte_count"]), relative
            assert sha256_bytes(payload) == row["sha256"], relative
            if relative.startswith("compact/") and relative.endswith(".npz"):
                observation_id = PurePosixPath(relative).stem
                destination = compact_dir / f"{observation_id}.npz"
                if destination.exists():
                    assert destination.stat().st_size == len(payload)
                    assert sha256_file(destination) == row["sha256"]
                else:
                    temporary = destination.with_suffix(".npz.partial")
                    temporary.write_bytes(payload)
                    assert sha256_file(temporary) == row["sha256"]
                    temporary.replace(destination)
                source_id, chain_id = observation_id[:4], observation_id[5:]
                assert source_id in expected_sources and chain_id in CHAIN_IDS
                compact_rows.append(
                    {
                        "observation_id": observation_id,
                        "source_id": source_id,
                        "chain_id": chain_id,
                        "partition": source_partition(source_id),
                        "compact_path": str(destination),
                        "compact_byte_count": len(payload),
                        "compact_sha256": row["sha256"],
                        "shard_index": shard_index,
                    }
                )
        assert len(compact_rows) == 56
        report = {
            "shard_index": shard_index,
            "archive_filename": archive_path.name,
            "archive_byte_count": archive_path.stat().st_size,
            "archive_sha256": sha256_file(archive_path),
            "archive_root": root,
            "export_manifest_sha256": sha256_bytes(manifest_payload),
            "manifest_files_checked": len(listed),
            "manifest_mismatches": 0,
            "compact_bundles_extracted": len(compact_rows),
            "source_ids": list(expected_sources),
            "test_inference_performed": False,
            "independent_test_run_authorized": False,
        }
        return report, compact_rows


def prepare_development_cache(archive_paths, cache_dir: Path) -> tuple[pd.DataFrame, dict]:
    archive_paths = [Path(path) for path in archive_paths]
    assert len(archive_paths) == 12, f"expected 12 shard archives, found {len(archive_paths)}"
    cache_dir = Path(cache_dir)
    compact_dir = cache_dir / "compact"
    reports, rows = [], []
    for path in sorted(archive_paths):
        report, compact_rows = inspect_and_extract_shard(path, compact_dir)
        print(
            f"Verified shard {report['shard_index']:02d}: "
            f"{report['manifest_files_checked']} files; {len(compact_rows)} bundles",
            flush=True,
        )
        reports.append(report)
        rows.extend(compact_rows)
    assert sorted(row["shard_index"] for row in reports) == list(range(12))
    frame = pd.DataFrame(rows).sort_values(["source_id", "chain_id"]).reset_index(drop=True)
    assert len(frame) == 672
    assert frame.observation_id.nunique() == 672
    assert tuple(sorted(frame.source_id.unique())) == DEVELOPMENT_SOURCE_IDS
    assert set(frame.chain_id) == set(CHAIN_IDS)
    assert frame.groupby("source_id").size().eq(7).all()
    partition_counts = frame.groupby("partition").source_id.nunique().to_dict()
    assert partition_counts == {"calibration": 32, "early_stop": 12, "fit": 52}
    dump_csv(cache_dir / "development_compact_index.csv", frame)
    report = {
        "experiment_id": EXPERIMENT_ID,
        "stage": STAGE,
        "role": ROLE,
        "archives_verified": 12,
        "manifest_files_checked": 12 * 124,
        "manifest_mismatches": 0,
        "sources": 96,
        "observations": 672,
        "partition_sources": partition_counts,
        "shards": sorted(reports, key=lambda row: row["shard_index"]),
        "test_inference_performed": False,
        "independent_test_run_authorized": False,
    }
    dump_json(cache_dir / "development_cache_receipt.json", report)
    return frame, report


def persist_input_receipts(index: pd.DataFrame, cache_report: dict, output_dir: Path) -> None:
    """Persist path-free development input receipts in the exported result bundle."""

    receipt_dir = Path(output_dir) / "input_receipts"
    portable = index.drop(columns=["compact_path"]).copy()
    dump_csv(receipt_dir / "development_compact_index.csv", portable)
    dump_json(receipt_dir / "development_cache_receipt.json", cache_report)


def load_compact(path: Path) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as stored:
        assert set(stored.files) == REQUIRED_COMPACT_ARRAYS
        arrays = {name: stored[name] for name in stored.files}
    assert arrays["observation_uint8"].shape == (576, 576, 3)
    assert arrays["observation_uint8"].dtype == np.uint8
    assert arrays["fbcnn_dpir_nominal"].shape == (576, 576, 3)
    assert arrays["fbcnn_dpir_nominal"].dtype == np.float32
    assert np.isfinite(arrays["fbcnn_dpir_nominal"]).all()
    assert 0 <= float(arrays["fbcnn_dpir_nominal"].min())
    assert float(arrays["fbcnn_dpir_nominal"].max()) <= 1
    target = arrays["target_bad_detail_0p05"]
    detail_error = arrays["detail_patch_error"]
    assert target.shape == detail_error.shape == (PATCHES_PER_OBSERVATION,)
    assert detail_error.dtype == np.float32 and np.isfinite(detail_error).all()
    assert float(detail_error.min()) >= 0
    assert target.dtype == np.uint8 and set(np.unique(target)).issubset({0, 1})
    assert np.array_equal(
        target,
        (np.sqrt(detail_error.astype(np.float64)) > PRIMARY_BAD_DETAIL_THRESHOLD).astype(np.uint8),
    )
    for pipeline in PIPELINES:
        for score in HEURISTIC_SCORES:
            values = arrays[f"{pipeline}__score__{score}"]
            assert values.shape == (PATCHES_PER_OBSERVATION,)
            assert values.dtype == np.float32 and np.isfinite(values).all()
            assert float(values.min()) >= 0
    return arrays


def _hash_u64(*parts) -> int:
    payload = "|".join(str(part) for part in parts).encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big", signed=False)


def fixed_patch_indices(
    observation_id: str,
    member_seed: int,
    count: int = 256,
    epoch: int | None = None,
) -> np.ndarray:
    assert 1 <= count <= PATCHES_PER_OBSERVATION
    ranked = sorted(
        range(PATCHES_PER_OBSERVATION),
        key=lambda index: (
            _hash_u64("patch", member_seed, epoch, observation_id, index),
            index,
        ),
    )
    return np.asarray(ranked[:count], dtype=np.int16)


def patch_context_bounds(patch_index: int) -> tuple[int, int, int, int]:
    assert 0 <= patch_index < PATCHES_PER_OBSERVATION
    row, column = divmod(int(patch_index), GRID_SIDE)
    patch_top = CONTEXT_BORDER + row * PATCH_SIZE
    patch_left = CONTEXT_BORDER + column * PATCH_SIZE
    context_top = patch_top - (CONTEXT_SIZE - PATCH_SIZE) // 2
    context_left = patch_left - (CONTEXT_SIZE - PATCH_SIZE) // 2
    return context_top, context_top + CONTEXT_SIZE, context_left, context_left + CONTEXT_SIZE


def _d4_transform(channels: np.ndarray, code: int) -> np.ndarray:
    assert channels.ndim == 3 and 0 <= code < 8
    transformed = np.rot90(channels, k=code % 4, axes=(1, 2))
    if code >= 4:
        transformed = transformed[:, :, ::-1]
    return np.ascontiguousarray(transformed)


def context_batch(
    arrays: dict[str, np.ndarray],
    patch_indices: np.ndarray,
    observation_id: str,
    member_seed: int,
    epoch: int | None,
) -> tuple[np.ndarray, np.ndarray]:
    observation = arrays["observation_uint8"].astype(np.float32) / 255.0
    reconstruction = arrays["fbcnn_dpir_nominal"].astype(np.float32, copy=False)
    inputs, targets = [], arrays["target_bad_detail_0p05"][patch_indices].astype(np.float32)
    for patch_index in patch_indices:
        top, bottom, left, right = patch_context_bounds(int(patch_index))
        six_channel = np.concatenate(
            [observation[top:bottom, left:right], reconstruction[top:bottom, left:right]],
            axis=2,
        ).transpose(2, 0, 1)
        assert six_channel.shape == (6, CONTEXT_SIZE, CONTEXT_SIZE)
        if epoch is not None:
            code = _hash_u64("d4", member_seed, epoch, observation_id, int(patch_index)) % 8
            six_channel = _d4_transform(six_channel, int(code))
        inputs.append(six_channel)
    result = np.stack(inputs).astype(np.float32, copy=False)
    assert np.isfinite(result).all() and 0 <= float(result.min()) <= float(result.max()) <= 1
    return result, targets


class PatchErrorNet(torch.nn.Module):
    """Frozen six-channel ResNet-18 scalar-logit architecture."""

    def __init__(self):
        super().__init__()
        network = torchvision.models.resnet18(weights=None)
        network.conv1 = torch.nn.Conv2d(6, 64, kernel_size=7, stride=2, padding=3, bias=False)
        network.fc = torch.nn.Linear(network.fc.in_features, 1)
        self.network = network

    def forward(self, observation_and_reconstruction):
        assert observation_and_reconstruction.ndim == 4
        assert observation_and_reconstruction.shape[1] == 6
        return self.network(observation_and_reconstruction).reshape(-1)


def configure_determinism(seed: int) -> None:
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    random.seed(seed)
    np.random.seed(seed % (2**32 - 1))
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True)


def runtime_environment(device) -> dict:
    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "torch": torch.__version__,
        "torchvision": torchvision.__version__,
        "scikit_learn": sklearn.__version__,
        "cuda_runtime": torch.version.cuda,
        "cudnn": torch.backends.cudnn.version(),
        "device_type": device.type,
        "device_name": torch.cuda.get_device_name(device) if device.type == "cuda" else "cpu",
        "cublas_workspace_config": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
        "deterministic_algorithms": True,
    }


def _atomic_torch_save(value, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".{uuid.uuid4().hex}.partial")
    torch.save(value, temporary)
    temporary.replace(path)


def training_signature(index: pd.DataFrame, member_seed: int) -> str:
    rows = index[index.partition.isin(["fit", "early_stop"])].sort_values("observation_id")
    payload = {
        "protocol_sha256": PROTOCOL_SHA256,
        "member_seed": member_seed,
        "observation_ids": rows.observation_id.tolist(),
        "compact_sha256": rows.compact_sha256.tolist(),
        "batch_size": BATCH_SIZE,
        "maximum_epochs": MAXIMUM_EPOCHS,
        "patience": EARLY_STOPPING_PATIENCE,
        "learning_rate": LEARNING_RATE,
        "weight_decay": WEIGHT_DECAY,
        "sampled_patches_per_observation": SAMPLED_PATCHES_PER_OBSERVATION,
    }
    return sha256_bytes(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())


def fit_positive_weight(index: pd.DataFrame) -> tuple[float, dict]:
    fit_rows = index[index.partition == "fit"]
    positives = 0
    total = 0
    for row in fit_rows.itertuples(index=False):
        arrays = load_compact(Path(row.compact_path))
        target = arrays["target_bad_detail_0p05"]
        positives += int(target.sum())
        total += int(target.size)
    negatives = total - positives
    assert positives > 0 and negatives > 0
    return negatives / positives, {
        "fit_patches": total,
        "fit_positive_patches": positives,
        "fit_negative_patches": negatives,
        "positive_weight": negatives / positives,
    }


def evaluate_member(model, index: pd.DataFrame, member_seed: int, device) -> tuple[float, dict]:
    model.eval()
    by_source = defaultdict(lambda: [0.0, 0])
    validation_rows = index[index.partition == "early_stop"].sort_values("observation_id")
    with torch.inference_mode():
        for row in validation_rows.itertuples(index=False):
            arrays = load_compact(Path(row.compact_path))
            selected = fixed_patch_indices(row.observation_id, member_seed)
            for start in range(0, len(selected), BATCH_SIZE):
                batch_indices = selected[start : start + BATCH_SIZE]
                inputs, targets = context_batch(
                    arrays, batch_indices, row.observation_id, member_seed, epoch=None
                )
                logits = model(torch.from_numpy(inputs).to(device))
                probabilities = torch.sigmoid(logits).cpu().numpy()
                errors = (probabilities - targets) ** 2
                by_source[row.source_id][0] += float(errors.sum())
                by_source[row.source_id][1] += int(len(errors))
    assert tuple(sorted(by_source)) == EARLY_STOP_SOURCE_IDS
    source_brier = {source: total / count for source, (total, count) in by_source.items()}
    macro = float(np.mean(list(source_brier.values())))
    return macro, source_brier


def _load_history(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return pd.read_csv(path).to_dict(orient="records")


def train_member(
    index: pd.DataFrame,
    member_index: int,
    member_seed: int,
    work_dir: Path,
    final_dir: Path,
    device,
    positive_weight: float,
    class_receipt: dict,
) -> dict:
    configure_determinism(member_seed)
    current_environment = runtime_environment(device)
    environment_history = [current_environment]
    signature = training_signature(index, member_seed)
    work_dir, final_dir = Path(work_dir), Path(final_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    final_dir.mkdir(parents=True, exist_ok=True)
    latest_path = work_dir / f"member_{member_index:02d}_latest.pt"
    best_path = final_dir / f"member_{member_index:02d}_best.pt"
    history_path = final_dir / f"member_{member_index:02d}_history.csv"
    receipt_path = final_dir / f"member_{member_index:02d}_receipt.json"

    if receipt_path.exists() and best_path.exists():
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        assert receipt["training_signature"] == signature
        assert receipt["model_sha256"] == sha256_file(best_path)
        print(f"Member {member_index + 1}/5 already complete; verified and reused.")
        return receipt

    model = PatchErrorNet().to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY
    )
    criterion = torch.nn.BCEWithLogitsLoss(
        pos_weight=torch.tensor([positive_weight], dtype=torch.float32, device=device)
    )
    history = _load_history(history_path)
    start_epoch = 0
    best_epoch = -1
    best_brier = float("inf")
    epochs_without_improvement = 0
    if latest_path.exists():
        checkpoint = torch.load(latest_path, map_location=device, weights_only=False)
        assert checkpoint["training_signature"] == signature
        model.load_state_dict(checkpoint["model_state"])
        optimizer.load_state_dict(checkpoint["optimizer_state"])
        start_epoch = int(checkpoint["epoch"]) + 1
        best_epoch = int(checkpoint["best_epoch"])
        best_brier = float(checkpoint["best_brier"])
        epochs_without_improvement = int(checkpoint["epochs_without_improvement"])
        history = checkpoint["history"]
        environment_history = checkpoint.get("environment_history", [])
        if not environment_history or environment_history[-1] != current_environment:
            environment_history.append(current_environment)
        dump_csv(history_path, pd.DataFrame(history))
        print(f"Resuming member {member_index + 1}/5 at epoch {start_epoch + 1}.")

    fit_rows = index[index.partition == "fit"].sort_values("observation_id").reset_index(drop=True)
    assert fit_rows.source_id.nunique() == 52
    for epoch in range(start_epoch, MAXIMUM_EPOCHS):
        model.train()
        order = np.random.default_rng(member_seed + epoch).permutation(len(fit_rows))
        total_loss = 0.0
        total_examples = 0
        for row_index in order:
            row = fit_rows.iloc[int(row_index)]
            arrays = load_compact(Path(row.compact_path))
            selected = fixed_patch_indices(row.observation_id, member_seed, epoch=epoch)
            selected = selected[
                np.random.default_rng(_hash_u64("order", member_seed, epoch, row.observation_id)).permutation(
                    len(selected)
                )
            ]
            for start in range(0, len(selected), BATCH_SIZE):
                batch_indices = selected[start : start + BATCH_SIZE]
                inputs, targets = context_batch(
                    arrays, batch_indices, row.observation_id, member_seed, epoch=epoch
                )
                input_tensor = torch.from_numpy(inputs).to(device)
                target_tensor = torch.from_numpy(targets).to(device)
                optimizer.zero_grad(set_to_none=True)
                logits = model(input_tensor)
                loss = criterion(logits, target_tensor)
                loss.backward()
                optimizer.step()
                total_loss += float(loss.detach().cpu()) * len(targets)
                total_examples += len(targets)

        validation_brier, _ = evaluate_member(model, index, member_seed, device)
        fit_loss = total_loss / total_examples
        improved = validation_brier < best_brier
        if improved:
            best_brier = validation_brier
            best_epoch = epoch
            epochs_without_improvement = 0
            _atomic_torch_save(
                {
                    "experiment_id": EXPERIMENT_ID,
                    "stage": STAGE,
                    "role": ROLE,
                    "member_index": member_index,
                    "member_seed": member_seed,
                    "epoch": epoch,
                    "validation_source_macro_brier": validation_brier,
                    "training_signature": signature,
                    "environment_history": environment_history,
                    "model_state": {key: value.detach().cpu() for key, value in model.state_dict().items()},
                    "test_inference_performed": False,
                    "independent_test_run_authorized": False,
                },
                best_path,
            )
        else:
            epochs_without_improvement += 1

        history.append(
            {
                "member_index": member_index,
                "member_seed": member_seed,
                "epoch": epoch + 1,
                "fit_weighted_bce": fit_loss,
                "early_stop_source_macro_brier": validation_brier,
                "best_so_far": improved,
            }
        )
        _atomic_torch_save(
            {
                "training_signature": signature,
                "epoch": epoch,
                "best_epoch": best_epoch,
                "best_brier": best_brier,
                "epochs_without_improvement": epochs_without_improvement,
                "history": history,
                "environment_history": environment_history,
                "model_state": model.state_dict(),
                "optimizer_state": optimizer.state_dict(),
            },
            latest_path,
        )
        dump_csv(history_path, pd.DataFrame(history))
        print(
            f"Member {member_index + 1}/5 epoch {epoch + 1:02d}: "
            f"fit BCE={fit_loss:.6f}; early-stop source-macro Brier={validation_brier:.6f}",
            flush=True,
        )
        if epochs_without_improvement >= EARLY_STOPPING_PATIENCE:
            break

    assert best_path.exists() and best_epoch >= 0
    receipt = {
        "experiment_id": EXPERIMENT_ID,
        "stage": STAGE,
        "role": ROLE,
        "member_index": member_index,
        "member_seed": member_seed,
        "training_signature": signature,
        "epochs_completed": len(history),
        "best_epoch": best_epoch + 1,
        "best_early_stop_source_macro_brier": best_brier,
        "model_path": best_path.name,
        "model_byte_count": best_path.stat().st_size,
        "model_sha256": sha256_file(best_path),
        "fit_sources": list(FIT_SOURCE_IDS),
        "early_stop_sources": list(EARLY_STOP_SOURCE_IDS),
        "calibration_sources_used": False,
        "class_balance": class_receipt,
        "environment_history": environment_history,
        "test_inference_performed": False,
        "independent_test_run_authorized": False,
    }
    dump_json(receipt_path, receipt)
    return receipt


def fit_ensemble(
    index: pd.DataFrame,
    output_dir: Path,
    device=None,
    member_indices: tuple[int, ...] | list[int] | None = None,
) -> dict:
    output_dir = Path(output_dir)
    work_dir = output_dir / "work_checkpoints"
    model_dir = output_dir / "models"
    device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    assert device.type == "cuda", "PatchErrorNet fitting requires a CUDA GPU"
    member_indices = tuple(range(5)) if member_indices is None else tuple(member_indices)
    assert member_indices and len(member_indices) == len(set(member_indices))
    assert all(0 <= member_index < 5 for member_index in member_indices)
    positive_weight, class_receipt = fit_positive_weight(index)
    for member_index in member_indices:
        member_seed = ENSEMBLE_SEEDS[member_index]
        train_member(
            index,
            member_index,
            member_seed,
            work_dir,
            model_dir,
            device,
            positive_weight,
            class_receipt,
        )

    receipts = []
    for member_index in range(5):
        receipt_path = model_dir / f"member_{member_index:02d}_receipt.json"
        if receipt_path.exists():
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            best_path = model_dir / f"member_{member_index:02d}_best.pt"
            assert receipt["member_seed"] == ENSEMBLE_SEEDS[member_index]
            assert receipt["model_sha256"] == sha256_file(best_path)
            receipts.append(receipt)
    if len(receipts) < 5:
        completed = sorted(int(row["member_index"]) for row in receipts)
        return {
            "experiment_id": EXPERIMENT_ID,
            "stage": STAGE,
            "role": ROLE,
            "ensemble_complete": False,
            "completed_member_indices": completed,
            "pending_member_indices": sorted(set(range(5)) - set(completed)),
            "test_inference_performed": False,
            "independent_test_run_authorized": False,
        }
    assert len(receipts) == 5
    assert all(row["calibration_sources_used"] is False for row in receipts)
    summary = {
        "experiment_id": EXPERIMENT_ID,
        "stage": STAGE,
        "role": ROLE,
        "architecture": "ResNet-18 from scratch; six input channels; one scalar logit",
        "ensemble_members": 5,
        "member_seeds": list(ENSEMBLE_SEEDS),
        "fit_source_count": 52,
        "early_stop_source_count": 12,
        "members": receipts,
        "ensemble_complete": True,
        "comparator_fitted": True,
        "calibration_fitted": False,
        "test_inference_performed": False,
        "independent_test_run_authorized": False,
    }
    dump_json(output_dir / "ensemble_training_receipt.json", summary)
    return summary


def load_frozen_ensemble(output_dir: Path, device) -> list:
    models = []
    for member_index, member_seed in enumerate(ENSEMBLE_SEEDS):
        path = Path(output_dir) / "models" / f"member_{member_index:02d}_best.pt"
        checkpoint = torch.load(path, map_location=device, weights_only=False)
        assert checkpoint["member_seed"] == member_seed
        assert checkpoint["test_inference_performed"] is False
        model = PatchErrorNet().to(device)
        model.load_state_dict(checkpoint["model_state"], strict=True)
        model.eval()
        models.append(model)
    return models


def ensemble_probabilities(arrays: dict[str, np.ndarray], observation_id: str, models, device):
    per_member = []
    all_indices = np.arange(PATCHES_PER_OBSERVATION, dtype=np.int16)
    with torch.inference_mode():
        for model in models:
            member_values = []
            for start in range(0, PATCHES_PER_OBSERVATION, BATCH_SIZE):
                batch_indices = all_indices[start : start + BATCH_SIZE]
                inputs, _ = context_batch(
                    arrays, batch_indices, observation_id, member_seed=0, epoch=None
                )
                probabilities = torch.sigmoid(model(torch.from_numpy(inputs).to(device)))
                member_values.append(probabilities.cpu().numpy().astype(np.float32))
            per_member.append(np.concatenate(member_values))
    matrix = np.stack(per_member)
    assert matrix.shape == (5, PATCHES_PER_OBSERVATION)
    return matrix.mean(axis=0).astype(np.float32), matrix.var(axis=0).astype(np.float32)


def _save_npz_atomic(path: Path, arrays: dict[str, np.ndarray]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".{uuid.uuid4().hex}.partial")
    with temporary.open("wb") as stream:
        np.savez_compressed(stream, **arrays)
    temporary.replace(path)


def collect_calibration_predictions(index: pd.DataFrame, output_dir: Path, device=None) -> dict:
    output_dir = Path(output_dir)
    prediction_path = output_dir / "calibration_predictions.npz"
    receipt_path = output_dir / "calibration_prediction_receipt.json"
    if prediction_path.exists() and receipt_path.exists():
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        assert receipt["sha256"] == sha256_file(prediction_path)
        return receipt

    device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    assert device.type == "cuda", "ensemble calibration inference requires a CUDA GPU"
    models = load_frozen_ensemble(output_dir, device)
    calibration_rows = index[index.partition == "calibration"].sort_values("observation_id")
    assert calibration_rows.source_id.nunique() == 32 and len(calibration_rows) == 224
    collected = defaultdict(list)
    for observation_number, row in enumerate(calibration_rows.itertuples(index=False), start=1):
        arrays = load_compact(Path(row.compact_path))
        mean_probability, probability_variance = ensemble_probabilities(
            arrays, row.observation_id, models, device
        )
        collected["source_id"].append(
            np.full(PATCHES_PER_OBSERVATION, int(row.source_id), dtype=np.int16)
        )
        collected["chain_index"].append(
            np.full(PATCHES_PER_OBSERVATION, CHAIN_IDS.index(row.chain_id), dtype=np.uint8)
        )
        collected["patch_index"].append(
            np.arange(PATCHES_PER_OBSERVATION, dtype=np.int16)
        )
        collected["target_bad_detail_0p05"].append(
            arrays["target_bad_detail_0p05"].astype(np.uint8)
        )
        for pipeline in PIPELINES:
            for score in HEURISTIC_SCORES:
                key = f"{pipeline}__score__{score}"
                collected[key].append(arrays[key].astype(np.float32))
        collected[ENSEMBLE_SCORE].append(mean_probability)
        collected[ENSEMBLE_VARIANCE].append(probability_variance)
        print(
            f"Calibration inference [{observation_number}/224] {row.observation_id}",
            flush=True,
        )
    arrays = {key: np.concatenate(values) for key, values in collected.items()}
    expected = 32 * 7 * PATCHES_PER_OBSERVATION
    assert {len(value) for value in arrays.values()} == {expected}
    _save_npz_atomic(prediction_path, arrays)
    receipt = {
        "experiment_id": EXPERIMENT_ID,
        "stage": STAGE,
        "role": ROLE,
        "path": prediction_path.name,
        "byte_count": prediction_path.stat().st_size,
        "sha256": sha256_file(prediction_path),
        "sources": 32,
        "observations": 224,
        "patch_rows": expected,
        "operational_scores": 11,
        "ensemble_members": 5,
        "test_inference_performed": False,
        "independent_test_run_authorized": False,
    }
    dump_json(receipt_path, receipt)
    return receipt


def _source_equal_weights(source_ids: np.ndarray) -> np.ndarray:
    unique, counts = np.unique(source_ids, return_counts=True)
    count_map = dict(zip(unique.tolist(), counts.tolist()))
    weights = np.asarray([1.0 / count_map[int(source)] for source in source_ids], dtype=np.float64)
    for source in unique:
        assert math.isclose(float(weights[source_ids == source].sum()), 1.0, abs_tol=1e-12)
    return weights


def source_macro_brier(probability, target, source_ids) -> float:
    rows = []
    for source in np.unique(source_ids):
        selected = source_ids == source
        rows.append(float(np.mean((probability[selected] - target[selected]) ** 2)))
    return float(np.mean(rows))


def equal_mass_ece(probability, target, weights, bins: int = 10) -> float:
    order = np.argsort(probability, kind="mergesort")
    p, y, w = probability[order], target[order], weights[order]
    cumulative = np.cumsum(w) - 0.5 * w
    assignments = np.minimum((cumulative / w.sum() * bins).astype(int), bins - 1)
    result = 0.0
    for bin_index in range(bins):
        selected = assignments == bin_index
        if not selected.any():
            continue
        mass = float(w[selected].sum())
        confidence = float(np.average(p[selected], weights=w[selected]))
        frequency = float(np.average(y[selected], weights=w[selected]))
        result += mass / float(w.sum()) * abs(confidence - frequency)
    return result


def apply_isotonic_mapping(values: np.ndarray, mapping: dict) -> np.ndarray:
    thresholds = np.asarray(mapping["x_thresholds"], dtype=np.float64)
    outputs = np.asarray(mapping["y_thresholds"], dtype=np.float64)
    oriented = np.asarray(values, dtype=np.float64) * float(mapping["orientation"])
    return np.interp(oriented, thresholds, outputs, left=outputs[0], right=outputs[-1])


def fit_calibration_mappings(output_dir: Path) -> dict:
    output_dir = Path(output_dir)
    prediction_path = output_dir / "calibration_predictions.npz"
    with np.load(prediction_path, allow_pickle=False) as stored:
        arrays = {key: stored[key] for key in stored.files}
    source_ids = arrays["source_id"].astype(np.int16)
    target = arrays["target_bad_detail_0p05"].astype(np.float64)
    assert tuple(f"{value:04d}" for value in sorted(np.unique(source_ids))) == CALIBRATION_SOURCE_IDS
    weights = _source_equal_weights(source_ids)
    score_keys = [
        f"{pipeline}__score__{score}"
        for pipeline in PIPELINES
        for score in HEURISTIC_SCORES
    ] + [ENSEMBLE_SCORE]
    mappings, diagnostics = {}, []
    for score_key in score_keys:
        values = arrays[score_key].astype(np.float64)
        assert np.isfinite(values).all()
        orientation = 1.0
        oriented = values * orientation
        estimator = IsotonicRegression(
            increasing=True, out_of_bounds="clip", y_min=0.0, y_max=1.0
        )
        estimator.fit(oriented, target, sample_weight=weights)
        mapping = {
            "score": score_key,
            "orientation": orientation,
            "orientation_rule": "Frozen score semantics: larger values indicate greater risk.",
            "x_thresholds": estimator.X_thresholds_.astype(float).tolist(),
            "y_thresholds": estimator.y_thresholds_.astype(float).tolist(),
            "out_of_bounds": "clip",
        }
        calibrated = apply_isotonic_mapping(values, mapping)
        assert np.isfinite(calibrated).all()
        assert 0 <= float(calibrated.min()) <= float(calibrated.max()) <= 1
        mappings[score_key] = mapping
        diagnostics.append(
            {
                "score": score_key,
                "calibration_sources": 32,
                "calibration_patch_rows": len(target),
                "mapping_knots": len(mapping["x_thresholds"]),
                "source_macro_brier_in_sample": source_macro_brier(
                    calibrated, target, source_ids
                ),
                "equal_mass_ece_10bin_in_sample": equal_mass_ece(
                    calibrated, target, weights, bins=10
                ),
                "calibration_in_the_large_in_sample": float(
                    np.average(target - calibrated, weights=weights)
                ),
            }
        )
    artifact = {
        "schema_version": "1.0.0",
        "experiment_id": EXPERIMENT_ID,
        "stage": STAGE,
        "role": ROLE,
        "protocol_sha256": PROTOCOL_SHA256,
        "method": "isotonic_regression",
        "fit_partition": "DIV2K 0869-0900 only",
        "weighting": "Each calibration source has equal total weight.",
        "target": "centre 16x16 patch detail RMSE > 0.05",
        "mappings": mappings,
        "claim_boundary": (
            "These are development-fitted mappings, not independent calibration results "
            "and not posterior-probability claims."
        ),
        "test_inference_performed": False,
        "independent_test_run_authorized": False,
    }
    dump_json(output_dir / "calibration_mappings.json", artifact)
    pd.DataFrame(diagnostics).to_csv(output_dir / "calibration_fit_diagnostics.csv", index=False)
    receipt = {
        "experiment_id": EXPERIMENT_ID,
        "stage": STAGE,
        "role": ROLE,
        "calibration_fitted": True,
        "mapping_count": len(mappings),
        "calibration_source_count": 32,
        "calibration_patch_rows": len(target),
        "mappings_sha256": sha256_file(output_dir / "calibration_mappings.json"),
        "diagnostics_sha256": sha256_file(output_dir / "calibration_fit_diagnostics.csv"),
        "test_inference_performed": False,
        "independent_test_run_authorized": False,
    }
    dump_json(output_dir / "calibration_receipt.json", receipt)
    return receipt


def build_diagnostic_figures(output_dir: Path) -> list[str]:
    import matplotlib.pyplot as plt

    output_dir = Path(output_dir)
    figure_dir = output_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    histories = []
    for member_index in range(5):
        history = pd.read_csv(output_dir / "models" / f"member_{member_index:02d}_history.csv")
        histories.append(history)
    history = pd.concat(histories, ignore_index=True)
    plt.figure(figsize=(8.5, 5.0))
    colors = ["#1f4e79", "#c58b16", "#d55e00", "#6b7d2a", "#b23a6f"]
    for member_index, color in enumerate(colors):
        rows = history[history.member_index == member_index]
        plt.plot(
            rows.epoch,
            rows.early_stop_source_macro_brier,
            marker="o",
            markersize=3,
            linewidth=1.5,
            color=color,
            label=f"Member {member_index + 1}",
        )
    plt.xlabel("Epoch")
    plt.ylabel("Source-macro Brier score")
    plt.title("PatchErrorNet early-stop performance (DIV2K 0857–0868)")
    plt.grid(axis="y", color="#dddddd", linewidth=0.8)
    plt.legend(ncol=3, frameon=False)
    plt.tight_layout()
    history_path = figure_dir / "patcherrornet_early_stop_history.png"
    plt.savefig(history_path, dpi=180)
    plt.close()

    with np.load(output_dir / "calibration_predictions.npz", allow_pickle=False) as stored:
        arrays = {key: stored[key] for key in stored.files}
    mappings = json.loads((output_dir / "calibration_mappings.json").read_text())["mappings"]
    target = arrays["target_bad_detail_0p05"].astype(float)
    weights = _source_equal_weights(arrays["source_id"])
    score_keys = list(mappings)
    fig, axes = plt.subplots(3, 4, figsize=(13, 9), sharex=True, sharey=True)
    axes = axes.ravel()
    for axis, score_key in zip(axes, score_keys):
        probability = apply_isotonic_mapping(arrays[score_key], mappings[score_key])
        order = np.argsort(probability, kind="mergesort")
        p, y, w = probability[order], target[order], weights[order]
        cumulative = np.cumsum(w) - 0.5 * w
        assignments = np.minimum((cumulative / w.sum() * 10).astype(int), 9)
        xs, ys = [], []
        for bin_index in range(10):
            selected = assignments == bin_index
            if selected.any():
                xs.append(float(np.average(p[selected], weights=w[selected])))
                ys.append(float(np.average(y[selected], weights=w[selected])))
        axis.plot([0, 1], [0, 1], color="#444444", linestyle="--", linewidth=1)
        axis.plot(xs, ys, marker="o", color="#1f4e79", linewidth=1.5)
        axis.set_title(score_key.replace("__score__", " · ").replace("_", " "), fontsize=8)
        axis.grid(color="#e5e5e5", linewidth=0.6)
    for axis in axes[len(score_keys) :]:
        axis.axis("off")
    fig.supxlabel("Mapped probability")
    fig.supylabel("Observed bad-detail rate")
    fig.suptitle("Development calibration fit diagnostics (DIV2K 0869–0900)")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    calibration_path = figure_dir / "development_calibration_reliability.png"
    fig.savefig(calibration_path, dpi=180)
    plt.close(fig)
    return [str(history_path), str(calibration_path)]


def finalize_development_bundle(output_dir: Path) -> dict:
    output_dir = Path(output_dir)
    ensemble = json.loads((output_dir / "ensemble_training_receipt.json").read_text())
    calibration = json.loads((output_dir / "calibration_receipt.json").read_text())
    assert ensemble["ensemble_members"] == 5 and ensemble["comparator_fitted"] is True
    assert calibration["mapping_count"] == 11 and calibration["calibration_fitted"] is True
    status = {
        "experiment_id": EXPERIMENT_ID,
        "stage": STAGE,
        "role": ROLE,
        "status": "passed_development_reliability_fit",
        "comparator_fitted": True,
        "ensemble_members": 5,
        "calibration_fitted": True,
        "calibration_mappings": 11,
        "fit_sources": 52,
        "early_stop_sources": 12,
        "calibration_sources": 32,
        "test_inference_performed": False,
        "test_performance_inspected": False,
        "independent_test_run_authorized": False,
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(output_dir / "status.json", status)
    checks = {
        "protocol_sha256": PROTOCOL_SHA256,
        "ensemble_members": 5,
        "member_model_files": 5,
        "member_history_files": 5,
        "calibration_mapping_count": 11,
        "partitions_disjoint": not (
            set(FIT_SOURCE_IDS) & set(EARLY_STOP_SOURCE_IDS)
            or set(FIT_SOURCE_IDS) & set(CALIBRATION_SOURCE_IDS)
            or set(EARLY_STOP_SOURCE_IDS) & set(CALIBRATION_SOURCE_IDS)
        ),
        "development_source_union": len(
            set(FIT_SOURCE_IDS) | set(EARLY_STOP_SOURCE_IDS) | set(CALIBRATION_SOURCE_IDS)
        ),
        "test_loader_present": False,
        "test_inference_performed": False,
        "independent_test_run_authorized": False,
    }
    assert checks["partitions_disjoint"] is True
    assert checks["development_source_union"] == 96
    dump_json(output_dir / "checks.json", checks)

    excluded = {"export_manifest.json"}
    manifest = []
    for path in sorted(output_dir.rglob("*")):
        if (
            not path.is_file()
            or path.name in excluded
            or ".partial" in path.name
            or "work_checkpoints" in path.parts
        ):
            continue
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
            "experiment_id": EXPERIMENT_ID,
            "stage": STAGE,
            "role": ROLE,
            "test_inference_performed": False,
            "independent_test_run_authorized": False,
            "files": manifest,
        },
    )
    for row in manifest:
        path = output_dir / row["path"]
        assert path.stat().st_size == row["byte_count"]
        assert sha256_file(path) == row["sha256"]
    archive_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    archive_path = output_dir.parent / f"{output_dir.name}_{archive_stamp}.zip"
    temporary_archive = archive_path.with_suffix(f".{uuid.uuid4().hex}.partial")
    with zipfile.ZipFile(
        temporary_archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
    ) as archive:
        for row in manifest:
            archive.write(output_dir / row["path"], arcname=row["path"])
        archive.write(output_dir / "export_manifest.json", arcname="export_manifest.json")
    temporary_archive.replace(archive_path)
    return {
        "status": status["status"],
        "output_dir": str(output_dir),
        "archive_path": str(archive_path),
        "archive_byte_count": archive_path.stat().st_size,
        "archive_sha256": sha256_file(archive_path),
        "manifest_files": len(manifest),
        "test_inference_performed": False,
        "independent_test_run_authorized": False,
    }


def static_self_check() -> dict:
    assert len(DEVELOPMENT_SOURCE_IDS) == 96
    assert len(FIT_SOURCE_IDS) == 52
    assert len(EARLY_STOP_SOURCE_IDS) == 12
    assert len(CALIBRATION_SOURCE_IDS) == 32
    assert not set(FIT_SOURCE_IDS) & set(EARLY_STOP_SOURCE_IDS)
    assert not set(FIT_SOURCE_IDS) & set(CALIBRATION_SOURCE_IDS)
    assert not set(EARLY_STOP_SOURCE_IDS) & set(CALIBRATION_SOURCE_IDS)
    assert expected_sources_for_shard(0) == tuple(f"{value:04d}" for value in range(805, 813))
    assert expected_sources_for_shard(11) == tuple(f"{value:04d}" for value in range(893, 901))
    assert patch_context_bounds(0) == (8, 72, 8, 72)
    assert patch_context_bounds(1023) == (504, 568, 504, 568)
    selected = fixed_patch_indices("0805_j75_b16_n2", ENSEMBLE_SEEDS[0], epoch=0)
    assert selected.shape == (256,) and len(np.unique(selected)) == 256
    assert not np.array_equal(
        selected,
        fixed_patch_indices("0805_j75_b16_n2", ENSEMBLE_SEEDS[0], epoch=1),
    )
    return {
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
