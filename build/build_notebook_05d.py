#!/usr/bin/env python3
"""Build the self-contained, outcome-sealed Stage-05D shard notebook."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_CANDIDATES = (
    ROOT / "notebooks" / "04_DIV2K_JPEG_Aware_Baseline.ipynb",
    ROOT / "build" / "notebook04_reference.ipynb",
    ROOT / "recovered" / "05C1B_Development_Reconstruction_Shards.ipynb",
)
CANARY = ROOT / "experiments" / "independent_05" / "canary.py"
RELIABILITY = ROOT / "experiments" / "independent_05" / "reliability_training.py"
RUNNER = ROOT / "experiments" / "independent_05" / "independent_run.py"
PROTOCOL = ROOT / "experiments" / "independent_05" / "protocol_freeze.json"
RECEIPT = ROOT / "experiments" / "independent_05" / "data_receipt.json"
TRANSITION = ROOT / "experiments" / "independent_05" / "stage_05d_transition.json"
AMENDMENT = (
    ROOT
    / "experiments"
    / "independent_05"
    / "amendments"
    / "0002_stage_05d_execution_clarifications.json"
)
OUTPUT = ROOT / "notebooks" / "05D_Locked_Independent_Evaluation_Shards.ipynb"


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
    reference_path = next((path for path in REFERENCE_CANDIDATES if path.is_file()), None)
    assert reference_path is not None, "missing audited reconstruction reference notebook"
    reference = json.loads(reference_path.read_text(encoding="utf-8"))
    inherited_setup = "".join(reference["cells"][1]["source"])
    if inherited_setup.lstrip().startswith("#@title"):
        inherited_setup = inherited_setup.split("\n", 1)[1]

    texts = {
        "canary": CANARY.read_text(encoding="utf-8"),
        "reliability": RELIABILITY.read_text(encoding="utf-8"),
        "runner": RUNNER.read_text(encoding="utf-8"),
        "protocol": PROTOCOL.read_text(encoding="utf-8"),
        "receipt": RECEIPT.read_text(encoding="utf-8"),
        "transition": TRANSITION.read_text(encoding="utf-8"),
        "amendment": AMENDMENT.read_text(encoding="utf-8"),
    }
    digests = {key: hashlib.sha256(value.encode()).hexdigest() for key, value in texts.items()}

    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3"},
            "colab": {"name": OUTPUT.name, "provenance": [], "gpuType": "L4"},
            "accelerator": "GPU",
            "experiment": {
                "id": "independent_05",
                "stage": "05D_locked_independent_inference",
                "role": "sealed_independent_test",
                "shard_count": 5,
                "sources_per_shard": 8,
                "test_inference_authorized": True,
                "performance_inspection_authorized": False,
            },
        },
        "cells": [
            markdown(
                """
# 05D · Locked independent evaluation shards

**40 sealed TESTIMAGES sources · five fixed shards · no interim result display**

The outcome-blind readiness gate has passed. This notebook runs one immutable shard of
eight sources across all seven frozen acquisition chains. It verifies every protocol,
dataset, model, calibration, and implementation digest before inference.

Duplicate the notebook into five Colab runtimes and use shard indices **0, 1, 2, 3, 4**.
Each output is resumable and contains cryptographically manifested evidence. The notebook
prints progress identifiers and hashes only—never quality, risk, calibration, or hypothesis
results. Do not open result CSV/JSON/NPZ files before all five shards are returned and the
separate Stage-05E unsealing notebook is locked.
"""
            ),
            markdown(
                """
### 1. Load the audited reconstruction modules

The long inherited implementation is collapsed. It is the same pinned DPIR/FBCNN path
that passed the Stage-05C engineering canary and development-shard readbacks.
"""
            ),
            code(
                "#@title 🔒 Embedded verified reconstruction modules (expand only for audit) { display-mode: \"form\" }\n"
                + inherited_setup,
                hidden=True,
            ),
            markdown(
                """
### 2. Verify the Stage-05D lock

Exact source text for the canary adapters, reliability inference, independent runner,
frozen protocol, data receipt, execution clarification, and authorization transition is
embedded and SHA-256 checked before any sealed archive is opened.
"""
            ),
            code(
                f"""
