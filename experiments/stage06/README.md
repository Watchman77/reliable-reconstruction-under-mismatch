# Stage 06 — External transport and chain-aware reliability

Stage 06 is a new study. It does not reopen Stage 05.

## Components

| Component | Purpose | Status |
| --- | --- | --- |
| 06A | Development-only event-threshold sensitivity | Executed |
| 06B | External-source provenance and overlap audit | 1,000 NEFs checked; 994-source eligibility v1 recorded; source-identity audit complete, final access/lineage decision pending |
| 06C | Second solver and alternate acquisition-chain development | Development work may proceed on eligible fit/early-stop sources; configurations not yet frozen |
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

Stage 06A is executed and the RAISE-1k source-identity audit is complete. Proceed with Stage 06C engineering and smoke tests on eligible development fit/early-stop sources using the versioned allowlist. Record any required publisher access details and actual checkpoint provenance before the Stage 06E freeze. Unresolved image-level checkpoint training overlap is a documented limitation to adjudicate before confirmatory claims, not a reason to stop development-only work or to reopen Stage 05.

## Active research order

1. **06C — Generalisation axes:** pin and smoke-test DiffPIR on eligible development fit/early-stop sources; implement and smoke-test the alternate linear-light camera-response chain. Record the actual renderer, source IDs, checkpoint and settings.
2. **06D — New reliability method:** generate development features; fit the chain-aware continuous-detail score and strong chain-agnostic controls; use source-disjoint early-stop and calibration roles.
3. **06E — Freeze:** calculate independent source count and event support, decide the operational threshold and remaining provenance risk, then hash all models, code, roles and analysis rules.
4. **06F — Independent run:** open the sealed sources once under the frozen bundle; report all supported and non-estimable outcomes.
5. **06G — Manuscript synthesis:** revise the unified manuscript against those locked results. The current Stage 05 manuscript is a baseline draft, not a place to prewrite Stage 06 claims. Keep development diagnostics in their research records until this stage.

If a later chat resumes this project, follow this order and the latest execution receipts. Do not return to a checkpoint-provenance discussion as a stand-alone project or advance manuscript claims before the novelty experiments are complete.

## External-source audit

Start with `notebooks/06B_RAISE_1k_Manifest_and_Resumable_Download.ipynb`. Place the official `RAISE_1k.csv.zip` manifest in `inputs/RAISE-1k/`, select one `SHARD_INDEX` from 0 through 19, and run the notebook. It downloads only NEF originals, resumes partial files, verifies server-reported byte counts, and writes one receipt per 50-source shard. Different Colab sessions may run different shard indices concurrently.

The frozen metadata-only allocation is stored at `experiments/stage06/manifests/RAISE_1k_source_roles_seed_20260925.csv`. It contains 500 development-fit, 150 development-early-stop, 150 development-calibration, 50 external-pilot, and 150 independent-test sources. Do not change these roles after reconstruction outcomes are generated.

Create a CSV with `source_id`, `relative_path`, and `role`, with every role represented, then run:

```bash
python scripts/audit_stage06_external_dataset.py \
  --candidate-dir /path/to/images \
  --roles-csv /path/to/source_roles.csv \
  --reference-manifest /path/to/stage05_source_manifest.csv \
  --output-dir results/stage06b_external_audit
```

The audit fails closed on exact or perceptual-overlap candidates. Perceptual candidates still require manual paired-image review. Camera RAW inputs require `rawpy`; its version and rendering settings must be frozen.

The executed RAISE-1k audit verified 1,000 NEF SHA-256 digests and RAW decodes. Its 14 overlap rows represent six byte-identical source pairs counted twice (file and decoded RGB) and two visually reviewed false-positive dHash candidates. No RAISE-versus-Stage 05 match was reported by the hash screen. See `docs/stage_06b_raise_integrity_and_overlap_review_2026-09-25.md` and the eight-pair decision ledger. The original 1,000-row role file remains untouched; `experiments/stage06/manifests/RAISE_1k_eligible_roles_v1_20260925.csv` is the source allowlist for later development, pilot, and eventual sealed test loaders. It has 994 rows: fit 495, early-stop 150, calibration 149, pilot 50, independent test 150. The companion receipt pins evidence/manifest hashes; `scripts/build_stage06b_eligibility.py` reproduces and validates it from the stored audit CSVs. Loaders must fail on any source outside the allowlist. The source-integrity audit is complete. Publisher access/retrieval documentation and the actual second checkpoint's provenance still require a recorded decision before the Stage 06E freeze; image-level absence from all pretrained training sets cannot be assumed. Development-only 06C work may proceed while these records are completed. The independent test remains sealed.

## Reliability development and external pilot

Prepare one row per patch with source role, observed detail RMSE, chain-aware features, and image-only comparator features. For example:

```bash
python scripts/fit_stage06_reliability.py \
  --table results/stage06d_features.csv \
  --eligible-source-manifest experiments/stage06/manifests/RAISE_1k_eligible_roles_v1_20260925.csv \
  --chain-aware-features forward_consistency_residual,cross_chain_disagreement,solver_uncertainty \
  --image-only-features image_texture,image_contrast,solver_uncertainty \
  --forward-residual-feature forward_consistency_residual \
  --evaluation-role external_pilot \
  --output-dir results/stage06d_reliability
```

The runner rejects sources outside the hashed 994-source eligible manifest and role changes. Pilot input tables must omit independent-test rows entirely. It selects hyperparameters on source-disjoint early-stop data, fits on development fit plus early-stop data, calibrates only on development calibration data, and evaluates on the external pilot. Independent evaluation is blocked unless the explicit post-freeze flag is supplied.

## Before Stage 06F

Complete `docs/stage_06_execution_checklist.md`, fill `freeze_spec.template.json`, and run:

```bash
python scripts/validate_stage06_freeze.py path/to/freeze_spec.json
```

The validator checks required declarations, source-role disjointness, artifact sizes, and SHA-256 hashes. Passing validation is necessary but does not itself authorise unsealing; the timestamped freeze receipt must also be archived.
