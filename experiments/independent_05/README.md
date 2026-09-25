# Independent validation 05

## Current state

Stages 05A–05F are complete. The protocol, development/test separation, duplicate audit, CUDA canary, 12 development shards, PatchErrorNet ensemble, 11 calibration mappings, five sealed test shards, one-time analysis and final literature/experimental synthesis all passed their recorded integrity checks.

The independent test contains 40 sealed TESTIMAGES sources across seven acquisition chains. Stage 05E recorded 280 source-chain observations, 1,680 quality rows, 33,600 risk rows, 10,000 paired source-bootstrap replicates and 100,000 sign-flip randomisations per confirmatory hypothesis.

H1 passed: FBCNN preprocessing followed by nominal DPIR reduced source detail MSE by 90.13% on the primary `j75_b16_n2` chain. H2 did not pass its combined confirmatory gate: operator-spread selection reduced 50%-coverage retained-patch detail risk by 4.46% relative to image-transform spread, which was statistically detectable but below the predeclared 5% practical threshold. No positive calibration event occurred at centre-patch detail RMSE greater than 0.05 across 286,720 rows, so positive-event calibration is not estimable.

Stage 05F therefore rejects the original unified novelty claim and supports a narrower acquisition-chain and reliability-assessment contribution. The exact decision, archive hashes, permitted wording and prohibited claims are in `../../docs/stage_05_final_checkpoint.md`. Compact 05E and 05F evidence is committed under `../../results/`; large sealed shards, original ZIPs and executed notebooks remain external immutable records linked by SHA-256.

## Files

