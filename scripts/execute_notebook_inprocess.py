"""Execute notebook cells in order without launching a Jupyter kernel.

This documented fallback is useful where kernel sockets are unavailable. It
checks Python execution and saves rich outputs; it does not validate Colab,
Drive mounting or the native Jupyter kernel lifecycle. Use a fresh process.
Dependencies: nbformat, IPython, matplotlib-inline, plus notebook dependencies.
"""
import argparse
import time
from datetime import datetime, timezone
from pathlib import Path

import nbformat
from IPython.terminal.interactiveshell import TerminalInteractiveShell
from IPython.utils.capture import capture_output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('notebook', type=Path)
    args = parser.parse_args()
    nb = nbformat.read(args.notebook, as_version=4)
    nbformat.validate(nb)
    for cell in nb.cells:
        if cell.cell_type == 'code':
            cell.outputs = []
            cell.execution_count = None
    shell = TerminalInteractiveShell.instance()
    shell.display_formatter.active_types = ['text/plain', 'text/html', 'image/png', 'image/svg+xml']
    metadata = dict(status='in_progress', mode='sequential in-process IPython; no Jupyter kernel',
        started_utc=datetime.now(timezone.utc).isoformat(),
        limitation='Native Jupyter/Colab execution and Drive mounting are unverified.',
        scope='Four development sources; original cell code is executed without replacement.')
    nb.metadata.validation = metadata
    count = 0
    for index, cell in enumerate(nb.cells):
        if cell.cell_type != 'code':
            continue
        count += 1
        print(f'Executing code cell {count} (notebook index {index})', flush=True)
        tic = time.perf_counter()
        with capture_output() as captured:
            execution = shell.run_cell(cell.source, store_history=False)
        cell.execution_count = count
        if captured.stdout:
            cell.outputs.append(nbformat.v4.new_output('stream', name='stdout', text=captured.stdout))
        if captured.stderr:
            cell.outputs.append(nbformat.v4.new_output('stream', name='stderr', text=captured.stderr))
        for item in captured.outputs:
            cell.outputs.append(nbformat.v4.new_output('display_data', data=item.data, metadata=item.metadata))
        error = execution.error_before_exec or execution.error_in_exec
        cell.metadata.inprocess_execution_seconds = round(time.perf_counter() - tic, 3)
        if error:
            cell.outputs.append(nbformat.v4.new_output('error', ename=type(error).__name__,
                evalue=str(error), traceback=captured.stdout.splitlines()))
            nb.metadata.validation['status'] = 'failed'
            nbformat.write(nb, args.notebook)
            print(captured.stdout, flush=True)
            raise RuntimeError(f'Cell {count} failed') from error
        nbformat.write(nb, args.notebook)
        print(f'Completed in {time.perf_counter() - tic:.2f}s; {len(cell.outputs)} outputs', flush=True)
    nb.metadata.validation.update(status='executed_inprocess', code_cells=count,
        finished_utc=datetime.now(timezone.utc).isoformat())
    nbformat.validate(nb)
    nbformat.write(nb, args.notebook)
    print('Saved validated notebook with captured outputs:', args.notebook)


if __name__ == '__main__':
    main()
