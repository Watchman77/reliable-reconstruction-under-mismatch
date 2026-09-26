#!/usr/bin/env python3
"""Audited, development-only gradient-regularised inverse comparator.

The gradient regularizer and strength 0.01 were selected on three RAISE
development-fit no-JPEG sources and checked on three early-stop sources.
This is exploratory source-level evidence, not a frozen Stage 06 result.
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from run_stage06c_paired_development import (ROOT, STAGE05_NOTEBOOK, acquire,
    check_inputs, load_stage05_components, quality, store_json)
from smoke_stage06c_raise_chains import decode_verified, sha256_file


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-ids', nargs='+', required=True)
    ap.add_argument('--nef-dir', type=Path, required=True)
    ap.add_argument('--audit-csv', type=Path, required=True)
    ap.add_argument('--eligible-manifest', type=Path, default=ROOT /
        'experiments/stage06/manifests/RAISE_1k_eligible_roles_v1_20260925.csv')
    ap.add_argument('--model-cache', type=Path, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    args = ap.parse_args()
    selected, audit_hash = check_inputs(args)  # rejects all independent IDs
    if args.output_dir.exists():
        raise FileExistsError(f'Will not overwrite existing output: {args.output_dir}')
    import torch
    if not torch.cuda.is_available():
        ap.error('GPU required for pinned FBCNN preprocessing')
    from experiments.stage06.acquisition_chains import srgb_to_linear, linear_to_srgb
    device = torch.device('cuda')
    B01, _, J04, _, fbcnn, _, provenance = load_stage05_components(args.model_cache, device)
    receipt = {
        'schema': 'stage06c-gradient-development-v1',
        'status': 'running',
        'claim_scope': 'development only; gradient inverse candidate, no independent evidence',
        'source_ids': [item['source_id'] for item in selected],
        'roles': [item['role'] for item in selected],
        'eligible_manifest_sha256': sha256_file(args.eligible_manifest),
        'audit_sha256': audit_hash,
        'stage05_component_notebook_sha256': sha256_file(STAGE05_NOTEBOOK),
        'fbcnn_checkpoint_sha256': provenance['fbcnn']['weight_sha256'],
        'config': {'regularizer': 'gradient', 'strength': 0.01,
                   'strength_origin': '3 development-fit no-JPEG sources; checked on 3 development early-stop sources',
                   'crop_size': 256, 'true_blur_sigma': 1.6,
                   'nominal_blur_sigma': 1.0, 'noise_std': 2 / 255,
                   'jpeg_quality': 75,
                   'chain_ids': ['srgb_j75_b16_n2', 'linear_j75_b16_n2'],
                   'methods': ['nominal', 'chain_aware'],
                   'seed': 20260925},
        'independent_test_inference': False, 'completed': [], 'failures': []}
    args.output_dir.mkdir(parents=True)
    store_json(args.output_dir / 'status.json', receipt)
    rows = []
    try:
        for item in selected:
            rgb = decode_verified(Path(item['nef']), item['decoded_rgb_sha256'])
            h, w = rgb.shape[:2]
            reference = rgb[(h-256)//2:(h+256)//2, (w-256)//2:(w+256)//2].astype(np.float64) / 255
            seed = 20260925 + int(hashlib.sha256(item['source_id'].encode()).hexdigest()[:8], 16)
            for chain in ('srgb_j75_b16_n2', 'linear_j75_b16_n2'):
                observation = acquire(reference, chain, seed, B01)
                deblocked, _, diag = J04.deblock(observation, fbcnn, device)
                for method in ('nominal', 'chain_aware'):
                    aware = method == 'chain_aware'
                    data = deblocked if aware else observation
                    if aware and chain.startswith('linear_'):
                        data = srgb_to_linear(data)
                    assumed_blur = 1.6 if aware else 1.0
                    estimate = B01.inverse_spectrum(np.fft.fft2(data, axes=(0, 1)),
                        assumed_blur, 'gradient', 0.01)
                    if aware and chain.startswith('linear_'):
                        estimate = linear_to_srgb(estimate)
                    metrics, patch_values = quality(reference, estimate, B01)
                    rows.append({'source_id': item['source_id'], 'role': item['role'],
                        'chain_id': chain, 'solver': 'gradient_inverse_candidate',
                        'method': method, 'assumed_blur': assumed_blur,
                        'observation_sha256': hashlib.sha256(np.ascontiguousarray(observation).tobytes()).hexdigest(),
                        'reconstruction_sha256': hashlib.sha256(np.ascontiguousarray(estimate).tobytes()).hexdigest(),
                        'noise_seed': seed, 'predicted_jpeg_degradation': diag['predicted_degradation'],
                        **metrics, 'patch_detail_mse': patch_values})
                    receipt['completed'].append([item['source_id'], chain, method])
                    store_json(args.output_dir / 'source_method_rows.json', {'rows': rows})
                    store_json(args.output_dir / 'status.json', receipt)
        receipt['status'] = 'completed_development_only'
        receipt['source_method_rows_sha256'] = sha256_file(args.output_dir / 'source_method_rows.json')
        receipt['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
    except Exception as exc:
        receipt['status'] = 'failed_development_run'
        receipt['failures'].append({'type': type(exc).__name__, 'message': str(exc),
                                    'completed_rows': len(rows)})
        store_json(args.output_dir / 'status.json', receipt)
        raise
    store_json(args.output_dir / 'status.json', receipt)
    print(json.dumps({'status': receipt['status'], 'sources': len(selected),
        'rows': len(rows), 'output_dir': str(args.output_dir)}, indent=2))


if __name__ == '__main__':
    main()
