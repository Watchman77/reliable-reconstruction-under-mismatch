# JPEG-aware baseline 04

Notebook: [`04_DIV2K_JPEG_Aware_Baseline.ipynb`](../../notebooks/04_DIV2K_JPEG_Aware_Baseline.ipynb).

Acquisition 03's verified four-source run showed the nominal DPIR/classical gap worsening at JPEG processing. This experiment compares established blind FBCNN preprocessing while preserving the historical simulator, inverse settings and exposed development sources. The [frozen design](design_freeze.md) specifies comparisons and descriptive decision rules before inspecting new outcomes. The [comparator audit](comparator_audit.md) documents official source/weight identities, training and codec limits, and the declared adapter.

## Local validation checkpoint

The [predeclared one-source CPU run](local_execution_review_2026-09-17.md) completed both conditions. Independent saved-array readback reproduced all 28 quality rows, 56 patch-error vectors, 32 score vectors and 224 risk rows; all four figures were inspected. On source 0801, FBCNN + DPIR gains 1.528 dB over raw DPIR with JPEG and reduces detail MSE by 52.563%, but loses 0.170 dB without JPEG. Operator detail spread beats the included operational controls in the primary one-source comparison. Both full four-source screens remain unassessed. The released notebook is clean, defaults to all four sources and has no inherited outputs; the exact local execution is preserved separately. GPU, Drive and full four-source inference remain pending.

## Design

Four sources × two conditions (8-bit uncompressed and JPEG Q75) give eight observations. The main models are input, classical gradient inverse, DPIR, FBCNN-only, FBCNN + classical, and FBCNN + DPIR. Raw DPIR and FBCNN + DPIR each additionally run two operator perturbations and two whole-pipeline rotations. FBCNN estimates quality automatically; it receives no quality metadata or clean references.

The primary reconstruction screen compares JPEG detail MSE against three inverse controls. The primary selective-detail screen uses the detail operator score at 50% retention, all patches, with rotation/residual/gradient/random controls and three bad-detail tolerances. Exact rules and secondary outcomes are frozen in the design. The four-source screens are not assessed on a one-source subset.

Full design: 112 quality rows including 48 main rows, 896 risk rows, 640 experiment DRUNet calls and 24 FBCNN calls. Loading/parity checks add two DRUNet and three FBCNN calls. Both score ensembles share nominal predictions; FBCNN rotation controls require more preprocessing calls than operator perturbations. Actual compute is recorded without claiming equal total budgets.

## Run and retrieve

1. Upload the notebook into Colab; select a GPU runtime and choose Run all.
2. Authorize the Drive mount. Keep the original four PNGs in `MyDrive/reliable-reconstruction-under-mismatch/samples`. The official weights are downloaded once or verified in `model_cache`.
3. Section 11 prints one dated SUMMARY ZIP and all numbered RAW ZIP parts. Upload the summary plus every part for review. The complete RAW archive and the original result folder also remain in Drive.

The notebook is self-contained and needs no repository clone. It saves unique dated folders, checks all source identities and historical observation hashes before inference, and preserves every reconstruction, patch-error vector, score vector, JPEG stream, metric, cost, trajectory and figure. Independent saved-array readback must pass before export marks a configured run complete. Sources and weights are external inputs.

The summary omits arrays and cannot replace raw verification. Transfer parts carry at most 96 MiB payload each. The exporter checks manifest identity, archived bytes and reconstructed whole-archive hashes. The helper's small roundtrip, idempotency, missing-part and corruption tests are recorded in [transfer_helper_validation.json](transfer_helper_validation.json).

Rebuild the unexecuted notebook with `python scripts/build_jpeg_aware_04_notebook.py`. Execute locally with the existing in-process runner and explicit `IMAGING04_SOURCE_IDS`, `IMAGING04_DATA_DIR`, `IMAGING04_WEIGHTS`, `IMAGING04_FBCNN_WEIGHTS` and a new `IMAGING04_OUTPUT_DIR`. All four source PNGs remain required for preflight even when a subset is selected.

Independent readback:

```bash
python scripts/validate_jpeg_aware_04.py --run-dir /path/to/run --data-dir /path/to/samples --audit-output /path/to/audit.json
```

## Interpretation limits

This is a baseline development composition, not an original architecture, optimal cascade, exact JPEG likelihood or FBCNN paper reproduction. Preprocessing can change the effective noise and remove useful detail. Both pretrained model families report DIV2K training and their checkpoint-level image overlap is unresolved. Source 0801–0804 outcomes do not establish independent performance.

The selection controls remain limited heuristics; trained uncertainty comparisons, independent calibration/testing and novelty assessment are outstanding. A negative cascade result does not reject the broad PhD topic or the separate scoping-review route. Earlier experiments, review protocol and formal screening counts are preserved.
