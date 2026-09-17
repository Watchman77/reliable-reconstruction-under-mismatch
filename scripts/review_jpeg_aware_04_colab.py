"""Audit Notebook 04 and readable exports; does NOT validate learned raw arrays.

Requires the original uploaded notebook, issued notebook, review evidence directory,
repository (for the official source manifest and historical anchors), and source PNGs.
No neural inference or input modification is performed.
"""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path

import nbformat
import numpy as np
import pandas as pd
from PIL import Image


def digest(data):
    return hashlib.sha256(data).hexdigest()


def review(notebook, issued_notebook, out, repo, data):
    out, repo, data = map(Path, (out, repo, data))
    nb = nbformat.read(notebook, 4)
    issued = nbformat.read(issued_notebook, 4)
    nbformat.validate(nb)
    assert len(nb.cells) == len(issued.cells) == 23
    assert all(a.cell_type == b.cell_type and a.source == b.source for a, b in zip(nb.cells, issued.cells))
    code = [c for c in nb.cells if c.cell_type == 'code']
    counts = [c.execution_count for c in code]
    assert len(code) == 11 and all(c.outputs for c in code)
    assert all(isinstance(c, int) and c > 0 for c in counts)
    assert not any(o.output_type == 'error' for c in code for o in c.outputs)
    assert not any(o.output_type == 'stream' and o.name == 'stderr' for c in code for o in c.outputs)
    for i, name in [(7,'checks'),(9,'independent_readback'),(19,'decisions')]:
        text=''.join(o.text for o in nb.cells[i].outputs if o.output_type=='stream')
        saved,_=json.JSONDecoder().raw_decode(text[text.index('{'):])
        exported=json.loads((out/(name+'.json')).read_text())
        # Cell 9 adds this flag after the cell 7 checks were printed.
        if name=='checks':
            assert exported.pop('independent_readback_passed') is True
        assert saved==exported, name
    provenance=json.loads((out/'provenance.json').read_text())
    assert provenance['design_freeze_sha256']==digest((repo/'experiments/jpeg_aware_04/design_freeze.md').read_bytes())
    manifest = json.loads((out/'export_manifest.json').read_text())
    listed = {r['name']: r for r in manifest['files']}
    assert len(listed) == len(manifest['files']) == 37
    verified = []
    for name, row in listed.items():
        path = out/'csv_exports'/name if name.endswith('.csv') else out/name
        if not path.is_file():
            continue
        raw = path.read_bytes()
        assert len(raw) == row['bytes'] and digest(raw) == row['sha256'], name
        verified.append(name)
    figures = {11: 'quality', 13: 'source_changes', 15: 'risk_coverage', 17: 'examples'}
    table_count = 0
    for i, cell in enumerate(nb.cells):
        for j, output in enumerate(cell.get('outputs', [])):
            d = output.get('data', {})
            if 'image/png' in d:
                name = figures[i]+'.png'
                raw = base64.b64decode(d['image/png'])
                assert raw == (out/name).read_bytes()
                assert digest(raw) == listed[name]['sha256']
            if 'text/html' in d:
                assert d['text/html'] == (out/f'table_{i}_{j}.html').read_text()
                table_count += 1
    read = lambda name: pd.read_csv(out/'csv_exports'/(name+'.csv'), dtype={'source_id': str}, float_precision='round_trip')
    frames = {p.stem: read(p.stem) for p in (out/'csv_exports').glob('*.csv')}
    expected_counts = dict(quality=112, risk=896, source_manifest=4, acquisition=8, summary=12,
        risk_summary=224, quality_changes=40, selection_comparisons=512, compute=120,
        score_costs=32, trajectories=640, preflight=16, fbcnn_diagnostics=24, endpoint_comparison=24)
    assert set(frames) == set(expected_counts)
    for name, n in expected_counts.items():
        assert len(frames[name]) == n
    q, r = frames['quality'], frames['risk']
    qkeys = ['source_id','stage','model']
    rkeys = ['source_id','stage','pipeline','region','score','coverage']
    assert not q.duplicated(qkeys).any() and not r.duplicated(rkeys).any()
    assert set(q.source_id) == set(r.source_id) == {'0801','0802','0803','0804'}
    assert set(q.stage) == set(r.stage) == {'quantized_8bit','jpeg_q75'}
    assert all(len(f) == 14 for _, f in q.groupby(['source_id','stage']))
    assert all(len(f) == 112 for _, f in r.groupby(['source_id','stage']))
    assert len(q[q.role == 'main']) == 48
    assert np.isfinite(q.select_dtypes('number')).all().all()
    assert np.isfinite(r.select_dtypes('number')).all().all()
    assert (q[['mse','detail_mse']] > 0).all().all()
    assert np.max(abs(q.psnr_db + 10*np.log10(q.mse))) < 1e-12
    tails = ['bad_detail_rate_0.025','bad_detail_rate_0.05','bad_detail_rate_0.1']
    metrics = ['rgb_mse','detail_mse'] + tails
    for frame in (q,r):
        assert frame[tails].ge(0).all().all() and frame[tails].le(1).all().all()
        assert frame[tails[0]].ge(frame[tails[1]]).all() and frame[tails[1]].ge(frame[tails[2]]).all()
    assert (r.retained_patches == np.ceil(r.coverage*r.available_patches)).all()
    assert r.loc[r.region=='all','available_patches'].eq(1024).all()
    assert r.loc[r.region=='textured_quartile','available_patches'].eq(256).all()
    full = r[r.coverage==1]
    assert full.groupby(['source_id','stage','pipeline','region'])[metrics].agg(lambda v: v.max()-v.min()).max().max() < 1e-14
    for row in r[(r.coverage==1)&(r.region=='all')].to_dict('records'):
        qr=q[(q.source_id==row['source_id'])&(q.stage==row['stage'])&(q.model==row['pipeline'])].iloc[0]
        for col in metrics:
            assert abs(row[col]-qr['mse' if col=='rgb_mse' else col]) < 1e-12
    assert r[r.score=='random_expected'].groupby(['source_id','stage','pipeline','region'])[metrics].agg(lambda v:v.max()-v.min()).max().max() < 1e-14
    for _, f in r.groupby(['source_id','stage','pipeline','region','coverage']):
        a=f.set_index('score')
        assert (a.loc['oracle_detail_error','detail_mse'] <= a.detail_mse+1e-12).all()
    summary = q[q.role=='main'].groupby(['stage','model'],as_index=False).agg(
        mean_mse=('mse','mean'),mean_detail_mse=('detail_mse','mean'),sources=('source_id','nunique'))
    summary['pooled_psnr_db']=-10*np.log10(summary.mean_mse)
    pd.testing.assert_frame_equal(summary,frames['summary'],check_exact=False,atol=1e-12,rtol=0)
    risk_summary=r.groupby(rkeys[1:],as_index=False)[metrics].mean()
    pd.testing.assert_frame_equal(risk_summary,frames['risk_summary'],check_exact=False,atol=1e-12,rtol=0)
    for row in frames['quality_changes'].to_dict('records'):
        f=q[(q.source_id==row['source_id'])&(q.stage==row['stage'])].set_index('model')
        for col in ['mse','detail_mse','psnr_db']:
            assert abs(f.loc[row['method'],col]-f.loc[row['comparator'],col]-row['delta_'+col]) < 1e-12
    for row in frames['selection_comparisons'].to_dict('records'):
        f=r
        for k in ['source_id','stage','pipeline','region','coverage']:
            f=f[f[k]==row[k]]
        f=f.set_index('score')
        for col in metrics:
            assert abs(f.loc['operator_spread_detail',col]-f.loc[row['control'],col]-row['delta_'+col]) < 1e-12
    compute,costs,diag=frames['compute'],frames['score_costs'],frames['fbcnn_diagnostics']
    assert compute.denoiser_calls.sum()==640 and compute.fbcnn_calls.sum()==24
    assert compute.elapsed_seconds.gt(0).all()
    assert not compute.duplicated(['source_id','stage','component']).any()
    assert diag.predicted_degradation.between(0,1).all()
    assert np.allclose(diag.predicted_quality,100*(1-diag.predicted_degradation),atol=1e-12,rtol=0)
    for row in costs.itertuples(index=False):
        f=compute[(compute.source_id==row.source_id)&(compute.stage==row.stage)].set_index('component')
        names=[row.pipeline]+[row.pipeline+'_'+s for s in (['sigma08','sigma12'] if row.score_family=='operator' else ['rot90','rot180'])]
        if row.pipeline=='fbcnn_dpir':
            names+=['fbcnn'] if row.score_family=='operator' else ['fbcnn','fbcnn_rot90_intermediate','fbcnn_rot180_intermediate']
        assert abs(f.loc[names].elapsed_seconds.sum()-row.elapsed_seconds) < 1e-9
        assert f.loc[names].denoiser_calls.sum()==row.denoiser_calls
        assert f.loc[names].fbcnn_calls.sum()==row.fbcnn_calls
    trajectory=frames['trajectories']
    assert not trajectory.duplicated(['source_id','stage','component','iteration']).any()
    assert all(sorted(f.iteration)==list(range(1,9)) for _,f in trajectory.groupby(['source_id','stage','component']))
    # Reconcile seven result tables; preserve the separate design budget table.
    primary=frames['risk_summary'].query("stage=='jpeg_q75' and pipeline=='fbcnn_dpir' and region=='all' and coverage==0.5")
    aggregate=compute.groupby('component',as_index=False).agg(runs=('elapsed_seconds','size'),seconds=('elapsed_seconds','sum'),drunet_calls=('denoiser_calls','sum'),fbcnn_calls=('fbcnn_calls','sum'))
    tables=[(11,0,frames['summary'],8),(13,0,frames['quality_changes'],8),(13,2,diag,5),
        (15,1,primary,8),(17,1,frames['endpoint_comparison'],10),(17,2,aggregate,3),(17,3,costs,3)]
    for i,j,frame,decimals in tables:
        actual=pd.read_html(io.StringIO((out/f'table_{i}_{j}.html').read_text()))[0]
        expected=pd.read_html(io.StringIO(frame.round(decimals)._repr_html_()))[0]
        pd.testing.assert_frame_equal(actual,expected,check_dtype=False,check_exact=False,atol=1e-12,rtol=0)
    # Independent simulator and classical inverse from the frozen equations, no torch.
    cfg=json.loads((out/'config.json').read_text())
    assert cfg['source_ids']==['0801','0802','0803','0804']
    assert (cfg['crop_size'],cfg['context_border'],cfg['patch_size'],cfg['detail_blur_sigma'])==(512,32,16,1.)
    assert cfg['true_sigmas']==[1.6] and cfg['nominal_sigma']==1. and cfg['gradient_lambda']==.05
    official=json.loads((repo/'data/manifests/div2k_development_100.json').read_text())
    hashes={v['source_id'].split(':')[1]:v['source_pixels_sha256'] for v in official['records']}
    cut=lambda x:x[32:544,32:544]
    fy=np.fft.fftfreq(576)[:,None];fx=np.fft.fftfreq(576)[None,:]
    ht=lambda sigma:np.exp(-2*np.pi**2*sigma**2*(fx**2+fy**2))
    smooth=lambda x,sigma:np.fft.ifft2(np.fft.fft2(x,axes=(0,1))*ht(sigma)[:,:,None],axes=(0,1)).real
    detail=lambda x:x-smooth(x,1.)
    filt=ht(1.)/(ht(1.)**2+.05*4*(np.sin(np.pi*fx)**2+np.sin(np.pi*fy)**2))
    cheap_max=0.;codec_count=0;observations=0;source_hashes=[]
    for row in frames['source_manifest'].itertuples(index=False):
        with Image.open(data/row.filename) as img: rgb=np.asarray(img.convert('RGB'))
        assert digest((data/row.filename).read_bytes())==row.sha256
        assert digest(rgb.tobytes())==row.rgb_sha256==hashes[row.source_id]
        assert rgb.shape==(row.height,row.width,3) and row.extent==576
        assert row.crop_top==(row.height-576)//2 and row.crop_left==(row.width-576)//2
        source_hashes.append(row.source_id)
        truth=rgb[row.crop_top:row.crop_top+576,row.crop_left:row.crop_left+576].astype(float)/255
        rng=np.random.default_rng(np.random.SeedSequence([cfg['seed'],int(digest(row.source_id.encode())[:8],16)]))
        linear=smooth(truth,1.6)+(2/255)*rng.standard_normal(truth.shape)
        ints=np.rint(np.clip(linear,0,1)*255).astype('uint8');quant=ints.astype(float)/255
        b=io.BytesIO();Image.fromarray(ints).save(b,format='JPEG',quality=75,subsampling=0,optimize=False)
        encoded=b.getvalue()
        with Image.open(io.BytesIO(encoded)) as img:jpeg=np.asarray(img.convert('RGB')).astype(float)/255
        for stage,y in [('quantized_8bit',quant),('jpeg_q75',jpeg)]:
            ar=frames['acquisition'].query('source_id==@row.source_id and stage==@stage').iloc[0]
            assert digest(y.tobytes())==ar.observation_sha256;observations+=1
            if stage=='jpeg_q75':
                assert len(encoded)==ar.jpeg_bytes and digest(encoded)==ar.jpeg_sha256
                assert digest(encoded)==listed['codec_inputs/'+row.source_id+'_q75.jpg']['sha256'];codec_count+=1
            classical=np.clip(np.fft.ifft2(np.fft.fft2(y,axes=(0,1))*filt[:,:,None],axes=(0,1)).real,0,1)
            for model,x in [('observed',y),('gradient_nominal',classical)]:
                re=((cut(x)-cut(truth))**2).mean(axis=-1);de=(cut(detail(x)-detail(truth))**2).mean(axis=-1)
                vals={'mse':float(re.mean()),'detail_mse':float(de.mean()),'psnr_db':float(-10*np.log10(re.mean()))}
                dp=de.reshape(32,16,32,16).mean(axis=(1,3)).ravel()
                vals.update({f'bad_detail_rate_{t:g}':float((np.sqrt(dp)>t).mean()) for t in [.025,.05,.1]})
                qr=q.query('source_id==@row.source_id and stage==@stage and model==@model').iloc[0]
                for col,val in vals.items():
                    diff=abs(val-qr[col]);assert diff<1e-12
                    if col in ['mse','detail_mse']:cheap_max=max(cheap_max,diff)
    anchor=pd.read_csv(repo/'experiments/jpeg_aware_04/anchors/quality.csv',dtype={'source_id':str},float_precision='round_trip')
    for row in frames['endpoint_comparison'].to_dict('records'):
        now=q;old=anchor
        for k in ['source_id','stage','model']:
            now=now[now[k]==row[k]];old=old[old[k]==row[k]]
        for col in ['mse','detail_mse','psnr_db']:
            name='delta_'+('psnr' if col=='psnr_db' else col)+'_from_acquisition03'
            assert abs(now.iloc[0][col]-old.iloc[0][col]-row[name])<1e-12
    controls=['image_transform_spread_detail','measurement_residual','image_gradient','random_expected']
    qm=q[q.stage=='jpeg_q75'].groupby('model').detail_mse.mean()
    qp=q[q.stage=='jpeg_q75'].pivot(index='source_id',columns='model',values='detail_mse')
    recon=bool(all(qm.fbcnn_dpir<qm[c] for c in ['dpir_nominal','gradient_nominal','fbcnn_gradient']) and (qp.fbcnn_dpir<qp.dpir_nominal).sum()>=3)
    pr=r.query("stage=='jpeg_q75' and pipeline=='fbcnn_dpir' and region=='all' and coverage==0.5")
    means=pr.groupby('score')[metrics].mean();op=means.loc['operator_spread_detail'];best=means.loc[controls,'detail_mse'].idxmin()
    per=pr.pivot(index='source_id',columns='score',values='detail_mse')
    selection=bool((op.detail_mse<means.loc[controls,'detail_mse']).all() and (per.operator_spread_detail<per[best]).sum()>=3 and all((op[c]<=means.loc[controls,c]+1e-12).all() for c in tails))
    decisions=json.loads((out/'decisions.json').read_text())
    assert decisions['reconstruction_screen_pass']==recon and decisions['selection_screen_pass']==selection
    assert decisions['selection_best_pooled_operational_control']==best
    assert decisions['selection_source_wins']==int((per.operator_spread_detail<per[best]).sum())==4
    assert decisions['reconstruction_source_wins_vs_raw_dpir']==int((qp.fbcnn_dpir<qp.dpir_nominal).sum())==4
    for key in ['independent_test','calibrated_reliability','novelty_established','stronger_trained_image_only_uncertainty_comparator_run']:
        assert decisions[key] is False
    pooled=summary.pivot(index='stage',columns='model',values='pooled_psnr_db')
    pooled.to_csv(out/'pooled_psnr_comparison.csv')
    means.to_csv(out/'primary_selection.csv')
    per.to_csv(out/'primary_selection_per_source.csv')
    comparison=frames['selection_comparisons']
    primary_comparison=comparison.query("stage=='jpeg_q75' and pipeline=='fbcnn_dpir' and region=='all' and coverage==0.5")
    reversals=primary_comparison[(primary_comparison[['delta_'+c for c in tails]]>1e-12).any(axis=1)]
    reversals.to_csv(out/'primary_source_tail_reversals.csv',index=False)
    stage_stats={}
    for stage in ['jpeg_q75','quantized_8bit']:
        f=summary[summary.stage==stage].set_index('model')
        stage_stats[stage]=dict(pooled_psnr_gain_vs_raw_dpir=float(f.loc['fbcnn_dpir','pooled_psnr_db']-f.loc['dpir_nominal','pooled_psnr_db']),
            detail_mse_percent_change_vs_raw_dpir=float(100*(f.loc['fbcnn_dpir','mean_detail_mse']/f.loc['dpir_nominal','mean_detail_mse']-1)))
    audit=dict(status='passed_for_notebook_and_readable_export_scope',notebook_sha256=digest(Path(notebook).read_bytes()),
        notebook_bytes=Path(notebook).stat().st_size,all_23_cell_sources_unchanged=True,code_cells=11,execution_counts=counts,
        consecutive_execution_counts=counts==list(range(1,12)),execution_count_gap_cause='unknown',saved_errors=0,saved_stderr=0,
        inherited_validation_metadata_is_historical=True,reported_checks_readback_decision_match_export_json=True,
        design_freeze_hash_matches=True,manifest_entries=37,verified_export_files=len(verified),verified_export_names=sorted(verified),
        original_learned_prediction_files_retrieved=0,full_export_hash_verification=False,zip_or_parts_bytes_verified=False,
        original_codec_files_retrieved=0,regenerated_codec_hashes_matching_manifest=codec_count,
        raw_download_attempt=dict(part='006_of_006',http_status=403),csv_row_counts=expected_counts,
        embedded_figures_matching_export_hashes=4,html_tables_preserved=table_count,result_tables_reconciled=len(tables),
        source_files_and_official_rgb_hashes_verified=source_hashes,regenerated_observation_hashes=observations,
        independently_recomputed_input_classical_quality_rows=16,cheap_quality_max_abs_mse_difference=cheap_max,
        primary_screens_recomputed_from_csv=dict(reconstruction=recon,selection=selection),
        stage_comparisons=stage_stats,primary_selection_relative_detail_mse_change_percent=float(100*(op.detail_mse/means.loc[best,'detail_mse']-1)),
        primary_per_source_tail_reversal_rows=len(reversals),recorded_component_seconds=float(compute.elapsed_seconds.sum()),
        experiment_drunet_calls=640,experiment_fbcnn_calls=24,small_validation_calls=dict(drunet=2,fbcnn=3),
        neural_inference_rerun=False,independent_learned_array_readback=False)
    (out/'audit.json').write_text(json.dumps(audit,indent=2,allow_nan=False)+'\n')
    print(json.dumps(audit,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['notebook','issued_notebook','out','repo','data']:
        p.add_argument('--'+k.replace('_','-'),required=True,type=Path)
    review(**vars(p.parse_args()))
