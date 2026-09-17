"""Paired acquisition-stage diagnosis with the unchanged Learned 02 adapter."""
import hashlib
import io
import json
import os
import platform
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import PIL
from PIL import Image, features
import torch

B01 = None
L02 = None
STAGES = ['linear_float', 'clipped_float', 'quantized_8bit', 'jpeg_q75']
STAGE_LABELS = ['Linear float', '+ Clipping', '+ 8-bit rounding', '+ JPEG Q75']
MODELS = ['observed', 'gradient_nominal', 'drunet_denoise_only', 'dpir_nominal', 'dpir_oracle_blur']
MODEL_LABELS = {'observed': 'Input (display-clipped)', 'gradient_nominal': 'Classical gradient',
                'drunet_denoise_only': 'DRUNet denoise only', 'dpir_nominal': 'Nominal DPIR',
                'dpir_oracle_blur': 'True-blur DPIR diagnostic'}
COLORS = dict(zip(MODELS, ['#667085', '#B78103', '#768A46', '#2463A6', '#AE547A']))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def array_hash(array):
    # Shape and dtype are recorded separately in acquisition.csv.
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def acquisition_stages(truth, sid, config):
    identity = int(hashlib.sha256(sid.encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(np.random.SeedSequence([config['seed'], identity]))
    linear = B01.apply(truth, config['true_sigmas'][0]) + config['noise_stds'][0] * rng.standard_normal(truth.shape)
    clipped = np.clip(linear, 0, 1)
    integers = np.rint(clipped * 255).astype(np.uint8)
    quantized = integers.astype(np.float64) / 255
    stream = io.BytesIO()
    Image.fromarray(integers).save(stream, format='JPEG', quality=config['jpeg_quality'],
                                   subsampling=config['jpeg_subsampling'], optimize=False)
    encoded = stream.getvalue()
    with Image.open(io.BytesIO(encoded)) as image:
        jpeg = np.asarray(image.convert('RGB'), dtype=np.float64) / 255
    stages = dict(zip(STAGES, [linear, clipped, quantized, jpeg]))
    inherited = {meta['scenario']: y for meta, y in B01.observations(truth, sid, config)}
    assert np.array_equal(linear, inherited['blur_noise']), 'Linear simulator endpoint changed'
    assert np.array_equal(jpeg, inherited['blur_noise_jpeg']), 'JPEG simulator endpoint changed'
    assert np.array_equal(clipped, np.clip(clipped, 0, 1))
    assert np.max(np.abs(quantized - clipped)) <= .5 / 255 + 1e-15
    rows = []
    previous = linear
    for index, (stage, observation) in enumerate(stages.items()):
        assert observation.shape == truth.shape and observation.dtype == np.float64
        assert np.isfinite(observation).all()
        delta = observation - previous
        rows.append(dict(source_id=sid, stage=stage, stage_index=index,
            observation_sha256=array_hash(observation), dtype=str(observation.dtype),
            height=observation.shape[0], width=observation.shape[1], channels=3,
            minimum=float(observation.min()), maximum=float(observation.max()),
            changed_component_fraction_from_previous=float(np.mean(delta != 0)),
            measurement_delta_mse=float(np.mean(B01.interior(delta, config)**2)),
            linear_out_of_range_fraction=float(np.mean((linear < 0) | (linear > 1))),
            jpeg_bytes=len(encoded) if stage == 'jpeg_q75' else 0,
            jpeg_sha256=hashlib.sha256(encoded).hexdigest() if stage == 'jpeg_q75' else ''))
        previous = observation
    return stages, rows, encoded


def errors(truth, estimate, config):
    inside = lambda x: B01.interior(x, config)
    rgb = np.mean((inside(estimate) - inside(truth))**2, axis=2)
    # Identical metric definition; independently checked on archive readback.
    detail_difference = inside(L02.detail(estimate, config) - L02.detail(truth, config))
    detail = np.mean(detail_difference**2, axis=2)
    rgb_patch = B01.patch_mean(rgb, config['patch_size']).ravel()
    detail_patch = B01.patch_mean(detail, config['patch_size']).ravel()
    row = dict(mse=float(rgb.mean()), psnr_db=B01.psnr(rgb.mean()), detail_mse=float(detail.mean()))
    for threshold in config['detail_rmse_tolerances']:
        row[f'bad_detail_rate_{threshold:g}'] = float(np.mean(np.sqrt(detail_patch) > threshold))
    return row, rgb_patch, detail_patch


def summaries(quality):
    summary = quality.groupby(['stage_index', 'stage', 'model'], as_index=False).agg(
        mean_mse=('mse', 'mean'), mean_detail_mse=('detail_mse', 'mean'), sources=('source_id', 'nunique'))
    summary['pooled_psnr_db'] = summary.mean_mse.map(B01.psnr)
    deltas = []
    for (sid, model), frame in quality.groupby(['source_id', 'model']):
        frame = frame.sort_values('stage_index')
        for before, after in zip(frame.to_dict('records'), frame.to_dict('records')[1:]):
            deltas.append(dict(source_id=sid, model=model, from_stage=before['stage'], to_stage=after['stage'],
                to_stage_index=after['stage_index'], delta_mse=after['mse']-before['mse'],
                delta_psnr_db=after['psnr_db']-before['psnr_db'],
                delta_detail_mse=after['detail_mse']-before['detail_mse']))
    gaps = []
    for (sid, index, stage), frame in quality.groupby(['source_id', 'stage_index', 'stage']):
        frame = frame.set_index('model')
        gaps.append(dict(source_id=sid, stage_index=index, stage=stage,
            nominal_minus_classical_detail_mse=float(frame.loc['dpir_nominal','detail_mse']-frame.loc['gradient_nominal','detail_mse']),
            nominal_minus_classical_psnr_db=float(frame.loc['dpir_nominal','psnr_db']-frame.loc['gradient_nominal','psnr_db'])))
    gaps = pd.DataFrame(gaps).sort_values(['source_id', 'stage_index'])
    gaps['change_in_detail_gap'] = gaps.groupby('source_id').nominal_minus_classical_detail_mse.diff()
    return summary, pd.DataFrame(deltas), gaps


def snapshot(result, output_dir, state, error=None):
    output_dir = Path(output_dir)
    for name in ['source_manifest', 'quality', 'summary', 'stage_deltas', 'model_gaps', 'acquisition', 'compute', 'trajectories', 'endpoint_comparison']:
        if name in result:
            result[name].to_csv(output_dir / (name + '.csv'), index=False)
    for name in ['config', 'checks', 'provenance', 'environment']:
        (output_dir / (name + '.json')).write_text(json.dumps(result[name], indent=2) + '\n')
    status = dict(status=state, completed_observations=result['completed_observations'],
        planned_observations=4*len(result['config']['source_ids']), full_design_observations=16,
        full_design_complete=result['completed_observations']==16,
        updated_utc=datetime.now(timezone.utc).isoformat())
    if error is not None:
        status['error'] = str(error)
    (output_dir/'status.json').write_text(json.dumps(status, indent=2)+'\n')
    files = [dict(name=str(p.relative_to(output_dir)), bytes=p.stat().st_size, sha256=sha256(p))
             for p in sorted(output_dir.rglob('*')) if p.is_file() and p.name != 'export_manifest.json']
    manifest = dict(experiment='acquisition_03', role='development_only', snapshot_status=state, files=files)
    (output_dir/'export_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')


def verify_saved_predictions(result, output_dir, sources):
    max_error = 0.
    expected_rows = len(result['quality'])
    count = 0
    for sid, truth in sources.items():
        for stage in STAGES:
            with np.load(Path(output_dir)/'predictions'/f'{sid}_{stage}.npz', allow_pickle=False) as archive:
                assert set(archive.files) == {'supplied_observation'} | set(MODELS) | {m+s for m in MODELS for s in ['__rgb_patch_error','__detail_patch_error']}
                assert array_hash(archive['supplied_observation']) == result['acquisition'].query('source_id == @sid and stage == @stage').iloc[0].observation_sha256
                for model in MODELS:
                    estimate = archive[model].astype(np.float64)
                    assert estimate.shape==truth.shape and np.isfinite(estimate).all()
                    assert estimate.min()>=0 and estimate.max()<=1
                    measured, rp, dp = errors(truth, estimate, result['config'])
                    row = result['quality'].query('source_id == @sid and stage == @stage and model == @model').iloc[0]
                    for key,value in measured.items():
                        difference=abs(value-row[key]);max_error=max(max_error,float(difference))
                        assert difference<1e-12, (sid,stage,model,key,difference)
                    assert np.allclose(rp, archive[model+'__rgb_patch_error'], atol=1e-15, rtol=0)
                    assert np.allclose(dp, archive[model+'__detail_patch_error'], atol=1e-15, rtol=0)
                    count+=1
    assert count==expected_rows
    return dict(saved_prediction_quality_rows_checked=count, saved_prediction_max_abs_metric_difference=max_error)


def plot_results(result, output_dir, sources):
    plt.rcParams.update({'font.size':10, 'axes.spines.top':False, 'axes.spines.right':False,
        'axes.grid':True, 'grid.alpha':.2, 'figure.facecolor':'white', 'savefig.facecolor':'white'})
    figures=[];scope=f"{len(sources)} development source(s); same noise across stages"
    fig, axes=plt.subplots(1,2,figsize=(12,4.8))
    for model in MODELS:
        rows=result['summary'].query('model == @model').sort_values('stage_index')
        for ax,column in zip(axes,['pooled_psnr_db','mean_detail_mse']):
            ax.plot(rows.stage_index, rows[column], marker='o', color=COLORS[model], label=MODEL_LABELS[model],
                    linestyle='--' if model=='dpir_oracle_blur' else '-')
    axes[0].set_ylabel('Pooled RGB PSNR (dB; higher is better)')
    axes[1].set_ylabel('Mean detail MSE (lower is better)');axes[1].ticklabel_format(axis='y',style='sci',scilimits=(0,0))
    for ax in axes:ax.set_xticks(range(4),STAGE_LABELS,rotation=12);ax.set_xlabel('Ordered acquisition stage')
    fig.suptitle('Reconstruction quality across acquisition stages\n'+scope)
    handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=3,frameon=False)
    fig.tight_layout(rect=(0,.13,1,.91));fig.savefig(Path(output_dir)/'stage_quality.png',dpi=130);figures.append(fig)
    fig, axes=plt.subplots(1,2,figsize=(12,4.5))
    source_colors=['#2463A6','#B78103','#768A46','#AE547A']
    for i,(sid,frame) in enumerate(result['model_gaps'].groupby('source_id')):
        for ax,column in zip(axes,['nominal_minus_classical_detail_mse','nominal_minus_classical_psnr_db']):
            ax.plot(frame.stage_index,frame[column],marker=['o','s','^','D'][i],color=source_colors[i],label=sid)
    axes[0].set_ylabel('Nominal − classical detail MSE\nPositive: learned is worse');axes[0].ticklabel_format(axis='y',style='sci',scilimits=(0,0))
    axes[1].set_ylabel('Nominal − classical RGB PSNR (dB)\nPositive: learned is better')
    for ax in axes:ax.axhline(0,color='#333333',linewidth=1);ax.set_xticks(range(4),STAGE_LABELS,rotation=12);ax.legend(title='Source',frameon=False)
    fig.suptitle('Paired source-level reconstruction gaps\n'+scope);fig.tight_layout(rect=(0,0,1,.9));fig.savefig(Path(output_dir)/'source_gaps.png',dpi=130);figures.append(fig)
    fig,ax=plt.subplots(figsize=(10,4.8))
    delta=result['stage_deltas'].groupby(['to_stage_index','model']).delta_detail_mse.mean()
    for i,model in enumerate(MODELS):
        ax.bar(np.arange(3)+(i-2)*.15,[delta.loc[(j,model)] for j in [1,2,3]],width=.145,color=COLORS[model],label=MODEL_LABELS[model])
    ax.axhline(0,color='#333333',linewidth=1);ax.set_xticks(range(3),['Add clipping','Add 8-bit rounding','Add JPEG codec'])
    ax.set_ylabel('Change in mean detail MSE\nPositive: added stage worsens error');ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
    ax.legend(loc='upper left',bbox_to_anchor=(1.01,1),frameon=False);fig.suptitle('Conditional adjacent-stage changes\n'+scope)
    fig.tight_layout(rect=(0,0,1,.9));fig.savefig(Path(output_dir)/'stage_changes.png',dpi=130);figures.append(fig)
    # Display the first configured source with a fixed centre inset; never select by outcome.
    sid=next(iter(sources));truth=sources[sid];inside=lambda x:B01.interior(x,result['config'])[128:384,128:384]
    fig,axes=plt.subplots(4,5,figsize=(12,10))
    shown=['reference','observed','gradient_nominal','dpir_nominal','dpir_oracle_blur']
    titles=['Reference','Input','Classical','Nominal DPIR','True-blur diagnostic']
    for i,stage in enumerate(STAGES):
        with np.load(Path(output_dir)/'predictions'/f'{sid}_{stage}.npz',allow_pickle=False) as archive:
            for j,key in enumerate(shown):
                axes[i,j].imshow(inside(truth if key=='reference' else archive[key]));axes[i,j].set_xticks([]);axes[i,j].set_yticks([]);axes[i,j].grid(False)
                if i==0:axes[i,j].set_title(titles[j])
                if j==0:axes[i,j].set_ylabel(STAGE_LABELS[i])
    fig.suptitle(f'Source {sid}: fixed central 256 × 256 inset\nAll methods are evaluated on the full 512 × 512 region')
    fig.tight_layout(rect=(0,0,1,.93));fig.savefig(Path(output_dir)/'stage_examples.png',dpi=125);figures.append(fig)
    for fig in figures:plt.close(fig)
    return figures


def run(data_dir, output_dir, vendor_dir, weights, provenance, expected_hashes, anchor_csv, config):
    config=json.loads(json.dumps(config));output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=False);(output_dir/'predictions').mkdir();(output_dir/'codec_inputs').mkdir()
    anchors=pd.read_csv(io.StringIO(anchor_csv),dtype={'source_id':str})
    result=dict(config=config,provenance=provenance,checks={},completed_observations=0,
        environment=dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,
            torch=torch.__version__,pillow=PIL.__version__,matplotlib=matplotlib.__version__,
            jpeg_codec=features.version_codec('jpg'),libjpeg_turbo=features.version_feature('libjpeg_turbo'),
            device='cuda' if torch.cuda.is_available() else 'cpu',
            cuda_name=torch.cuda.get_device_name() if torch.cuda.is_available() else None))
    snapshot(result,output_dir,'initializing')
    try:
        full_config=json.loads(json.dumps(config));full_config['source_ids']=['0801','0802','0803','0804']
        all_sources,full_manifest=B01.load_sources(data_dir,expected_hashes,full_config)
        sources={sid:all_sources[sid] for sid in config['source_ids']}
        result['source_manifest']=full_manifest
        # Validate endpoints and cheap controls on all four sources before any new inference.
        preflight=[]
        for sid,truth in all_sources.items():
            stages,_,_=acquisition_stages(truth,sid,config)
            for stage,scenario in [('linear_float','blur_noise'),('jpeg_q75','blur_noise_jpeg')]:
                y=stages[stage]
                controls={'observed':np.clip(y,0,1),'gradient_nominal':B01.inverse_spectrum(np.fft.fft2(y,axes=(0,1)),config['nominal_sigma'],'gradient',config['gradient_lambda'])}
                for name,x in controls.items():
                    measured,_,_=errors(truth,x,config)
                    old=anchors.query('source_id == @sid and scenario == @scenario and model == @name').iloc[0]
                    difference=max(abs(measured['mse']-old.mse),abs(measured['detail_mse']-old.detail_mse))
                    assert difference<1e-12, 'Learned 02 input/classical endpoint mismatch'
                    preflight.append(difference)
        result['checks'].update(source_identities_verified=4,simulator_endpoints_verified_sources=4,
            input_classical_anchor_rows_checked=len(preflight),input_classical_anchor_max_abs_mse_difference=max(preflight),
            clipping_idempotence=True,quantization_half_step_bound=True)
        L02.download_weights(weights,provenance)
        model,device=L02.load_model(vendor_dir,weights,provenance,config)
        result['checks'].update(L02.validate_adapter(model,device,vendor_dir,config))
        result['environment'].update(cpu_threads=torch.get_num_threads(),deterministic_algorithms=torch.are_deterministic_algorithms_enabled())
        quality=[];costs=[];traces=[];acquisition=[];comparisons=[]
        snapshot(result,output_dir,'running')
        for sid,truth in sources.items():
            stages,measurements,encoded=acquisition_stages(truth,sid,config)
            acquisition.extend(measurements);result['acquisition']=pd.DataFrame(acquisition)
            (output_dir/'codec_inputs'/f'{sid}_q75.jpg').write_bytes(encoded)
            for index,(stage,y) in enumerate(stages.items()):
                print(f'{sid} | {stage} | observation {result["completed_observations"]+1}/{4*len(sources)}',flush=True)
                meta=dict(source_id=sid,stage=stage,stage_index=index)
                estimates={'observed':np.clip(y,0,1)};tic=time.perf_counter()
                estimates['gradient_nominal']=B01.inverse_spectrum(np.fft.fft2(y,axes=(0,1)),config['nominal_sigma'],'gradient',config['gradient_lambda'])
                costs.append(dict(**meta,model='gradient_nominal',elapsed_seconds=time.perf_counter()-tic,denoiser_calls=0))
                for name,sigma,only in [('dpir_nominal',config['nominal_sigma'],False),('dpir_oracle_blur',config['true_sigmas'][0],False),('drunet_denoise_only',config['nominal_sigma'],True)]:
                    x,cost,trace=L02.reconstruct(y,sigma,model,device,config,denoise_only=only)
                    estimates[name]=x;costs.append(dict(**meta,model=name,**cost));traces.extend(dict(**meta,model=name,**t) for t in trace)
                    print(f'  {MODEL_LABELS[name]}: {cost["elapsed_seconds"]:.2f}s',flush=True)
                arrays={'supplied_observation':y}
                for name in MODELS:
                    estimate=estimates[name];measured,rp,dp=errors(truth,estimate,config)
                    quality.append(dict(**meta,model=name,**measured))
                    arrays[name]=estimate.astype(np.float32) if name.startswith(('dpir','drunet')) else estimate
                    arrays[name+'__rgb_patch_error']=rp;arrays[name+'__detail_patch_error']=dp
                    if stage in ['linear_float','jpeg_q75']:
                        scenario='blur_noise' if stage=='linear_float' else 'blur_noise_jpeg'
                        old=anchors.query('source_id == @sid and scenario == @scenario and model == @name').iloc[0]
                        comparisons.append(dict(**meta,model=name,anchor_scenario=scenario,
                            delta_mse_from_colab=measured['mse']-old.mse,delta_detail_mse_from_colab=measured['detail_mse']-old.detail_mse,
                            delta_psnr_db_from_colab=measured['psnr_db']-old.psnr_db))
                np.savez_compressed(output_dir/'predictions'/f'{sid}_{stage}.npz',**arrays)
                result.update(quality=pd.DataFrame(quality),compute=pd.DataFrame(costs),trajectories=pd.DataFrame(traces),endpoint_comparison=pd.DataFrame(comparisons))
                result['completed_observations']+=1
                snapshot(result,output_dir,'running')
        result['summary'],result['stage_deltas'],result['model_gaps']=summaries(result['quality'])
        n=4*len(sources)
        assert len(result['quality'])==5*n and len(result['compute'])==4*n and len(result['trajectories'])==16*n
        assert not result['quality'].duplicated(['source_id','stage','model']).any()
        assert result['compute'].denoiser_calls.sum()==17*n
        for (sid,name),frame in result['stage_deltas'].groupby(['source_id','model']):
            endpoint=result['quality'].query('source_id == @sid and model == @name').sort_values('stage_index')
            assert abs(frame.delta_detail_mse.sum()-(endpoint.iloc[-1].detail_mse-endpoint.iloc[0].detail_mse))<1e-15
        result['checks'].update(quality_rows=len(result['quality']),stage_delta_rows=len(result['stage_deltas']),
            observation_count=n,denoiser_calls=int(result['compute'].denoiser_calls.sum()),paired_deltas_telescope=True)
        result['checks'].update(verify_saved_predictions(result,output_dir,sources))
        assert all(sha256(Path(data_dir)/r.filename)==r.sha256 for r in full_manifest.itertuples())
        result['checks']['source_files_unchanged']=True
        result['figures']=plot_results(result,output_dir,sources)
        snapshot(result,output_dir,'complete_for_configured_subset')
        return result
    except Exception as error:
        snapshot(result,output_dir,'failed',error)
        raise


