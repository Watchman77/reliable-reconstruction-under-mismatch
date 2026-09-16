# Full-text checkpoint 09 — 16 September 2026

**84 of 90 seed records now have AI full-text eligibility assessments: 83 include recommendations and 1 exclude recommendation (P060). Six remain pending.** All ten records pending at checkpoint 08 received retrieval attempts; four yielded sufficient full-text evidence. The retrieval pass is complete, but full-text screening is not.

This continues protocol v0.4 and the existing 2020-01-01 through 2026-09-15 window. No new studies or screening stages were added. Human adjudication and formal database search/inclusion accounting remain pending. These are seed-record recommendations, not 84 formally included PRISMA studies.

The [register](full_text_09.json) specifies inspected versions, reading extent, five eligibility criteria, feature boundaries and source hashes. The [change audit](full_text_09_changes.json) records workbook edits and validation. Previous checkpoints preserve their historical counts.

## Four new assessments

| ID | Recommendation | Evidence and implication |
|---|---|---|
| P044 | Include | Joint image/PSF estimation uses forward consistency; training still needs calibration targets. Unseen-noise testing does not prove held-out-PSF transfer. [WACV paper](https://openaccess.thecvf.com/content/WACV2021/papers/Rego_Robust_Lensless_Image_Reconstruction_via_PSF_Estimation_WACV_2021_paper.pdf) |
| P055 | Include | Joint low-light, blur and noise restoration already has a simulator and real-night evaluation. Unpaired image-quality scores do not certify recovered details. [LEDNet v2](https://arxiv.org/pdf/2202.03373v2) |
| P058 | Include | RealVSR provides captured video pairs and cross-phone tests; reference misalignment and severe-case exclusions limit the benchmark. [ICCV paper](https://openaccess.thecvf.com/content/ICCV2021/papers/Yang_Real-World_Video_Super-Resolution_A_Benchmark_Dataset_and_a_Decomposition_Based_ICCV_2021_paper.pdf) |
| P073 | Include | AutoDIR predicts degradation categories and can stop on its clean class. Structural comparisons and perceptual gains do not establish calibrated, observation-supported detail. [ECCV paper](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/05684.pdf) |

Only the register's listed feature fields are verified. Unlisted fields remain provisional. Four PDFs were acquired for reading; paper content is not committed. Eligibility assessment is not independent reproduction of results or a complete supplementary/code audit.

## Six pending full texts

| ID | Paper / canonical source | Current obstacle | What resolves it |
|---|---|---|---|
| P029 | [Robust Unrolled Network for Lensless Imaging](https://doi.org/10.1364/OE.531694) | Publisher verification page; no full text acquired | Publisher PDF or author manuscript |
| P030 | [Empirical Bayesian Imaging With Large-Scale Push-Forward Generative Priors](https://doi.org/10.1109/LSP.2024.3361806) | Institutional PDF HTTP 403; attempted IEEE route HTTP 418 | Accepted manuscript or publisher PDF |
| P035 | [Mitigating Forward Model Mismatch via Learned Residuals and Diffusion Priors](https://doi.org/10.1117/12.3098133) | Publisher request unsuccessful; institution offers metadata/abstract | Full SPIE proceedings paper |
| P040 | [Video Diffusion Posterior Sampling](https://doi.org/10.1109/TPAMI.2025.3598457) | IEEE PDF unavailable; author code does not include paper | TPAMI paper or author manuscript |
| P049 | [DeepVibes](https://doi.org/10.1109/TGRS.2024.3415372) | HAL access challenge; IEEE/OpenReview retrieval unsuccessful | HAL manuscript or publisher PDF |
| P053 | [FaverNet](https://doi.org/10.1007/s11263-026-02977-y) | Abstract and first-page preview; author repository contains code | Full IJCV article; then reconcile P026 lineage |

The register preserves attempted URLs and observed outcomes. Access failure is not exclusion. Other legitimate sources may exist; no universal claim of inaccessibility is made. A new copy can be assessed immediately without restarting completed work. The unrelated arXiv 2508.01975 survey was rejected as a P040 locator.

## Implication for the research question

**Retain the umbrella topic and candidate question; novelty remains unestablished.** This is a synthesis inference, not a claim that the remaining papers have been ruled out.

The proposed selective-release mechanism must be compared with both simple quality/task stopping and the previously assessed reliability/certificate methods. Physical-parameter uncertainty, categorical degradation scores, perceptual image quality and calibrated error risk must be evaluated separately. AutoDIR receives only partial categorical/stopping credit; its clean-class decision supplies no demonstrated risk guarantee.

The next feasible analysis is to specify the release unit, acceptable error, validation-only calibration rule and out-of-family test before adding architecture components. Complete the six missing assessments and existing version/lineage follow-ups before making a definitive novelty claim. The [deferred work list](deferred_review_tasks.md) preserves the user's pending tasks; no new approval is required for accessible work.
