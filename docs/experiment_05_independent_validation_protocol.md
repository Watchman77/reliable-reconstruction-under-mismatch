# Experiment 05 independent-validation protocol

Frozen 21 September 2026, before downloading the independent images or running any test inference.

## Decision

Experiment 05 will use the 40 natural reference images in the exact TESTIMAGES/SAMPLING archive `SAMPLING_8BIT_RGB_2400x2400.tar.bz2` as a sealed primary cohort. The protocol and documented exposure audit are frozen. The independent run is **not yet authorized**: the archive receipt, source hashes, duplicate audit, trained comparator, calibration mappings and development-only canary still have to pass.

This is an intermediate independent confirmation. Forty sources do not satisfy the repository's separate final gate of at least 100 held-out natural images. Even a positive result cannot establish novelty or prove absence from checkpoint training, because the released FBCNN and DRUNet checkpoints have no image-level training manifests.

The machine-readable authority is [`experiments/independent_05/protocol_freeze.json`](../experiments/independent_05/protocol_freeze.json). This document explains it; it does not override it.

## Why this cohort

The reviewed official FBCNN configuration names DIV2K and Flickr2K for training. Its test scripts name LIVE1, BSDS500, Classic5 and ICB. The DRUNet paper reports training on BSD400, Waterloo Exploration, DIV2K and Flickr2K, and reports benchmarks including BSD/CBSD, Set12, Kodak, McMaster, Classic5 and LIVE1.

Those families are therefore excluded from the strict primary cohort. TESTIMAGES/SAMPLING was not named in any reviewed pinned source. The exact selected archive is the 8-bit RGB 2400 × 2400 derivative listed by the publisher: 40 PNG images, one per source. The defensible conclusion is **no documented exposure found**, not **proven unseen**.

The full evidence table is [`experiments/independent_05/dataset_exposure_audit.csv`](../experiments/independent_05/dataset_exposure_audit.csv).

## Sealed-data rules

- Use all and only decoded 8-bit RGB 2400 × 2400 PNG members from the named archive; abort unless there are exactly 40 before duplicate adjudication.
- Record archive bytes and SHA-256 before extraction, then record path, bytes, SHA-256, dimensions and mode for every member.
- Compare the cohort with the 96 development images using exact SHA-256, pHash and dHash before corruptions or inference. Exact duplicates are excluded. Pairs with both perceptual-hash Hamming distances at most four are adjudicated before outcomes exist.
- Never replace an excluded or failed source. Continue only if at least 36 sources remain; otherwise abort.
- Take one fixed 576 × 576 centre crop per source and evaluate its central 512 × 512 region. A source image, not a patch or corruption, is the independent unit.

## Frozen acquisition ladder

All chains reuse the same source-specific standard-normal noise field, scaled by the named noise level. The operational model continues to assume blur sigma 1.0 and noise 2/255. Pillow JPEG uses 4:4:4 (`subsampling=0`) and `optimize=False`.

| ID | True blur | Noise | Codec | Role |
|---|---:|---:|---|---|
| `q8_b16_n2` | 1.6 | 2/255 | 8-bit quantization, no JPEG | negative control |
| `j90_b16_n2` | 1.6 | 2/255 | JPEG Q90 | codec strength |
| `j75_b16_n2` | 1.6 | 2/255 | JPEG Q75 | primary anchor |
| `j50_b16_n2` | 1.6 | 2/255 | JPEG Q50 | codec strength |
| `j75_b12_n2` | 1.2 | 2/255 | JPEG Q75 | blur strength |
| `j75_b20_n2` | 2.0 | 2/255 | JPEG Q75 | blur strength |
| `j75_b16_n5` | 1.6 | 5/255 | JPEG Q75 | noise strength |

The six frozen reconstruction outputs are the observation, nominal classical gradient inverse, nominal DPIR, FBCNN alone, FBCNN plus the classical inverse, and FBCNN plus nominal DPIR. Experiment 04's model weights, hashes, eight-iteration DPIR schedule, prior trade-off, classical regularization, automatic FBCNN quality inference and clipping rule remain unchanged.

## Primary hypotheses

