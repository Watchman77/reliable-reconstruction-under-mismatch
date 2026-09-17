# Acquisition 03: paired acquisition-stage diagnosis

Frozen on 17 September 2026 before new stage-reconstruction outcomes are examined. This is a follow-up to the mixed Learned 02 result, not an independently conceived or registered experiment. The notebook records this file's SHA-256 and its source-code digests before inference.

## Question and scope

Which added acquisition stage changes reconstruction quality under the existing fixed methods? Use four previously exposed DIV2K sources, 0801–0804, the same 576 × 576 native centre crops (512 × 512 evaluation region), analytic periodic blur sigma 1.6, source-keyed noise with seed 20260917 and standard deviation 2/255. For each source, generate the noisy linear observation once and derive four ordered stages:

1. `linear_float`: original unbounded floating blur plus noise.
2. `clipped_float`: clip the same observation to [0, 1], retaining floating precision.
3. `quantized_8bit`: NumPy round-to-nearest-even after multiplying the clipped observation by 255, then divide uint8 values by 255.
4. `jpeg_q75`: encode that exact uint8 image as JPEG at quality 75, subsampling 0 and optimize=False, then decode to floating RGB.

This gives 16 paired source-stage observations. The first and fourth reproduce Learned 02's linear/JPEG simulator endpoints in the current environment. Adjacent contrasts are conditional effects of adding a stage in this order. The codec contrast includes its RGB/YCbCr conversions and encode/decode processing; it does not isolate DCT quantization alone. Four stages are not four independent source replicates. The same noise realization is retained throughout.

## Fixed comparisons

Retain all five Learned 02 quality comparators: observed input, nominal gradient inverse (lambda 0.05), one-call denoising-only DRUNet, nominal DPIR-style and true-blur DPIR-style. Use the exact verified Learned 02 adapter, weights, eight iterations, 49-to-2 schedule, trade-off 0.23 and geometric transforms. Operational methods receive nominal blur 1.0 and noise 2/255; true blur 1.6 remains a labelled diagnostic. No method receives codec parameters or reference errors for tuning. No learned uncertainty ensemble or selective retention is recomputed in this diagnostic.

The observed-image quality control is clipped to [0, 1] at every stage, preserving Learned 02. Thus its linear/clipped scores are identical by construction; reconstruction methods still receive the unbounded linear observation at stage 1. No algorithm setting, iteration count, resolution, regularization strength or codec quality is selected using the new outcomes.

## Readouts

Primary: per-source and pooled high-pass detail MSE of nominal DPIR and the classical comparator, using D(x)=x-G_1*x before context removal. Report their detail-MSE gap at each stage and its adjacent-stage change. Positive gap means nominal DPIR is worse; positive gap change means the added stage worsens its relative position. Also report each method's adjacent-stage detail-MSE change.

Secondary: RGB MSE/PSNR for all five models, full-coverage patch detail-RMSE exceedance rates at the unchanged tolerances 0.025, 0.05 and 0.10, and model iteration residuals. PSNR pooling uses -10 log10(mean MSE). Do not describe these full-coverage rates as calibrated risk or hallucination detection.

Record the magnitude of each measurement change, clipping fractions, observation hashes, JPEG bytes/digest, model costs and environment/codec versions. Show paired per-source gaps alongside pooled summaries. Adjacent changes telescope to the endpoint difference, but squared measurement-perturbation energies need not add because of cross-terms.

## Validation and saving

Before inference: validate four source identities/crops, unchanged adapter/vendor/weight hashes, inherited dense HQS/schedule/transform/smoke checks, equality of both simulator endpoints, clipping bounds/idempotence, quantization half-step bounds, and JPEG round-trip. Compare input/classical endpoint errors against the verified Learned 02 CSV (absolute MSE tolerance 1e-12). If that anchor fails, stop and investigate rather than silently treating a changed endpoint as equivalent.

After inference: save every compared reconstruction, raw supplied observations and patch errors; recompute all model errors from saved arrays; check row counts, paired contrasts, endpoint telescoping and finite values. Record learned endpoint differences from the Colab CSV without demanding bitwise CPU/GPU agreement or changing the algorithm to fit the anchor. No learned drift tolerance is used to promote a robustness finding. Save failure/running/completed status explicitly and regenerate the manifest only after each complete snapshot, including failure handling.

Write into a new dated results folder and create one verified ZIP beside it for upload. Source images and model weights remain unchanged. Full default run: 16 observations, 80 quality rows and 272 experiment denoiser calls, plus two small adapter-validation calls.

Local validation is predeclared as source 0801 through all four stages (4 observations, 20 quality rows, 68 experiment denoiser calls plus two small checks), at full resolution. The workspace has CPU only. Native notebook execution will be attempted; any execution gap must be explicit. Colab defaults stay at all four sources. A one-source local result cannot be presented as the 16-observation result.

## Decision boundary

Record gains, losses and null changes. Identify where the fixed reconstruction gap changes, without claiming a unique internal solver/prior failure mechanism. A later, separately frozen experiment may test acquisition-aware reconstruction based on this diagnosis. Do not invent a new architecture, retune to these outputs, claim novelty/calibration/held-out performance, or amend the scoping-review protocol. The four sources and unresolved pretrained DIV2K overlap remain development limitations.

Implementation references: existing `experiments/learned_02/learned.py` and `experiments/baseline_01/baseline.py`; [Pillow JPEG options](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg).
