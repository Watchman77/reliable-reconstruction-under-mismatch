"""Review a saved Acquisition 03 notebook against readable Drive CSV exports.

This does not substitute for raw prediction/manifest/ZIP verification.
"""
import argparse,base64,hashlib,importlib.util,io,json
from pathlib import Path
import numpy as np
import pandas as pd
import nbformat


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--notebook',type=Path,required=True)
    parser.add_argument('--issued-notebook',type=Path,required=True)
    parser.add_argument('--review-dir',type=Path,required=True)
    parser.add_argument('--repo-dir',type=Path,required=True)
    parser.add_argument('--data-dir',type=Path,required=True)
    args=parser.parse_args();out=args.review_dir;root=args.repo_dir
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    nb=nbformat.read(args.notebook,as_version=4);issued=nbformat.read(args.issued_notebook,as_version=4)
    nbformat.validate(nb)
    code=[c for c in nb.cells if c.cell_type=='code'];oldcode=[c for c in issued.cells if c.cell_type=='code']
    assert len(nb.cells)==len(issued.cells)==21 and len(code)==len(oldcode)==10
    assert all(c.source==d.source for c,d in zip(code,oldcode))
    assert [c.execution_count for c in code]==list(range(1,11))
    errors=[o for c in code for o in c.outputs if o.output_type=='error'];assert not errors
    stderr=[o.text for c in code for o in c.outputs if o.output_type=='stream' and o.name=='stderr'];assert not stderr
    figures=[base64.b64decode(o['data']['image/png']) for c in code for o in c.outputs if 'image/png' in o.get('data',{})]
    assert len(figures)==4
    image_dir=out/'embedded_figures' if (out/'embedded_figures').exists() else out
    for raw,name in zip(figures,['stage_quality','stage_changes','source_gaps','stage_examples']):
        assert raw==(image_dir/(name+'.png')).read_bytes()
    md_changes=[i for i,(c,d) in enumerate(zip(nb.cells,issued.cells)) if c.source!=d.source]
    assert md_changes==[20]
    text=''.join(o.text for o in code[3].outputs if o.output_type=='stream')
    start=text.index('{\n');end=text.index('\n}\n',start)+2
    checks=json.loads(text[start:end]);assert checks['observation_count']==16 and checks['quality_rows']==80 and checks['denoiser_calls']==272
    receipt_text=''.join(o.text for o in code[9].outputs if o.output_type=='stream')
    receipt=json.loads(receipt_text[:receipt_text.index('\n}\n')+2]);assert receipt['full_design_complete'] and receipt['configured_observations']==16 and receipt['verified_result_files']==38
    frames={p.stem:pd.read_csv(p,dtype={'source_id':str}) for p in (out/'csv_exports').glob('*.csv')}
    assert set(frames)=={'acquisition','compute','endpoint_comparison','model_gaps','quality','source_manifest','stage_deltas','summary','trajectories'}
    counts={'quality':80,'summary':20,'model_gaps':16,'stage_deltas':60,'endpoint_comparison':40,'acquisition':16,'compute':64,'trajectories':256,'source_manifest':4}
    for name,n in counts.items():assert len(frames[name])==n,(name,len(frames[name]))
    q=frames['quality'];c=frames['compute'];s=frames['summary'];delta=frames['stage_deltas'];gaps=frames['model_gaps'];acq=frames['acquisition']
    models=['observed','gradient_nominal','drunet_denoise_only','dpir_nominal','dpir_oracle_blur']
    stages=['linear_float','clipped_float','quantized_8bit','jpeg_q75']
    assert set(q.source_id)=={'0801','0802','0803','0804'}
    assert not q.duplicated(['source_id','stage','model']).any()
    assert all(set(x.model)==set(models) for _,x in q.groupby(['source_id','stage']))
    assert (q[['mse','detail_mse']]>0).all().all()
    assert np.isfinite(q.select_dtypes('number')).all().all()
    assert np.max(abs(q.psnr_db+10*np.log10(q.mse)))<1e-9
    tails=['bad_detail_rate_0.025','bad_detail_rate_0.05','bad_detail_rate_0.1']
    assert ((q[tails]>=0)&(q[tails]<=1)).all().all()
    assert (q[tails[0]]>=q[tails[1]]).all() and (q[tails[1]]>=q[tails[2]]).all()
    for row in s.itertuples(index=False):
        f=q[(q.stage==row.stage)&(q.model==row.model)]
        assert f.source_id.nunique()==row.sources==4
        assert abs(f.mse.mean()-row.mean_mse)<1e-15 and abs(f.detail_mse.mean()-row.mean_detail_mse)<1e-15
        assert abs(-10*np.log10(f.mse.mean())-row.pooled_psnr_db)<1e-9
    for row in delta.itertuples(index=False):
        f=q[(q.source_id==row.source_id)&(q.model==row.model)].set_index('stage')
        for metric in ['mse','detail_mse','psnr_db']:
            assert abs(f.loc[row.to_stage,metric]-f.loc[row.from_stage,metric]-getattr(row,'delta_'+metric))<1e-12
    for row in gaps.itertuples(index=False):
        f=q[(q.source_id==row.source_id)&(q.stage==row.stage)].set_index('model')
        assert abs(f.loc['dpir_nominal','detail_mse']-f.loc['gradient_nominal','detail_mse']-row.nominal_minus_classical_detail_mse)<1e-15
        assert abs(f.loc['dpir_nominal','psnr_db']-f.loc['gradient_nominal','psnr_db']-row.nominal_minus_classical_psnr_db)<1e-12
    for sid,f in gaps.groupby('source_id'):
        f=f.sort_values('stage_index')
        assert np.allclose(f.nominal_minus_classical_detail_mse.diff(),f.change_in_detail_gap,atol=1e-15,rtol=0,equal_nan=True)
        assert abs(f.change_in_detail_gap.sum()-(f.iloc[-1].nominal_minus_classical_detail_mse-f.iloc[0].nominal_minus_classical_detail_mse))<1e-15
    assert c.denoiser_calls.sum()==272
    assert all(c[c.model==m].denoiser_calls.eq(n).all() for m,n in [('gradient_nominal',0),('dpir_nominal',8),('dpir_oracle_blur',8),('drunet_denoise_only',1)])
    assert c.elapsed_seconds.gt(0).all()
    learned=c[c.model!='gradient_nominal'];assert learned.input_height.eq(576).all() and learned.input_width.eq(576).all()
    trajectories=frames['trajectories']
    assert not trajectories.duplicated(['source_id','stage','model','iteration']).any()
    assert all(list(sorted(f.iteration))==list(range(1,9)) for _,f in trajectories.groupby(['source_id','stage','model']))
    # Cross-check the embedded rendered tables with the full-precision CSVs.
    def rendered(frame,decimals,indexed=False):
        expected=frame.round(decimals).copy()
        expected=pd.read_html(io.StringIO(expected.to_html()))[0]
        return expected
    stage_changes=delta.groupby(['to_stage_index','to_stage','model'],as_index=False).agg(mean_delta_detail_mse=('delta_detail_mse','mean'),mean_delta_rgb_mse=('delta_mse','mean'),sources=('source_id','nunique'))
    tails_table=q.groupby(['stage_index','stage','model'])[tails].mean()
    cost_table=c.groupby('model',as_index=False).agg(runs=('elapsed_seconds','size'),seconds=('elapsed_seconds','sum'),denoiser_calls=('denoiser_calls','sum'))
    for filename,frame,decimals in [('table_9_0.html',s,7),('table_11_0.html',stage_changes,8),('table_13_0.html',gaps,8),('table_13_2.html',tails_table,6),('table_15_1.html',frames['endpoint_comparison'],9),('table_15_2.html',cost_table,3)]:
        table_dir=out/'rendered_tables' if (out/'rendered_tables').exists() else out
        actual=pd.read_html(io.StringIO((table_dir/filename).read_text()))[0]
        expected=rendered(frame,decimals)
        pd.testing.assert_frame_equal(actual,expected,check_dtype=False,check_exact=False,atol=5.1e-10,rtol=0)
    # Rehash source files and regenerate observations/cheap controls; no learned inference.
    def module(name,path):
        spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
    b=module('baseline03_review',root/'experiments/baseline_01/baseline.py')
    l=module('learned03_review',root/'experiments/learned_02/learned.py');l.B01=b
    d=module('diagnostic03_review',root/'experiments/acquisition_03/diagnostic.py');d.B01=b;d.L02=l
    cfg=json.loads(json.dumps(l.CONFIG));cfg['acquisition_stages']=stages;cfg['experiment']='acquisition_03'
    official=json.loads((root/'data/manifests/div2k_development_100.json').read_text())
    hashes={r['source_id'].split(':')[1]:r['source_pixels_sha256'] for r in official['records']}
    sources,source_manifest=b.load_sources(args.data_dir,hashes,cfg)
    pd.testing.assert_frame_equal(source_manifest,frames['source_manifest'],check_dtype=False)
    observation_hashes=[];cheap_max=0.;codec_hashes=[];stage_measurement_max=0.
    for sid,truth in sources.items():
        generated,measurements,encoded=d.acquisition_stages(truth,sid,cfg)
        for row in measurements:
            old=acq.query('source_id == @sid and stage == @row["stage"]').iloc[0]
            observation_hashes.append(row['observation_sha256']==old.observation_sha256)
            for key in ['minimum','maximum','changed_component_fraction_from_previous','measurement_delta_mse','linear_out_of_range_fraction']:
                difference=abs(row[key]-old[key]);stage_measurement_max=max(stage_measurement_max,difference);assert difference<1e-12
        codec_hashes.append(hashlib.sha256(encoded).hexdigest()==acq.query('source_id == @sid and stage == "jpeg_q75"').iloc[0].jpeg_sha256)
        for stage,y in generated.items():
            estimates={'observed':np.clip(y,0,1),'gradient_nominal':b.inverse_spectrum(np.fft.fft2(y,axes=(0,1)),1.,'gradient',.05)}
            for model,x in estimates.items():
                measured,_,_=d.errors(truth,x,cfg);old=q.query('source_id == @sid and stage == @stage and model == @model').iloc[0]
                difference=max(abs(measured['mse']-old.mse),abs(measured['detail_mse']-old.detail_mse));cheap_max=max(cheap_max,difference);assert difference<1e-12
    anchor=pd.read_csv(root/'experiments/learned_02/colab_review_20260917/csv_exports/quality.csv',dtype={'source_id':str})
    for row in frames['endpoint_comparison'].itertuples(index=False):
        current=q[(q.source_id==row.source_id)&(q.stage==row.stage)&(q.model==row.model)].iloc[0]
        old=anchor[(anchor.source_id==row.source_id)&(anchor.scenario==row.anchor_scenario)&(anchor.model==row.model)].iloc[0]
        for metric in ['mse','detail_mse','psnr_db']:
            assert abs(current[metric]-old[metric]-getattr(row,'delta_'+metric+'_from_colab'))<1e-12
    file_index=json.loads((out/'drive_file_index.json').read_text())
    csv_integrity=[]
    for p in sorted((out/'csv_exports').glob('*.csv')):
        f=next(x for x in file_index['files'] if x['title']==p.name)
        assert p.stat().st_size==int(f['size']);csv_integrity.append(dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)))
    all_files=[f for f in file_index['files'] if f['file_or_folder']=='file']+file_index['children']['predictions']+file_index['children']['codec_inputs']
    assert len(all_files)==39 and len(file_index['children']['predictions'])==16 and len(file_index['children']['codec_inputs'])==4
    # Descriptive derived findings, without a novelty or causal mechanism claim.
    pooled=s.pivot(index='stage',columns='model',values='pooled_psnr_db').loc[stages]
    pooled['nominal_minus_classical_db']=pooled.dpir_nominal-pooled.gradient_nominal
    pooled.to_csv(out/'pooled_psnr_comparison.csv')
    codec_deltas=delta.query('to_stage == "jpeg_q75"').copy();codec_deltas.to_csv(out/'codec_effects_per_source.csv',index=False)
    tails_table.to_csv(out/'full_coverage_tail_rates.csv')
    audit=dict(notebook_bytes=args.notebook.stat().st_size,notebook_sha256=sha(args.notebook),
        code_cells=10,consecutive_execution_counts=True,all_code_sources_unchanged=True,changed_markdown_cells=md_changes,
        saved_error_outputs=0,saved_stderr_streams=0,reported_checks=checks,reported_zip_receipt=receipt,
        csv_row_counts=counts,reconciled_result_tables=6,embedded_figures=4,csv_files=csv_integrity,
        source_files_rehashed=4,regenerated_observation_hash_matches=sum(observation_hashes),regenerated_observations=16,
        regenerated_codec_hash_matches=sum(codec_hashes),regenerated_codecs=4,
        regenerated_input_classical_quality_rows=32,cheap_quality_max_abs_mse_difference=cheap_max,
        acquisition_measurement_max_abs_difference=stage_measurement_max,
        notebook_metadata_is_inherited_local_history=True,
        recorded_reconstruction_seconds=float(c.elapsed_seconds.sum()),
        recorded_cuda_peak_allocated_mib=[float(learned.peak_cuda_allocated_mib.min()),float(learned.peak_cuda_allocated_mib.max())],
        raw_manifest_retrieved=False,raw_manifest_transfer_error='HTTP 403; readable JSON content empty',
        full_export_hash_verification=False,raw_learned_prediction_readback=False,
        learned_inference_rerun=False,zip_bytes_independently_verified=False)
    (out/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit,indent=2))
    print(pooled.to_string())


if __name__=='__main__':main()
