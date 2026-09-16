# Full-text checkpoint 04 — 16 September 2026

Eight additional AI eligibility assessments are complete, all recommending inclusion. Cumulative progress is **44 of 90 assessed: 43 include recommendations, 1 exclude, 46 pending**. Human adjudication remains outstanding. Formal search/inclusion counters remain zero; the 90 seeds are not a completed PRISMA corpus.

The [criterion-level register](full_text_04.json) records versions, reading extent, technical evidence, selected verified features and follow-ups. Decisions use protocol v0.4. Eligibility assessment does not imply an audit of every proof, supplement or codebase. Unlisted legacy feature codes remain provisional. Access failures remain pending, not exclusions.

## Evidence added

| Seed | Inspected source | Relevant boundary |
|---|---|---|
| P005 | [Zeng and Lam, lensless mismatch compensation](https://www.eee.hku.hk/optima/pub/journal/2109_TCI.pdf), final TCI 2021 | Reconstruction compensation already combines physics and learned corrections; it does not infer a physical-operator posterior. |
| P008 | [On hallucinations in tomographic image reconstruction](https://arxiv.org/html/2012.00646v3), arXiv v3 | Null-space hallucination maps need reference truth. Measurement-space maps and heuristic regions have different requirements. |
| P014 | [Conffusion](https://arxiv.org/html/2211.09795v1), arXiv v1 | Calibrated reconstruction intervals already exist; calibration assumptions and validation reuse need careful reconciliation. |
| P015 | [Diffusion Posterior Sampling](https://arxiv.org/html/2209.14687v4), arXiv v4 | Approximate image posterior sampling uses a supplied operator; it does not provide joint operator uncertainty or calibrated coverage. |
| P054 | [RELED / event-guided low-light deblurring](https://arxiv.org/html/2408.14916v1), arXiv v1 | Extra event measurements support the reconstruction. This differs from ordinary RGB-only CCTV. |
| P056 | [RealBasicVSR](https://arxiv.org/html/2111.12704v1), arXiv v1 | Compound and time-varying training degradations are already present. Real-video quality evidence does not verify exact recovered detail. |
| P057 | [SRWD-VSR](https://arxiv.org/pdf/2305.02660), inspected PDF header v1 | Motion blur is excluded and parameters are fixed within training clips; evaluation lacks clean video truth. |
| P080 | [Generative Diffusion Prior](https://arxiv.org/html/2304.01247v1), arXiv v1 | Joint point estimation of a flexible degradation model already exists; it is not a calibrated operator posterior. |

Final proceedings/journal versions were not silently substituted for the inspected preprints. The register identifies unresolved version comparisons. No paper PDFs are redistributed.

## Implication for our proposed contribution

The original topic remains **Physics-Informed Deep Learning for Robust Image Reconstruction Under Forward-Model Mismatch**. Novelty remains unestablished. The candidate question remains:

> Can accounting for uncertainty in an estimated forward operator improve the reliability of selectively released image detail when the true acquisition process leaves the assumed model family?

The table supports a comparison design, not a claim that nobody has solved this question. Our experiment specification should separate:

1. The truth being evaluated: reference-image error, measurement support, perceptual quality or correctness of a particular detail.
2. Available observations: ordinary RGB, multi-frame observations or additional sensor channels.
3. What is inferred: image samples, degradation point estimates or an operator distribution.
4. What calibration covers: a declared risk and population, with thresholds and tuning fixed before test evaluation.

These are our design inferences from the assessed evidence. They are not new empirical findings or guarantees. Previous close competitors and their assumptions remain in checkpoints 01–03; no weaker comparator should replace them.

## Work remaining

Continue the existing full-text workflow for **46 records**. Checkpoint 04 adds failed source routes for P001/P012/P017/P055, with alternative sources not exhausted, and records successful alternate retrieval for P057/P080. The exact attempts are in the register.

The [deferred-work list](deferred_review_tasks.md) retains human adjudication, unresolved access, lineage, final-version comparisons, quality follow-ups and formal database-search accounting. The user has deferred these items; accessible assessments continue without a new approval step. No new screening level has been introduced.

The workbook, tracker, CSV, BibTeX, RIS and bibliography are synchronized. All 90 IDs, completed earlier decisions and historical triage are retained. See the [field-level change audit](full_text_04_changes.json) and [migration script](../../scripts/update_full_text_04.mjs).
