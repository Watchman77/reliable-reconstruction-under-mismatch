# Stage 06 — Novelty-strengthening protocol

Status: development protocol, to be frozen before any new independent outcome is inspected.

## 1. Purpose and boundary

Stage 06 tests whether acquisition-chain mismatch is a reproducible, transportable cause of reconstruction failure and whether chain-aware reliability modelling can identify that failure better than strong chain-agnostic controls.

Stage 05 remains immutable. Its sealed conclusions are:

- H1 passed: codec restoration before nominal DPIR substantially improved the locked detail-error endpoint.
- H2 produced a statistically detectable 4.464% reduction in operator spread but missed its locked 5% practical gate by 0.536 percentage points.
- The locked independent cohort contained no positive events for the binary endpoint `centre-patch detail RMSE > 0.05`, so positive-event calibration was not estimable.

Nothing in Stage 06 relabels, retunes, reruns, or replaces those conclusions.

## 2. Stage 06A result: what threshold sensitivity actually showed

The retrospective analysis is restricted to the 32 held-out development-calibration sources (DIV2K source IDs 0869–0900) and 229,376 patch rows. Uncertainty is estimated by resampling sources, not individual patches.

| RMSE threshold | Positive patches | Patch prevalence | 95% source-bootstrap interval | Sources with positives |
| ---: | ---: | ---: | ---: | ---: |
| 0.020 | 137,231 | 59.83% | 49.99%–69.26% | 32/32 |
| 0.030 | 99,778 | 43.50% | 33.34%–53.56% | 32/32 |
| 0.050 | 50,824 | 22.16% | 14.83%–29.81% | 32/32 |
| 0.075 | 13,555 | 5.91% | 3.41%–8.80% | 27/32 |
| 0.100 | 2,605 | 1.14% | 0.42%–2.10% | 20/32 |

Interpretation: the 0.05 endpoint had substantial development support and was not an obviously unsupported threshold. The zero-event independent result therefore diagnoses an event-support/transport shift. Lowering the threshold after seeing the independent labels would be post-test outcome redefinition and is prohibited. The 0.02 and 0.03 results are useful sensitivity evidence, but their high prevalences also show why a lower threshold is not automatically a better operational definition.

## 3. Seven novelty-strengthening components

### 3.1 External validation on a genuinely separate image source

Use a public image cohort that is disjoint from all development sources and, as far as documented, from the training data of each learned component. DIV2K cannot serve this role because it already supplied development data and may overlap the training provenance of pretrained reconstruction components.

Required pre-analysis checks:

1. record dataset release, licence, download URL, archive hash, and file-level hashes;
2. audit exact and perceptual duplicates against all Stage 05 development/test sources;
3. document camera/source diversity and any resizing or colour conversions;
4. assign sources—not patches—to development, calibration, and independent roles;
5. freeze all source IDs and exclusions before outcome inspection.

Primary external-validation estimand: the difference in reconstruction detail error between a nominal reconstruction chain and its acquisition-aware counterpart, aggregated first within source and then across sources.

### 3.2 Second inverse solver or reconstruction prior

Replicate the acquisition-awareness comparison with a second solver family whose prior and optimisation mechanism differ materially from DPIR. The purpose is not to find the strongest model after testing; it is to evaluate whether the mismatch effect survives a change of reconstruction prior.

Design requirements:

- predeclare one primary second solver and one frozen checkpoint;
- match the forward operator, input scaling, crop, and evaluation code across solvers;
- tune solver-specific nuisance parameters only on development sources;
- report both absolute performance and acquisition-aware minus nominal paired differences;
- retain failed or unstable runs in the audit log.

### 3.3 Alternate acquisition-chain perturbation

Add at least one omitted but plausible acquisition stage, selected before the new test is opened. Candidate stages include resampling/downsampling, demosaicing, tone/gamma mapping, clipping, or a second codec implementation. The selected stage must be parameterised on development data and applied identically across solver families.

This tests the broader mechanism: inversion fails when the assumed forward operator omits a consequential acquisition transformation. It should not be framed as a JPEG-only effect.

### 3.4 Continuous and severity-stratified reliability targets

The primary reliability outcome will be continuous centre-patch detail RMSE. Binary events become secondary operating points.

Required reporting:

- continuous calibration: predicted versus observed RMSE with source-clustered uncertainty;
- proper scores for predictive distributions or quantiles where available;
- severity-stratified exceedance at frozen thresholds, provisionally 0.03, 0.05, and 0.075;
- source-level coverage, not just pooled patch-level coverage;
- distribution-shift diagnostics for outcome support and score support.

The threshold set is provisional until Stage 06 development work is frozen. One threshold may be designated as the primary operational event only if it has a stated decision interpretation; event frequency alone is insufficient.

### 3.5 Development-selected, frozen operational threshold

Threshold selection is a decision problem, not a search for the most favourable p-value. Before the new independent run, define:

- the harm or intervention represented by an event;
- the acceptable false-alert/false-reassurance trade-off;
- the development and external-pilot data permitted for selection;
- the chosen threshold and all secondary sensitivity thresholds;
- the exact analysis code and cryptographic hashes.

After freezing, the threshold cannot change in response to independent outcomes. If independent event support is inadequate, the binary endpoint is reported as non-estimable while continuous and severity analyses remain valid.

### 3.6 New, adequately supported independent cohort

