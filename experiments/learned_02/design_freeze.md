# Learned baseline 02: bounded development design

Frozen before learned reconstruction outcomes are examined, 17 September 2026.

Use the official colour DRUNet checkpoint in a DPIR-style half-quadratic-splitting adapter. The source snapshot is `cszn/DPIR@15bca3fcc1f3cc51a1f99ccf027691e278c19354`. The official downloader identifies `https://github.com/cszn/KAIR/releases/download/v1.0/drunet_color.pth`. Its downloaded size is 130,579,305 bytes and our observed SHA-256 is `479abe3c5327dfd10ff54a80ec7d4098ca80752a5c9492cdff31cee430bec4b4`. This is an observed digest, not a publisher-signed checksum.

## Scope and information

- Four previously used DIV2K development sources, 0801–0804. Preserve their 576 × 576 native centre crops, 512 × 512 evaluation regions, stored RGB, periodic Gaussian forward model, noise seeds and JPEG chain from Baseline 01.
- One true blur width, 1.6 px, one noise standard deviation, 2/255, and both linear and JPEG-chain conditions: **eight observations**. This is the original anchor subset of the 48-condition classical experiment, not its entire severity grid.
- Nominal blur is 1.0 px and nominal noise is fixed at 2/255 for every method. Only the separate oracle-blur diagnostic receives true blur. Codec information and clean references are not supplied to operational reconstructions or scores.
- The DPIR paper reports denoiser training on 900 DIV2K images. Exact checkpoint/source lineage is not recovered. These images cannot substantiate unseen-image performance for these weights; they remain development-only.

## Fixed reconstruction and score choices

- Keep the observed input and the nominal gradient-regularised inverse with lambda 0.05, inherited from Baseline 01 without further tuning.
- DPIR adapter: eight iterations, the official log-spaced 49-to-2 denoiser noise schedule, trade-off 0.23, and the official eight periodical geometric transforms. Initialise from the supplied observation. Use a native complex FFT data update with the same analytic Gaussian transfer as our simulator.
- Run the denoiser on the full tensor, without the demo's recursive quadrant tiling, and evaluate clipped floating output rather than its rounded uint8 export. The supplied acquisition and these declared adaptations mean this is not a reproduction of the paper's benchmark scores.
- A one-call DRUNet denoising-only control is operator-oblivious; it is not a strong trained deblurring comparator. NAFNet or an equivalent dedicated restoration baseline remains a later requirement.
- Operator ensemble: assumed blur widths 0.8, 1.0 and 1.2 px. Fixed-operator image-transformation ensemble: original input plus rotations of 90 and 180 degrees, invert the rotations after reconstruction. Each score uses three complete eight-iteration reconstructions with the same image prior, noise assumption and iteration budget. The nominal reconstruction is shared; each ensemble adds sixteen denoiser calls.
- Compare detail-domain operator spread with detail-domain image-transformation spread, measurement residual, reconstructed-image gradient and RGB-domain operator spread. These are heuristic sensitivities, not posterior samples or calibrated uncertainty.

## Evaluation and cost

- Retain RGB MSE/PSNR for reconstruction quality. Add patch high-pass detail error using `D(x)=x-G_1*x`; take this transform before removing the 32 px context margin. Patch size is 16 × 16.
- Report RGB and detail MSE plus bad-detail rate at patch detail-RMSE tolerances 0.025, 0.05 and 0.10, at fixed coverages 50%, 75%, 90% and 100%. No risk threshold is calibrated in this development run.
- Report all patches and the top reference-gradient texture quartile separately. Reference-based strata and oracle-error rankings are evaluation-only.
- Save per-reconstruction elapsed times, device, tensor size, denoiser calls, iteration trajectories and peak memory where available. Equal denoiser-call budgets do not imply equal wall-clock cost. No superiority claim over a learned family or sampler not run here.
- Validate strict checkpoint loading, official source digests, the noise schedule, FFT data updates against independent NumPy/dense solutions, transform inverses, source identity, finite outputs, risk endpoints and output-file hashes.
- Measure one full-size forward pass before the complete run. If available CPU execution is prohibitively slow, deliver the fully executable notebook and explicitly label the actually executed source/condition subset; never silently resize images, reduce iterations or claim the full experiment ran.

## Decision

Record negative and conflicting findings. Do not change these settings after seeing results to manufacture a gain. This is a learned-baseline engineering checkpoint. Independent calibration/testing, trained image-only uncertainty, blind sampling, matched-wall-time comparisons and definitive closest-method novelty checks remain outstanding.

Sources: [official DPIR code](https://github.com/cszn/DPIR/tree/15bca3fcc1f3cc51a1f99ccf027691e278c19354), [paper, inspected v2](https://arxiv.org/html/2008.13751v2), [prior baseline report](../baseline_01/README.md), [broader pilot design](../../docs/selective_reconstruction_pilot_spec.md).
