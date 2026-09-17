"""Frozen DRUNet/DPIR-style development adapter; no independent-test claims.

Caller supplies the audited Baseline 01 module as B01, the official vendor
directory, the provenance manifest and the expected source-image hashes.
"""
import hashlib
import importlib.util
import json
import os
import platform
import resource
import sys
import time
import types
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import PIL
import torch

B01 = None
CONFIG = {
    'source_ids': ['0801', '0802', '0803', '0804'], 'seed': 20260917,
    'crop_size': 512, 'context_border': 32, 'true_sigmas': [1.6],
    'noise_stds': [2 / 255], 'nominal_sigma': 1.0, 'nominal_noise_std': 2 / 255,
    'scenarios': ['blur_noise', 'blur_noise_jpeg'], 'jpeg_quality': 75,
    'jpeg_subsampling': 0, 'gradient_lambda': 0.05, 'iterations': 8,
    'model_sigma_start_255': 49.0, 'model_sigma_end_255': 2.0,
    'prior_tradeoff': 0.23, 'periodic_x8': True,
    'operator_sigmas': [0.8, 1.0, 1.2], 'outer_rotations': [0, 1, 2],
    'patch_size': 16, 'coverages': [0.5, 0.75, 0.9, 1.0],
    'detail_blur_sigma': 1.0, 'detail_rmse_tolerances': [0.025, 0.05, 0.10],
    'cpu_threads': 4, 'role': 'development_only',
    'model_information': 'fixed nominal blur/noise; true blur only in oracle diagnostic',
    'uncertainty_interpretation': 'heuristic sensitivities; not posterior samples or calibrated uncertainty',
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def download_weights(destination, provenance):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        partial = destination.with_suffix('.part')
        try:
            with urllib.request.urlopen(provenance['weight_url'], timeout=60) as response, partial.open('wb') as out:
                while True:
                    chunk = response.read(4 * 1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
            assert partial.stat().st_size == provenance['weight_bytes'], 'Incomplete checkpoint download'
            assert digest(partial) == provenance['weight_sha256'], 'Checkpoint hash mismatch'
            partial.replace(destination)
        finally:
            if partial.exists():
                partial.unlink()
    assert destination.stat().st_size == provenance['weight_bytes']
    assert digest(destination) == provenance['weight_sha256'], 'Cached checkpoint mismatch'
    return destination


def load_model(vendor_dir, checkpoint, provenance, config):
    vendor_dir = Path(vendor_dir)
    for relative, expected in provenance['files'].items():
        assert digest(vendor_dir / relative) == expected, f'Vendor file changed: {relative}'
    torch.set_num_threads(config['cpu_threads'])
    torch.manual_seed(config['seed'])
    torch.use_deterministic_algorithms(True)
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cuda.matmul.allow_tf32 = False
    # Private module names prevent collisions with another notebook's `models`.
    spec = importlib.util.spec_from_file_location('dpir02_basicblock', vendor_dir / 'models/basicblock.py')
    basic = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = basic
    spec.loader.exec_module(basic)
    network = types.ModuleType('dpir02_network')
    source = (vendor_dir / 'models/network_unet.py').read_text()
    assert source.count('import models.basicblock as B') == 1
    exec(compile(source.replace('import models.basicblock as B', 'import dpir02_basicblock as B'),
                 str(vendor_dir / 'models/network_unet.py'), 'exec'), network.__dict__)
    model = network.UNetRes(in_nc=4, out_nc=3, nc=[64, 128, 256, 512], nb=4,
        act_mode='R', downsample_mode='strideconv', upsample_mode='convtranspose')
    weights = torch.load(checkpoint, map_location='cpu', weights_only=True)
    assert isinstance(weights, dict) and all(isinstance(v, torch.Tensor) for v in weights.values())
    model.load_state_dict(weights, strict=True)
    model.eval().requires_grad_(False)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    assert sum(p.numel() for p in model.parameters()) == 32640960
    print(f'Loaded verified DRUNet: 32,640,960 parameters; device={device}', flush=True)
    return model, device


def augment(x, mode):
    # Same mode ordering as official utils_image.augment_img_tensor4.
    if mode == 0: return x
    if mode == 1: return x.rot90(1, [2, 3]).flip([2])
    if mode == 2: return x.flip([2])
    if mode == 3: return x.rot90(3, [2, 3])
    if mode == 4: return x.rot90(2, [2, 3]).flip([2])
    if mode == 5: return x.rot90(1, [2, 3])
    if mode == 6: return x.rot90(2, [2, 3])
    if mode == 7: return x.rot90(3, [2, 3]).flip([2])
    raise ValueError(mode)


def undo_augment(x, mode):
    return augment(x, 8 - mode if mode in (3, 5) else mode)


def schedule(config):
    sigmas = np.logspace(np.log10(config['model_sigma_start_255']),
        np.log10(config['model_sigma_end_255']), config['iterations']).astype(np.float32) / 255
    rhos = np.array([config['prior_tradeoff'] * config['nominal_noise_std']**2 / s**2
                    for s in sigmas], dtype=np.float32)
    return rhos, sigmas


def data_step(z, fy, h, rho):
    return torch.fft.ifft2((h.conj() * fy + rho * torch.fft.fft2(z)) /
                           (h.abs().square() + rho)).real


def sync(device):
    if device.type == 'cuda':
        torch.cuda.synchronize(device)


def to_tensor(image, device):
    return torch.from_numpy(np.ascontiguousarray(image.transpose(2, 0, 1), dtype=np.float32))[None].to(device)


def reconstruct(observation, blur_sigma, model, device, config, denoise_only=False):
    assert observation.ndim == 3 and observation.shape[-1] == 3
    assert observation.shape[0] % 8 == observation.shape[1] % 8 == 0
    sync(device)
    if device.type == 'cuda': torch.cuda.reset_peak_memory_stats(device)
    tic = time.perf_counter()
    trace = []
    with torch.inference_mode():
        y = to_tensor(observation, device)
        z = y.clone()
        if denoise_only:
            sigma = config['nominal_noise_std']
            z = model(torch.cat([z, torch.full_like(z[:, :1], sigma)], dim=1))
            calls = 1
        else:
            h = torch.as_tensor(B01.transfer(observation.shape[:2], blur_sigma),
                                dtype=torch.float32, device=device)[None, None]
            fy = torch.fft.fft2(y)
            rhos, sigmas = schedule(config)
            for i, (rho, sigma) in enumerate(zip(rhos, sigmas)):
                previous = z
                x = data_step(z, fy, h, float(rho))
                mode = i % 8 if config['periodic_x8'] else 0
                x = augment(x, mode)
                x = model(torch.cat([x, torch.full_like(x[:, :1], float(sigma))], dim=1))
                z = undo_augment(x, mode)
                assert bool(z.isfinite().all()), f'Non-finite learned output at iteration {i}'
                residual = torch.fft.ifft2(torch.fft.fft2(z) * h).real - y
                trace.append(dict(iteration=i + 1, rho=float(rho), denoiser_sigma=float(sigma),
                    iterate_change_mse=float((z - previous).square().mean()),
                    measurement_residual_mse=float(residual.square().mean())))
            calls = config['iterations']
        assert bool(z.isfinite().all())
        clipped_fraction = float(((z < 0) | (z > 1)).float().mean())
        result = z.clamp(0, 1).squeeze(0).permute(1, 2, 0).cpu().numpy().astype(np.float64)
    sync(device)
    timing = dict(elapsed_seconds=time.perf_counter() - tic, denoiser_calls=calls,
        input_height=observation.shape[0], input_width=observation.shape[1],
        clipped_fraction=clipped_fraction,
        peak_cuda_allocated_mib=(torch.cuda.max_memory_allocated(device) / 2**20 if device.type == 'cuda' else None),
        process_peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
    return result, timing, trace


def validate_adapter(model, device, vendor_dir, config):
    # Independent tiny dense objective, including a nonzero HQS prior centre.
    shape = (5, 6); n = int(np.prod(shape)); eye = np.eye(n)
    a = np.column_stack([B01.apply(eye[:, j].reshape(*shape, 1), 1.3).ravel() for j in range(n)])
    rng = np.random.default_rng(37)
    y, z = rng.normal(size=(2, *shape)); rho = .03
    dense = np.linalg.solve(a.T @ a + rho * np.eye(n), a.T @ y.ravel() + rho * z.ravel())
    ht = torch.from_numpy(B01.transfer(shape, 1.3))
    actual = data_step(torch.from_numpy(z), torch.fft.fft2(torch.from_numpy(y)), ht, rho).numpy()
    err = float(abs(dense - actual.ravel()).max()); assert err < 1e-10
    for mode in range(8):
        x = torch.arange(1 * 3 * 16 * 24).reshape(1, 3, 16, 24)
        assert torch.equal(undo_augment(augment(x, mode), mode), x)
    image = rng.normal(size=(32, 40, 3))
    for rotation in config['outer_rotations']:
        assert np.allclose(B01.apply(np.rot90(image, rotation), 1.3),
                           np.rot90(B01.apply(image, 1.3), rotation), atol=1e-12)
    spec = importlib.util.spec_from_file_location('dpir02_schedule', Path(vendor_dir) / 'utils/utils_pnp.py')
    official = importlib.util.module_from_spec(spec); spec.loader.exec_module(official)
    er, es = official.get_rho_sigma(sigma=config['nominal_noise_std'], iter_num=config['iterations'],
        modelSigma1=config['model_sigma_start_255'], modelSigma2=config['model_sigma_end_255'], w=1.0)
    ar, ass = schedule(config)
    assert np.allclose(ar, er, rtol=1e-6) and np.array_equal(ass, es)
    # Smoke test actual learned weights, including an independent repeat.
    x = torch.zeros(1, 4, 64, 64, device=device); x[:, 3] = 2 / 255
    with torch.inference_mode():
        one, two = model(x), model(x)
        assert one.shape == (1, 3, 64, 64) and bool(one.isfinite().all())
        assert torch.equal(one, two)
    return dict(dense_hqs_max_abs_error=err, transform_inverse_checks=True,
        isotropic_operator_rotation_equivariance=True, official_schedule_matches=True,
        strict_weight_load=True, learned_smoke_finite=True, repeat_smoke_identical=True)


def detail(image, config):
    return image - B01.apply(image, config['detail_blur_sigma'])


def evaluate_scores(truth, nominal, observation, operators, transforms, config):
    inside = lambda x: B01.interior(x, config)
    pool = lambda x: B01.patch_mean(x, config['patch_size']).ravel()
    rgb_error = pool(np.mean((inside(nominal) - inside(truth))**2, axis=-1))
    detail_error = pool(np.mean(inside(detail(nominal, config) - detail(truth, config))**2, axis=-1))
    gy, gx = np.gradient(nominal.mean(axis=-1))
    raw_scores = {
        'operator_spread_detail': np.sqrt(np.var([detail(x, config) for x in operators], axis=0).mean(axis=-1)),
        'image_transform_spread_detail': np.sqrt(np.var([detail(x, config) for x in transforms], axis=0).mean(axis=-1)),
        'operator_spread_rgb': np.sqrt(np.var(operators, axis=0).mean(axis=-1)),
        'measurement_residual': np.sqrt(np.mean((B01.apply(nominal, config['nominal_sigma']) - observation)**2, axis=-1)),
        'image_gradient': np.hypot(gx, gy),
    }
    scores = {name: pool(inside(value)) for name, value in raw_scores.items()}
    gy, gx = np.gradient(inside(truth).mean(axis=-1)); texture = pool(np.hypot(gx, gy))
    textured = np.argsort(texture, kind='stable')[-int(np.ceil(len(texture) / 4)):]
    rows = []
    for region, ids in [('all', np.arange(len(rgb_error))), ('textured_quartile', textured)]:
        re, de = rgb_error[ids], detail_error[ids]
        for name, score in list(scores.items()) + [('random_expected', None), ('oracle_detail_error', detail_error)]:
            order = None if score is None else np.lexsort((np.random.default_rng(82).random(len(ids)), score[ids]))
            for coverage in config['coverages']:
                count = int(np.ceil(coverage * len(ids)))
                chosen = np.arange(len(ids)) if order is None else order[:count]
                # Random's reported risk is its exact expectation, not an actual selected mask.
                row = dict(region=region, score=name, coverage=coverage,
                    available_patches=len(ids), retained_patches=count,
                    rgb_mse=float(re[chosen].mean()), detail_mse=float(de[chosen].mean()))
                for threshold in config['detail_rmse_tolerances']:
                    row[f'bad_detail_rate_{threshold:g}'] = float((np.sqrt(de[chosen]) > threshold).mean())
                if coverage == 1:
                    assert np.isclose(row['rgb_mse'], re.mean()) and np.isclose(row['detail_mse'], de.mean())
                if order is not None:
                    oracle = np.sort(de)[:count].mean()
                    assert row['detail_mse'] >= oracle - 1e-12
                rows.append(row)
    return pd.DataFrame(rows), dict(rgb_patch_error=rgb_error, detail_patch_error=detail_error,
        reference_texture=texture, **scores)


def plot_results(quality, curves, trajectories, examples, output_dir):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False})
    figs = []; scenarios = quality.scenario.unique().tolist()
    fig, axes = plt.subplots(1, len(scenarios), figsize=(6.2 * len(scenarios), 4.2), squeeze=False)
    for ax, scenario in zip(axes[0], scenarios):
        q = quality[quality.scenario == scenario].groupby('model').mse.mean()
        order = ['observed', 'gradient_nominal', 'drunet_denoise_only', 'dpir_nominal', 'dpir_oracle_blur']
        values = -10 * np.log10(q.reindex(order))
        ax.barh(range(len(order)), values, color=['#777777','#C46F28','#8B5C94','#236A9B','#599795'])
        ax.set_yticks(range(len(order)), [x.replace('_', ' ') for x in order]); ax.invert_yaxis()
        ax.set_xlabel('Pooled RGB PSNR (dB)'); ax.set_title(scenario.replace('_', ' + ')); ax.set_xlim(left=0)
    fig.suptitle('Learned baseline development | Executed sources only')
    fig.tight_layout(); fig.savefig(output_dir / 'quality.png', dpi=140); figs.append(fig)
    fig, axes = plt.subplots(2, len(scenarios), figsize=(6.2 * len(scenarios), 7.5), squeeze=False)
    palette = {'operator_spread_detail':'#236A9B', 'image_transform_spread_detail':'#8B5C94',
        'measurement_residual':'#C46F28', 'image_gradient':'#778839', 'random_expected':'#666666'}
    for col, scenario in enumerate(scenarios):
        for row, region in enumerate(['all','textured_quartile']):
            ax = axes[row,col]
            subset = curves[(curves.scenario == scenario) & (curves.region == region)]
            for (name,color),style in zip(palette.items(),['-o','--s','-.^',':D','--']):
                s = subset[subset.score == name].groupby('coverage').detail_mse.mean()
                ax.plot(s.index*100,s.values*1e4,style,color=color,label=name.replace('_',' '),markersize=4)
            ax.set_title(f'{scenario} | {region}'.replace('_',' ')); ax.set_ylim(bottom=0)
            ax.set_ylabel('Retained detail MSE (× 0.0001)'); ax.set_xlabel('Patches retained within stratum (%)')
    handles,labels=axes[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',ncol=2,fontsize=8,frameon=False)
    fig.suptitle('DPIR detail selection | Heuristic scores; no calibration guarantee')
    fig.tight_layout(rect=(0,.12,1,.94)); fig.savefig(output_dir/'detail_risk_coverage.png',dpi=140);figs.append(fig)
    fig, axes=plt.subplots(len(examples),4,figsize=(11,2.7*len(examples)),squeeze=False)
    for i,ex in enumerate(examples):
        for j,key in enumerate(['reference','observed','gradient_nominal','dpir_nominal']):
            axes[i,j].imshow(ex[key]);axes[i,j].axis('off');axes[i,j].set_title(ex['source_id']+' | '+key.replace('_',' '))
    fig.suptitle('Full-resolution anchor crops | Linear condition when available')
    fig.tight_layout();fig.savefig(output_dir/'reconstruction_examples.png',dpi=120);figs.append(fig)
    fig, axes=plt.subplots(1,2,figsize=(11,4.2))
    for (sid,scenario),frame in trajectories[trajectories.variant=='nominal'].groupby(['source_id','scenario']):
        axes[0].plot(frame.iteration,frame.measurement_residual_mse,label=sid+' '+scenario)
        axes[1].plot(frame.iteration,frame.iterate_change_mse,label=sid+' '+scenario)
    for ax,title in zip(axes,['Measurement residual MSE','Iterate-change MSE']):
        ax.set_yscale('log');ax.set_xlabel('Iteration');ax.set_title(title)
    axes[1].legend(fontsize=7,frameon=False)
    fig.suptitle('Nominal DPIR trajectories | Changing schedules are not convergence proofs')
    fig.tight_layout();fig.savefig(output_dir/'iteration_trajectories.png',dpi=140);figs.append(fig)
    return figs


def save_snapshot(result, output_dir, status):
    for name in ['quality','summary','compute','curves','trajectories','source_manifest']:
        if name in result: result[name].to_csv(output_dir / (name+'.csv'),index=False)
    for name in ['config','checks','environment','provenance']:
        (output_dir / (name+'.json')).write_text(json.dumps(result[name],indent=2)+'\n')
    (output_dir/'status.json').write_text(json.dumps({'status':status,
        'completed_observations':result.get('completed_observations',0),
        'planned_observations':len(result['config']['source_ids'])*len(result['config']['scenarios']),
        'updated_utc':datetime.now(timezone.utc).isoformat()},indent=2)+'\n')
    files=sorted(p for p in output_dir.rglob('*') if p.is_file() and p.name!='export_manifest.json')
    manifest=[{'name':str(p.relative_to(output_dir)),'bytes':p.stat().st_size,'sha256':digest(p)} for p in files]
    (output_dir/'export_manifest.json').write_text(json.dumps({'experiment':'learned_02','role':'development_only','files':manifest},indent=2)+'\n')
    assert all(digest(output_dir/r['name'])==r['sha256'] for r in manifest)


def run(data_dir, output_dir, vendor_dir, checkpoint, provenance, expected_rgb_hashes, config=None):
    config=json.loads(json.dumps(CONFIG if config is None else config))
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=False)
    (output_dir/'predictions').mkdir()
    model,device=load_model(vendor_dir,checkpoint,provenance,config)
    checks=validate_adapter(model,device,vendor_dir,config)
    sources,manifest=B01.load_sources(data_dir,expected_rgb_hashes,config)
    result=dict(config=config,checks=checks,provenance=provenance,source_manifest=manifest,
        environment={'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,
            'torch':torch.__version__,'pillow':PIL.__version__,'matplotlib':matplotlib.__version__,
            'device':str(device),'cuda_name':torch.cuda.get_device_name(device) if device.type=='cuda' else None,
            'cpu_threads':torch.get_num_threads(),'deterministic_algorithms':torch.are_deterministic_algorithms_enabled(),
            'cpu_memory_note':'process lifetime peak RSS; not isolated per-inference memory'},completed_observations=0)
    save_snapshot(result,output_dir,'running')
    quality=[];compute=[];curves=[];trajectories=[];examples=[]
    for sid,truth in sources.items():
        for meta,y in B01.observations(truth,sid,config):
            inside=lambda x:B01.interior(x,config)
            print(f'Starting {sid} | {meta["scenario"]}',flush=True)
            estimates={'observed':np.clip(y,0,1)}
            tic=time.perf_counter()
            estimates['gradient_nominal']=B01.inverse_spectrum(np.fft.fft2(y,axes=(0,1)),
                config['nominal_sigma'],'gradient',config['gradient_lambda'])
            compute.append(dict(**meta,variant='gradient_nominal',elapsed_seconds=time.perf_counter()-tic,denoiser_calls=0))
            learned={}
            variants=[('nominal',config['nominal_sigma'],0,False),('oracle_blur',meta['true_sigma'],0,False),
                ('operator_0.8',config['operator_sigmas'][0],0,False),('operator_1.2',config['operator_sigmas'][2],0,False),
                ('rotation_90',config['nominal_sigma'],1,False),('rotation_180',config['nominal_sigma'],2,False),
                ('denoise_only',config['nominal_sigma'],0,True)]
            for name,sigma,rotation,only in variants:
                observed=np.rot90(y,rotation).copy()
                x,cost,trace=reconstruct(observed,sigma,model,device,config,denoise_only=only)
                learned[name]=np.rot90(x,-rotation).copy()
                compute.append(dict(**meta,variant=name,**cost))
                trajectories.extend(dict(**meta,variant=name,**t) for t in trace)
                pd.DataFrame(compute).to_csv(output_dir/'compute.csv',index=False)
                print(f'  {name}: {cost["elapsed_seconds"]:.1f}s, {cost["denoiser_calls"]} denoiser calls',flush=True)
            estimates.update(dpir_nominal=learned['nominal'],dpir_oracle_blur=learned['oracle_blur'],drunet_denoise_only=learned['denoise_only'])
            for name,x in estimates.items():
                mse=float(np.mean((inside(x)-inside(truth))**2))
                dmse=float(np.mean(inside(detail(x,config)-detail(truth,config))**2))
                quality.append(dict(**meta,model=name,mse=mse,psnr_db=B01.psnr(mse),detail_mse=dmse))
            curve,patches=evaluate_scores(truth,learned['nominal'],y,
                [learned['operator_0.8'],learned['nominal'],learned['operator_1.2']],
                [learned['nominal'],learned['rotation_90'],learned['rotation_180']],config)
            for k,v in meta.items():curve[k]=v
            curves.append(curve)
            np.savez_compressed(output_dir/'predictions'/f'{sid}_{meta["scenario"]}.npz',
                nominal_reconstruction=learned['nominal'].astype(np.float32),**patches)
            if meta['scenario']==config['scenarios'][0]:
                examples.append(dict(source_id=sid,reference=inside(truth),**{k:inside(v) for k,v in estimates.items()}))
            result.update(quality=pd.DataFrame(quality),compute=pd.DataFrame(compute),curves=pd.concat(curves,ignore_index=True),trajectories=pd.DataFrame(trajectories))
            result['summary']=result['quality'].groupby(['scenario','model'],as_index=False).agg(mean_mse=('mse','mean'),mean_detail_mse=('detail_mse','mean'),sources=('source_id','nunique'),observations=('mse','size'))
            result['summary']['pooled_psnr_db']=result['summary'].mean_mse.map(B01.psnr)
            result['completed_observations']+=1
            save_snapshot(result,output_dir,'running')
    n=len(sources)*len(config['scenarios'])
    assert len(result['quality'])==5*n and len(result['curves'])==56*n
    assert result['compute'].denoiser_calls.sum()==49*n
    assert all(digest(Path(data_dir)/r.filename)==r.sha256 for r in manifest.itertuples())
    checks.update(source_count=len(sources),observation_count=n,quality_rows=len(result['quality']),
        risk_rows=len(result['curves']),denoiser_calls=int(result['compute'].denoiser_calls.sum()),input_files_unchanged=True)
    result['figures']=plot_results(result['quality'],result['curves'],result['trajectories'],examples,output_dir)
    for figure in result['figures']:plt.close(figure)
    save_snapshot(result,output_dir,'complete_for_configured_subset')
    return result
