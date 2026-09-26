#!/usr/bin/env python3
"""Development-only DiffPIR sampler check; never opens RAISE images or test roles.

Run from the 06C Colab kernel after its checkout/checkpoint cells. This checks
the exact pinned model helper against our direct p_sample call at three noise
levels and reports a deterministic synthetic deblurring control.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from run_stage06c_paired_development import (DIFFPIR_COMMIT, diffpir_reconstruct,
                                             ensure_diffpir_source, load_diffpir)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--diffpir-root', required=True, type=Path)
    parser.add_argument('--checkpoint', required=True, type=Path)
    parser.add_argument('--nfe', default=20, type=int)
    args = parser.parse_args()
    import torch
    if not torch.cuda.is_available():
        parser.error('GPU required for the 256px ImageNet checkpoint')
    assert ensure_diffpir_source(args.diffpir_root) == DIFFPIR_COMMIT
    network, diffusion = load_diffpir(args.diffpir_root, args.checkpoint, torch.device('cuda'))
    from utils import utils_model

    beta = torch.linspace(0.0001, 0.02, 1000, device='cuda')
    alpha_bar = torch.cumprod(1 - beta, dim=0)
    reduced = torch.sqrt((1 - alpha_bar) / alpha_bar)
    torch.manual_seed(406)
    x = torch.randn(1, 3, 256, 256, device='cuda')
    checks = {}
    with torch.inference_mode():
        for step in (999, 499, 50):
            # Both paths consume the same x. p_sample pred_xstart has no random
            # contribution, even though p_sample also creates a sampled image.
            helper = utils_model.model_fn(
                x, noise_level=float(reduced[step]) * 255,
                model_out_type='pred_xstart', model_diffusion=network,
                diffusion=diffusion, ddim_sample=False,
                alphas_cumprod=alpha_bar.cpu())
            direct = diffusion.p_sample(network, x,
                torch.full((1,), step, device='cuda', dtype=torch.long),
                clip_denoised=True, denoised_fn=None, cond_fn=None,
                model_kwargs={})['pred_xstart']
            checks[str(step)] = float((helper - direct).abs().max())

    # Synthetic known observation, no JPEG/FBCNN/RAISE. This is a smooth
    # analytic Fourier Gaussian diagnostic, not the Stage 05 kernel.
    class GaussianOperator:
        @staticmethod
        def transfer(shape, sigma):
            fy = np.fft.fftfreq(shape[0])[:, None]
            fx = np.fft.fftfreq(shape[1])[None, :]
            return np.exp(-2 * np.pi**2 * sigma**2 * (fx**2 + fy**2))

    yy, xx = np.mgrid[:256, :256]
    clean = np.stack([(np.sin(xx / 23) + 1) / 2,
                      (np.sin(yy / 29) + 1) / 2,
                      ((xx // 32 + yy // 32) % 2).astype(float)], axis=-1)
    clean = np.clip(clean, 0, 1)
    h = GaussianOperator.transfer(clean.shape[:2], 1.0)
    obs = np.fft.ifft2(np.fft.fft2(clean, axes=(0, 1)) * h[:, :, None], axes=(0, 1)).real
    obs = np.clip(obs, 0, 1)
    restored = diffpir_reconstruct(obs, 1.0, (network, diffusion, GaussianOperator),
                                   seed=406, nfe=args.nfe)
    report = {'stage': '06C_dev_solver_sanity', 'source_commit': DIFFPIR_COMMIT,
              'uses_raise_data': False, 'independent_test_inference': False,
              'max_abs_helper_vs_direct': checks,
              'observation_mse': float(np.mean((obs - clean)**2)),
              'restored_mse': float(np.mean((restored - clean)**2)),
              'restored_range': [float(restored.min()), float(restored.max())]}
    print(json.dumps(report, indent=2))
    if max(checks.values()) > 5e-4:
        sys.exit('MODEL CALL MISMATCH: do not scale Stage 06C')
    # A generative prior need not reduce MSE on this artificial checkerboard;
    # report the outcome for diagnosis without treating it as an accuracy gate.


if __name__ == '__main__':
    main()
