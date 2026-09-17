"""Independent numerical and integrity readback of an Acquisition 03 run.

No model inference. Use original source PNGs, the completed run directory and
an output path for this machine-readable audit. Not a calibration/novelty test.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
import numpy as np
import pandas as pd
from PIL import Image


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir',type=Path,required=True)
    parser.add_argument('--data-dir',type=Path,required=True)
    parser.add_argument('--audit-output',type=Path,required=True)
    args=parser.parse_args();run=args.run_dir
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    status=json.loads((run/'status.json').read_text());cfg=json.loads((run/'config.json').read_text())
    manifest=json.loads((run/'export_manifest.json').read_text())
    assert status['status']=='complete_for_configured_subset'
    files={r['name']:r for r in manifest['files']}
    assert len(files)==len(manifest['files'])
    assert set(files)=={str(p.relative_to(run)) for p in run.rglob('*') if p.is_file() and p.name!='export_manifest.json'}
    for name,row in files.items():assert (run/name).stat().st_size==row['bytes'] and sha(run/name)==row['sha256']
    source=pd.read_csv(run/'source_manifest.csv',dtype={'source_id':str})
    quality=pd.read_csv(run/'quality.csv',dtype={'source_id':str})
    acquisition=pd.read_csv(run/'acquisition.csv',dtype={'source_id':str})
    summary=pd.read_csv(run/'summary.csv');delta=pd.read_csv(run/'stage_deltas.csv',dtype={'source_id':str})
    gaps=pd.read_csv(run/'model_gaps.csv',dtype={'source_id':str})
    models=['observed','gradient_nominal','drunet_denoise_only','dpir_nominal','dpir_oracle_blur']
    stages=['linear_float','clipped_float','quantized_8bit','jpeg_q75']
    assert len(quality)==20*len(cfg['source_ids'])
    assert not quality.duplicated(['source_id','stage','model']).any()
    maximum=0.;checked=0;patch_maximum=0.
    def detail(x):
        h,w=x.shape[:2]
        htf=np.exp(-2*np.pi**2*(np.fft.fftfreq(h)[:,None]**2+np.fft.fftfreq(w)[None,:]**2))
        return x-np.fft.ifft2(np.fft.fft2(x,axes=(0,1))*htf[:,:,None],axes=(0,1)).real
    def interior(x):return x[32:-32,32:-32]
    def pool(x):return x.reshape(32,16,32,16).mean(axis=(1,3)).ravel()
    for row in source.itertuples(index=False):
        path=args.data_dir/row.filename
        with Image.open(path) as img:rgb=np.asarray(img.convert('RGB'))
        assert sha(path)==row.sha256 and hashlib.sha256(rgb.tobytes()).hexdigest()==row.rgb_sha256
    for sid in cfg['source_ids']:
        row=source.query('source_id == @sid').iloc[0]
        with Image.open(args.data_dir/row.filename) as img:rgb=np.asarray(img.convert('RGB'))
        truth=rgb[int(row.crop_top):int(row.crop_top+row.extent),int(row.crop_left):int(row.crop_left+row.extent)].astype(np.float64)/255
        supplied={}
        for stage in stages:
            with np.load(run/'predictions'/f'{sid}_{stage}.npz',allow_pickle=False) as saved:
                y=saved['supplied_observation'];supplied[stage]=y
                ar=acquisition.query('source_id == @sid and stage == @stage').iloc[0]
                assert hashlib.sha256(np.ascontiguousarray(y).tobytes()).hexdigest()==ar.observation_sha256
                for model in models:
                    x=saved[model].astype(np.float64)
                    assert x.shape==(576,576,3) and np.isfinite(x).all() and x.min()>=0 and x.max()<=1
                    re=np.mean((interior(x)-interior(truth))**2,axis=2)
                    de=np.mean(interior(detail(x)-detail(truth))**2,axis=2)
                    qr=quality.query('source_id == @sid and stage == @stage and model == @model').iloc[0]
                    for actual,recorded in [(re.mean(),qr.mse),(de.mean(),qr.detail_mse),(-10*np.log10(re.mean()),qr.psnr_db)]:
                        maximum=max(maximum,float(abs(actual-recorded)));assert abs(actual-recorded)<1e-12
                    for domain,array in [('rgb',re),('detail',de)]:
                        difference=float(abs(pool(array)-saved[model+'__'+domain+'_patch_error']).max())
                        patch_maximum=max(patch_maximum,difference);assert difference<1e-14
                    for tolerance in [.025,.05,.1]:
                        rate=np.mean(np.sqrt(pool(de))>tolerance)
                        assert abs(rate-qr[f'bad_detail_rate_{tolerance:g}'])<1e-12
                    checked+=1
        assert np.array_equal(np.clip(supplied['linear_float'],0,1),supplied['clipped_float'])
        assert np.array_equal(np.rint(supplied['clipped_float']*255).astype('uint8').astype(float)/255,supplied['quantized_8bit'])
        with Image.open(run/'codec_inputs'/f'{sid}_q75.jpg') as img:
            assert np.array_equal(np.asarray(img.convert('RGB')).astype(float)/255,supplied['jpeg_q75'])
    for row in summary.itertuples(index=False):
        q=quality[(quality.stage==row.stage)&(quality.model==row.model)]
        assert abs(q.mse.mean()-row.mean_mse)<1e-12
        assert abs(q.detail_mse.mean()-row.mean_detail_mse)<1e-12
        assert abs(-10*np.log10(q.mse.mean())-row.pooled_psnr_db)<1e-9
    for row in delta.itertuples(index=False):
        q=quality[(quality.source_id==row.source_id)&(quality.model==row.model)].set_index('stage')
        assert abs(q.loc[row.to_stage,'detail_mse']-q.loc[row.from_stage,'detail_mse']-row.delta_detail_mse)<1e-12
        assert abs(q.loc[row.to_stage,'psnr_db']-q.loc[row.from_stage,'psnr_db']-row.delta_psnr_db)<1e-9
    for row in gaps.itertuples(index=False):
        q=quality[(quality.source_id==row.source_id)&(quality.stage==row.stage)].set_index('model')
        assert abs(q.loc['dpir_nominal','detail_mse']-q.loc['gradient_nominal','detail_mse']-row.nominal_minus_classical_detail_mse)<1e-12
    zip_path=run.with_suffix('.zip')
    receipt=json.loads(zip_path.with_suffix('.receipt.json').read_text())
    assert zip_path.stat().st_size==receipt['zip_bytes'] and sha(zip_path)==receipt['zip_sha256']
    with zipfile.ZipFile(zip_path) as z:
        assert z.testzip() is None
        for name,row in files.items():assert hashlib.sha256(z.read(run.name+'/'+name)).hexdigest()==row['sha256']
    audit=dict(status='passed',configured_sources=cfg['source_ids'],observations=status['completed_observations'],
        full_design_complete=status['full_design_complete'],manifest_files_verified=len(files),
        all_source_images_rehashed=len(source),independently_recomputed_quality_rows=checked,
        max_abs_quality_difference=maximum,max_abs_patch_error_difference=patch_maximum,
        stage_construction_and_saved_codec_verified=True,summary_deltas_and_gaps_verified=True,
        zip_sha256=receipt['zip_sha256'],zip_verified=True,learned_inference_repeated=False)
    args.audit_output.parent.mkdir(parents=True,exist_ok=True)
    args.audit_output.write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit,indent=2))


if __name__=='__main__':main()
