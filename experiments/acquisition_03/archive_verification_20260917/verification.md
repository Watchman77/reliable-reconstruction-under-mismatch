# Acquisition 03: complete raw-archive verification

17 September 2026. **The raw-export verification gap is closed for this completed four-source development run.** All five uploaded parts reproduce the original archive; all 38 exported files pass manifest checks, and all 80 saved reconstruction outputs reproduce the recorded metrics. The scientific result remains mixed and does not establish novelty or independent-test performance.

## Archive identity and integrity

- Reconstructed archive: `acquisition_03_20260917T160754_303637Z.zip`.
- Bytes: **431,278,719**.
- SHA-256: `902cee988b76eb982efb068eca4c821d0259b4ef06d6c6f0d09163d1117549dc`.
- The size and hash match the receipt printed in the uploaded Notebook 03's final code-cell output. This expected receipt was parsed directly from the notebook; the separately stored Drive receipt was not retrieved. [Receipt origin](receipt_origin.json), [recorded receipt](notebook_recorded_zip_receipt.json).
- All five part hashes, part ordering and byte offsets pass; the assembled stream has the expected full-archive hash. [Transfer audit](transfer_validation.json).
- All 39 ZIP entries pass CRC checks. These comprise **38 result files plus the export manifest**. Every result file matches its manifest size and SHA-256; no extra or missing result file was found. [File audit](file_verification.json).

The earlier two failed whole-ZIP uploads were never read. This review uses the five subsequently accessible parts. Original uploads and experiment outputs were not edited.

## Independent numerical readback

The [independent validator](../../../scripts/validate_acquisition_03.py) implements the Fourier high-pass metric, interior crop and patch pooling separately from the notebook's reconstruction helper. It reads the original reference PNGs and the stored arrays without neural inference.

| Check | Verified scope |
|---|---|
| Source identity | All four original PNG file hashes and decoded RGB hashes |
| Acquisition coverage | 4 sources x 4 stages = 16 observations; complete status |
| Saved outputs | All 80 source/stage/model rows: 48 learned outputs and 32 input/classical controls |
| Reconstruction metrics | RGB MSE, RGB PSNR and detail MSE recomputed for all 80 outputs |
| Patch errors | All 160 saved RGB/detail vectors, 1,024 entries each; maximum absolute difference **0.0** |
| Full-coverage tail rates | All 240 values at detail-RMSE thresholds 0.025, 0.05 and 0.10 |
| Acquisition construction | All 16 stored observation hashes; clipping and rounding relationships; all four saved JPEG decodes |
| Codec identity | All four JPEG byte counts and hashes agree with acquisition.csv |
| Tables | Pooled summaries, adjacent-stage contrasts and model gaps reconcile |
| Earlier review | All nine raw CSVs are byte-identical to the previously retrieved CSVs |
| Recorded project provenance | Baseline, learned adapter, diagnosis implementation and design-freeze hashes match repository files |

All metric differences are below the pre-existing 1e-12 absolute acceptance threshold. The validator's maximum over its mixed metric fields is 7.11e-15; it is **not** reported as an MSE-specific quantity. [Numerical audit](raw_prediction_validation.json), [supplementary checks](supplementary_checks.json), [raw run metadata](run_metadata/).

`environment.json` now directly records CUDA on **Tesla T4**. This is preserved runtime metadata, not a new hardware measurement. Previously recorded model-loading and inference checks remain historical execution evidence; this audit did not rerun the learned network.

## Visual review

All four raw PNG figures were inspected and are byte-identical to the embedded figures already reviewed. The original source-0801 montage remains a one-source visualization.

The new [all-source readback montage](all_sources_codec_readback.png) uses the same fixed central 256 x 256 inset for each of the four sources, with reference, classical and nominal DPIR outputs before and after JPEG. No region was selected by error or visual impact. The numerical evaluation covers the full 512 x 512 interior. Structured artifacts are visible in the nominal JPEG insets, particularly sources 0801 and 0804; the quantitative ranking below comes from the full-region metrics, not visual judgement alone. This montage is not a visual inspection of every pixel of every saved reconstruction.

## Scientific finding reproduced

Pooled RGB PSNR is -10 log10 of the mean RGB MSE across the four sources.

| Acquisition stage | Nominal DPIR | Classical inverse | Nominal minus classical |
|---|---:|---:|---:|
| Linear float | 31.314871 dB | 30.820968 dB | +0.493903 dB |
| Clipped float | 31.314842 dB | 30.821189 dB | +0.493652 dB |
| 8-bit rounded | 31.315850 dB | 30.817274 dB | +0.498575 dB |
| JPEG Q75 | 30.057392 dB | 30.469349 dB | -0.411957 dB |

Adding JPEG after rounding lowers nominal pooled PSNR by **1.258458 dB**, versus **0.347925 dB** for the classical inverse. Nominal detail MSE increases **52.052910%**, versus **3.428938%** for classical reconstruction. Its relative detail ranking loses on all four JPEG sources; its RGB ranking loses on three, while source 0802 retains a +0.121048 dB advantage. These reproduce the prior review; the archive introduces no numerical reversal or new performance result.

This identifies a large relative deterioration at the whole JPEG encode/decode stage under the frozen order and Q75 setting. It does not uniquely identify an internal codec component or establish that clipping/rounding are harmless in general. The prior input-metric, true-blur diagnostic and error-tail qualifications remain applicable.

## Decision and limits

No further archive upload or experiment rerun is required for this verification. Preserve the classical baseline and frozen settings in the next acquisition-aware comparison. Before claiming a new correction method, complete the closest-method assessment, including the full paper supplied by the user from Prof Jang, and specify a bounded follow-up experiment.

These are the same four exposed development images, with one noise realization per source and unresolved pretrained DRUNet/DIV2K overlap. Verification establishes file integrity and reproducibility of saved-output metrics; it does not establish a new method, calibrated uncertainty, a unique causal mechanism, independent-test generalisation or novelty. The scoping-review protocol and screening decisions are unchanged.

## Reproduce the audit

From the repository root, provide the five transfer files, the executed notebook and the four original source PNGs:

```bash
python scripts/review_acquisition_03_archive.py \
  --parts-dir /path/to/uploaded_parts \
  --notebook /path/to/executed_notebook_03.ipynb \
  --data-dir /path/to/original_source_pngs \
  --work-dir /path/to/archive_work \
  --evidence-dir /path/to/audit_output
```

The script reconstructs and checks the archive, records the notebook-derived receipt provenance, verifies and extracts only the expected result files, invokes the independent metric readback, reconciles earlier reviewed bytes, and creates the fixed-inset montage. Visual interpretation requires opening the figures.
