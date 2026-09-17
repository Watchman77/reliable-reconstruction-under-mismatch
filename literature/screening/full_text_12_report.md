# Full-text checkpoint 12: P035 received and assessed

**Date:** 17 September 2026. **Protocol:** v0.4; eligibility criteria and search window unchanged.

**90/90 seed records now have AI full-text eligibility assessments: 89 include recommendations, one exclude recommendation (P060), zero awaiting full text.** Human adjudication, publication-lineage reconciliation and formal search accounting remain outstanding. This closes the seed-set AI reading pass, not the scoping review or a novelty claim.

## Source and recommendation

**P035. Chanseok Lee and Mooseok Jang (2026). Mitigating Forward Model Mismatch in Inverse Problems via Learned Residuals and Diffusion Priors. Proceedings of SPIE 14016, 140160D.** [DOI](https://doi.org/10.1117/12.3098133).

The user supplied `140160D(1).pdf` and reported receiving it from Professor Jang. The complete 12-page publisher-formatted article identifies the title, authors, volume, article number and DOI on page 1. The conference name includes 2025; the publication imprint is 2026. We inspected the main text on pages 1-8, equations 1-11 and all five figures; references on pages 8-12 were scanned, not independently audited. Pages 4-8 were also rendered and visually inspected. No supplement or code was supplied.

SHA-256: `ba25f9979984520a89fbdb049fdc932893c0ca59bdb79c319ee277e25d233eb1`.

**AI recommendation: include.** This is primary in-window imaging research with an explicit operator-mismatch method, experiments and a complete English full text. The [criterion-level register](full_text_12.json) records each criterion and feature locator. The supplied PDF and its page images are not redistributed in this repository.

## What the paper establishes

| Evidence | Finding | Locator |
|---|---|---|
| Correction mechanism | Jointly optimise the image and an additive measurement residual under a diffusion prior and residual regularisation. A shallow network is updated during sampling; a second diffusion pass refines the image using the estimated residual. This is nuisance correction, not a posterior over physical operator parameters. | Sections 2.3-2.4, equation 8, figure 1, pp. 4-5 |
| Identifiability concern | The authors explicitly recognise multiple image/residual explanations and failure when the residual absorbs too much measurement signal. Neither learned correction nor this failure concern is a new idea for our project. | Sections 2.4 and 3.3, pp. 4, 7 |
| Holography | The reported rectum-tissue DHM demonstration compares with compressed sensing and DeepDIH under a distance error of -3 depth-of-field units. The prior uses bead/tissue fields. | Section 3.1, figure 2, p. 5 |
| Model-family violation | A simulated scattering experiment uses different speckle PSFs inside and outside a prescribed angular-memory-effect region. Reconstruction targets the valid region; outside-region contributions are intentionally absorbed into the residual. This is not evidence of recovering the entire object. | Section 3.2, figure 4, pp. 6-7 |
| Operational boundary | A depth-error sweep covers -4 to +4 depth-of-field units for beads, rectum and lung tissue. A normalised model-error threshold of approximately 0.1 is selected by visual reconstruction degradation. | Section 3.3, equation 11, figure 5, pp. 7-8 |

The paper's broad introductory wording includes real-world scattering, but the actual scattering experiment in section 3.2 is explicitly simulated. The real-measurement code refers to the reported DHM demonstration, not that simulation. Dataset sizes, source-disjoint splits and aggregate quality statistics are not supplied in enough detail to extract a general performance effect.

## The reliability comparison that matters

Equation 11 defines

\[
\zeta=\frac{\|F(x,d)-F(x,d+\Delta d)\|_2}{\|y\|_2}.
\]

The reported threshold is **an empirical operational-boundary diagnostic**, not probability calibration or a validated universal safety threshold. The definition evaluates a common object under true and perturbed physical parameters. Our inference is that it requires reference information or an additional estimation procedure when used on unknown captures; the paper does not demonstrate such a deployment estimator. Replacing its numerator by a learned residual norm would create a proxy, not reproduce equation 11.

The coding dictionary includes explicit reliability thresholds under abstention/selection. We therefore record **X=Partial**, rather than erase this overlap: there is a threshold and a valid-region reconstruction example, but no validated automatic reject rule, patch-level risk-coverage evaluation or selected-detail error control. **W=Partial** records visual artifact/fidelity comparisons and the signal-absorption failure analysis; it does not imply a systematic hallucination detector.

Image posterior sampling motivates reconstruction, but a reconstruction trajectory alone does not demonstrate an image uncertainty estimate. P/Q/R are therefore **No** in this inspected article: no evaluated image-UQ output, operator-uncertainty distribution or probability/coverage calibration. O is **Partial** because the jointly learned quantity is an additive nuisance residual. S is **Partial** because physical/model shifts are tested but training/evaluation independence is insufficiently documented. T is **Yes** for reported DHM measurements. U/V are **No** for demonstrated compound-degradation and video time-variation tests under the existing definitions.

## Consequence for our contribution

Keep **Physics-Informed Deep Learning for Robust Image Reconstruction Under Forward-Model Mismatch** as the umbrella topic. P035 occupies learned residual correction with diffusion, a signal/residual ambiguity discussion, an outside-model-family example and an empirical failure boundary. We must not present any of those alone as novel.

The narrower question remains testable: **can a score available without clean truth or true acquisition parameters identify unreliable reconstructed regions better than image uncertainty, measurement residual and correction-magnitude controls, at matched retained coverage and computation?** P035 does not settle that comparison. Its absence from an experiment does not establish that no other paper addresses it.

For a subsequent experiment:

1. Retain the existing baseline-development task and independent calibration/test requirements. This paper is not a reason to switch our development dataset to microscopy or claim a new result.
2. Include an additive-correction comparator when a compatible implementation is available. Label any simplified implementation as an adaptation, not a P035 reproduction.
3. Treat true-model discrepancy as an oracle diagnostic only. Evaluate observable correction-magnitude proxies separately and fit any thresholds on calibration sources only; do not transplant 0.1 to DIV2K/JPEG.
4. Measure both observation fit and retained-reference error, including cases where correction improves fit but hides image error, or all candidate models agree while wrong.
5. Maintain separate whole-image failure detection, spatial selection and statistical calibration endpoints. Demonstrate incremental benefit against strong controls before claiming novelty.

## Quality follow-ups

- Obtain architecture, hyperparameters, checkpoints, runtime, dataset counts, split information and code before an exact reproduction claim. No code link is printed in the supplied article; public availability was not exhaustively searched.
- Clarify construction of DHM reference phase and how the empirical boundary transfers across samples and systems. The article provides visual examples rather than a calibrated error-control evaluation.
- Figure 5b appears to have a nonzero value at zero depth perturbation, whereas equation 11 is zero when its two model evaluations coincide. Record this as a figure/definition question; do not invent a noise-floor explanation or alter the plot.
- Section 2.3 introduces an error magnitude and subsequently a signal-shaped residual. Preserve that distinction when implementing the vector correction in equation 8.

Historical checkpoints and synthesis 01 retain their dated evidence state. The current matrix, reference exports, this checkpoint and the [P035 synthesis addendum](../synthesis/p035_novelty_addendum_2026-09-17.md) record the resolved access gap.
