# Stage 06 execution checklist

This checklist is operational. A checked box must be backed by a named artifact and SHA-256 entry in the freeze manifest.

## Completed now

- [x] Preserve Stage 05 as immutable sealed evidence.
- [x] Recover and verify Stage 05C1 calibration-shard inputs.
- [x] Reconstruct the frozen Stage 05C2 target patch-for-patch.
- [x] Run development-only sensitivity at RMSE thresholds 0.02, 0.03, and 0.05.
- [x] Extend sensitivity to 0.015, 0.025, 0.04, 0.075, and 0.10.
- [x] Use source-cluster bootstrap intervals.
- [x] Export figures, tables, summary, and integrity manifest.

## 06B — External source

- [ ] Choose and document a genuinely external dataset.
- [ ] Pin archive URL/version/licence and SHA-256.
- [ ] Produce exact-hash and perceptual-overlap audit.
- [ ] Freeze source-level fit/calibration/pilot/test roles.
- [ ] Document pretrained-model training-overlap risk.

## 06C — Generalisation axes

- [ ] Select and pin a second solver/checkpoint.
- [ ] Implement one alternate acquisition stage.
- [ ] Run development smoke tests across both solver families.
- [ ] Tune only on permitted development sources.
- [ ] Freeze reconstruction and acquisition configurations.

## 06D — Reliability method

- [ ] Keep continuous detail RMSE as primary target.
- [ ] Implement severity thresholds and source-level support tables.
- [ ] Implement forward-consistency, cross-chain disagreement, and solver-uncertainty features.
- [ ] Train the chain-aware score on development fit only.
- [ ] Calibrate on source-disjoint development calibration only.
- [ ] Run constant, image-only, residual-only, and strong trained comparators.
- [ ] Run component ablations and leave-one-chain-out evaluation.

## 06E — Freeze

- [ ] State primary/secondary hypotheses and multiplicity rule.
- [ ] Select operational threshold from decision meaning, not favourable significance.
- [ ] Perform source-level sample-size calculation.
- [ ] Define the event-support non-estimability rule.
- [ ] Freeze environment, seeds, source IDs, checkpoints, scripts, and output schema.
- [ ] Generate timestamped SHA-256 freeze receipt.

## 06F — Independent run

- [ ] Mount only the sealed test archive and frozen bundle.
- [ ] Execute once without outcome-guided changes.
- [ ] Seal and hash raw outputs before inspection.
- [ ] Verify file manifest and execution receipt.
- [ ] Report unsupported endpoints as non-estimable.

## 06G — Paper

- [ ] Update abstract and claims only after gates are known.
- [ ] Separate confirmatory and exploratory results.
- [ ] Include all negative, failed, and non-estimable findings.
- [ ] Add external-data, solver-transfer, alternate-chain, and reliability tables.
- [ ] Archive the exact paper-to-result provenance map.

