#!/usr/bin/env python3
"""Build the self-contained Colab notebook for the stage-05C GPU canary."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_NOTEBOOK = ROOT / "notebooks" / "04_DIV2K_JPEG_Aware_Baseline.ipynb"
CANARY_SOURCE = ROOT / "experiments" / "independent_05" / "canary.py"
PROTOCOL = ROOT / "experiments" / "independent_05" / "protocol_freeze.json"
RECEIPT = ROOT / "experiments" / "independent_05" / "data_receipt.json"
OUTPUT = ROOT / "notebooks" / "05C_Independent_Validation_Engineering_Canary.ipynb"


def code(source: str):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
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
    protocol_text = PROTOCOL.read_text(encoding="utf-8")
    receipt_text = RECEIPT.read_text(encoding="utf-8")
    canary_sha256 = hashlib.sha256(canary_source.encode("utf-8")).hexdigest()
    protocol_sha256 = hashlib.sha256(protocol_text.encode("utf-8")).hexdigest()
    receipt_sha256 = hashlib.sha256(receipt_text.encode("utf-8")).hexdigest()

    notebook = {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": []}
    notebook["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
        "colab": {"name": OUTPUT.name, "provenance": []},
        "experiment": {
            "id": "independent_05",
            "stage": "05C_development_canary",
            "test_inference_authorized": False,
            "canary_source_ids": ["0805", "0806"],
            "canary_chain_ids": ["q8_b16_n2", "j75_b16_n2"],
        },
    }
    notebook["cells"] = [
        markdown(
            """
# 05C · Independent-validation engineering canary

**Development data only · DIV2K 0805–0806 · no TESTIMAGES inference**

This notebook exercises the frozen FBCNN, classical inverse and DPIR code paths on two
development sources. It uses the uncompressed negative control and the primary JPEG-Q75
chain, verifies deterministic acquisition, runs the complete operator/transformation score
paths, and smoke-tests the frozen six-channel PatchErrorNet architecture.

It does **not** fit PatchErrorNet, fit isotonic calibration, process any TESTIMAGES image,
inspect independent performance, or authorize the independent run. A passing result only
closes the reconstruction engineering-canary sub-gate of stage 05C.

Expected workload: 4 observations, 320 DRUNet calls, 12 FBCNN calls, plus small adapter
checks. Select a CUDA runtime before running the GPU cell. CPU execution is deliberately
blocked for the full canary.
"""
        ),
        code(inherited_setup),
        markdown(
            """
### 1. Load the frozen stage-05C canary implementation

The implementation, frozen protocol, and outcome-blind data receipt are embedded and
SHA-256 checked before use. The inherited DPIR/FBCNN sources and official component pins
are checked by the preceding cell.
"""
        ),
        code(
            f"""
CANARY_SOURCE = {canary_source!r}
CANARY_SOURCE_SHA256 = {canary_sha256!r}
PROTOCOL_TEXT = {protocol_text!r}
PROTOCOL_SHA256 = {protocol_sha256!r}
DATA_RECEIPT_TEXT = {receipt_text!r}
DATA_RECEIPT_SHA256 = {receipt_sha256!r}

assert hashlib.sha256(CANARY_SOURCE.encode()).hexdigest() == CANARY_SOURCE_SHA256
assert hashlib.sha256(PROTOCOL_TEXT.encode()).hexdigest() == PROTOCOL_SHA256
assert hashlib.sha256(DATA_RECEIPT_TEXT.encode()).hexdigest() == DATA_RECEIPT_SHA256
PROTOCOL_05 = json.loads(PROTOCOL_TEXT)
DATA_RECEIPT_05 = json.loads(DATA_RECEIPT_TEXT)
assert PROTOCOL_05['independent_test_run_authorized'] is False
assert DATA_RECEIPT_05['test_inference_performed'] is False
assert DATA_RECEIPT_05['receipt_status'] == 'pass'

C05 = types.ModuleType('independent_05_canary_embedded')
exec(compile(CANARY_SOURCE, '<independent_05_canary_embedded>', 'exec'), C05.__dict__)
C05.B01, C05.L02, C05.J04 = B01, L02, J04
print('Embedded stage-05C code, protocol, and data receipt verified.')
"""
        ),
        markdown(
            """
