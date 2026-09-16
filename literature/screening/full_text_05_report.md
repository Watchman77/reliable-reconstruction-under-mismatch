# Full-text checkpoint 05 — 16 September 2026

Nine additional AI eligibility assessments are complete, all recommending inclusion. Cumulative progress is **53 of 90 assessed: 52 include recommendations, 1 exclude, 37 pending**. Human adjudication remains outstanding. Formal search/inclusion counters remain zero; these seeds are not a completed PRISMA corpus.

The [criterion-level register](full_text_05.json) records the source version, reading extent, criteria, verified feature fields and quality follow-ups. Protocol v0.4 and its date window are unchanged. Eligibility assessment does not certify every proof, supplement or codebase. Unlisted feature codes remain provisional.

## Evidence added

| Seed | Inspected primary text | Boundary relevant to our comparison |
|---|---|---|
| P012 | [DDRM](https://arxiv.org/html/2201.11793v3), arXiv v3 | Image sampling assumes a supplied linear operator; class-conditioned comparisons need matched information. |
| P020 | [PromptIR](https://arxiv.org/html/2306.13090v1), arXiv v1 | Unknown-degradation prompting includes held-out noise tests; separate tasks do not demonstrate a compound chain. |
| P074 | [DA-CLIP](https://arxiv.org/html/2310.01018v2), arXiv v2 | Degradation embeddings differ from physical-operator estimates; simultaneous corruptions remain a stated limitation. |
| P075 | [MPerceiver](https://arxiv.org/html/2312.02918v1), arXiv v1 | Compound restoration and transfer already exist; class probabilities do not establish operator uncertainty. |
| P076 | [InstructIR](https://arxiv.org/html/2401.16468v1), arXiv v1 | Instruction-selected restoration is different from reliability-based abstention. |
| P079 | [BIR-D](https://arxiv.org/html/2408.11287v1), arXiv v1 | Joint kernel/mask point estimation and adaptive guidance already exist. |
| P081 | [DP-IR](https://arxiv.org/html/2411.05993v1), arXiv v1 | Modular conditional sampling reuses networks but trains fusion per task. |
| P083 | [DPnP](https://arxiv.org/html/2403.17042v1), inspected HTML route | Robustness bounds concern sampler errors under a supplied likelihood; rendered-date reconciliation remains open. |
| P085 | [InvFusion](https://arxiv.org/html/2504.01689v1), arXiv v1 using “InvFussion” | Operator conditioning, unseen outpainting and posterior principal directions are existing comparators. |

Final publication texts were not silently substituted for these inspected versions. The DPnP route displays a 2026 body date despite its v1 URL and 2024 lineage; do not attribute every inspected statement to the final proceedings without comparison. The register also flags BIR-D numerical/kernel-setting reconciliation. No paper PDFs are redistributed.

## Implication for the proposed contribution

The umbrella topic remains **Physics-Informed Deep Learning for Robust Image Reconstruction Under Forward-Model Mismatch**. The candidate question remains:

> Can accounting for uncertainty in an estimated forward operator improve the reliability of selectively released image detail when the true acquisition process leaves the assumed model family?

**Novelty remains unestablished.** This batch strengthens the comparator set rather than proving an absence in the literature. Prior uncertainty, calibration, mismatch and fallback competitors in checkpoints 01–04 remain essential.

Our design inference is to keep four distinctions explicit: degradation features versus physical parameters; parameter point estimates versus a distribution; posterior variation versus validated calibration; and choosing a restoration task versus withholding unreliable detail. Tests should separately name content shift, operator shift, compound corruptions and adaptation data. These are comparison requirements, not newly demonstrated results.

## Retrieval correction and work remaining

The P017 retrieval entry in checkpoint 04 used the wrong arXiv identifier. DDNM is [arXiv 2212.00490](https://arxiv.org/abs/2212.00490), already present in the seed metadata. The unrelated locator supplied no eligibility evidence. This checkpoint explicitly supersedes that historical retrieval entry; P017 remains pending after corrected routes failed.

P073 and P088 also remain pending after unsuccessful HTML attempts. Alternate routes resolved access for P012/P074/P079/P083. Access failure is not an exclusion, and alternative sources are not exhausted.

Continue the existing full-text workflow for **37 remaining records**. Human adjudication, final-version comparison, lineage questions, formal database searches and flagged quality checks remain on the [deferred-work list](deferred_review_tasks.md). No new screening stage has been introduced, and accessible reading does not wait on the user's deferred actions.

The workbook, tracker and four reference exports are synchronized. All 90 seed IDs and earlier decisions are retained. See the [field-level audit](full_text_05_changes.json) and [migration script](../../scripts/update_full_text_05.mjs).
