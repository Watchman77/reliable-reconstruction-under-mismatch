# Acquisition 03: clipping, rounding and JPEG diagnosis

**Latest checkpoint:** the [completed Colab run is now reviewed](colab_execution_review_2026-09-17.md). All 16 observations are recorded complete on CUDA/T4 metadata with ten unchanged code cells. Nine retrieved CSVs reconcile six result tables; all 16 regenerated observation hashes, four codec hashes and 32 input/classical quality rows agree. Nominal DPIR's advantage is preserved through clipping/8-bit rounding and reverses overall at the JPEG step; its relative detail error worsens on all four sources. Four embedded figures were inspected. Raw learned-array and all-export hash verification still require the results ZIP.

**Archive transfer update:** the original 431,278,719-byte ZIP and receipt are visible in Drive, but the connector rejects ZIP downloads above 268,435,456 bytes. A separate streamed manifest download returned HTTP 403. [Notebook 03A](../../notebooks/03A_Package_Existing_Acquisition_Results.ipynb) packages the existing archive into five ZIPs under 100 MiB each, preserving its exact bytes and checking the recorded original hash. Run this transfer utility on CPU; do not rerun the experiment. Upload all five parts individually. [Local helper validation](transfer_helper_validation_2026-09-17.json) passed on the earlier one-source archive; full Colab raw verification remains pending. [Access details and instructions](archive_transfer_access_2026-09-17.md).

The local-run sections below are historical. Their full-Colab-pending statements are superseded by the linked review; the original local evidence remains intact.

This notebook follows the verified Learned 02 run: nominal DPIR improved the linear-blur comparator but underperformed the classical inverse with the JPEG chain. It measures the effect of adding each acquisition stage while preserving every reconstruction setting.

[Open/download Notebook 03](../../notebooks/03_DIV2K_Acquisition_Stage_Diagnosis.ipynb). Upload it into Colab, select a GPU and run all cells. Existing samples and the verified checkpoint are reused from the same Drive project. The final cell creates and verifies one ZIP beside the new results folder for review.

**Local execution complete:** [read the scoped review](local_execution_review_2026-09-17.md) and [independent audit](validation.json). Source 0801 completed all four stages; the full four-source Colab run remains pending. All 20 saved model outputs/metric rows and the result ZIP passed readback. Four figures are embedded after documented presentation replay.

## Frozen comparison

| Stage | Change from previous stage |
|---|---|
| Linear float | Original unbounded blur/noise observation |
| Clipped float | Clip to [0, 1], keeping floating precision |
| Quantized 8-bit | Round clipped values to the nearest 1/255 level |
| JPEG Q75 | Encode/decode the same uint8 pixels, quality 75, subsampling 0 |

Each source supplies all four stages with a shared noise realization. Five unchanged quality comparators are retained: observed input, classical gradient inverse, denoising-only DRUNet, nominal DPIR and true-blur DPIR. The input quality control remains display-clipped, so its first two scores are identical by construction. Inference still receives the unbounded first-stage observation.

[Design freeze](design_freeze.md), [diagnostic implementation](diagnostic.py) and [provenance](provenance.json) preserve the stage order, information budget, source/model identities and readouts. Earlier source files, notebooks and outputs are unchanged. The codec contrast includes colour conversion and whole encode/decode processing; it cannot identify DCT quantization as the sole cause. Adjacent error changes are conditional on stage order and are not independent source replicates.

The default experiment covers four exposed sources, 0801–0804, at four stages: 16 observations, 80 quality rows and 272 experiment denoiser calls plus two small checks. The predeclared local CPU validation covers only source 0801 at all four stages: 4 observations, 20 quality rows and 68 calls plus two checks. No resizing, shortened solver or outcome-dependent source selection is used.

## Validation and reproducibility

The notebook verifies all four source identities and the first/fourth simulator endpoints. Sixteen input/classical endpoint quality rows must match the verified Learned 02 CSV within 1e-12 absolute MSE before new learned inference. The unchanged adapter performs strict weight loading, upstream hash, schedule, transform, dense HQS and repeated smoke checks.

Every compared reconstruction and supplied observation is saved, with RGB/detail patch errors, source/stage identities, codec bytes, timing, iteration traces and recorded software/codec versions. Completed snapshots regenerate the manifest. Final checks recompute all errors from saved arrays, validate row counts and adjacent-stage arithmetic, then verify the result ZIP. Partial/failed runs retain explicit status and are not packaged as complete.

An additional [independent readback script](../../scripts/validate_acquisition_03.py) recomputes the Fourier detail transform and patch pooling directly, checks every saved model image and full-coverage tail rate, reconciles summaries/contrasts and rechecks the ZIP:

```bash
python scripts/validate_acquisition_03.py \
  --run-dir /path/to/results/acquisition_03_RUN \
  --data-dir /path/to/samples \
  --audit-output /path/to/validation.json
```

The local native Jupyter kernel failed before executing a cell (`Operation not permitted` from ZeroMQ's interface resolution). The [attempt record](native_kernel_attempt.json) preserves that limit. The declared fallback runs notebook cells sequentially through IPython; it does not verify Colab, GPU execution or Drive mounting.

To reproduce the bounded CPU validation from the repository root:

```bash
IMAGING03_DATA_DIR=/path/to/samples \
IMAGING03_WEIGHTS=/path/to/drunet_color.pth \
IMAGING03_SOURCE_IDS=0801 \
IMAGING03_OUTPUT_DIR=/path/to/new/acquisition_03_RUN \
python scripts/execute_notebook_inprocess.py \
  notebooks/03_DIV2K_Acquisition_Stage_Diagnosis.ipynb \
  --scope 'Source 0801; four stages; full resolution; 4/16 design observations.'
```

Omit the source override for all four sources. The notebook builder embeds all required source code and the upstream MIT licence; raw source images and pretrained weights are not embedded. `python scripts/build_acquisition_03_notebook.py` rebuilds the notebook and clears its saved outputs.

## Interpretation boundary

The intended decision is where the fixed nominal-versus-classical reconstruction gap changes and what acquisition-aware follow-up deserves a separately frozen test. This diagnosis does not tune a new solver or establish a unique internal mechanism. Full-coverage patch exceedance rates are not calibrated uncertainty or direct hallucination detection.

The four sources remain exposed development data with unresolved DRUNet/DIV2K training overlap. No independent-test, statistical significance, calibration or novelty claim is warranted. The topic, scoping-review protocol and screening decisions remain unchanged.
