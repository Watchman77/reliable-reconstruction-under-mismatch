#!/usr/bin/env python3
"""Build the self-contained sharded development-generation notebook."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_NOTEBOOK = ROOT / "notebooks" / "04_DIV2K_JPEG_Aware_Baseline.ipynb"
if not REFERENCE_NOTEBOOK.is_file():
    REFERENCE_NOTEBOOK = ROOT / "build" / "notebook04_reference.ipynb"
CANARY_SOURCE = ROOT / "experiments" / "independent_05" / "canary.py"
GENERATOR_SOURCE = ROOT / "experiments" / "independent_05" / "development_generation.py"
PROTOCOL = ROOT / "experiments" / "independent_05" / "protocol_freeze.json"
RECEIPT = ROOT / "experiments" / "independent_05" / "data_receipt.json"
AMENDMENT = ROOT / "experiments" / "independent_05" / "amendments" / "0001_canary_schema_and_provenance.json"
OUTPUT = ROOT / "notebooks" / "05C1_Development_Reconstruction_Shards.ipynb"


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
    reference = json.loads(REFERENCE_NOTEBOOK.read_text(encoding="utf-8"))
    inherited_setup = "".join(reference["cells"][1]["source"])
    canary_source = CANARY_SOURCE.read_text(encoding="utf-8")
    generator_source = GENERATOR_SOURCE.read_text(encoding="utf-8")
    protocol_text = PROTOCOL.read_text(encoding="utf-8")
    receipt_text = RECEIPT.read_text(encoding="utf-8")
    amendment_text = AMENDMENT.read_text(encoding="utf-8")

    digests = {
        "canary": hashlib.sha256(canary_source.encode()).hexdigest(),
        "generator": hashlib.sha256(generator_source.encode()).hexdigest(),
        "protocol": hashlib.sha256(protocol_text.encode()).hexdigest(),
        "receipt": hashlib.sha256(receipt_text.encode()).hexdigest(),
        "amendment": hashlib.sha256(amendment_text.encode()).hexdigest(),
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
                "stage": "05C_development_generation",
                "role": "development_only",
                "shard_size": 8,
                "shard_count": 12,
                "test_inference_authorized": False,
            },
        },
        "cells": [
            markdown(
                """
# 05C1 · Full development reconstruction shards

**DIV2K 0805–0900 only · 12 resumable shards · no TESTIMAGES inference**

This notebook generates the compact reconstruction evidence needed to train the frozen
five-member PatchErrorNet comparator and fit the frozen isotonic calibration mappings.
Each shard contains eight sources across all seven acquisition chains: 56 observations,
4,480 DRUNet calls, and 168 FBCNN calls.

Run shard indices **0 through 11**, one at a time. A completed observation is hash-checked
and skipped on rerun, so an interrupted shard resumes safely from its Drive folder. The
large embedded implementation cells are collapsed; expand them only for audit.

This stage remains development-only. It cannot load or process TESTIMAGES and cannot
authorize the independent run.
"""
            ),
            code(
                "#@title 🔒 Embedded verified reconstruction modules (expand only for audit) { display-mode: \"form\" }\n"
                + inherited_setup,
                hidden=True,
            ),
            markdown(
                """
### 1. Load the audited stage code

The canary implementation, sharded generator, frozen protocol, data receipt, and recorded
outcome-blind amendment are embedded and SHA-256 checked before execution.
"""
            ),
            code(
                f"""
#@title 🔒 Embedded Stage 05C1 code and receipts (expand only for audit) {{ display-mode: "form" }}
CANARY_SOURCE = {canary_source!r}
GENERATOR_SOURCE = {generator_source!r}
PROTOCOL_TEXT = {protocol_text!r}
DATA_RECEIPT_TEXT = {receipt_text!r}
AMENDMENT_TEXT = {amendment_text!r}
EXPECTED_DIGESTS = {digests!r}

assert hashlib.sha256(CANARY_SOURCE.encode()).hexdigest() == EXPECTED_DIGESTS['canary']
assert hashlib.sha256(GENERATOR_SOURCE.encode()).hexdigest() == EXPECTED_DIGESTS['generator']
assert hashlib.sha256(PROTOCOL_TEXT.encode()).hexdigest() == EXPECTED_DIGESTS['protocol']
assert hashlib.sha256(DATA_RECEIPT_TEXT.encode()).hexdigest() == EXPECTED_DIGESTS['receipt']
assert hashlib.sha256(AMENDMENT_TEXT.encode()).hexdigest() == EXPECTED_DIGESTS['amendment']

