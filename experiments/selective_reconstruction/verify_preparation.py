#!/usr/bin/env python3
"""Reproduce checkpoint-01 data and forward-operator integrity checks."""
import hashlib
import json
from pathlib import Path

import numpy as np
import PIL
from PIL import Image
import scipy

from prepare_observations import ROOT, array_hash, forward_blur, make_pair


def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    rng = np.random.default_rng(17)
    x = rng.normal(size=(32, 32, 3)).astype(np.float32)
    z = rng.normal(size=x.shape).astype(np.float32)
    constant_error = float(np.max(abs(forward_blur(np.ones_like(x), 1.6) - 1)))
    fx, fz = forward_blur(x, 1.6), forward_blur(z, 1.6)
    adjoint_error = float(abs(np.sum(fx * z, dtype=np.float64) - np.sum(x * fz, dtype=np.float64)))
    impulse = np.zeros_like(x)
    impulse[0, 0, :] = 1
    response = forward_blur(impulse, 1.6)
    fft_y = np.fft.ifft2(np.fft.fft2(x, axes=(0, 1)) * np.fft.fft2(response, axes=(0, 1)), axes=(0, 1)).real
    fft_error = float(np.max(abs(fx - fft_y)))
    if constant_error >= 1e-6 or adjoint_error >= 1e-5 or fft_error >= 1e-6:
        raise ValueError('Forward operator check failed')
    mp = ROOT / 'data/manifests/div2k_development_100.json'
    manifest = json.loads(mp.read_text())
    if manifest['source_count'] != 100 or manifest['evaluation_approved']:
        raise ValueError('Unexpected dataset purpose or count')
    if len({r['source_pixels_sha256'] for r in manifest['records']}) != 100:
        raise ValueError('Source duplicate detected')
    if digest(ROOT / manifest['archive_local_path']) != manifest['archive_sha256']:
        raise ValueError('Archive checksum changed')
    for r in manifest['records']:
        crop = ROOT / r['crop_path']
        if r['project_split'] != 'development' or digest(crop) != r['crop_sha256']:
            raise ValueError('Source split or crop checksum changed')
        with Image.open(crop) as im:
            if im.size != (256, 256):
                raise ValueError('Checkpoint 01 expects 256 pixel crops')
    folder = ROOT / 'data/processed/development_observations'
    obs_path = folder / 'manifest.json'
    obs = json.loads(obs_path.read_text())
    if obs['source_manifest_sha256'] != digest(mp) or obs['source_count'] != 12:
        raise ValueError('Checkpoint 01 expects 12 sources from the current manifest')
    for r in obs['records']:
        with np.load(folder / r['file']) as a:
            for key in ['clean', 'blur_noise', 'omitted_processing']:
                if array_hash(a[key]) != r[key + '_array_sha256']:
                    raise ValueError('Stored array changed')
            y, j = make_pair(a['clean'], r['seed'])
            if not np.array_equal(y, a['blur_noise']) or not np.array_equal(j, a['omitted_processing']):
                raise ValueError('Observation regeneration differs')
    report = {
        'date': '2026-09-17', 'scope': 'data and forward-operator engineering checks only',
        'reconstruction_run': False, 'sources_acquired': 100,
        'sources_in_observation_smoke_run': 12, 'observations_generated': 24,
        'constant_preservation_max_error': constant_error,
        'adjoint_inner_product_absolute_error': adjoint_error,
        'fft_equivalence_max_error': fft_error,
        'all_source_and_crop_hashes_verified': True, 'exact_decoded_source_duplicates': 0,
        'all_observations_regenerated_identically': True,
        'source_manifest_sha256': digest(mp), 'observation_manifest_sha256': digest(obs_path),
        'versions': {'numpy': np.__version__, 'scipy': scipy.__version__, 'Pillow': PIL.__version__},
        'scripts': {p: digest(ROOT / p) for p in [
            'experiments/selective_reconstruction/prepare_observations.py',
            'scripts/prepare_div2k_development.py']},
    }
    (Path(__file__).parent / 'engineering_check_01.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
