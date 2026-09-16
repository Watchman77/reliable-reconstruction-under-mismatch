# Seed screening completed: P001–P090

Checked 16 September 2026 under working protocol v0.3. This checkpoint completes the **initial AI-assisted triage of the 90 seed records**. It does not represent 90 full-paper reviews or a completed systematic review.

| Status | Previous checkpoint | This batch | Cumulative |
|---|---:|---:|---:|
| Initial recommendations recorded | 40 | 50 | **90** |
| Advance to full-text assessment | 38 | 44 | **82** |
| Unclear: scope or access needs resolution | 2 | 6 | **8** |
| Seed records without an initial recommendation | 50 | −50 | **0** |
| Complete formal full-text eligibility assessments | 0 | 0 | **0** |
| Formally included / excluded | 0 / 0 | 0 / 0 | **0 / 0** |

There is no additional batch of untriaged seed records. Every recommendation has an evidence basis, source, scope rationale and a specific full-text question. All human adjudication remains pending. The first two batches and their original decisions remain preserved; [pilot_03.json](pilot_03.json) records the final 50 and five revisits. The workbook's Screening Log is the cumulative tracker.

## What this changes for our research

Retain the umbrella topic **Physics-Informed Deep Learning for Robust Image Reconstruction Under Forward-Model Mismatch**. Its components are established research areas. A publishable contribution requires a demonstrated limitation of the nearest methods and evidence that our proposed mechanism addresses it.

The final batch adds direct competitors to the narrower reliability question:

