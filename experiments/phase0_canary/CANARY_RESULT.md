# Phase-0 Canary Result

Run date: 15 September 2026  
Scope: one deterministic synthetic image; classical Wiener reconstruction only

## Result table

| Acquisition | Assumed blur | PSNR (dB) | SSIM | Edge MAE | Normalized residual |
|---|---:|---:|---:|---:|---:|
| Blur only | Blur matched | 19.9825 | 0.5403 | 0.2365 | 0.0478 |
| Blur only | Mild mismatch | 18.9111 | 0.4896 | 0.2756 | 0.0434 |
| Blur only | Moderate mismatch | 18.1650 | 0.5685 | 0.2392 | 0.0335 |
| Blur only | Severe/wrong family | 18.0802 | 0.6163 | 0.2528 | 0.0418 |
| Compound | Blur matched | 16.1587 | 0.1749 | 0.5727 | 0.0691 |
| Compound | Mild mismatch | 16.0725 | 0.1638 | 0.5719 | 0.0629 |
| Compound | Moderate mismatch | 16.4703 | 0.1731 | 0.5174 | 0.0445 |
| Compound | Severe/wrong family | 16.6435 | 0.1906 | 0.5182 | 0.0511 |

Spearman correlation between normalized residual and the negative-PSNR error proxy:

- Blur-only chain: -0.80
- Compound chain: 0.60

## What this establishes

1. The implementation records true and assumed operators reproducibly.
2. Blur-only PSNR falls by about 1.90 dB between the blur-matched and wrong-family assumptions.
3. Measurement residual is not a trustworthy standalone proxy for image fidelity in this canary. Under blur-only degradation, the moderate mismatch achieves the lowest residual while producing lower PSNR than the blur-matched reconstruction.
4. Metric rankings conflict: the wrong Gaussian kernel obtains the highest blur-only SSIM while the blur-matched operator obtains the highest PSNR. This is consistent with smoothing receiving favourable structural-similarity scores despite losing or altering detail.
5. Under compound degradation, matching only the blur kernel is not equivalent to matching the full acquisition operator. Unmodelled noise, downsampling and compression dominate the result and can reverse the expected ordering.

## What this does not establish

- It does not support a novelty or superiority claim.
- It does not estimate generalization because only one synthetic source image was used.
- It does not evaluate deep, unrolled or generative reconstruction.
- It does not yet quantify calibrated uncertainty, hallucination or abstention.

## Next experiment

Run the same frozen degradation manifest on a minimum of 100 held-out natural images, then add an operator-oblivious neural baseline and an operator-conditioned physics baseline. Reliability claims should be assessed only after validation-set calibration and external testing on real degradations.

