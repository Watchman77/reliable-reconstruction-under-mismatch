"""Independent saved-array readback for Notebook 04; no neural inference."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def validate(run_dir, data_dir):
    run=Path(run_dir);data_dir=Path(data_dir)
    cfg=json.loads((run/'config.json').read_text())
    status=json.loads((run/'status.json').read_text())
    assert status['status'] in ['inference_complete_pending_independent_readback','complete_for_configured_subset']
    assert cfg['crop_size']==512 and cfg['context_border']==32 and cfg['patch_size']==16 and cfg['detail_blur_sigma']==1
    manifest=json.loads((run/'export_manifest.json').read_text())
    files={r['name']:r for r in manifest['files']}
    assert len(files)==len(manifest['files'])
    assert set(files)=={str(p.relative_to(run)) for p in run.rglob('*') if p.is_file() and p.name!='export_manifest.json'}
    for name,r in files.items():assert (run/name).stat().st_size==r['bytes'] and sha(run/name)==r['sha256']
    read=lambda name:pd.read_csv(run/(name+'.csv'),dtype={'source_id':str})
    source,quality,risk,acq=map(read,['source_manifest','quality','risk','acquisition'])
    n=2*len(cfg['source_ids']);assert len(quality)==14*n and len(risk)==112*n and len(acq)==n
    assert set(acq.stage)=={'quantized_8bit','jpeg_q75'} and set(acq.source_id)==set(cfg['source_ids'])
    assert not quality.duplicated(['source_id','stage','model']).any()
    assert not risk.duplicated(['source_id','stage','pipeline','region','score','coverage']).any()
    assert status['completed_observations']==n and status['full_design_complete']==(n==8)
    cut=lambda x:x[32:544,32:544]
    pool=lambda x:x.reshape(32,16,32,16).mean(axis=(1,3)).ravel()
    def smooth(x,sigma=1):
        h,w=x.shape[:2]
        htf=np.exp(-2*np.pi**2*sigma**2*(np.fft.fftfreq(h)[:,None]**2+np.fft.fftfreq(w)[None,:]**2))
        return np.fft.ifft2(np.fft.fft2(x,axes=(0,1))*htf[:,:,None],axes=(0,1)).real
    detail=lambda x:x-smooth(x)
    maximum=patch_max=score_max=risk_max=0.;checked=patches=scored=risks=0
    main=['observed','gradient_nominal','dpir_nominal','fbcnn','fbcnn_gradient','fbcnn_dpir']
    pipeline_names=['dpir_nominal','fbcnn_dpir'];models=main.copy()
    for pipe in pipeline_names:models.extend(pipe+'_'+v for v in ['sigma08','sigma12','rot90','rot180'])
    score_names=['operator_spread_detail','image_transform_spread_detail','operator_spread_rgb','measurement_residual','image_gradient']
    arrays_expected={'supplied_observation','fbcnn_rot90_intermediate','fbcnn_rot180_intermediate'} | set(models)
    arrays_expected|={m+s for m in models for s in ['__rgb_patch_error','__detail_patch_error']}
    arrays_expected|={p+'__score__'+s for p in pipeline_names for s in score_names+['rgb_patch_error','detail_patch_error','reference_texture']}
    truths={}
    for row in source.itertuples(index=False):
        p=data_dir/row.filename
        with Image.open(p) as img:rgb=np.asarray(img.convert('RGB'))
        assert sha(p)==row.sha256 and hashlib.sha256(rgb.tobytes()).hexdigest()==row.rgb_sha256
        truth=rgb[row.crop_top:row.crop_top+row.extent,row.crop_left:row.crop_left+row.extent].astype(np.float64)/255
        assert truth.shape==(576,576,3);truths[row.source_id]=truth
    assert set(truths)=={'0801','0802','0803','0804'}
    for sid in cfg['source_ids']:
        truth=truths[sid];dt=detail(truth)
        identity=int(hashlib.sha256(sid.encode()).hexdigest()[:8],16)
        rng=np.random.default_rng(np.random.SeedSequence([cfg['seed'],identity]))
        linear=smooth(truth,1.6)+(2/255)*rng.standard_normal(truth.shape)
        quant=np.rint(np.clip(linear,0,1)*255).astype('uint8').astype(float)/255
        for stage in ['quantized_8bit','jpeg_q75']:
            with np.load(run/'predictions'/f'{sid}_{stage}.npz',allow_pickle=False) as saved:
                assert set(saved.files)==arrays_expected
                y=saved['supplied_observation'];ar=acq.query('source_id==@sid and stage==@stage').iloc[0]
                assert hashlib.sha256(np.ascontiguousarray(y).tobytes()).hexdigest()==ar.observation_sha256
                if stage=='quantized_8bit':assert np.array_equal(y,quant)
                else:
                    jpeg=run/'codec_inputs'/f'{sid}_q75.jpg'
                    assert jpeg.stat().st_size==ar.jpeg_bytes and sha(jpeg)==ar.jpeg_sha256
                    with Image.open(jpeg) as img:assert np.array_equal(np.asarray(img.convert('RGB')).astype(float)/255,y)
                assert np.array_equal(saved['observed'],y)
                for aux in ['fbcnn_rot90_intermediate','fbcnn_rot180_intermediate']:
                    assert saved[aux].shape==(576,576,3) and np.isfinite(saved[aux]).all() and saved[aux].min()>=0 and saved[aux].max()<=1
                for model in models:
                    x=saved[model].astype(np.float64)
                    assert x.shape==(576,576,3) and np.isfinite(x).all() and x.min()>=0 and x.max()<=1
                    re=((cut(x)-cut(truth))**2).mean(axis=2)
                    de=(cut(detail(x)-dt)**2).mean(axis=2)
                    rp,dp=pool(re),pool(de)
                    qr=quality.query('source_id==@sid and stage==@stage and model==@model').iloc[0]
                    actual={'mse':float(re.mean()),'psnr_db':float(-10*np.log10(re.mean())),'detail_mse':float(de.mean())}
                    for t in [.025,.05,.1]:actual[f'bad_detail_rate_{t:g}']=float((np.sqrt(dp)>t).mean())
                    for col,val in actual.items():
                        e=abs(val-qr[col]);maximum=max(maximum,e);assert e<1e-12,(sid,stage,model,col,e)
                    for domain,p in [('rgb',rp),('detail',dp)]:
                        e=float(np.abs(p-saved[model+'__'+domain+'_patch_error']).max())
                        patch_max=max(patch_max,e);assert e<1e-14;patches+=1
                    checked+=1
                for pipeline in pipeline_names:
                    x=saved[pipeline].astype(np.float64)
                    operator=[saved[pipeline+'_sigma08'].astype(float),x,saved[pipeline+'_sigma12'].astype(float)]
                    transforms=[x,saved[pipeline+'_rot90'].astype(float),saved[pipeline+'_rot180'].astype(float)]
                    def spread(xs):
                        stack=np.stack(xs);return np.sqrt(((stack-stack.mean(axis=0))**2).mean(axis=0).mean(axis=-1))
                    gy,gx=np.gradient(x.mean(axis=-1))
                    raw={'operator_spread_detail':spread([detail(a) for a in operator]),
                         'image_transform_spread_detail':spread([detail(a) for a in transforms]),
                         'operator_spread_rgb':spread(operator),
                         'measurement_residual':np.sqrt(((smooth(x)-y)**2).mean(axis=-1)),
                         'image_gradient':np.hypot(gx,gy)}
                    score_vectors={k:pool(cut(v)) for k,v in raw.items()}
                    gy,gx=np.gradient(cut(truth).mean(axis=-1));texture=pool(np.hypot(gx,gy))
                    score_vectors['reference_texture']=texture
                    rp=saved[pipeline+'__rgb_patch_error'];dp=saved[pipeline+'__detail_patch_error']
                    score_vectors.update(rgb_patch_error=rp,detail_patch_error=dp)
                    for name,value in score_vectors.items():
                        vec=saved[pipeline+'__score__'+name];assert vec.shape==(1024,) and np.isfinite(vec).all()
                        e=float(np.abs(value-vec).max());score_max=max(score_max,e);assert e<1e-12;scored+=1
                    groups={'all':np.arange(1024),'textured_quartile':np.argsort(texture,kind='stable')[-256:]}
                    for region,ids in groups.items():
                        for score in score_names+['random_expected','oracle_detail_error']:
                            scores=None if score=='random_expected' else dp if score=='oracle_detail_error' else saved[pipeline+'__score__'+score]
                            order=None if scores is None else np.lexsort((np.random.default_rng(82).random(len(ids)),scores[ids]))
                            for coverage in [.5,.75,.9,1.]:
                                k=int(np.ceil(coverage*len(ids)))
                                chosen=ids if order is None else ids[order[:k]]
                                rows=risk.query('source_id==@sid and stage==@stage and pipeline==@pipeline and region==@region and score==@score and coverage==@coverage')
                                assert len(rows)==1;rr=rows.iloc[0]
                                assert rr.available_patches==len(ids) and rr.retained_patches==k
                                vals={'rgb_mse':rp[chosen].mean(),'detail_mse':dp[chosen].mean()}
                                for t in [.025,.05,.1]:vals[f'bad_detail_rate_{t:g}']=(np.sqrt(dp[chosen])>t).mean()
                                for col,val in vals.items():
                                    e=abs(float(val)-rr[col]);risk_max=max(risk_max,e);assert e<1e-12
                                risks+=1
    summary=read('summary')
    for row in summary.itertuples(index=False):
        q=quality[(quality.stage==row.stage)&(quality.model==row.model)]
        assert abs(q.mse.mean()-row.mean_mse)<1e-12 and abs(q.detail_mse.mean()-row.mean_detail_mse)<1e-12
        assert abs(-10*np.log10(q.mse.mean())-row.pooled_psnr_db)<1e-12
    metrics=['rgb_mse','detail_mse','bad_detail_rate_0.025','bad_detail_rate_0.05','bad_detail_rate_0.1']
    agg=risk.groupby(['stage','pipeline','region','score','coverage'])[metrics].mean().sort_index()
    recorded=read('risk_summary').set_index(['stage','pipeline','region','score','coverage'])[metrics].sort_index()
    assert agg.index.equals(recorded.index) and np.allclose(agg,recorded,rtol=0,atol=1e-12)
    for row in read('quality_changes').to_dict('records'):
        frame=quality[(quality.source_id==row['source_id'])&(quality.stage==row['stage'])].set_index('model')
        for metric in ['mse','detail_mse','psnr_db']:
            assert abs(frame.loc[row['method'],metric]-frame.loc[row['comparator'],metric]-row['delta_'+metric])<1e-12
    for row in read('selection_comparisons').to_dict('records'):
        f=risk[(risk.source_id==row['source_id'])&(risk.stage==row['stage'])&(risk.pipeline==row['pipeline'])&
               (risk.region==row['region'])&(risk.coverage==row['coverage'])].set_index('score')
        for metric in metrics:assert abs(f.loc['operator_spread_detail',metric]-f.loc[row['control'],metric]-row['delta_'+metric])<1e-12
    compute=read('compute');costs=read('score_costs');diag=read('fbcnn_diagnostics')
    assert len(compute)==15*n and compute.denoiser_calls.sum()==80*n and compute.fbcnn_calls.sum()==3*n
    assert len(read('trajectories'))==80*n and len(diag)==3*n and len(costs)==4*n
    assert diag.predicted_degradation.between(0,1).all() and np.allclose(diag.predicted_quality,100*(1-diag.predicted_degradation))
    for row in costs.itertuples(index=False):
        f=compute[(compute.source_id==row.source_id)&(compute.stage==row.stage)].set_index('component')
        names=[row.pipeline]+[row.pipeline+'_'+s for s in (['sigma08','sigma12'] if row.score_family=='operator' else ['rot90','rot180'])]
        if row.pipeline=='fbcnn_dpir':names+=['fbcnn'] if row.score_family=='operator' else ['fbcnn','fbcnn_rot90_intermediate','fbcnn_rot180_intermediate']
        assert abs(f.loc[names].elapsed_seconds.sum()-row.elapsed_seconds)<1e-7
        assert f.loc[names].denoiser_calls.sum()==row.denoiser_calls and f.loc[names].fbcnn_calls.sum()==row.fbcnn_calls
    decision=json.loads((run/'decisions.json').read_text())
    full=set(cfg['source_ids'])=={'0801','0802','0803','0804'} and n==8
    assert decision['full_design_assessed']==full
    if not full:assert decision['reconstruction_screen_pass'] is None and decision['selection_screen_pass'] is None
    else:
        means=quality[quality.stage=='jpeg_q75'].groupby('model').detail_mse.mean()
        q=quality[quality.stage=='jpeg_q75'].pivot(index='source_id',columns='model',values='detail_mse')
        recon=bool(all(means.fbcnn_dpir<means[c] for c in ['dpir_nominal','gradient_nominal','fbcnn_gradient']) and (q.fbcnn_dpir<q.dpir_nominal).sum()>=3)
        controls=['image_transform_spread_detail','measurement_residual','image_gradient','random_expected']
        r=risk.query("stage=='jpeg_q75' and pipeline=='fbcnn_dpir' and region=='all' and coverage==0.5")
        m=r.groupby('score')[metrics].mean();best=m.loc[controls,'detail_mse'].idxmin()
        p=r.pivot(index='source_id',columns='score',values='detail_mse');op=m.loc['operator_spread_detail']
        selection=bool((op.detail_mse<m.loc[controls,'detail_mse']).all() and (p.operator_spread_detail<p[best]).sum()>=3 and
                       all((op[col]<=m.loc[controls,col]+1e-12).all() for col in metrics[2:]))
        assert decision['reconstruction_screen_pass']==recon and decision['selection_screen_pass']==selection
    assert checked==14*n and risks==112*n
    return dict(status='passed',configured_sources=cfg['source_ids'],observations=n,full_design_complete=full,
        manifest_files_verified_at_readback=len(files),quality_rows_recomputed=checked,patch_error_vectors=patches,
        score_vectors_recomputed=scored,risk_rows_recomputed=risks,max_abs_quality_difference=maximum,
        max_abs_patch_difference=patch_max,max_abs_score_difference=score_max,max_abs_risk_difference=risk_max,
        source_hashes_verified=4,summary_and_contrasts_verified=True,compute_accounting_verified=True,
        decision_scope_verified=True,neural_inference_repeated=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir',required=True,type=Path);parser.add_argument('--data-dir',required=True,type=Path)
    parser.add_argument('--audit-output',required=True,type=Path)
    args=parser.parse_args();audit=validate(args.run_dir,args.data_dir)
    args.audit_output.write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit,indent=2))
