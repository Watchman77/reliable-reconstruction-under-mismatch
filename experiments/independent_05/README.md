# Independent validation 05

## Current state

Stages 05A–05C are complete: the protocol is frozen, the documented dataset/checkpoint exposure audit passes, the data receipt is complete, and the development comparator/calibration result passed independent readback. The official TESTIMAGES archive matches the publisher SHA-256, all 40 sealed sources decode as RGB 2400 × 2400, and the exhaustive 40 × 96 comparison against the locked DIV2K development pool found zero exact or near-duplicate candidates.

No independent reconstruction has yet been run and no test performance has been inspected. The development-only `0805`–`0806` CUDA canary and all 12 development shards (`0805`–`0900`) passed independent readback, covering 96 sources and 672 observations. Container-repackaging findings remain recorded, while every scientific payload was accepted only after complete internal-manifest verification.

The returned 05C2 CUDA result has 27 exactly matching manifested files, five internally consistent PatchErrorNet members, disjoint 52/12/32 source partitions, and 11 source-equal-weighted isotonic mappings fitted only on DIV2K `0869`–`0900`. The 229,376-row calibration diagnostics reproduce to a maximum absolute difference of \(1.74 \times 10^{-17}\). These remain development-fit diagnostics, not independent calibration evidence.

The outcome-blind Stage-05D readiness audit now passes all 11 frozen requirements. Amendment 0002 resolves only pre-outcome execution details: H2 uses the full evaluation region, score ties use ascending patch index, and the 40 sources are split lexicographically into five fixed shards of eight. The versioned transition explicitly authorizes the exact hashed runner. The self-contained 05D notebook writes sealed, resumable shard evidence and never displays performance. The one-time 05E analysis—including H1/H2 formulas, bootstrap, sign-flip tests, Holm correction and calibration conventions—was also hash-locked before any Stage-05D output existed. Test inference is authorized, but remains unperformed; test performance remains unseen.

The strict primary cohort is the 40-image TESTIMAGES/SAMPLING 8-bit RGB 2400 × 2400 archive. The audit found no documented exposure in the reviewed pinned FBCNN and DPIR sources. Because checkpoint-level image manifests are unavailable, this is not proof of non-exposure.

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
