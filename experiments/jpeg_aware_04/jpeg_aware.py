"""Frozen FBCNN preprocessing comparison; no new-method or test-set claims."""
import ast
import hashlib
import io
import json
import platform
import time
import types
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import PIL
from PIL import features
import torch

B01 = L02 = D03 = None
STAGES = ['quantized_8bit', 'jpeg_q75']
MAIN_MODELS = ['observed', 'gradient_nominal', 'dpir_nominal', 'fbcnn', 'fbcnn_gradient', 'fbcnn_dpir']
PIPELINES = ['dpir_nominal', 'fbcnn_dpir']
VARIANTS = [('nominal', 1.0, 0), ('sigma08', 0.8, 0), ('sigma12', 1.2, 0),
            ('rot90', 1.0, 1), ('rot180', 1.0, 2)]
LABELS = {'observed': 'Input', 'gradient_nominal': 'Classical', 'dpir_nominal': 'DPIR',
          'fbcnn': 'FBCNN only', 'fbcnn_gradient': 'FBCNN + classical', 'fbcnn_dpir': 'FBCNN + DPIR'}
COLORS = dict(zip(MAIN_MODELS, ['#667085', '#B78103', '#2463A6', '#AE547A', '#768A46', '#123F68']))
CONTROL_SCORES = ['image_transform_spread_detail', 'measurement_residual', 'image_gradient', 'random_expected']
FRAME_NAMES = ['source_manifest', 'acquisition', 'preflight', 'quality', 'summary', 'risk',
               'risk_summary', 'quality_changes', 'selection_comparisons', 'compute', 'score_costs',
               'trajectories', 'fbcnn_diagnostics', 'endpoint_comparison']


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def variant_name(pipeline, variant):
    return pipeline if variant == 'nominal' else pipeline + '_' + variant


def load_fbcnn(vendor_dir, checkpoint, provenance, device):
    vendor_dir = Path(vendor_dir)
    for rel, expected in provenance['files'].items():
        assert sha256(vendor_dir / rel) == expected, f'FBCNN source mismatch: {rel}'
    L02.download_weights(checkpoint, provenance)
    source = (vendor_dir / 'models/network_fbcnn.py').read_text()
    tree = ast.parse(source)
    imports = [n for n in tree.body if isinstance(n, ast.Import) and
               any(a.name == 'torchvision.models' for a in n.names)]
    assert len(imports) == 1 and len(imports[0].names) == 1
    assert not any(isinstance(n, ast.Name) and n.id == 'models' for n in ast.walk(tree)), 'Import is no longer unused'
    # Preserve original vendor bytes. Remove only an unused optional dependency.
    tree.body.remove(imports[0])
    module = types.ModuleType('fbcnn04_network')
    exec(compile(tree, str(vendor_dir / 'models/network_fbcnn.py'), 'exec'), module.__dict__)
    model = module.FBCNN(in_nc=3, out_nc=3, nc=[64,128,256,512], nb=4, act_mode='R')
    state = torch.load(checkpoint, map_location='cpu', weights_only=True)
    assert isinstance(state, dict) and all(isinstance(v, torch.Tensor) for v in state.values())
    model.load_state_dict(state, strict=True)
    model.eval().requires_grad_(False)
    model.to(device)
    count = sum(p.numel() for p in model.parameters())
    print(f'Loaded verified FBCNN: {count:,} parameters; device={device}', flush=True)
    return model, count


