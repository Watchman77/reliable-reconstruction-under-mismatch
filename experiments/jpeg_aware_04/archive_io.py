"""Verified summary/full ZIP export and bounded transfer parts for experiment 04."""
import hashlib
import json
from pathlib import Path
import zipfile


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def verify_manifest(run):
    run=Path(run);manifest=json.loads((run/'export_manifest.json').read_text())
    assert json.loads((run/'status.json').read_text())['status']=='complete_for_configured_subset'
    names={r['name'] for r in manifest['files']}
    assert len(names)==len(manifest['files'])
    assert names=={str(p.relative_to(run)) for p in run.rglob('*') if p.is_file() and p.name!='export_manifest.json'}
    for r in manifest['files']:
        p=run/r['name'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
    return manifest


def make_zip(target,run,names,readme=None):
    target=Path(target);run=Path(run)
    expected={run.name+'/'+n:run/n for n in names}
    if not target.exists():
        temporary=target.with_suffix('.zip.partial')
        with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for name,p in sorted(expected.items()):z.write(p,name)
            if readme:z.writestr('READ_ME_FIRST.txt',readme)
        temporary.replace(target)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        assert set(z.namelist())==set(expected)|({'READ_ME_FIRST.txt'} if readme else set())
        for name,p in expected.items():
            h=hashlib.sha256()
            with z.open(name) as f:
                for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
            assert h.hexdigest()==sha(p),name
        if readme:assert z.read('READ_ME_FIRST.txt').decode()==readme
    return dict(path=str(target),bytes=target.stat().st_size,sha256=sha(target),entries=len(expected)+(1 if readme else 0))


def split_archive(archive,chunk_bytes=96*1024**2):
    archive=Path(archive);assert 0<chunk_bytes<=96*1024**2
    whole_hash=sha(archive);size=archive.stat().st_size;count=(size+chunk_bytes-1)//chunk_bytes
    folder=archive.parent/(archive.stem+'_upload_parts');folder.mkdir(exist_ok=True)
    parts=[]
    with archive.open('rb') as source:
        for index in range(1,count+1):
            block=source.read(chunk_bytes)
            info=dict(format='jpeg_aware04_raw_zip_chunks_v1',archive_name=archive.name,
                archive_sha256=whole_hash,archive_bytes=size,index=index,total_parts=count,
                chunk_bytes=len(block),chunk_sha256=hashlib.sha256(block).hexdigest())
            part=folder/f'{archive.stem}_part_{index:03d}_of_{count:03d}.zip'
            if not part.exists():
                temporary=part.with_suffix('.zip.partial')
                with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_STORED) as z:
                    z.writestr('archive_chunk.bin',block)
                    z.writestr('transfer_part.json',json.dumps(info,indent=2)+'\n')
                temporary.replace(part)
            with zipfile.ZipFile(part) as z:
                assert z.testzip() is None and set(z.namelist())=={'archive_chunk.bin','transfer_part.json'}
                assert json.loads(z.read('transfer_part.json'))==info
                assert z.read('archive_chunk.bin')==block
            assert part.stat().st_size<100*1024**2
            parts.append(part)
    verified=verify_parts(parts)
    assert verified['archive_sha256']==whole_hash
    return parts,verified


def verify_parts(parts,destination=None):
    """Verify complete unordered parts; optionally reconstruct a previously absent ZIP."""
    records=[]
    for p in map(Path,parts):
        with zipfile.ZipFile(p) as z:
            assert z.testzip() is None and set(z.namelist())=={'archive_chunk.bin','transfer_part.json'}
            m=json.loads(z.read('transfer_part.json'))
            assert m['format']=='jpeg_aware04_raw_zip_chunks_v1'
            records.append((m,p))
    assert records
    records.sort(key=lambda a:a[0]['index']);first=records[0][0]
    assert [m['index'] for m,p in records]==list(range(1,first['total_parts']+1)), 'Missing/duplicate transfer part'
    if destination is not None:
        destination=Path(destination);assert not destination.exists()
        output=destination.with_suffix(destination.suffix+'.partial');assert not output.exists()
        stream=output.open('xb')
    else:stream=None
    digest=hashlib.sha256();size=0
    try:
        for m,p in records:
            assert all(m[k]==first[k] for k in ['archive_name','archive_sha256','archive_bytes','total_parts'])
            with zipfile.ZipFile(p) as z:block=z.read('archive_chunk.bin')
            assert len(block)==m['chunk_bytes'] and hashlib.sha256(block).hexdigest()==m['chunk_sha256']
            digest.update(block);size+=len(block)
            if stream:stream.write(block)
        assert size==first['archive_bytes'] and digest.hexdigest()==first['archive_sha256']
    finally:
        if stream:stream.close()
    if destination is not None:output.replace(destination)
    return dict(archive_name=first['archive_name'],archive_bytes=size,archive_sha256=digest.hexdigest(),
        verified_parts=len(records),part_paths=[str(p) for m,p in records])


def export(run):
    run=Path(run);manifest=verify_manifest(run)
    names=[r['name'] for r in manifest['files']]+['export_manifest.json']
    summary_names=[n for n in names if not n.startswith(('predictions/','codec_inputs/'))]
    summary=make_zip(run.parent/(run.name+'_SUMMARY.zip'),run,summary_names,
        'SUMMARY ONLY. Raw predictions and codec inputs are omitted. The included full-run manifest lists omitted files too.\n'
        'Use ALL RAW transfer parts for independent saved-array verification.\n')
    raw_path=run.parent/(run.name+'_RAW.zip');raw=make_zip(raw_path,run,names)
    parts,verification=split_archive(raw_path)
    receipt=dict(experiment='jpeg_aware_04',summary=summary,raw=raw,transfer=verification,
        manifest_files_verified=len(manifest['files']),full_design_complete=json.loads((run/'status.json').read_text())['full_design_complete'])
    (run.parent/(run.name+'_EXPORT_RECEIPT.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt
