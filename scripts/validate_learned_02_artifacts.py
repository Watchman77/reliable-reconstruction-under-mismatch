"""Read back Learned 02 canary artifacts; do not run or retune the model."""
import ast
import hashlib
import importlib.util
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import nbformat
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / 'experiments/learned_02'
OUT = EXP / 'outputs/canary_20260917'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    nbpath = ROOT / 'notebooks/02_DIV2K_Learned_Baseline.ipynb'
    nb = nbformat.read(nbpath, as_version=4)
    nbformat.validate(nb)
    cells = [c for c in nb.cells if c.cell_type == 'code']
    assert len(cells) == 9
    assert [c.execution_count for c in cells] == list(range(1,10))
    assert not any(o.output_type == 'error' for c in cells for o in c.outputs)
    figures = sum('image/png' in o.get('data',{}) for c in cells for o in c.outputs)
    assert figures == 4
    assert nb.metadata.validation.status == 'executed_inprocess_with_display_readback'
    assert 'One development source' in nb.metadata.validation.scope
    assert nb.metadata.learned_source_sha256 == sha(EXP/'learned.py')
    assert nb.metadata.baseline_source_sha256 == sha(ROOT/'experiments/baseline_01/baseline.py')
    definitions = lambda text: {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
    expected = definitions((EXP/'learned.py').read_text())
    actual = definitions('\n\n'.join(c.source for c in cells))
    assert expected == actual, 'Embedded adapter functions differ from module'
    literal = ast.parse(cells[1].source)
    literals = {n.targets[0].id: ast.literal_eval(n.value) for n in literal.body[:4]}
    assert literals['BASELINE_SOURCE'] == (ROOT/'experiments/baseline_01/baseline.py').read_text()
    for relative, expected_hash in literals['PROVENANCE']['files'].items():
        assert hashlib.sha256(literals['VENDOR_SOURCES'][relative].encode()).hexdigest() == expected_hash
        assert sha(EXP/'vendor/dpir'/relative) == expected_hash

    manifest = json.loads((OUT/'export_manifest.json').read_text())['files']
    actual_files = {str(p.relative_to(OUT)) for p in OUT.rglob('*') if p.is_file() and p.name != 'export_manifest.json'}
    assert {r['name'] for r in manifest} == actual_files
    assert len(manifest) == 16
    for row in manifest:
        p = OUT / row['name']
        assert p.stat().st_size == row['bytes'] and sha(p) == row['sha256']
    status = json.loads((OUT/'status.json').read_text())
    assert status['status'] == 'complete_for_configured_subset'
    assert status['completed_observations'] == status['planned_observations'] == 1
    cfg = json.loads((OUT/'config.json').read_text())
    assert cfg['source_ids'] == ['0801'] and cfg['scenarios'] == ['blur_noise']
    assert cfg['iterations'] == 8 and cfg['crop_size'] == 512 and cfg['context_border'] == 32
    quality = pd.read_csv(OUT/'quality.csv',dtype={'source_id':str})
    summary = pd.read_csv(OUT/'summary.csv')
    curves = pd.read_csv(OUT/'curves.csv')
    compute = pd.read_csv(OUT/'compute.csv')
    trajectories = pd.read_csv(OUT/'trajectories.csv')
    assert len(quality)==5 and len(summary)==5 and len(curves)==56 and len(compute)==8 and len(trajectories)==48
    assert compute.denoiser_calls.sum()==49
    assert np.isfinite(quality[['mse','psnr_db','detail_mse']]).all().all()
    assert np.allclose(quality.psnr_db, -10*np.log10(quality.mse),rtol=0,atol=1e-10)
    assert np.allclose(summary.pooled_psnr_db,-10*np.log10(summary.mean_mse),rtol=0,atol=1e-10)
    joined = summary.merge(quality,on=['model','scenario'])
    assert np.allclose(joined.mean_mse,joined.mse,rtol=0,atol=1e-16)
    assert np.allclose(joined.mean_detail_mse,joined.detail_mse,rtol=0,atol=1e-16)
    for _, group in curves.groupby('region'):
        endpoints = group[group.coverage == 1]
        for col in ['rgb_mse','detail_mse','bad_detail_rate_0.025','bad_detail_rate_0.05','bad_detail_rate_0.1']:
            assert np.ptp(endpoints[col]) < 1e-12
    assert (curves['bad_detail_rate_0.025'] >= curves['bad_detail_rate_0.05']).all()
    assert (curves['bad_detail_rate_0.05'] >= curves['bad_detail_rate_0.1']).all()

    # Classical anchor values must equal Baseline 01's already-saved condition.
    old = ROOT/'experiments/baseline_01/outputs/run_20260917'
    controls = pd.read_csv(old/'controls.csv',dtype={'source_id':str})
    selected = pd.read_csv(old/'selected.csv',dtype={'source_id':str})
    def anchor(table):
        return table[(table.source_id=='0801') & (table.scenario=='blur_noise') &
                     (table.true_sigma==1.6) & np.isclose(table.noise_std,2/255)]
    old_input = float(anchor(controls).query("model == 'observed'").mse.iloc[0])
    old_gradient = float(anchor(selected).query("model == 'gradient' and operator_info == 'nominal'").mse.iloc[0])
    assert abs(float(quality.query("model == 'observed'").mse.iloc[0])-old_input)<1e-14
    assert abs(float(quality.query("model == 'gradient_nominal'").mse.iloc[0])-old_gradient)<1e-14

    # Independently read the nominal image and recover its image/patch errors.
    b = module(ROOT/'experiments/baseline_01/baseline.py','baseline01_audit')
    data_dir = Path(os.environ.get('IMAGING02_DATA_DIR', str(ROOT.parent/'imaging_inputs')))
    sources, _ = b.load_sources(data_dir,literals['EXPECTED_RGB_HASHES'],cfg)
    truth = sources['0801']
    with np.load(OUT/'predictions/0801_blur_noise.npz',allow_pickle=False) as saved:
        pred = saved['nominal_reconstruction'].astype(np.float64)
        assert pred.shape == truth.shape == (576,576,3)
        squared = (pred[32:-32,32:-32]-truth[32:-32,32:-32])**2
        rgb = squared.mean(axis=2).reshape(32,16,32,16).mean(axis=(1,3)).ravel()
        dp = pred-b.apply(pred,1.0)
        dt = truth-b.apply(truth,1.0)
        detail = ((dp[32:-32,32:-32]-dt[32:-32,32:-32])**2).mean(axis=2).reshape(32,16,32,16).mean(axis=(1,3)).ravel()
        assert np.allclose(rgb,saved['rgb_patch_error'],rtol=0,atol=1e-15)
        assert np.allclose(detail,saved['detail_patch_error'],rtol=0,atol=1e-15)
        row=quality.query("model == 'dpir_nominal'").iloc[0]
        assert abs(row.mse-rgb.mean())<1e-15 and abs(row.detail_mse-detail.mean())<1e-15
        for region, ids in [('all',np.arange(1024)),('textured_quartile',np.argsort(saved['reference_texture'],kind='stable')[-256:])]:
            for name in ['operator_spread_detail','image_transform_spread_detail','operator_spread_rgb','measurement_residual','image_gradient']:
                tie = np.random.default_rng(82).random(len(ids))
                order = np.lexsort((tie,saved[name][ids]))
                for coverage in [.5,.75,.9,1.]:
                    chosen = ids[order[:int(np.ceil(coverage*len(ids)))]]
                    row=curves[(curves.region==region)&(curves.score==name)&(curves.coverage==coverage)].iloc[0]
                    assert abs(row.detail_mse-detail[chosen].mean())<1e-15
                    assert abs(row.rgb_mse-rgb[chosen].mean())<1e-15
                    for tolerance in [.025,.05,.10]:
                        assert abs(row[f'bad_detail_rate_{tolerance:g}']-(np.sqrt(detail[chosen])>tolerance).mean())<1e-12
    audit=dict(audited_utc=datetime.now(timezone.utc).isoformat(),status='passed',
        scope='0801, linear anchor only; eight-observation Colab experiment pending',
        notebook_sha256=sha(nbpath),notebook_code_cells=9,embedded_figures=figures,presentation_cells_replayed=[8,9],
        error_outputs=0,adapter_functions_identical=True,upstream_files_and_license_verified=True,
        exported_files_verified=len(manifest),manifest_covers_all_outputs=True,
        quality_rows=5,risk_rows=56,trajectory_rows=48,experiment_denoiser_calls=49,
        learned_validation_calls=2,dense_hqs_max_abs_error=json.loads((OUT/'checks.json').read_text())['dense_hqs_max_abs_error'],
        baseline01_classical_anchor_reproduced=True,saved_prediction_and_patch_errors_reconcile=True,
        saved_score_rankings_and_bad_detail_rates_reconcile=True,full_run_complete=False,
        colab_drive_gpu_validation='pending')
    (EXP/'validation.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit,indent=2))

if __name__=='__main__':main()