def verify_and_zip(output_dir):
    output_dir=Path(output_dir)
    manifest=json.loads((output_dir/'export_manifest.json').read_text())
    status=json.loads((output_dir/'status.json').read_text())
    assert status['status']=='complete_for_configured_subset', 'Only completed configured runs are packaged'
    expected={r['name'] for r in manifest['files']}
    actual={str(p.relative_to(output_dir)) for p in output_dir.rglob('*') if p.is_file() and p.name!='export_manifest.json'}
    assert expected==actual and len(expected)==len(manifest['files'])
    for row in manifest['files']:
        path=output_dir/row['name'];assert path.stat().st_size==row['bytes'] and sha256(path)==row['sha256']
    destination=output_dir.with_suffix('.zip')
    assert not destination.exists(), f'Existing ZIP preserved: {destination}'
    with zipfile.ZipFile(destination,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
        for path in sorted(output_dir.rglob('*')):
            if path.is_file():z.write(path,arcname=str(Path(output_dir.name)/path.relative_to(output_dir)))
    with zipfile.ZipFile(destination) as z:
        assert z.testzip() is None
        for row in manifest['files']:
            data=z.read(output_dir.name+'/'+row['name'])
            assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
    receipt=dict(zip_name=destination.name,zip_bytes=destination.stat().st_size,zip_sha256=sha256(destination),
        verified_result_files=len(expected),configured_observations=status['completed_observations'],
        full_design_complete=status['full_design_complete'])
    destination.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return destination,receipt
