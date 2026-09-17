"""Repair figure presentation from saved exports without rerunning inference.

Used only after the sequential local run completes. Rebuild the notebook with
the builder, then pass the original executed copy to preserve cells 1–4 and
verify their unchanged source text. Replay only presentation cells 5–10.
"""
import argparse,json,time
from pathlib import Path
import nbformat
from IPython.terminal.interactiveshell import TerminalInteractiveShell
from IPython.utils.capture import capture_output

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--notebook',type=Path,required=True)
p.add_argument('--executed-copy',type=Path,required=True)
p.add_argument('--run-dir',type=Path,required=True)
a=p.parse_args()
nb=nbformat.read(a.notebook,as_version=4);old=nbformat.read(a.executed_copy,as_version=4)
old_codes=[c for c in old.cells if c.cell_type=='code'];new_codes=[c for c in nb.cells if c.cell_type=='code']
assert len(new_codes)==len(old_codes)==10
for i in range(4):
 assert new_codes[i].source==old_codes[i].source
 assert old_codes[i].execution_count==i+1 and not any(o.output_type=='error' for o in old_codes[i].outputs)
 new_codes[i].outputs=old_codes[i].outputs;new_codes[i].execution_count=i+1;new_codes[i].metadata=old_codes[i].metadata
shell=TerminalInteractiveShell.instance();shell.display_formatter.active_types=['text/plain','text/html','image/png']
with capture_output():
 outcome=shell.run_cell(new_codes[0].source)
 assert not outcome.error_in_exec and not outcome.error_before_exec
setup=f"""OUTPUT_DIR=Path({str(a.run_dir.resolve())!r})
CONFIG=json.loads((OUTPUT_DIR/'config.json').read_text())
result={{'completed_observations':json.loads((OUTPUT_DIR/'status.json').read_text())['completed_observations']}}
for name in ['summary','quality','model_gaps','stage_deltas','endpoint_comparison','compute']:
    result[name]=pd.read_csv(OUTPUT_DIR/(name+'.csv'),dtype={{'source_id':str}})
"""
outcome=shell.run_cell(setup);assert not outcome.error_in_exec
for i,cell in enumerate(new_codes[4:],start=5):
 tic=time.perf_counter()
 with capture_output() as captured:outcome=shell.run_cell(cell.source,store_history=False)
 assert not outcome.error_in_exec and not outcome.error_before_exec
 cell.outputs=[];cell.execution_count=i
 for name,text in [('stdout',captured.stdout),('stderr',captured.stderr)]:
  if text:cell.outputs.append(nbformat.v4.new_output('stream',name=name,text=text))
 for item in captured.outputs:cell.outputs.append(nbformat.v4.new_output('display_data',data=item.data,metadata=item.metadata))
 cell.metadata.update(presentation_replayed_from_saved_exports=True,replay_seconds=round(time.perf_counter()-tic,3))
nb.metadata.validation=old.metadata.validation
nb.metadata.validation.update(status='executed_inprocess_with_presentation_replay',
 presentation_note='After numerical execution completed, figure displays were changed from Figure repr to embedded PNG display. Cells 5–10 were replayed from saved CSV/PNG/ZIP exports; unchanged cells 1–4 and their outputs are preserved. Learned inference was not repeated.',
 full_design_complete=False,configured_observations=4)
images=sum('image/png' in o.get('data',{}) for c in new_codes for o in c.outputs)
assert images==4
nbformat.validate(nb);nbformat.write(nb,a.notebook)
print(json.dumps({'code_cells':10,'embedded_pngs':images,'numerical_cells_unchanged':True,'presentation_cells_replayed':list(range(5,11))}))
