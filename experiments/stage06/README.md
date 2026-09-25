# Stage 06 — External transport and chain-aware reliability

Stage 06 is a new study. It does not reopen Stage 05.

## Components

| Component | Purpose | Status |
| --- | --- | --- |
| 06A | Development-only event-threshold sensitivity | Executed |
| 06B | External-source provenance and overlap audit | Protocol ready; dataset not yet frozen |
| 06C | Second solver and alternate acquisition-chain development | Protocol ready; configurations not yet frozen |
| 06D | Continuous/severity calibration and chain-aware reliability score | Interface specified; training not yet run |
| 06E | Preregistration and cryptographic freeze | Template ready; blocked on 06B–06D |
| 06F | One-time sealed independent evaluation | Not run |
| 06G | Manuscript synthesis | Not run |

## Non-negotiable boundary

- Stage 05's H1, H2, and non-estimable binary calibration result remain unchanged.
- Stage 06A may explain why the endpoint lacked independent support, but cannot relabel the independent outcome.
- All Stage 06 test sources are sealed until the protocol, models, thresholds, source roles, and code are frozen.
- The source—not the patch—is the splitting and inferential unit.

## Current entry point

Run `notebooks/06A_Development_Event_Threshold_Sensitivity.ipynb`. In Colab, mount Drive and leave the archive directory field blank if the Stage 05C1 shard ZIPs are in the project's `results/` folder. Locally, set the archive directory to a folder containing development shards 08–11 and the exact Stage 05C2 reliability bundle.

Expected outputs are in `results/stage06a_development_threshold_sensitivity/`.

## Before Stage 06F

Complete `docs/stage_06_execution_checklist.md`, fill `freeze_spec.template.json`, and run:

```bash
python scripts/validate_stage06_freeze.py path/to/freeze_spec.json
```

The validator checks required declarations, source-role disjointness, artifact sizes, and SHA-256 hashes. Passing validation is necessary but does not itself authorise unsealing; the timestamped freeze receipt must also be archived.