#@title 🔒 Embedded Stage 05D code and lock documents (expand only for audit) {{ display-mode: "form" }}
CANARY_SOURCE = {texts['canary']!r}
RELIABILITY_SOURCE = {texts['reliability']!r}
INDEPENDENT_SOURCE = {texts['runner']!r}
PROTOCOL_TEXT = {texts['protocol']!r}
DATA_RECEIPT_TEXT = {texts['receipt']!r}
TRANSITION_TEXT = {texts['transition']!r}
AMENDMENT_TEXT = {texts['amendment']!r}
EXPECTED_DIGESTS = {digests!r}

for name, source in {{
    'canary': CANARY_SOURCE,
    'reliability': RELIABILITY_SOURCE,
    'runner': INDEPENDENT_SOURCE,
    'protocol': PROTOCOL_TEXT,
    'receipt': DATA_RECEIPT_TEXT,
    'transition': TRANSITION_TEXT,
    'amendment': AMENDMENT_TEXT,
}}.items():
    assert hashlib.sha256(source.encode()).hexdigest() == EXPECTED_DIGESTS[name], name

C05 = types.ModuleType('independent_05_canary_embedded')
exec(compile(CANARY_SOURCE, '<independent_05_canary_embedded>', 'exec'), C05.__dict__)
C05.B01, C05.L02, C05.J04 = B01, L02, J04
RT05 = types.ModuleType('independent_05_reliability_embedded')
exec(compile(RELIABILITY_SOURCE, '<independent_05_reliability_embedded>', 'exec'), RT05.__dict__)
IR05 = types.ModuleType('independent_05_locked_runner_embedded')
exec(compile(INDEPENDENT_SOURCE, '<independent_05_locked_runner_embedded>', 'exec'), IR05.__dict__)
IR05.C05, IR05.RT05 = C05, RT05

PROTOCOL_05, DATA_RECEIPT_05, TRANSITION_05D = IR05.validate_frozen_inputs(
    PROTOCOL_TEXT,
    DATA_RECEIPT_TEXT,
    TRANSITION_TEXT,
    EXPECTED_DIGESTS['runner'],
)
AMENDMENT_05D = json.loads(AMENDMENT_TEXT)
assert AMENDMENT_05D['outcome_blind'] is True
assert AMENDMENT_05D['independent_test_output_existed'] is False
assert TRANSITION_05D['independent_test_run_authorized'] is True
print(json.dumps(IR05.static_self_check(), indent=2))
print('Outcome-blind readiness transition: VERIFIED')
""",
                hidden=True,
            ),
            markdown(
                """
### 3. Select exactly one fixed shard

Set `SHARD_INDEX` to an integer from `0` through `4`. Never change the listed source IDs,
shard count, or shard size. Parallel runtimes are safe because their output paths do not
overlap.
"""
            ),
            code(
                """
SHARD_INDEX = 0  #@param {type:"integer"}
assert 0 <= int(SHARD_INDEX) < IR05.SHARD_COUNT
SELECTED_SOURCES_05D = IR05.sources_for_shard(DATA_RECEIPT_05, int(SHARD_INDEX))
assert TRANSITION_05D['sharding']['source_ids_by_shard'][str(int(SHARD_INDEX))] == list(SELECTED_SOURCES_05D)
print(f'Locked shard {int(SHARD_INDEX) + 1}/5')
print('Source IDs:', list(SELECTED_SOURCES_05D))
print('Expected workload: 56 observations; no performance values will be displayed')
"""
            ),
            markdown(
                """
### 4. Mount Drive and locate the two immutable input archives

Default locations:

- `inputs/SAMPLING_8BIT_RGB_2400x2400.tar.bz2`
- the exact Stage-05C2 reliability ZIP anywhere in `results/`

Leave both text boxes blank for those defaults. A custom value must be a complete file
path, not a directory. The reliability ZIP is selected by its exact frozen SHA-256.
"""
            ),
            code(
                """
try:
    import google.colab
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

if IN_COLAB:
    from google.colab import drive
    drive.mount('/content/drive')
    PROJECT_DIR = Path('/content/drive/MyDrive/reliable-reconstruction-under-mismatch')
    RELIABILITY_CACHE_05D = Path('/content/independent_05d_frozen_reliability')
