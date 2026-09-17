# Local Notebook 04 validation — 17 September 2026

The predeclared CPU subset completed source **0801 at both acquisition conditions**, at the original 576 × 576 context and 512 × 512 evaluation resolution. These are two observations of one exposed development source, not the four-source design or independent evidence.

## Execution and evidence

All eleven cells executed sequentially in in-process IPython with no saved error outputs. Native Jupyter/Colab, CUDA and Drive mounting were not validated. The [executed local notebook](local_validation_0801_20260917/executed_local_before_colab_bootstrap.ipynb) preserves the exact initial code and outputs. The user-facing notebook is a clean copy with the four-source default. After this CPU run, its setup added the documented CUDA workspace setting and corrected an inherited descriptive information-budget string; every numerical helper and cells 2–11 are identical. The final three setup cells passed locally at the four-source default; numerical inference was not repeated. See [notebook_validation.json](notebook_validation.json).

Before learned inference, all four source identities, all eight historical observation hashes and 16 input/classical anchor rows matched Acquisition 03. Strict weights, deterministic small repeats, odd-size FBCNN padding, automatic-quality wiring, inherited HQS parity, transforms and schedule checks passed. Actual experiment calls were 160 DRUNet + 6 FBCNN; loading checks added 2 + 3 respectively.

Independent readback recomputed **28 quality rows, 56 patch-error vectors, 32 score vectors and 224 risk rows**. Maximum absolute differences: quality 9.66e-17, patch errors 0, scores 0, risks 9.91e-17. It also reconciled summaries, contrasts, source identity, compute and decision scope. No neural inference was repeated in readback. The original check manifest precedes adding the independent audit and final completion status; the exporter separately verifies the final 28 files.

## Reconstruction results — source 0801 only

| Condition | Method | RGB PSNR (dB) | Detail MSE |
|---|---|---:|---:|
| quantized_8bit | Input | 32.572750 | 0.000198315 |
| quantized_8bit | Classical | 33.945141 | 0.000153344 |
| quantized_8bit | DPIR | 34.581665 | 0.000135264 |
| quantized_8bit | FBCNN only | 32.883384 | 0.000158986 |
| quantized_8bit | FBCNN + classical | 34.083924 | 0.000144393 |
| quantized_8bit | FBCNN + DPIR | 34.411760 | 0.000137123 |
| jpeg_q75 | Input | 32.674482 | 0.000166369 |
| jpeg_q75 | Classical | 33.634317 | 0.000155278 |
| jpeg_q75 | DPIR | 32.528116 | 0.000301034 |
| jpeg_q75 | FBCNN only | 32.749052 | 0.000157109 |
| jpeg_q75 | FBCNN + classical | 33.795898 | 0.000147601 |
| jpeg_q75 | FBCNN + DPIR | 34.055678 | 0.000142802 |

On this source's JPEG condition, FBCNN + DPIR versus raw DPIR changes PSNR by **+1.527562 dB** and detail MSE by **-52.563%**. This is a one-source observation, not a four-source conclusion. All six comparisons and the uncompressed-condition results are retained above.

## Selective detail — source 0801, JPEG, FBCNN + DPIR, 50% retention

| Score | Retained detail MSE | Rate >0.025 RMSE | Rate >0.05 | Rate >0.10 |
|---|---:|---:|---:|---:|
| image_gradient | 0.000060707 | 0.000000 | 0.000000 | 0.000000 |
| image_transform_spread_detail | 0.000046465 | 0.000000 | 0.000000 | 0.000000 |
| measurement_residual | 0.000063762 | 0.000000 | 0.000000 | 0.000000 |
| operator_spread_detail | 0.000038102 | 0.000000 | 0.000000 | 0.000000 |
| operator_spread_rgb | 0.000045230 | 0.000000 | 0.000000 | 0.000000 |
| oracle_detail_error | 0.000023025 | 0.000000 | 0.000000 | 0.000000 |
| random_expected | 0.000142802 | 0.052734 | 0.000000 | 0.000000 |

The best included operational control by mean detail error is `image_transform_spread_detail`. Operator detail spread minus that control is **-0.000008363** detail MSE (negative favours operator spread). The reference-error ranking is an oracle evaluation bound, not an operational control. Zero tail rates are uninformative. Full four-source reconstruction and selection screens both remain **not assessed**; their JSON values are null, not passes or failures. Trained image-only uncertainty comparison, calibration, independent testing and novelty remain unestablished.

## Figure inspection

All four PNGs were visually inspected: quality, source-specific changes, risk–coverage and the fixed-inset montage. Labels and legends are readable; the one-source scope is explicit. The JPEG raw-DPIR inset shows stronger block/stripe-like structure than the FBCNN pipelines, while the reference retains finer texture. This qualitative observation does not establish recovery of unsupported detail. The montage shows only source 0801 at the two conditions.

## Exports and scope

The final raw ZIP contains every compared output, observation, patch error, score vector and JPEG stream plus all tables, figures and metadata. It is 127,219,832 bytes, SHA-256 `f166db93cad5b5b3776289532d5449bab557bd13bc7421406e0b56391aa75d54`. Its 2 transfer parts were checked against the whole-archive hash. The summary ZIP explicitly omits raw arrays. Small helper tests also reject missing/corrupt parts and verify repeat packaging without replacement.

Numerical tables, figures, source/checkpoint provenance, status and receipt are copied into [local_validation_0801_20260917](local_validation_0801_20260917). Raw arrays are preserved separately in the exact archive. Results cover one image only; the next action is the frozen four-source Colab run, followed by review of the summary and all raw parts. No protocol, formal screening count or earlier experiment was changed.
