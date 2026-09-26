# Stage 06E freeze preparation — evidence review

Status: **reviewed development evidence; freeze NOT issued; independent test sealed**.
The Stage 06D evidence bundle was supplied on 26 September 2026. This record
does not authorize independent evaluation or change Stage 05 or the manuscript.

## Verified from the supplied bundle

- The 994-row eligible RAISE manifest has SHA-256
  `a989e066ab5c66bec753719b3a3006c15a0635504f63977750a9192aa2995426`.
  Roles: fit 495, early-stop 150, calibration 149, pilot 50, independent 150.
- The model receipt records 142,560 fit patch rows, 43,200 early-stop rows,
  42,912 calibration rows and 14,400 pilot rows; independent rows: **zero**.
  It records fit=development_fit, selection=development_early_stop,
  calibration=development_calibration, model family=gradient boosting,
  thresholds RMSE 0.0075 and 0.01, independent evaluation disabled.
- All eight files physically included in the evidence ZIP matched the supplied
  inventory's byte counts and SHA-256 digests. The prediction table contains
  14,400 rows from exactly 50 distinct sources, each assigned `external_pilot`
  in the eligible manifest. No independent source appears in that table.
- Source-level mean absolute error: chain-aware 0.001972382256 versus
  residual-only 0.002416955180 (18.4% relative reduction, rounded).
  The paired mean improvement was 0.000444572924, on 37 of 50 sources.
  Recomputed source-cluster bootstrap with seed 20260926 and 20,000 resamples:
  95% percentile interval [0.00024858, 0.00065004]. This is **exploratory**:
  the pilot pool was inspected during model development.
- Patch RMSE: 0.002796587253 chain-aware versus 0.003364524312 residual-only;
  Brier 0.1387682171 versus 0.1538246706 at 0.0075, and
  0.08712251023 versus 0.1070489018 at 0.01. Calibration positives occurred
  on 129/149 linear and 128/149 sRGB sources at 0.0075; at 0.01 on 98/149
  and 93/149 respectively. These are *source-support counts*, not independent
  evidence of transport or proof of calibrated probabilities.

## Artifact provenance

The supplied inventory records, but does not include the bytes of:

| Artifact | Bytes | Recorded SHA-256 |
| --- | ---: | --- |
| Full development feature table | 37,456,420 | `ecfb74add9a57162f48ce5de860ad2741112bb01489c9cffc4e53e39bbaaecdd` |
| Development plus pilot feature table | 39,759,408 | `c4130f1423f4e19f9aa6b4cd8da883760d2aaa56570523c9f914f550d31cb7aa` |
| Fitted models (`joblib`) | 1,413,853 | `8b67ba7f3775254c2ab47b1a4a1c36b92554f17783abf60c6aa9612d9a3458fd` |

The fitted model's bytes have **not** been independently checked here; the
reported hash and size must be reverified in the environment used for freezing.
The supplied `export_manifest.json` has SHA-256
`a77876cf414bc2f75675beca96768fee38d78eca20168a510988b023b570981f`.
The checked training receipt has SHA-256
`78be676a83655e02688a82a6476b5d05ee944c1fc789c59384283b5c32f4463b`.

## Required before a valid Stage 06E freeze

1. **Complete provenance:** archive the publisher access/licence/retrieval
   record. Document the actual DRUNet and FBCNN checkpoint training overlap
   investigation, its limits, and an explicit go/no-go decision about unresolved
   image-level overlap. The gradient inverse uses no learned checkpoint.
2. **Resolve protocol/template drift:** the current template still lists
   0.03/0.05/0.075 and a diffusion second checkpoint. Specify gradient inverse
   (strength 0.01) as the second solver, correct the feature names and thresholds,
   and declare which of 0.0075 or 0.01 has operational meaning as the primary
   event endpoint. Retain continuous detail RMSE as the primary prediction
   target and source-macro MAE as the primary comparison metric. Predeclare
   multiplicity and the non-estimability rule.
3. **Finish planned validation:** run the required leave-one-chain-out analysis
   on permitted development material; document all ablations and unfavorable
   outcomes. Calculate a source-level precision/sample-size rationale for the
   already allocated 150 independent sources. Do not choose hypotheses from
   the inspected pilot results.
4. **Freeze executable artifacts:** record repo commit, software versions,
   acquisition renderer, seeds, source IDs, checkpoint weights, scripts,
   preprocessing configuration, feature schema, fitted model bytes and their
   verified hashes. Ensure the eventual independent loader consumes the exact
   frozen model/configuration, rejects all other source IDs, and cannot fit or
   tune on the independent partition. The current development feature runner
   expressly rejects independent sources and is not a 06F runner.
5. **Validate and archive:** assemble the actual freeze bundle, run
   `scripts/validate_stage06_freeze.py` on it, archive a dated receipt and
   inspect it before any one-time independent evaluation. The validator checks
   declared fields and file hashes; a passing validator alone does not resolve
   the scientific provenance and protocol gates above.

This document is a preparation record, **not** the freeze specification.
