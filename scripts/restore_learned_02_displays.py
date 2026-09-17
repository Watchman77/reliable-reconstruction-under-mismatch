"""Restore final presentation cells from saved results, without rerunning inference.

The sequential runner reported all nine cells complete, but readback retained
only cells 1-7. This records the separate replay of presentation cells 8-9;
it does not label the replay as a new reconstruction or a native kernel run.
"""
from datetime import datetime, timezone
from pathlib import Path
import nbformat
import pandas as pd
from PIL import Image
import numpy as np
from IPython.display import display
from IPython.terminal.interactiveshell import TerminalInteractiveShell
from IPython.utils.capture import capture_output
import json
import base64

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'experiments/learned_02/outputs/canary_20260917'
NB = ROOT/'notebooks/02_DIV2K_Learned_Baseline.ipynb'
nb = nbformat.read(NB,as_version=4)
result = {name:pd.read_csv(OUT/(name+'.csv'),dtype={'source_id':str}) for name in ['quality','summary','curves','compute']}
result['figures'] = [Image.open(OUT/name).copy() for name in ['quality.png','detail_risk_coverage.png','reconstruction_examples.png','iteration_trajectories.png']]
result['completed_observations'] = json.loads((OUT/'status.json').read_text())['completed_observations']
config = json.loads((OUT/'config.json').read_text())
shell = TerminalInteractiveShell.instance()
shell.display_formatter.active_types=['text/plain','text/html','image/png']
shell.user_ns.update(result=result,CONFIG=config,OUTPUT_DIR=OUT,display=display,np=np)
for count,index in [(8,15),(9,17)]:
    cell=nb.cells[index]
    with capture_output() as captured:
        execution=shell.run_cell(cell.source,store_history=False)
    error=execution.error_before_exec or execution.error_in_exec
    if error:raise RuntimeError(captured.stdout) from error
    cell.execution_count=count;cell.outputs=[]
    for name,value in [('stdout',captured.stdout),('stderr',captured.stderr)]:
        if value:cell.outputs.append(nbformat.v4.new_output('stream',name=name,text=value))
    for item in captured.outputs:
        data = {mime:base64.b64encode(value).decode() if isinstance(value,bytes) else value for mime,value in item.data.items()}
        cell.outputs.append(nbformat.v4.new_output('display_data',data=data,metadata=item.metadata))
    cell.metadata.presentation_readback='Replayed unchanged display-cell code from persisted CSVs and PNGs; inference was not repeated.'
nb.metadata.validation.update(status='executed_inprocess_with_display_readback',code_cells=9,
    finished_utc=datetime.now(timezone.utc).isoformat(),
    presentation_replay={'cells':[8,9],'reason':'Sequential runner reported completion; final file readback retained only cells 1-7.',
                        'source':'Saved run CSVs and PNGs; numerical experiment not rerun.'})
nbformat.validate(nb)
nbformat.write(nb,NB)
check=nbformat.read(NB,as_version=4)
assert [c.execution_count for c in check.cells if c.cell_type=='code']==list(range(1,10))
print('Saved and read back all nine cells; separate display replay recorded in metadata.')
