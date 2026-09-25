#!/usr/bin/env python3
"""Build the Stage 06C Colab canary launcher without executing model inference."""

from __future__ import annotations

import nbformat as nbf
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "notebooks/06C_RAISE_Paired_DPIR_DiffPIR_Development.ipynb"


def main() -> None:
    cells = [
        nbf.v4.new_markdown_cell("""# 06C · Paired DPIR–DiffPIR on audited RAISE development images

## Goal

Run one **development early-stop source** through the same two JPEG acquisition chains and the same detail-error evaluator using DPIR and DiffPIR. Compare each solver's nominal input with FBCNN preprocessing; for the linear-light chain the aware arm also converts the measurement to linear light before inversion. This is a **development canary**, not a confirmatory result.

The runner verifies the 994-source eligibility manifest, the independently audited RAW and rendered-RGB digests, both existing DPIR/FBCNN checkpoints, the exact DiffPIR Git commit, and the downloaded DiffPIR checkpoint digest. It refuses calibration, pilot and independent source IDs. No Stage 05 outputs or Stage 06 independent outcomes are loaded.

**Preparation:** in Colab select **Runtime → Change runtime type → GPU**. The project Drive folder must contain `inputs/RAISE-1k/NEF/` and `results/stage06b_external_audit/external_source_audit.csv`, plus `model_cache/drunet_color.pth` and `model_cache/fbcnn_color.pth`. The notebook downloads the public DiffPIR ImageNet checkpoint from the [official model zoo](https://github.com/yuanzhi-zhu/DiffPIR/blob/2a9898129a1b274131b98746e5b364bc20adc1e1/model_zoo/README.md) if it is missing. First use may download a large weight file.

**Operator note:** The earlier 06C acquisition smoke used reflective edges. This solver run generates new observations with the Stage 05 periodic Gaussian operator, which both inverse solvers use in their data steps. The two receipts are separate studies; do not pool their pixel numbers."""),
        nbf.v4.new_markdown_cell("## 1. Set up the runtime and Drive"),
        nbf.v4.new_code_cell("""%pip -q install 'rawpy>=0.21,<1' 'requests>=2.31,<3'
import os, sys, subprocess, json, hashlib
from pathlib import Path
from datetime import datetime, timezone
import torch
assert torch.cuda.is_available(), 'Select a GPU runtime before running the solver cells.'
from google.colab import drive
drive.mount('/content/drive')
PROJECT = Path('/content/drive/MyDrive/reliable-reconstruction-under-mismatch')
assert PROJECT.is_dir(), f'Missing project folder: {PROJECT}'
print('GPU:', torch.cuda.get_device_name(0))"""),
        nbf.v4.new_markdown_cell("## 2. Check out the research runner and pin DiffPIR source"),
        nbf.v4.new_code_cell("""REPO = Path('/content/stage06_research_repo')
if not REPO.exists():
    subprocess.run(['git','clone','--depth','1','https://github.com/Watchman77/reliable-reconstruction-under-mismatch.git',str(REPO)],check=True)
research_commit = subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()
assert (REPO/'scripts/run_stage06c_paired_development.py').is_file(), 'Runner missing; refresh research checkout.'
DIFFPIR = Path('/content/stage06_DiffPIR')
if not DIFFPIR.exists():
    subprocess.run(['git','clone','https://github.com/yuanzhi-zhu/DiffPIR.git',str(DIFFPIR)],check=True)
PIN = '2a9898129a1b274131b98746e5b364bc20adc1e1'
subprocess.run(['git','-C',str(DIFFPIR),'checkout','--detach',PIN],check=True)
assert subprocess.check_output(['git','-C',str(DIFFPIR),'rev-parse','HEAD'],text=True).strip() == PIN
print('Research commit:',research_commit,'\\nDiffPIR commit:',PIN)"""),
        nbf.v4.new_markdown_cell("## 3. Verify one audited source before any model download"),
        nbf.v4.new_code_cell("""SOURCE_IDS = ['r137bcd7at']  # development early-stop; change only to other eligible development IDs
NEF_DIR = PROJECT/'inputs/RAISE-1k/NEF'
AUDIT = PROJECT/'results/stage06b_external_audit/external_source_audit.csv'
assert NEF_DIR.is_dir() and AUDIT.is_file(), 'Run the 06B audit first; missing NEFs or audit CSV.'
preflight = [sys.executable,str(REPO/'scripts/run_stage06c_paired_development.py'),
    '--mode','preflight','--nef-dir',str(NEF_DIR),'--audit-csv',str(AUDIT),
    '--source-ids',*SOURCE_IDS]
subprocess.run(preflight,check=True)"""),
        nbf.v4.new_markdown_cell("## 4. Download and hash the official ImageNet DiffPIR checkpoint"),
        nbf.v4.new_code_cell("""import requests
MODEL_CACHE = PROJECT/'model_cache'
MODEL_CACHE.mkdir(parents=True,exist_ok=True)
CHECKPOINT = MODEL_CACHE/'256x256_diffusion_uncond.pt'
MODEL_URL = 'https://openaipublic.blob.core.windows.net/diffusion/jul-2021/256x256_diffusion_uncond.pt'
PART = CHECKPOINT.with_suffix('.pt.part')
if not CHECKPOINT.exists():
    offset = PART.stat().st_size if PART.exists() else 0
    headers = {'Range':f'bytes={offset}-'} if offset else {}
    with requests.get(MODEL_URL,headers=headers,stream=True,timeout=(30,120)) as response:
        response.raise_for_status()
        if offset and response.status_code == 206:
            assert response.headers.get('Content-Range','').startswith(f'bytes {offset}-'), 'Server returned wrong range'
            mode = 'ab'
        elif response.status_code == 200:
            offset, mode = 0, 'wb'  # server ignored Range; restart partial file
        else:
            raise RuntimeError(f'Unexpected download status {response.status_code}')
        total = offset + int(response.headers.get('Content-Length','0'))
        with PART.open(mode) as out:
            for block in response.iter_content(chunk_size=1024*1024):
                if block:out.write(block)
    assert total and PART.stat().st_size == total, 'Incomplete checkpoint; rerun this cell to resume'
    PART.replace(CHECKPOINT)
def sha256_file(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()
checkpoint_sha = sha256_file(CHECKPOINT)
CHECKPOINT_RECEIPT = MODEL_CACHE/'stage06c_diffpir_checkpoint_receipt.json'
if CHECKPOINT_RECEIPT.exists():
    previous=json.loads(CHECKPOINT_RECEIPT.read_text())
    assert previous['sha256'] == checkpoint_sha and previous['bytes'] == CHECKPOINT.stat().st_size, 'Checkpoint differs from first recorded download'
else:
    CHECKPOINT_RECEIPT.write_text(json.dumps({'source':MODEL_URL,'filename':CHECKPOINT.name,
        'bytes':CHECKPOINT.stat().st_size,'sha256':checkpoint_sha,'upstream_commit':PIN,
        'recorded_at_utc':datetime.now(timezone.utc).isoformat(),
        'claim':'observed downloaded bytes; not publisher-signed and not a final model freeze'},indent=2)+'\\n')
print('DiffPIR checkpoint SHA-256:',checkpoint_sha)
print('Bytes:',CHECKPOINT.stat().st_size)"""),
        nbf.v4.new_markdown_cell("## 5. Execute the paired development canary\n\nThis is GPU work. The selected source generates two acquisition chains × two solvers × two methods. The runner writes an output row after each reconstruction. It keeps partial results and records an error if the run fails; it never labels a partial run complete."),
        nbf.v4.new_code_cell("""RUN_DIR = PROJECT/'results'/('stage06c_paired_canary_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
command = [sys.executable,str(REPO/'scripts/run_stage06c_paired_development.py'),
    '--mode','run','--nef-dir',str(NEF_DIR),'--audit-csv',str(AUDIT),
    '--source-ids',*SOURCE_IDS, '--model-cache',str(MODEL_CACHE),
    '--diffpir-root',str(DIFFPIR),'--diffpir-checkpoint',str(CHECKPOINT),
    '--checkpoint-sha256',checkpoint_sha,'--output-dir',str(RUN_DIR),
    '--nfe','20']  # development canary; select/freeze NFE before independent test
print('Research commit:',research_commit,'\\nOutput:',RUN_DIR)
subprocess.run(command,check=True)"""),
        nbf.v4.new_markdown_cell("## 6. Read the source-paired outcome and integrity receipt\n\nA one-source canary tests integration; it cannot establish generalisation. Share the receipt and row file for inspection before scaling to development-fit and early-stop images."),
        nbf.v4.new_code_cell("""import pandas as pd
status=json.loads((RUN_DIR/'status.json').read_text())
assert status['status']=='completed_development_only'
assert status['independent_test_inference'] is False
row_path=RUN_DIR/'source_method_rows.json'
assert sha256_file(row_path)==status['source_method_rows_sha256']
rows=pd.DataFrame(json.loads(row_path.read_text())['rows'])
display(rows[['source_id','role','chain_id','solver','method','rgb_mse','detail_mse','elapsed_seconds']])
paired=rows.pivot(index=['source_id','chain_id','solver'],columns='method',values='detail_mse')
paired['nominal_minus_aware_detail_mse']=paired['nominal']-paired['chain_aware']
display(paired)
print('Upload/share these two small files:',RUN_DIR/'status.json',row_path)
print('This is one development source; no independent test was run.')"""),
        nbf.v4.new_markdown_cell("## Next steps\n\nAfter the one-source run and operator/metric checks pass, expand `SOURCE_IDS` only within development-fit and development early-stop roles in a **new** run directory. Choose solver settings on development data, check source-level effects and failed runs, then train Stage 06D reliability models. A freeze and a separate independent run are required before any publication claim or manuscript edit."),
    ]
    notebook = nbf.v4.new_notebook(cells=cells, metadata={
        "kernelspec": {"display_name":"Python 3", "language":"python", "name":"python3"},
        "colab": {"name":OUTPUT.name,"provenance":[],"gpuType":"L4"},
        "accelerator":"GPU",
        "research_stage":"06C_development_canary",
        "independent_test_run_authorized":False,
    })
    nbf.validate(notebook)
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    nbf.write(notebook, OUTPUT)
    print(OUTPUT, "cells:",len(cells))


if __name__ == "__main__":
    main()
