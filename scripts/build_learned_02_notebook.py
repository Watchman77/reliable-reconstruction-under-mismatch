"""Build the self-contained, source-verified Learned 02 Colab notebook."""
import ast
import hashlib
import json
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / 'experiments/learned_02'
source = (EXP / 'learned.py').read_text()
base = (ROOT / 'experiments/baseline_01/baseline.py').read_text()
provenance = json.loads((EXP / 'provenance.json').read_text())
provenance['adapter_source_sha256'] = hashlib.sha256(source.encode()).hexdigest()
provenance['baseline_helper_sha256'] = hashlib.sha256(base.encode()).hexdigest()
vendor = {p: (EXP / 'vendor/dpir' / p).read_bytes().decode() for p in provenance['files']}
manifest = json.loads((ROOT / 'data/manifests/div2k_development_100.json').read_text())
hashes = {r['source_id'].split(':')[1]: r['source_pixels_sha256'] for r in manifest['records']
          if r['source_id'].split(':')[1] in ['0801','0802','0803','0804']}
lines = source.splitlines(keepends=True)
tree = ast.parse(source)
functions = {node.name: ''.join(lines[node.lineno-1:node.end_lineno])
             for node in tree.body if isinstance(node, ast.FunctionDef)}
first = next(node.lineno for node in tree.body if isinstance(node, ast.FunctionDef))
setup = ''.join(lines[:first-1])
cells=[]
def md(text): cells.append(nbf.v4.new_markdown_cell(text))
def code(text): cells.append(nbf.v4.new_code_cell(text))
def defs(names): code('\n\n\n'.join(functions[name] for name in names))

