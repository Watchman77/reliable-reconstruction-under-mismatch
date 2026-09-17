# Acquisition 03: review of the completed Colab run

17 September 2026. **All 16 observations are recorded complete, and the retrieved tables reproduce the notebook's results. The main reconstruction deterioration appears when the JPEG codec is added.** This statement is specific to these four exposed development sources and the frozen stage order.

## Execution evidence and source identity

Reviewed attachment: `03_DIV2K_Acquisition_Stage_Diagnosis (1).ipynb`, 3,251,602 bytes, SHA-256 `018c76ca47ec82728fac364774cfdf915862851f751f9f05d13412921edfe751`.

All ten code cells exactly match the issued notebook at commit `11b39e19f607699449a2a3fde24d910721021aa5`. Counts run consecutively from 1 to 10, with no saved error outputs or stderr streams. The only source-text difference is the opening of the final Markdown cell: “Keep the earlier experiment frozen” becomes “we keep the earlier experiment frozen.” No numerical setting or algorithm changed.

Section 2 records a mounted Drive, CUDA and sources 0801–0804 across all four stages. Colab metadata names a T4 GPU. Section 4 records 16 completed observations, 80 quality rows, 60 adjacent-stage rows and 272 experiment denoiser calls, plus the two small validation calls. It reports all 80 stored-model quality rows passing its internal readback. These are recorded checks; fresh neural inference was not performed in this review.

