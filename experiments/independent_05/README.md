# Independent validation 05

## Current state

Stages 05A and 05B are complete: the protocol is frozen and the documented dataset/checkpoint exposure audit passes. The outcome-blind data-receipt portion of stage 05C also passes. The official TESTIMAGES archive matches the publisher SHA-256, all 40 sealed sources decode as RGB 2400 × 2400, and the exhaustive 40 × 96 comparison against the locked DIV2K development pool found zero exact or near-duplicate candidates.

No independent reconstruction has been run, no test performance has been inspected, and the independent run remains unauthorized. The guarded canary implementation and self-contained CUDA notebook are prepared and pass static validation. The notebook has not been executed because the preparation workspace has neither PyTorch nor CUDA. Stage 05C is not complete until the development-only `0805`–`0806` GPU canary, comparator fitting, and calibration fitting pass.

The strict primary cohort is the 40-image TESTIMAGES/SAMPLING 8-bit RGB 2400 × 2400 archive. The audit found no documented exposure in the reviewed pinned FBCNN and DPIR sources. Because checkpoint-level image manifests are unavailable, this is not proof of non-exposure.

## Files

- `protocol_freeze.json` — machine-readable scientific and execution authority.
- `dataset_exposure_audit.csv` — training/benchmark exposure evidence and cohort decisions.
- `freeze_receipt.json` — validation result and hashes for the protocol, audit, explanatory document and validator.
- `notebook_verification.json` — executed-notebook and rendered-HTML checks.
- `data_receipt.json` — outcome-blind archive, source, decode and fingerprint receipt.
- `duplicate_audit.csv` — all 3,840 TESTIMAGES × DIV2K exact/pHash/dHash comparisons.
- `stage_05c_status.json` — granular readiness state; test authorization remains false.
- `notebook_05c_verification.json` — static notebook verification and explicit CUDA execution gap.
- `canary.py` — guarded reconstruction/score canary and frozen PatchErrorNet architecture.
- `../../notebooks/05A_Independent_Validation_Protocol_Audit.ipynb` — executed audit notebook.
- `../../notebooks/05C_Independent_Validation_Engineering_Canary.ipynb` — self-contained CUDA canary for DIV2K `0805`–`0806`.
- `../../docs/experiment_05_independent_validation_protocol.md` — human-readable protocol.
- `../../scripts/validate_independent_05_protocol.py` — deterministic structural validator.
- `../../scripts/prepare_independent_05_data.py` — deterministic data-receipt and duplicate-audit utility.
- `../../scripts/validate_independent_05c.py` — data, duplicate-audit, implementation and notebook validator.

## Validate

From the repository root:

```bash
python scripts/validate_independent_05_protocol.py
python scripts/validate_independent_05c.py
```

The command must report `status: pass`, zero independent performance artifacts, and `independent_run_authorized: false`.

## Next permitted work

Run `notebooks/05C_Independent_Validation_Engineering_Canary.ipynb` in a CUDA Colab runtime and return the raw canary ZIP for independent readback. After a verified canary pass, continue stage 05C with full development reconstruction generation, five-member PatchErrorNet fitting, and the frozen source-separated calibration mappings.

Do not run TESTIMAGES inference until every readiness requirement passes and a versioned, outcome-blind stage transition explicitly authorizes it.
