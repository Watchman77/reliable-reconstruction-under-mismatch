#!/usr/bin/env python3
"""Generate development-only paired measurements; no reconstruction is run.

The first condition retains float blur-plus-noise measurements. The second
adds clipping, uint8 quantization and JPEG. These omitted processing steps
are all declared, rather than calling their combination pure compression.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

ROOT = Path(__file__).resolve().parents[2]


def array_hash(x: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()


def forward_blur(x: np.ndarray, sigma: float) -> np.ndarray:
    return gaussian_filter(x, sigma=(sigma, sigma, 0), mode='wrap', truncate=4.0).astype(np.float32)


def jpeg_process(y: np.ndarray, quality: int) -> np.ndarray:
    b = io.BytesIO()
    u8 = np.rint(np.clip(y, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(u8).save(b, format='JPEG', quality=quality, subsampling=2)
    b.seek(0)
    with Image.open(b) as im:
        return np.asarray(im.convert('RGB'), dtype=np.float32) / 255


def make_pair(x: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    y = forward_blur(x, 1.6) + rng.normal(0, 0.01, x.shape).astype(np.float32)
    return y, jpeg_process(y, 40)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--limit', type=int, default=12)
    p.add_argument('--seed', type=int, default=20260917)
    p.add_argument('--output-dir', type=Path, default=ROOT / 'data/processed/development_observations')
    args = p.parse_args()
    manifest_path = ROOT / 'data/manifests/div2k_development_100.json'
    raw_manifest = manifest_path.read_bytes()
    manifest = json.loads(raw_manifest)
    assert manifest['purpose'] == 'development_only' and not manifest['evaluation_approved']
    if not 1 <= args.limit <= len(manifest['records']):
        p.error('limit must be between one and the number of development sources')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in manifest['records'][:args.limit]:
        assert r['project_split'] == 'development'
        path = ROOT / r['crop_path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != r['crop_sha256']:
            raise ValueError('Crop changed since source manifest was prepared')
        with Image.open(path) as im:
            x = np.asarray(im.convert('RGB'), dtype=np.float32) / 255
        seed = int.from_bytes(hashlib.sha256(f"{args.seed}/{r['source_id']}".encode()).digest()[:8], 'big')
        y, compound = make_pair(x, seed)
        assert x.shape == y.shape == compound.shape and np.isfinite(y).all()
        output = args.output_dir / (path.stem + '.npz')
        np.savez_compressed(output, clean=x, blur_noise=y, omitted_processing=compound)
        rows.append({'source_id': r['source_id'], 'project_split': 'development',
                     'seed': seed, 'shape': list(x.shape), 'file': output.name,
                     'clean_array_sha256': array_hash(x), 'blur_noise_array_sha256': array_hash(y),
                     'omitted_processing_array_sha256': array_hash(compound)})
    report = {
        'schema_version': 1, 'purpose': 'development_only', 'reconstruction_run': False,
        'source_manifest_sha256': hashlib.sha256(raw_manifest).hexdigest(),
        'master_seed': args.seed, 'source_count': len(rows), 'observation_count': 2 * len(rows),
        'measurement_format': 'NPZ float32 arrays; do not replace float observations with PNG previews',
        'colour': 'stored RGB values; controlled approximation, not a calibrated camera simulator',
        'boundary': 'circular; identical channel-independent Gaussian filter',
        'nominal_information_for_future_solver': {'blur_family': 'stationary Gaussian',
                                                 'nominal_sigma': 1.2, 'noise_std': 0.01},
        'evaluation_only_true_acquisition': {'blur_sigma': 1.6, 'gaussian_truncate': 4.0,
            'noise_std': 0.01, 'order': ['blur', 'additive Gaussian noise'],
            'omitted_processing_order': ['clip to [0,1]', 'round to uint8', 'JPEG encode/decode'],
            'jpeg_quality': 40, 'jpeg_subsampling': 2, 'paired_noise': True},
        'records': rows,
    }
    (args.output_dir / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'sources': len(rows), 'observations': 2 * len(rows),
                      'reconstruction_run': False, 'output_dir': str(args.output_dir)}))


if __name__ == '__main__':
    main()
