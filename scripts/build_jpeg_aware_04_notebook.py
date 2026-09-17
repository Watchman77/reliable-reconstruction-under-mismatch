"""Build the portable, source-hashed Notebook 04; execution is a separate step."""
import hashlib
import json
from pathlib import Path
import nbformat as nbf
ROOT=Path(__file__).resolve().parents[1];EXP=ROOT/'experiments/jpeg_aware_04'
sha=lambda x:hashlib.sha256(x.encode()).hexdigest()
paths={'baseline':'experiments/baseline_01/baseline.py','learned':'experiments/learned_02/learned.py',
    'diagnostic':'experiments/acquisition_03/diagnostic.py','jpeg_aware':'experiments/jpeg_aware_04/jpeg_aware.py',
    'validator':'scripts/validate_jpeg_aware_04.py','archive':'experiments/jpeg_aware_04/archive_io.py'}
sources={k:(ROOT/p).read_text() for k,p in paths.items()}
freeze=(EXP/'design_freeze.md').read_text()
anchors={n:(EXP/'anchors'/n).read_text() for n in ['quality.csv','acquisition.csv']}
prov={'experiment':'jpeg_aware_04','parent_checkpoint':'0021f09ddc2da06cf54a8835ba5eaffd7352cc79',
    'dpir':json.loads((ROOT/'experiments/learned_02/provenance.json').read_text()),
    'fbcnn':json.loads((EXP/'fbcnn_provenance.json').read_text()),
    'embedded_source_sha256':{k:sha(v) for k,v in sources.items()},'source_paths':paths,
    'design_freeze_sha256':sha(freeze),'anchor_sha256':{k:sha(v) for k,v in anchors.items()}}
vendors={key:{p:(root/p).read_bytes().decode() for p in prov[key]['files']} for key,root in [
    ('dpir',ROOT/'experiments/learned_02/vendor/dpir'),('fbcnn',EXP/'vendor/fbcnn')]}
