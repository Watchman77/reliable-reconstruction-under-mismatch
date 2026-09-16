# Full-text checkpoint 03 — 16 September 2026

Twelve additional AI full-text eligibility assessments are complete, all with include recommendations. Cumulative progress is **36 assessed: 35 include recommendations, 1 exclude, 54 pending**, from 90 seed records. Human adjudication and formal inclusion remain pending. This continues the existing screening stage; it does not add another screening level.

The [criterion-level register](full_text_03.json) records sources, versions, inspected extent and verified feature fields. [Checkpoint 01](full_text_01_report.md) and [checkpoint 02](full_text_02_report.md) remain unchanged. “Include” here is an AI recommendation, not a formally included PRISMA study.

## Assessed papers

| ID | Paper / inspected source | Decision | Distinction for our comparison |
|---|---|---|---|
| P007 | [Deep Probabilistic Imaging](https://ojs.aaai.org/index.php/AAAI/article/view/16366/16173) | AI include | Posterior approximation versus empirical coverage. |
| P010 | [Real-ESRGAN](https://arxiv.org/html/2107.10833v2) | AI include | Compound training versus reliable detail recovery. |
| P011 | [Image-to-Image UQ](https://proceedings.mlr.press/v162/angelopoulos22a/angelopoulos22a.pdf) | AI include | Average risk control versus conditional coverage. |
| P018 | [BlindDPS](https://arxiv.org/html/2211.10656v1) | AI include | Joint sampling within a specified operator family. |
| P019 | [GibbsDDRM](https://proceedings.mlr.press/v202/murata23a/murata23a.pdf) | AI include | Ideal sampler guarantees versus practical approximations. |
| P022 | [Fast Diffusion EM](https://arxiv.org/html/2309.00287v2) | AI include | Image samples with a point-estimated kernel. |
| P023 | [BIRD](https://proceedings.neurips.cc/paper_files/paper/2024/file/3d13d910b48ac2e672a32cfdf98be1bf-Paper-Conference.pdf) | AI include | Optimization convergence versus rejection. |
| P024 | [LatentDEM](https://arxiv.org/html/2407.01027v1) | AI include | Annealed consistency versus operator uncertainty. |
| P041 | [HSDiff](https://arxiv.org/html/2511.18473v1) | AI include | Coverage evaluation with specified optics. |
| P050 | [LADiBI](https://arxiv.org/html/2412.00557v1) | AI include | Learned nonlinear operator; task-prompt assumptions. |
| P051 | [ADOBI](https://arxiv.org/html/2411.16535v1) | AI include | Sensitivity-map fitting versus uncertainty calibration. |
| P052 | [CaMB-Diff](https://arxiv.org/html/2603.01890v1) | AI include | Restricted intensity mappings versus general acquisition. |

## Implication for the candidate gap

The umbrella topic and candidate question remain unchanged. This batch strengthens the case for comparing **what is uncertain, which assumptions are known, and how reliability is evaluated**. The detailed evidence supporting those distinctions is in the linked register. Neither adding an operator estimator nor displaying sample variance establishes a novel contribution.

Our working question remains:

> Can accounting for uncertainty in an estimated forward operator improve the reliability of selectively released image detail when the true acquisition process leaves the assumed model family?

This is our research hypothesis, not a literature-established gap. The remaining 54 records and unresolved nearest-method questions can still change it. No new architecture or guaranteed publication outcome is inferred from this checkpoint.

For the eventual comparison, separately record image-only sampling, joint image/operator sampling and operator point estimation. Also separate content shifts from parameter shifts and failures of the operator's functional form. Evaluate reliability at useful retained coverage using validation-only threshold selection. These are proposed comparison controls, not claims that existing methods cannot satisfy them.

## Evidence limits and deferred work

An accessible preprint supports a version-specific assessment; it does not certify that the final conference or journal text is identical. Supplements and proofs were not exhaustively audited. No quantitative meta-analysis is performed. Numerical entries missing from HTML were not reconstructed or guessed.

P009 and P021 remain pending after unsuccessful access attempts. P010, P018 and P022 were assessed through accessible author versions after initial source routes failed. Earlier unresolved retrievals and publication-lineage checks remain in the [deferred-work list](deferred_review_tasks.md). The user's pending actions are deferred and do not block further accessible readings.

The workbook preserves all 90 IDs, historical triage, formal decisions, formulas, tables, chart and validation rules. Only explicitly listed feature fields are verified; other legacy codes and short gap descriptions remain provisional. The [change audit](full_text_03_changes.json) records cell-level edits. Reference exports are synchronized draft metadata; complete author lists and final versions still require reconciliation before submission.
