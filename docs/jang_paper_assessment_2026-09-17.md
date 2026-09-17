# Lee and Jang: full-paper assessment and research decision

17 September 2026. This is a methodological assessment of the supplied full paper and a targeted comparison with our experiments. It is not an exhaustive novelty search, a reproduction of the authors' results, or a formal screening/adjudication update.

**Recommendation: retain the broad research topic, but do not propose generic learned residual correction as our new contribution. First establish an acquisition-aware comparison, then test whether observable model sensitivity adds useful error detection and selective retention beyond strong controls.** This paper leaves that specific question unanswered; it does not establish that the question is novel across the literature.

## 1. Source and reading extent

Chanseok Lee and Mooseok Jang, *Mitigating Forward Model Mismatch in Inverse Problems via Learned Residuals and Diffusion Priors*, Proceedings of SPIE 14016, 140160D, 2026, SPIE ABC 2025. DOI: [10.1117/12.3098133](https://doi.org/10.1117/12.3098133).

The authoritative source for this assessment is the user's `140160D.pdf`: 12 pages, 12,433,769 bytes, SHA-256 `ba25f9979984520a89fbdb049fdc932893c0ca59bdb79c319ee277e25d233eb1`. All 12 pages were read, including the reference list; all five figures and the key equations were visually inspected in rendered pages. Page numbers below are PDF pages, matching the article's suffix pagination. The paper matches seed record **P035** by title and DOI. The DOI web retrieval failed during this review; the supplied full text, rather than an abstract or search snippet, supports the findings below.

The earlier synthesis and screening counts remain dated historical records. P035's previous lack of full-text access is resolved, but this note does not silently change the formal eligibility register, generated evidence matrix, or human-adjudication status. No author was contacted during this review.

## 2. What the method actually does

Pages 3-5, Equations 5-8 and Figure 1 describe an extension of diffusion posterior sampling. The main idea is to estimate both the object and a measurement-domain discrepancy:

\[
(\widehat x,\widehat r)\in\arg\min_{x,r}
\|y-F(x)-r\|_2^2+\lambda_x R_x(x)+\lambda_r R_r(r).
\]

This rewrites the minimisation in Equation 8 using argmin notation to distinguish an optimiser from its objective value. Here, the pretrained diffusion prior constrains the object, while a shallow network estimates the discrepancy. The latter is a correction of the measurement prediction, not an error bar on the reconstructed image.

In the first stage, each reverse-diffusion step forms a clean-image estimate, computes the preliminary discrepancy `y - F(x_hat)`, and updates the residual network for K iterations using a regularised fitting loss. The estimated residual then changes the measurement-consistency guidance. In the second stage, the method adds noise back to the first reconstruction and runs a refinement diffusion using the estimated residual. Figure 3 depicts a first-stage trajectory from T=1000 and refinement from T=200; these displayed trajectories are not a complete specification of every experiment.

The authors explicitly recognise the identifiability problem on page 4: many combinations of object and discrepancy explain the same measurement. A flexible residual can absorb signal that ought to be reconstructed. Their network and image prior constrain this ambiguity; the paper does not prove that the recovered residual uniquely identifies the actual physical error.

## 3. Evidence and its limits

| Evidence in the supplied paper | What it supports | What it does not establish |
|---|---|---|
| Digital holographic microscopy, rectum tissue at a distance error of -3 depth-of-field units; comparison with CS and DeepDIH (p. 5, Fig. 2) | A visual demonstration of improved reconstruction under the depicted distance mismatch | A numerical effect size over a reported independent test population, or superiority to all current mismatch methods |
| Two-stage reconstruction and residual trajectory (p. 6, Fig. 3) | Illustration of how the displayed reconstruction changes during both stages | A quantitative ablation isolating the residual network from the diffusion prior, or a general convergence theorem |
| Scattering experiment with different speckle PSFs for object contributions inside/outside the angular memory-effect region (pp. 6-7, Fig. 4) | A simulated example in which one assumed convolution fails to explain the whole measurement | A real scattering experiment in this results section, or faithful recovery of the whole object |
| Distance sweep from -4 to +4 depth-of-field units for beads, lung tissue and rectum tissue (pp. 7-8, Fig. 5) | Visual degradation with increasing mismatch and a plotted model-error ratio | A calibrated failure probability, a universally valid 0.1 threshold, or an operational score requiring only an unknown measurement |

The scattering distinction matters: the authors intentionally reconstruct the valid-region contribution and absorb out-of-region contributions into the residual. This is already relevant to deciding what is recoverable. It is not the same as learning an image-patch acceptance rule and measuring retained-detail error at controlled coverage.

The supplied article contains no PSNR/SSIM results table, statistical uncertainty intervals, explicit test-population size/split, or risk-coverage evaluation. Its experimental presentation is predominantly qualitative, with a numerical mismatch-ratio plot. These are limits of the reported evidence, not evidence that the method fails.

## 4. The failure threshold needs careful interpretation

On page 7, Equation 11 defines

\[
\zeta=\frac{\|F(x,d)-F(x,d+\Delta d)\|_2}{\|y\|_2}.
\]

The authors report a threshold near 0.1 and explicitly say it was identified visually. This is a norm ratio, not a stated squared-energy ratio or a 90% confidence level. The numerator requires the object and both true/perturbed forward configurations. **As written, it is an analysis quantity; the paper supplies no procedure that makes it an observable, calibrated warning score for a wholly unknown object and unknown true distance.** Replacing the true object with a reconstruction would define a new proxy whose validity must be tested.

There is also a specific equation/figure clarification to resolve before reproduction: Equation 11 gives zero numerator when Delta d is zero, whereas Figure 5b visibly has a positive minimum at zero perturbation. The plotted quantity may incorporate an additional error term or use a different reference; the supplied text does not explain this. This is an apparent inconsistency to ask about, not a basis for alleging misconduct or rejecting the method. We should neither copy the threshold into our system nor invent a reason for the discrepancy.

## 5. Reproduction details not supplied here

The PDF does not provide a complete executable recipe: residual-network layer specification, its optimiser/learning rate/initialisation, a numerical K, regularisation weights, full diffusion schedules/checkpoints, training-set counts and splits, and runtime/hardware measurements are not fully specified. It is also unclear from the description whether differentiation through the estimated residual is stopped during the image update, and precisely how the residual is held or updated during refinement. No code or checkpoint link is supplied in this PDF. This does not establish that none exists elsewhere.

Before calling any implementation a reproduction, obtain these details, the definition/data underlying Figure 5b, and the provenance of the experimental ground-truth phase references. A DPIR-based residual adaptation would be a separately declared comparator, not a reproduction of Lee and Jang's diffusion method. Our own eight-iteration DRUNet/HQS adapter does not implement DDPM/DPS sampling.

## 6. Comparison with our verified checkpoint

Our evidence comes from the [Acquisition 03 archive audit](../experiments/acquisition_03/archive_verification_20260917/verification.md), [Learned 02 design](../experiments/learned_02/design_freeze.md), [Acquisition 03 design](../experiments/acquisition_03/design_freeze.md), and the actual [DPIR-style adapter](../experiments/learned_02/learned.py).

| Dimension | Lee and Jang | Our current work | Consequence |
|---|---|---|---|
| Reconstruction | Diffusion prior plus online residual network and second refinement | Frozen Gaussian DRUNet prior in HQS; classical and input controls | We have not reproduced or beaten their method |
| Mismatch | Holographic propagation-distance error; simulated failure of one convolution outside the memory-effect range | Wrong blur width; progressively added clipping, rounding and JPEG codec | Both address departures from an assumed forward process; an outside-family claim alone is insufficient |
| Correction | Learned additive measurement discrepancy | No learned discrepancy correction in Notebooks 02/03 | Adding one would directly overlap with existing work |
| Reliability | Empirical global boundary based on model-error ratio | Heuristic operator/transformation spread, residual and gradient comparisons in Notebook 02 | These are distinct measurements; neither current project result establishes calibrated reliability |
| Selective output | Valid-region contribution in a constructed scattering model | Patch retention with measured detail error; no independent calibrated acceptance rule | A narrower comparison remains possible, but novelty is not established |

Across the same four exposed development sources, nominal DPIR's pooled RGB advantage over the classical comparator is +0.498575 dB after 8-bit rounding and -0.411957 dB after JPEG Q75. This is the verified whole-codec stage contrast, not an isolated DCT mechanism. It says nothing directly about Lee and Jang's performance on our data. Our four images, one noise draw per source and unresolved DRUNet/DIV2K training overlap do not provide independent-test evidence.

## 7. Other overlap checked for this decision

This targeted check is deliberately narrower than a new systematic search. The versions and portions inspected here are explicit:

| Primary source and reading scope | Relevant established overlap | Implication for us |
|---|---|---|
| [Guan et al., arXiv:2403.04847v1](https://arxiv.org/html/2403.04847v1), abstract and Sections 1/3, especially Eq. 5 | Per-instance neural residual estimation within model-based reconstruction already uses a discrepancy-regularised joint objective | A residual network added to an inverse solver is not sufficient novelty |
| [LADiBI, arXiv:2412.00557v1](https://arxiv.org/html/2412.00557v1), abstract and Section 4.3 | Blind JPEG decompression is explicitly evaluated with a learned operator representation; its information and prompt choices are described | Switching from holography to JPEG is not sufficient novelty; domain, information and compute must be matched in a fair comparison |
| [BlindDPS, arXiv:2211.10656v1](https://arxiv.org/html/2211.10656v1), abstract and method overview | Image and operator inference using parallel diffusion already exists within specified functional families | Merely adding multiple operator hypotheses is not a new general principle |
| [DPIR, arXiv:2008.13751v2](https://arxiv.org/html/2008.13751v2), overview and Section III-C3 | The paper also trains a separate JPEG-deblocking DRUNet by changing training data and conditioning | Our Gaussian denoiser checkpoint's JPEG failure cannot represent the performance of all DRUNet variants or JPEG-aware restoration |
| [Angelopoulos et al., ICML 2022](https://proceedings.mlr.press/v162/angelopoulos22a.html), official abstract and selected PDF evaluation passages | Calibrated imaging uncertainty is existing methodology, including phase microscopy | Adding confidence intervals is not sufficient novelty; any claim must specify its error target and statistical assumptions |

These supporting papers were not all reread in full during this turn. The previous [provisional synthesis](../literature/synthesis/provisional_gap_synthesis_01.md) contains further competitor requirements, including certificate/fallback and joint-inference methods; this note does not claim to clear them.

## 8. Way forward: one bounded question before another architecture

Retain the umbrella topic **Physics-Informed Deep Learning for Robust Image Reconstruction Under Forward-Model Mismatch**. Keep the narrower question provisional:

> When an acquisition stage is missing from the assumed model, can information available at reconstruction time identify inaccurate details and improve their selective retention beyond strong restoration, residual and image-only controls?

The immediate next development comparison should ask **whether accounting for JPEG processing reduces the observed failure before adding a flexible learned residual**. Preserve the input, classical inverse and current DPIR adapter. Add a justified acquisition-aware comparator, auditing its code, weights and training domain before selecting it. A known-codec control can diagnose the value of that information, but must be reported separately from methods receiving only decoded pixels. It is not automatically a performance upper bound. Do not use the true blur or clean reference to choose operational outputs.

Then test the reliability question at matched retained coverage: measure retained high-pass detail error, bad-detail rate, full-image quality and actual compute. Retain the residual, gradient and fixed-operator transformation controls; add a stronger image-only uncertainty comparator before a superiority claim. Operator spread must beat these comparisons and retain useful image content, rather than merely report low disagreement. If every candidate shares the omitted stage, low spread can coexist with error; our acquisition/score choices must expose that possibility.

Any later learned-discrepancy comparison should include a no-correction baseline and a simple regularisation/data-fidelity-strength control. The reason is mathematical: for a freely optimised additive residual with a **squared** L2 penalty,

\[
\min_r\|e-r\|_2^2+\lambda\|r\|_2^2
=\frac{\lambda}{1+\lambda}\|e\|_2^2,\qquad
r^*=\frac{e}{1+\lambda},\quad \lambda>0.
\]

Here e is a fixed measurement discrepancy. Thus this particular unconstrained correction only changes the effective fidelity weight. This derivation is a proposed control rationale, **not a claim of equivalence to the paper's network-constrained, two-stage algorithm**; its text describes an L2 regulariser without enough implementation detail to equate the two.

Use the four existing images for engineering only. Before confirmatory claims, establish checkpoint-disjoint source data, separate development/calibration/test by source, predeclare acquisition conditions and noise repetitions, and keep test results sealed until decisions are frozen. Several patches or acquisition stages from one source are not independent source replicates. Any failure guarantee under distribution shift needs its own justified conditions and evaluation.

Proceed with a proposed method only if it adds a reproducible benefit beyond these controls. If codec-aware reconstruction removes the apparent advantage, or selection fails against the strongest control at useful coverage, revise or reject the specific mechanism. A negative finding does not automatically become a publishable contribution. Nothing in this paper alone requires abandoning the broad topic or closes the separate scoping-review route; those routes still need their own defensible contribution and methodology.

**Status:** paper assessment complete; no new experiment executed, no new notebook issued, no novelty claim made. The next experiment is recommended here, not frozen or implemented.
