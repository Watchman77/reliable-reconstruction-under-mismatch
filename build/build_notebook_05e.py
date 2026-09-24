#!/usr/bin/env python3
"""Build the pre-locked one-time Stage-05E analysis notebook."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "experiments" / "independent_05" / "independent_analysis.py"
LOCK = ROOT / "experiments" / "independent_05" / "stage_05e_analysis_lock.json"
OUTPUT = ROOT / "notebooks" / "05E_One_Time_Locked_Independent_Analysis.ipynb"


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
    analysis_source = ANALYSIS.read_text(encoding="utf-8")
    lock_text = LOCK.read_text(encoding="utf-8")
    digests = {
        "analysis": hashlib.sha256(analysis_source.encode()).hexdigest(),
        "lock": hashlib.sha256(lock_text.encode()).hexdigest(),
    }
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
            "colab": {"name": OUTPUT.name, "provenance": []},
            "experiment": {
                "id": "independent_05",
                "stage": "05E_one_time_locked_analysis",
                "required_shards": 5,
                "outcome_blind_analysis_locked": True,
                "unsealing_authorized_only_after_all_shards_verify": True,
            },
        },
        "cells": [
            markdown(
                """
# 05E · One-time locked independent analysis

**Run only after all five sealed Stage-05D shard ZIPs are present**

This notebook was fixed before independent inference. It first verifies every byte and
every cross-shard lock while results remain sealed. Only after all five archives pass does
it perform the one-time unsealing, frozen H1/H2 tests, 10,000-replicate source bootstrap,
100,000 sign flips per hypothesis, Holm correction, calibration assessment, secondary
summaries, and diagnostic figures.

No GPU is required. Do not edit the implementation or analysis lock.
"""
            ),
            markdown(
                """
### 1. Mount Drive and load the precommitted analysis

The implementation and analysis lock are embedded byte-for-byte and hash-checked. The
lock records the exact Stage-05D runner and transition hashes, all statistical conventions,
and the fixed five-shard source map.
"""
            ),
            code(
                """
import hashlib
import json
import types
from pathlib import Path

import numpy as np
import pandas as pd
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
else:
    PROJECT_DIR = Path.cwd()
    if PROJECT_DIR.name == 'notebooks':
        PROJECT_DIR = PROJECT_DIR.parent
print('Project:', PROJECT_DIR)
"""
            ),
            code(
                f"""
#@title 🔒 Embedded Stage 05E implementation and analysis lock (expand only for audit) {{ display-mode: "form" }}
ANALYSIS_SOURCE = {analysis_source!r}
ANALYSIS_LOCK_TEXT = {lock_text!r}
EXPECTED_DIGESTS = {digests!r}

assert hashlib.sha256(ANALYSIS_SOURCE.encode()).hexdigest() == EXPECTED_DIGESTS['analysis']
assert hashlib.sha256(ANALYSIS_LOCK_TEXT.encode()).hexdigest() == EXPECTED_DIGESTS['lock']
IA05 = types.ModuleType('independent_05_locked_analysis_embedded')
exec(compile(ANALYSIS_SOURCE, '<independent_05_locked_analysis_embedded>', 'exec'), IA05.__dict__)
ANALYSIS_LOCK_05E = IA05.validate_analysis_lock(
    ANALYSIS_LOCK_TEXT, EXPECTED_DIGESTS['analysis']
)
print(json.dumps(IA05.static_self_check(), indent=2))
print('Outcome-blind Stage-05E analysis lock: VERIFIED')
""",
                hidden=True,
            ),
            markdown(
                """
### 2. Locate exactly five sealed shard archives

Leave the folder blank to use the project `results/` directory. There must be exactly one
ZIP for each shard index 0–4. If duplicate rerun ZIPs exist, move the extras elsewhere;
the notebook refuses to choose between them.
"""
            ),
            code(
                """
SHARD_ARCHIVE_DIR_TEXT = ''  #@param {type:"string"}
SHARD_ARCHIVE_DIR = (
    Path(SHARD_ARCHIVE_DIR_TEXT) if SHARD_ARCHIVE_DIR_TEXT.strip()
    else PROJECT_DIR / 'results'
)
candidates = sorted(SHARD_ARCHIVE_DIR.glob('independent_05d_test_shard_*_of_05*.zip'))
assert candidates, f'No Stage-05D sealed shard ZIPs found in {SHARD_ARCHIVE_DIR}'
by_index = {}
for path in candidates:
    index = IA05.shard_identity(path)
    by_index.setdefault(index, []).append(path)
