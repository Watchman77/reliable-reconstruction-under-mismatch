# Research artifact inventory

This index distinguishes reproducible repository assets from large raw archives. The repository is the authoritative location for code, clean notebooks, small result tables, figures, manifests, checksums, and verification receipts. Raw datasets, model weights, executed notebooks, and large ZIP/NPZ bundles are retained outside ordinary Git history and are identified by hashes in committed receipts.

## Experimental stages

| Stage | Canonical implementation | Committed evidence | Raw-artifact status |
| --- | --- | --- | --- |
| Phase-0 classical canary | `experiments/phase0_canary/pilot.py` | `experiments/phase0_canary/CANARY_RESULT.md` and compact outputs | Compact results committed |
| 00 four-source Colab pilot | `notebooks/00_DIV2K_Operator_Mismatch_Pilot.ipynb` | `experiments/colab_pilot_00/saved_run_review.json` | Executed notebook/raw export retained externally |
| 01 classical baseline | `experiments/baseline_01/baseline.py` | Reproducible implementation | No separate notebook required |
| 02 learned baseline | `experiments/learned_02/learned.py` | Reproducible implementation | Model weights excluded |
| 03 acquisition diagnosis | `experiments/acquisition_03/diagnostic.py` | Reproducible implementation | No separate notebook required |
| 04 JPEG-aware baseline | `notebooks/04_DIV2K_JPEG_Aware_Baseline.ipynb` and `experiments/jpeg_aware_04/` | `results/jpeg_aware_04_20260917T201107_721467Z/` and `docs/jpeg_aware_04_verified_checkpoint.md` | Large multipart ZIP retained externally |
| 05A protocol/data audit | `notebooks/05A_Independent_Validation_Protocol_Audit.ipynb` | Protocol, freeze receipt, data receipt and duplicate audit in `experiments/independent_05/` | Raw dataset archives excluded |
| 05C engineering canary | `notebooks/05C_Independent_Validation_Engineering_Canary.ipynb` | `canary_readback_receipt.json` and amendment 0001 | Raw canary ZIP/executed notebook retained externally |
| 05C1 development generation | `notebooks/05C1_Development_Reconstruction_Shards.ipynb` | Per-shard receipts and `development_shard_registry.json` | Shard ZIPs retained externally |
| Independent held-out evaluation | Frozen by `protocol_freeze.json` | No test result exists | Unauthorized until the explicit transition gate passes |

## Current 05C1 checkpoint

- Verified development shards: **1 of 12**.
- Shard 00 sources: DIV2K `0805`–`0812`.
- Shard 00 observations: **56 of 56**.
- Shard 00 receipt: `experiments/independent_05/development_shard_00_readback_receipt.json`.
- Shard 00 raw ZIP SHA-256: `4b7a011a4300417104278e673a2e61eb4a301f776a95a96259cafcecb25ea608`.
- Independent test inference remains **not authorized** and **not performed**.

## Notebook policy

Clean, self-contained notebooks are committed when a notebook is the canonical execution interface. Stages 01–03 are canonical Python modules rather than missing notebook deliverables. Exact executed notebooks are retained externally when their stored outputs materially increase size or expose environment-specific metadata; committed verification records preserve the execution evidence.

The received executed 05C canary notebook is 390,597 bytes with SHA-256 `2ee9ce03d9de8fc1448a7bf7bd669a33122a27cedcc08bece3f8b838c6c50180`; all seven code cells were executed and no error output was present. The clean canonical notebook remains the committed version. An executed 05C1 notebook was not received with shard 00, but the returned raw shard archive was independently verified.

## Raw-artifact policy

Do not commit downloaded datasets, pretrained weights, raw ZIP archives, or large per-observation arrays to ordinary Git history. For every accepted external result archive, commit:

1. its SHA-256 and byte count;
2. its internal manifest verification result;
3. the relevant row, record and tensor counts;
4. the test-data firewall state;
5. the validator path and any limitations.

This preserves reproducibility and auditability without turning the source repository into binary storage.
