#!/usr/bin/env python3
"""Extract reference-safe Stage 06D features on audited development sources.

This is an engineering canary, not calibration or an independent evaluation.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

from run_stage06c_paired_development import (
    ROOT, STAGE05_NOTEBOOK, acquire, load_stage05_components,
    quality, store_json,
)
from smoke_stage06c_raise_chains import (
    AUDIT_SHA256, ELIGIBLE_SHA256, decode_verified, load_unique_rows,
    sha256_file,
)

PERMITTED_ROLES = {'development_fit', 'development_early_stop',
                   'development_calibration', 'external_pilot'}


def authorize_stage06d(args):
    """Validate pinned 06B identities without importing 06C's narrower role set."""
    if sha256_file(args.eligible_manifest) != ELIGIBLE_SHA256:
        raise ValueError('Eligibility manifest differs from reviewed 06B v1')
    if sha256_file(args.audit_csv) != AUDIT_SHA256:
        raise ValueError('RAW audit differs from reviewed 06B v1')
    eligible = load_unique_rows(args.eligible_manifest)
    audited = load_unique_rows(args.audit_csv)
    if len(eligible) != 994 or not args.source_ids or len(set(args.source_ids)) != len(args.source_ids):
        raise ValueError('Expected distinct source IDs against 994-source allowlist')
    selected = []
    for source_id in args.source_ids:
        row = eligible.get(source_id)
        if row is None or row['role'] not in PERMITTED_ROLES:
            raise ValueError(f'Sealed, excluded or unknown source: {source_id}')
        checked = audited.get(source_id)
        path = args.nef_dir / f'{source_id}.NEF'
        if (checked is None or row['relative_path'] != path.name or
                checked['relative_path'] != path.name or
                checked['role'] != row['role']):
            raise ValueError(f'Audited source identity/role mismatch: {source_id}')
        if not path.is_file() or path.stat().st_size != int(checked['byte_count']):
            raise ValueError(f'Missing or truncated audited RAW: {source_id}')
        if sha256_file(path) != checked['file_sha256']:
            raise ValueError(f'RAW hash changed: {source_id}')
        selected.append({'source_id': source_id, 'role': row['role'],
                         'nef': str(path), 'decoded_rgb_sha256': checked['decoded_rgb_sha256']})
    return sorted(selected, key=lambda r: r['source_id']), AUDIT_SHA256


def patch_means(image, margin=32, patch=16):
    """Non-overlapping 16px patches in the 192px evaluation interior."""
    view = np.asarray(image)[margin:-margin, margin:-margin]
    if view.shape[:2] != (192, 192):
        raise ValueError(f"Unexpected patch interior {view.shape}")
    if view.ndim == 3:
        view = view.mean(axis=2)
    return view.reshape(12, patch, 12, patch).mean(axis=(1, 3)).ravel()


def patch_squared(a, b, B01, detail=False):
    if detail:
        a = a - B01.apply(a, 1.0)
        b = b - B01.apply(b, 1.0)
    return patch_means((a - b) ** 2)