| Record | Evidence already present | What still requires comparison |
|---|---|---|
| P042 No-Harm | Residual certificates govern replacement of a baseline, including fallback. Selected discussion and limitations distinguish certificate dominance from actual-error dominance. | Stability/admissible-class assumptions and uncertain observation operators; controlled tests do not establish arbitrary-mismatch deployment guarantees. [Author text, §§9–10](https://arxiv.org/html/2606.07153v1) |
| P048 PnP posterior mismatch | Posterior sensitivity to measurement and denoiser mismatch is already analyzed. | Whether its distance bounds support calibrated or selective decisions under our acquisition conditions. [ICLR abstract](https://proceedings.iclr.cc/paper_files/paper/2024/hash/2a2874875861f6a6436b505dd77683d1-Abstract-Conference.html) |
| P064 Inexact nanoCT | Inexact operators and uncertainty-aware reconstruction are already compared. | Operator distribution, calibration and behavior when the assumed family is wrong. [Author abstract](https://arxiv.org/abs/2307.10474) |
| P066 Self-supervised conformal | Calibration using noisy measurements without clean targets is already proposed. | Validity of its noise/operator assumptions under deployment mismatch. [SSVM abstract](https://link.springer.com/chapter/10.1007/978-3-031-92366-1_9) |
| P062/P063/P065/P067 | Risk control, task-level intervals and several forms of conformal image uncertainty are established. | Guarantee units, calibration assumptions and operator-shift experiments; do not equate pixel-marginal coverage with every-image reliability. See the record-level source links below. |
| P053/P070 | All-in-one video restoration already addresses changing or combined degradation. | Detailed train/test separation, physical fidelity, and study lineage. [FaverNet](https://link.springer.com/article/10.1007/s11263-026-02977-y), [language-grounded video restoration](https://arxiv.org/abs/2507.14851) |

These findings add to the earlier targeted evidence for PRISM, AverNet and VDPS in [pilot_02_report.md](pilot_02_report.md). They rule out claiming novelty merely for adding uncertainty, fallback or changing degradation to a reconstruction pipeline. They do **not** establish that the precise candidate question has already been solved, or that it is novel.

The candidate question remains:

> Can accounting for uncertainty in an estimated forward operator improve the reliability of selectively released image detail when the true acquisition process leaves the assumed model family?

Treat this as a hypothesis to test. Establish the precise estimand, assumptions, reference baselines and failure regime before committing to a new architecture. A missing intersection of many feature labels is not evidence of novelty.

## Eight unresolved recommendations

These records have been checked and assigned an explicit decision; they are not untouched records. None is formally excluded.

| ID | Remaining issue | Resolution required |
|---|---|---|
| P006 | Known-operator deep-equilibrium reconstruction is clear; protocol criterion 3 remains uncertain. | Check explicit mismatch, uncertainty or reliability experiments; retain as a baseline if outside primary synthesis. |
| P016 | Complete abstract/technical text could not be retrieved despite OpenReview and author-source attempts. | Obtain the paper and assess criterion 3. Missing access is not an exclusion. |
| P060 | CCTV image-quality dataset; reconstruction centrality is uncertain. | Decide whether its evaluation supports criteria 2/4 or belongs in contextual background. |
| P072 | Degradation-perception architecture across tasks; blind/compound/OOD setting not established from inspected material. | Inspect training setup and experiments against criterion 3. |
| P082 | General differentiable inverse solver; relevant mismatch/reliability experiment not established from abstract. | Inspect that evidence rather than infer relevance from general inverse reconstruction. |
| P084 | Diffusion-prior MAP solver; handling noise alone does not establish criterion 3. | Check explicit blind, mismatch, uncertainty or fidelity-support analysis. |
| P086 | Data-fidelity and regularization calibration; statistical reliability not established. | Check whether measurement support is assessed beyond the optimization objective. |
| P087 | Linear consistency and residual-energy matching under an assumed model. | Check incorrect-model experiments or reconstruction uncertainty/calibration. |

Advancement also does not mean complete source access. P001, P013, P032, P049 and P071 retain conservative advance recommendations with incomplete abstract/technical retrieval. Their title, repository or indexed primary-source evidence is documented. P032's legacy positive uncertainty/calibration codes remain unverified. Do not use them as established capabilities.

## Reference and lineage repairs

- **P050 LADiBI:** corrected the seed venue from NeurIPS to **SPIGM at NeurIPS 2025 (workshop)** using the [coauthor's publication listing](https://kellyyutonghe.github.io/). The legacy peer-review flag is not a newly verified review-process claim.
- **P052 CaMB-Diff:** retained ICML with a more precise evidence note. A [coauthor explicitly announces acceptance](https://iwuqing.github.io/); the final proceedings/OpenReview metadata remain to be checked. This updates the earlier audit's absence of acceptance evidence without presenting an author announcement as a fetched version of record.
- **P074 DA-CLIP:** current author materials and [official ICLR slides](https://iclr.cc/media/iclr-2024/Slides/17626.pdf) use **Multi-Task Image Restoration**. The older **Universal Image Restoration** wording is a title alias for the same record, not a new paper.
- **P088 StableSR:** corrected the DOI to **10.1007/s11263-024-02168-7**, verified on the [publisher page](https://link.springer.com/article/10.1007/s11263-024-02168-7). The old DOI ending `02092-y` must not be used.
- **P026/P053:** compare AverNet and FaverNet for possible conference/journal lineage before counting independent studies. Similar authors and subject matter justify checking; they do not alone justify merging.

No seed ID was added, removed or silently merged. Metadata/status corrections are recorded in [pilot_03_changes.json](pilot_03_changes.json) and propagated to the workbook and CSV/BibTeX/RIS/Markdown exports. Those exports remain draft references; many author lists are abbreviated and some final publication details still need verification.

## Full-text completion plan

1. Resolve the eight cases above and the incomplete-source advances. Keep retrieval failures separate from irrelevance decisions.
2. Complete eligibility and evidence extraction for every advancing record. Begin the novelty comparison with P038/P042/P048/P064/P066, then P026/P040/P053/P070 and the conformal-risk group. This prioritizes work; it does not waive assessment of other advancing records.
3. For each assessed paper, record eligibility criteria, one primary exclusion reason if excluded, exact sections supporting feature codes, operator assumptions, data/splits, uncertainty definition, calibration target, limitations and reproducibility evidence.
4. Execute and preserve reproducible database searches, deduplication and citation chaining before freezing a formal corpus. These 90 targeted seed lookups do not replace database exports or establish literature completeness.
5. Apply the protocol's human verification and disagreement procedure before publication. No AI recommendation is represented as independent human review.

Complete formal full-text assessments remaining at this checkpoint: **90 seed records have no completed assessment**; 82 are recommended to advance and 8 await resolution. Some may later be excluded, merged as reports of one study, or retained only as background. Formal counts should follow those decisions, not a target of 90 included studies.

## P041–P090 decision register

The linked source is the evidence locator, which may differ from the final citation. “Advance” means proceed to full-text assessment; “unclear” preserves a specific unresolved issue. Detailed evidence limits and questions are in the companion JSON.

| ID / source | Publication | Recommendation | Evidence inspected |
|---|---|---|---|
| [P041](https://arxiv.org/abs/2511.18473) | Uncertainty Quantification in HSI Reconstruction using Physics-Aware Diffusion Priors and Optics-Encoded Measurements | advance | Abstract inspected; full-text pending |
| [P042](https://arxiv.org/html/2606.07153v1) | No-Harm Physics-Informed Inverse Learning with Residual-Calibrated Uncertainty | advance | Targeted full-text sections inspected |
| [P043](https://arxiv.org/abs/2012.00139) | Model Adaptation for Inverse Problems in Imaging | advance | Abstract inspected; full-text pending |
| [P044](https://asu.elsevierpure.com/en/publications/robust-lensless-image-reconstruction-via-psf-estimation/) | Robust Lensless Image Reconstruction via PSF Estimation | advance | Abstract inspected; full-text pending |
| [P045](https://proceedings.neurips.cc/paper_files/paper/2023/hash/f810c2ba07bae78dfe9d25c5d40c5536-Abstract-Conference.html) | Block Coordinate Plug-and-Play Methods for Blind Inverse Problems | advance | Abstract inspected; full-text pending |
| [P046](https://arxiv.org/abs/2202.11342) | Training Adaptive Reconstruction Networks for Blind Inverse Problems | advance | Abstract inspected; full-text pending |
| [P047](https://arxiv.org/abs/2403.04847) | Solving Inverse Problems with Model Mismatch using Untrained Neural Networks within Model-based Architectures | advance | Abstract inspected; full-text pending |
| [P048](https://proceedings.iclr.cc/paper_files/paper/2024/hash/2a2874875861f6a6436b505dd77683d1-Abstract-Conference.html) | Plug-and-Play Posterior Sampling under Mismatched Measurement and Prior Models | advance | Abstract inspected; full-text pending |
| [P049](https://ieeexplore.ieee.org/document/10559627/) | DeepVibes: Correcting Micro-Vibrations in Satellite Imaging With Pushbroom Cameras | advance | Incomplete evidence; retrieval pending |
| [P050](https://arxiv.org/abs/2412.00557) | Blind Inverse Problem Solving Made Easy by Text-to-Image Latent Diffusion | advance | Abstract inspected; full-text pending |
| [P051](https://arxiv.org/abs/2411.16535) | ADOBI: Adaptive Diffusion Bridge For Blind Inverse Problems with Application to MRI Reconstruction | advance | Abstract inspected; full-text pending |
| [P052](https://arxiv.org/abs/2603.01890) | Resolving Blind Inverse Problems under Dynamic Range Compression via Structured Forward Operator Modeling | advance | Abstract inspected; full-text pending |
| [P053](https://link.springer.com/article/10.1007/s11263-026-02977-y) | FaverNet: All-in-One Video Restoration via Frequency-Discriminative Conditioning | advance | Abstract inspected; full-text pending |
| [P054](https://arxiv.org/abs/2408.14916) | Towards Real-world Event-guided Low-light Video Enhancement and Deblurring | advance | Abstract inspected; full-text pending |
| [P055](https://arxiv.org/abs/2202.03373) | LEDNet: Joint Low-Light Enhancement and Deblurring in the Dark | advance | Abstract inspected; full-text pending |
| [P056](https://arxiv.org/abs/2111.12704) | Investigating Tradeoffs in Real-World Video Super-Resolution | advance | Abstract inspected; full-text pending |
| [P057](https://arxiv.org/abs/2305.02660) | Expanding Synthetic Real-World Degradations for Blind Video Super Resolution | advance | Abstract inspected; full-text pending |
| [P058](https://research.polyu.edu.hk/en/publications/real-world-video-super-resolution-a-benchmark-dataset-and-a-decom/) | Real-world Video Super-resolution: A Benchmark Dataset and a Decomposition Based Learning Scheme | advance | Abstract inspected; full-text pending |
| [P059](https://link.springer.com/article/10.1007/s11263-022-01705-6) | Real-World Video Deblurring: A Benchmark Dataset and an Efficient Recurrent Neural Network | advance | Abstract inspected; full-text pending |
| [P060](https://www.jmis.org/archive/view_article?pid=jmis-12-3-81) | CQAD: An Image Quality Assessment Dataset for CCTV | unclear | Abstract inspected; full-text pending |
| [P061](https://arxiv.org/abs/2601.08807) | S3-CLIP: Video Super Resolution for Person-ReID | advance | Abstract and repository inspected |
| [P062](https://proceedings.mlr.press/v202/teneggi23a.html) | How to Trust Your Diffusion Model: A Convex Optimization Approach to Conformal Risk Control | advance | Abstract inspected; full-text pending |
| [P063](https://arxiv.org/abs/2405.18527) | Task-Driven Uncertainty Quantification in Inverse Problems via Conformal Prediction | advance | Abstract inspected; full-text pending |
| [P064](https://arxiv.org/abs/2307.10474) | Learning-Based Approaches for Reconstructions With Inexact Operators in nanoCT Applications | advance | Abstract inspected; full-text pending |
| [P065](https://arxiv.org/abs/2504.07696) | Conformalized Generative Bayesian Imaging: An Uncertainty Quantification Framework for Computational Imaging | advance | Abstract inspected; full-text pending |
| [P066](https://link.springer.com/chapter/10.1007/978-3-031-92366-1_9) | Self-supervised Conformal Prediction for Uncertainty Quantification in Imaging Problems | advance | Abstract inspected; full-text pending |
| [P067](https://arxiv.org/abs/2507.14760) | QUTCC: Quantile Uncertainty Training and Conformal Calibration for Imaging Inverse Problems | advance | Abstract inspected; full-text pending |
| [P068](https://arxiv.org/abs/1912.00157) | Correction Filter for Single Image Super-Resolution | advance | Abstract inspected; full-text pending |
| [P069](https://arxiv.org/abs/1802.04073) | Blind Image Deconvolution Using Deep Generative Priors | advance | Abstract inspected; full-text pending |
| [P070](https://arxiv.org/abs/2507.14851) | Grounding Degradations in Natural Language for All-In-One Video Restoration | advance | Abstract inspected; full-text pending |
| [P071](https://openaccess.thecvf.com/content/CVPR2023/html/Park_All-in-One_Image_Restoration_for_Unknown_Degradations_Using_Adaptive_Discriminative_Filters_CVPR_2023_paper.html) | All-in-One Image Restoration for Unknown Degradations Using Adaptive Discriminative Filters for Specific Degradations | advance | Title/project checked; abstract pending |
| [P072](https://proceedings.neurips.cc/paper_files/paper/2023/file/1c364d98a5cdc426fd8c76fbb2c10e34-Paper-Conference.pdf) | PromptRestorer: A Prompting Image Restoration Method with Degradation Perception | unclear | Abstract inspected; full-text pending |
| [P073](https://arxiv.org/abs/2310.10123) | AutoDIR: Automatic All-in-One Image Restoration with Latent Diffusion | advance | Abstract inspected; full-text pending |
| [P074](https://arxiv.org/abs/2310.01018) | Controlling Vision-Language Models for Multi-Task Image Restoration | advance | Abstract and repository inspected |
| [P075](https://arxiv.org/abs/2312.02918) | Multimodal Prompt Perceiver: Empower Adaptiveness, Generalizability and Fidelity for All-in-One Image Restoration | advance | Abstract inspected; full-text pending |
| [P076](https://arxiv.org/abs/2401.16468) | InstructIR: High-Quality Image Restoration Following Human Instructions | advance | Abstract inspected; full-text pending |
| [P077](https://proceedings.neurips.cc/paper_files/paper/2024/file/c78f639424b8d89ceb4f2efbb4dfe4f4-Paper-Conference.pdf) | RestoreAgent: Autonomous Image Restoration Agent via Multimodal Large Language Models | advance | Abstract inspected; full-text pending |
| [P078](https://arxiv.org/abs/2410.18666) | DreamClear: High-Capacity Real-World Image Restoration with Privacy-Safe Dataset Curation | advance | Abstract inspected; full-text pending |
| [P079](https://proceedings.neurips.cc/paper_files/paper/2024/hash/25869dbf7682272357bc2cbbf860e1c8-Abstract-Conference.html) | Taming Generative Diffusion Prior for Universal Blind Image Restoration | advance | Abstract inspected; full-text pending |
| [P080](https://arxiv.org/abs/2304.01247) | Generative Diffusion Prior for Unified Image Restoration and Enhancement | advance | Abstract inspected; full-text pending |
| [P081](https://proceedings.neurips.cc/paper_files/paper/2024/hash/b213d9a999b82cb6fcd03a0d5a7498be-Abstract-Conference.html) | A Modular Conditional Diffusion Framework for Image Reconstruction | advance | Abstract inspected; full-text pending |
| [P082](https://proceedings.neurips.cc/paper_files/paper/2024/hash/86655bc516148e311bcfcf88f1744de7-Abstract-Conference.html) | Solving Inverse Problems via Diffusion Optimal Control | unclear | Abstract inspected; full-text pending |
| [P083](https://proceedings.neurips.cc/paper_files/paper/2024/hash/3fa2d2b637122007845a2fbb7c21453b-Abstract-Conference.html) | Provably Robust Score-Based Diffusion Posterior Sampling for Plug-and-Play Image Reconstruction | advance | Abstract inspected; full-text pending |
| [P084](https://proceedings.neurips.cc/paper_files/paper/2024/hash/54fa8255cdf30736ecad38e842725e7f-Abstract-Conference.html) | Unleashing the Denoising Capability of Diffusion Prior for Solving Inverse Problems | unclear | Abstract inspected; full-text pending |
| [P085](https://proceedings.neurips.cc/paper_files/paper/2025/hash/33367b9ff199d26280db6cf539d1125c-Abstract-Conference.html) | InvFusion: Bridging Supervised and Zero-shot Diffusion for Inverse Problems | advance | Abstract inspected; full-text pending |
| [P086](https://proceedings.neurips.cc/paper_files/paper/2025/hash/c7ae6e9659f0c99582c2e8214ba0b413-Abstract-Conference.html) | Solving Inverse Problems with FLAIR | unclear | Abstract inspected; full-text pending |
| [P087](https://proceedings.neurips.cc/paper_files/paper/2025/hash/d92d3aec6a48e93f93194503ee49f11a-Abstract-Conference.html) | Linearly Constrained Diffusion Implicit Models | unclear | Abstract inspected; full-text pending |
| [P088](https://link.springer.com/article/10.1007/s11263-024-02168-7) | Exploiting Diffusion Prior for Real-World Image Super-Resolution | advance | Abstract inspected; full-text pending |
| [P089](https://arxiv.org/abs/2311.16518) | SeeSR: Towards Semantics-Aware Real-World Image Super-Resolution | advance | Abstract inspected; full-text pending |
| [P090](https://arxiv.org/abs/2312.06640) | Upscale-A-Video: Temporal-Consistent Diffusion Model for Real-World Video Super-Resolution | advance | Abstract inspected; full-text pending |