def deblock(image, model, device):
    assert image.ndim == 3 and image.shape[2] == 3 and np.isfinite(image).all()
    assert image.min() >= 0 and image.max() <= 1
    L02.sync(device)
    if device.type == 'cuda':
        torch.cuda.reset_peak_memory_stats(device)
    start = time.perf_counter()
    with torch.inference_mode():
        tensor = L02.to_tensor(image, device)
        restored, q = model(tensor)  # Automatic quality; never supply Q75.
        assert restored.shape == tensor.shape and bool(restored.isfinite().all())
        assert q.shape == (1,1) and bool(q.isfinite().all()) and 0 <= float(q.item()) <= 1
        clipped = float(((restored < 0) | (restored > 1)).float().mean().item())
        output = restored.clamp(0,1).squeeze(0).permute(1,2,0).cpu().numpy().astype(np.float64)
        degradation = float(q.item())
    L02.sync(device)
    return (output, dict(elapsed_seconds=time.perf_counter()-start, denoiser_calls=0, fbcnn_calls=1,
        peak_cuda_memory_mb=float(torch.cuda.max_memory_allocated(device)/1024**2) if device.type=='cuda' else None),
        dict(predicted_degradation=degradation, predicted_quality=100*(1-degradation), output_clipped_fraction=clipped))


def validate_fbcnn(model, device):
    x = torch.linspace(0,1,3*31*37,device=device).reshape(1,3,31,37)
    with torch.inference_mode():
        a, qa = model(x)
        b, qb = model(x)
        forced, q_forced = model(x, qa)
    assert a.shape == x.shape and torch.equal(a,b) and torch.equal(qa,qb)
    assert bool(a.isfinite().all()) and 0 <= float(qa.item()) <= 1
    assert torch.equal(qa,q_forced)
    error = float((a-forced).abs().max().item())
    assert error < 1e-7
    return dict(fbcnn_strict_load=True, fbcnn_repeat_identical=True, fbcnn_odd_size_padding=True,
                automatic_vs_own_predicted_quality_max_abs_error=error, fbcnn_small_validation_calls=3)


def snapshot(result, output_dir, state, error=None):
    output_dir = Path(output_dir)
    for name in FRAME_NAMES:
        if name in result:
            result[name].to_csv(output_dir / (name+'.csv'), index=False)
    for name in ['config','provenance','checks','environment','decisions']:
        if name in result:
            dump(output_dir / (name+'.json'), result[name])
    status = dict(status=state, configured_sources=result['config']['source_ids'],
        completed_observations=result['completed_observations'], planned_observations=2*len(result['config']['source_ids']),
        full_design_observations=8, full_design_complete=result['completed_observations']==8,
        updated_utc=datetime.now(timezone.utc).isoformat())
    if error is not None:
        status['error'] = str(error)
    dump(output_dir/'status.json', status)
    files = [dict(name=str(p.relative_to(output_dir)), bytes=p.stat().st_size, sha256=sha256(p))
             for p in sorted(output_dir.rglob('*')) if p.is_file() and p.name!='export_manifest.json']
    dump(output_dir/'export_manifest.json', dict(experiment='jpeg_aware_04', role='development_only',
                                                snapshot_status=state, files=files))


