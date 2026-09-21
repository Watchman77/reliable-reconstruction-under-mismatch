# JPEG-aware development checkpoint 04

## Status

This checkpoint records the completed four-source development experiment for JPEG-aware reconstruction and selective-detail scoring. It is a **development result**, not an independent test, calibrated reliability result, or established novelty claim.

The run covered DIV2K sources `0801`–`0804` under two acquisition stages (`quantized_8bit` and `jpeg_q75`), giving eight observations. The frozen design used the same 576 × 576 centre crop, 512 × 512 evaluation region, nominal blur and downstream reconstruction settings recorded in the notebook.

## Integrity record

- Exact uploaded executed notebook SHA-256: `8ea271c3ff9dcb9b30a73be22565d2e58caba14999f0c2207239a96d30127c88`
- Reconstructed raw archive size: `512634668` bytes
- Reconstructed raw archive SHA-256: `7d5f10a4b31364f202f73a254ed764f60342024dec8b90d2d03d09912d455f8a`
- Transfer parts verified: `6/6`
- Embedded chunk hashes verified: `6/6`
- Raw ZIP integrity test: passed
- Manifest-controlled internal files verified: `37/37`
- Configured source hashes reported by the saved readback: `4/4`
- Quality rows recomputed: `112`
- Patch-error vectors checked: `224`
- Score vectors recomputed: `128`
- Risk rows recomputed: `896`
- Maximum absolute quality difference: `7.105427357601002e-15`
- Maximum absolute patch difference: `0.0`
- Maximum absolute score difference: `0.0`
- Maximum absolute risk difference: `1.1102230246251565e-16`

The saved prediction arrays were independently read back and used to recompute the recorded metrics. Neural inference itself was not repeated during this archive audit.

## Development observations

For JPEG Q75 observations:

- Raw DPIR pooled PSNR: `30.057391 dB`
- FBCNN + DPIR pooled PSNR: `30.947555 dB`
- Difference: `+0.890164 dB`
- Raw DPIR mean detail MSE: `0.0005126495`
- FBCNN + DPIR mean detail MSE: `0.0003495773`
- Relative detail-MSE reduction: approximately `31.81%`
- Source-level wins against raw DPIR: `4/4`

For uncompressed 8-bit quantised observations, preprocessing did not improve the aggregate DPIR result:

- Raw DPIR pooled PSNR: `31.315850 dB`
- FBCNN + DPIR pooled PSNR: `31.231396 dB`
- Difference: `-0.084454 dB`

At 50% patch coverage for the JPEG FBCNN + DPIR pipeline:

- Best tested operational control, image-transform spread: approximately `0.00011784` detail MSE
- Operator-detail spread: approximately `0.00010497` detail MSE
- Relative reduction: approximately `10.92%`
- Source-level wins: `4/4`

Both frozen descriptive development screens passed.

## Scientific limits

The following remain false or unresolved in the saved decision record:

- `independent_test: false`
- `calibrated_reliability: false`
- `novelty_established: false`
- `stronger_trained_image_only_uncertainty_comparator_run: false`

The four DIV2K sources are exposed development examples. The pretrained DPIR and FBCNN families report DIV2K-related training, while checkpoint-specific overlap remains unresolved. Patches and acquisition stages do not create independent source replicates. Operator spread is therefore treated as a heuristic selection score, not posterior uncertainty or a calibrated probability.

The JPEG-aware cascade shows an acquisition-specific benefit on this development set; it is not evidence of universal improvement. It also does not test or invalidate Prof. Jang's diffusion method.

## Repository packaging

The repository notebook is a compact, reviewable derivative of the exact executed notebook. Code cells, execution counts, stdout and plain-text tables are retained, while bulky embedded HTML and image MIME payloads are removed. Standalone compact result tables and plots are stored with this checkpoint.

The 513 MB raw archive, eight prediction NPZ files, transfer ZIPs, model weights and source images are deliberately excluded from GitHub. Their hashes and manifests remain recorded in the compact evidence. The raw archive can be reconstructed from the six preserved transfer parts when a full prediction-level audit is required.

## Next scientific step

Freeze this checkpoint and design Experiment 05 as an independent evaluation with held-out source images, frozen Notebook 04 settings, multiple acquisition strengths, the existing operational controls, at least one stronger trained image-only uncertainty comparator, and a predeclared calibration/risk-coverage analysis. No setting or decision rule should be changed after inspecting the independent results.
