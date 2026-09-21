# Independent validation 05

## Current state

Stages 05A and 05B are complete: the protocol is frozen and the documented dataset/checkpoint exposure audit passes. No independent image has been processed, no test performance has been inspected, and the independent run remains unauthorized.

The strict primary cohort is the 40-image TESTIMAGES/SAMPLING 8-bit RGB 2400 × 2400 archive. The audit found no documented exposure in the reviewed pinned FBCNN and DPIR sources. Because checkpoint-level image manifests are unavailable, this is not proof of non-exposure.

## Files

- `protocol_freeze.json` — machine-readable scientific and execution authority.
- `dataset_exposure_audit.csv` — training/benchmark exposure evidence and cohort decisions.
- `freeze_receipt.json` — validation result and hashes for the protocol, audit, explanatory document and validator.
- `notebook_verification.json` — executed-notebook and rendered-HTML checks.
- `../../notebooks/05A_Independent_Validation_Protocol_Audit.ipynb` — executed audit notebook.
- `../../docs/experiment_05_independent_validation_protocol.md` — human-readable protocol.
- `../../scripts/validate_independent_05_protocol.py` — deterministic structural validator.

## Validate

From the repository root:

```bash
python scripts/validate_independent_05_protocol.py
```

The command must report `status: pass`, zero independent performance artifacts, and `independent_run_authorized: false`.

## Next permitted work

Stage 05C may acquire and hash the named TESTIMAGES archive, complete decode and duplicate checks, implement the locked experiment runner and PatchErrorNet comparator, fit the frozen calibration mappings, and run an engineering canary on DIV2K sources `0805`–`0806` only.

Do not run TESTIMAGES inference until every readiness requirement passes and a versioned, outcome-blind stage transition explicitly authorizes it.
