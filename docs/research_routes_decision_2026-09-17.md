# Experimental contribution and scoping review: separate decisions

17 September 2026. Working decision, not a registration or novelty finding.

## Decision

Retain the umbrella topic **Physics-Informed Deep Learning for Robust Image Reconstruction Under Forward-Model Mismatch**. Develop the reconstruction baseline before expanding the proposed operator-sensitivity mechanism. Keep the scoping-review route open and assess its own contribution independently of the experimental outcome.

| Track | Contribution to demonstrate | Current evidence | Next decision |
|---|---|---|---|
| Experimental paper | A specific mechanism or empirical finding beyond the closest methods | Pilot 00's score loses to the best simple control. The executed Baseline 01 improves reconstruction with gradient regularisation and finds positive pooled patch-score comparisons on the same four development sources; novelty remains unestablished | Retain the stronger classical comparator; audit and run a verified learned baseline and appropriate image-only uncertainty control before independent calibration/testing |
| Scoping review | A rigorous, useful map of evidence and assumptions, with a clear difference from existing reviews | 90 seed records; the repository synthesis records 89 AI full-text assessments, 88 include recommendations, one exclude and one pending report; human decisions and formal searches remain incomplete | Compare scope with existing reviews and align the protocol, searches, screening and reporting with the chosen review question |

A failed or already-known experimental mechanism does not invalidate a review of that literature. Conversely, finding many relevant papers does not by itself establish a publishable review. These are separate decisions.

## Bounded contribution test

**Candidate question:** At the same retained coverage, does local sensitivity to acquisition-model perturbations identify lower-error reconstructed regions beyond residual, image-gradient and appropriate image-only uncertainty controls when acquisition includes omitted processing?

The distinction is conditional on evidence. It is not a claim that this combination is absent from existing literature.

| Closest line | Established overlap in the project evidence register | Specific comparison still required |
|---|---|---|
| Mismatch-aware unrolling and correction, including Zeng and Lam | Explicit physics and learned mismatch compensation already exist | Distinguish improved observation fit from improved retained-region fidelity |
| BlindDPS, GibbsDDRM, PRISM | Joint image/operator inference and sampling already exist within specified model families | Test the same-information, same-budget selection mechanism under omitted processing; sampling operators is not itself new |
| Imaging uncertainty and conformal methods | Calibrated image sets/intervals already exist under specified targets and conditions | Compare the selected-region target and shift assumptions precisely; avoid treating variance as calibrated confidence |
| Posterior sensitivity and fallback work | Perturbation analysis and forms of rejection/fallback already exist | Identify an incremental mechanism or diagnostic beyond those claims; do not infer novelty from missing feature codes |
| P035, learned residuals and diffusion priors | Direct competitor; full-text assessment remains pending in the existing register | Resolve its methods and scope before a definitive novelty statement; do not infer absence of a feature from an inaccessible paper |

The source-linked [provisional synthesis](../literature/synthesis/provisional_gap_synthesis_01.md) provides the underlying inspected versions and limits. This note reuses those assessments; it does not claim a new full-text re-review of every comparator.

The [Baseline 01 result report](../experiments/baseline_01/README.md) contains the executed notebook, exact conditions, numerical findings and runtime limitations. Its change from Pilot 00 also changes the selection unit and condition grid, so it does not isolate the cause of improved score performance.

## Notebook 01 scope and controls

- Preserve Pilot 00, including its negative and source-specific findings.
- Use the same four development sources and 512-pixel central evaluation regions, with decoded-RGB identity checks against the official-archive manifest.
- Compare ridge and periodic first-derivative Tikhonov regularisation, input and fixed Gaussian smoothing, over three blur widths, two noise levels and linear/JPEG-chain conditions.
- Select each reconstruction family's regularisation using the other three development sources, pooling the conditions. Report per-source and aggregate results, plus boundary optima. This is internal development evaluation, not an untouched test set.
- Compare patch-level operator spread with measurement residual, image gradient and a fixed-operator measurement-noise perturbation control. The latter is not a calibrated neural image-only uncertainty comparator. Patch rankings use fixed coverage, not learned risk thresholds.
- Report the reference-defined textured stratum separately as an evaluation diagnostic. The deployed score does not receive the clean reference.
- A positive classical result justifies a later verified learned baseline; two classical regularisers do not satisfy the broader requirement for multiple learned reconstruction families.

Stop or redesign the candidate if its claimed difference is already supplied by existing work, if an apparent advantage disappears against credible controls, or if it works only by discarding informative detail. Do not keep tuning the same four sources to manufacture a positive claim. A negative-result paper is not assumed publishable either.

## Why the scoping route remains open

PRISMA describes scoping reviews as evidence syntheses that assess the scope of literature [1]. Munn et al. explain that mapping evidence, clarifying concepts and examining how research is conducted can justify a scoping review [2]. It does not require inventing a reconstruction network.

**Proposed mapping question:** What forms of forward-model mismatch have been studied in learned image reconstruction, and how are uncertainty, calibration, unsupported detail and selective output defined and evaluated under those conditions?

Potential value lies in distinguishing parameter mismatch from omitted processes, variability from calibrated uncertainty, and measurement agreement from reference fidelity, with reproducible evidence for each distinction. These are proposed synthesis dimensions, not findings that the field has neglected them.

An existing review by Ongie et al. organises inverse imaging methods partly by forward-model knowledge and learning supervision [3]. Our review must explicitly compare its questions and extraction dimensions with that and newer reviews. This turn's targeted public lookups did not establish a comprehensive review-overlap inventory; sparse or noisy search results are not evidence that no competing review exists.

## Methodological repairs before a formal scoping manuscript

1. Prepare a dated amendment from the current **systematic-review v0.4 draft** to the selected scoping question, including the population/concept/context, source types, charting fields and PRISMA-ScR reporting. This note does not silently rename or amend the protocol.
2. Execute and archive reproducible database-specific searches. Preserve the existing 1 January 2020–15 September 2026 window until a documented amendment or update changes it. Searches performed later must carry their actual dates.
3. Complete report/study lineage reconciliation, title/abstract and full-text screening, explicit exclusion reasons and human adjudication. AI recommendations are preparatory; they are not two independent human reviewers.
4. Treat inaccessible full texts as retrieval limitations, not scientific evidence of irrelevance. Resolve the protocol's older wording against its later retrieval convention in the dated amendment.
5. Verify extracted evidence and report limitations. Do not pool incompatible reconstruction metrics or claim a complete PRISMA corpus from the 90 seeds.
6. Compare prior review scope before finalising the review's claimed added value. Protocol registration can improve transparency; PRISMA-ScR reporting is not certification of methodological quality or publication acceptance.

No new database screening, human adjudication, registration, model training or final novelty determination is claimed by this note.

## Sources checked

1. [PRISMA-ScR official guidance](https://www.prisma-statement.org/scoping), accessed 17 September 2026.
2. Munn et al. (2018), [Systematic review or scoping review?](https://doi.org/10.1186/s12874-018-0611-x), methodological guidance, accessed 17 September 2026.
3. Ongie et al. (2020), [Deep Learning Techniques for Inverse Problems in Imaging](https://arxiv.org/abs/2005.06001). Abstract and bibliographic record checked in this turn; no exhaustive comparison of the full review is claimed.
4. [Current protocol](systematic_review_protocol.md), [topic reference](research_topic_and_review_reference.md), and [provisional synthesis](../literature/synthesis/provisional_gap_synthesis_01.md), repository checkpoint `e1f2471db5be4ca4b1ed006415d47a9db001c7fc`.
