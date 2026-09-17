# Baseline 01: review of the user's saved Colab execution

17 September 2026. The saved Colab execution is now reviewed. This supersedes the earlier **Colab verification pending** status for this specific run.

## Evidence examined

- The user-uploaded `01_DIV2K_Baseline_Development (1).ipynb`: 2,437,859 bytes; SHA-256 `27f6354b217cfbaf0fbcb545e9e36abf8138c9201372eb85587f3a88aad2df95`.
- [Colab notebook](https://colab.research.google.com/drive/1CcWK7rUp9rEePzF_WMd77FRnIVeVajxz) and [dated Drive result folder](https://drive.google.com/drive/folders/1Gq58XTwllhKXrE6NgIo4fAskjwFxJBcP), named `pilot_01_20260917T115643_959108Z`.
- All seven readable CSVs from that folder, checked in the preceding continuation turn, and all three embedded tables plus all four embedded PNG figures from the uploaded notebook.
- [Machine-readable evidence](colab_execution_review_2026-09-17.json), including source and embedded-figure hashes and exact validation limits.

The attachment supplies the notebook evidence that the Drive connector could not return as readable content. It is a separate downloaded artifact; byte identity with the inaccessible Drive notebook download has not been established.

## Findings

The notebook is valid nbformat 4. All eleven code cells have consecutive execution counts 1–11 and there are no saved error outputs. Nine computational cells exactly match the delivered Baseline 01 notebook. The two added cells mount Google Drive and display the source-folder path. The saved output confirms mounting, prints progress for all four sources and points to the same dated folder that was located in Drive.

The dense-solver checks report maximum absolute errors of `1.9984014443252818e-15` for ridge and `9.992007221626409e-16` for gradient regularisation. The constant-image, selection, source-file and source-exclusion checks pass. The run reports four sources, 48 observations, 1,344 grid rows, 192 selected-inverse rows, 96 control rows and 4,608 patch-risk rows. These are dependent development combinations, not independent image counts.

The saved tables reproduce the earlier results. All 1,344 grid rows match the local run to at most `1.1102230246251565e-16` MSE difference; all 4,608 risk rows match to at most `9.996344030316351e-17`. All sixteen tuning choices exclude their evaluated source. The four recorded decoded-RGB hashes match the official archive manifest. The embedded 12-row summary, 16-row selection table and eight-row patch-score table match their CSV calculations at the precision displayed by pandas.

| Nominal inverse | Linear-condition pooled PSNR gain over input | JPEG-chain pooled PSNR gain over input |
|---|---:|---:|
| Gradient regularisation | +1.141 dB | +0.615 dB |
| Ridge regularisation | −1.567 dB | −1.754 dB |

The gradient inverse improves over the input in all 48 evaluated source/condition combinations. At 50% patch retention, its operator-spread score reduces pooled MSE by 9.94% (linear) and 11.18% (JPEG chain) relative to the best included residual, gradient or measurement-noise-spread control. Within the reference-defined textured quartile, the corresponding reductions are 11.32% and 7.88%. These are development findings without a significance, calibration or novelty claim.

## Figure inspection

1. **Regularisation sweep:** both logarithmic axes and the input references are visible; the poor small-strength settings and the gradient minimum remain represented.
2. **Source-excluded gains:** all four sources and both information modes appear. The nominal gradient gains are positive and ridge gains negative for each source after pooling its six conditions.
3. **Patch risk versus coverage:** labels identify the JPEG-chain condition and the reference-defined texture stratum. Methods reconcile at full coverage; operator spread is below the included operational controls in the displayed pooled comparisons.
4. **Reconstruction examples:** all four sources have reference, observed, ridge and gradient columns. The montage is an illustrative view of one linear anchor condition; it does not independently establish preservation of fine detail or absence of hallucination.

All four notebook figures were actually opened and inspected. This does not constitute a byte-level audit of the separately exported Drive PNGs.

## Warning and provenance housekeeping

There is one non-fatal pandas `FutureWarning` about concatenating DataFrames that contain empty/all-NA entries. The following checks and output cells complete. It does not invalidate the independently reconciled numerical results. A future maintenance change can concatenate only the columns used by the summary; the archived run and warning are preserved here.

The notebook's top-level `validation` object still describes the earlier in-process local execution and says Colab is unverified. Per-cell `inprocess_execution_seconds` values are inherited too. Those fields are stale for this Colab run and were **not** used as proof of native execution or its duration. The review instead uses consecutive saved execution counts, Colab/Drive outputs, the unchanged computational source and the separately retrieved result tables. The saved numerical check's elapsed time excludes plotting and saving and is not the total notebook runtime.

The original uploaded notebook is unchanged. The earlier local-run notebook and validation JSON in this repository remain historical records of that local execution.

## Decision and limits

The saved Colab run and its embedded presentation are verified to the extent described above. No rerun is needed to resolve the previous notebook-inspection gap. Separately exported PNG/JSON bytes and all fourteen output hashes have **not** been independently retrieved and verified, so no complete export-integrity claim is made.

Retain the stronger gradient-regularised classical baseline. The next research step remains a verified learned reconstruction baseline and an appropriate image-only uncertainty comparator, followed by genuinely source-disjoint calibration/testing. The current four sources remain development-only. This review does not establish novelty, validate the live Colab runtime, alter the scoping protocol or change screening decisions.
