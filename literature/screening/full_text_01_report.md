# Full-text checkpoint 01 — 16 September 2026

**12 AI full-text eligibility assessments completed: 11 recommendations to include and 1 to exclude. Another 78 seed records await this assessment.** All 90 retain stable IDs. Human adjudication and final formal inclusion remain pending; these are not 12 independently human-verified studies.

The historical initial pass remains 90 triaged, 82 advance and 8 unclear. Seven of those eight unclear records now have full-text decisions. P016 remains unresolved because its author PDF could not be opened. Retrieval failure is not an exclusion.

## Decisions and evidence

| ID | Decision | Full-text basis / interpretation | Inspected source |
|---|---|---|---|
| P006 | Include | Noise-shift experiment resolves scope (§6.7). | [Deep equilibrium](https://arxiv.org/pdf/2102.07944) |
| P038 | Include | Joint uncertainty; initialization robustness differs from wrong-family robustness (§3). | [PRISM](https://arxiv.org/html/2509.16106v1) |
| P042 | Include | Conditional certificates; operational score and controlled candidate construction need care (§§4,8). | [No-Harm](https://arxiv.org/html/2606.07153v1) |
| P048 | Include | Posterior sensitivity with supplied operators (§§3–5). | [PnP mismatch](https://proceedings.iclr.cc/paper_files/paper/2024/file/2a2874875861f6a6436b505dd77683d1-Paper-Conference.pdf) |
| P060 | Exclude | Criterion 2: IQA, not a central reconstruction study (§§III–IV). Retain as ancillary data reference. | [CQAD](https://www.jmis.org/archive/view_article?pid=jmis-12-3-81) |
| P064 | Include | Inexact geometry plus image variance; simulation-dependent error estimates (§§III–V). | [nanoCT](https://arxiv.org/pdf/2307.10474) |
| P066 | Include | Self-supervised calibration has explicit operator/noise assumptions (§§2–4). | [SURE conformal](https://arxiv.org/html/2502.05127v1) |
| P072 | Include | GoPro-to-HIDE/RealBlur transfer; separate task models (§4). | [PromptRestorer](https://proceedings.neurips.cc/paper_files/paper/2023/file/1c364d98a5cdc426fd8c76fbb2c10e34-Paper-Conference.pdf) |
| P082 | Include | Posterior formulation and prior-approximation stress test (§4, Figure 6). | [Diffusion optimal control](https://proceedings.neurips.cc/paper_files/paper/2024/file/86655bc516148e311bcfcf88f1744de7-Paper-Conference.pdf) |
| P084 | Include | Supplied noise-level perturbation is in Appendix C.2, Table 14. | [ProjDiff](https://proceedings.neurips.cc/paper_files/paper/2024/file/54fa8255cdf30736ecad38e842725e7f-Paper-Conference.pdf) |
| P086 | Include | Sample variance/fidelity assessment; regularizer calibration is not coverage calibration (§5). | [FLAIR](https://arxiv.org/html/2506.02680v1) |
| P087 | Include | Measurement-support comparison and imprecise real application (§5). | [CDIM](https://arxiv.org/html/2411.00359v2) |

## What this checkpoint establishes

[The assessment register](full_text_01.json) records all five eligibility criteria, the inspected version and extent, a technical extraction, applicability limits and exactly which feature fields were verified. Full-text assessment means sufficient evidence for eligibility; it does not mean every proof was independently checked or code reproduced. Where an author preprint was used, equivalence to the final proceedings version remains unverified.

The workbook's Screening Log column J contains the AI full-text recommendations, K the primary exclusion category, and L the rationale. Evidence Matrix column AA remains the final formal decision. Column M continues to mean local full-paper acquisition; online inspection does not imply a downloaded copy. Summary cell E15 counts completed AI decisions and updates when J changes. Unlisted feature fields remain provisional.

This batch used the existing criteria, not a new requirement that every eligible study solve operator mismatch. Reconstruction uncertainty, explicit transfer/noise-shift tests and operational measurement-support evaluation also qualify. A generic data-consistency layer alone does not establish calibrated reliability. The CQAD exclusion concerns the central task, not a blanket exclusion of datasets.

## Consequences for the proposed contribution

The narrower selective-detail question remains a **candidate**, not an established gap. The evidence above gives us distinct comparison conditions: acquisition error, prior error, noise-parameter error, uncertainty calibration and output selection must be evaluated separately. We cannot infer wrong-family reliability from successful initialization tests, posterior variance or ordinary transfer results.

The next closest-method assessments are P026/P053 (including study-lineage comparison), P040, P039, P043–P047 and the other calibration/hallucination papers. Incomplete-source records P001/P013/P016/P032/P049/P071 remain retrieval priorities. These priorities do not replace assessment of the remaining 78 records.

Two additional conformal extensions surfaced as citation-search leads. They are logged as unassessed follow-ups in the register and have not been added to the 90 or counted as included studies. Formal database searches, deduplication and human verification are still outstanding.

## Checkpoint validation

The matrix, screening log and four reference exports retain 90 unique seed IDs. Initial-triage decisions and final-formal fields are preserved. Twelve AI decisions reconcile to 11 include, 1 exclude and 78 pending. The workbook counter responds to a temporary decision change and returns to the correct total. Five sheets, three tables, one chart, frozen panes and merges are preserved; only the existing decision dropdown is extended. Changed views were visually inspected. See [the field-level change audit](full_text_01_changes.json).
