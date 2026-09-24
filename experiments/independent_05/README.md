# Independent validation 05

## Current state

Stages 05A and 05B are complete: the protocol is frozen and the documented dataset/checkpoint exposure audit passes. The outcome-blind data-receipt portion of stage 05C also passes. The official TESTIMAGES archive matches the publisher SHA-256, all 40 sealed sources decode as RGB 2400 × 2400, and the exhaustive 40 × 96 comparison against the locked DIV2K development pool found zero exact or near-duplicate candidates.

No independent reconstruction has been run, no test performance has been inspected, and the independent run remains unauthorized. The development-only `0805`–`0806` CUDA canary passed in Colab and its returned payload passed independent readback: all 19 manifested files matched, all four prediction bundles were finite and shape-valid, and the quality and risk tables reproduced to numerical precision. Three outcome-blind metadata findings were recorded and corrected for future runs: the random-baseline alias, child-stage provenance, and the repackaged outer ZIP receipt. Development shard 00 of 12 (`0805`–`0812`) has now also passed independent readback: 124 manifested files, 56 records and compact bundles, 336 quality rows, 6,272 risk rows and 1,568 recalculated compact-metric risk rows were verified. Stage 05C remains incomplete until the remaining 11 development shards, five-member PatchErrorNet fitting, and calibration fitting pass.

The strict primary cohort is the 40-image TESTIMAGES/SAMPLING 8-bit RGB 2400 × 2400 archive. The audit found no documented exposure in the reviewed pinned FBCNN and DPIR sources. Because checkpoint-level image manifests are unavailable, this is not proof of non-exposure.

## Files

- `protocol_freeze.json` — machine-readable scientific and execution authority.
- `dataset_exposure_audit.csv` — training/benchmark exposure evidence and cohort decisions.
- `freeze_receipt.json` — validation result and hashes for the protocol, audit, explanatory document and validator.
- `notebook_verification.json` — executed-notebook and rendered-HTML checks.
- `data_receipt.json` — outcome-blind archive, source, decode and fingerprint receipt.
- `duplicate_audit.csv` — all 3,840 TESTIMAGES × DIV2K exact/pHash/dHash comparisons.
- `stage_05c_status.json` — granular readiness state; test authorization remains false.
- `canary_readback_receipt.json` — independent hash, schema, tensor, calculation and sealed-scope readback evidence.
- `development_shard_registry.json` — append-only register of independently verified development shards.
- `development_shard_00_readback_receipt.json` — archive, manifest, record, compact-array, metric and sealed-scope verification for shard 00.
- `amendments/0001_canary_schema_and_provenance.json` — outcome-blind schema/provenance correction record.
- `notebook_05c_verification.json` — static notebook verification and explicit CUDA execution gap.
- `notebook_05c1_verification.json` — static verification of the 12-shard development generator.
- `canary.py` — guarded reconstruction/score canary and frozen PatchErrorNet architecture.
- `development_generation.py` — resumable compact development-data shard generator.
- `../../notebooks/05A_Independent_Validation_Protocol_Audit.ipynb` — executed audit notebook.
- `../../notebooks/05C_Independent_Validation_Engineering_Canary.ipynb` — self-contained CUDA canary for DIV2K `0805`–`0806`.
- `../../notebooks/05C1_Development_Reconstruction_Shards.ipynb` — self-contained CUDA worker for shard indices `0`–`11`.
- `../../docs/experiment_05_independent_validation_protocol.md` — human-readable protocol.
- `../../scripts/validate_independent_05_protocol.py` — deterministic structural validator.
- `../../scripts/prepare_independent_05_data.py` — deterministic data-receipt and duplicate-audit utility.
- `../../scripts/validate_independent_05c.py` — data, duplicate-audit, implementation and notebook validator.
- `../../scripts/validate_independent_05c_result.py` — independent raw canary ZIP readback validator.
- `../../scripts/validate_independent_05c_development_shard.py` — outcome-blind validator for every returned development shard.

## Validate

From the repository root:

```bash
python scripts/validate_independent_05_protocol.py
python scripts/validate_independent_05c.py
python scripts/validate_independent_05c_result.py /path/to/returned_canary.zip \
  --expected-outer-sha256 eee0e3b35184e3718a1a9b0503caf572935fe43d65f78865175345dbe463c414
python scripts/validate_independent_05c_development_shard.py /path/to/returned_shard.zip
```

The command must report `status: pass`, zero independent performance artifacts, and `independent_run_authorized: false`.

## Next permitted work

Run shard index `1` in `notebooks/05C1_Development_Reconstruction_Shards.ipynb` and return its raw ZIP for independent readback. Shard 00 is verified and must not be rerun unless its source archive changes. After all 12 shards pass, fit the five-member PatchErrorNet ensemble and the frozen source-separated calibration mappings. The verified canary does not need to be rerun because the recorded corrections are schema/provenance-only and every numerical result was independently recomputed.

Do not run TESTIMAGES inference until every readiness requirement passes and a versioned, outcome-blind stage transition explicitly authorizes it.
