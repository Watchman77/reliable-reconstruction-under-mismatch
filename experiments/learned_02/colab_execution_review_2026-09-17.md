# Learned 02: review of the completed Colab development run

17 September 2026. **The eight-observation run completed; the scientific findings are mixed.**

The learned baseline improves reconstruction under linear blur/noise, but loses to the inherited classical baseline when the JPEG chain is added. Operator sensitivity gives positive pooled mean-detail-error comparisons against the included controls. That advantage does not consistently extend to bad-detail rates or every source. These observations support a focused diagnosis of the acquisition-chain failure, not a novelty or calibration claim.

**Subsequent archive update, 17 September 2026:** the user supplied the raw results ZIP. The [separate archive verification](archive_verification_20260917/verification.md) confirms all 23 completed-run file hashes, eight saved nominal predictions and all 448 risk rows, and adds visual inspection of the raw figures and JPEG prediction readback. The access limitation described below and the original audit JSON are preserved as the earlier review history; they no longer describe current access to this completed run.

## Evidence and execution

- Reviewed the uploaded `02_DIV2K_Learned_Baseline (1).ipynb`, 2,541,643 bytes, SHA-256 `eff283ea870efd5a8c9f39151fd5a78848e8bac627e5fde66897d0e3ab7f33aa`.
- [User's Colab notebook](https://colab.research.google.com/drive/1HLzxabIHN0r6EO0FqX5zCgIfZKtyZ_yL). The attachment is the reviewed snapshot; its byte identity with the current Drive notebook is not asserted.
- All 19 cell sources, including all nine code cells, match the issued notebook at repository commit `fe8c2d7b879552267f98402108ff4af616eb4dea`. Execution counts are 1–9. There are no saved error outputs or stderr streams.
- Setup output records Drive mounting, CUDA and all four sources with both conditions. Colab metadata records an L4 GPU. The final output reports eight completed observations, 40 quality rows, 448 risk rows and 392 experiment denoiser calls. The two small learned validation calls are additional to that experiment count.
- [Dated Drive results](https://drive.google.com/drive/folders/1c_613akY5iGZOga6n5PMbAqmq-39uZW5): `learned_02_20260917T141654_945004Z`. The listing contains the expected 23 exports plus the manifest, including eight prediction archives in its subfolder.
- Retrieved all six CSVs through the readable-text interface. Their byte lengths match the corresponding Drive listing. Recomputed summaries, PSNR, risk endpoints, oracle-error bounds, row uniqueness/counts and denoiser-call totals. All three notebook tables reconcile at their displayed precision. Their renderer shows six decimal places, including where the code first applies `.round(7)`; full CSV precision was used for this review's arithmetic.
- The four reported RGB hashes agree with the official DIV2K archive manifest. The inherited input and classical-gradient errors reproduce the same eight-condition subset of Baseline 01 to below 1e-14 absolute MSE. This comparison uses precisely the same true blur/noise settings, not the earlier 48-observation pool.
- Decoded and visually inspected all four embedded figures. The reconstruction montage contains only the linear condition; it does not visually establish what happened in the JPEG reconstructions.

[Machine-readable audit](colab_review_20260917/audit.json), [CSV evidence](colab_review_20260917/csv_exports/), [embedded figures](colab_review_20260917/embedded_figures/) and [review script](../../scripts/review_learned_02_colab.py) are preserved. The original attachment, issued notebook and local one-case records were not rewritten. No learned inference was rerun for this review.

## Reconstruction quality

These are pooled RGB PSNR values from the mean MSE across four sources in each condition, not mean per-image PSNRs.

| Acquisition condition | Input | Classical gradient | Denoising-only DRUNet | Nominal DPIR-style | True-blur diagnostic |
|---|---:|---:|---:|---:|---:|
| Blur + noise | 29.744 dB | 30.821 dB | 29.902 dB | 31.315 dB | 34.782 dB |
| Blur + noise + JPEG chain | 29.678 dB | 30.469 dB | 29.756 dB | 30.057 dB | 30.153 dB |

Nominal DPIR gains **0.494 dB over the classical inverse** under linear blur/noise and improves all four individual sources. Under the JPEG chain it loses **0.412 dB** to the classical inverse and loses on three of the four sources. On 0801 with the JPEG chain it also falls below the input: 32.528 versus 32.674 dB. The complete source-level comparisons are [saved here](colab_review_20260917/quality_per_source.csv).

The high-pass detail metric exposes a stronger failure. Under the JPEG chain, nominal DPIR's mean detail MSE is **35.237% above the classical inverse** and **27.525% above the input**, even though its pooled RGB PSNR remains 0.380 dB above the input. It has higher detail MSE than the classical inverse on all four JPEG-chain sources. Under linear blur/noise, its mean detail MSE is 7.924% below the classical inverse.

The true-blur diagnostic reaches 34.782 dB in the linear condition but only 30.153 dB with the JPEG chain, still below the classical inverse. It is also worse than nominal DPIR in RGB PSNR for JPEG-chain sources 0802 and 0803. Supplying true blur therefore does not repair the omitted clipping/quantisation/codec chain in this experiment. The design does not isolate which omitted stage or solver/prior interaction causes the failure. The word “oracle” denotes access to true blur, not a guaranteed quality upper bound under an incomplete model.

## Selection: positive mean-error results with exceptions

All selections concern the nominal DPIR reconstruction. The primary score is detail-domain operator spread. Included operational controls are detail-domain fixed-operator image-transformation spread, measurement residual and reconstructed-image gradient. Both ensemble scores use three eight-iteration reconstructions with a shared nominal output; each adds sixteen denoiser calls. They are heuristic sensitivities, not calibrated uncertainty estimates.

At 50% retained coverage, the following are pooled detail-MSE reductions against the lowest-error included operational control. That control is image-transformation spread in all four rows.

| Condition | All patches | Within the reference-defined texture quartile |
|---|---:|---:|
| Blur + noise | 10.190% | 6.396% |
| Blur + noise + JPEG chain | 6.518% | 2.696% |

Pooled reductions remain positive at the prespecified 75% and 90% coverages; all scores agree at 100%. Across all patches, all four sources improve at 50%. Within the texture quartile, only three of four do: source 0804 loses by 0.442% in the linear condition and source 0801 loses by 0.732% in the JPEG condition, relative to each source's lowest-error included control. The [full comparison table](colab_review_20260917/selection_comparisons.csv) retains these distinctions.

**Mean error and failure rate can rank scores differently.** At 50% coverage and detail-RMSE tolerance 0.05:

| Condition and stratum | Operator-detail bad-patch rate | Transformation-detail bad-patch rate |
|---|---:|---:|
| Linear, all patches | 0% | 0% |
| Linear, texture quartile | **3.125%** | **1.953%** |
| JPEG chain, all patches | **0.1465%** | **0.0977%** |
| JPEG chain, texture quartile | 6.445% | 6.836% |

For linear textured patches, these rates correspond to 16 versus 10 bad patches among 512 retained patches across the four sources. For JPEG across all patches, they correspond to 3 versus 2 among 2,048. These are descriptive counts, not independent Bernoulli trials or significance tests. A lower mean error does not establish fewer severe errors or calibrated reliability. All three preset tolerances are retained in the [failure-rate table](colab_review_20260917/failure_rates_at_50.csv).

The secondary RGB-domain operator score also beats the primary detail-domain operator score in both JPEG strata at 50% coverage. Thus, this run does not establish that moving sensitivity into the detail domain is an improvement. That comparison was not omitted or used to switch the primary score after seeing the outcome.

## Compute and metadata limits

The recorded reconstruction calls total **53.938 seconds**. Nominal DPIR averages 1.132 seconds per observation; the classical inverse averages 0.070 seconds. Operator-perturbation calls total 17.298 seconds, versus 17.318 seconds for the two outer rotations, across all eight observations. These costs exclude final score computation, plotting, saving and setup. They are timings of this saved run, not general GPU benchmarks. All learned-call rows record 576 × 576 inputs and CUDA peak allocated memory between 618.44 and 636.63 MiB.

The notebook's `validation` metadata and `inprocess_execution_seconds` still describe the earlier local one-case run, including its display replay. They were inherited when the user opened the notebook in Colab. They are not evidence that this new run was partial, nor valid timings for it. Current setup/final outputs and the retrieved CSVs establish the eight-observation scope. Their coexistence is documented rather than silently rewriting historical provenance.

**Historical limitation at the time of this notebook/CSV review; subsequently resolved by the linked archive review.** Full raw-export integrity was then unverified. The raw manifest transfer produced a signed reference, but downloading it returned HTTP 403; its readable JSON fallback was empty. Therefore, separately exported JSONs, PNGs and prediction archives were not byte-audited. The figures reviewed here are the notebook's embedded versions. The locally recorded CSV hashes preserve the text retrieved for this review; they were not compared with the unavailable run manifest. Nominal predictions and patch arrays were not independently recomputed from the raw archives. This limitation must not be described as “all 23 hashes verified.”

## Research decision

Keep this run frozen, retain the classical comparator, and continue with a bounded diagnosis of the JPEG chain before expanding the mechanism or claiming robustness. A useful next design should separate clipping/quantisation from compression and test whether accounting for the omitted acquisition processing improves reconstruction. Preserve the current comparison alongside any new model or solver setting; do not repeatedly tune these same four sources and present the result as independent confirmation.

These are four previously exposed development sources with reported DRUNet/DIV2K training overlap, one noise realisation per source, one true blur/noise anchor and no source-disjoint calibration/test split. A transformation ensemble is not a substitute for all appropriate learned uncertainty comparators. Multiple learned reconstruction families and definitive closest-method checks remain outstanding. Novelty and calibrated reliability remain unestablished.

The scoping-review route remains a separate decision requiring added value over prior reviews and a completed formal method. No protocol, screening decision or review-corpus record was changed by this execution review.