The new cohort must be source-disjoint and kept sealed until the entire Stage 06 bundle is frozen. Sample size is determined at the source level and must consider both effect precision and event support.

Minimum gates before unsealing:

- a documented source-level sample-size calculation;
- conservative expected event prevalence from development plus external pilot data;
- enough independent sources to estimate between-source variability;
- an event-support contingency that declares calibration non-estimable without changing the endpoint;
- all models, thresholds, exclusions, random seeds, and scripts hashed and frozen.

No independent labels or performance summaries may be inspected while choosing models, chains, thresholds, or exclusions.

### 3.7 New chain-aware reliability score

Develop a reliability score that explicitly conditions on acquisition-chain evidence rather than only on the reconstructed image. A concrete candidate is a cross-chain disagreement-and-residual score:

\[
S(x)=\alpha\,R_{\mathrm{forward}}(x)+\beta\,D_{\mathrm{chain}}(x)+\gamma\,U_{\mathrm{solver}}(x),
\]

where `R_forward` measures consistency after reapplying the hypothesised acquisition operator, `D_chain` measures disagreement among reconstructions under plausible chains, and `U_solver` is a frozen solver-uncertainty feature. Coefficients are learned only on development fit data and calibrated on source-disjoint development calibration data.

Required comparators:

- a constant/base-rate predictor;
- image-only error or confidence proxies;
- solver residual alone;
- a strong trained uncertainty model with no chain features;
- ablations removing each term from the proposed score.

Primary reliability comparison: source-clustered difference in a continuous proper score or absolute calibration error. Binary AUROC is descriptive only when both classes are supported and cannot substitute for calibration.

## 4. Frozen analysis hierarchy

### Confirmatory primary questions

1. Does acquisition-aware reconstruction improve source-level detail RMSE on an external dataset?
2. Does the effect replicate under the second solver family?
3. Does the chain-aware reliability score improve a predeclared continuous calibration score over the strongest chain-agnostic comparator?

### Confirmatory secondary questions

1. Does the mismatch effect appear for the alternate acquisition stage?
2. Is calibration stable across severity thresholds and acquisition chains?
3. Does the chain-aware score retain advantage under leave-one-chain-out evaluation?

### Exploratory analyses

- interactions between chain severity and solver family;
- source-content subgroup effects;
- alternative thresholds not frozen as operating points;
- diagnostic visualisations and failure-case taxonomy.

Exploratory results are labelled as such regardless of statistical strength.

## 5. Data separation

| Partition | Permitted uses | Prohibited uses |
| --- | --- | --- |
| Development fit | train score/model; tune solver nuisance parameters | final performance claim |
| Development early-stop | checkpoint/epoch selection | threshold optimisation after test |
| Development calibration | calibrate predictions; select/freeze operational threshold | model refitting after freeze |
| External pilot | check transport and conservative event support without entering final test | final confirmatory estimate |
| Independent test | one locked evaluation | any tuning, relabelling, or exclusion chosen from outcomes |

Splits are by source. Patches from one source never cross roles.

## 6. Statistical rules

- The source is the resampling and inferential unit; patch rows are nested observations.
- Report paired source-level effects with 95% confidence intervals and the complete source distribution.
- Multiplicity: three primary confirmatory questions use a predeclared familywise or hierarchical procedure; all other p-values are descriptive unless separately controlled.
- Report effect sizes regardless of gate outcomes.
- Missing or unsupported outcomes are labelled non-estimable, never silently removed.
- Thresholded analyses always accompany the continuous outcome.
- All exclusions and failed runs appear in a machine-readable ledger.

## 7. Freeze and integrity procedure

Before the independent run, export a freeze bundle containing:

1. protocol and hypotheses;
2. source-role manifest and overlap audit;
3. model/checkpoint identifiers;
4. acquisition-chain definitions;
5. thresholds and calibration mappings;
6. executable notebooks/scripts and environment lock;
7. expected output schema;
8. file sizes and SHA-256 hashes;
9. a timestamped freeze receipt.

Independent results are written to a new directory, sealed into an archive, hashed, and inspected only after integrity checks pass. Corrections to software bugs require a public deviation note that states whether outcomes had already been seen.

## 8. Execution sequence and stop rules

| Stage | Deliverable | Gate to continue |
| --- | --- | --- |
| 06A | development threshold-sensitivity notebook | executed, audited, Stage 05 boundary explicit |
| 06B | external-data manifest and overlap audit | licence, hashes, source roles, no disallowed overlap |
| 06C | second-solver and alternate-chain development results | frozen configurations and successful smoke tests |
| 06D | continuous/severity reliability model and controls | source-disjoint calibration, ablations complete |
| 06E | preregistration/freeze bundle | all hashes and sample-size/event-support calculations complete |
| 06F | sealed independent execution | no tuning; archive and manifest verified |
| 06G | manuscript synthesis | claims match gates; exploratory/confirmatory labels preserved |

Stop rather than unseal if dataset provenance is ambiguous, source overlap is detected, required model checkpoints cannot be pinned, the analysis bundle is not reproducible, or the cohort cannot meet the source-level design requirement.

## 9. Defensible novelty claim if all gates pass

The intended contribution is not “a better threshold.” It is evidence that acquisition-chain mismatch is a reproducible and solver-transferable failure mode, together with a chain-aware, continuously evaluated reliability method that detects or quantifies the resulting risk under external shift. The final wording must be reduced if any primary gate fails.

