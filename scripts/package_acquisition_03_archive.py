"""Package an existing result ZIP for transfer; never run reconstruction.

Every output is an ordinary ZIP containing one byte segment of the original
archive and its metadata. All parts are needed to reassemble the original ZIP.
Uses only the Python standard library.
"""
import hashlib
import json
import math
from pathlib import Path
import zipfile


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def verify_parts(parts, output_archive=None):
    """Verify complete transfer parts; optionally restore original archive bytes."""
    parts = [Path(p) for p in parts]
    if not parts:
        raise ValueError('No transfer parts supplied.')
    entries = []
    for path in parts:
        with zipfile.ZipFile(path) as archive:
            if sorted(archive.namelist()) != ['archive_chunk.bin', 'transfer_part.json']:
                raise ValueError(f'Unexpected ZIP members: {path.name}')
            if archive.getinfo('transfer_part.json').file_size > 65536:
                raise ValueError('Oversized transfer metadata.')
            metadata = json.loads(archive.read('transfer_part.json'))
            if metadata['format'] != 'acquisition03-byte-parts-v1':
                raise ValueError('Unknown transfer format.')
            if archive.getinfo('archive_chunk.bin').file_size != metadata['chunk_bytes']:
                raise ValueError('Chunk byte count differs from metadata.')
            entries.append((metadata, path))
    entries.sort(key=lambda item: item[0]['part_index'])
    first = entries[0][0]
    if [m['part_index'] for m, _ in entries] != list(range(1, first['part_count'] + 1)):
        raise ValueError('Parts are missing or duplicated. Supply every part exactly once.')
    common = ['archive_name', 'archive_bytes', 'archive_sha256', 'part_count']
    offset = 0
    for metadata, _ in entries:
        if any(metadata[key] != first[key] for key in common):
            raise ValueError('Parts belong to different archives.')
        if metadata['chunk_offset'] != offset or metadata['chunk_bytes'] <= 0:
            raise ValueError('Invalid chunk offsets or sizes.')
        offset += metadata['chunk_bytes']
    if offset != first['archive_bytes']:
        raise ValueError('Parts do not cover the complete archive.')

    target = Path(output_archive) if output_archive is not None else None
    if target is not None and target.exists():
        raise FileExistsError(f'Will not overwrite: {target}')
    destination = target.open('xb') if target is not None else None
    whole_digest = hashlib.sha256()
    try:
        for metadata, path in entries:
            chunk_digest = hashlib.sha256()
            with zipfile.ZipFile(path) as archive, archive.open('archive_chunk.bin') as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b''):
                    chunk_digest.update(block)
                    whole_digest.update(block)
                    if destination is not None:
                        destination.write(block)
            if chunk_digest.hexdigest() != metadata['chunk_sha256']:
                raise ValueError(f'Chunk hash mismatch: {path.name}')
        if whole_digest.hexdigest() != first['archive_sha256']:
            raise ValueError('Reassembled archive SHA-256 mismatch.')
    except Exception:
        if destination is not None:
            destination.close()
            target.unlink(missing_ok=True)
        raise
    else:
        if destination is not None:
            destination.close()
    return dict(archive_bytes=offset, archive_sha256=whole_digest.hexdigest(),
                verified_parts=len(parts), byte_preserving_transfer_verified=True)


def package_archive(source, output_dir, expected_bytes, expected_sha256,
                    chunk_mib=96):
    """Validate the source receipt, package byte chunks, then verify readback."""
    source, output_dir = Path(source), Path(output_dir)
    if not source.is_file():
        raise FileNotFoundError(f'Saved ZIP not found: {source}. Check the Drive path; do not rerun the experiment.')
    if source.stat().st_size != expected_bytes:
        raise ValueError('Original ZIP size differs from the recorded run. Stop and report this difference.')
    print('Checking the original archive SHA-256...', flush=True)
    if sha256_file(source) != expected_sha256:
        raise ValueError('Original ZIP hash differs from Notebook 03. Stop and report this difference.')
    if not zipfile.is_zipfile(source):
        raise ValueError('Source file is not a ZIP archive.')
    if not isinstance(chunk_mib, int) or not 1 <= chunk_mib <= 96:
        raise ValueError('chunk_mib must be an integer from 1 to 96.')
    chunk_bytes = chunk_mib * 1024 * 1024
    count = math.ceil(expected_bytes / chunk_bytes)
    output_dir.mkdir(parents=True, exist_ok=False)
    paths, records = [], []
    with source.open('rb') as stream:
        for index in range(1, count + 1):
            offset = stream.tell()
            payload = stream.read(chunk_bytes)
            wanted = min(chunk_bytes, expected_bytes - offset)
            if len(payload) != wanted:
                raise ValueError('Original archive changed or could not be read completely.')
            metadata = dict(format='acquisition03-byte-parts-v1',
                            archive_name=source.name, archive_bytes=expected_bytes,
                            archive_sha256=expected_sha256, part_index=index,
                            part_count=count, chunk_offset=offset,
                            chunk_bytes=len(payload),
                            chunk_sha256=hashlib.sha256(payload).hexdigest())
            path = output_dir / f'acquisition03_transfer_part_{index:02d}_of_{count:02d}.zip'
            with zipfile.ZipFile(path, 'x', compression=zipfile.ZIP_STORED) as archive:
                archive.writestr('transfer_part.json', json.dumps(metadata, indent=2) + '\n')
                archive.writestr('archive_chunk.bin', payload)
            del payload
            if path.stat().st_size >= 100 * 1024 * 1024:
                raise ValueError('A transfer ZIP exceeded the 100 MiB cap.')
            paths.append(path)
            records.append(dict(name=path.name, bytes=path.stat().st_size,
                                sha256=sha256_file(path)))
            print(f'Created {path.name} ({path.stat().st_size / 1024**2:.2f} MiB)', flush=True)
        if stream.read(1):
            raise ValueError('Original archive grew during packaging.')
    print('Verifying all saved parts against the original hash...', flush=True)
    verified = verify_parts(paths)
    receipt = dict(**verified, original_archive_name=source.name,
                   original_expected_hash_source='Caller-supplied recorded receipt',
                   experiment_rerun=False, raw_prediction_metrics_recomputed=False,
                   parts=records)
    (output_dir / 'transfer_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(f'PASS: all {len(paths)} parts reproduce the original archive bytes.', flush=True)
    return paths, receipt