def analyse(result):
    q, r = result['quality'], result['risk']
    summary = q[q.model.isin(MAIN_MODELS)].groupby(['stage','model'],as_index=False).agg(
        mean_mse=('mse','mean'), mean_detail_mse=('detail_mse','mean'), sources=('source_id','nunique'))
    summary['pooled_psnr_db'] = -10*np.log10(summary.mean_mse)
    metrics = ['rgb_mse','detail_mse']+[f'bad_detail_rate_{t:g}' for t in result['config']['detail_rmse_tolerances']]
    risk_summary = r.groupby(['stage','pipeline','region','score','coverage'],as_index=False)[metrics].mean()
    changes = []
    pairs = [('fbcnn_dpir','dpir_nominal'),('fbcnn_dpir','gradient_nominal'),
             ('fbcnn_dpir','fbcnn_gradient'),('fbcnn_gradient','gradient_nominal'),('fbcnn','observed')]
    for (sid,stage), frame in q.groupby(['source_id','stage']):
        f = frame.set_index('model')
        for a,b in pairs:
            changes.append(dict(source_id=sid,stage=stage,method=a,comparator=b,
                delta_detail_mse=float(f.loc[a,'detail_mse']-f.loc[b,'detail_mse']),
                delta_mse=float(f.loc[a,'mse']-f.loc[b,'mse']),
                delta_psnr_db=float(f.loc[a,'psnr_db']-f.loc[b,'psnr_db'])))
    selections = []
    for (sid,stage,pipeline,region,coverage), frame in r.groupby(['source_id','stage','pipeline','region','coverage']):
        f = frame.set_index('score'); op = f.loc['operator_spread_detail']
        for control in CONTROL_SCORES:
            row = dict(source_id=sid,stage=stage,pipeline=pipeline,region=region,coverage=float(coverage),control=control)
            row.update({'delta_'+m:float(op[m]-f.loc[control,m]) for m in metrics})
            selections.append(row)
    result.update(summary=summary, risk_summary=risk_summary, quality_changes=pd.DataFrame(changes),
                  selection_comparisons=pd.DataFrame(selections))
    full = sorted(result['config']['source_ids']) == ['0801','0802','0803','0804'] and result['completed_observations']==8
    qc = result['quality_changes'].query("stage=='jpeg_q75' and method=='fbcnn_dpir'")
    cmp_means = qc.groupby('comparator').delta_detail_mse.mean()
    reconstruction_wins = int((qc.query("comparator=='dpir_nominal'").delta_detail_mse < 0).sum())
    rs = r.query("stage=='jpeg_q75' and pipeline=='fbcnn_dpir' and region=='all' and coverage==0.5")
    means = rs.groupby('score')[metrics].mean()
    best_control = means.loc[CONTROL_SCORES,'detail_mse'].idxmin()
    per_source = rs.pivot(index='source_id',columns='score',values='detail_mse')
    selection_wins = int((per_source.operator_spread_detail < per_source[best_control]).sum())
    op = means.loc['operator_spread_detail']
    decisions = dict(scope='descriptive_development_screen_only', full_design_assessed=full,
        status='assessed_development_only' if full else 'not_assessed_full_design',
        jpeg_detail_mse_deltas_vs_inverse_controls={str(k):float(v) for k,v in cmp_means.items()},
        reconstruction_source_wins_vs_raw_dpir=reconstruction_wins,
        selection_best_pooled_operational_control=str(best_control), selection_source_wins=selection_wins,
        reconstruction_screen_pass=None, selection_screen_pass=None,
        independent_test=False, calibrated_reliability=False, novelty_established=False,
        stronger_trained_image_only_uncertainty_comparator_run=False)
    if full:
        decisions['reconstruction_screen_pass'] = bool((cmp_means < 0).all() and reconstruction_wins>=3)
        tails = [m for m in metrics if m.startswith('bad_detail')]
        decisions['selection_screen_pass'] = bool(
            (op.detail_mse < means.loc[CONTROL_SCORES,'detail_mse']).all() and selection_wins>=3 and
            all((op[m] <= means.loc[CONTROL_SCORES,m]+1e-12).all() for m in tails))
    result['decisions'] = decisions


