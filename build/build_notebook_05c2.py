#!/usr/bin/env python3
"""Build the self-contained development reliability fitting notebook."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION = ROOT / "experiments" / "independent_05" / "reliability_training.py"
PROTOCOL = ROOT / "experiments" / "independent_05" / "protocol_freeze.json"
REGISTRY = ROOT / "experiments" / "independent_05" / "development_shard_registry.json"
STAGE_STATUS = ROOT / "experiments" / "independent_05" / "stage_05c_status.json"
OUTPUT = ROOT / "notebooks" / "05C2_Development_Reliability_Training_and_Calibration.ipynb"


def code(source: str, *, hidden: bool = False):
    metadata = {}
    if hidden:
        metadata = {
            "cellView": "form",
            "jupyter": {"source_hidden": True},
            "tags": ["hide-input"],
        }
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": metadata,
        "outputs": [],
        "source": (source.strip() + "\n").splitlines(keepends=True),
    }


def markdown(source: str):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": (source.strip() + "\n").splitlines(keepends=True),
    }


def main() -> None:
    implementation_source = IMPLEMENTATION.read_text(encoding="utf-8")
    protocol_text = PROTOCOL.read_text(encoding="utf-8")
    registry_text = REGISTRY.read_text(encoding="utf-8")
    stage_status_text = STAGE_STATUS.read_text(encoding="utf-8")
    digests = {
        "implementation": hashlib.sha256(implementation_source.encode()).hexdigest(),
        "protocol": hashlib.sha256(protocol_text.encode()).hexdigest(),
        "registry": hashlib.sha256(registry_text.encode()).hexdigest(),
        "stage_status": hashlib.sha256(stage_status_text.encode()).hexdigest(),
    }

    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3"},
            "colab": {"name": OUTPUT.name, "provenance": [], "gpuType": "L4"},
            "accelerator": "GPU",
            "experiment": {
                "id": "independent_05",
                "stage": "05C2_development_reliability_training_and_calibration",
                "role": "development_only",
                "ensemble_members": 5,
                "calibration_mappings": 11,
                "test_inference_authorized": False,
            },
        },
        "cells": [
            markdown(
                """
# 05C2 · Development reliability training and calibration

**Verified DIV2K shards only · five-member PatchErrorNet · frozen isotonic mappings**

This notebook consumes all 12 audited Stage 05C1 shard ZIPs. It trains the frozen
six-channel ResNet-18 ensemble using only sources 0805–0856, early-stops using only
0857–0868, and fits all operational-score mappings using only 0869–0900.

The independent TESTIMAGES cohort is never loaded. This notebook cannot authorize or
perform the independent run. The long implementation is embedded and collapsed for a
clean Colab view while remaining fully auditable.
"""
            ),
            markdown(
                """
### 1. Set up the GPU runtime and Drive

Use a Colab GPU runtime. The result folder is resumable: completed ensemble members are
hash-checked and reused after an interruption.
"""
            ),
            code(
                """
import os
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'

import hashlib
import json
import types
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torchvision
import sklearn
from IPython.display import Image as DisplayImage, display

try:
    import google.colab
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

if IN_COLAB:
    from google.colab import drive
    drive.mount('/content/drive')
    PROJECT_DIR = Path('/content/drive/MyDrive/reliable-reconstruction-under-mismatch')
    CACHE_DIR = Path('/content/independent_05c2_development_cache')
else:
    PROJECT_DIR = Path.cwd()
    if PROJECT_DIR.name == 'notebooks':
        PROJECT_DIR = PROJECT_DIR.parent
    CACHE_DIR = PROJECT_DIR / 'results' / '.independent_05c2_development_cache'

assert torch.cuda.is_available(), 'Select Runtime > Change runtime type > GPU.'
OUTPUT_DIR = PROJECT_DIR / 'results' / 'independent_05c2_development_reliability'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
print('GPU:', torch.cuda.get_device_name(0))
print('Resumable destination:', OUTPUT_DIR)
"""
            ),
            markdown(
                """
### 2. Verify and load the frozen implementation

The implementation, protocol, completed-shard registry, and current stage status are
embedded byte-for-byte. Their SHA-256 digests and the development-only barriers are
checked before any fitting begins.
"""
            ),
            code(
                f"""