duplicates = {index: paths for index, paths in by_index.items() if len(paths) != 1}
assert not duplicates, (
    'Expected exactly one ZIP per shard index. Move duplicate reruns out of this folder: '
    f'{duplicates}'
)
assert sorted(by_index) == list(range(5)), f'Missing shard indices: {sorted(set(range(5)) - set(by_index))}'
SHARD_ARCHIVES_05D = [by_index[index][0] for index in range(5)]
print('Found the complete fixed shard set:')
for index, path in enumerate(SHARD_ARCHIVES_05D):
    print(f'  shard {index}: {path.name}')
print('No outcome file has been opened by this cell.')
"""
            ),
            markdown(
                """
### 3. Verify all shards, then unseal once

This cell is the formal boundary. It verifies all 625 manifested shard files before
creating the analysis directory. It then runs only the precommitted analysis. The final
directory is published atomically, and a second run is refused.
"""
            ),
            code(
                """
OUTPUT_DIR_05E = PROJECT_DIR / 'results' / 'independent_05e_locked_analysis'
RESULT_05E = IA05.run_analysis(
    SHARD_ARCHIVES_05D,
    OUTPUT_DIR_05E,
    ANALYSIS_LOCK_TEXT,
    EXPECTED_DIGESTS['analysis'],
)
assert RESULT_05E['status'] == 'passed_one_time_locked_analysis'
assert RESULT_05E['final_literature_novelty_claim_established'] is False
print('ONE-TIME ANALYSIS STATUS:', RESULT_05E['status'])
print('RESULT ARCHIVE:', RESULT_05E['archive_path'])
print('ARCHIVE SHA-256:', RESULT_05E['archive_sha256'])
"""
            ),
            markdown(
                """
### 4. Read the confirmatory decision and calibration results

The cohort is now formally unsealed. The table below reports the exact frozen decision
components; secondary outcomes cannot rescue a failed primary gate.
"""
            ),
            code(
                """
PRIMARY_05E = json.loads((OUTPUT_DIR_05E / 'primary_hypotheses.json').read_text())
primary_rows = []
for hypothesis, row in PRIMARY_05E['hypotheses'].items():
    primary_rows.append({
        'hypothesis': hypothesis,
        'mean_difference': row['mean_difference'],
        'ci_low': row['paired_source_bootstrap_95_ci'][0],
        'ci_high': row['paired_source_bootstrap_95_ci'][1],
        'relative_reduction': row['relative_reduction'],
        'raw_one_sided_p': row['p_value_one_sided'],
        'holm_adjusted_p': row['holm_adjusted_p_value'],
        'practical_gate': row['practical_gate_passed'],
        'statistical_gate': row['statistical_gate_passed'],
        'confirmatory_gate': row['confirmatory_gate_passed'],
    })
display(pd.DataFrame(primary_rows))
print('Both confirmatory gates passed:', PRIMARY_05E['both_confirmatory_gates_passed'])
print('Experimental novelty gate passed:', PRIMARY_05E['experimental_novelty_gate_passed'])
print('Final literature novelty claim established:', PRIMARY_05E['final_literature_novelty_claim_established'])
print(PRIMARY_05E['claim_boundary'])

CALIBRATION_05E = pd.read_csv(OUTPUT_DIR_05E / 'calibration_metrics.csv')
display(CALIBRATION_05E[CALIBRATION_05E.scope == 'all_chains'].reset_index(drop=True))
"""
            ),
            markdown(
                """
### 5. Display the locked diagnostic figures

These figures are generated entirely by the precommitted analysis: confirmatory paired
contrasts, the primary-chain risk–coverage curves, and independent reliability diagrams.
"""
            ),
            code(
                """
for filename in (
    'primary_contrasts.png',
    'primary_risk_coverage.png',
    'independent_calibration_reliability.png',
):
    display(DisplayImage(filename=str(OUTPUT_DIR_05E / 'figures' / filename)))
"""
            ),
            markdown(
                """
## Handoff

Return the generated `independent_05e_locked_analysis_<timestamp>.zip` and this executed
notebook. Stage 05E decides the independent experimental gates. Stage 05F is the final
claim synthesis: it must combine this result with the already locked nearest-method
literature boundary and must preserve failures as carefully as successes.
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
