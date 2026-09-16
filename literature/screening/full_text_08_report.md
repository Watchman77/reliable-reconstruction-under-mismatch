# Full-text checkpoint 08 — 16 September 2026

Ten additional AI eligibility assessments are complete, all recommending inclusion. Cumulative progress is **80 of 90 assessed: 79 include recommendations, 1 exclude, 10 pending**. Human adjudication remains outstanding; formal search/inclusion counters remain zero.

The [criterion-level register](full_text_08.json) records inspected versions, reading extent, sources, feature decisions and follow-ups. Protocol v0.4 and its date window are unchanged. Eligibility assessment does not certify every proof, appendix or implementation. Only listed feature fields are verified; “No” means not demonstrated in the inspected evidence.

## Evidence added

| Seed | Inspected primary text | Boundary relevant to our comparison |
|---|---|---|
| P013 | [AirNet](https://openaccess.thecvf.com/content/CVPR2022/papers/Li_All-in-One_Image_Restoration_for_Unknown_Corruption_CVPR_2022_paper.pdf), CVPR 2022 | Pooled restoration tasks do not establish compound corruption per image. |
| P021 | [Differentiable Uncalibrated Imaging](https://arxiv.org/pdf/2211.10525v3), arXiv v3 | Acquisition-coordinate estimates are not uncertainty distributions. |
| P032 | [UA-FP](https://pmc.ncbi.nlm.nih.gov/articles/PMC12234902/), published article | Joint system correction does not demonstrate probability calibration; provisional P/Q/R codes are corrected. |
| P043 | [Model Adaptation](https://arxiv.org/pdf/2012.00139v2), arXiv v2 | Known-operator adaptation and blind estimation require separate comparisons. |
| P046 | [Adaptive Reconstruction Networks](https://arxiv.org/pdf/2202.11342v3), arXiv v3 | Operator-family training is established; blind deblurring kernel estimation fails in the reported experiment. |
| P059 | [BSD/ESTRNN](https://arxiv.org/pdf/2106.16028v2), expanded arXiv v2 | Captured-video transfer tests expose limitations of synthetic blur/noise. |
| P061 | [S3-CLIP](https://arxiv.org/pdf/2601.08807v1), arXiv v1 | Recognition gains vary by direction; they do not certify reconstructed detail. |
| P068 | [Correction Filter](https://openaccess.thecvf.com/content_CVPR_2020/papers/Abu_Hussein_Correction_Filter_for_Single_Image_Super-Resolution_Robustifying_Off-the-Shelf_Deep_Super-Resolvers_CVPR_2020_paper.pdf), CVPR 2020 | The linear exact-recovery motivation is conditional; the full published title is restored. |
| P071 | [ADMS](https://openaccess.thecvf.com/content/CVPR2023/papers/Park_All-in-One_Image_Restoration_for_Unknown_Degradations_Using_Adaptive_Discriminative_Filters_CVPR_2023_paper.pdf), CVPR 2023 | Soft degradation-type weights receive partial credit, without a calibration claim. |
| P090 | [Upscale-A-Video](https://openaccess.thecvf.com/content/CVPR2024/papers/Zhou_Upscale-A-Video_Temporal-Consistent_Diffusion_Model_for_Real-World_Video_Super-Resolution_CVPR_2024_paper.pdf), CVPR 2024 | Flow-based propagation rejection differs from withholding unreliable output detail. |

## Implication for the proposed contribution

The umbrella remains **Physics-Informed Deep Learning for Robust Image Reconstruction Under Forward-Model Mismatch**. The candidate question remains:

> Can accounting for uncertainty in an estimated forward operator improve the reliability of selectively released image detail when the true acquisition process leaves the assumed model family?

**Novelty remains unestablished.** Our synthesis inference is that the experiment must distinguish physical parameter estimation, categorical degradation inference, uncertainty calibration and selective output. A combination of these labels is not itself a contribution. Earlier posterior-mismatch, calibration and fallback competitors remain necessary comparisons.

This batch strengthens the need to report failures as well as average reconstruction gains. The later feasibility experiment should separate parameter changes within a model family from changes that invalidate the family, and compare calibrated output decisions with simple restoration and adaptation baselines. This is a proposed experimental requirement, not a demonstrated result of our own system.

## Progress and remaining work

Nine PDFs were retrieved for assessment. UA-FP was inspected using the published HTML and public full-article XML archive; its PDF-acquisition flag is not upgraded. Versions and content hashes preserve provenance. No paper content is redistributed.

**10 seeds remain:** P029, P030, P035, P040, P044, P049, P053, P055, P058 and P073. Failed routes and unresolved publication lineage are recorded in the register and [deferred-work list](deferred_review_tasks.md). These are pending assessments, not exclusions. Alternate public routes remain to investigate.

Human adjudication, formal database searches, lineage reconciliation and source-specific quality follow-ups remain deferred. No new screening stage has been introduced. All 90 seed IDs and previous decisions are preserved; the matrix, tracker and four reference exports are synchronized. See the [field-level audit](full_text_08_changes.json) and [migration script](../../scripts/update_full_text_08.mjs).
