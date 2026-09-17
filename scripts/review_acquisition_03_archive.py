"""Reproduce Acquisition 03 transfer, raw-output and evidence verification.

Requires the five uploaded transfer ZIPs, executed Notebook 03 and source PNGs.
No learned model inference. Evidence is written separately from original outputs.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import zipfile

import numpy as np
import pandas as pd
from PIL import Image
from package_acquisition_03_archive import verify_parts, sha256_file


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parts-dir', type=Path, required=True)
    parser.add_argument('--notebook', type=Path, required=True)
    parser.add_argument('--data-dir', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, required=True)
    parser.add_argument('--evidence-dir', type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    work, evidence = args.work_dir, args.evidence_dir
    work.mkdir(parents=True, exist_ok=True)
    evidence.mkdir(parents=True, exist_ok=True)
    notebook = json.loads(args.notebook.read_text())
    last = next(c for c in reversed(notebook['cells']) if c['cell_type'] == 'code')
    stdout = ''.join(''.join(o.get('text', [])) for o in last.get('outputs', []))
    receipt, _ = json.JSONDecoder().raw_decode(stdout.lstrip())
    expected_name = 'acquisition_03_20260917T160754_303637Z.zip'
    expected_sha = '902cee988b76eb982efb068eca4c821d0259b4ef06d6c6f0d09163d1117549dc'
    assert receipt['zip_name'] == expected_name
    assert receipt['zip_bytes'] == 431278719 and receipt['zip_sha256'] == expected_sha
    assert receipt['configured_observations'] == 16 and receipt['full_design_complete']
    parts = [args.parts_dir / f'acquisition03_transfer_part_{i:02d}_of_05.zip' for i in range(1, 6)]
    part_records = []
    for index, part in enumerate(parts, 1):
        with zipfile.ZipFile(part) as archive:
            metadata = json.loads(archive.read('transfer_part.json'))
        assert metadata['part_index'] == index and metadata['part_count'] == 5
        assert metadata['archive_name'] == expected_name
        assert metadata['archive_sha256'] == expected_sha
        assert metadata['archive_bytes'] == receipt['zip_bytes']
        part_records.append(dict(filename=part.name, bytes=part.stat().st_size,
                                 sha256=sha256_file(part), metadata=metadata))
    archive_path = work / expected_name
    if archive_path.exists():
        assert archive_path.stat().st_size == receipt['zip_bytes']
        assert sha256_file(archive_path) == expected_sha
        transfer = verify_parts(parts)
    else:
        transfer = verify_parts(parts, archive_path)
    assert transfer['archive_sha256'] == expected_sha
    write_json(evidence / 'transfer_validation.json', dict(**transfer, parts=part_records))
    origin = dict(receipt_source='JSON parsed from final saved code-cell stdout of uploaded Notebook 03; not the separately retrieved Drive receipt',
                  notebook_filename=args.notebook.name, notebook_sha256=sha256_file(args.notebook))
    write_json(evidence / 'receipt_origin.json', origin)
    write_json(evidence / 'notebook_recorded_zip_receipt.json', receipt)
    # The existing independent validator expects this sibling receipt pathname.
    # The separate origin record explicitly identifies its notebook source.
    write_json(archive_path.with_suffix('.receipt.json'), receipt)
    run = work / archive_path.stem
    file_records = []
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names))
        for name in names:
            path = PurePosixPath(name)
            assert not path.is_absolute() and '..' not in path.parts
            assert path.parts[0] == archive_path.stem
        manifest = json.loads(archive.read(archive_path.stem + '/export_manifest.json'))
        files = {row['name']: row for row in manifest['files']}
        assert len(files) == len(manifest['files']) == 38
        assert set(names) == {archive_path.stem + '/' + n for n in files} | {archive_path.stem + '/export_manifest.json'}
        for name in names:
            data = archive.read(name)  # A complete read also validates entry CRC.
            relative = str(PurePosixPath(name).relative_to(archive_path.stem))
            digest = hashlib.sha256(data).hexdigest()
            if relative != 'export_manifest.json':
                assert len(data) == files[relative]['bytes']
                assert digest == files[relative]['sha256']
            destination = work / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                assert destination.read_bytes() == data
            else:
                destination.write_bytes(data)
            file_records.append(dict(name=relative, bytes=len(data), sha256=digest,
                                     manifest_match=relative != 'export_manifest.json'))
    write_json(evidence / 'file_verification.json', file_records)
    audit_path = evidence / 'raw_prediction_validation.json'
    subprocess.run([sys.executable, str(repo / 'scripts/validate_acquisition_03.py'),
                    '--run-dir', str(run), '--data-dir', str(args.data_dir),
                    '--audit-output', str(audit_path)], check=True)
    audit = json.loads(audit_path.read_text())
    assert audit['observations'] == 16 and audit['independently_recomputed_quality_rows'] == 80

    previous = repo / 'experiments/acquisition_03/colab_review_20260917'
    csv_names = sorted(p.name for p in run.glob('*.csv'))
    assert len(csv_names) == 9
    for name in csv_names:
        assert (run / name).read_bytes() == (previous / 'csv_exports' / name).read_bytes()
    figure_names = sorted(p.name for p in run.glob('*.png'))
    assert len(figure_names) == 4
    for name in figure_names:
        assert (run / name).read_bytes() == (previous / 'embedded_figures' / name).read_bytes()
    metadata_dir = evidence / 'run_metadata'
    metadata_dir.mkdir(exist_ok=True)
    for path in run.glob('*.json'):
        shutil.copyfile(path, metadata_dir / path.name)
    cfg = json.loads((run / 'config.json').read_text())
    assert cfg['source_ids'] == ['0801', '0802', '0803', '0804']
    models = ['observed', 'gradient_nominal', 'drunet_denoise_only', 'dpir_nominal', 'dpir_oracle_blur']
    keys = {'supplied_observation'} | set(models) | {m + suffix for m in models for suffix in ['__rgb_patch_error', '__detail_patch_error']}
    acquisition = pd.read_csv(run / 'acquisition.csv', dtype={'source_id': str})
    for sid in cfg['source_ids']:
        for stage in cfg['acquisition_stages']:
            with np.load(run / 'predictions' / f'{sid}_{stage}.npz', allow_pickle=False) as saved:
                assert set(saved.files) == keys
                assert saved['supplied_observation'].shape == (576, 576, 3)
                assert np.isfinite(saved['supplied_observation']).all()
                assert np.array_equal(saved['observed'], np.clip(saved['supplied_observation'], 0, 1))
                for model in models:
                    for suffix in ['__rgb_patch_error', '__detail_patch_error']:
                        assert saved[model + suffix].shape == (1024,)
            if stage == 'jpeg_q75':
                row = acquisition.query('source_id == @sid and stage == @stage').iloc[0]
                jpeg = run / 'codec_inputs' / f'{sid}_q75.jpg'
                assert jpeg.stat().st_size == row.jpeg_bytes
                assert sha256_file(jpeg) == row.jpeg_sha256
    provenance = json.loads((run / 'provenance.json').read_text())
    sources = dict(baseline_helper_sha256='experiments/baseline_01/baseline.py',
                   adapter_source_sha256='experiments/learned_02/learned.py',
                   diagnostic_source_sha256='experiments/acquisition_03/diagnostic.py',
                   design_freeze_sha256='experiments/acquisition_03/design_freeze.md')
    for key, relative in sources.items():
        assert sha256_file(repo / relative) == provenance[key]
    write_json(evidence / 'supplementary_checks.json', dict(
        csv_files_byte_identical_to_prior_review=csv_names,
        raw_figures_byte_identical_to_notebook_embeds=figure_names,
        exact_npz_schemas_verified=16, full_patch_vector_shapes_verified=160,
        input_control_equals_clipped_observation=16, jpeg_hashes_match_acquisition_table=4,
        project_source_and_design_hashes_verified=sources,
        saved_learned_predictions_recomputed=48, saved_control_predictions_recomputed=32,
        full_coverage_tail_rates_recomputed=240, learned_inference_repeated=False))

    # Fixed central insets on all four sources; no outcome-based region selection.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    source_rows = pd.read_csv(run / 'source_manifest.csv', dtype={'source_id': str}).set_index('source_id')
    fig, axes = plt.subplots(4, 5, figsize=(13, 10.8))
    columns = [('Reference', None, None), ('Classical\n8-bit input', 'quantized_8bit', 'gradient_nominal'),
               ('Nominal DPIR\n8-bit input', 'quantized_8bit', 'dpir_nominal'),
               ('Classical\nJPEG Q75 input', 'jpeg_q75', 'gradient_nominal'),
               ('Nominal DPIR\nJPEG Q75 input', 'jpeg_q75', 'dpir_nominal')]
    for i, sid in enumerate(cfg['source_ids']):
        row = source_rows.loc[sid]
        with Image.open(args.data_dir / row.filename) as image:
            rgb = np.asarray(image.convert('RGB'))
        top, left, extent = int(row.crop_top), int(row.crop_left), int(row.extent)
        truth = rgb[top:top + extent, left:left + extent].astype(float) / 255
        for j, (label, stage, model) in enumerate(columns):
            if stage is None:
                pixels = truth
            else:
                with np.load(run / 'predictions' / f'{sid}_{stage}.npz', allow_pickle=False) as saved:
                    pixels = saved[model]
            axes[i, j].imshow(pixels[160:416, 160:416], interpolation='nearest')
            axes[i, j].set_xticks([]); axes[i, j].set_yticks([])
            if i == 0: axes[i, j].set_title(label, fontsize=11)
            if j == 0: axes[i, j].set_ylabel('Source ' + sid, fontsize=11)
    fig.suptitle('Raw prediction readback: fixed central insets on all four development sources\n256 x 256 shown; numerical metrics use the full 512 x 512 evaluation region', fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, .94))
    fig.savefig(evidence / 'all_sources_codec_readback.png', dpi=130)
    plt.close(fig)
    print('PASS: complete raw archive audit and supporting evidence written.')


if __name__ == '__main__':
    main()
