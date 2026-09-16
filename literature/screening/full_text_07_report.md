# Full-text checkpoint 07 — 16 September 2026

Ten additional AI eligibility assessments are complete, all recommending inclusion. Cumulative progress is **70 of 90 assessed: 69 include recommendations, 1 exclude, 20 pending**. Human adjudication remains outstanding; formal search/inclusion counters remain zero.

The [criterion-level register](full_text_07.json) records inspected versions, reading extent, source links, evidence and follow-ups. Protocol v0.4 and its date window are unchanged. An eligibility assessment does not certify every proof, appendix or implementation. Only explicitly listed feature codes are verified; “No” means not demonstrated in the inspected evidence.

## Evidence added

| Seed | Inspected primary text | Boundary relevant to our comparison |
|---|---|---|
| P001 | [Kernel/model uncertainty](https://raw.githubusercontent.com/ysnan/NBD_KerUnc/master/paper/kn.pdf), author manuscript | Learned residual compensation does not identify a unique physical kernel. |
| P004 | [RealBlur](https://cg.postech.ac.kr/research/RealBlur/assets/pdf/RealBlur_eccv2020.pdf), author manuscript | Captured pairs involve target preprocessing and static-scene assumptions. |
| P009 | [BSRGAN](https://arxiv.org/pdf/2103.14006v2), arXiv v2 | Compound degradation training already has a practical comparator. |
| P016 | [ΠGDM](https://jankautz.com/publications/PiGDM_ICLR23.pdf), ICLR 2023 author copy | Conditional image sampling uses supplied measurement maps. |
| P017 | [DDNM](https://arxiv.org/pdf/2212.00490v2), arXiv v2 | Range-space consistency leaves ambiguity in generated detail. |
| P025 | [DiffBIR](https://arxiv.org/html/2308.15070v3), arXiv v3 | Fidelity guidance follows a restored image, without calibrated abstention. |
| P027 | [SR+Codec](https://bmva-archive.org.uk/bmvc/2024/papers/Paper_959/paper.pdf), proceedings | Codec/downsampling tests do not reproduce a captured CCTV pipeline. |
| P031 | [The Troublesome Kernel](https://arxiv.org/html/2001.01258v4), arXiv v4 | Hallucination results require their stated operator and stability assumptions. |
| P069 | [Generative blind deconvolution](https://arxiv.org/pdf/1802.04073v4), arXiv v4 | Joint image/kernel point estimation precedes our proposed work. |
| P088 | [StableSR](https://arxiv.org/pdf/2305.07015v4), expanded arXiv v4 | User-controlled fidelity is different from uncertainty-based selective release. |

P069 remains the existing **2020 journal lineage**, confirmed by matching title/authors and print year in [publisher-deposited Crossref metadata](https://api.crossref.org/works/10.1109/TCI.2020.3032671). The inspected precursor is dated 2019. Its equivalence to the final journal report has not been assumed; no new pre-2020 seed has been added.

## Implication for the proposed contribution

The umbrella remains **Physics-Informed Deep Learning for Robust Image Reconstruction Under Forward-Model Mismatch**. The candidate question remains:

> Can accounting for uncertainty in an estimated forward operator improve the reliability of selectively released image detail when the true acquisition process leaves the assumed model family?

**Novelty remains unestablished.** Our synthesis inference is that evaluation must distinguish four capabilities: compensating for an incorrect model, estimating physical parameters, quantifying uncertainty and withholding unreliable detail. A result in one category does not establish the others. Existing uncertainty/calibration and fallback competitors from earlier checkpoints remain essential comparisons.

This batch adds comparators and assumptions; it does not demonstrate that the complete candidate question is either solved or novel. The register flags version reconciliation, target preprocessing, generator-range evaluation, manual inputs, metric selection and user-study consistency before quantitative reuse.

## Progress and remaining work

P016, the last initially unclear seed, now has an AI full-text recommendation. **All eight initially unclear cases have progressed**, while their original triage labels remain intact.

Seven PDFs were retrieved for assessment. Acquisition flags and SHA-256 hashes are recorded; the papers are not redistributed. P025/P027/P031 were inspected online. Earlier access failures for newly assessed records remain historical entries, not current blocks. A further P073 web-reader attempt failed; alternative sources remain available to investigate.

**20 seeds remain:** P013, P021, P029, P030, P032, P035, P040, P043, P044, P046, P049, P053, P055, P058, P059, P061, P068, P071, P073 and P090. These are pending assessments, not exclusions.

Human adjudication, formal database searches, lineage reconciliation and source-specific quality checks remain on the [deferred-work list](deferred_review_tasks.md). Accessible assessment continues without waiting on user actions. No new screening stage has been introduced.

The matrix, tracker and four reference exports are synchronized. All 90 seed IDs and earlier decisions remain intact. See the [field-level audit](full_text_07_changes.json) and [migration script](../../scripts/update_full_text_07.mjs).
