# Full-text checkpoint 06 — 16 September 2026

Seven additional AI eligibility assessments are complete, all recommending inclusion. Cumulative progress is **60 of 90 assessed: 59 include recommendations, 1 exclude, 30 pending**. Human adjudication remains outstanding; formal search/inclusion counters remain zero.

The [criterion-level register](full_text_06.json) records inspected versions, reading extent, evidence and follow-ups. Protocol v0.4 and its date window are unchanged. These assessments do not certify every proof, supplement or implementation. Unlisted feature codes remain provisional; “No” means not demonstrated in the inspected evidence.

## Evidence added

| Seed | Inspected primary text | Boundary relevant to our comparison |
|---|---|---|
| P002 | [NETT](https://arxiv.org/pdf/1803.00092), PDF v3 (2019) | Fixed-operator stability and content transfer do not establish wrong-operator robustness. |
| P003 | [Reconstruction instabilities](https://arxiv.org/pdf/1902.05300), PDF v1 (2019) | Perturbation and missing-detail tests precede our proposed evaluation. |
| P028 | [SUPIR](https://arxiv.org/html/2401.13627v1), arXiv v1 | Prompt/fidelity examples require distinction from certified recovered information. |
| P070 | [Ronin](https://arxiv.org/html/2507.14851v1), arXiv v1 | Held-out degradation intervals provide a specific temporal-transfer comparison. |
| P077 | [RestoreAgent](https://proceedings.neurips.cc/paper_files/paper/2024/file/c78f639424b8d89ceb4f2efbb4dfe4f4-Paper-Conference.pdf), proceedings | Replanning/rollback is an existing partial failure-handling comparator. |
| P078 | [DreamClear](https://arxiv.org/html/2410.18666v1), arXiv v1 | Training-data filtering is different from withholding unreliable reconstructed detail. |
| P089 | [SeeSR](https://arxiv.org/pdf/2311.16518), PDF v2 | Semantic-fidelity tests and acknowledged tag/text failures constrain interpretation. |

P002 and P003 retain their **2020 journal lineages**, supported respectively by [Crossmark metadata](https://crossmark.crossref.org/dialog/?doi=10.1088%2F1361-6420%2Fab6d57&domain=pdf) and [author arXiv metadata](https://arxiv.org/abs/1902.05300). Their inspected 2019 precursors are explicitly identified; no final-text equivalence is assumed and no pre-2020 seed has been added. P002’s metadata access limits are recorded in the register. Other preprints likewise remain distinct from their final reports.

## Implication for the proposed contribution

The umbrella remains **Physics-Informed Deep Learning for Robust Image Reconstruction Under Forward-Model Mismatch**. The candidate question remains:

> Can accounting for uncertainty in an estimated forward operator improve the reliability of selectively released image detail when the true acquisition process leaves the assumed model family?

**Novelty remains unestablished.** Our synthesis inference is that a proposed selective method must compare with existing rollback/fallback approaches, and that a claim about reliable detail needs more than semantic quality or user preference. Prior operator-uncertainty and calibration competitors remain essential. This batch does not show that the complete candidate question has already been resolved or that no other paper addresses it.

The new register flags score direction/normalization, adapted versus zero-shot evaluation, source-version comparison and stopping-rule selection. These checks matter before numerical comparisons or implementation choices; they are not reasons to erase supported eligibility recommendations.

## Work remaining

**30 seeds remain pending** in the existing full-text workflow. P001, P009 and P016 remain unresolved after further access attempts. Candidate routes for P025 and P090 also failed; no technical evidence was attributed to those failed routes. Alternate sources are not exhausted, and access failure does not imply exclusion.

Human adjudication, formal database searches, lineage reconciliation and source-specific quality checks remain on the [deferred-work list](deferred_review_tasks.md). Accessible reading continues without waiting on user actions. No new screening stage has been introduced.

The matrix, tracker and four reference exports are synchronized. All 90 seed IDs and earlier decisions remain intact. See the [field-level audit](full_text_06_changes.json) and [migration script](../../scripts/update_full_text_06.mjs).
