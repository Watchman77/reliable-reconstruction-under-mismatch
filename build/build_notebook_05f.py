from __future__ import annotations

import base64
import gzip
import hashlib
import json
from pathlib import Path
from textwrap import dedent

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "library_inputs" / "Reconstruction_Systematic_Review_Matrix_2020_2026.xlsx"
OUTPUT_PATH = ROOT / "notebooks" / "05F_Locked_Literature_and_Experimental_Synthesis.ipynb"


def split_source(text: str) -> list[str]:
    lines = text.strip("\n").splitlines()
    first = next((line for line in lines if line.strip()), "")
    indent = len(first) - len(first.lstrip())
    prefix = " " * indent
    normalized = [line[indent:] if line.startswith(prefix) else line for line in lines]
    return ("\n".join(normalized) + "\n").splitlines(keepends=True)


def markdown(text: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": split_source(text),
    }


def code(text: str, *, cell_id: str | None = None) -> dict:
    metadata = {}
    if cell_id:
        metadata["id"] = cell_id
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": metadata,
        "outputs": [],
        "source": split_source(text),
    }


def build_literature_snapshot() -> tuple[str, str, int]:
    evidence = pd.read_excel(MATRIX_PATH, sheet_name="Evidence Matrix")
    columns = [
        "Study ID",
        "Year",
        "Authors",
        "Title",
        "Venue",
        "Publication type",
        "Peer reviewed",
        "Modality",
        "Forward model",
        "Mismatch type",
        "Solver family",
        "Physics integration",
        "Joint image/operator",
        "Image UQ",
        "Operator UQ",
        "Calibration",
        "OOD test",
        "Real data/hardware",
        "Compound degradation",
        "Time varying",
        "Hallucination test",
        "Abstention",
        "Code available",
        "Evidence status",
        "Inclusion decision",
        "Closest competitor",
        "Gap left open",
        "Primary source URL",
        "Review notes",
    ]
    evidence = evidence[columns].copy()
    csv_bytes = evidence.to_csv(index=False, lineterminator="\n").encode("utf-8")
    digest = hashlib.sha256(csv_bytes).hexdigest()
    encoded = base64.b64encode(gzip.compress(csv_bytes, compresslevel=9, mtime=0)).decode("ascii")
    return encoded, digest, len(evidence)