def plot_results(result, output_dir, sources):
    output_dir = Path(output_dir)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
        'axes.spines.right':False,'axes.grid':True,'grid.alpha':.18,'figure.facecolor':'white'})
    stage_labels = {'quantized_8bit':'8-bit, no JPEG','jpeg_q75':'JPEG Q75'}
    scope = f"{len(sources)} development source(s); no independent test"
    fig, axes = plt.subplots(2,2,figsize=(12,7.3),sharey=True)
    for j,stage in enumerate(STAGES):
        frame=result['summary'].query('stage==@stage').set_index('model').loc[MAIN_MODELS]
        for i,col in enumerate(['pooled_psnr_db','mean_detail_mse']):
            ax=axes[i,j]
            for k,model in enumerate(MAIN_MODELS):
                ax.scatter(frame.loc[model,col],k,s=55,c=COLORS[model],marker='D' if model.startswith('fbcnn') else 'o')
            ax.set_yticks(range(6),[LABELS[m] for m in MAIN_MODELS]);ax.set_ylim(5.6,-.6)
            ax.set_title(stage_labels[stage]);ax.set_xlabel('Pooled RGB PSNR (dB; higher better)' if i==0 else 'Mean detail MSE (lower better)')
            if i: ax.ticklabel_format(axis='x',style='sci',scilimits=(0,0))
    fig.suptitle('Frozen reconstruction comparisons | '+scope)
    fig.tight_layout(rect=(0,0,1,.95));fig.savefig(output_dir/'quality.png',dpi=135);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11.5,4.4),sharey=True)
    for ax,stage in zip(axes,STAGES):
        frame=result['quality_changes'].query('stage==@stage and method=="fbcnn_dpir"')
        for k,(cmp,color,marker) in enumerate([('dpir_nominal','#2463A6','o'),('gradient_nominal','#B78103','s'),('fbcnn_gradient','#768A46','D')]):
            f=frame.query('comparator==@cmp').set_index('source_id').reindex(list(sources))
            ax.plot(np.arange(len(sources))+(k-1)*.10,f.delta_detail_mse,marker=marker,linestyle='none',color=color,label=LABELS[cmp])
        ax.axhline(0,color='#333333',linewidth=1);ax.set_xticks(range(len(sources)),list(sources));ax.set_xlabel('Source')
        ax.set_title(stage_labels[stage]);ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
    axes[0].set_ylabel('FBCNN + DPIR minus comparator detail MSE\nNegative favours FBCNN + DPIR')
    axes[1].legend(title='Comparator',frameon=False)
    fig.suptitle('Source-specific reconstruction changes | '+scope)
    fig.tight_layout(rect=(0,0,1,.94));fig.savefig(output_dir/'source_changes.png',dpi=135);plt.close(fig)
    style={'operator_spread_detail':('#2463A6','-','o','Operator detail'),
           'image_transform_spread_detail':('#AE547A','--','s','Whole-pipeline rotations'),
           'measurement_residual':('#B78103',':','^','Original-measurement residual'),
           'image_gradient':('#768A46','-.','v','Image gradient'),
           'operator_spread_rgb':('#123F68','--','D','Operator RGB (secondary)'),
           'random_expected':('#667085',':','x','Random expectation'),
           'oracle_detail_error':('#222222','-.','+','Reference-error ranking')}
    fig,axes=plt.subplots(2,2,figsize=(12,8),sharex=True)
    for i,pipeline in enumerate(PIPELINES):
        for j,stage in enumerate(STAGES):
            ax=axes[i,j]
            f=result['risk_summary'].query('pipeline==@pipeline and stage==@stage and region=="all"')
            for score,(color,ls,marker,label) in style.items():
                rows=f.query('score==@score').sort_values('coverage')
                ax.plot(100*rows.coverage,rows.detail_mse,color=color,linestyle=ls,marker=marker,label=label)
            ax.set_title(LABELS[pipeline]+' | '+stage_labels[stage]);ax.set_xlabel('Requested patch retention (%)')
            ax.set_ylabel('Retained detail MSE');ax.set_xticks([50,75,90,100]);ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
    handles,labels=axes[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',ncol=3,frameon=False,fontsize=9)
    fig.suptitle('Heuristic selection | All patches | '+scope)
    fig.tight_layout(rect=(0,.12,1,.95));fig.savefig(output_dir/'risk_coverage.png',dpi=135);plt.close(fig)
    sid=next(iter(sources));truth=sources[sid]
    shown=['reference','observed','gradient_nominal','dpir_nominal','fbcnn_gradient','fbcnn_dpir']
    fig,axes=plt.subplots(2,6,figsize=(14,5.4))
    for i,stage in enumerate(STAGES):
        with np.load(output_dir/'predictions'/f'{sid}_{stage}.npz',allow_pickle=False) as saved:
            for j,key in enumerate(shown):
                value=truth if key=='reference' else saved[key]
                axes[i,j].imshow(value[160:416,160:416]);axes[i,j].set_xticks([]);axes[i,j].set_yticks([]);axes[i,j].grid(False)
                if i==0:axes[i,j].set_title('Reference' if key=='reference' else LABELS[key],fontsize=10)
                if j==0:axes[i,j].set_ylabel(stage_labels[stage])
    fig.suptitle(f'Fixed central 256 x 256 inset | Source {sid} only | Metrics use the full 512 x 512 interior')
    fig.tight_layout(rect=(0,0,1,.92));fig.savefig(output_dir/'examples.png',dpi=135);plt.close(fig)


def run(data_dir, output_dir, dpir_vendor, dpir_weights, fbcnn_vendor, fbcnn_weights,
        provenance, expected_hashes, anchor_csv, anchor_acquisition_csv, config):
    config=json.loads(json.dumps(config));output_dir=Path(output_dir)
    assert config['stages']==STAGES and config['operator_sigmas']==[.8,1.,1.2] and config['outer_rotations']==[0,1,2]
    output_dir.mkdir(parents=True,exist_ok=False)
    for d in ['predictions','codec_inputs']:(output_dir/d).mkdir()
    result=dict(config=config,provenance=provenance,checks={},completed_observations=0,
        environment=dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,
            torch=str(torch.__version__),pillow=PIL.__version__,matplotlib=matplotlib.__version__,
            jpeg_codec=features.version_codec('jpg'),libjpeg_turbo=features.version_feature('libjpeg_turbo'),
            device='cuda' if torch.cuda.is_available() else 'cpu',
            cuda_name=torch.cuda.get_device_name() if torch.cuda.is_available() else None))
    snapshot(result,output_dir,'initializing')
    try:
        anchors=pd.read_csv(io.StringIO(anchor_csv),dtype={'source_id':str})
        anchor_acq=pd.read_csv(io.StringIO(anchor_acquisition_csv),dtype={'source_id':str})
        full_config={**config,'source_ids':['0801','0802','0803','0804']}
        all_sources,manifest=B01.load_sources(data_dir,expected_hashes,full_config)
        result['source_manifest']=manifest
        sources={sid:all_sources[sid] for sid in config['source_ids']}
        preflight=[]
        for sid,truth in all_sources.items():
            stages,measurements,_=D03.acquisition_stages(truth,sid,config)
            for stage in STAGES:
                ar=next(m for m in measurements if m['stage']==stage)
                old=anchor_acq.query('source_id==@sid and stage==@stage').iloc[0]
                assert ar['observation_sha256']==old.observation_sha256,'Acquisition 03 observation bytes changed'
                y=stages[stage]
                controls={'observed':y,'gradient_nominal':B01.inverse_spectrum(np.fft.fft2(y,axes=(0,1)),1.,'gradient',config['gradient_lambda'])}
                for model,x in controls.items():
                    row,_,_=D03.errors(truth,x,config)
                    old=anchors.query('source_id==@sid and stage==@stage and model==@model').iloc[0]
                    error=max(abs(row['mse']-old.mse),abs(row['detail_mse']-old.detail_mse))
                    assert error<1e-12,'Input/classical anchor changed'
                    preflight.append(dict(source_id=sid,stage=stage,model=model,max_abs_mse_difference=error))
        result['preflight']=pd.DataFrame(preflight)
        result['checks'].update(source_identities_verified=4,observation_hashes_verified=8,
            input_classical_anchor_rows=len(preflight),input_classical_anchor_max_abs_mse_difference=max(r['max_abs_mse_difference'] for r in preflight))
        L02.download_weights(dpir_weights,provenance['dpir'])
        dpir,device=L02.load_model(dpir_vendor,dpir_weights,provenance['dpir'],config)
        result['checks'].update(L02.validate_adapter(dpir,device,dpir_vendor,config))
        result['checks']['drunet_small_validation_calls']=2
        fbcnn,parameters=load_fbcnn(fbcnn_vendor,fbcnn_weights,provenance['fbcnn'],device)
        result['checks'].update(validate_fbcnn(fbcnn,device),fbcnn_parameters=parameters)
        result['environment'].update(cpu_threads=torch.get_num_threads(),deterministic_algorithms=torch.are_deterministic_algorithms_enabled())
        quality=[];risk=[];costs=[];score_costs=[];traces=[];acquisitions=[];fdiag=[];endpoint=[]
        snapshot(result,output_dir,'running')
        for sid,truth in sources.items():
            stages,measurements,encoded=D03.acquisition_stages(truth,sid,config)
            acquisitions.extend(m for m in measurements if m['stage'] in STAGES)
            result['acquisition']=pd.DataFrame(acquisitions)
            (output_dir/'codec_inputs'/f'{sid}_q75.jpg').write_bytes(encoded)
            for stage in STAGES:
                meta=dict(source_id=sid,stage=stage);y=stages[stage]
                print(f'{sid} | {stage} | {result["completed_observations"]+1}/{2*len(sources)}',flush=True)
                estimates={'observed':y};aux={};local_cost={}
                start=time.perf_counter()
                estimates['gradient_nominal']=B01.inverse_spectrum(np.fft.fft2(y,axes=(0,1)),1.,'gradient',config['gradient_lambda'])
                costs.append(dict(**meta,component='gradient_nominal',elapsed_seconds=time.perf_counter()-start,denoiser_calls=0,fbcnn_calls=0))
                for rotation in [0,1,2]:
                    restored,cost,diagnostic=deblock(np.rot90(y,rotation).copy(),fbcnn,device)
                    key='fbcnn' if rotation==0 else f'fbcnn_rot{rotation*90}_intermediate'
                    if rotation==0:estimates['fbcnn']=restored
                    else:aux[key]=restored.astype(np.float32)
                    local_cost[key]=cost;costs.append(dict(**meta,component=key,**cost))
                    fdiag.append(dict(**meta,rotation_degrees=rotation*90,**diagnostic))
                    print(f'  FBCNN rotation {rotation*90}: {cost["elapsed_seconds"]:.2f}s',flush=True)
                start=time.perf_counter()
                estimates['fbcnn_gradient']=B01.inverse_spectrum(np.fft.fft2(estimates['fbcnn'],axes=(0,1)),1.,'gradient',config['gradient_lambda'])
                costs.append(dict(**meta,component='fbcnn_gradient_inverse_only',elapsed_seconds=time.perf_counter()-start,denoiser_calls=0,fbcnn_calls=0))
                for pipeline in PIPELINES:
                    for variant,sigma,rotation in VARIANTS:
                        key=variant_name(pipeline,variant)
                        if pipeline=='dpir_nominal':inp=np.rot90(y,rotation).copy()
                        else:inp=estimates['fbcnn'] if rotation==0 else aux[f'fbcnn_rot{rotation*90}_intermediate'].astype(np.float64)
                        restored,cost,trace=L02.reconstruct(inp,sigma,dpir,device,config)
                        estimates[key]=np.rot90(restored,-rotation).copy()
                        cost={**cost,'fbcnn_calls':0};local_cost[key]=cost
                        costs.append(dict(**meta,component=key,**cost))
                        traces.extend(dict(**meta,component=key,**t) for t in trace)
                        print(f'  {key}: {cost["elapsed_seconds"]:.2f}s',flush=True)
                arrays={'supplied_observation':y,**aux}
                for name,x in estimates.items():
                    measured,rp,de=D03.errors(truth,x,config)
                    quality.append(dict(**meta,model=name,role='main' if name in MAIN_MODELS else 'ensemble_component',**measured))
                    arrays[name]=x if name in ['observed','gradient_nominal','fbcnn_gradient'] else x.astype(np.float32)
                    arrays[name+'__rgb_patch_error']=rp;arrays[name+'__detail_patch_error']=de
                    if name in ['observed','gradient_nominal','dpir_nominal']:
                        old=anchors.query('source_id==@sid and stage==@stage and model==@name').iloc[0]
                        endpoint.append(dict(**meta,model=name,delta_mse_from_acquisition03=measured['mse']-old.mse,
                            delta_detail_mse_from_acquisition03=measured['detail_mse']-old.detail_mse,
                            delta_psnr_from_acquisition03=measured['psnr_db']-old.psnr_db))
                for pipeline in PIPELINES:
                    operators=[estimates[variant_name(pipeline,k)] for k in ['sigma08','nominal','sigma12']]
                    transforms=[estimates[variant_name(pipeline,k)] for k in ['nominal','rot90','rot180']]
                    curve,score_arrays=L02.evaluate_scores(truth,estimates[pipeline],y,operators,transforms,config)
                    risk.extend(dict(**meta,pipeline=pipeline,**row) for row in curve.to_dict('records'))
                    arrays.update({pipeline+'__score__'+k:v for k,v in score_arrays.items()})
                    for family,variants in [('operator',['nominal','sigma08','sigma12']),('transformation',['nominal','rot90','rot180'])]:
                        components=[variant_name(pipeline,k) for k in variants]
                        if pipeline=='fbcnn_dpir':
                            components+=['fbcnn'] if family=='operator' else ['fbcnn','fbcnn_rot90_intermediate','fbcnn_rot180_intermediate']
                        score_costs.append(dict(**meta,pipeline=pipeline,score_family=family,
                            elapsed_seconds=sum(local_cost[k]['elapsed_seconds'] for k in components),
                            denoiser_calls=sum(local_cost[k]['denoiser_calls'] for k in components),
                            fbcnn_calls=sum(local_cost[k]['fbcnn_calls'] for k in components),
                            accounting='standalone score cost incl. shared nominal; do not sum overlapping score costs'))
                np.savez_compressed(output_dir/'predictions'/f'{sid}_{stage}.npz',**arrays)
                result.update(quality=pd.DataFrame(quality),risk=pd.DataFrame(risk),compute=pd.DataFrame(costs),
                    score_costs=pd.DataFrame(score_costs),trajectories=pd.DataFrame(traces),
                    fbcnn_diagnostics=pd.DataFrame(fdiag),endpoint_comparison=pd.DataFrame(endpoint))
                result['completed_observations']+=1
                snapshot(result,output_dir,'running')
        n=2*len(sources)
        assert len(result['quality'])==14*n and len(result['risk'])==112*n
        assert result['compute'].denoiser_calls.sum()==80*n and result['compute'].fbcnn_calls.sum()==3*n
        assert len(result['trajectories'])==80*n and len(result['score_costs'])==4*n
        assert not result['quality'].duplicated(['source_id','stage','model']).any()
        assert not result['risk'].duplicated(['source_id','stage','pipeline','region','score','coverage']).any()
        analyse(result)
        result['checks'].update(quality_rows=len(result['quality']),main_quality_rows=6*n,risk_rows=len(result['risk']),
            drunet_experiment_calls=80*n,fbcnn_experiment_calls=3*n,
            source_files_unchanged=all(sha256(Path(data_dir)/row.filename)==row.sha256 for row in manifest.itertuples()))
        assert result['checks']['source_files_unchanged']
        plot_results(result,output_dir,sources)
        snapshot(result,output_dir,'inference_complete_pending_independent_readback')
        return result
    except Exception as error:
        snapshot(result,output_dir,'failed',error)
        raise
