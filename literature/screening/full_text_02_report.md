# Full-text checkpoint 02 — 16 September 2026

Twelve additional seed records have completed AI full-text eligibility assessment, all with recommendations to include. Together with [checkpoint 01](full_text_01_report.md), this gives **24 assessed: 23 include recommendations, 1 exclude, 66 pending**. The seed list remains 90 records; potential publication lineages have not been silently merged.

These are completed AI assessments against the existing five eligibility criteria. Human adjudication and formal database-search accounting remain outstanding; final formal inclusion/exclusion counts remain zero. No new screening level or eligibility criterion was introduced. Protocol v0.4 and the search window are unchanged.

## Evidence register

The [criterion-level register](full_text_02.json) records the inspected version, reading extent, source locators, feature corrections and follow-ups for each paper. Reading was sufficient for eligibility and the listed technical extraction; it was not an independent audit of every proof, appendix or implementation. Findings from preprints are version-specific; final publications have not automatically been verified.

| ID | Inspected source | Role in the comparison | AI decision |
|---|---|---|---|
| P026 | [AverNet — NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/e635a25e49e73adc51f76aef462ff2f8-Paper-Conference.pdf) | Compound, temporally varying video restoration | Include |
| P033 | [Unsupervised distribution-shift detection — v1](https://arxiv.org/html/2505.11482v1) | Prior/content shift under known operators | Include |
| P034 | [Distribution-shift uncertainty — v1](https://arxiv.org/html/2510.10947v1) | Measurement-repetition variance | Include |
| P036 | [InverseNet — v1](https://arxiv.org/html/2603.04538v1) | Controlled acquisition mismatch | Include |
| P037 | [Hallucination limits and assessment — v1](https://arxiv.org/html/2605.13146v1) | Feasible alternatives and unsupported detail | Include |
| P039 | [ABAIR — v1](https://arxiv.org/html/2411.18412v1) | Adapter-based compound restoration | Include |
| P045 | [BC-PnP — NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/file/f810c2ba07bae78dfe9d25c5d40c5536-Paper-Conference.pdf) | Joint image/operator point estimation | Include |
| P047 | [A-adaptive reconstruction — v1](https://arxiv.org/html/2403.04847v1) | Learned forward-model correction | Include |
| P062 | [K-RCPS — ICML 2023](https://proceedings.mlr.press/v202/teneggi23a/teneggi23a.pdf) | Reconstruction risk control | Include |
| P063 | [Task-driven conformal prediction — v1](https://arxiv.org/html/2405.18527v1) | Task-score intervals and acquisition stopping | Include |
| P065 | [Conformalized generative Bayesian imaging — v1](https://arxiv.org/html/2504.07696v1) | Image/weight uncertainty and calibration | Include |
| P067 | [QUTCC — v1](https://arxiv.org/html/2507.14760v1) | Quantile intervals and empirical coverage | Include |

Only feature columns explicitly listed in each record were verified. Unlisted legacy codes remain provisional. `No` means not demonstrated in the inspected evidence, rather than proof that the capability is impossible. Online full-text inspection does not change the tracker's local-PDF acquisition flag.

## Implications for the proposed contribution

The umbrella topic remains **Physics-Informed Deep Learning for Robust Image Reconstruction Under Forward-Model Mismatch**. The candidate question remains:

> Can accounting for uncertainty in an estimated forward operator improve the reliability of selectively released image detail when the true acquisition process leaves the assumed model family?

This is still a question to test, not an established novelty claim. The comparison must distinguish:

- **Operator fitting from operator uncertainty:** BC-PnP and A-adaptive reconstruction already occupy joint estimation/correction. See their sources above and the record-level assumptions.
- **The target of coverage:** K-RCPS addresses image risk; task-driven conformal prediction targets a classifier score. Their guarantees cannot be exchanged without redefining the target and assumptions.
- **Reported calibration from deployment reliability:** QUTCC's risk-stratified results motivate checking the particular retained regions. Conformalized generative imaging's qualitative OOD examples are separate from its coverage tests.
- **A collection of alternatives from a certificate:** the hallucination assessment's lower approximation to feasible-set diameter does not supply an upper error certificate.

These distinctions narrow the experiment design. They do not establish that no other paper solves the candidate problem. Continue the remaining records before drawing a corpus-wide conclusion.

## Evidence that requires reconciliation

- P036: resolve the recovery-ratio differences between Tables 1–2 and §4.4 before extracting comparative numerical results.
- P067: inspect the §3.4 coverage-inequality notation and the stated confidence guarantee against Algorithm 1 before reusing the theory.
- P033/P045/P047: theorem statements have been inspected, but their assumptions and proofs have not been independently validated.
- P065: link the explicitly identified conference precursor before determining the number of distinct studies.

The corresponding primary sources and exact reading extents are in the register. These flags do not by themselves justify excluding a relevant study.

## Retrieval and lineage still pending

| ID | This checkpoint's access outcome | Next action |
|---|---|---|
| P032 | Publisher section access failed | Obtain complete publisher/author text |
| P035 | Institutional abstract only | Obtain SPIE paper |
| P040 | Institutional record; no usable author full text | Obtain VDPS manuscript |
| P043 | arXiv HTML/PDF access failed | Obtain author/publisher copy |
| P046 | arXiv HTML/PDF access failed | Obtain author/publisher copy |
| P053 | Publisher abstract/references accessible; methods unavailable | Obtain FaverNet and compare with P026 |

These six records are among the 66 pending, not exclusions. P016's earlier access issue also remains. P026/P053 authorship overlap and a citation are insufficient to settle study identity. All original IDs are retained.

The next pass continues the same full-text workflow, covering accessible pending records while pursuing this retrieval queue. There is no need to restart the seed list or add papers to reach a round number. Formal searching and citation chaining may later identify legitimate additions.

## Checkpoint validation

The workbook, screening log and four reference exports are synchronized. Validation checks the cumulative decision counts, all 90 stable IDs, unchanged formal decisions, the live counter's response to an input change, and preservation of native workbook objects. Cell-level edits are recorded in [the change audit](full_text_02_changes.json). Historical pilot and checkpoint-01 files are preserved.