def main() -> None:
    encoded_snapshot, snapshot_sha256, study_count = build_literature_snapshot()

    cells = [
        markdown(
            """
            # 05F · Locked literature and experimental synthesis

            **Purpose:** close Experiment 05 without changing any Stage-05E threshold, hypothesis,
            endpoint, or test. This notebook validates the completed 05E archive, combines it with
            the literature snapshot locked to **15 September 2026**, and writes the final claim
            boundary and manuscript-ready reporting package.

            This is a reporting and decision notebook, not a new experiment. It performs no model
            fitting, no threshold tuning, no alternative hypothesis testing, and no post-test rescue.

            **Expected valid outcome:** the notebook may conclude that the broad novelty claim is not
            established while retaining a narrower, independently supported acquisition-chain
            contribution. That is a completed scientific result, not a runtime failure.

            **Runtime:** CPU only; approximately one minute after Drive mounts.
            """
        ),
        markdown(
            """
            ## 1. Setup and immutable inputs

            Leave the archive field blank to search the project `results/` folder. If the original
            notebook-generated 05E ZIP is present, it is selected by its recorded SHA-256. A Google
            Drive folder re-ZIP is also accepted when every internal file matches the 05E export
            manifest.
            """
        ),
        code(
            """
            import base64
            import csv
            import gzip
            import hashlib
            import io
            import json
            import os
            import shutil
            import zipfile
            from datetime import datetime, timezone
            from pathlib import Path

            import matplotlib.pyplot as plt
            import numpy as np
            import pandas as pd

            try:
                from IPython.display import Image as DisplayImage, display
            except ImportError:
                DisplayImage = None
                def display(value):
                    print(value)

            try:
                import google.colab  # noqa: F401
                IN_COLAB = True
            except ImportError:
                IN_COLAB = False

            if IN_COLAB:
                from google.colab import drive
                drive.mount('/content/drive')
                PROJECT_DIR = Path('/content/drive/MyDrive/reliable-reconstruction-under-mismatch')
            else:
                PROJECT_DIR = Path(os.environ.get('RRM_PROJECT_DIR', Path.cwd())).resolve()

            RESULTS_DIR = PROJECT_DIR / 'results'
            RESULTS_DIR.mkdir(parents=True, exist_ok=True)

            ANALYSIS_ARCHIVE_TEXT = os.environ.get('RRM_05E_ARCHIVE', '')  #@param {type:"string"}
            EXPECTED_ORIGINAL_05E_SHA256 = '6566319869d7b2c86902aa4f29d071c8a7bdbbce2bbe1b5a9649f4aaab690fa3'
            EXPECTED_GAP_MAP_SHA256 = '873701f82aed5cb244d222dbb9544fa3d6da5801c9e87ce350479106a9d6a5fb'
            EXPECTED_REVIEW_MATRIX_SHA256 = '3291b46520bcca12f0c1caf971fe9b0852ecf8e7662df453e7ed2b4a5bc4c5fd'
            LITERATURE_CUTOFF = '2026-09-15'
            PRIMARY_CHAIN = 'j75_b16_n2'

            def sha256_bytes(data):
                return hashlib.sha256(data).hexdigest()

            def sha256_file(path):
                digest = hashlib.sha256()
                with Path(path).open('rb') as handle:
                    for block in iter(lambda: handle.read(1024 * 1024), b''):
                        digest.update(block)
                return digest.hexdigest()

            def show_table(frame, rows=20):
                frame = frame.head(rows)
                try:
                    display(frame)
                except Exception:
                    print(frame.to_string(index=False))

            print(json.dumps({
                'in_colab': IN_COLAB,
                'project_dir': str(PROJECT_DIR),
                'literature_cutoff': LITERATURE_CUTOFF,
                'gpu_required': False,
            }, indent=2))
            """,
            cell_id="setup",
        ),
        markdown(
            """
            ## 2. Locate and fully validate the Stage-05E archive

            The validation is content-based. It supports both the original flat archive and a Drive
            wrapper ZIP containing an `independent_05e_locked_analysis/` top-level directory.
            """
        ),
        code(
            """
            def inspect_05e_archive(path):
                path = Path(path)
                result = {
                    'path': str(path),
                    'archive_sha256': sha256_file(path),
                    'archive_byte_count': path.stat().st_size,
                    'valid': False,
                }
                with zipfile.ZipFile(path) as archive:
                    bad_member = archive.testzip()
                    assert bad_member is None, f'CRC failure in {path.name}: {bad_member}'
                    names = set(archive.namelist())
                    manifest_members = [name for name in names if name.endswith('export_manifest.json')]
                    candidates = []
                    for member in manifest_members:
                        try:
                            manifest = json.loads(archive.read(member))
                        except Exception:
                            continue
                        if manifest.get('stage') == '05E_one_time_locked_analysis':
                            prefix = member[:-len('export_manifest.json')]
                            candidates.append((prefix, member, manifest))
                    assert len(candidates) == 1, f'Expected one Stage-05E manifest in {path.name}, found {len(candidates)}'
                    prefix, manifest_member, manifest = candidates[0]
                    checked = 0
                    for row in manifest['files']:
                        member = prefix + row['path']
                        assert member in names, f'Missing manifested member: {member}'
                        payload = archive.read(member)
                        assert len(payload) == int(row['byte_count']), f'Byte-count mismatch: {member}'
                        assert sha256_bytes(payload) == row['sha256'], f'SHA-256 mismatch: {member}'
                        checked += 1
                    status = json.loads(archive.read(prefix + 'status.json'))
                    primary = json.loads(archive.read(prefix + 'primary_hypotheses.json'))
                    checks = json.loads(archive.read(prefix + 'checks.json'))
                    receipt = json.loads(archive.read(prefix + 'unsealing_receipt.json'))
                    assert status['status'] == 'passed_one_time_locked_analysis'
                    assert status['independent_test_run_complete'] is True
                    assert status['independent_test_performance_inspected'] is True
                    assert status['unsealed'] is True
                    assert primary['experimental_novelty_gate_passed'] is False
                    assert checks['sources'] == 40 and checks['sealed_shards'] == 5
                    assert receipt['sealed_shards_verified_before_unsealing'] is True
                    assert receipt['test_performance_inspected_before_unsealing'] is False
                    result.update({
                        'valid': True,
                        'prefix': prefix,
                        'manifest_member': manifest_member,
                        'manifest_files_checked': checked,
                        'internal_manifest_sha256': sha256_bytes(archive.read(manifest_member)),
                    })
                return result

            if ANALYSIS_ARCHIVE_TEXT.strip():
                archive_candidates = [Path(ANALYSIS_ARCHIVE_TEXT).expanduser()]
            else:
                archive_candidates = sorted(RESULTS_DIR.rglob('independent_05e_locked_analysis*.zip'))
                archive_candidates += sorted((PROJECT_DIR / 'upload').glob('independent_05e_locked_analysis*.zip'))
                archive_candidates = list(dict.fromkeys(path.resolve() for path in archive_candidates if path.is_file()))

            assert archive_candidates, (
                'No Stage-05E ZIP found. Put the original independent_05e_locked_analysis_<timestamp>.zip '
                'inside the project results/ folder, or paste its complete path above.'
            )

            inspected_archives = []
            inspection_errors = []
            for candidate in archive_candidates:
                try:
                    inspected_archives.append(inspect_05e_archive(candidate))
                except Exception as error:
                    inspection_errors.append({'path': str(candidate), 'error': repr(error)})

            valid_archives = [row for row in inspected_archives if row['valid']]
            assert valid_archives, f'No valid Stage-05E archive. Errors: {inspection_errors}'
            originals = [row for row in valid_archives if row['archive_sha256'] == EXPECTED_ORIGINAL_05E_SHA256]
            if originals:
                selected_archive = originals[0]
            else:
                internal_hashes = {row['internal_manifest_sha256'] for row in valid_archives}
                assert len(internal_hashes) == 1, (
                    'Multiple non-equivalent valid 05E archives were found. Paste the intended full ZIP path above.'
                )
                selected_archive = valid_archives[0]

            ANALYSIS_ARCHIVE_05E = Path(selected_archive['path'])
            print(json.dumps({
                'selected_archive': str(ANALYSIS_ARCHIVE_05E),
                'outer_sha256': selected_archive['archive_sha256'],
                'is_original_notebook_zip': selected_archive['archive_sha256'] == EXPECTED_ORIGINAL_05E_SHA256,
                'manifest_files_checked': selected_archive['manifest_files_checked'],
                'content_equivalent_valid_archives_found': len(valid_archives),
            }, indent=2))
            """,
            cell_id="validate-05e",
        ),
        markdown(
            """
            ## 3. Load the locked results and literature snapshot

            The 90-study evidence snapshot is embedded in compressed canonical CSV form so Colab
            does not depend on Excel readers, network access, or a mutable external literature file.
            Its canonical SHA-256 is checked before use. The source workbook and gap-map hashes are
            recorded in the final receipt.
            """
        ),
        code(
            f"""
            LITERATURE_SNAPSHOT_GZIP_B64 = '''{encoded_snapshot}'''
            EXPECTED_LITERATURE_SNAPSHOT_SHA256 = '{snapshot_sha256}'
            EXPECTED_LITERATURE_STUDIES = {study_count}

            literature_csv_bytes = gzip.decompress(base64.b64decode(LITERATURE_SNAPSHOT_GZIP_B64))
            assert sha256_bytes(literature_csv_bytes) == EXPECTED_LITERATURE_SNAPSHOT_SHA256
            literature = pd.read_csv(io.BytesIO(literature_csv_bytes))
            assert len(literature) == EXPECTED_LITERATURE_STUDIES == 90
            assert (literature['Closest competitor'] == 'Yes').sum() == 62
            assert (literature['Peer reviewed'] == 'Yes').sum() == 81
            assert (literature['Inclusion decision'] == 'Include').all()

            with zipfile.ZipFile(ANALYSIS_ARCHIVE_05E) as archive:
                prefix = selected_archive['prefix']
                def read_json(name):
                    return json.loads(archive.read(prefix + name))
                def read_csv(name):
                    return pd.read_csv(io.BytesIO(archive.read(prefix + name)))

                STATUS_05E = read_json('status.json')
                CHECKS_05E = read_json('checks.json')
                PRIMARY_05E = read_json('primary_hypotheses.json')
                RECEIPT_05E = read_json('unsealing_receipt.json')
                QUALITY_05E = read_csv('quality_summary.csv')
                RISK_05E = read_csv('risk_summary.csv')
                CALIBRATION_METRICS_05E = read_csv('calibration_metrics.csv')
                CALIBRATION_BINS_05E = read_csv('calibration_bins.csv')
                SOURCE_MANIFEST_05E = read_csv('source_manifest.csv')

            assert SOURCE_MANIFEST_05E['source_id'].nunique() == 40
            assert not SOURCE_MANIFEST_05E['source_id'].duplicated().any()
            assert set(QUALITY_05E['chain_id']) == {{
                'q8_b16_n2', 'j90_b16_n2', 'j75_b12_n2', 'j75_b16_n2',
                'j75_b20_n2', 'j75_b16_n5', 'j50_b16_n2'
            }}

            literature_summary = pd.DataFrame([
                ('Studies in locked snapshot', len(literature)),
                ('Peer-reviewed studies', int((literature['Peer reviewed'] == 'Yes').sum())),
                ('Coded closest competitors', int((literature['Closest competitor'] == 'Yes').sum())),
                ('Studies with calibration = Yes', int((literature['Calibration'] == 'Yes').sum())),
                ('Studies with abstention = Yes', int((literature['Abstention'] == 'Yes').sum())),
                ('Studies with operator UQ = Yes', int((literature['Operator UQ'] == 'Yes').sum())),
            ], columns=['Literature audit item', 'Count'])
            show_table(literature_summary)
            """,
            cell_id="load-locked-inputs",
        ),
        markdown(
            """
            ## 4. Apply the fixed synthesis rules

            A confirmatory claim is retained only if its predeclared statistical and practical gates
            passed. Calibration cannot be claimed when the locked failure event has no positives.
            Secondary chain and risk-coverage patterns are descriptive and cannot rescue a failed
            confirmatory gate.
            """
        ),
        code(
            """
            h1 = PRIMARY_05E['hypotheses']['H1_reconstruction']
            h2 = PRIMARY_05E['hypotheses']['H2_selection']

            quality_pivot = QUALITY_05E.pivot(index='chain_id', columns='method', values='mean_detail_mse')
            chain_effects = quality_pivot[['dpir_nominal', 'fbcnn_dpir_nominal']].reset_index().rename(columns={
                'dpir_nominal': 'dpir_nominal_mean_detail_mse',
                'fbcnn_dpir_nominal': 'fbcnn_dpir_nominal_mean_detail_mse',
            })
            chain_effects.columns.name = None
            chain_effects['relative_detail_mse_reduction'] = (
                chain_effects['dpir_nominal_mean_detail_mse']
                - chain_effects['fbcnn_dpir_nominal_mean_detail_mse']
            ) / chain_effects['dpir_nominal_mean_detail_mse']
            chain_order = ['q8_b16_n2', 'j90_b16_n2', 'j75_b12_n2', 'j75_b16_n2', 'j75_b20_n2', 'j75_b16_n5', 'j50_b16_n2']
            chain_effects['chain_id'] = pd.Categorical(chain_effects['chain_id'], categories=chain_order, ordered=True)
            chain_effects = chain_effects.sort_values('chain_id').reset_index(drop=True)
            chain_effects['chain_role'] = np.where(
                chain_effects['chain_id'].astype(str).eq('q8_b16_n2'),
                'uncompressed control',
                'JPEG acquisition chain',
            )

            observed_bin_rates = CALIBRATION_BINS_05E['observed_bad_detail_rate'].dropna().to_numpy()
            zero_positive_events = bool(len(observed_bin_rates) and np.allclose(observed_bin_rates, 0.0))
            assert zero_positive_events, 'Locked calibration boundary changed unexpectedly.'

            primary_risk = RISK_05E[
                (RISK_05E['chain_id'] == PRIMARY_CHAIN)
                & (RISK_05E['pipeline'] == 'fbcnn_dpir_nominal')
                & (RISK_05E['region'] == 'all')
                & (RISK_05E['coverage'].isin([0.50, 0.75, 0.90, 1.00]))
                & (RISK_05E['score'].isin([
                    'oracle_detail_error',
                    'operator_spread_detail',
                    'image_transform_spread_detail',
                    'trained_image_only_patcherrornet_ensemble',
                    'expected_random',
                ]))
            ].copy()

            claims = pd.DataFrame([
                {
                    'claim_id': 'C1',
                    'claim': 'JPEG-aware deblocking before mismatch-aware DPIR improves detail fidelity under compressed acquisition-chain mismatch.',
                    'decision': 'SUPPORTED_WITHIN_LOCKED_SCOPE',
                    'basis': f"H1 passed: {100*h1['relative_reduction']:.2f}% reduction; Holm p={h1['holm_adjusted_p_value']:.6g}.",
                    'permitted_wording': 'Independently confirmed for the seven-chain locked experiment; describe the compressed-chain pattern and uncompressed control.',
                    'prohibited_wording': 'Do not call deblocking, DPIR, or their serial composition generally novel or universally superior.',
                },
                {
                    'claim_id': 'C2',
                    'claim': 'Operator-spread selection achieves the predeclared practical selective-risk advantage.',
                    'decision': 'NOT_ESTABLISHED',
                    'basis': f"Statistically detectable but {100*h2['relative_reduction']:.2f}% < {100*h2['practical_gate_threshold']:.0f}% practical threshold.",
                    'permitted_wording': 'Report a statistically detectable, subthreshold improvement and descriptive comparison with the learned comparator.',
                    'prohibited_wording': 'Do not claim the confirmatory selection gate passed; do not change the 5% threshold.',
                },
                {
                    'claim_id': 'C3',
                    'claim': 'The scores are calibrated for the locked bad-detail event.',
                    'decision': 'NOT_ESTIMABLE_FOR_POSITIVE_EVENTS',
                    'basis': 'All reliability bins had zero observed events for detail RMSE > 0.05 across 286,720 patch rows.',
                    'permitted_wording': 'State that the maps overpredicted the locked event and positive-event calibration could not be validated.',
                    'prohibited_wording': 'Do not claim calibrated failure probabilities or use point-estimate Brier rankings as formal superiority tests.',
                },
                {
                    'claim_id': 'C4',
                    'claim': 'The unified evidence-calibrated selective-reconstruction novelty claim is established.',
                    'decision': 'NOT_ESTABLISHED',
                    'basis': 'The combined experimental gate failed and the calibration target produced no positive events.',
                    'permitted_wording': 'Present the study as a rigorous acquisition-chain and reliability assessment with a transparent pivot.',
                    'prohibited_wording': 'Do not use first, uniquely reliable, fully calibrated, hallucination-free, or forensic recovery.',
                },
                {
                    'claim_id': 'C5',
                    'claim': 'A narrower acquisition-chain/reliability-assessment contribution is supportable.',
                    'decision': 'SUPPORTED_AS_PIVOT',
                    'basis': 'Strong H1, coherent compressed-versus-control pattern, complete held-out audit, and informative negative reliability boundaries.',
                    'permitted_wording': 'Emphasise what improved, where it improved, and which reliability claims did not survive.',
                    'prohibited_wording': 'Do not relabel the pivot as proof of the original unified architecture claim.',
                },
            ])

            assert h1['confirmatory_gate_passed'] is True
            assert h2['statistical_gate_passed'] is True
            assert h2['practical_gate_passed'] is False
            assert h2['confirmatory_gate_passed'] is False
            assert PRIMARY_05E['experimental_novelty_gate_passed'] is False
            assert (claims.loc[claims.claim_id == 'C4', 'decision'].iloc[0] == 'NOT_ESTABLISHED')

            decision_summary = pd.DataFrame([
                ('H1 reconstruction gate', 'PASS', f"{100*h1['relative_reduction']:.2f}% detail-MSE reduction"),
                ('H2 statistical gate', 'PASS', f"Holm p={h2['holm_adjusted_p_value']:.6g}"),
                ('H2 practical gate', 'FAIL', f"{100*h2['relative_reduction']:.2f}% versus 5% required"),
                ('Positive-event calibration', 'NOT ESTIMABLE', 'Zero locked bad-detail events'),
                ('Unified novelty claim', 'NOT ESTABLISHED', 'Combined gate did not pass'),
                ('Narrow acquisition-chain contribution', 'SUPPORTED', 'Proceed as transparent pivot'),
            ], columns=['Decision item', 'Outcome', 'Evidence'])
            show_table(decision_summary)
            """,
            cell_id="synthesis-rules",
        ),
        markdown(
            """
            ## 5. Inspect the descriptive robustness pattern

            The figure below is secondary evidence. It supports interpretation of H1 but does not
            replace or modify either confirmatory test.
            """
        ),
        code(
            """
            OUTPUT_DIR_05F = RESULTS_DIR / 'independent_05f_locked_synthesis'
            FIGURE_DIR_05F = OUTPUT_DIR_05F / 'figures'
            FIGURE_DIR_05F.mkdir(parents=True, exist_ok=True)

            plot_frame = chain_effects.copy()
            values = 100 * plot_frame['relative_detail_mse_reduction'].to_numpy()
            colors = ['#8c8c8c' if role == 'uncompressed control' else '#1769aa' for role in plot_frame['chain_role']]
            fig, ax = plt.subplots(figsize=(10.5, 5.6))
            bars = ax.bar(plot_frame['chain_id'].astype(str), values, color=colors, edgecolor='black', linewidth=0.5)
            ax.axhline(0, color='black', linewidth=1)
            ax.set_ylim(min(-10, float(values.min()) - 5), max(105, float(values.max()) + 5))
            ax.set_ylabel('Relative detail-MSE reduction (%)')
            ax.set_xlabel('Locked acquisition chain')
            ax.set_title('FBCNN + DPIR versus DPIR across the independent acquisition chains')
            ax.grid(axis='y', alpha=0.25)
            for bar, value in zip(bars, values):
                offset = 1.8 if value >= 0 else -1.5
                va = 'bottom' if value >= 0 else 'top'
                ax.text(bar.get_x() + bar.get_width()/2, value + offset, f'{value:.1f}%', ha='center', va=va, fontsize=9)
            from matplotlib.patches import Patch
            ax.legend(
                handles=[
                    Patch(facecolor='#8c8c8c', edgecolor='black', label='Uncompressed control'),
                    Patch(facecolor='#1769aa', edgecolor='black', label='JPEG acquisition chains'),
                ],
                loc='upper left',
                frameon=False,
            )
            fig.text(0.99, 0.01, 'Descriptive secondary analysis', ha='right', va='bottom', fontsize=8.5, color='#555555')
            fig.tight_layout()
            chain_figure_path = FIGURE_DIR_05F / 'independent_chain_reconstruction_effect.png'
            fig.savefig(chain_figure_path, dpi=180, bbox_inches='tight')
            plt.show()
            plt.close(fig)

            display_effects = chain_effects[['chain_id', 'chain_role', 'relative_detail_mse_reduction']].copy()
            display_effects['relative_detail_mse_reduction_percent'] = 100 * display_effects.pop('relative_detail_mse_reduction')
            show_table(display_effects, rows=10)
            """,
            cell_id="descriptive-robustness",
        ),
        markdown(
            """
            ## 6. Write the final synthesis package

            The generated package contains the claim table, exact input receipt, literature snapshot,
            manuscript-ready wording, checks, figure, status, and cryptographic export manifest.
            """
        ),
        code(
            """
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')

            nearest_competitors = literature[literature['Closest competitor'] == 'Yes'].copy()
            strongest_calibration_rows = CALIBRATION_METRICS_05E[
                (CALIBRATION_METRICS_05E['scope'] == 'all_chains')
                & (CALIBRATION_METRICS_05E['metric'] == 'source_macro_brier')
            ].sort_values('estimate').reset_index(drop=True)

            risk_50 = primary_risk[np.isclose(primary_risk['coverage'], 0.50)].set_index('score')['mean_detail_mse']
            required_scores = {
                'oracle_detail_error', 'operator_spread_detail', 'image_transform_spread_detail',
                'trained_image_only_patcherrornet_ensemble', 'expected_random'
            }
            assert required_scores.issubset(set(risk_50.index))

            literature_boundary = {
                'cutoff_date': LITERATURE_CUTOFF,
                'studies': int(len(literature)),
                'peer_reviewed': int((literature['Peer reviewed'] == 'Yes').sum()),
                'closest_competitors': int((literature['Closest competitor'] == 'Yes').sum()),
                'source_gap_map_sha256': EXPECTED_GAP_MAP_SHA256,
                'source_review_matrix_sha256': EXPECTED_REVIEW_MATRIX_SHA256,
                'embedded_canonical_snapshot_sha256': EXPECTED_LITERATURE_SNAPSHOT_SHA256,
                'boundary_statement': (
                    'The broad ideas of physics-informed mismatch handling, blind image/operator inference, '
                    'all-in-one restoration, diffusion priors, and uncertainty alone are already occupied. '
                    'The original unified evidence-calibrated selective-reconstruction claim is not established '
                    'by Experiment 05 because its combined gate did not pass.'
                ),
            }

            synthesis_decision = {
                'stage': '05F_locked_literature_and_experimental_synthesis',
                'status': 'completed_locked_synthesis',
                'experiment_id': 'independent_05',
                'completed_at_utc': datetime.now(timezone.utc).isoformat(),
                'independent_evaluation_complete': True,
                'literature_synthesis_complete': True,
                'experimental_novelty_gate_passed': False,
                'final_literature_novelty_claim_established': False,
                'original_unified_claim_retained': False,
                'narrow_acquisition_chain_contribution_supported': True,
                'recommended_pivot': 'acquisition_chain_and_reliability_assessment',
                'h1_reconstruction': h1,
                'h2_selection': h2,
                'calibration_boundary': {
                    'locked_event': 'centre 16x16 patch detail RMSE > 0.05',
                    'patch_rows': int(CHECKS_05E['calibration_patch_rows']),
                    'observed_positive_events_in_reliability_bins': 0,
                    'positive_event_calibration_estimable': False,
                    'interpretation': 'The maps overpredicted this event; positive-event calibration was not validated.',
                },
                'literature_boundary': literature_boundary,
                'next_stage': 'manuscript_and_repository_checkpoint',
            }

            input_receipt = {
                'stage_05e_archive_path': str(ANALYSIS_ARCHIVE_05E),
                'stage_05e_outer_sha256': selected_archive['archive_sha256'],
                'stage_05e_expected_original_outer_sha256': EXPECTED_ORIGINAL_05E_SHA256,
                'stage_05e_is_original_notebook_zip': selected_archive['archive_sha256'] == EXPECTED_ORIGINAL_05E_SHA256,
                'stage_05e_internal_manifest_sha256': selected_archive['internal_manifest_sha256'],
                'stage_05e_manifest_files_checked': int(selected_archive['manifest_files_checked']),
                'stage_05e_sources': int(CHECKS_05E['sources']),
                'stage_05e_sealed_shards': int(CHECKS_05E['sealed_shards']),
                'literature_boundary': literature_boundary,
            }

            manuscript_text = f'''# Locked literature and experimental synthesis

## Scope

This synthesis uses the one-time independent analysis of 40 sealed sources across seven acquisition chains and the literature snapshot locked to 15 September 2026. No post-test threshold, endpoint, method, or hypothesis was changed.

## Confirmatory reconstruction result

On the primary JPEG chain (`{PRIMARY_CHAIN}`), FBCNN preprocessing followed by nominal DPIR reduced source-level detail MSE by **{100*h1['relative_reduction']:.2f}%** relative to nominal DPIR alone. The mean paired difference was {h1['mean_difference']:.9g}, with a 95% source-bootstrap interval of [{h1['paired_source_bootstrap_95_ci'][0]:.9g}, {h1['paired_source_bootstrap_95_ci'][1]:.9g}] and Holm-adjusted one-sided p = {h1['holm_adjusted_p_value']:.6g}. The predeclared reconstruction gate passed.

The secondary chain analysis was directionally coherent: the serial FBCNN+DPIR pipeline improved detail MSE on every JPEG chain, while the uncompressed control changed by {100*chain_effects.loc[chain_effects['chain_id'].astype(str).eq('q8_b16_n2'), 'relative_detail_mse_reduction'].iloc[0]:.2f}%. This pattern supports an acquisition-chain interpretation rather than a universal advantage.

## Confirmatory selection result

At 50% coverage on the primary chain, operator-spread selection reduced source retained-patch detail risk by **{100*h2['relative_reduction']:.2f}%** relative to image-transform spread. The paired 95% bootstrap interval for the absolute difference was [{h2['paired_source_bootstrap_95_ci'][0]:.9g}, {h2['paired_source_bootstrap_95_ci'][1]:.9g}], and the Holm-adjusted one-sided p-value was {h2['holm_adjusted_p_value']:.6g}. The statistical gate passed, but the predeclared 5% practical gate did not; therefore the confirmatory selection claim was not established.

Descriptively, the 50%-coverage detail risks were {risk_50['oracle_detail_error']:.9g} for the oracle, {risk_50['operator_spread_detail']:.9g} for operator spread, {risk_50['image_transform_spread_detail']:.9g} for image-transform spread, {risk_50['trained_image_only_patcherrornet_ensemble']:.9g} for the trained PatchErrorNet ensemble, and {risk_50['expected_random']:.9g} for random retention. These comparisons are secondary and do not override the failed practical gate.

## Calibration boundary

Across {CHECKS_05E['calibration_patch_rows']:,} calibration patch rows, no reliability-bin event exceeded the locked threshold of centre-patch detail RMSE > 0.05. Consequently, positive-event calibration and discrimination could not be validated. The non-zero predicted probabilities indicate overprediction of this locked failure event. Brier-score rankings are descriptive only because no formal pairwise calibration comparison was predeclared.

## Literature boundary and final claim decision

The locked evidence snapshot contains {len(literature)} studies, including {(literature['Peer reviewed'] == 'Yes').sum()} peer-reviewed works and {(literature['Closest competitor'] == 'Yes').sum()} coded closest competitors. It establishes that physics-informed mismatch handling, blind image/operator inference, all-in-one restoration, diffusion priors, and uncertainty estimation are not individually novel.

Because the combined experimental novelty gate did not pass, the original unified evidence-calibrated selective-reconstruction novelty claim is **not established**. The supportable contribution is narrower: an independently audited demonstration that JPEG-aware deblocking can substantially improve detail fidelity before mismatch-aware DPIR on compressed acquisition chains, together with a transparent reliability assessment showing that operator-spread selection was statistically detectable but practically subthreshold and that the locked calibration event was too rare to validate.

## Permitted claim

> In the locked independent experiment, JPEG-aware deblocking before mismatch-aware DPIR produced large detail-fidelity gains across compressed acquisition chains, while offering no benefit on the uncompressed control. Operator-spread uncertainty yielded a statistically detectable but subthreshold selective-risk improvement, and positive-event calibration could not be established at the predeclared failure threshold.

## Prohibited claims

- first physics-informed reconstruction method robust to mismatch;
- first blind or joint image/operator reconstruction system;
- fully calibrated uncertainty or guaranteed abstention;
- hallucination-free or forensic recovery;
- practical superiority of operator-spread selection under the predeclared 5% gate.

## Recommended paper direction

Proceed as an acquisition-chain and reliability-assessment paper or a rigorous benchmark/protocol contribution. Preserve the negative H2 practical-gate result and calibration boundary as central findings. A future confirmatory study may define a better-powered failure event and broader real-device transfer protocol, but it must be preregistered and reported as a new experiment.
'''

            status_05f = {
                'stage': '05F_locked_literature_and_experimental_synthesis',
                'status': 'completed_locked_synthesis',
                'experiment_id': 'independent_05',
                'final_literature_novelty_claim_established': False,
                'original_unified_claim_retained': False,
                'narrow_acquisition_chain_contribution_supported': True,
                'recommended_pivot': 'acquisition_chain_and_reliability_assessment',
                'next_stage': 'manuscript_and_repository_checkpoint',
                'updated_at_utc': datetime.now(timezone.utc).isoformat(),
            }

            checks_05f = {
                'stage_05e_archive_crc_passed': True,
                'stage_05e_manifest_files_checked': int(selected_archive['manifest_files_checked']),
                'stage_05e_sources': int(CHECKS_05E['sources']),
                'stage_05e_chains': int(CHECKS_05E['chains']),
                'literature_rows': int(len(literature)),
                'literature_closest_competitors': int((literature['Closest competitor'] == 'Yes').sum()),
                'claims': int(len(claims)),
                'h1_gate_passed': bool(h1['confirmatory_gate_passed']),
                'h2_statistical_gate_passed': bool(h2['statistical_gate_passed']),
                'h2_practical_gate_passed': bool(h2['practical_gate_passed']),
                'zero_positive_calibration_events': bool(zero_positive_events),
                'final_unified_claim_established': False,
            }

            (OUTPUT_DIR_05F / 'literature_snapshot.csv').write_bytes(literature_csv_bytes)
            nearest_competitors.to_csv(OUTPUT_DIR_05F / 'nearest_competitors.csv', index=False)
            chain_effects.to_csv(OUTPUT_DIR_05F / 'secondary_chain_effects.csv', index=False)
            primary_risk.to_csv(OUTPUT_DIR_05F / 'primary_risk_coverage.csv', index=False)
            strongest_calibration_rows.to_csv(OUTPUT_DIR_05F / 'calibration_brier_point_estimates.csv', index=False)
            claims.to_csv(OUTPUT_DIR_05F / 'claim_decisions.csv', index=False)
            (OUTPUT_DIR_05F / 'manuscript_results.md').write_text(manuscript_text, encoding='utf-8')
            (OUTPUT_DIR_05F / 'synthesis_decision.json').write_text(json.dumps(synthesis_decision, indent=2), encoding='utf-8')
            (OUTPUT_DIR_05F / 'input_receipt.json').write_text(json.dumps(input_receipt, indent=2), encoding='utf-8')
            (OUTPUT_DIR_05F / 'checks.json').write_text(json.dumps(checks_05f, indent=2), encoding='utf-8')
            (OUTPUT_DIR_05F / 'status.json').write_text(json.dumps(status_05f, indent=2), encoding='utf-8')

            manifest_files = []
            for path in sorted(OUTPUT_DIR_05F.rglob('*')):
                if path.is_file() and path.name != 'export_manifest.json':
                    manifest_files.append({
                        'path': path.relative_to(OUTPUT_DIR_05F).as_posix(),
                        'byte_count': path.stat().st_size,
                        'sha256': sha256_file(path),
                    })
            export_manifest = {
                'stage': '05F_locked_literature_and_experimental_synthesis',
                'status': 'completed_locked_synthesis',
                'experiment_id': 'independent_05',
                'files': manifest_files,
            }
            (OUTPUT_DIR_05F / 'export_manifest.json').write_text(json.dumps(export_manifest, indent=2), encoding='utf-8')

            archive_path = OUTPUT_DIR_05F.parent / f'{OUTPUT_DIR_05F.name}_{timestamp}.zip'
            temporary_archive = archive_path.with_suffix('.zip.partial')
            with zipfile.ZipFile(temporary_archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
                for path in sorted(OUTPUT_DIR_05F.rglob('*')):
                    if path.is_file():
                        archive.write(path, arcname=f'{OUTPUT_DIR_05F.name}/{path.relative_to(OUTPUT_DIR_05F).as_posix()}')
            temporary_archive.replace(archive_path)

            with zipfile.ZipFile(archive_path) as archive:
                assert archive.testzip() is None
            for row in export_manifest['files']:
                path = OUTPUT_DIR_05F / row['path']
                assert path.stat().st_size == row['byte_count']
                assert sha256_file(path) == row['sha256']

            print(json.dumps({
                'stage': status_05f['stage'],
                'status': status_05f['status'],
                'final_literature_novelty_claim_established': False,
                'narrow_acquisition_chain_contribution_supported': True,
                'recommended_pivot': status_05f['recommended_pivot'],
                'output_directory': str(OUTPUT_DIR_05F),
                'archive_path': str(archive_path),
                'archive_sha256': sha256_file(archive_path),
                'manifested_files': len(export_manifest['files']),
            }, indent=2))
            """,
            cell_id="write-package",
        ),
        markdown(
            """
            ## 7. Final decision and handoff

            The table is the locked reporting boundary. A `NOT_ESTABLISHED` result is not an error
            and must not be converted into a pass by changing the practical threshold, the event
            definition, the comparison, or the reporting population.
            """
        ),
        code(
            """
            show_table(claims[['claim_id', 'decision', 'claim', 'basis']], rows=10)
            print()
            print('FINAL PERMITTED CLAIM:')
            print()
            permitted_section = manuscript_text.split('## Permitted claim', 1)[1].split('## Prohibited claims', 1)[0].strip()
            print(permitted_section)
            print()
            print('UPLOAD/ARCHIVE THIS ZIP:', archive_path)
            print('ZIP SHA-256:', sha256_file(archive_path))
            print('ALSO DOWNLOAD THIS EXECUTED NOTEBOOK: File > Download > Download .ipynb')
            """,
            cell_id="handoff",
        ),
    ]

    notebook = {
        "cells": cells,
        "metadata": {
            "colab": {
                "name": OUTPUT_PATH.name,
                "provenance": [],
            },
            "experiment": {
                "experiment_id": "independent_05",
                "stage": "05F_locked_literature_and_experimental_synthesis",
                "literature_cutoff": "2026-09-15",
                "post_test_tuning_permitted": False,
            },
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.x",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(OUTPUT_PATH)
    print(f"cells={len(cells)}")
    print(f"literature_snapshot_sha256={snapshot_sha256}")


if __name__ == "__main__":
    main()
