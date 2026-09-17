# Pilot specification: operator-sensitive selective reconstruction

**Version:** 0.1, 16 September 2026

**Status:** executable design brief; not yet registered, implemented or experimentally validated.

**Evidence basis:** [provisional synthesis 01](../literature/synthesis/provisional_gap_synthesis_01.md). The umbrella topic and protocol v0.4 remain unchanged.

## Decision this pilot should support

Determine whether operator-sensitive information adds useful prediction of reconstruction error beyond image-only uncertainty and measurement residuals. Begin with still images and frozen reconstruction methods. A positive result motivates a mechanism study; it does not establish a new journal architecture or a universal reliability guarantee.

## Information available to the method

The method receives an observed image `y`, a nominal acquisition family, and any explicitly declared calibration metadata. It does not receive the clean test image, true degradation parameters, corruption regime label, or a correct codec label unless those are supplied equally to every compared method in that experiment.

Use the conceptual model

\[
y=F_*(x)+n,\qquad \hat F_\theta\in\mathcal F.
\]

Here additive noise is an initial controlled case. The compound simulator will place sensor noise and quantization at their declared positions in the acquisition chain, rather than treating JPEG or clipping as additive Gaussian noise. Log boundary handling, kernel centering, colour/linearization, resampling and codec order. Do not compare physical residuals from incompatible units or different forward maps as though they were the same score.

## Data separation

- Preserve source-image identities. Every crop, degradation and random seed derived from one source stays in the same partition.
- For a first natural-image pilot, target at least 100 unique calibration sources and a separate 100 unique test sources, plus a disjoint development partition. This is a feasibility scale, not a power calculation or a sufficient sample size for a formal guarantee.
- Choose the public dataset and exact manifest after checking image/weight-domain compatibility and data terms. The existing DIV2K option is suitable for general-image methods; a face-trained sampler needs a declared content-domain control before general-image transfer claims.
- The development set selects models, score features, weights and hyperparameters. The calibration set selects the release threshold. The test set evaluates the frozen choices once.
- Use clean images to score simulated errors and calibrate the initial supervised reliability rule. Deployment scores must depend only on permitted observations and method outputs. This pilot makes no claim of ground-truth-free calibration.
- Treat real paired captures as a later external check with registration/target uncertainty documented. Unpaired CCTV can demonstrate behaviour and failure cases, but cannot validate pixel-truth coverage.

## Acquisition regimes

| Regime | True acquisition | Reconstruction assumption | Purpose |
|---|---|---|---|
| M0 | Spatially invariant blur plus declared Gaussian noise | Same operator family; true parameters supplied only in a separate oracle control | Check operator plumbing and sampling behaviour. |
| M1 | Same family, with perturbed or unknown blur/noise parameters | Nominal family with estimated parameters | Isolate parameter mismatch. Keep a fitted-point and a multiple-operator variant. |
| M2 | Held-out family, e.g. spatially varying blur | Spatially invariant blur family | Test structural misspecification. An unrestricted kernel can represent many defocus/motion shapes, so merely changing a kernel label is not enough. |
| M3 | Blur plus noise plus an omitted JPEG or resampling stage | Family omits the named stage | Test a clearly specified unmodelled process. Freeze its severity range before running. |
| M4 | New combinations of explicitly modelled stages | Full family available, but held-out combinations | Separate composition transfer from a missing physics family. |

Keep source images matched across M0–M4 so content change does not explain acquisition effects. Generate several fixed random realizations per source, but never count them as independent images. The primary pilot comparison is M1 versus M3; M2 is a second structural stress test. Results need not worsen monotonically with a chosen severity label.

Initially calibrate on the declared in-family distribution (M0/M1). Evaluate frozen thresholds on M2/M3 as genuine shifts; do not recalibrate on their test labels. A separately labelled matched-compound calibration experiment may show what extra calibration data buy, but must not be described as unseen-condition performance.

## What is a retained detail?

Use a fixed spatial grid and a fixed linear high-pass transform before examining test outputs. A simple initial target is a 16-by-16 patch of `D x`, where `D x = x - G_1 * x` and `G_1` is a declared Gaussian filter with standard deviation one pixel. Freeze the border crop and colour handling with the manifest.

For region `p`, define

\[
e_p=\sqrt{\operatorname{mean}_{p}\!\left[(D\hat x-Dx)^2\right]},
\qquad b_p=\mathbf 1\{e_p>\tau\}.
\]