def features(reference, observation, deblocked, dpir, gradient, other_dpir,
             chain, B01):
    """Only the target reads reference. Predictor inputs read observations/outputs."""
    from experiments.stage06.acquisition_chains import srgb_to_linear

    target = np.sqrt(patch_squared(reference, dpir, B01, detail=True))
    assert np.allclose(target ** 2, quality(reference, dpir, B01)[1], rtol=1e-9)
    if chain.startswith("linear_"):
        data = srgb_to_linear(deblocked)
        estimate = srgb_to_linear(np.clip(dpir, 0, 1))
    else:
        data, estimate = deblocked, dpir
    forward = B01.apply(estimate, 1.6)
    out = {
        "observed_detail_rmse": target,
        "forward_consistency_residual": np.sqrt(patch_squared(data, forward, B01)),
        "solver_uncertainty": np.sqrt(patch_squared(dpir, gradient, B01)),
        "cross_chain_disagreement": np.sqrt(patch_squared(dpir, other_dpir, B01, detail=True)),
        "image_texture": np.sqrt(patch_means((observation - B01.apply(observation, 1.0)) ** 2)),
        "image_contrast": np.sqrt(patch_means((observation - observation.mean(axis=(0, 1))) ** 2)),
    }
    if any(x.shape != (144,) or not np.isfinite(x).all() for x in out.values()):
        raise ValueError("Malformed reliability features")
    return out


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
    selected, audit_hash = authorize_stage06d(args)  # four development/pilot roles only
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    import torch
    from experiments.stage06.acquisition_chains import linear_to_srgb, srgb_to_linear
    if not torch.cuda.is_available():
        ap.error('CUDA required for pinned DPIR and FBCNN')
    B01, L02, J04, dpir_model, fbcnn, settings, provenance = load_stage05_components(
        args.model_cache, torch.device('cuda'))
    receipt = {
        'schema': 'stage06d-feature-canary-v1', 'status': 'running',
        'claim_scope': 'development feature extraction; no independent inference',
        'independent_test_inference': False,
        'source_ids': [x['source_id'] for x in selected],
        'roles': [x['role'] for x in selected],
        'audit_sha256': audit_hash,
        'eligible_manifest_sha256': sha256_file(args.eligible_manifest),
        'stage05_component_notebook_sha256': sha256_file(STAGE05_NOTEBOOK),
        'checkpoint_sha256': {k: provenance[k]['weight_sha256'] for k in ('dpir', 'fbcnn')},
        'configuration': {'gradient_strength': .01, 'gradient_regularizer': 'gradient',
            'dpir_blur_sigma': 1.0, 'gradient_blur_sigma': 1.6,
            'blur_sigma_true': 1.6, 'noise_std': 2/255, 'jpeg_quality': 75,
            'margin': 32, 'patch_size': 16, 'patches_per_source_chain': 144,
            'thresholds_rmse': [.01, .02, .03, .05, .075],
            'forward_residual_note': 'pre-JPEG blur residual against FBCNN deblocked observation'},
        'completed_source_ids': [], 'failures': []}
    args.output_dir.mkdir(parents=True)
    store_json(args.output_dir / 'status.json', receipt)
    import csv
    table_path = args.output_dir / 'features.csv'
    keys = ['source_id', 'role', 'chain_id', 'patch_id', 'observed_detail_rmse',
            'forward_consistency_residual', 'solver_uncertainty',
            'cross_chain_disagreement', 'image_texture', 'image_contrast']
    try:
        with table_path.open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=keys)
            writer.writeheader()
            for item in selected:
                rgb = decode_verified(Path(item['nef']), item['decoded_rgb_sha256'])
                h, w = rgb.shape[:2]
                reference = rgb[(h-256)//2:(h+256)//2, (w-256)//2:(w+256)//2].astype(np.float64) / 255
                seed = 20260925 + int(hashlib.sha256(item['source_id'].encode()).hexdigest()[:8], 16)
                recon = {}
                for chain in ('srgb_j75_b16_n2', 'linear_j75_b16_n2'):
                    obs = acquire(reference, chain, seed, B01)
                    deblocked, _, _ = J04.deblock(obs, fbcnn, torch.device('cuda'))
                    data = srgb_to_linear(deblocked) if chain.startswith('linear_') else deblocked
                    dpir, _, _ = L02.reconstruct(data, 1.0, dpir_model, torch.device('cuda'), settings)
                    grad = B01.inverse_spectrum(np.fft.fft2(data, axes=(0, 1)),
                                                 1.6, 'gradient', .01)
                    if chain.startswith('linear_'):
                        dpir, grad = linear_to_srgb(dpir), linear_to_srgb(grad)
                    recon[chain] = (obs, deblocked, dpir, grad)
                for chain, (obs, deblocked, dpir, grad) in recon.items():
                    other = next(x for x in recon if x != chain)
                    computed = features(reference, obs, deblocked, dpir, grad,
                                        recon[other][2], chain, B01)
                    for j in range(144):
                        writer.writerow({'source_id': item['source_id'],
                            'role': item['role'], 'chain_id': chain, 'patch_id': j,
                            **{k: float(v[j]) for k, v in computed.items()}})
                stream.flush()
                receipt['completed_source_ids'].append(item['source_id'])
                store_json(args.output_dir / 'status.json', receipt)
        import pandas as pd
        df = pd.read_csv(table_path)
        if len(df) != len(selected) * 288 or df[keys[4:]].isna().any().any():
            raise ValueError('Incomplete feature table')
        support = []
        for (role, chain), subset in df.groupby(['role', 'chain_id']):
            for threshold in receipt['configuration']['thresholds_rmse']:
                positives = subset.observed_detail_rmse > threshold
                support.append({'role': role, 'chain_id': chain, 'threshold': threshold,
                    'sources': int(subset.source_id.nunique()), 'patches': len(subset),
                    'positive_patches': int(positives.sum()),
                    'positive_sources': int(subset.loc[positives, 'source_id'].nunique())})
        pd.DataFrame(support).to_csv(args.output_dir / 'event_support.csv', index=False)
        receipt['features_sha256'] = sha256_file(table_path)
        receipt['event_support_sha256'] = sha256_file(args.output_dir / 'event_support.csv')
        receipt['status'] = 'completed_development_only'
    except Exception as exc:
        receipt['status'] = 'failed_development_run'
        receipt['failures'].append({'type': type(exc).__name__, 'message': str(exc)})
        raise
    finally:
        store_json(args.output_dir / 'status.json', receipt)
    print(json.dumps({'status': receipt['status'], 'sources': len(selected),
                      'patch_rows': len(df), 'output_dir': str(args.output_dir)}, indent=2))


if __name__ == '__main__':
    main()
