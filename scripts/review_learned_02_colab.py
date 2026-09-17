import argparse,hashlib,json,io,re
from pathlib import Path
import numpy as np,pandas as pd,nbformat
parser=argparse.ArgumentParser(description='Review the saved Learned 02 Colab notebook against its CSV exports; no model inference.')
parser.add_argument('--notebook',type=Path,required=True)
parser.add_argument('--exports',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
REPO=Path(__file__).resolve().parents[1]
OUT=args.output;OUT.mkdir(parents=True,exist_ok=True)
DATA=args.exports
read=lambda name:pd.read_csv(DATA/(name+'.csv'),dtype={'source_id':str})
quality,summary,curves,compute,traj,sources=[read(x) for x in ['quality','summary','curves','compute','trajectories','source_manifest']]
keys=['source_id','scenario']
assert len(quality)==40 and len(summary)==10 and len(curves)==448 and len(compute)==64 and len(traj)==384 and len(sources)==4
assert not quality.duplicated(keys+['model']).any()
assert not curves.duplicated(keys+['region','score','coverage']).any()
assert not compute.duplicated(keys+['variant']).any()
assert not traj.duplicated(keys+['variant','iteration']).any()
assert (quality.groupby(keys).size()==5).all() and (curves.groupby(keys).size()==56).all()
assert (compute.groupby(keys).denoiser_calls.sum()==49).all()
assert compute.denoiser_calls.sum()==392
assert set(quality.source_id)=={'0801','0802','0803','0804'}
assert set(quality.scenario)=={'blur_noise','blur_noise_jpeg'}
assert (quality.true_sigma==1.6).all() and np.allclose(quality.noise_std,2/255)
assert np.isfinite(quality[['mse','detail_mse','psnr_db']]).all().all()
assert np.allclose(quality.psnr_db,-10*np.log10(quality.mse),rtol=0,atol=1e-10)
agg=quality.groupby(['scenario','model'],as_index=False).agg(mean_mse=('mse','mean'),mean_detail_mse=('detail_mse','mean'),sources=('source_id','nunique'),observations=('mse','size'))
agg['pooled_psnr_db']=-10*np.log10(agg.mean_mse)
pd.testing.assert_frame_equal(agg,summary,check_dtype=False,rtol=1e-10,atol=1e-14)
full=curves[(curves.region=='all')&(curves.coverage==1)].merge(quality[quality.model=='dpir_nominal'],on=keys,suffixes=('','_quality'))
assert np.allclose(full.rgb_mse,full.mse,rtol=1e-10,atol=1e-14)
assert np.allclose(full.detail_mse,full.detail_mse_quality,rtol=1e-10,atol=1e-14)
for _,group in curves.groupby(keys+['region']):
    endpoint=group[group.coverage==1]
    for col in ['rgb_mse','detail_mse','bad_detail_rate_0.025','bad_detail_rate_0.05','bad_detail_rate_0.1']:
        assert np.ptp(endpoint[col])<1e-12
    for coverage,part in group.groupby('coverage'):
        assert int(part.retained_patches.iloc[0])==int(np.ceil(coverage*part.available_patches.iloc[0]))
        assert (part.detail_mse >= part[part.score=='oracle_detail_error'].detail_mse.iloc[0]-1e-14).all()
        assert (part['bad_detail_rate_0.025']>=part['bad_detail_rate_0.05']).all()
        assert (part['bad_detail_rate_0.05']>=part['bad_detail_rate_0.1']).all()
# Source identity is checked against the official archive record, using reported RGB hashes.
manifest=json.loads((REPO/'data/manifests/div2k_development_100.json').read_text())
expected={r['source_id'].split(':')[1]:r['source_pixels_sha256'] for r in manifest['records']}
assert all(row.rgb_sha256==expected[row.source_id] for row in sources.itertuples())
assert (sources.extent==576).all() and set(sources.role)=={'development_only'}
# Inherited classical controls at precisely this condition.
old=REPO/'experiments/baseline_01/outputs/run_20260917'
old_controls=pd.read_csv(old/'controls.csv',dtype={'source_id':str})
old_selected=pd.read_csv(old/'selected.csv',dtype={'source_id':str})
diffs=[]
for old_frame,new_model,old_model in [(old_controls,'observed','observed'),(old_selected,'gradient_nominal','gradient')]:
    a=old_frame[(old_frame.true_sigma==1.6)&np.isclose(old_frame.noise_std,2/255)&(old_frame.model==old_model)]
    if new_model=='gradient_nominal':a=a[a.operator_info=='nominal']
    joined=quality[quality.model==new_model].merge(a,on=keys,suffixes=('','_old'))
    assert len(joined)==8
    diff=float(abs(joined.mse-joined.mse_old).max());assert diff<1e-14;diffs.append(diff)
# Source code parity and all three displayed tables, at their printed precision.
nb=nbformat.read(args.notebook,as_version=4)
issued=nbformat.read(REPO/'notebooks/02_DIV2K_Learned_Baseline.ipynb',as_version=4)
nbformat.validate(nb)
assert len(nb.cells)==len(issued.cells)==19
assert all(a.source==b.source for a,b in zip(nb.cells,issued.cells))
code=[c for c in nb.cells if c.cell_type=='code']
assert [c.execution_count for c in code]==list(range(1,10))
assert not any(o.output_type=='error' for c in code for o in c.outputs)
assert not any(o.output_type=='stream' and o.get('name')=='stderr' for c in code for o in c.outputs)
expected_cost=compute.groupby('variant',as_index=False).agg(runs=('elapsed_seconds','size'),total_seconds=('elapsed_seconds','sum'),mean_seconds=('elapsed_seconds','mean'),denoiser_calls=('denoiser_calls','sum'))
half=curves.query('coverage==0.5').groupby(['scenario','region','score'],as_index=False).agg(detail_mse=('detail_mse','mean'),rgb_mse=('rgb_mse','mean'),bad_detail_rate_005=('bad_detail_rate_0.05','mean'))
for cell,out_idx,expected_table,decimals in [(13,0,summary,6),(13,1,expected_cost,3),(15,0,half,7)]:
    got=pd.read_html(io.StringIO(nb.cells[cell].outputs[out_idx].data['text/html']))[0].drop(columns=['Unnamed: 0'])
    # Colab's HTML renderer shows six decimal places even after .round(7).
    pd.testing.assert_frame_equal(got,expected_table.round(decimals),check_dtype=False,rtol=0,atol=0.500001e-6)
# Runtime metadata inherited from local validation is not used as Colab timing.
comparison=quality.pivot(index=keys,columns='model',values='psnr_db').reset_index()
comparison['dpir_gain_over_gradient_db']=comparison.dpir_nominal-comparison.gradient_nominal
comparison['dpir_gain_over_input_db']=comparison.dpir_nominal-comparison.observed
comparison.to_csv(OUT/'quality_per_source.csv',index=False)
scored=[]
for (scenario,region,coverage),frame in curves.groupby(['scenario','region','coverage']):
    means=frame.groupby('score').detail_mse.mean()
    controls=means[['image_transform_spread_detail','measurement_residual','image_gradient']]
    by_source=frame.pivot(index='source_id',columns='score',values='detail_mse')
    wins=(by_source.operator_spread_detail<by_source[['image_transform_spread_detail','measurement_residual','image_gradient']].min(axis=1)-1e-14)
    scored.append(dict(scenario=scenario,region=region,coverage=coverage,
        best_included_control=controls.idxmin(),operator_detail_mse=float(means.operator_spread_detail),
        best_control_detail_mse=float(controls.min()),relative_reduction_pct=float(100*(1-means.operator_spread_detail/controls.min())),
        source_wins_over_own_best_control=int(wins.sum()),sources=len(by_source),
        rgb_operator_detail_mse=float(means.operator_spread_rgb)))
score=pd.DataFrame(scored);score.to_csv(OUT/'selection_comparisons.csv',index=False)
failures=curves.query('coverage==0.5').groupby(['scenario','region','score'])[['bad_detail_rate_0.025','bad_detail_rate_0.05','bad_detail_rate_0.1']].mean().reset_index()
failures.to_csv(OUT/'failure_rates_at_50.csv',index=False)
print('QUALITY SUMMARY\n',summary.to_string(index=False))
print('PER SOURCE\n',comparison.to_string(index=False))
print('SCORE COMPARISONS\n',score.to_string(index=False))
print('BAD RATES AT 0.05\n',failures[failures.score.isin(['operator_spread_detail','image_transform_spread_detail','operator_spread_rgb'])].to_string(index=False))
print('COST\n',expected_cost.to_string(index=False))
for scenario,frame in summary.groupby('scenario'):
    x=frame.set_index('model')
    print('DETAIL_MSE_CHANGE',scenario,{target:100*(x.loc['dpir_nominal','mean_detail_mse']/x.loc[target,'mean_detail_mse']-1) for target in ['observed','gradient_nominal']})
audit=dict(uploaded_notebook_sha256=hashlib.sha256((args.notebook).read_bytes()).hexdigest(),
    notebook_code_cells=9,code_identical_to_issued=True,error_outputs=0,stderr_streams=0,embedded_tables_reconciled=3,embedded_figure_count=sum('image/png' in o.get('data',{}) for c in code for o in c.outputs),
    source_count=4,observations=8,quality_rows=40,risk_rows=448,compute_rows=64,trajectory_rows=384,experiment_denoiser_calls=392,
    official_reported_rgb_hashes_match=True,classical_anchor_max_mse_difference=max(diffs),
    metadata_warning='validation and inprocess_execution_seconds are inherited local records, not this Colab run.',
    visual_inspection='Not automated by this script; see the dated human-readable review.',
    full_raw_export_hash_verification=False,raw_access_limitation='Raw manifest transfer returned HTTP 403; readable JSON fallback was empty. CSV text retrieval succeeded. Separate PNG/NPZ bytes were not retrieved.',
    inference_not_rerun_for_review=True,development_only=True,
    files=[dict(name=p.name,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(DATA.glob('*.csv'))])
(OUT/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print('AUDIT PASSED')