PROTOCOL_05 = json.loads(PROTOCOL_TEXT)
DATA_RECEIPT_05 = json.loads(DATA_RECEIPT_TEXT)
AMENDMENT_05 = json.loads(AMENDMENT_TEXT)
assert PROTOCOL_05['independent_test_run_authorized'] is False
assert DATA_RECEIPT_05['test_inference_performed'] is False
assert AMENDMENT_05['outcome_blind'] is True
assert AMENDMENT_05['independent_test_output_existed'] is False

C05 = types.ModuleType('independent_05_canary_embedded')
exec(compile(CANARY_SOURCE, '<independent_05_canary_embedded>', 'exec'), C05.__dict__)
C05.B01, C05.L02, C05.J04 = B01, L02, J04
DG05 = types.ModuleType('independent_05_development_generation_embedded')
exec(compile(GENERATOR_SOURCE, '<independent_05_development_generation_embedded>', 'exec'), DG05.__dict__)
DG05.C05 = C05

PARENT_PROVENANCE_04 = json.loads(json.dumps(PROVENANCE))
PROVENANCE_05C_DEV = json.loads(json.dumps(PROVENANCE))
PROVENANCE_05C_DEV['parent_experiment'] = PROVENANCE_05C_DEV.pop('experiment')
PROVENANCE_05C_DEV['experiment'] = 'independent_05'
PROVENANCE_05C_DEV['stage'] = '05C_development_generation'
PROVENANCE_05C_DEV['role'] = 'development_only'
PROVENANCE_05C_DEV['parent_provenance_sha256'] = hashlib.sha256(
    json.dumps(PARENT_PROVENANCE_04, sort_keys=True, separators=(',', ':')).encode()
).hexdigest()
PROVENANCE_05C_DEV['protocol_sha256'] = EXPECTED_DIGESTS['protocol']
PROVENANCE_05C_DEV['amendment_sha256'] = EXPECTED_DIGESTS['amendment']
PROVENANCE_05C_DEV['dpir']['training_overlap'] = (
    'The DPIR paper reports DIV2K training. All 0805-0900 outputs are exposed '
    'development data and cannot support independent claims.'
)
PROVENANCE_05C_DEV['fbcnn']['training_overlap'] = (
    'The FBCNN paper reports DIV2K and Flickr2K training. All 0805-0900 outputs '
    'are exposed development data and cannot support independent claims.'
)
print('Stage 05C1 code, frozen inputs, amendment and provenance verified.')
""",
                hidden=True,
            ),
            markdown(
                """
### 2. Select one development shard

Choose an integer from `0` to `11`. Keep `SHARD_SIZE = 8`; changing it would alter the
locked shard map and is deliberately blocked.
"""
            ),
            code(
                """
SHARD_INDEX = 0  #@param {type:"integer"}
SHARD_SIZE = 8
assert SHARD_SIZE == 8
SELECTED_SOURCES_05C1 = DG05.shard_sources(int(SHARD_INDEX), SHARD_SIZE)
SHARD_COUNT_05C1 = 12
print(f'Shard {SHARD_INDEX + 1}/{SHARD_COUNT_05C1}:', list(SELECTED_SOURCES_05C1))
print('Expected workload: 56 observations; 4,480 DRUNet + 168 FBCNN experiment calls')
"""
            ),
            markdown(
                """
### 3. Mount Drive and verify the selected source bytes

Place `DIV2K_valid_HR.zip` either directly in the project folder or in its `inputs/`
subfolder. Only the eight selected source members are extracted, and every byte hash is
checked against the outcome-blind receipt.
"""
            ),
            code(
                """
import zipfile
import torch
try:
    import google.colab
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

if IN_COLAB:
    from google.colab import drive
    drive.mount('/content/drive')
    PROJECT_DIR = Path('/content/drive/MyDrive/reliable-reconstruction-under-mismatch')
else:
    PROJECT_DIR = Path.cwd()
    if PROJECT_DIR.name == 'notebooks':
        PROJECT_DIR = PROJECT_DIR.parent

INPUT_DIR = PROJECT_DIR / 'inputs'
archive_candidates = [PROJECT_DIR / 'DIV2K_valid_HR.zip', INPUT_DIR / 'DIV2K_valid_HR.zip']
DIV2K_ARCHIVE = next((path for path in archive_candidates if path.is_file()), archive_candidates[-1])
DEVELOPMENT_DATA_DIR = INPUT_DIR / 'div2k_development'
DEVELOPMENT_DATA_DIR.mkdir(parents=True, exist_ok=True)

