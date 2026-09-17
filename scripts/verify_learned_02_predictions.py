"""Independent readback of stored nominal predictions and patch-risk tables."""
import argparse,ast,hashlib,importlib.util,json
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--run-dir',type=Path,required=True)
parser.add_argument('--data-dir',type=Path,required=True)
parser.add_argument('--repo-dir',type=Path,required=True)
parser.add_argument('--output-dir',type=Path,required=True)
args=parser.parse_args()
run,repo,out=args.run_dir,args.repo_dir,args.output_dir
out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cfg=json.loads((run/'config.json').read_text())
provenance=json.loads((run/'provenance.json').read_text())
status=json.loads((run/'status.json').read_text())
assert status['completed_observations']==status['planned_observations']==8
assert status['status']=='complete_for_configured_subset'
assert sha(repo/'experiments/learned_02/learned.py')==provenance['adapter_source_sha256']
assert sha(repo/'experiments/baseline_01/baseline.py')==provenance['baseline_helper_sha256']
config_node=next(n for n in ast.parse((repo/'experiments/learned_02/learned.py').read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CONFIG' for t in n.targets))
expected_cfg=eval(compile(ast.Expression(config_node.value),'<audited fixed configuration>','eval'),{'__builtins__':{}})
assert cfg==expected_cfg
expected_prov=json.loads((repo/'experiments/learned_02/provenance.json').read_text())
assert all(provenance[k]==v for k,v in expected_prov.items())
for rel,expected in provenance['files'].items():assert sha(repo/'experiments/learned_02/vendor/dpir'/rel)==expected
# Load only the already-audited simulator; no Torch, checkpoint load or model inference.
spec=importlib.util.spec_from_file_location('baseline01_archive_audit',repo/'experiments/baseline_01/baseline.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
manifest=json.loads((repo/'data/manifests/div2k_development_100.json').read_text())
expected_rgb={r['source_id'].split(':')[1]:r['source_pixels_sha256'] for r in manifest['records']}
sources,local_manifest=b.load_sources(args.data_dir,expected_rgb,cfg)
reported_manifest=pd.read_csv(run/'source_manifest.csv',dtype={'source_id':str})
pd.testing.assert_frame_equal(local_manifest,reported_manifest,check_dtype=False)
quality=pd.read_csv(run/'quality.csv',dtype={'source_id':str})
curves=pd.read_csv(run/'curves.csv',dtype={'source_id':str})
prior=repo/'experiments/learned_02/colab_review_20260917/csv_exports'
assert all((run/p.name).read_bytes()==p.read_bytes() for p in prior.glob('*.csv'))
# Recompute the Fourier detail transform directly from its definition.
def detail(x):
    h,w=x.shape[:2]
    fy=np.fft.fftfreq(h)[:,None];fx=np.fft.fftfreq(w)[None,:]
    transfer=np.exp(-2*np.pi**2*(fx**2+fy**2))
    return x-np.fft.ifft2(np.fft.fft2(x,axes=(0,1))*transfer[:,:,None],axes=(0,1)).real

def inside(x):return x[32:-32,32:-32]
def pool(x):return x.reshape(32,16,32,16).mean(axis=(1,3)).ravel()
expected_keys={'nominal_reconstruction','rgb_patch_error','detail_patch_error','reference_texture','operator_spread_detail','image_transform_spread_detail','operator_spread_rgb','measurement_residual','image_gradient'}
max_rgb=max_detail=max_curve=max_bad=max_texture=max_cheap=max_quality=0.
records=[];montage=[];curve_rows=0
for sid,truth in sources.items():
    for meta,y in b.observations(truth,sid,cfg):
        scenario=meta['scenario'];npz_path=run/'predictions'/f'{sid}_{scenario}.npz'
        with np.load(npz_path,allow_pickle=False) as saved:
            assert set(saved.files)==expected_keys
            assert saved['nominal_reconstruction'].shape==(576,576,3)
            assert saved['nominal_reconstruction'].dtype==np.float32
            for key in expected_keys:
                assert np.isfinite(saved[key]).all()
                if key!='nominal_reconstruction':assert saved[key].shape==(1024,)
                assert saved[key].min()>=0
            pred=saved['nominal_reconstruction'].astype(np.float64)
            assert pred.max()<=1
            rgb=pool(((inside(pred)-inside(truth))**2).mean(axis=2))
            de=pool((inside(detail(pred)-detail(truth))**2).mean(axis=2))
            max_rgb=max(max_rgb,float(abs(rgb-saved['rgb_patch_error']).max()))
            max_detail=max(max_detail,float(abs(de-saved['detail_patch_error']).max()))
            assert np.allclose(rgb,saved['rgb_patch_error'],atol=1e-14,rtol=0)
            assert np.allclose(de,saved['detail_patch_error'],atol=1e-14,rtol=0)
            gy,gx=np.gradient(inside(truth).mean(axis=2));texture=pool(np.hypot(gx,gy))
            max_texture=max(max_texture,float(abs(texture-saved['reference_texture']).max()))
            assert np.allclose(texture,saved['reference_texture'],atol=1e-14,rtol=0)
            gy,gx=np.gradient(pred.mean(axis=2));gradient=pool(inside(np.hypot(gx,gy)))
            residual=pool(inside(np.sqrt(((b.apply(pred,1.0)-y)**2).mean(axis=2))))
            for key,array in [('measurement_residual',residual),('image_gradient',gradient)]:
                max_cheap=max(max_cheap,float(abs(array-saved[key]).max()))
                assert np.allclose(array,saved[key],atol=1e-13,rtol=0)
            gradient_pred=b.inverse_spectrum(np.fft.fft2(y,axes=(0,1)),1.0,'gradient',.05)
            for model,x in [('observed',np.clip(y,0,1)),('gradient_nominal',gradient_pred),('dpir_nominal',pred)]:
                row=quality[(quality.source_id==sid)&(quality.scenario==scenario)&(quality.model==model)].iloc[0]
                mse=float(((inside(x)-inside(truth))**2).mean())
                dmse=float((inside(detail(x)-detail(truth))**2).mean())
                error=max(abs(mse-row.mse),abs(dmse-row.detail_mse));max_quality=max(max_quality,error)
                assert error<1e-13
                assert abs(-10*np.log10(mse)-row.psnr_db)<1e-9
            local_curves=curves[(curves.source_id==sid)&(curves.scenario==scenario)]
            textured=np.argsort(texture,kind='stable')[-256:]
            for row in local_curves.itertuples(index=False,name=None):
                # Column names with decimal points cannot be safely read as namedtuple attributes.
                row=dict(zip(local_curves.columns,row))
                ids=np.arange(1024) if row['region']=='all' else textured
                keep=int(np.ceil(row['coverage']*len(ids)))
                if row['score']=='random_expected':chosen=ids
                else:
                    score=de if row['score']=='oracle_detail_error' else saved[row['score']]
                    order=np.lexsort((np.random.default_rng(82).random(len(ids)),score[ids]))
                    chosen=ids[order[:keep]]
                assert row['available_patches']==len(ids) and row['retained_patches']==keep
                for column,array in [('rgb_mse',rgb),('detail_mse',de)]:
                    error=abs(array[chosen].mean()-row[column]);max_curve=max(max_curve,float(error));assert error<1e-13
                for tolerance in [.025,.05,.1]:
                    error=abs((np.sqrt(de[chosen])>tolerance).mean()-row[f'bad_detail_rate_{tolerance:g}'])
                    max_bad=max(max_bad,float(error));assert error<1e-12
                curve_rows+=1
            records.append(dict(source_id=sid,scenario=scenario,shape=list(pred.shape),dtype='float32',min=float(pred.min()),max=float(pred.max()),rgb_mse=float(rgb.mean()),detail_mse=float(de.mean()),npz_sha256=sha(npz_path),risk_rows_checked=len(local_curves)))
            if scenario=='blur_noise_jpeg':montage.append(dict(source_id=sid,reference=inside(truth),observed=inside(np.clip(y,0,1)),gradient=inside(gradient_pred),learned=inside(pred)))
assert len(records)==8 and curve_rows==448
pd.DataFrame(records).to_csv(out/'prediction_readback.csv',index=False)
# This is a new review visualization of the already-saved JPEG predictions.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,axes=plt.subplots(4,4,figsize=(12,12))
for i,example in enumerate(montage):
    for j,key in enumerate(['reference','observed','gradient','learned']):
        axes[i,j].imshow(example[key]);axes[i,j].axis('off');axes[i,j].set_title(example['source_id']+' | '+key)
fig.suptitle('JPEG-chain readback | Stored nominal DPIR predictions; regenerated controls',fontsize=13)
fig.tight_layout(rect=(0,0,1,.97));fig.savefig(out/'jpeg_prediction_readback.png',dpi=140);plt.close(fig)
audit=dict(status='passed',source_images_rehashed=4,source_manifest_matches_local_inputs=True,
    configuration_matches_frozen_defaults=True,source_and_vendor_hashes_match_provenance=True,
    prior_six_csvs_byte_identical=True,nominal_prediction_archives_checked=8,
    prediction_dtype='float32',prediction_shape=[576,576,3],evaluation_shape=[512,512,3],
    quality_rows_independently_recomputed=24,risk_rows_recomputed=curve_rows,
    rgb_patch_error_max_abs_difference=max_rgb,detail_patch_error_max_abs_difference=max_detail,
    reference_texture_max_abs_difference=max_texture,cheap_score_max_abs_difference=max_cheap,
    quality_mse_max_abs_difference=max_quality,risk_mse_max_abs_difference=max_curve,
    bad_detail_rate_max_abs_difference=max_bad,
    original_models_not_rerun=True,
    remaining_scope_limits=['Only nominal learned predictions were stored; oracle-blur and denoising-only learned outputs were not independently regenerated.',
                           'Operator and transformation spread arrays were used to recompute rankings and risks; their construction cannot be independently repeated without the unsaved ensemble predictions or new inference.',
                           'Integrity and arithmetic checks do not establish novelty, calibration or independent-test performance.'])
(out/'prediction_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print(json.dumps(audit,indent=2))