Both hypotheses use the Q75 anchor and source-level paired inference.

1. **H1 reconstruction:** FBCNN+DPIR reduces mean detail MSE relative to raw DPIR. Passing requires at least a 5% relative reduction, a two-sided 95% paired source-bootstrap interval wholly below zero, and a Holm-adjusted one-sided paired sign-flip p-value below 0.05.
2. **H2 selection:** at 50% patch coverage on FBCNN+DPIR, detail operator spread reduces retained-patch detail MSE relative to whole-pipeline transformation spread. The same 5%, bootstrap and Holm-adjusted sign-flip gates apply.

There are 10,000 paired source bootstraps and 100,000 paired sign-flip draws, both with seed `20260921`. Patches are never treated as independent replicates. Secondary codec, blur, noise, PSNR, coverage and calibration outcomes cannot rescue a failed primary gate.

The 5% practical margins were chosen after the four-source development result was known but before any independent outcome. They are therefore development-informed and explicitly not independent discoveries.

## Stronger image-only comparator

The required trained control is a five-member PatchErrorNet ensemble. Each member is a ResNet-18 trained from scratch with six input channels: a 64 × 64 context from the supplied observation and the FBCNN+DPIR reconstruction. It predicts whether the centre 16 × 16 patch has detail RMSE above 0.05. It receives no operator variants, source identity, clean image, true corruption parameters or codec metadata.

Source partitions are fixed:

- fit: DIV2K `0805`–`0856`;
- early stopping: `0857`–`0868`;
- calibration: `0869`–`0900`;
- independent test: all eligible TESTIMAGES/SAMPLING sources;
- engineering canary: development sources `0805` and `0806` only.

The fit, early-stop and calibration images are deliberately labelled development data with documented component-training-family exposure. Their role is to train and calibrate a comparator without touching the independent cohort.

## Calibration

Every operational score is oriented so larger means greater risk and receives its own isotonic mapping fitted only on DIV2K `0869`–`0900`, with equal total weight per source. The frozen binary event is detail RMSE above 0.05.

On the independent cohort, report source-macro Brier score, ten-bin equal-mass expected calibration error, calibration-in-the-large, calibration slope and reliability diagrams with source-bootstrap intervals. “Calibrated” is limited to this event and acquisition family; it is not a posterior-probability claim.

## Execution barriers

1. **05A–05B, now complete:** protocol freeze and documented exposure audit only. No independent outcomes exist.
2. **05C, next:** acquire and hash the archive; finish duplicate checks; implement the locked runner, comparator and calibration artifacts; run schema, determinism, resume and readback checks on DIV2K `0805`–`0806` only.
3. **05D:** after every readiness assertion passes, run all independent sources without interim aggregate inspection or tuning.
4. **05E–05F:** unseal once, apply the frozen calibration/statistics and report the decision, including failures and exclusions.

A crash may be resumed from source-level checkpoints, but performance cannot guide reruns, exclusions or setting changes. Any outcome-blind engineering correction requires a versioned amendment identifying the bug and whether independent output already existed.

## Sources

- [FBCNN training configuration](https://github.com/jiaxi-jiang/FBCNN/blob/54d1831927506b3247e2d4d245abb4f4dab1a1cd/options/train_fbcnn_color.json)
- [FBCNN colour test script](https://github.com/jiaxi-jiang/FBCNN/blob/54d1831927506b3247e2d4d245abb4f4dab1a1cd/main_test_fbcnn_color.py)
- [FBCNN paper](https://arxiv.org/abs/2109.14573)
- [DPIR/DRUNet paper](https://arxiv.org/abs/2008.13751)
- [Pinned DPIR repository](https://github.com/cszn/DPIR/tree/15bca3fcc1f3cc51a1f99ccf027691e278c19354)
- [TESTIMAGES/SAMPLING documentation](https://testimages.org/sampling/)
- [Selected 8-bit RGB archive listing](https://sourceforge.net/projects/testimages/files/SAMPLING/8BIT/RGB/)
- [Asuni and Giachetti, TESTIMAGES](https://doi.org/10.1080/2165347X.2015.1024298)
