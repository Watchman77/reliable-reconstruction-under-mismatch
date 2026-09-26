#!/usr/bin/env python3
"""Development-only colour-TV deblurring candidate under periodic Gaussian blur.

The second prior is explicit vectorial total variation, unlike DPIR's learned
denoiser. This is a candidate, not a frozen Stage 06 solver or an independent
result. Tune regularisation only on development-fit images.
"""

import argparse
import json

import numpy as np
from scipy.optimize import minimize


def reconstruct(observation, transfer, weight=0.0001, epsilon=0.001,
                maxiter=120):
    """Minimise 0.5*||H*x-y||_2^2 + weight*vectorial_TV_epsilon(x)."""
    y = np.asarray(observation, dtype=np.float64)
    h = np.asarray(transfer, dtype=np.float64)
    if y.ndim != 3 or y.shape[-1] != 3 or h.shape != y.shape[:2]:
        raise ValueError('Expected RGB HxWx3 observation and HxW Fourier transfer')
    if not np.isfinite(y).all() or not np.isfinite(h).all():
        raise ValueError('Observation and transfer must be finite')
    if weight < 0 or epsilon <= 0 or maxiter < 1:
        raise ValueError('Invalid TV settings')

    def objective(flat):
        x = flat.reshape(y.shape)
        hx = np.fft.ifft2(np.fft.fft2(x, axes=(0, 1)) * h[..., None], axes=(0, 1)).real
        residual = hx - y
        fdata = 0.5 * np.sum(residual ** 2)
        gdata = np.fft.ifft2(np.fft.fft2(residual, axes=(0, 1)) * h[..., None], axes=(0, 1)).real
        dx = np.roll(x, -1, axis=0) - x
        dy = np.roll(x, -1, axis=1) - x
        norm = np.sqrt(epsilon ** 2 + np.sum(dx ** 2 + dy ** 2, axis=2, keepdims=True))
        p, q = dx / norm, dy / norm
        gtv = np.roll(p, 1, axis=0) - p + np.roll(q, 1, axis=1) - q
        return fdata + weight * np.sum(norm), (gdata + weight * gtv).ravel()

    result = minimize(objective, np.clip(y, 0, 1).ravel(), jac=True,
        method='L-BFGS-B', bounds=[(0.0, 1.0)] * y.size,
        options={'maxiter': maxiter, 'ftol': 1e-10})
    estimate = result.x.reshape(y.shape)
    if not np.isfinite(estimate).all():
        raise ValueError('TV candidate returned non-finite reconstruction')
    return estimate, {'iterations': int(result.nit), 'success': bool(result.success),
                      'optimizer_message': str(result.message), 'objective': float(result.fun)}


def self_test():
    rng = np.random.default_rng(1337)
    truth = rng.uniform(0.15, 0.85, (16, 16, 3))
    fy, fx = np.fft.fftfreq(16)[:, None], np.fft.fftfreq(16)[None, :]
    h = np.exp(-2 * np.pi**2 * (fx**2 + fy**2))
    y = np.fft.ifft2(np.fft.fft2(truth, axes=(0, 1)) * h[..., None], axes=(0, 1)).real
    x, info = reconstruct(y, h, weight=1e-6, maxiter=200)
    e = rng.uniform(0, 1, y.shape)
    def obj(z):
        r = np.fft.ifft2(np.fft.fft2(z, axes=(0, 1)) * h[..., None], axes=(0, 1)).real - y
        dx = np.roll(z, -1, axis=0) - z
        dy = np.roll(z, -1, axis=1) - z
        return 0.5 * np.sum(r*r) + 1e-4 * np.sqrt(1e-6 + np.sum(dx*dx+dy*dy, axis=2)).sum()
    # Central-difference check of the analytic gradient on a non-boundary point.
    z = e.ravel().copy()
    test_i, delta = 91, 1e-6
    def check_fun(v):
        return obj(v.reshape(y.shape))
    numeric = (check_fun(z + np.eye(1, z.size, test_i).ravel()*delta) -
               check_fun(z - np.eye(1, z.size, test_i).ravel()*delta))/(2*delta)
    # Evaluate objective with the same regularisation as the finite-difference check.
    def probe(v):
        x = v.reshape(y.shape)
        r = np.fft.ifft2(np.fft.fft2(x, axes=(0, 1))*h[..., None], axes=(0, 1)).real-y
        dx,dy=np.roll(x,-1,axis=0)-x,np.roll(x,-1,axis=1)-x
        norm=np.sqrt(1e-6+np.sum(dx*dx+dy*dy,axis=2,keepdims=True))
        p,q=dx/norm,dy/norm
        grad=np.fft.ifft2(np.fft.fft2(r,axes=(0,1))*h[...,None],axes=(0,1)).real
        grad+=1e-4*(np.roll(p,1,axis=0)-p+np.roll(q,1,axis=1)-q)
        return grad.ravel()[test_i]
    error = abs(numeric-probe(z))
    if error > 1e-6:
        raise AssertionError(f'TV analytic gradient mismatch: {error}')
    if np.mean((x-truth)**2) >= np.mean((y-truth)**2):
        raise AssertionError('Synthetic TV deblurring did not improve MSE')
    print(json.dumps({'status':'candidate_self_test_passed','gradient_error':error,
        'observation_mse':float(np.mean((y-truth)**2)),
        'tv_mse':float(np.mean((x-truth)**2)), 'optimizer':info},indent=2))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--self-test', action='store_true')
    args = ap.parse_args()
    if not args.self_test:
        ap.error('Run --self-test first; real images must be audited development sources')
    self_test()