md('''# 02 · Verified learned reconstruction baseline
**DRUNet / DPIR-style development · 17 September 2026**

## Purpose and execution scope
Compare a verified pretrained reconstruction baseline with our improved classical baseline, then test two sensitivity scores at equal denoiser-call budgets. This is a development experiment, not a new method or a calibrated uncertainty guarantee.

**Default Colab run:** four DIV2K sources, 0801–0804, each with blur/noise and blur/noise/JPEG: **eight observations**. The notebook's saved local validation uses **only source 0801, blur/noise**, at full resolution. The configuration and outputs below state the actual executed subset. Running all cells in Colab without local environment overrides runs all eight observations and replaces displayed outputs.

**Start:** Upload/open this notebook in Colab, choose a GPU runtime if available, and **Run all**. Your existing images must be in `MyDrive/reliable-reconstruction-under-mismatch/samples`. The first run downloads the official colour DRUNet checkpoint (~131 MB). Results are saved directly to a new dated Drive folder. All computational code and the upstream MIT licence are embedded. No repository clone is needed. Torch, NumPy, pandas, Matplotlib, Pillow and IPython are dependencies normally available in Colab.

A measured full-resolution denoiser call took about 8.5 seconds on the preparation CPU. The full experiment requires **392 experiment denoiser calls**, plus two small validation calls, so allow substantial runtime. GPU time has not been measured. Existing source files and result folders are preserved.

## Methods and limits
- Same native 576 × 576 centre crop, 32 px context margin and 512 × 512 evaluation region as Baseline 01. One true blur width (1.6 px) and noise standard deviation (2/255); this is the original anchor condition, not the earlier entire severity grid.
- Stored gamma-encoded RGB, periodic analytic Gaussian blur and source-keyed noise remain controlled approximations. JPEG means clipping, 8-bit rounding and quality 75, without chroma subsampling.
- Operational methods use fixed nominal blur 1.0 px and noise 2/255. Only the separate oracle diagnostic receives true blur. Clean images are used for evaluation, not operational scores or iteration selection.
- Classical comparison: gradient regularisation with lambda 0.05 inherited from Baseline 01. Learned reconstruction: eight HQS iterations, official 49-to-2 noise schedule, trade-off 0.23, and periodical geometric self-ensemble. Full-tensor denoising, our analytic transfer function and clipped floating output are declared adaptations; this is **DPIR-style**, not a reproduction of the paper's benchmark scores.
- Denoising-only DRUNet is a one-call, operator-oblivious control. It is not a strong dedicated deblurring comparator.
- Operator sensitivity uses assumed blur widths 0.8/1.0/1.2. Image-transformation sensitivity uses fixed-operator reconstructions of the original image and 90°/180° rotations, then reverses the rotations. Each uses three eight-iteration reconstructions; the nominal output is shared. Equal denoiser calls do not guarantee equal wall-clock cost. Neither is calibrated image uncertainty.
- Primary detail error uses `D(x) = x − G₁*x` before removing the context border. Select 16 × 16 patches by low score at fixed 50%, 75%, 90% and 100% coverages. Report RGB/detail MSE and bad-detail rates at detail-RMSE tolerances 0.025, 0.05 and 0.10. These are development tolerances, not learned calibration thresholds.
- Report all patches and the clean-reference top texture quartile separately. The clean-reference stratum and oracle-error ranking are evaluation-only. High-pass error is not a proof of measurement support or hallucination detection.

**Training overlap:** The DPIR paper reports denoiser training on 900 DIV2K images. An exact checkpoint training-image manifest was not recovered. Our four previously used sources cannot establish unseen-image performance for these weights. Independent calibration/testing, additional learned families and definitive novelty assessment remain outstanding.

### 1. Imports and frozen defaults
''')
code(setup)
md('### 2. Reuse the verified data simulator and preserve official model code\nThe Baseline 01 helper is embedded verbatim. The official files are verified byte-for-byte; only the network import namespace is adapted at load time to avoid collisions.')
code('''BASELINE_SOURCE = '''+repr(base)+'''
PROVENANCE = '''+repr(provenance)+'''
VENDOR_SOURCES = '''+repr(vendor)+'''
EXPECTED_RGB_HASHES = '''+repr(hashes)+'''
assert hashlib.sha256(BASELINE_SOURCE.encode()).hexdigest() == PROVENANCE['baseline_helper_sha256']
B01 = types.ModuleType('baseline01_helper')
exec(compile(BASELINE_SOURCE, '<embedded baseline01_helper>', 'exec'), B01.__dict__)
''')
md('### 3. Locate images, cache weights and create a fresh destination\nLocal environment overrides may select a source/condition subset, but do not resize images or change the frozen numerical settings. The actual scope is printed and saved. Colab mounts Drive once.')
code('''from IPython.display import display
get_ipython().run_line_magic('matplotlib', 'inline')
plt.ioff()
try:
    import google.colab
    IN_COLAB = True
except ImportError:
    IN_COLAB = False
if IN_COLAB:
    from google.colab import drive
    drive.mount('/content/drive')
    PROJECT_DIR = Path('/content/drive/MyDrive/reliable-reconstruction-under-mismatch')
else:
    PROJECT_DIR = Path.cwd()
    if PROJECT_DIR.name == 'notebooks': PROJECT_DIR = PROJECT_DIR.parent

DATA_DIR = Path(os.environ.get('IMAGING02_DATA_DIR', str(PROJECT_DIR / 'samples')))
timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
OUTPUT_DIR = Path(os.environ.get('IMAGING02_OUTPUT_DIR', str(PROJECT_DIR / 'results' / ('learned_02_' + timestamp))))
WEIGHTS = Path(os.environ.get('IMAGING02_WEIGHTS', str(PROJECT_DIR / 'model_cache/drunet_color.pth')))
VENDOR_DIR = PROJECT_DIR / 'model_cache/dpir_15bca3f'
for relative, content in VENDOR_SOURCES.items():
    path = VENDOR_DIR / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode())
for key, env in [('source_ids','IMAGING02_SOURCE_IDS'), ('scenarios','IMAGING02_SCENARIOS')]:
    if env in os.environ:
        subset = [x.strip() for x in os.environ[env].split(',')]
        assert subset and len(subset) == len(set(subset)) and set(subset) <= set(CONFIG[key]), env
        CONFIG[key] = subset
assert DATA_DIR.is_dir(), f'Missing source folder: {DATA_DIR}'
for sid in CONFIG['source_ids']:
    assert (DATA_DIR / (sid + '.png')).is_file(), f'Missing source: {sid}'
assert not OUTPUT_DIR.exists(), f'Choose a new output folder: {OUTPUT_DIR}'
print('ACTUAL CONFIGURED SOURCES:', CONFIG['source_ids'])
print('ACTUAL CONFIGURED CONDITIONS:', CONFIG['scenarios'])
print('Planned observations:', len(CONFIG['source_ids']) * len(CONFIG['scenarios']))
print('Device:', 'CUDA GPU' if torch.cuda.is_available() else 'CPU')
print('Results destination:', OUTPUT_DIR)
''')
md('### 4. Define and verify the learned reconstruction adapter\nStrict checkpoint loading, official file digests, all transform inverses, the upstream schedule, a tiny independent dense HQS solution and repeated learned smoke outputs are checked before full image reconstruction.')
defs(['digest','download_weights','load_model','augment','undo_augment','schedule','data_step','sync','to_tensor','reconstruct','validate_adapter'])
md('### 5. Define evaluation and auditable saving\nEvery completed observation is checkpointed. Final exports include metric tables, costs, trajectories, configuration, provenance, four figures, nominal predictions and patch arrays. The manifest hashes every exported file except itself. A partial run retains an explicit running status.')
defs(['detail','evaluate_scores','plot_results','save_snapshot','run'])
md('### 6. Execute the configured experiment\nThis is the long cell. Each completed reconstruction prints its time and denoiser-call count. Settings are not tuned against the resulting errors.')
code('''download_weights(WEIGHTS, PROVENANCE)
result = run(DATA_DIR, OUTPUT_DIR, VENDOR_DIR, WEIGHTS, PROVENANCE, EXPECTED_RGB_HASHES, CONFIG)
print(json.dumps(result['checks'], indent=2))
print('Completed only the subset printed in Section 3.')
''')
md('## Results\n### 7. Reconstruction quality and cost\nPooled PSNR is −10 log10(mean MSE), not an average of per-image PSNRs. Costs cover reconstruction calls; data loading and final score/plot/export work are excluded. CPU peak memory is process-lifetime RSS, not isolated inference memory.')
code('''display(result['summary'].round(6))
display(result['compute'].groupby('variant', as_index=False).agg(
    runs=('elapsed_seconds','size'), total_seconds=('elapsed_seconds','sum'),
    mean_seconds=('elapsed_seconds','mean'), denoiser_calls=('denoiser_calls','sum')).round(3))
display(result['figures'][0])
display(result['figures'][2])
''')
md('### 8. Detail selection and iteration diagnostics\nCompare operator spread with the fixed-operator image-transformation score and inexpensive residual/gradient controls. Random risk is its exact expectation. Neither a low residual nor a visually pleasing image establishes fidelity to the clean reference.')
code('''half = result['curves'].query('coverage == 0.5').groupby(['scenario','region','score'], as_index=False).agg(
    detail_mse=('detail_mse','mean'), rgb_mse=('rgb_mse','mean'),
    bad_detail_rate_005=('bad_detail_rate_0.05','mean'))
display(half.round(7))
display(result['figures'][1])
display(result['figures'][3])
''')
md('### 9. Computed readout and next decision\nRead these as bounded development results. A negative score comparison is retained. No global novelty or scoping-review verdict follows from this experiment.')
code('''summary = result['summary']
for scenario in CONFIG['scenarios']:
    values = summary[summary.scenario == scenario].set_index('model').mean_mse
    for model in ['gradient_nominal','drunet_denoise_only','dpir_nominal','dpir_oracle_blur']:
        print(f'{scenario} | {model}: pooled gain over input {10*np.log10(values.observed/values[model]):+.3f} dB')
for (scenario, region), frame in half.groupby(['scenario','region']):
    values = frame.set_index('score').detail_mse
    controls = values[['image_transform_spread_detail','measurement_residual','image_gradient']]
    reduction = 100 * (1 - values.operator_spread_detail / controls.min())
    print(f'{scenario} | {region}: operator detail spread vs lowest-error included control ({controls.idxmin()}), at 50% coverage: {reduction:+.2f}% detail-MSE reduction')
print('Completed observations:', result['completed_observations'])
print('Configured sources:', CONFIG['source_ids'], '| conditions:', CONFIG['scenarios'])
print('Eight-observation development plan complete:', result['completed_observations'] == 8)
print('No independent-test, statistical-significance, calibration or novelty claim.')
print('Results saved:', OUTPUT_DIR)
''')
md('''## Takeaways and reproduction
The decision is to establish a trustworthy learned-baseline comparison before designing a custom method. Run the full eight-observation configuration before drawing even a four-source development conclusion. A promising score must next survive stronger image-only uncertainty comparators, independent learned families, compute checks and source-disjoint calibration/testing. Repeated tuning of these four exposed sources cannot supply independent confirmation.

The scoping review remains a separate route. Its viability depends on added value over existing reviews and a completed formal method; an individual experimental score cannot settle it.

- [Official DPIR code at the inspected commit](https://github.com/cszn/DPIR/tree/15bca3fcc1f3cc51a1f99ccf027691e278c19354)
- [DPIR paper, inspected v2](https://arxiv.org/html/2008.13751v2)
- [Official checkpoint downloader](https://github.com/cszn/DPIR/blob/15bca3fcc1f3cc51a1f99ccf027691e278c19354/main_download_pretrained_models.py)
- [Official DIV2K](https://data.vision.ee.ethz.ch/cvl/DIV2K/)

Generated from `experiments/learned_02/learned.py` and the existing Baseline 01 helper. Their hashes are in notebook metadata and run provenance. The recorded checkpoint SHA-256 is our observed digest, not a publisher-signed checksum. Local in-process execution does not validate Colab/Drive or GPU behaviour; notebook metadata records that distinction. Raw source images and pretrained weights are not bundled into the notebook.
''')
nb=nbf.v4.new_notebook(cells=cells)
nb.metadata.update(kernelspec=dict(display_name='Python 3',language='python',name='python3'),
    language_info=dict(name='python',version='3'), colab=dict(name='02_DIV2K_Learned_Baseline.ipynb'),
    learned_source_sha256=provenance['adapter_source_sha256'],baseline_source_sha256=provenance['baseline_helper_sha256'],
    validation=dict(status='not_yet_executed',scope='Default four sources/two conditions; local validation subset must be labelled.'))
nbf.validate(nb)
target=ROOT/'notebooks/02_DIV2K_Learned_Baseline.ipynb'
nbf.write(nb,target)
print(target)
