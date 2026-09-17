"""Generate the self-contained Colab notebook from baseline.py (no manual JSON edits)."""
import ast
import hashlib
import json
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'experiments/baseline_01/baseline.py'
text = SOURCE.read_text()
lines = text.splitlines(keepends=True)
tree = ast.parse(text)
functions = {node.name: ''.join(lines[node.lineno-1:node.end_lineno])
             for node in tree.body if isinstance(node, ast.FunctionDef)}
first = next(node.lineno for node in tree.body if isinstance(node, ast.FunctionDef))
setup = ''.join(lines[:first-1])
manifest = json.loads((ROOT / 'data/manifests/div2k_development_100.json').read_text())
hashes = {r['source_id'].split(':')[1]: r['source_pixels_sha256']
          for r in manifest['records'] if r['source_id'].split(':')[1] in ['0801','0802','0803','0804']}
cells = []


def md(text): cells.append(nbf.v4.new_markdown_cell(text))
def code(text): cells.append(nbf.v4.new_code_cell(text))
def defs(names): code('\n\n\n'.join(functions[name] for name in names))


md('''# 01 · Reconstruction baseline development
**Four DIV2K development sources · 17 September 2026**

## tl;dr
This notebook tests whether tuning classical regularisation repairs Pilot 00's weak baseline,
then rechecks local operator sensitivity on 16 × 16 patches. Execution status is recorded in notebook metadata; running the cells produces the outputs below.
This is development evidence; no novel method, deep-learning result, calibrated uncertainty,
or independent test performance is claimed.

**Colab:** Run all. The setup mounts your Drive and uses the existing four source images.
Results and figures are written directly into a new dated Drive folder. Pilot 00 is preserved.
No GPU is required. The complete computational code is embedded here.

## Context & Methods
- 3 true Gaussian blur widths × 2 Gaussian noise levels × 2 processing conditions = 12 conditions per source.
- Nominal inverse blur is always 1.0 px. A separate oracle diagnostic receives the true blur width.
- Ridge: minimise ‖Ax−y‖² + λ‖x‖². Gradient regularisation: minimise ‖Ax−y‖² + λ(‖Dx x‖²+‖Dy x‖²), with periodic forward differences.
- The FFT solution uses H*/(|H|²+λP). Ridge P=1; gradient P=4[sin²(πfx)+sin²(πfy)]. Clipping the solved image to [0,1] is separate postprocessing.
- For each evaluated development source, choose one λ for each regulariser/information mode using only the other three sources, averaged across all 12 conditions. All variants of one source stay together. Choices are not made separately using each evaluated image's true blur severity.
- Keep the input and a prespecified 0.5 px Gaussian smoothing control. These are not deep-learning baselines.

### Key Assumptions
The same 512 × 512 native centre region and 32 px margin as Pilot 00 are used. Stored gamma-encoded RGB and periodic blur are controlled approximations, not calibrated camera physics. True blur and noise levels are simulation settings; only the oracle branch receives true blur. Common random noise is coupled across severities. JPEG means clipping + 8-bit rounding + quality-75 JPEG, without chroma subsampling.

**Four sources have already influenced project development.** Leaving each one out of λ selection prevents direct source reuse within that step but does not make these untouched test data. There is one noise realisation per source, not independent repetitions. The finite λ grid and severity range are engineering choices; boundary optima are flagged.

**Score limits:** operator spread uses blur widths 0.8/1.0/1.2 px and is not a posterior or confidence interval. Measurement-noise spread uses a prespecified 2/255 perturbation amplitude at fixed operator, regardless of the true noise level. It is an antithetic perturbation control, not a calibrated image-only uncertainty estimator. Each spread is based on three reconstructions (nominal plus two perturbations); residual and gradient are cheaper. A learned image-only uncertainty comparator and matched-budget model comparisons remain outstanding.

## Data
0801–0804 remain development-only. Embedded expected decoded-RGB hashes come from the repository's official-archive manifest at commit `e1f2471db5be4ca4b1ed006415d47a9db001c7fc`.
All crops and degraded versions inherit that role. No original images are included in the repository.

### 1. Imports and fixed configuration
Dependencies: numpy, pandas, matplotlib and Pillow. Colab normally provides these; locally install them before running.
''')
code(setup)
md('### 2. Locate the images and create a dated destination\nLocal runs can set `IMAGING01_DATA_DIR` and `IMAGING01_OUTPUT_DIR`. The output path must be new; existing runs are never overwritten.')
code('''import os
import sys
from datetime import datetime, timezone
from IPython.display import display, Markdown

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
    if PROJECT_DIR.name == 'notebooks':
        PROJECT_DIR = PROJECT_DIR.parent

DATA_DIR = Path(os.environ.get('IMAGING01_DATA_DIR', str(PROJECT_DIR / 'samples')))
timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
OUTPUT_DIR = Path(os.environ.get('IMAGING01_OUTPUT_DIR', str(PROJECT_DIR / 'results' / ('pilot_01_' + timestamp))))
assert DATA_DIR.is_dir(), f'Source folder does not exist: {DATA_DIR}'
print('Sources:', ', '.join(CONFIG['source_ids']))
print('Results will be saved in:', OUTPUT_DIR)
EXPECTED_RGB_HASHES = ''' + repr(hashes))
md('### 3. Define the data and inverse operators\nBoth inverse methods share the same forward operator and boundaries. Their regularisers differ.')
defs(['sha256','transfer','penalty','apply','inverse_spectrum','interior','psnr','load_sources','observations'])
md('### 4. Define source-excluded tuning and patch evaluation\nRisk is mean RGB squared error per 16 × 16 patch. Patches are ranked within each image. The textured stratum is the top quarter by clean-reference patch gradient: evaluation-only, unavailable to the deployed selector. It checks performance among informative regions; it is not a calibration guarantee.')
defs(['metric_row','grid_search','choose_source_excluded','patch_mean','selected_risk','score_diagnostic','quality_summary'])
md('### 5. Validation and result saving\nA tiny dense linear solve independently checks each FFT inverse. Constant-image checks expose ridge shrinkage and verify gradient-regulariser DC preservation. Input hashes, source exclusions, row counts, and risk endpoints are checked. Every saved output receives a SHA-256 entry.')
defs(['validate_math','plot_figures','save_results','run'])
md('### 6. Execute the development experiment\nProgress is printed once per source and phase. This cell also creates all four figures and the result manifest.')
code("result = run(DATA_DIR, OUTPUT_DIR, EXPECTED_RGB_HASHES, CONFIG)\nprint(json.dumps(result['checks'], indent=2))")
md('## Results\n### 7. Inspect quality and tuning choices\nPooled PSNR converts mean MSE to dB; mean image PSNR is a separate statistic. The oracle-blur branch is a diagnostic, including an incomplete model in the JPEG condition.')
code("display(result['summary'].round(5))\ndisplay(result['selections'])\ndisplay(result['figures'][0])\ndisplay(result['figures'][1])")
md('### 8. Recheck patch selection and images\nThe plot shows the JPEG-chain condition; `curves.csv` contains both conditions. Each curve weights the 24 source/condition combinations equally within a reconstruction family. The two classical regularisers are not substitutes for testing independent learned reconstruction families.')
code("half = result['curves'].query('coverage == 0.5').groupby(['scenario','region','model','score']).mse.mean().unstack()\ndisplay(half.round(7))\ndisplay(result['figures'][2])\ndisplay(result['figures'][3])")
md('## Takeaways\n### 9. Read the computed decision summary\nThis summary uses saved results, not a promised outcome. It reports every family and both acquisition conditions.')
code('''s = result['summary']
for scenario in CONFIG['scenarios']:
    baseline_mse = float(s[(s.scenario == scenario) & (s.model == 'observed')].mean_mse.iloc[0])
    for family in CONFIG['families']:
        mse = float(s[(s.scenario == scenario) & (s.model == family) & (s.operator_info == 'nominal')].mean_mse.iloc[0])
        print(f'{scenario} | {family}: pooled PSNR gain over input = {10*np.log10(baseline_mse/mse):+.3f} dB')
for (scenario, region, family), values in half.iterrows():
    controls = values[['measurement_noise_spread','measurement_residual','image_gradient']]
    best = controls.idxmin()
    change = 100 * (1 - values.operator_spread / controls.min())
    print(f'{scenario} | {region} | {family}: operator spread vs best control ({best}) = {change:+.2f}% MSE reduction')
print('Boundary selections:', int(result['selections'].grid_boundary.sum()))
print('Development only. A positive entry is not a novelty, significance or calibration claim.')
print('Saved:', OUTPUT_DIR)
''')
md('''### What this can and cannot decide
A stronger classical baseline justifies moving to a verified pretrained reconstructor; it does not establish the proposed research contribution. A score advantage must survive useful coverage, informative-region checks, appropriate image-only uncertainty, matched information/compute, more than one learned family and source-disjoint calibration/testing.

If gains disappear against controls, redesign or stop the score rather than repeatedly tuning the same four sources. Read the unresolved direct competitor before making any definitive novelty claim. Full-reference MSE does not establish measurement support or hallucination detection.

The scoping review is a separate evidence-synthesis project. It may map what is already solved, conditional or untested even if this particular score fails. Its own added value over prior reviews and its formal methodology still require completion.

### Reproduction and sources
- [Pilot 00](https://github.com/Watchman77/reliable-reconstruction-under-mismatch/blob/main/notebooks/00_DIV2K_Operator_Mismatch_Pilot.ipynb)
- [Dataset and baseline audit](https://github.com/Watchman77/reliable-reconstruction-under-mismatch/blob/main/docs/dataset_and_baseline_audit_01.md)
- [Official DIV2K](https://data.vision.ee.ethz.ch/cvl/DIV2K/): academic research terms and original-image copyright apply.
- [Provisional gap synthesis](https://github.com/Watchman77/reliable-reconstruction-under-mismatch/blob/main/literature/synthesis/provisional_gap_synthesis_01.md)

The notebook is generated from `experiments/baseline_01/baseline.py`; its source hash is in notebook metadata. Software versions and output hashes are saved with each run. Rerunning in Colab is a separate environment check; this notebook never claims to have controlled your live Colab runtime.
''')
nb = nbf.v4.new_notebook(cells=cells)
nb.metadata.update(kernelspec=dict(display_name='Python 3', language='python', name='python3'),
    language_info=dict(name='python', version='3'), baseline_source_sha256=hashlib.sha256(text.encode()).hexdigest(),
    colab=dict(name='01_DIV2K_Baseline_Development.ipynb'),
    validation=dict(status='not_yet_executed', scope='four development sources'))
nbf.validate(nb)
target = ROOT / 'notebooks/01_DIV2K_Baseline_Development.ipynb'
nbf.write(nb, target)
print(target)
