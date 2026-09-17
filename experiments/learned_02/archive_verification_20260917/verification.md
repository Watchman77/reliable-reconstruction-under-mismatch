# Learned 02: completed-run archive verification

17 September 2026. **The completed Learned 02 run passes manifest integrity and saved-prediction readback.** This closes the raw-export access gap in the [earlier Colab review](../colab_execution_review_2026-09-17.md). It does not change that review's mixed scientific findings.

## Archive and run identity

Reviewed user attachment: `results-20260917T145005Z-1-001.zip`, **64,986,509 bytes**, SHA-256:

`cad475e235aedfcd114d88394c74b9804e9a83068965a695eedc2896960e1ff9`

All 79 ZIP entries pass CRC checks. Entry names contain no duplicate names, absolute paths or parent traversal; there are no symlinks. The ZIP contains five separate run folders. Each run was checked against its own manifest; the manifest itself is excluded from its listed file count.

| Run folder under `results/` | Manifest files matching size and SHA-256 | Finding |
|---|---:|---|
| `pilot_00_20260917T091557_922071Z` | 11/11 | Integrity passes |
| `pilot_00_20260917T115150_838153Z` | 11/11 | Integrity passes |
| `pilot_01_20260917T115643_959108Z` | 14/14 | Integrity passes |
| `learned_02_20260917T125501_043474Z` | 14/15 | Older incomplete run; excluded |
| **`learned_02_20260917T141654_945004Z`** | **23/23** | **Completed run; reviewed below** |

No manifest-listed files are missing and no unlisted result files occur in these folders. The [integrity inventory](integrity_inventory.json) records the checks. Hash agreement establishes consistency with the bundled manifest, not independent authentication of how the results were produced.

The older Learned 02 folder records `running`, four completed observations out of eight, and a last status update at 14:01:51 UTC. Its `compute.csv` is 4,342 bytes versus the manifest's 3,670 bytes and has a different hash. The archive alone does not establish why that run stopped. It is not used for the completed-run findings. The three earlier pilot folders received integrity checks here, not a new full scientific review.

The completed folder records `complete_for_configured_subset`, eight completed/planned observations, and a final status update at 14:18:37 UTC. Its 23 exports comprise six CSVs, five JSONs, four PNGs and eight prediction archives. The preserved [manifest and run metadata](run_metadata/) confirm the frozen configuration and recorded NVIDIA L4/CUDA environment. The six CSVs are byte-identical to the versions previously retrieved from Drive and reviewed with the notebook.

## Independent saved-prediction readback

The [readback script](../../../scripts/verify_learned_02_predictions.py) loads NPZ files with `allow_pickle=False`; it does not load the neural-network weights or rerun learned inference. It verifies the audited adapter/helper/vendor digests and rehashes the four local source PNGs and their decoded RGB against the recorded source identities and official development manifest.

All eight nominal learned predictions are finite `float32` arrays of shape 576 × 576 × 3, bounded within [0, 1]. The evaluation region is 512 × 512, divided into 1,024 patches of 16 × 16 pixels. All eight stored patch vectors per observation have the expected length and finite nonnegative values.

| Recomputed quantity | Result |
|---|---|
| RGB and detail patch errors from saved predictions and reference crops | Exact array agreement; maximum absolute difference 0 |
| Reference texture, image-gradient and measurement-residual scores | Exact array agreement; maximum absolute difference 0 |
| 24 quality rows: input, classical gradient inverse and saved nominal learned prediction across eight observations | Maximum absolute MSE difference 9.63 × 10⁻¹⁷ |
| All 448 risk-table rows from saved scores and recomputed errors | Maximum absolute MSE difference 1.00 × 10⁻¹⁶ |
| Bad-detail rates at all three preset tolerances | Maximum absolute difference 1.12 × 10⁻¹⁶ |

Risk checks include both strata, all preset coverages, recorded patch counts, tie handling, oracle-error ordering and the expected-random control. Numerical differences above are CSV floating-point round-trip differences. The [machine-readable audit](prediction_audit.json) and [eight-observation readback](prediction_readback.csv) preserve the results.

All four original exported figures were visually inspected. The original reconstruction montage covers the linear condition only. A further [JPEG readback montage](jpeg_prediction_readback.png) displays all four saved nominal JPEG predictions beside their reference crops and regenerated input/classical controls. This is a new visualization of existing outputs, not a new learned experiment. Visual inspection does not identify the causal source of the JPEG failure.

## Scientific conclusion and remaining limits

The completed-run evidence supports the earlier numbers: nominal DPIR improves pooled RGB PSNR over the classical comparator by **0.494 dB** for linear blur/noise, but loses **0.412 dB** with the JPEG chain. Its JPEG detail MSE is **35.237% higher** than the classical comparator. Positive pooled operator-selection comparisons coexist with source-specific losses and bad-detail-rate reversals; the full earlier review retains those exceptions.

Only nominal learned predictions were saved. The other 16 quality rows for true-blur learned and denoising-only outputs were checked arithmetically in the prior CSV review, but their images were not independently regenerated here. Operator/transformation spread arrays support verified ranking and risk arithmetic; their construction cannot be independently recomputed without the unsaved ensemble predictions or new inference. Recorded model smoke checks and environment information are hash-verified run records, not a fresh GPU execution by this review.

These remain four exposed development sources with unresolved checkpoint-training overlap, one noise realization per source and no independent calibration/test evaluation. File integrity does not establish novelty, calibrated reliability or generalization.

The next research step remains a bounded JPEG-chain diagnosis that separates clipping, quantization and compression while retaining the classical comparator and this frozen checkpoint. This archive review does not start that experiment, change the topic, amend the scoping-review protocol or change any screening decisions.

## Reproduce the prediction checks

Extract the completed run from the supplied ZIP. From the repository root, using the original four source PNGs:

```bash
python scripts/verify_learned_02_predictions.py \
  --run-dir /path/to/results/learned_02_20260917T141654_945004Z \
  --data-dir /path/to/samples \
  --repo-dir . \
  --output-dir /path/to/new-review-output
```

Dependencies: NumPy, pandas, Pillow and Matplotlib. The script uses the preserved Baseline 01 simulator to regenerate observations/classical controls and directly implements the detail transform and patch pooling for readback. Raw source images, pretrained weights and the large uploaded archive are not duplicated into Git; the exact archive identity, result manifest, metadata and derived review evidence are preserved here.