#@title 🔒 Embedded Stage 05C2 implementation and receipts (expand only for audit) {{ display-mode: "form" }}
IMPLEMENTATION_SOURCE = {implementation_source!r}
PROTOCOL_TEXT = {protocol_text!r}
REGISTRY_TEXT = {registry_text!r}
STAGE_STATUS_TEXT = {stage_status_text!r}
EXPECTED_DIGESTS = {digests!r}

assert hashlib.sha256(IMPLEMENTATION_SOURCE.encode()).hexdigest() == EXPECTED_DIGESTS['implementation']
assert hashlib.sha256(PROTOCOL_TEXT.encode()).hexdigest() == EXPECTED_DIGESTS['protocol']
assert hashlib.sha256(REGISTRY_TEXT.encode()).hexdigest() == EXPECTED_DIGESTS['registry']
assert hashlib.sha256(STAGE_STATUS_TEXT.encode()).hexdigest() == EXPECTED_DIGESTS['stage_status']

REGISTRY_05C = json.loads(REGISTRY_TEXT)
STAGE_STATUS_05C = json.loads(STAGE_STATUS_TEXT)
assert REGISTRY_05C['verified_shards'] == 12
assert REGISTRY_05C['next_expected_shard_index'] is None
assert REGISTRY_05C['independent_test_run_authorized'] is False
assert STAGE_STATUS_05C['development_generation_complete'] is True
assert STAGE_STATUS_05C['development_generation_shards_completed'] == 12
assert STAGE_STATUS_05C['comparator_fitted'] is False
assert STAGE_STATUS_05C['calibration_fitted'] is False
assert STAGE_STATUS_05C['independent_test_run_authorized'] is False
assert STAGE_STATUS_05C['test_inference_performed'] is False

RT05 = types.ModuleType('independent_05_reliability_training_embedded')
exec(compile(IMPLEMENTATION_SOURCE, '<independent_05_reliability_training_embedded>', 'exec'), RT05.__dict__)
RT05.validate_frozen_protocol(PROTOCOL_TEXT)
print(json.dumps(RT05.static_self_check(), indent=2))
""",
                hidden=True,
            ),
            markdown(
                """
### 3. Locate and independently verify all 12 shard archives

The default archive folder is the `results` folder used by Notebook 05C1. Every one of
the 1,488 manifest-listed files is byte-counted and SHA-256 checked. Only the 672 compact
development bundles are extracted into the runtime cache.
"""
            ),
            code(
                """
SHARD_ARCHIVE_DIR_TEXT = ''  #@param {type:"string"}
SHARD_ARCHIVE_DIR = (
    Path(SHARD_ARCHIVE_DIR_TEXT) if SHARD_ARCHIVE_DIR_TEXT.strip()
    else PROJECT_DIR / 'results'
)
archive_candidates = sorted(
    SHARD_ARCHIVE_DIR.glob('independent_05c_development_shard_*_of_12*.zip')
)
assert archive_candidates, f'No Stage 05C1 shard ZIPs found in {SHARD_ARCHIVE_DIR}'

by_index = {}
for path in archive_candidates:
    shard_index = RT05.archive_shard_index(path)
    by_index.setdefault(shard_index, []).append(path)

duplicates = {index: paths for index, paths in by_index.items() if len(paths) != 1}
assert not duplicates, (
    'Expected exactly one ZIP per shard index. Move duplicate reruns out of the selected '
    f'folder and rerun this cell: {duplicates}'
)
assert sorted(by_index) == list(range(12)), f'Missing shard indices: {sorted(set(range(12)) - set(by_index))}'
SHARD_ARCHIVES = [by_index[index][0] for index in range(12)]

DEVELOPMENT_INDEX, CACHE_RECEIPT = RT05.prepare_development_cache(
    SHARD_ARCHIVES, CACHE_DIR
)
RT05.persist_input_receipts(DEVELOPMENT_INDEX, CACHE_RECEIPT, OUTPUT_DIR)
print(json.dumps({
    'archives_verified': CACHE_RECEIPT['archives_verified'],
    'manifest_files_checked': CACHE_RECEIPT['manifest_files_checked'],
    'sources': CACHE_RECEIPT['sources'],
    'observations': CACHE_RECEIPT['observations'],
    'partition_sources': CACHE_RECEIPT['partition_sources'],
}, indent=2))
"""
            ),
            markdown(
                """