### 2. Locate the two original DIV2K canary sources

The default project folder is `MyDrive/reliable-reconstruction-under-mismatch`. Put the
original `DIV2K_valid_HR.zip` in its `inputs/` folder, or place the already-extracted original
`0805.png` and `0806.png` files in `inputs/div2k_canary/`. The notebook extracts only those
two members and verifies their receipt hashes; it never rewrites the source bytes.
"""
        ),
        code(
            """
import zipfile
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
DIV2K_ARCHIVE = Path(os.environ.get('IMAGING05_DIV2K_ARCHIVE', str(INPUT_DIR / 'DIV2K_valid_HR.zip')))
CANARY_DATA_DIR = Path(os.environ.get('IMAGING05_CANARY_DATA_DIR', str(INPUT_DIR / 'div2k_canary')))
CANARY_DATA_DIR.mkdir(parents=True, exist_ok=True)

receipt_sources = {row['source_id']: row for row in DATA_RECEIPT_05['development_archive']['sources']}
missing = [sid for sid in C05.CANARY_SOURCE_IDS if not (CANARY_DATA_DIR / f'{sid}.png').is_file()]
if missing:
    assert DIV2K_ARCHIVE.is_file(), f'Missing DIV2K archive: {DIV2K_ARCHIVE}'
    assert C05.sha256_file(DIV2K_ARCHIVE) == DATA_RECEIPT_05['development_archive']['observed_sha256']
    with zipfile.ZipFile(DIV2K_ARCHIVE) as archive:
        for sid in missing:
            member = receipt_sources[sid]['member_path']
            payload = archive.read(member)
            assert hashlib.sha256(payload).hexdigest() == receipt_sources[sid]['sha256']
            (CANARY_DATA_DIR / f'{sid}.png').write_bytes(payload)

for sid in C05.CANARY_SOURCE_IDS:
    path = CANARY_DATA_DIR / f'{sid}.png'
    assert C05.sha256_file(path) == receipt_sources[sid]['sha256'], f'Changed canary source: {sid}'
print('Verified canary inputs:', [str(CANARY_DATA_DIR / f'{sid}.png') for sid in C05.CANARY_SOURCE_IDS])
"""
        ),
        markdown(
            """
### 3. Outcome-blind preflight

This cell performs scope, source, crop and acquisition-repeat checks without loading a
neural checkpoint. It is safe to run on CPU. It must report exactly two sources and four
source/chain combinations.
"""
        ),
        code(
            """
CONFIG_05C = C05.derive_config(PROTOCOL_05)
CHAINS_05C = C05.validate_canary_scope(PROTOCOL_05, CONFIG_05C)
SOURCES_05C, SOURCE_MANIFEST_05C = C05.load_canary_sources(CANARY_DATA_DIR, DATA_RECEIPT_05, CONFIG_05C)
ACQUISITION_REPEAT_05C = C05.verify_acquisition_determinism(SOURCES_05C, CHAINS_05C, CONFIG_05C)
assert SOURCE_MANIFEST_05C.source_id.tolist() == ['0805', '0806']
assert len(ACQUISITION_REPEAT_05C) == 4 and ACQUISITION_REPEAT_05C.repeat_identical.all()
display(SOURCE_MANIFEST_05C)
display(ACQUISITION_REPEAT_05C)
print('Outcome-blind preflight passed; TESTIMAGES inference performed: false')
"""
        ),
        markdown(
            """
### 4. Prepare pinned components and destination

Official source bytes are embedded from the already-pinned Experiment 04 notebook. Official
release checkpoints are downloaded only when absent, then checked against the frozen byte
counts and SHA-256 digests. Results go to a new timestamped Drive folder.
"""
        ),
        code(
            """
