#!/usr/bin/env python3
"""Acquire official DIV2K validation HR images for development, never unseen testing.

The DPIR paper reports 900 DIV2K training images. This script deliberately
assigns every source to development and does not create calibration/test splits.
Raw images and crops stay in ignored data directories; only metadata is tracked.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import urllib.request
import zipfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://data.vision.ee.ethz.ch/cvl/DIV2K/DIV2K_valid_HR.zip'
EXPECTED_BYTES = 448993893  # Official server HEAD, checked 16 September 2026.


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def download(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.zip.part')
    try:
        with urllib.request.urlopen(URL, timeout=60) as response, temp.open('wb') as out:
            received = 0
            next_report = 50 * 1024 * 1024
            for chunk in iter(lambda: response.read(1024 * 1024), b''):
                out.write(chunk)
                received += len(chunk)
                if received >= next_report:
                    print(f'Downloaded {received / 1024**2:.0f} MiB', flush=True)
                    next_report += 50 * 1024 * 1024
        if received != EXPECTED_BYTES:
            raise ValueError(f'Archive size changed: {received}; inspect source before updating expectation')
        with zipfile.ZipFile(temp) as archive:
            if archive.testzip() is not None:
                raise ValueError('ZIP CRC check failed')
        os.replace(temp, path)
    except Exception:
        temp.unlink(missing_ok=True)
        raise


def prepare(archive_path: Path, output: Path, crop_size: int) -> dict:
    if crop_size < 16:
        raise ValueError('Crop size must be at least 16')
    if archive_path.stat().st_size != EXPECTED_BYTES:
        raise ValueError('Unexpected archive size; inspect the source')
    crop_root = ROOT / 'data/processed/div2k_development' / str(crop_size)
    crop_root.mkdir(parents=True, exist_ok=True)
    rows = []
    pixel_hashes: set[str] = set()
    with zipfile.ZipFile(archive_path) as archive:
        wanted = [f'DIV2K_valid_HR/{i:04d}.png' for i in range(801, 901)]
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Archive contains duplicate names')
        actual_png = sorted(n for n in names if n.lower().endswith('.png'))
        if actual_png != wanted:
            raise ValueError('Archive does not contain exactly the expected 100 source PNGs')
        for name in wanted:
            # Read exact validated members; do not extract arbitrary archive paths.
            blob = archive.read(name)
            with Image.open(io.BytesIO(blob)) as raw:
                raw.load()
                width, height = raw.size
                if raw.mode != 'RGB' or min(width, height) < crop_size:
                    raise ValueError(f'Unexpected mode/dimensions for {name}')
                pixel_hash = hashlib.sha256(raw.tobytes()).hexdigest()
                if pixel_hash in pixel_hashes:
                    raise ValueError('Identical decoded source images detected')
                pixel_hashes.add(pixel_hash)
                left, top = (width - crop_size) // 2, (height - crop_size) // 2
                box = (left, top, left + crop_size, top + crop_size)
                crop_path = crop_root / Path(name).name
                raw.crop(box).save(crop_path)
            rows.append({
                'source_id': 'DIV2K:' + Path(name).stem,
                'official_split': 'validation', 'project_split': 'development',
                'archive_member': name, 'source_sha256': hashlib.sha256(blob).hexdigest(),
                'source_pixels_sha256': pixel_hash, 'width': width, 'height': height,
                'crop_box_xyxy': list(box), 'crop_path': crop_path.relative_to(ROOT).as_posix(),
                'crop_sha256': sha256(crop_path),
            })
    result = {
        'schema_version': 1, 'dataset': 'DIV2K validation HR',
        'purpose': 'development_only', 'evaluation_approved': False,
        'reason': 'Known dataset-level overlap with reported DPIR denoiser training; not held-out evaluation.',
        'source_url': URL, 'terms_url': 'https://data.vision.ee.ethz.ch/cvl/DIV2K/',
        'terms_summary': 'Academic research only; original image copyright remains with owners.',
        'archive_bytes': archive_path.stat().st_size, 'archive_sha256': sha256(archive_path),
        'archive_local_path': archive_path.resolve().relative_to(ROOT).as_posix(),
        'preprocessing': {'crop': 'native-resolution center', 'size': crop_size,
                          'resize': False, 'padding': False, 'colour': 'stored RGB, no linearization'},
        'independence': 'Exact decoded-source duplicates checked; semantic/scene duplicates not assessed.',
        'source_count': len(rows), 'records': rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix(output.suffix + '.tmp')
    temp.write_text(json.dumps(result, indent=2) + '\n')
    os.replace(temp, output)
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--download', action='store_true', help='Fetch official 449 MB archive if absent')
    p.add_argument('--crop-size', type=int, default=256)
    args = p.parse_args()
    archive = ROOT / 'data/raw/DIV2K_valid_HR.zip'
    if not archive.exists():
        if not args.download:
            p.error('Archive missing; supply --download to fetch it')
        download(archive)
    output = ROOT / 'data/manifests/div2k_development_100.json'
    result = prepare(archive, output, args.crop_size)
    print(json.dumps({'manifest': str(output), 'sources': result['source_count'],
                      'purpose': result['purpose'], 'archive_sha256': result['archive_sha256']}))


if __name__ == '__main__':
    main()