An initial engineering tolerance is `tau = 0.05` for images normalized to `[0,1]`; lock or revise it on development data before calibration. Report sensitivity to predeclared tolerances `0.025` and `0.10`. These are experimental error tolerances, not thresholds for forensic use. The release target is the specified high-frequency estimate; it is not every semantic claim about the image.

Let `a_p(t)` equal one when a fixed score passes threshold `t`. Report retained coverage and selective bad-detail rate:

\[
C(t)=\frac{\sum_p a_p(t)}{N},\qquad
R(t)=\frac{\sum_p a_p(t)b_p}{\sum_p a_p(t)}.
\]

Report `R(t)` as undefined if nothing is retained. Never assign zero risk to an empty output. Whole-image PSNR/SSIM remain separate outcomes. Report flat and textured-region strata because a selector can obtain a deceptively favourable average by retaining only easy background. Ground-truth-based strata are evaluation diagnostics, not deployment inputs.

Ground-truth detail error does not by itself prove measurement support. Use separate known-operator ambiguity examples to illustrate when different details fit the same observation. Search-based disagreement provides evidence of ambiguity; failure to find disagreement is not a certificate that ambiguity is absent. This distinction follows the limitations extracted for [P008](https://arxiv.org/html/2012.00646v3) and [P037](https://arxiv.org/html/2605.13146v1).

## Scores and ablations

| Score | Information used | Interpretation and required control |
|---|---|---|
| Residual only | Reprojected reconstruction and observation under the declared nominal map | Measures model fit. Keep the normalization and map identical across compared outputs. |
| Image-only variability | Multiple image reconstructions conditional on a fitted point operator | A heuristic unless valid posterior sampling/calibration is established. Use the same image prior as the candidate. |
| Operator sensitivity only | Change in reconstructed detail across estimated plausible operators | Measures dependence on the assumed operator; a perturbation grid is not automatically a posterior. |
| Combined score | Image variability, operator sensitivity and declared mismatch diagnostics | Fit a small nonnegative linear combination on development data first. Compare with both single-score ablations; avoid introducing a large predictor. |
| Simple fallback/stop baseline | Residual threshold or an available degradation/clean-class score | Compare the decision, not just reconstruction quality. Distinguish adaptations from faithful reproductions of P042/P073. |
| Oracle diagnostics | True operator or clean error for ranking | Evaluation upper references only; unavailable to deployed methods and excluded from practical superiority claims. |

Where approximate nested image/operator samples are available, inspect the familiar decomposition

\[
\operatorname{Var}(\phi_p(x)\mid y)
=\mathbb E_{\theta\mid y}\!\left[\operatorname{Var}(\phi_p(x)\mid\theta,y)\right]
+\operatorname{Var}_{\theta\mid y}\!\left[\mathbb E(\phi_p(x)\mid\theta,y)\right].
\]

This is the law of total variance, not a new theorem or proof that approximate samples are calibrated. The second term motivates testing operator-sensitive information. A small value in both terms can still occur when every operator/sample is wrong. For a deterministic solver, label variation from perturbations as sensitivity or resampling stability; do not call it a posterior variance.

Start with one fixed candidate set and a simple discrepancy diagnostic, such as residual structure under the nominal map. Do not assume a learned image-sized residual is a valid detector: it can absorb the discrepancy it is supposed to reveal. Construct at least one stress condition where candidate operators share the same omitted process.

## Comparator and compute gates

Required families are:

1. the existing classical reconstruction as an implementation/sensitivity control;
2. an operator-conditioned learned reconstruction with documented input and noise assumptions;
3. a blind image/operator inference method, prioritizing the P018/P019/P038 joint-sampling group after code/weights checks;
4. a strong operator-oblivious restoration baseline for image quality and simple confidence comparisons.

No implementation is claimed reproduced yet. Reuse an available reconstruction rather than training a new backbone for this pilot. Do not silently substitute one sampler for another; record why a proposed baseline is unavailable, and retain it as a comparison limitation.

Report wall-clock time, hardware, peak memory, image-prior evaluations, operator updates and sample counts. Where feasible, compare `4 operators × 4 image draws` with `1 fitted operator × 16 image draws`, while separately reporting the operator-estimation cost. Also report a matched-wall-time comparison if that cost materially differs. Nested conditional sampling may need a different implementation than joint chain output; do not relabel one as the other.

## Calibration and evaluation

- Freeze score features and weights using development data only.
- On independent calibration sources, select the largest retained coverage meeting a predeclared empirical risk target, initially `R <= 0.10` with desired `C >= 0.50`. If none qualifies, record an unmet target; do not lower the requirement after seeing test results.
- Evaluate both this fixed threshold and descriptive risk–coverage curves. For curves, ranking uses observed scores only; clean truth is used to calculate risk, never to construct the practical ranking.
- Report risk at 50%, 75% and 90% retained coverage; area under the risk–coverage curve; coverage achieved at the frozen threshold; error-detection AUROC; whole-image PSNR/SSIM; and compute. AUC is undefined when the evaluated set has only one error class.
- Use a paired bootstrap over unique source images, keeping all patches, degradations and repetitions for an image together. Report 95% intervals as approximate sampling uncertainty. Do not bootstrap pixels independently or present a hundred image variants as a hundred independent sources.
- Report conditions and scene/texture strata separately. A pooled good average must not hide a wrong-family failure.
- Re-evaluate retained-region risk directly. Calibrating image intervals and then selecting the narrowest regions does not automatically preserve their original guarantee.

The initial empirical threshold rule provides no formal distribution-free risk guarantee, especially after shift. Formal guarantees require a specified sampling unit, calibration independence, a selection-valid argument and an explicit shift assumption. See the distinctions in [P011](https://proceedings.mlr.press/v162/angelopoulos22a/angelopoulos22a.pdf), [P062](https://proceedings.mlr.press/v202/teneggi23a/teneggi23a.pdf) and [P066](https://arxiv.org/html/2502.05127v1). A source-only conformal guarantee must not be advertised for arbitrary unmodelled acquisition.

## Go / redesign / stop

**Feasibility signal:** at least two representative reconstruction families exhibit a residual or image-only uncertainty failure, and operator-sensitive selection improves the paired selective-risk comparison at 50% retained coverage. Predeclare a target reduction of at least two percentage points in the bad-detail rate for M3; use paired uncertainty intervals and state if the pilot is inconclusive. Also show full coverage curves, so a favourable operating point cannot conceal broad deterioration.

**Progression gate:** the improvement survives matched information and compute, avoids material unexplained matched-condition regressions, and remains useful on textured regions. This earns a larger study and a mechanism/guarantee investigation. It is not yet journal evidence.

**Redesign:** the signal helps only within the candidate operator family, fails under the shared omitted-process test, or depends on excessive abstention. Diagnose whether the limit is score design, insufficient calibration data or non-identifiability before adding a network.

**Stop this candidate:** nearest-method evidence duplicates the mechanism; improvements vanish against the strongest matched-budget comparator; or deployment requires unavailable clean truth or oracle acquisition parameters.

## Deliverables for the implementation turn

- A manifest with unique sources, split assignment, acquisition order, true parameters, supplied information and every random seed.
- An inference-results schema with method/version/weights, reconstructed image, score maps, optional samples and compute logs.
- Evaluation code that enforces split separation, distinguishes missing/undefined metrics and resamples at source level.
- A results report including all declared conditions and failures.
- A dated freeze of this draft's unresolved implementation choices before running the full calibration/test experiment.

No experiment results, new method performance, or claim of reliable CCTV identity recovery are asserted by this specification.


## 17 September 2026 addendum: final direct comparator P035

The [P035 assessment](../literature/screening/full_text_12_report.md) resolves the final seed-set access gap. It establishes learned additive correction with diffusion, an image/residual identifiability concern, prescribed valid-region recovery and an empirical model-error threshold near 0.1. These are prior-art overlaps, not new experimental results here.

Compare observable correction-magnitude and residual scores alongside image-only uncertainty and operator sensitivity when a compatible correction baseline is implemented. Exact reproduction requires code, weights and implementation details; a simplified residual method must be labelled an adaptation. P035 equation 11 uses true-versus-perturbed model evaluations and belongs only in an oracle diagnostic unless an observable estimator is separately validated. Do not transfer its visual 0.1 threshold to DIV2K/JPEG. Preserve source-disjoint calibration/test splits, matched coverage/compute and explicit common-misspecification failures. The existing baseline-development priority and original research topic remain unchanged.