MODEL_CACHE = PROJECT_DIR / 'model_cache'
DPIR_WEIGHTS = Path(os.environ.get('IMAGING05_DPIR_WEIGHTS', str(MODEL_CACHE / 'drunet_color.pth')))
FBCNN_WEIGHTS = Path(os.environ.get('IMAGING05_FBCNN_WEIGHTS', str(MODEL_CACHE / 'fbcnn_color.pth')))
VENDOR_DIRS_05 = {
    key: MODEL_CACHE / f"{key}_{PROVENANCE[key]['upstream_commit'][:7]}"
    for key in VENDORS
}
for key, files in VENDORS.items():
    for relative, source in files.items():
        path = VENDOR_DIRS_05[key] / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            assert J04.sha256(path) == PROVENANCE[key]['files'][relative], f'Changed vendor file: {path}'
        else:
            path.write_bytes(source.encode())

timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
OUTPUT_DIR_05C = Path(os.environ.get(
    'IMAGING05_CANARY_OUTPUT_DIR',
    str(PROJECT_DIR / 'results' / f'independent_05c_canary_{timestamp}')
))
assert not OUTPUT_DIR_05C.exists(), f'Existing run preserved: {OUTPUT_DIR_05C}'

print('Device:', 'CUDA GPU' if torch.cuda.is_available() else 'CPU (full canary will stop)')
print('Sources:', CONFIG_05C['source_ids'])
print('Chains:', CONFIG_05C['chain_ids'])
print('Planned workload: 4 observations; 320 DRUNet + 12 FBCNN experiment calls')
print('Destination:', OUTPUT_DIR_05C)
"""
        ),
        markdown(
            """
### 5. Run the development-only GPU canary

This is the long cell. It hard-fails without CUDA and snapshots after every observation.
Interruption preserves partial CSV/JSON/NPZ evidence in the result folder; rerun with a new
destination rather than overwriting it.
"""
        ),
        code(
            """
assert torch.cuda.is_available(), 'Select Runtime > Change runtime type > GPU, then run all cells.'
RESULT_05C = C05.run_canary(
    CANARY_DATA_DIR,
    OUTPUT_DIR_05C,
    PROTOCOL_05,
    DATA_RECEIPT_05,
    PROVENANCE,
    VENDOR_DIRS_05,
    DPIR_WEIGHTS,
    FBCNN_WEIGHTS,
)
print(json.dumps(RESULT_05C['payloads']['checks'], indent=2))
"""
        ),
        markdown(
            """
### 6. Verify and package the raw canary evidence

The package contains development-only engineering outputs. It contains no TESTIMAGES
prediction or performance artifact and does not authorize the independent run.
"""
        ),
        code(
            """
import shutil
status = json.loads((OUTPUT_DIR_05C / 'status.json').read_text())
manifest = json.loads((OUTPUT_DIR_05C / 'export_manifest.json').read_text())
assert status['status'] == 'passed_development_canary'
assert status['test_inference_performed'] is False
assert status['independent_test_run_authorized'] is False
assert manifest['test_inference_performed'] is False
for row in manifest['files']:
    path = OUTPUT_DIR_05C / row['path']
    assert path.stat().st_size == row['byte_count']
    assert C05.sha256_file(path) == row['sha256']

archive_path = Path(shutil.make_archive(str(OUTPUT_DIR_05C), 'zip', root_dir=OUTPUT_DIR_05C))
print('CANARY STATUS:', status['status'])
print('UPLOAD THIS RAW CANARY ZIP:', archive_path)
print('ZIP SHA-256:', C05.sha256_file(archive_path))
print('Independent test run authorized: false')
"""
        ),
        markdown(
            """
## Handoff

Upload the raw canary ZIP for independent readback. A verified pass permits continued stage
05C work on full development reconstruction generation, five-member PatchErrorNet fitting,
and source-separated isotonic calibration. It still does not permit TESTIMAGES inference;
that requires a separate versioned authorization after every readiness gate passes.
"""
        ),
    ]

    assert notebook["nbformat"] == 4 and notebook["cells"]
    assert all(cell["cell_type"] in {"markdown", "code"} for cell in notebook["cells"])
    assert all(not cell.get("outputs") for cell in notebook["cells"] if cell["cell_type"] == "code")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "path": str(OUTPUT),
                "cell_count": len(notebook["cells"]),
                "canary_source_sha256": canary_sha256,
                "protocol_sha256": protocol_sha256,
                "data_receipt_sha256": receipt_sha256,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
