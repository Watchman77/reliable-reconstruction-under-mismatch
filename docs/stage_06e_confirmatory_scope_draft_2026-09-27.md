# Stage 06E confirmatory scope — draft, not frozen

This draft translates the development evidence into a pre-test decision rule.
It does **not** authorize evaluation of the 150 independent RAISE sources.
The model was chosen after inspecting both external-pilot batches; their
reported intervals are exploratory.

## Population and claim

The confirmatory population is the 150 audited independent RAISE sources under
the **two acquisition chains represented during training**, `srgb_j75_b16_n2`
and `linear_j75_b16_n2`. Each source produces both chains. The experimental
unit is the source; patches are nested observations. No claim is proposed for
transport to an unseen acquisition chain. A development leave-one-chain-out
check was strongly adverse in the sRGB-to-linear direction and must appear
in any eventual report, regardless of the independent outcome.

## Primary reliability endpoint

The frozen gradient-boosting chain-aware score predicts DPIR reconstruction
patch detail RMSE from `forward_consistency_residual`,
`cross_chain_disagreement`, and `solver_uncertainty`. Its source-disjoint
comparator is the frozen residual-only ridge model. For source *i*, average
absolute prediction error first over all its 288 patches (both chains), then
calculate `gain_i = MAE_residual,i - MAE_chain_aware,i`. The primary estimand
is the mean of `gain_i` over the 150 independent sources. Positive means the
proposed score is better. Use a prespecified source-cluster bootstrap
(20,000 resamples, seed to be frozen) for the two-sided 95% percentile
interval. The primary success criterion is a strictly positive lower bound.
Report the signed effect, interval and 150 source-level paired values even
if the criterion fails. As a robustness diagnostic, also report source-level
MAE by chain; no chain-specific result can rescue a failed pooled primary
criterion.

This is one confirmatory reliability test. Patch RMSE, severity-event Brier
scores at RMSE 0.0075 and 0.01, calibration curves, ablations, reconstruction
gain versus nominal settings, and second-solver comparisons are secondary
and descriptive unless separately predeclared with a multiplicity rule before
test access. Do not call either severity threshold a universal operational
failure standard. If the independent cohort provides no positive or no
negative events at a threshold, mark its binary calibration endpoint
non-estimable and retain the continuous endpoint and complete support table.

## Partitions, planning and adaptation

The pinned 994-source manifest allocates 495 fit, 150 early-stop, 149
calibration, 50 external-pilot, and 150 independent-test sources. Final model
parameters were fit on development_fit only; the early-stop role selected
hyperparameters and the calibration role fit isotonic mappings. The already
inspected external pilot must not participate in fitting or rule changes.
Its paired-difference SD was 0.0007290. If that SD transports, 150 sources
give an approximate normal 95% precision half-width of 0.0001167. This is an
illustrative precision calculation, **not** a guaranteed power calculation:
the pilot was inspected adaptively and the independent variance may differ.

## Gating fields still open

- Publisher retrieval date, accepted RAISE access terms and nonredistribution
  record, with the official manifest and audit digests.
- Documented DRUNet and FBCNN checkpoint training-source overlap assessment
  and a signed go/no-go statement on residual image-level overlap risk.
- Hash-verification in the Colab/Drive environment of the actual saved fitted
  model (recorded SHA-256 `8b67ba7f3775254c2ab47b1a4a1c36b92554f17783abf60c6aa9612d9a3458fd`),
  feature table, source allocation, checkpoint weights and runnable code.
- Frozen source-count/bootstrapping seed, runtime versions, model loading
  instructions and a fail-closed independent-only inference runner that loads
  the fitted model without fitting, tuning or recalibrating it.
- Actual Stage 06E freeze specification and successful validation receipt.

No independent test image or outcome may be read to resolve these fields.
