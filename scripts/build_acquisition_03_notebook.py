"""Build Notebook 03 with unchanged verified helpers and a frozen stage diagnosis."""
import hashlib
import json
from pathlib import Path
import nbformat as nbf

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/'experiments/acquisition_03'
sha=lambda text:hashlib.sha256(text.encode()).hexdigest()
base=(ROOT/'experiments/baseline_01/baseline.py').read_text()
learned=(ROOT/'experiments/learned_02/learned.py').read_text()
diagnostic=(EXP/'diagnostic.py').read_text()
freeze=(EXP/'design_freeze.md').read_text()
anchor=(ROOT/'experiments/learned_02/colab_review_20260917/csv_exports/quality.csv').read_text()
provenance=json.loads((ROOT/'experiments/learned_02/provenance.json').read_text())
provenance.update(baseline_helper_sha256=sha(base),adapter_source_sha256=sha(learned),
    diagnostic_source_sha256=sha(diagnostic),design_freeze_sha256=sha(freeze),
    learned02_anchor_csv_sha256=sha(anchor),parent_checkpoint='36c0fb9e9730d588c8fc59ee2c8982f5165bb7d3')
vendor={p:(ROOT/'experiments/learned_02/vendor/dpir'/p).read_bytes().decode() for p in provenance['files']}
manifest=json.loads((ROOT/'data/manifests/div2k_development_100.json').read_text())
hashes={r['source_id'].split(':')[1]:r['source_pixels_sha256'] for r in manifest['records'] if r['source_id'].split(':')[1] in ['0801','0802','0803','0804']}
(EXP/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
cells=[]
md=lambda s:cells.append(nbf.v4.new_markdown_cell(s))
code=lambda s:cells.append(nbf.v4.new_code_cell(s))
md('''# 03 · Diagnose the acquisition-chain failure
**Paired clipping, 8-bit rounding and JPEG stages · development experiment**

## Goal and execution scope
Learned 02 improved the linear-blur baseline but underperformed the classical comparator with the JPEG chain. This notebook asks **where the reconstruction gap changes when acquisition stages are added**, with the learned model and all reconstruction settings fixed.

**Saved local result (0801 only):** all four stages completed, with all 20 reconstruction-quality rows independently checked from saved predictions. Nominal DPIR changes by +0.000705 dB through clipping/8-bit rounding, then loses 2.053549 dB when JPEG encoding/decoding is added. This is one exposed development source, not the full four-source result. The native local kernel failed; sequential IPython execution and the replay of figure-display cells are recorded in metadata. Colab/GPU/Drive execution for this notebook remains pending.

**Default Colab run: four sources × four stages = 16 observations.** The predeclared local validation covers **only source 0801 × all four stages**, at full resolution, because this workspace has CPU only. Saved local outputs, when present, are evidence for that subset. Colab runs all four sources unless you deliberately set a local environment override. Section 2 prints the actual scope; the final cell reports completion and the ZIP path.

**Your steps:** upload this `.ipynb` into Colab, select a GPU runtime, then **Run all**. Authorize the Drive mount when Colab requests it. Your four existing PNGs should be in `MyDrive/reliable-reconstruction-under-mismatch/samples`; the verified DRUNet checkpoint is reused from `model_cache` or downloaded if absent. No repository clone is needed. NumPy, pandas, Pillow, Matplotlib, Torch, IPython and nbformat are dependencies.

Outputs go into a new dated `results/acquisition_03_...` Drive folder. Section 10 creates **one ZIP beside that folder** and verifies its contents. Download that ZIP from Drive and upload it here for review. Every compared reconstruction is included; allow a few hundred MB for a full result folder and another copy in the ZIP. Exact size is printed after saving.

## Context & methods

| Stage | Supplied observation | What changes from the previous stage |
|---|---|---|
| Linear float | Original floating blur + noise, possibly outside [0, 1] | Baseline endpoint |
| Clipped float | Clip the identical observation to [0, 1] | Clipping only |
| Quantized 8-bit | Round clipped values to the nearest 1/255 level | 8-bit rounding only |
| JPEG Q75 | Encode/decode those same uint8 values, quality 75, no chroma subsampling | Whole JPEG codec processing |

### Key assumptions and limits
- Sources 0801–0804 remain exposed development data. The unresolved DRUNet/DIV2K training overlap prevents unseen-image claims. The same noise realization is used across stages; patches/stages are not independent source replicates.
- Preserve the 576 × 576 centre crop, 512 × 512 evaluation region, 32 px context, true blur 1.6 and noise 2/255. Operational methods receive nominal blur 1.0/noise 2/255. True-blur reconstruction is an information-advantaged diagnostic that still omits downstream processing.
- Keep the classical gradient inverse at lambda 0.05 and the unchanged DPIR-style adapter at eight iterations, 49-to-2 schedule and trade-off 0.23. Retain one-call DRUNet denoising. No hyperparameter or codec-quality search is performed.
- The input quality control is display-clipped at every stage, preserving Learned 02. Therefore its linear/clipped scores are equal by construction. The reconstruction methods receive the actual unbounded linear observation at the first stage.
- Primary outcome: high-pass detail MSE, with D(x)=x−G₁*x before border removal; compare nominal DPIR with classical reconstruction and inspect their adjacent-stage gap changes. Also retain all five models' RGB MSE/PSNR and full-coverage patch error exceedance rates at 0.025, 0.05 and 0.10 detail RMSE.
- Adjacent effects depend on this stage order. The codec contrast includes colour conversion and encode/decode processing; it does not isolate DCT quantization alone. A change in error does not uniquely identify an internal solver/prior mechanism. These results do not establish novelty, calibrated reliability or hallucination detection.

### 1. Load the frozen code and source identities
The earlier simulator and learned adapter are embedded unchanged. Hashes cover their source, the new diagnostic, frozen design, anchor CSV and official upstream files. The upstream MIT licence is embedded with the vendor code.
''')
code("""import os, json, hashlib, types
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from IPython.display import display
"""+'\nBASELINE_SOURCE = '+repr(base)+'\nLEARNED_SOURCE = '+repr(learned)+'\nDIAGNOSTIC_SOURCE = '+repr(diagnostic)+'\nDESIGN_FREEZE = '+repr(freeze)+'\nANCHOR_CSV = '+repr(anchor)+'\nPROVENANCE = '+repr(provenance)+'\nVENDOR_SOURCES = '+repr(vendor)+'\nEXPECTED_RGB_HASHES = '+repr(hashes)+'''
for text, field in [(BASELINE_SOURCE,'baseline_helper_sha256'), (LEARNED_SOURCE,'adapter_source_sha256'),
                    (DIAGNOSTIC_SOURCE,'diagnostic_source_sha256'), (DESIGN_FREEZE,'design_freeze_sha256'),
                    (ANCHOR_CSV,'learned02_anchor_csv_sha256')]:
    assert hashlib.sha256(text.encode()).hexdigest() == PROVENANCE[field]
B01 = types.ModuleType('baseline01_embedded')
L02 = types.ModuleType('learned02_embedded')
D03 = types.ModuleType('acquisition03_embedded')
for source, module in [(BASELINE_SOURCE,B01),(LEARNED_SOURCE,L02),(DIAGNOSTIC_SOURCE,D03)]:
    exec(compile(source, '<' + module.__name__ + '>', 'exec'), module.__dict__)
L02.B01 = B01
D03.B01, D03.L02 = B01, L02
CONFIG = json.loads(json.dumps(L02.CONFIG))
CONFIG['acquisition_stages'] = D03.STAGES
CONFIG['experiment'] = 'acquisition_03'
print('Embedded source and design hashes verified.')
''')
md('''### 2. Locate Drive data and declare the actual scope
The default is all four sources and all four stages. The local validation override changes only the source list, never image resolution, stage list, iterations or reconstruction settings.''')
code('''try:
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
DATA_DIR = Path(os.environ.get('IMAGING03_DATA_DIR', str(PROJECT_DIR/'samples')))
WEIGHTS = Path(os.environ.get('IMAGING03_WEIGHTS', str(PROJECT_DIR/'model_cache/drunet_color.pth')))
VENDOR_DIR = PROJECT_DIR/'model_cache/dpir_15bca3f'
for relative, source in VENDOR_SOURCES.items():
    path = VENDOR_DIR/relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert D03.sha256(path) == PROVENANCE['files'][relative], f'Cached vendor file changed: {relative}'
    else:
        path.write_bytes(source.encode())
if 'IMAGING03_SOURCE_IDS' in os.environ:
    requested = [s.strip() for s in os.environ['IMAGING03_SOURCE_IDS'].split(',')]
    assert requested and len(requested)==len(set(requested)) and set(requested)<=set(CONFIG['source_ids'])
    CONFIG['source_ids'] = requested
for sid in ['0801','0802','0803','0804']:
    assert (DATA_DIR/(sid+'.png')).is_file(), f'Missing original source: {DATA_DIR/(sid+".png")}'
timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
OUTPUT_DIR = Path(os.environ.get('IMAGING03_OUTPUT_DIR', str(PROJECT_DIR/'results'/('acquisition_03_'+timestamp))))
assert not OUTPUT_DIR.exists(), f'Choose a new destination; existing run preserved: {OUTPUT_DIR}'
print('ACTUAL SOURCES:', CONFIG['source_ids'])
print('ACTUAL STAGES:', CONFIG['acquisition_stages'])
print('Planned observations:', 4*len(CONFIG['source_ids']), '/ full design: 16')
print('Experiment denoiser calls:', 68*len(CONFIG['source_ids']), '+ two small validation calls')
print('Device:', 'CUDA GPU' if D03.torch.cuda.is_available() else 'CPU')
print('Destination:', OUTPUT_DIR)
''')
md('''### 3. Confirm the frozen information and evaluation budget
The printed table states exactly what each method receives. All numerical settings are saved in `config.json`. Endpoint input/classical errors must match the reviewed Learned 02 CSV before learned inference starts.''')
code('''display(pd.DataFrame([
    ['Observed control','Display-clipped observation','No inference'],
    ['Classical gradient','Stage observation; nominal blur 1.0','lambda 0.05'],
    ['DRUNet denoising only','Stage observation; noise 2/255','1 denoiser call'],
    ['Nominal DPIR','Stage observation; nominal blur 1.0, noise 2/255','8 iterations'],
    ['True-blur DPIR diagnostic','Stage observation; true blur 1.6, noise 2/255','8 iterations'],
], columns=['Method','Information','Fixed setting']))
print('Design SHA-256:', PROVENANCE['design_freeze_sha256'])
print('Model checkpoint SHA-256:', PROVENANCE['weight_sha256'])
''')
md('''### 4. Run the paired diagnosis
This is the long cell. It checks all four source identities and both historical simulator endpoints, loads the verified weights, then processes only the configured sources. Each complete observation saves every reconstruction and its patch errors. Failure status is recorded if a computation fails; completed runs undergo prediction readback before being marked complete.''')
code('''result = D03.run(DATA_DIR, OUTPUT_DIR, VENDOR_DIR, WEIGHTS, PROVENANCE,
                 EXPECTED_RGB_HASHES, ANCHOR_CSV, CONFIG)
print(json.dumps(result['checks'], indent=2))
print('Completed observations:', result['completed_observations'])
''')
md('''## Results
### 5. Reconstruction quality across the four stages
Pooled PSNR is −10 log10(mean MSE), not mean per-source PSNR. Both panels concern exactly the configured sources. All methods and negative comparisons are retained.''')
code('''from IPython.display import Image as DisplayImage
display(result['summary'].round(7))
display(DisplayImage(filename=str(OUTPUT_DIR/'stage_quality.png')))
''')
md('''### 6. Where does the error change?
Positive detail-MSE change means adding that stage worsens that method's error. These changes are paired and conditional on earlier stages. They are not independent causal contributions of internal codec operations.''')
code('''stage_changes = result['stage_deltas'].groupby(['to_stage_index','to_stage','model'],as_index=False).agg(
    mean_delta_detail_mse=('delta_detail_mse','mean'), mean_delta_rgb_mse=('delta_mse','mean'),
    sources=('source_id','nunique'))
display(stage_changes.round(8))
display(DisplayImage(filename=str(OUTPUT_DIR/'stage_changes.png')))
''')
md('''### 7. Check source-specific gaps and error tails
The source curves prevent a pooled average from hiding reversals. Positive detail-MSE gap means nominal DPIR is worse than classical reconstruction; the PSNR panel has the opposite quality direction. Tail rates below are at full coverage, not selectively calibrated risks.''')
code('''display(result['model_gaps'].round(8))
display(DisplayImage(filename=str(OUTPUT_DIR/'source_gaps.png')))
tail_columns = ['bad_detail_rate_0.025','bad_detail_rate_0.05','bad_detail_rate_0.1']
display(result['quality'].groupby(['stage_index','stage','model'])[tail_columns].mean().round(6))
''')
md('''### 8. Inspect saved images, endpoint drift and compute
The montage uses a fixed centre inset of the first configured source; all numerical evaluation uses the full region. Endpoint differences compare the new run with the preserved Colab CSV. CPU/GPU or software differences may change learned values; the table records that drift without relabelling it as a new acquisition effect.''')
code('''display(DisplayImage(filename=str(OUTPUT_DIR/'stage_examples.png')))
display(result['endpoint_comparison'].round(9))
display(result['compute'].groupby('model',as_index=False).agg(
    runs=('elapsed_seconds','size'),seconds=('elapsed_seconds','sum'),denoiser_calls=('denoiser_calls','sum')).round(3))
''')
md('''### 9. Computed readout and decision boundary
This readout is calculated from the current run, including any losses or null changes. It does not select new solver parameters or claim novelty.''')
code('''for index,stage in enumerate(D03.STAGES):
    values = result['summary'].query('stage == @stage').set_index('model')
    rgb_gain = values.loc['dpir_nominal','pooled_psnr_db'] - values.loc['gradient_nominal','pooled_psnr_db']
    detail_gap = values.loc['dpir_nominal','mean_detail_mse'] - values.loc['gradient_nominal','mean_detail_mse']
    print(f'{stage}: nominal − classical RGB PSNR {rgb_gain:+.4f} dB; detail-MSE gap {detail_gap:+.8f}')
for stage,frame in result['model_gaps'].dropna(subset=['change_in_detail_gap']).groupby('stage',sort=False):
    print(f'Add {stage}: mean change in nominal − classical detail gap {frame.change_in_detail_gap.mean():+.8f}')
print('Executed sources:', CONFIG['source_ids'])
print('Full 16-observation design complete:', result['completed_observations']==16)
print('Stage effects are order-conditional development findings, not a unique internal failure mechanism.')
print('Review these outputs before proposing acquisition-aware reconstruction; no tuning or novelty claim is made here.')
''')
md('''### 10. Verify and package this run for review
The result folder is already saved directly to Drive in Colab. This cell verifies every manifest entry, creates one ZIP beside the folder, verifies the archived bytes, and prints the exact file to download. Download **only this new ZIP**, then upload it in our chat. If this cell is rerun after successful packaging, it preserves and re-verifies the existing ZIP.''')
code('''ZIP_PATH = OUTPUT_DIR.with_suffix('.zip')
if ZIP_PATH.exists():
    receipt_path = ZIP_PATH.with_suffix('.receipt.json')
    assert receipt_path.is_file(), 'Existing ZIP has no receipt; inspect it before retrying.'
    receipt = json.loads(receipt_path.read_text())
    assert ZIP_PATH.stat().st_size == receipt['zip_bytes'] and D03.sha256(ZIP_PATH) == receipt['zip_sha256']
else:
    ZIP_PATH, receipt = D03.verify_and_zip(OUTPUT_DIR)
print(json.dumps(receipt, indent=2))
print('DOWNLOAD THIS ZIP:', ZIP_PATH)
print('Then upload that ZIP in our chat for review.')
''')
md('''## Takeaways and reproduction
Keep the earlier experiment frozen. The next scientific decision depends on the actual source-level and pooled stage changes, then a separately specified test of acquisition-aware reconstruction if warranted. Completing this notebook does not establish an original method, calibrated reliability or generalization beyond the exposed development sources. The scoping-review protocol and literature decisions remain separate and unchanged.

The default run requires 272 experiment denoiser calls plus two small checks. The predeclared one-source local validation uses 68 plus two. Source files and model weights are not included in the output ZIP. Observation arrays, every compared reconstruction, patch errors, codec bytes, metrics, environment, status, figures and hashes are included. If execution stops, the result folder records partial/failed status; only completed configured runs are packaged.

Code: `experiments/acquisition_03/diagnostic.py`, unchanged Learned 02 adapter and Baseline 01 simulator. Provenance and the full frozen design are embedded above. The recorded checkpoint digest is locally observed, not a publisher-signed checksum.

References: [Pillow JPEG options](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg), [pinned official DPIR code](https://github.com/cszn/DPIR/tree/15bca3fcc1f3cc51a1f99ccf027691e278c19354), [prior verified development checkpoint](https://github.com/Watchman77/reliable-reconstruction-under-mismatch/pull/1).
''')
nb=nbf.v4.new_notebook(cells=cells)
nb.metadata.update(kernelspec=dict(display_name='Python 3',language='python',name='python3'),
    language_info=dict(name='python'),colab=dict(name='03_DIV2K_Acquisition_Stage_Diagnosis.ipynb'),
    provenance=provenance,validation=dict(status='not_yet_executed',planned_local_scope='0801; all four stages; full resolution',default_scope='0801–0804; all four stages'))
nbf.validate(nb)
target=ROOT/'notebooks/03_DIV2K_Acquisition_Stage_Diagnosis.ipynb'
nbf.write(nb,target);print(target)