else:
    PROJECT_DIR = Path.cwd()
    if PROJECT_DIR.name == 'notebooks':
        PROJECT_DIR = PROJECT_DIR.parent
    RELIABILITY_CACHE_05D = PROJECT_DIR / 'results' / '.independent_05d_frozen_reliability'

TEST_ARCHIVE_TEXT = ''  #@param {type:"string"}
RELIABILITY_ARCHIVE_TEXT = ''  #@param {type:"string"}
TEST_ARCHIVE_05D = (
    Path(TEST_ARCHIVE_TEXT) if TEST_ARCHIVE_TEXT.strip()
    else PROJECT_DIR / 'inputs' / 'SAMPLING_8BIT_RGB_2400x2400.tar.bz2'
)

if RELIABILITY_ARCHIVE_TEXT.strip():
    RELIABILITY_ARCHIVE_05D = Path(RELIABILITY_ARCHIVE_TEXT)
else:
    candidates = sorted((PROJECT_DIR / 'results').glob('independent_05c2_development_reliability*.zip'))
    exact = [path for path in candidates if IR05.sha256_file(path) == IR05.RELIABILITY_ARCHIVE_SHA256]
    assert exact, 'Exact frozen Stage-05C2 reliability ZIP not found in results/. Upload it or enter its full path.'
    RELIABILITY_ARCHIVE_05D = exact[0]

assert TEST_ARCHIVE_05D.is_file(), f'Missing sealed archive: {TEST_ARCHIVE_05D}'
assert RELIABILITY_ARCHIVE_05D.is_file(), f'Missing reliability archive: {RELIABILITY_ARCHIVE_05D}'
assert TEST_ARCHIVE_05D.stat().st_size == IR05.TEST_ARCHIVE_BYTES
assert IR05.sha256_file(TEST_ARCHIVE_05D) == IR05.TEST_ARCHIVE_SHA256
assert IR05.sha256_file(RELIABILITY_ARCHIVE_05D) == IR05.RELIABILITY_ARCHIVE_SHA256
print('Sealed test archive hash: VERIFIED')
print('Frozen reliability archive hash: VERIFIED')
"""
            ),
            markdown(
                """
### 5. Prepare the pinned runtime and resumable destination

The result directory is deterministic for this shard. Completed observations are reused
only when both their record and compact bundle match the exact Stage-05D lock.
"""
            ),
            code(
                """
assert torch.cuda.is_available(), 'Select Runtime > Change runtime type > GPU before continuing.'
MODEL_CACHE = PROJECT_DIR / 'model_cache'
DPIR_WEIGHTS = Path(os.environ.get('IMAGING05_DPIR_WEIGHTS', str(MODEL_CACHE / 'drunet_color.pth')))
FBCNN_WEIGHTS = Path(os.environ.get('IMAGING05_FBCNN_WEIGHTS', str(MODEL_CACHE / 'fbcnn_color.pth')))

PARENT_PROVENANCE_04 = json.loads(json.dumps(PROVENANCE))
PROVENANCE_05D = json.loads(json.dumps(PROVENANCE))
PROVENANCE_05D['parent_experiment'] = PROVENANCE_05D.pop('experiment')
PROVENANCE_05D['experiment'] = 'independent_05'
PROVENANCE_05D['stage'] = IR05.STAGE
PROVENANCE_05D['role'] = IR05.ROLE
PROVENANCE_05D['protocol_sha256'] = IR05.PROTOCOL_SHA256
PROVENANCE_05D['data_receipt_sha256'] = IR05.DATA_RECEIPT_SHA256
PROVENANCE_05D['transition_sha256'] = hashlib.sha256(TRANSITION_TEXT.encode()).hexdigest()
PROVENANCE_05D['run_code_sha256'] = EXPECTED_DIGESTS['runner']
PROVENANCE_05D['reliability_archive_sha256'] = IR05.RELIABILITY_ARCHIVE_SHA256
PROVENANCE_05D['test_archive_sha256'] = IR05.TEST_ARCHIVE_SHA256
PROVENANCE_05D['test_inference_authorized'] = True
PROVENANCE_05D['test_performance_inspection_authorized'] = False

