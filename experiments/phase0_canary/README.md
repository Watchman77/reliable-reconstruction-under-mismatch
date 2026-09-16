# Compound Forward-Model Mismatch: Phase-0 Go/No-Go Pilot

> This file preserves the original canary design and hypotheses. Its executed results remain in `CANARY_RESULT.md`. The current progression gate is defined in [provisional synthesis 01](../../literature/synthesis/provisional_gap_synthesis_01.md) and the [selective-reconstruction pilot specification](../../docs/selective_reconstruction_pilot_spec.md); a missing feature intersection alone is insufficient novelty. The proposed multi-image reliability experiment has not yet run.

## Purpose

This pilot tests whether controlled forward-model mismatch creates a measurable and scientifically useful reliability problem before any large neural model is trained.

The observation model is

\[
y = Q_q\!\left(U_s\!\left(D_s\!\left(H_{k}x+n_{p,g}\right)\right)\right),
\]

where `H_k` is spatial blur, `n_{p,g}` is Poisson-Gaussian noise, `D_s/U_s` is a downsample/upsample cycle, and `Q_q` is JPEG compression. Reconstruction uses an assumed operator `H_k_tilde`, which may differ from the true kernel.

This Phase-0 canary is deliberately small. It validates reproducibility, parameter logging, mismatch severity, metric calculation and output structure. It is not evidence for a journal claim by itself.

## Preregistered questions

1. Does reconstruction quality decline monotonically as the assumed blur kernel diverges from the true kernel?
2. Does measurement residual track image error under compound degradation?
3. Can a reliability score distinguish usable from unsafe reconstructions?
4. Do compression, noise and resolution loss break the relationship between data consistency and true image fidelity?

## Immediate hypotheses

- **H1:** Moderate/severe kernel mismatch will reduce PSNR by at least 2 dB relative to the blur-matched assumption on at least half of the evaluation images. This is tested separately for a blur-only chain and a compound chain.
- **H2:** Measurement residual alone will be an imperfect reliability signal under compound degradation, with rank correlation below 0.8 against reconstruction error or clear counterexamples where low residual accompanies poor image fidelity.
- **H3:** The failure pattern will justify adding operator uncertainty and observation-support assessment rather than relying on image uncertainty alone.

## Stage-A data

- Built-in deterministic synthetic image for a zero-download canary.
- Optional user-supplied PNG/JPEG directory.
- Next data layer after the canary: DIV2K clean images for controlled degradation; RealBlur and REDS for external real-world checks.
- CCTV footage enters only after the controlled experiment is stable because unpaired CCTV does not supply pixel-level ground truth.

## Mismatch ladder

| Level | Assumed blur relative to truth | Purpose |
|---|---|---|
| Blur matched | Correct blur type, length and angle | Blur-physics control; not an oracle for the compound chain |
| Mild | Small length/angle error | Calibration drift |
| Moderate | Larger length/angle error | Practical miscalibration |
| Severe | Wrong kernel family | Structural model error |

The script runs two acquisition conditions. The blur-only condition isolates kernel error. The compound condition also includes noise, downsampling and JPEG compression while the initial reconstruction baseline still models only blur. Therefore, “blur matched” must not be interpreted as a fully specified oracle under the compound condition.

## Baseline ladder after Phase 0

1. Wiener/Tikhonov deconvolution — classical sensitivity control.
2. Restormer or MPRNet — operator-oblivious data-driven baseline.
3. DRUNet plug-and-play or USRNet — operator-conditioned/physics-informed baseline.
4. BlindDPS or an equivalent maintained blind diffusion solver — joint image/operator baseline.
5. Oracle version of the strongest method using the true degradation parameters.

No method enters the benchmark unless its code, weights, licence and inference environment can be reproduced.

## Evaluation plan

### Reconstruction

- PSNR
- SSIM
- LPIPS at the neural-baseline stage
- edge preservation error

### Operator

- kernel L2 error after alignment
- blur-length and angle error
- estimated-versus-true degradation parameters

### Reliability

- normalized measurement residual
- interval coverage and width after uncertainty is introduced
- calibration error
- error-detection AUROC
- risk-coverage curve and area under the risk-coverage curve
- hallucination/measurement-support map

## Go/no-go gate

Proceed to the journal architecture only if all literature and experimental conditions hold:

1. No fully verified competitor jointly solves compound/time-varying mismatch, image-and-operator uncertainty, measurement-supported-detail assessment, OOD evaluation and selective abstention.
2. At least two representative reconstruction families show material deterioration under controlled mismatch.
3. Existing uncertainty or residual scores fail to rank reconstruction risk reliably under at least one compound/OOD condition.
4. A simple combined reliability score or abstention rule shows a meaningful improvement in selective risk without hiding most samples.

Stop or redesign if a reproducible existing method already satisfies the complete claim, mismatch produces negligible failure, or reliable abstention requires unavailable ground truth at deployment.

## Reproducibility rules

- Every degraded image has a JSON record containing source identity, random seed, true operator, assumed operator and codec/noise parameters.
- Dataset partitions are split by source image/video, never by derived degraded sample.
- Thresholds and calibration mappings are selected on validation data only.
- Test-set ground truth is used only for final evaluation.
- Every experiment stores software version, configuration and output metrics.

## Run the canary

```bash
python pilot.py --output-dir outputs/canary
```

Optional image directory:

```bash
python pilot.py --input-dir /path/to/images --output-dir outputs/images
```

Expected outputs:

- `metrics.csv`
- `manifest.json`
- one comparison PNG per source image
- a console summary grouped by mismatch severity