- `protocol_freeze.json` — machine-readable scientific and execution authority.
- `dataset_exposure_audit.csv` — training/benchmark exposure evidence and cohort decisions.
- `freeze_receipt.json` — validation result and hashes for the protocol, audit, explanatory document and validator.
- `notebook_verification.json` — executed-notebook and rendered-HTML checks.
- `data_receipt.json` — outcome-blind archive, source, decode and fingerprint receipt.
- `duplicate_audit.csv` — all 3,840 TESTIMAGES × DIV2K exact/pHash/dHash comparisons.
- `stage_05c_status.json` — granular readiness state; test authorization remains false.
- `stage_05d_status.json` — current authorized-but-unrun state and exact Stage-05D/05E artifact hashes.
- `canary_readback_receipt.json` — independent hash, schema, tensor, calculation and sealed-scope readback evidence.
- `development_shard_registry.json` — append-only register of independently verified development shards.
- `development_shard_00_readback_receipt.json` — archive, manifest, record, compact-array, metric and sealed-scope verification for shard 00.
- `development_shard_01_readback_receipt.json` — shard 01 verification with the outer-container mismatch explicitly recorded.
- `development_shard_02_readback_receipt.json` — shard 02 verification with the outer-container mismatch explicitly recorded.
- `development_shard_03_readback_receipt.json` — shard 03 verification; executed notebook and notebook-reported outer hash were not received.
- `development_shard_04_readback_receipt.json` — shard 04 verification with the outer-container mismatch explicitly recorded.
- `development_shard_05_readback_receipt.json` — shard 05 verification with the outer-container mismatch explicitly recorded.
- `development_shard_06_readback_receipt.json` — shard 06 verification with the outer-container mismatch explicitly recorded.
- `development_shard_07_readback_receipt.json` — shard 07 verification with the outer-container mismatch explicitly recorded.
- `development_shard_08_readback_receipt.json` — shard 08 verification with the outer-container mismatch explicitly recorded.
- `development_shard_09_readback_receipt.json` — shard 09 verification with the outer-container mismatch explicitly recorded.
- `development_shard_10_readback_receipt.json` — shard 10 verification with the outer-container mismatch explicitly recorded.
- `development_shard_11_readback_receipt.json` — shard 11 verification with the outer-container mismatch explicitly recorded.
- `amendments/0001_canary_schema_and_provenance.json` — outcome-blind schema/provenance correction record.
- `notebook_05c_verification.json` — static notebook verification and explicit CUDA execution gap.
- `notebook_05c1_verification.json` — static verification of the 12-shard development generator.
- `notebook_05c2_verification.json` — static, synthetic-calibration and actual 12-shard consumer verification for reliability fitting.
- `development_reliability_readback_receipt.json` — independent archive, model, mapping, diagnostic and executed-notebook verification for the returned 05C2 run.
- `development_reliability/` — committed compact 05C2 evidence: mappings, diagnostics, receipts, histories, input index, checks, manifest and figures; large model/NPZ artifacts remain external by hash.
- `canary.py` — guarded reconstruction/score canary and frozen PatchErrorNet architecture.
- `development_generation.py` — resumable compact development-data shard generator.
- `reliability_training.py` — development-only PatchErrorNet ensemble fitting, calibration and audited packaging implementation.
- `amendments/0002_stage_05d_execution_clarifications.json` — outcome-blind H2-region, tie, sharding, calibration-use and random-control resolutions.
- `stage_05d_transition.json` — all 11 readiness decisions and the explicit exact-code authorization.
- `independent_run.py` — sealed, resumable five-shard independent inference implementation.
- `stage_05e_analysis_lock.json` — pre-result lock for H1/H2, resampling, multiplicity and calibration analysis.
- `independent_analysis.py` — one-time five-shard verification, unsealing, statistics and reporting implementation.
- `../../notebooks/05A_Independent_Validation_Protocol_Audit.ipynb` — executed audit notebook.
- `../../notebooks/05C_Independent_Validation_Engineering_Canary.ipynb` — self-contained CUDA canary for DIV2K `0805`–`0806`.
- `../../notebooks/05C1_Development_Reconstruction_Shards.ipynb` — self-contained CUDA worker for shard indices `0`–`11`.
- `../../notebooks/05C2_Development_Reliability_Training_and_Calibration.ipynb` — self-contained CUDA trainer/calibrator with resumable and parallel member support.
- `../../notebooks/05D_Locked_Independent_Evaluation_Shards.ipynb` — self-contained sealed CUDA worker for fixed shard indices `0`–`4`.
- `../../notebooks/05E_One_Time_Locked_Independent_Analysis.ipynb` — precommitted all-shard verification and one-time unsealing notebook.
- `../../notebooks/05F_Locked_Literature_and_Experimental_Synthesis.ipynb` — locked literature/experimental synthesis and final claim-decision notebook.
- `../../results/independent_05e_locked_analysis/` — compact one-time analysis evidence and figures.
- `../../results/independent_05f_locked_synthesis/` — compact final synthesis, claim decisions, literature snapshot and figure.
- `../../docs/stage_05_final_checkpoint.md` — final claim boundary, archive receipts and repository disposition.
- `../../manuscript/manuscript_draft.md` — manuscript-ready evidence-locked draft.
- `../../docs/experiment_05_independent_validation_protocol.md` — human-readable protocol.
- `../../scripts/validate_independent_05_protocol.py` — deterministic structural validator.
- `../../scripts/prepare_independent_05_data.py` — deterministic data-receipt and duplicate-audit utility.
- `../../scripts/validate_independent_05c.py` — data, duplicate-audit, implementation and notebook validator.
- `../../scripts/validate_independent_05c_result.py` — independent raw canary ZIP readback validator.
- `../../scripts/validate_independent_05c_development_shard.py` — outcome-blind validator for every returned development shard.
- `../../scripts/validate_independent_05c2.py` — static notebook, implementation and synthetic calibration validator.
- `../../scripts/validate_independent_05c2_result.py` — independent returned-result and executed-notebook readback validator.
- `../../scripts/validate_independent_05d.py` — transition, runner, shard-map and sealed-notebook validator.
- `../../scripts/validate_independent_05e.py` — pre-result analysis-lock, statistical and unsealing-notebook validator.
- `../../scripts/validate_independent_05f.py` — final directory/ZIP manifest and claim-decision validator.

## Validate

From the repository root:

```bash
python scripts/validate_independent_05_protocol.py
python scripts/validate_independent_05c.py
python scripts/validate_independent_05c_result.py /path/to/returned_canary.zip \
  --expected-outer-sha256 eee0e3b35184e3718a1a9b0503caf572935fe43d65f78865175345dbe463c414
python scripts/validate_independent_05c_development_shard.py /path/to/returned_shard.zip
python scripts/validate_independent_05c2.py
python scripts/validate_independent_05c2_result.py /path/to/returned_05c2.zip \
  --executed-notebook /path/to/executed_05c2.ipynb
python scripts/validate_independent_05d.py
python scripts/validate_independent_05e.py
```

Before Stage 05D execution, both new validators must report `status: pass`, `test_inference_performed: false`, and `test_performance_inspected: false`.

## Next permitted work

Run notebook 05D for shard indices `0`–`4`, in parallel if useful. Return all five sealed ZIPs and at least one executed notebook without opening shard metrics. After all five archives pass independent integrity readback, run the already locked notebook 05E exactly once. Stage 05F will combine the experimental decision with the locked nearest-method literature boundary; neither a successful development screen nor Stage 05D execution alone establishes novelty.