assert DIV2K_ARCHIVE.is_file(), f'Missing DIV2K archive: {DIV2K_ARCHIVE}'
assert C05.sha256_file(DIV2K_ARCHIVE) == DATA_RECEIPT_05['development_archive']['observed_sha256']
receipt_sources = {row['source_id']: row for row in DATA_RECEIPT_05['development_archive']['sources']}
with zipfile.ZipFile(DIV2K_ARCHIVE) as archive:
    for source_id in SELECTED_SOURCES_05C1:
        destination = DEVELOPMENT_DATA_DIR / f'{source_id}.png'
        expected = receipt_sources[source_id]
        if not destination.exists():
            payload = archive.read(expected['member_path'])
            assert hashlib.sha256(payload).hexdigest() == expected['sha256']
            destination.write_bytes(payload)
        assert C05.sha256_file(destination) == expected['sha256']
print('Verified selected development sources:', list(SELECTED_SOURCES_05C1))
"""
            ),
            markdown(
                """
### 4. Prepare pinned models and the resumable destination

The output directory is deterministic for the shard. Rerunning the same index resumes only
completed, hash-valid observations and preserves partial evidence for inspection.
"""
            ),
            code(
                """
assert torch.cuda.is_available(), 'Select Runtime > Change runtime type > GPU before continuing.'
MODEL_CACHE = PROJECT_DIR / 'model_cache'
DPIR_WEIGHTS = Path(os.environ.get('IMAGING05_DPIR_WEIGHTS', str(MODEL_CACHE / 'drunet_color.pth')))
FBCNN_WEIGHTS = Path(os.environ.get('IMAGING05_FBCNN_WEIGHTS', str(MODEL_CACHE / 'fbcnn_color.pth')))
VENDOR_DIRS_05 = {
    key: MODEL_CACHE / f"{key}_{PROVENANCE_05C_DEV[key]['upstream_commit'][:7]}"
    for key in VENDORS
}
for key, files in VENDORS.items():
    for relative, source in files.items():
        path = VENDOR_DIRS_05[key] / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            assert J04.sha256(path) == PROVENANCE_05C_DEV[key]['files'][relative]
        else:
            path.write_bytes(source.encode())

OUTPUT_DIR_05C1 = PROJECT_DIR / 'results' / (
    f'independent_05c_development_shard_{int(SHARD_INDEX):02d}_of_{SHARD_COUNT_05C1:02d}'
)
print('GPU:', torch.cuda.get_device_name(0))
print('Resumable destination:', OUTPUT_DIR_05C1)
"""
            ),
            markdown(
                """
### 5. Generate or resume the shard

This is the long GPU cell. It writes one compact bundle and one record atomically after
each observation, then builds aggregate tables and a complete export manifest.
"""
            ),
            code(
                """
RESULT_05C1 = DG05.run_shard(
    DEVELOPMENT_DATA_DIR,
    OUTPUT_DIR_05C1,
    PROTOCOL_05,
    DATA_RECEIPT_05,
    PROVENANCE_05C_DEV,
    VENDOR_DIRS_05,
    DPIR_WEIGHTS,
    FBCNN_WEIGHTS,
    SELECTED_SOURCES_05C1,
)
print(json.dumps(RESULT_05C1['checks'], indent=2))
"""
            ),
            markdown(
                """
### 6. Verify and package the shard

The packaged shard remains development-only. Upload its ZIP for independent readback; do
not combine or edit the files manually.
"""
            ),
            code(
                """
import shutil
status = json.loads((OUTPUT_DIR_05C1 / 'status.json').read_text())
manifest = json.loads((OUTPUT_DIR_05C1 / 'export_manifest.json').read_text())
assert status['status'] == 'passed_development_shard'
assert status['test_inference_performed'] is False
assert status['independent_test_run_authorized'] is False
assert manifest['source_ids'] == list(SELECTED_SOURCES_05C1)
assert manifest['test_inference_performed'] is False
for row in manifest['files']:
    path = OUTPUT_DIR_05C1 / row['path']
    assert path.stat().st_size == row['byte_count']
    assert DG05.sha256_file(path) == row['sha256']

package_stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
archive_base = OUTPUT_DIR_05C1.parent / f'{OUTPUT_DIR_05C1.name}_{package_stamp}'
archive_path = Path(shutil.make_archive(str(archive_base), 'zip', root_dir=OUTPUT_DIR_05C1))
print('SHARD STATUS:', status['status'])
print('UPLOAD THIS SHARD ZIP:', archive_path)
print('ZIP SHA-256:', DG05.sha256_file(archive_path))
print('Independent test run authorized: false')
"""
            ),
            markdown(
                """
## Handoff

Repeat the notebook for the remaining shard indices. All 12 independently verified shards
are required before PatchErrorNet training begins. Comparator fitting will use only shards
covering 0805–0868; calibration will use only 0869–0900 after the ensemble is frozen.
"""
            ),
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "path": str(OUTPUT),
                "cell_count": len(notebook["cells"]),
                "digests": digests,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