manifest=json.loads((ROOT/'data/manifests/div2k_development_100.json').read_text())
hashes={r['source_id'].split(':')[1]:r['source_pixels_sha256'] for r in manifest['records'] if r['source_id'].split(':')[1] in ['0801','0802','0803','0804']}
(EXP/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
cells=[]
def md(s):cells.append(nbf.v4.new_markdown_cell(s))
def code(s):cells.append(nbf.v4.new_code_cell(s))
md('''# 04 · JPEG-aware baseline and selective-detail development
**Established FBCNN preprocessing + frozen classical/DPIR inverses · development data only**

This experiment tests whether blind JPEG preprocessing improves the fixed reconstruction baseline that degraded at the JPEG stage in Notebook 03. It then reassesses operator-sensitivity patch selection with the improved or worsened reconstruction. FBCNN is an existing published method; this composition is not a new-method claim or an exact JPEG likelihood.

**Default run:** four sources (0801–0804) × two conditions = eight observations. **Local validation plan:** source 0801 at both conditions, identical full resolution and settings, on CPU. Any saved local results concern that subset only; Section 2 prints the actual execution scope. A four-source decision is never inferred from a one-source run.

**Run in Colab:** select a GPU runtime, choose **Run all**, and authorize Drive mounting. Use the same four original PNGs in `MyDrive/reliable-reconstruction-under-mismatch/samples`. Verified DRUNet weights are reused; official FBCNN colour weights (~288 MB) are downloaded once and cached. No repository clone is needed. Dependencies: Python, NumPy, pandas, Pillow, Matplotlib, Torch, IPython and nbformat (normally provided by Colab).

**Retrieve results:** Section 11 prints the exact dated `SUMMARY.zip` and an `upload_parts` folder. Upload the summary ZIP **and every numbered RAW part ZIP** from that folder. Parts are automatically verified and kept below 100 MiB; no additional packaging notebook is needed. The unsplit RAW ZIP is also preserved. Allow several GB of Drive space for arrays, weights, archives and transfer copies.

### Fixed comparisons and limits
- Input, classical inverse, DPIR, FBCNN alone, FBCNN + classical, FBCNN + DPIR. Every method runs on 8-bit uncompressed and JPEG Q75 observations from the same noise draw.
- All methods receive decoded pixels; operational reconstruction never sees clean truth, true blur or JPEG quality metadata. FBCNN estimates quality automatically. References are used only for evaluation, texture stratification and oracle ranking.
- Preserve the 576 × 576 centre crop, 512 × 512 evaluation region, true blur 1.6, nominal blur 1.0, noise 2/255, eight DPIR iterations and classical lambda 0.05. No hyperparameter search.
- The two pretrained families report DIV2K training; checkpoint-specific overlap is unresolved. These four sources are already exposed development data, not an independent test. Patches and stages do not create independent source replicates.
- A deblocking-then-deblurring cascade can alter the effective noise and remove useful details. Frozen downstream settings isolate this intervention, not the best possible cascade.
- Whole-pipeline rotations, measurement residual, image gradient and exact expected random selection are controls. Rotation spread is a limited heuristic; a stronger trained uncertainty comparator remains outstanding. Residuals use the original supplied observation and are not JPEG likelihoods.
- The FBCNN paper reports MATLAB JPEG training; the repository's dataset/demo use OpenCV. Our inherited Pillow encoder is preserved. This is not a reproduction of the FBCNN paper's benchmark.

### 1. Verify and load the embedded code
The inherited helpers remain unchanged. Both upstream licences, pinned vendor bytes, checkpoint identities, earlier verified anchors and the frozen design are included. Source hashes are checked before inference.''')
code('''import os, json, hashlib, types
# Set before Torch/CUDA initialization for deterministic matrix operations on supported CUDA runtimes.
os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from IPython.display import display, Image as DisplayImage
'''+ '\nSOURCES = '+repr(sources)+'\nPROVENANCE = '+repr(prov)+'\nVENDORS = '+repr(vendors)+'\nDESIGN_FREEZE = '+repr(freeze)+'\nANCHORS = '+repr(anchors)+'\nEXPECTED_RGB_HASHES = '+repr(hashes)+'''
for key, source in SOURCES.items():
    assert hashlib.sha256(source.encode()).hexdigest()==PROVENANCE['embedded_source_sha256'][key]
assert hashlib.sha256(DESIGN_FREEZE.encode()).hexdigest()==PROVENANCE['design_freeze_sha256']
for name, source in ANCHORS.items():
    assert hashlib.sha256(source.encode()).hexdigest()==PROVENANCE['anchor_sha256'][name]
modules={k:types.ModuleType(k+'04_embedded') for k in SOURCES}
for key,module in modules.items():
    exec(compile(SOURCES[key],'<'+module.__name__+'>','exec'),module.__dict__)
B01,L02,D03,J04,AUDIT,ARCHIVE=[modules[k] for k in ['baseline','learned','diagnostic','jpeg_aware','validator','archive']]
L02.B01=B01
D03.B01,D03.L02=B01,L02
J04.B01,J04.L02,J04.D03=B01,L02,D03
CONFIG=json.loads(json.dumps(L02.CONFIG))
CONFIG.update(experiment='jpeg_aware_04',stages=J04.STAGES,
    model_information='decoded RGB and fixed nominal blur/noise only; automatic FBCNN quality; no true-blur reconstruction')
print('Embedded sources, design and anchors verified.')
''')
md('''### 2. Locate Drive inputs and print the actual scope
The default includes all four sources. Environment overrides exist solely for reproducible local validation; they never change image resolution or model settings. An existing result folder is preserved rather than overwritten.''')
code('''try:
    import google.colab
    IN_COLAB=True
except ImportError:
    IN_COLAB=False
if IN_COLAB:
    from google.colab import drive
    drive.mount('/content/drive')
    PROJECT_DIR=Path('/content/drive/MyDrive/reliable-reconstruction-under-mismatch')
else:
    PROJECT_DIR=Path.cwd()
    if PROJECT_DIR.name=='notebooks':PROJECT_DIR=PROJECT_DIR.parent
DATA_DIR=Path(os.environ.get('IMAGING04_DATA_DIR',str(PROJECT_DIR/'samples')))
DPIR_WEIGHTS=Path(os.environ.get('IMAGING04_WEIGHTS',str(PROJECT_DIR/'model_cache/drunet_color.pth')))
FBCNN_WEIGHTS=Path(os.environ.get('IMAGING04_FBCNN_WEIGHTS',str(PROJECT_DIR/'model_cache/fbcnn_color.pth')))
VENDOR_DIRS={k:PROJECT_DIR/'model_cache'/(k+'_'+PROVENANCE[k]['upstream_commit'][:7]) for k in VENDORS}
for key,files in VENDORS.items():
    for relative,source in files.items():
        path=VENDOR_DIRS[key]/relative;path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists():assert J04.sha256(path)==PROVENANCE[key]['files'][relative], f'Changed vendor file: {path}'
        else:path.write_bytes(source.encode())
if 'IMAGING04_SOURCE_IDS' in os.environ:
    requested=[s.strip() for s in os.environ['IMAGING04_SOURCE_IDS'].split(',')]
    assert requested and len(requested)==len(set(requested)) and set(requested)<=set(CONFIG['source_ids'])
    CONFIG['source_ids']=requested
for sid in EXPECTED_RGB_HASHES:
    assert (DATA_DIR/(sid+'.png')).is_file(), f'Missing original PNG: {DATA_DIR/(sid+".png")}'
timestamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
OUTPUT_DIR=Path(os.environ.get('IMAGING04_OUTPUT_DIR',str(PROJECT_DIR/'results'/('jpeg_aware_04_'+timestamp))))
assert not OUTPUT_DIR.exists(), f'Existing run preserved; choose a new output directory: {OUTPUT_DIR}'
print('ACTUAL SOURCES:',CONFIG['source_ids'])
print('ACTUAL STAGES:',CONFIG['stages'])
print('Observations:',2*len(CONFIG['source_ids']),'/ full design: 8')
print('Experiment calls:',160*len(CONFIG['source_ids']),'DRUNet +',6*len(CONFIG['source_ids']),'FBCNN; plus 2 and 3 small checks')
print('Device:','CUDA GPU' if J04.torch.cuda.is_available() else 'CPU')
print('Destination:',OUTPUT_DIR)
''')
md('''### 3. Record the frozen decision rules
Primary reconstruction endpoint: JPEG mean detail MSE. The provisional screen requires FBCNN + DPIR to beat raw DPIR, raw classical and FBCNN + classical in the pooled comparison, and raw DPIR on at least three of four sources.

Primary selection endpoint: JPEG **all-patch detail MSE at 50% retention** on FBCNN + DPIR. Detail operator spread must beat all four operational controls, win against the best pooled control on at least three of four sources, and have no higher pooled bad-detail rate at any of the three fixed tolerances. All other coverages, RGB spread and textured strata are secondary.

These are descriptive development screens, not significance, calibration or novelty tests. A one-source run reports `not_assessed_full_design`. Retain negative outcomes and uncompressed-condition losses.''')
code('''display(pd.DataFrame([
    ['Input','Decoded RGB','No inference'],
    ['Classical','Decoded RGB + nominal blur 1.0','lambda 0.05'],
    ['DPIR','Decoded RGB + nominal blur/noise','8 DRUNet calls'],
    ['FBCNN','Decoded RGB; automatic quality','1 FBCNN call'],
    ['FBCNN + classical','FBCNN output + same inverse assumptions','1 FBCNN call + FFT inverse'],
    ['FBCNN + DPIR','FBCNN output + same solver assumptions','1 FBCNN call + 8 DRUNet calls'],
],columns=['Method','Information','Nominal cost']))
print('Design SHA-256:',PROVENANCE['design_freeze_sha256'])
print('FBCNN weight SHA-256:',PROVENANCE['fbcnn']['weight_sha256'])
print('A score ensemble uses 24 DRUNet calls. FBCNN operator spread adds 1 FBCNN pass; whole-pipeline rotations add 3.')
''')
md('''### 4. Run the frozen comparison
This long cell checks all four source hashes and all eight historical observation hashes before learned inference. It saves every reconstruction, score vector and patch error after each observation. CPU execution can be slow; GPU is recommended. A completed inference run still requires Section 5's independent readback.''')
code('''result=J04.run(DATA_DIR,OUTPUT_DIR,VENDOR_DIRS['dpir'],DPIR_WEIGHTS,
    VENDOR_DIRS['fbcnn'],FBCNN_WEIGHTS,PROVENANCE,EXPECTED_RGB_HASHES,
    ANCHORS['quality.csv'],ANCHORS['acquisition.csv'],CONFIG)
print(json.dumps(result['checks'],indent=2))
''')
md('''### 5. Independently recompute the saved evidence
A separate implementation reads the saved arrays and recomputes reconstruction errors, patch errors, score construction, every risk row, summaries, contrasts and compute accounting. Neural inference is not repeated. Only successful readback marks the configured run complete.''')
code('''independent_audit=AUDIT.validate(OUTPUT_DIR,DATA_DIR)
J04.dump(OUTPUT_DIR/'independent_readback.json',independent_audit)
result['checks']['independent_readback_passed']=independent_audit['status']=='passed'
J04.snapshot(result,OUTPUT_DIR,'complete_for_configured_subset')
print(json.dumps(independent_audit,indent=2))
''')
md('''### 6. Reconstruction quality
Pooled RGB PSNR is computed from pooled MSE, not by averaging dB. Detail MSE uses the inherited high-pass operator before removing the context border.''')
code('''display(result['summary'].round(8))
display(DisplayImage(filename=str(OUTPUT_DIR/'quality.png')))
''')
md('''### 7. Source-level changes and blind quality estimates
Negative detail-MSE differences favour FBCNN + DPIR. FBCNN's inferred quality is a model output, not a calibrated uncertainty measure or verified codec metadata.''')
code('''display(result['quality_changes'].round(8))
display(DisplayImage(filename=str(OUTPUT_DIR/'source_changes.png')))
display(result['fbcnn_diagnostics'].round(5))
''')
md('''### 8. Selective-detail errors and tails
Retain all coverages and all seven rankings. The oracle uses reference errors solely as an evaluation bound. Random curves show exact expected error under uniform retention, not one sampled mask. Nonzero error at low spread can reflect a shared missing acquisition stage.''')
code('''display(DisplayImage(filename=str(OUTPUT_DIR/'risk_coverage.png')))
primary=result['risk_summary'].query("stage=='jpeg_q75' and pipeline=='fbcnn_dpir' and region=='all' and coverage==0.5")
display(primary.round(8))
print('All regions, coverages, source comparisons and tail rates are saved in the CSVs.')
''')
md('''### 9. Inspect images, historical drift and compute
The montage uses a fixed central inset from the first configured source; metrics use the full interior. Historical DPIR differences may reflect CPU/GPU/software drift and are reported explicitly. Standalone score costs overlap at the shared nominal reconstruction: do not sum them as total experiment cost.''')
code('''display(DisplayImage(filename=str(OUTPUT_DIR/'examples.png')))
display(result['endpoint_comparison'].round(10))
display(result['compute'].groupby('component',as_index=False).agg(
    runs=('elapsed_seconds','size'),seconds=('elapsed_seconds','sum'),drunet_calls=('denoiser_calls','sum'),fbcnn_calls=('fbcnn_calls','sum')).round(3))
display(result['score_costs'].round(3))
''')
md('''### 10. Read the actual decision status
A successful numerical run is not a successful scientific hypothesis. The JSON records the predeclared screen outcomes only when all four sources have completed. Independent testing, calibration and novelty remain false regardless of these outcomes.''')
code('''print(json.dumps(result['decisions'],indent=2))
print('Executed sources:',CONFIG['source_ids'])
print('Review all results, including failures, before proposing another method or tuning settings.')
''')
md('''### 11. Save verified summary and RAW transfer ZIPs
Results already reside in the dated Drive folder in Colab. This cell checks all final hashes, verifies both archives byte for byte and automatically creates numbered RAW ZIP parts with payloads of at most 96 MiB. It verifies their complete reassembly hash. Rerunning this cell verifies existing archives instead of overwriting them.

**Upload the SUMMARY ZIP plus every numbered RAW part ZIP printed below.** The summary is sufficient for a first reading, but raw parts are needed to verify arrays independently. Do not upload the large unsplit RAW ZIP as well.''')
code('''export_receipt=ARCHIVE.export(OUTPUT_DIR)
print('UPLOAD SUMMARY:',export_receipt['summary']['path'])
print('UPLOAD ALL THESE RAW PARTS:')
for path in export_receipt['transfer']['part_paths']:print(path)
print('Verified parts:',export_receipt['transfer']['verified_parts'])
print('Full raw ZIP bytes:',export_receipt['raw']['bytes'])
print('Full raw ZIP SHA-256:',export_receipt['raw']['sha256'])
print('Full four-source design complete:',export_receipt['full_design_complete'])
''')
md('''## Interpretation and reproduction
The useful next decision is whether this established preprocessing baseline improves reconstruction and whether operator sensitivity adds selective-detail value under the fixed controls. Failure of this particular cascade does not reject the broad PhD topic or the separate scoping-review route.

The full design has eight observations, 48 main quality rows (112 including ensemble members), 896 risk rows, 640 experiment DRUNet calls and 24 FBCNN calls. Local source-0801 validation has two observations, 12 main quality rows (28 including ensemble members), 224 risk rows, 160 DRUNet calls and six FBCNN calls. Two DRUNet and three FBCNN loading/parity calls are separate. Source PNGs and model weights are external inputs, not included in result exports.

References: [official FBCNN source and release](https://github.com/jiaxi-jiang/FBCNN/tree/54d1831927506b3247e2d4d245abb4f4dab1a1cd), [FBCNN paper](https://arxiv.org/abs/2109.14573), [official pinned DPIR](https://github.com/cszn/DPIR/tree/15bca3fcc1f3cc51a1f99ccf027691e278c19354). The exact sources, licences, design and reviewed Acquisition 03 anchors are embedded in this notebook. Observed checkpoint hashes are not publisher-signed checksums.
''')
nb=nbf.v4.new_notebook(cells=cells)
nb.metadata.update(kernelspec=dict(display_name='Python 3',language='python',name='python3'),language_info=dict(name='python'),
    colab=dict(name='04_DIV2K_JPEG_Aware_Baseline.ipynb'),provenance=prov,
    validation=dict(status='not_yet_executed',planned_local_scope='0801; both stages; full resolution',default_scope='0801–0804; both stages'))
nbf.validate(nb)
for c in nb.cells:
    if c.cell_type=='code':compile(c.source,'notebook04','exec')
target=ROOT/'notebooks/04_DIV2K_JPEG_Aware_Baseline.ipynb';nbf.write(nb,target);print(target)