The [dated Drive folder](https://drive.google.com/drive/folders/1tgf-S722lWgQO0EYe46k0lBhXUZnUGAb) contains the expected 38 result files plus its manifest: nine CSVs, five JSONs, four PNGs, sixteen prediction archives and four JPEG files. All nine CSVs were retrieved as text; their local byte lengths agree with the Drive listing. Their hashes preserve the versions read here, but cannot yet be compared with the inaccessible export manifest.

## What was independently checked

- Reconciled all six result tables against full-precision CSVs at their displayed rounding: pooled quality, stage changes, source gaps, full-coverage tail rates, endpoint drift and grouped costs. The separate five-row method table is descriptive.
- Checked the full 80-row source/stage/model grid, PSNR arithmetic, positive finite MSEs, tail-rate bounds/order, pooled summaries, all 60 adjacent changes, all 16 model gaps, telescoping endpoint changes, 64 cost rows and 256 iteration records.
- Rehashed all four local source PNGs and decoded RGB arrays; source identities and crop metadata agree with the official development manifest and retrieved source table.
- Regenerated all 16 stage observations from those sources and the unchanged simulator. All 16 observation hashes match the acquisition table. Regenerated all four JPEG byte streams; all four codec hashes also match the acquisition table. This checks deterministic construction against recorded hashes, not independent inspection of the separately stored codec files.
- Regenerated all 32 input/classical quality rows; maximum absolute RGB/detail MSE difference is 9.63 × 10⁻¹⁷. Acquisition statistics agree to below 1.12 × 10⁻¹⁶. Reconciled all 40 endpoint comparisons with the prior Learned 02 CSV; the largest recorded absolute PSNR drift is 1.53 × 10⁻⁶ dB.
- Inspected all four embedded figures. Their trends agree with the tables; the image montage covers source 0801 only. The other three sources have numerical comparisons, but their individual reconstructed images were not visually inspected here.

[Machine-readable audit](colab_review_20260917/audit.json), [retrieved CSVs](colab_review_20260917/csv_exports/), [embedded figures](colab_review_20260917/embedded_figures/), [rendered tables](colab_review_20260917/rendered_tables/) and the [review script](../../scripts/review_acquisition_03_colab.py) preserve the evidence. The uploaded notebook and earlier local run are not rewritten.

## Reconstruction result

Pooled RGB PSNR is −10 log10(mean MSE across the four sources), not mean per-source PSNR.

| Acquisition stage | Nominal DPIR | Classical gradient | Nominal minus classical |
|---|---:|---:|---:|
| Linear float | 31.314871 dB | 30.820968 dB | +0.493903 dB |
| Clipped float | 31.314842 dB | 30.821189 dB | +0.493652 dB |
| 8-bit rounded | 31.315850 dB | 30.817274 dB | +0.498575 dB |
| JPEG Q75 | 30.057392 dB | 30.469349 dB | −0.411957 dB |

Adding the JPEG codec after 8-bit rounding lowers nominal DPIR's pooled PSNR by **1.258458 dB**, versus **0.347925 dB** for the classical inverse. Nominal detail MSE rises **52.052910%** at that step; classical detail MSE rises **3.428938%**. Clipping and initial 8-bit rounding have small effects under this tested setting. That does not establish that they are harmless at other noise levels, exposures, bit depths or scenes.

The learned-versus-classical detail gap changes from negative to positive at the JPEG stage on **all four sources**. The JPEG step worsens nominal RGB PSNR and detail MSE on all four, and worsens its relative detail-MSE gap on all four. In JPEG RGB PSNR, nominal DPIR loses to classical reconstruction on three sources, while 0802 retains a small +0.121048 dB advantage. Thus the stronger all-four statement applies to the detail metric, not the RGB ranking.

The true-blur DPIR diagnostic also deteriorates: its pooled PSNR drops **4.624501 dB** when the codec is added. Its final 30.153138 dB remains below the classical inverse. Supplying true blur does not repair the omitted codec in this setup; it is not a guaranteed quality upper bound under an incomplete acquisition model.

The input control supplies a useful qualification: adding JPEG slightly worsens its pooled RGB PSNR by 0.061182 dB but lowers its high-pass detail MSE by 5.273116%. Different metrics and algorithms respond differently. The codec is not uniformly worsening every measured quantity.

## Full-coverage error tails

At JPEG Q75, the pooled full-coverage bad-detail rates are:

| Detail-RMSE tolerance | Nominal DPIR | Classical gradient |
|---|---:|---:|
| 0.025 | 20.092773% | 17.089844% |
| 0.05 | 4.687500% | 2.124023% |
| 0.10 | 0.097656% | 0% |

At 0.05 these correspond to 192 versus 87 patches out of 4,096; at 0.10, four versus zero. These patches are spatially dependent and the four sources are development data. The counts are descriptive, not independent-trial significance tests, calibrated failure probabilities or direct hallucination detections. All five models remain in the [full tail-rate table](colab_review_20260917/full_coverage_tail_rates.csv).

## Execution metadata and integrity boundary

Recorded reconstruction calls total **99.212 seconds** on this run. This excludes setup, metrics, plots and export. Learned rows record 576 × 576 inputs and CUDA peak allocated memory of 618.438–636.625 MiB; these are run records, not general hardware benchmarks.

The notebook still carries the old local-validation metadata, including `configured_observations: 4`, `full_design_complete: false`, sequential-IPython timings and the local presentation replay. The introductory local-result paragraph is historical too. Those fields were inherited when the notebook was opened in Colab. Current cell outputs, the full source/stage CSV grid and Section 10 establish the new 16-observation scope. That inherited metadata is not evidence of a replay in this Colab run.

Section 10 reports successful creation and verification of `acquisition_03_20260917T160754_303637Z.zip`, **431,278,719 bytes**, SHA-256 `902cee988b76eb982efb068eca4c821d0259b4ef06d6c6f0d09163d1117549dc`, with 38 verified result files. **These are the notebook's recorded archive checks, not independent ZIP verification by this review.**

The raw manifest fetch produced a streamed reference, but retrieving it returned HTTP 403; readable JSON content was empty. Therefore the separately exported JSON/PNG/NPZ/JPEG bytes and all 38 manifest hashes have not been independently audited here. In particular, the 48 learned model images across 16 observations have not undergone fresh raw-array error readback. The 32 input/classical rows were regenerated as described above. No learned inference was rerun. Uploading the reported ZIP will close this remaining raw-export verification step.

## Research decision

The acquisition-stage diagnosis now has four-source development evidence: the marked relative degradation arises at the whole JPEG encode/decode step after initial clipping and 8-bit rounding. It does not identify DCT coefficient quantization, colour conversion, boundary effects or solver/prior response as a unique internal cause. Effects are conditional on this stage order and codec setting.

Preserve this run and the classical comparator. After raw-export verification, specify a bounded acquisition-aware follow-up that compares an explicit JPEG-processing treatment with the frozen baseline, records compute and keeps negative controls. Do not describe ordinary codec-aware reconstruction as novel without a separate closest-method assessment.

These remain four exposed sources, one noise realization per source and unresolved DRUNet/DIV2K training overlap. There is no held-out calibration/test or novelty result. This review changes neither the umbrella topic nor the separate scoping-review protocol or screening decisions.