### 4. Train or resume the five-member PatchErrorNet ensemble

Default: train members `0,1,2,3,4` sequentially in this runtime.

For parallel Colabs, duplicate this notebook and give each runtime disjoint member indices
(for example `0,1`, `2,3`, and `4`). They may share the same Drive result folder because
member filenames do not overlap. Once all five finish, rerun this cell in any one runtime;
completed members are verified and reused.
"""
            ),
            code(
                """
MEMBER_INDICES_TEXT = '0,1,2,3,4'  #@param {type:"string"}
MEMBER_INDICES = tuple(int(value.strip()) for value in MEMBER_INDICES_TEXT.split(',') if value.strip())
assert MEMBER_INDICES and len(MEMBER_INDICES) == len(set(MEMBER_INDICES))
assert all(0 <= value < 5 for value in MEMBER_INDICES)

ENSEMBLE_RECEIPT = RT05.fit_ensemble(
    DEVELOPMENT_INDEX,
    OUTPUT_DIR,
    device='cuda',
    member_indices=MEMBER_INDICES,
)
ENSEMBLE_READY = ENSEMBLE_RECEIPT['ensemble_complete']
print(json.dumps(ENSEMBLE_RECEIPT, indent=2))
if not ENSEMBLE_READY:
    print('This member subset is safely complete. Pending members:', ENSEMBLE_RECEIPT['pending_member_indices'])
    print('After all parallel runtimes finish, rerun this cell in any one notebook.')
"""
            ),
            markdown(
                """
### 5. Freeze the ensemble and fit source-separated calibration mappings

This runs only after all five model receipts are present. It evaluates the frozen ensemble
on calibration sources 0869–0900 and fits 11 isotonic mappings: five heuristic scores for
each of two pipelines, plus the PatchErrorNet ensemble mean. Every calibration source has
equal total fitting weight.
"""
            ),
            code(
                """
if ENSEMBLE_READY:
    CALIBRATION_PREDICTION_RECEIPT = RT05.collect_calibration_predictions(
        DEVELOPMENT_INDEX, OUTPUT_DIR, device='cuda'
    )
    CALIBRATION_RECEIPT = RT05.fit_calibration_mappings(OUTPUT_DIR)
    FIGURE_PATHS = RT05.build_diagnostic_figures(OUTPUT_DIR)
    print(json.dumps(CALIBRATION_PREDICTION_RECEIPT, indent=2))
    print(json.dumps(CALIBRATION_RECEIPT, indent=2))
    for figure_path in FIGURE_PATHS:
        display(DisplayImage(filename=figure_path))
else:
    CALIBRATION_RECEIPT = None
    print('Calibration skipped until all five ensemble members are complete.')
"""
            ),
            markdown(
                """
### 6. Audit and package the development reliability bundle

The final ZIP contains frozen model checkpoints, histories, calibration predictions,
mappings, diagnostics, figures, and cryptographic receipts. Mutable resume checkpoints are
deliberately excluded. Upload the ZIP and the executed notebook for independent readback.
"""
            ),
            code(
                """
if ENSEMBLE_READY and CALIBRATION_RECEIPT is not None:
    FINAL_RESULT = RT05.finalize_development_bundle(OUTPUT_DIR)
    print(json.dumps(FINAL_RESULT, indent=2))
    print('UPLOAD THIS RESULT ZIP:', FINAL_RESULT['archive_path'])
    print('ALSO DOWNLOAD THIS EXECUTED NOTEBOOK from Colab: File > Download > .ipynb')
    print('Independent test run authorized: false')
else:
    FINAL_RESULT = None
    print('Packaging skipped until ensemble fitting and calibration both finish.')
"""
            ),
            markdown(
                """
## Handoff

Return two files after the green final cell:

1. `independent_05c2_development_reliability_<timestamp>.zip`
2. the executed `05C2_Development_Reliability_Training_and_Calibration.ipynb`

Successful completion establishes that the trained comparator and frozen calibration
mappings are ready. It does **not** establish independent calibration or the final novelty
claim, and it does not authorize test inference; those require a separate readiness gate.
"""
            ),
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {"path": str(OUTPUT), "cell_count": len(notebook["cells"]), "digests": digests},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
