# Acquisition 03: local execution review

17 September 2026. **Source 0801 completed all four acquisition stages at full resolution.** This is 4/16 observations in the default four-source design, not a full Colab result. The one-source validation was declared in the design before the new stage outputs were examined.

## What executed

The unchanged Learned 02 adapter ran all five quality comparators on linear float, clipped float, 8-bit rounded and JPEG Q75 observations. The run produced 20 quality rows, 16 reconstruction cost rows, 64 iteration records, 15 adjacent-stage comparison rows and four source-stage gaps. It used 68 experiment denoiser calls plus two small learned checks. Recorded reconstruction times sum to 429.237 seconds on CPU; loading, metrics, plotting and saving are additional.

The native Jupyter kernel failed before the first cell with a ZeroMQ interface-resolution permission error. The [attempt record](native_kernel_attempt.json) is preserved. All ten cells then executed sequentially through the existing in-process IPython runner. That environment initially rendered Figure objects as text rather than embedded images. Presentation cells 5–10 were subsequently replayed from the saved CSV/PNG/ZIP exports using explicit PNG displays; cells 1–4, their computational source and saved outputs were preserved. No learned inference was repeated. Notebook metadata records the display repair and execution boundary. Colab, GPU execution and Drive mounting for Notebook 03 remain unverified.

## Observed quality

RGB PSNR in dB; for this single source, pooled and per-source PSNR coincide:

| Stage | Input | Classical gradient | Denoising only | Nominal DPIR | True-blur DPIR |
|---|---:|---:|---:|---:|---:|
| linear_float | 32.582669 | 33.953588 | 32.939911 | 34.580960 | 37.836579 |
| clipped_float | 32.582669 | 33.953627 | 32.939908 | 34.580964 | 37.836626 |
| quantized_8bit | 32.572750 | 33.945141 | 32.939740 | 34.581665 | 37.825610 |
| jpeg_q75 | 32.674482 | 33.634317 | 32.777848 | 32.528116 | 32.889027 |

Nominal DPIR changes by +0.000705 dB between the linear and 8-bit stages, and by -2.053549 dB when JPEG encoding/decoding is then added. Read those as conditional effects in this one source and stage order. The earlier endpoint mismatch has not been explained away by changing reconstruction settings.

| Stage | Nominal detail MSE | Classical detail MSE | Nominal − classical gap |
|---|---:|---:|---:|
| linear_float | 0.000135288 | 0.000153043 | -0.000017755 |
| clipped_float | 0.000135288 | 0.000153041 | -0.000017753 |
| quantized_8bit | 0.000135264 | 0.000153344 | -0.000018081 |
| jpeg_q75 | 0.000301034 | 0.000155278 | +0.000145756 |

The measured stage contrasts identify where the fixed reconstruction behavior changes in this case. They do not isolate an internal prior/solver mechanism or individual codec operation. All five comparators and the full-coverage patch error tails remain in the [saved tables](local_validation_0801_20260917/). The separate denoising-only control is not a strong trained deblurring comparator.

## Verification evidence

- All four official source identities and both simulator endpoints were checked before inference. Sixteen input/classical endpoint rows agree with the verified Learned 02 Colab CSV to below 1e-12 absolute MSE.
- Strict weight loading, pinned vendor hashes, the inherited schedule/transforms, dense HQS comparison and repeated learned smoke tests passed.
- Every supplied observation and every compared reconstruction is stored. A separate [readback audit](validation.json) checks all 20 quality rows and patch arrays using independently implemented Fourier detail filtering and pooling, verifies all four source PNG/RGB hashes, clipping/rounding/codec readback, summary/contrast arithmetic and the archive.
- 23 result files match their recorded sizes and SHA-256 hashes. The ZIP also passes CRC and entry-hash checks. Its identity is preserved in [the ZIP receipt](local_validation_0801_20260917/zip_receipt.json); the full raw local archive is preserved separately as `acquisition_03_local_0801.zip`.
- Maximum absolute independent quality-metric discrepancy is 7.11e-15; maximum patch-error discrepancy is 0. Learned endpoint PSNR differs from the earlier GPU CSV by at most 1.02e-05 dB. The complete endpoint-drift table is retained; cross-platform equality is not asserted.
- All four final PNG figures were inspected, and the delivered notebook contains four embedded PNGs, ten numbered code cells and no saved errors after presentation replay. The fixed image inset uses source 0801's centre; it was not selected by outcome.

The Git review folder contains the small tables, metadata and figures. The full prediction arrays and codec files are preserved in the separate ZIP; use that complete extracted run for the independent readback command.

## Next action and limits

Run the default Notebook 03 in Colab on all four sources, then upload the ZIP printed by Section 10. Review per-source and pooled stage changes before specifying an acquisition-aware reconstruction test. This notebook performs diagnosis only; it does not tune or deploy a new solver.

The sources remain previously exposed development data with unresolved pretrained DIV2K overlap and one noise realization per source. There is no independent calibration/test result, significance test, calibrated reliability or novelty claim. No review protocol or screening decision changed.