VENDOR_DIRS_05D = {
    key: MODEL_CACHE / f"{key}_{PROVENANCE_05D[key]['upstream_commit'][:7]}"
    for key in VENDORS
}
for key, files in VENDORS.items():
    for relative, source in files.items():
        path = VENDOR_DIRS_05D[key] / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            assert J04.sha256(path) == PROVENANCE_05D[key]['files'][relative]
        else:
            path.write_bytes(source.encode())
            assert J04.sha256(path) == PROVENANCE_05D[key]['files'][relative]

OUTPUT_DIR_05D = PROJECT_DIR / 'results' / (
    f'independent_05d_test_shard_{int(SHARD_INDEX):02d}_of_{IR05.SHARD_COUNT:02d}'
)
print('GPU:', torch.cuda.get_device_name(0))
print('Resumable sealed destination:', OUTPUT_DIR_05D)
"""
            ),
            markdown(
                """
### 6. Run or resume the sealed shard

This is the long GPU cell. It writes each observation atomically and prints only the
observation identifier. Do not expand or inspect the result files after it finishes.
"""
            ),
            code(
                """
RESULT_05D = IR05.run_shard(
    TEST_ARCHIVE_05D,
    RELIABILITY_ARCHIVE_05D,
    RELIABILITY_CACHE_05D,
    OUTPUT_DIR_05D,
    PROTOCOL_TEXT,
    DATA_RECEIPT_TEXT,
    TRANSITION_TEXT,
    EXPECTED_DIGESTS['runner'],
    PROVENANCE_05D,
    VENDOR_DIRS_05D,
    DPIR_WEIGHTS,
    FBCNN_WEIGHTS,
    int(SHARD_INDEX),
)
assert RESULT_05D['status'] == 'passed_locked_independent_shard'
assert RESULT_05D['test_performance_inspected'] is False
assert RESULT_05D['unsealed'] is False
print('SEALED SHARD STATUS:', RESULT_05D['status'])
print('Completed observations:', RESULT_05D['completed_observations'])
print('Export manifest SHA-256:', RESULT_05D['export_manifest_sha256'])
print('Performance values displayed: false')
"""
            ),
            markdown(
                """
### 7. Verify and package without unsealing

This checks every output byte against the internal manifest and packages the shard. It
does not parse or display quality, risk, prediction, or calibration values.
"""
            ),
            code(
                """
status = json.loads((OUTPUT_DIR_05D / 'status.json').read_text())
manifest = json.loads((OUTPUT_DIR_05D / 'export_manifest.json').read_text())
assert status['status'] == 'passed_locked_independent_shard'
assert status['test_inference_performed'] is True
assert status['test_performance_inspected'] is False
assert status['unsealed'] is False
assert manifest['source_ids'] == list(SELECTED_SOURCES_05D)
assert manifest['shard_index'] == int(SHARD_INDEX)
assert manifest['test_performance_inspected'] is False
assert manifest['unsealed'] is False
for row in manifest['files']:
    path = OUTPUT_DIR_05D / row['path']
    assert path.stat().st_size == row['byte_count']
    assert IR05.sha256_file(path) == row['sha256']

package_stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
archive_path = OUTPUT_DIR_05D.parent / f'{OUTPUT_DIR_05D.name}_{package_stamp}.zip'
temporary_archive = archive_path.with_suffix('.zip.partial')
with zipfile.ZipFile(temporary_archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    for row in manifest['files']:
        archive.write(OUTPUT_DIR_05D / row['path'], arcname=row['path'])
    archive.write(OUTPUT_DIR_05D / 'export_manifest.json', arcname='export_manifest.json')
temporary_archive.replace(archive_path)
print('UPLOAD THIS SEALED SHARD ZIP:', archive_path)
print('ZIP SHA-256:', IR05.sha256_file(archive_path))
print('ALSO DOWNLOAD THIS EXECUTED NOTEBOOK: File > Download > Download .ipynb')
print('DO NOT OPEN THE RESULT FILES. Unsealed: false')
"""
            ),
            markdown(
                """
## Handoff

Return the five sealed ZIPs (shards 0–4) plus one executed notebook. All five will be
independently checked for archive safety, manifest completeness, fixed membership, exact
locks, row counts, and cross-shard coverage before the one-time Stage-05E unsealing.

Running multiple shard indices in parallel is allowed. Running only favorable shards,
opening intermediate metrics, or changing any setting is forbidden by the frozen protocol.
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
                "reference": str(reference_path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
