# Evidence inventory for provisional synthesis 01

As of 2026-09-16; generated from full_text_11 and earlier full-text registers.

**90 seed records; 89 assessed; 88 AI include recommendations; 1 AI exclude recommendation; 1 pending. Formal included/excluded: 0/0.**

The main provisional synthesis uses the 88 include recommendations. P060 is ancillary; P035 contributes no full-text claims. These are record counts, not final PRISMA counts or independent-study counts.

## Extraction coverage

Every row has denominator 88. Missing extraction is not a negative finding. Yes indicates recorded evidence within its stated scope; calibration tested does not mean calibration succeeded. No means not demonstrated in the inspected evidence. Do not treat these counts as prevalence estimates.

| Field | Yes | Partial | No | Not extracted |
|---|---:|---:|---:|---:|
| Joint image/operator inference | 22 | 6 | 48 | 12 |
| Image uncertainty | 31 | 1 | 42 | 14 |
| Operator uncertainty | 3 | 2 | 81 | 2 |
| Calibration evaluated | 8 | 3 | 75 | 2 |
| Out-of-distribution test | 30 | 26 | 7 | 25 |
| Real measurements/hardware | 39 | 5 | 39 | 5 |
| Compound degradation | 55 | 0 | 5 | 28 |
| Time variation (legacy scope; see caveat) | 8 | 0 | 26 | 54 |
| Hallucination/support assessment | 4 | 24 | 6 | 54 |
| Abstention/selection | 1 | 3 | 76 | 8 |

## Interpretation limits

- P026, P053: Predecessor relationship confirmed in checkpoint 11; study-level grouping/shared experiments pending. Earlier P026 wording is historical.
- P064: Legacy Yes describes projection-dependent tomography motion, whereas the dictionary says video-sequence variation. Preserve the extraction; do not interpret this count as a homogeneous video count. Adjudication pending.
- P071, P073: Partial denotes categorical degradation weights, not a calibrated physical-parameter posterior.
- P042, P063, P073, P077: Certificate fallback, acquisition stopping, clean-class stopping and rollback are different decisions; no pooled selective-risk performance follows.

Only three extracted records have Q=Yes: P018 (BlindDPS), P019 (GibbsDDRM), and P038 (PRISM). That observation identifies comparators; it does not establish that only three such methods exist. The JSON snapshot contains every counted ID and its evidence locator.

## Record index

Titles are carried from the draft reference export. The linked register is authoritative for the inspected source/version, reading extent and limitations. Unassessed P035 is linked to its metadata page only.

| ID | Title | AI decision | Evidence register |
|---|---|---|---|
| P001 | [Deep Learning for Handling Kernel/Model Uncertainty in Image Deconvolution](https://raw.githubusercontent.com/ysnan/NBD_KerUnc/master/paper/kn.pdf) | include | [full_text_07](../screening/full_text_07.json) |
| P002 | [NETT: Solving Inverse Problems with Deep Neural Networks](https://arxiv.org/pdf/1803.00092) | include | [full_text_06](../screening/full_text_06.json) |
| P003 | [On Instabilities of Deep Learning in Image Reconstruction and the Potential Costs of AI](https://arxiv.org/pdf/1902.05300) | include | [full_text_06](../screening/full_text_06.json) |
| P004 | [Real-World Blur Dataset for Learning and Benchmarking Deblurring Algorithms](https://cg.postech.ac.kr/research/RealBlur/assets/pdf/RealBlur_eccv2020.pdf) | include | [full_text_07](../screening/full_text_07.json) |
| P005 | [Robust Reconstruction With Deep Learning to Handle Model Mismatch in Lensless Imaging](https://www.eee.hku.hk/optima/pub/journal/2109_TCI.pdf) | include | [full_text_04](../screening/full_text_04.json) |
| P006 | [Deep Equilibrium Architectures for Inverse Problems in Imaging](https://arxiv.org/pdf/2102.07944) | include | [full_text_01](../screening/full_text_01.json) |
| P007 | [Deep Probabilistic Imaging: Uncertainty Quantification and Multi-modal Solution Characterization for Computational Imaging](https://ojs.aaai.org/index.php/AAAI/article/view/16366/16173) | include | [full_text_03](../screening/full_text_03.json) |
| P008 | [On Hallucinations in Tomographic Image Reconstruction](https://arxiv.org/html/2012.00646v3) | include | [full_text_04](../screening/full_text_04.json) |
| P009 | [Designing a Practical Degradation Model for Deep Blind Image Super-Resolution](https://arxiv.org/pdf/2103.14006v2) | include | [full_text_07](../screening/full_text_07.json) |
| P010 | [Real-ESRGAN: Training Real-World Blind Super-Resolution With Pure Synthetic Data](https://arxiv.org/html/2107.10833v2) | include | [full_text_03](../screening/full_text_03.json) |
| P011 | [Image-to-Image Regression with Distribution-Free Uncertainty Quantification and Applications in Imaging](https://proceedings.mlr.press/v162/angelopoulos22a/angelopoulos22a.pdf) | include | [full_text_03](../screening/full_text_03.json) |
| P012 | [Denoising Diffusion Restoration Models](https://arxiv.org/html/2201.11793v3) | include | [full_text_05](../screening/full_text_05.json) |
| P013 | [All-in-One Image Restoration for Unknown Corruption](https://openaccess.thecvf.com/content/CVPR2022/papers/Li_All-in-One_Image_Restoration_for_Unknown_Corruption_CVPR_2022_paper.pdf) | include | [full_text_08](../screening/full_text_08.json) |
| P014 | [Conffusion: Confidence Intervals for Diffusion Models](https://arxiv.org/html/2211.09795v1) | include | [full_text_04](../screening/full_text_04.json) |
| P015 | [Diffusion Posterior Sampling for General Noisy Inverse Problems](https://arxiv.org/html/2209.14687v4) | include | [full_text_04](../screening/full_text_04.json) |
| P016 | [Pseudoinverse-Guided Diffusion Models for Inverse Problems](https://jankautz.com/publications/PiGDM_ICLR23.pdf) | include | [full_text_07](../screening/full_text_07.json) |
| P017 | [Zero-Shot Image Restoration Using Denoising Diffusion Null-Space Model](https://arxiv.org/pdf/2212.00490v2) | include | [full_text_07](../screening/full_text_07.json) |
| P018 | [Parallel Diffusion Models of Operator and Image for Blind Inverse Problems](https://arxiv.org/html/2211.10656v1) | include | [full_text_03](../screening/full_text_03.json) |
| P019 | [GibbsDDRM: A Partially Collapsed Gibbs Sampler for Solving Blind Inverse Problems with Denoising Diffusion Restoration](https://proceedings.mlr.press/v202/murata23a/murata23a.pdf) | include | [full_text_03](../screening/full_text_03.json) |
| P020 | [PromptIR: Prompting for All-in-One Image Restoration](https://arxiv.org/html/2306.13090v1) | include | [full_text_05](../screening/full_text_05.json) |
| P021 | [Differentiable Uncalibrated Imaging](https://arxiv.org/pdf/2211.10525v3) | include | [full_text_08](../screening/full_text_08.json) |
| P022 | [Fast Diffusion EM: A Diffusion Model for Blind Inverse Problems With Application to Deconvolution](https://arxiv.org/html/2309.00287v2) | include | [full_text_03](../screening/full_text_03.json) |
| P023 | [Blind Image Restoration via Fast Diffusion Inversion](https://proceedings.neurips.cc/paper_files/paper/2024/file/3d13d910b48ac2e672a32cfdf98be1bf-Paper-Conference.pdf) | include | [full_text_03](../screening/full_text_03.json) |
| P024 | [Blind Inversion Using Latent Diffusion Priors](https://arxiv.org/html/2407.01027v1) | include | [full_text_03](../screening/full_text_03.json) |
| P025 | [DiffBIR: Toward Blind Image Restoration with Generative Diffusion Prior](https://arxiv.org/html/2308.15070v3) | include | [full_text_07](../screening/full_text_07.json) |
| P026 | [AverNet: All-in-One Video Restoration for Time-Varying Unknown Degradations](https://proceedings.neurips.cc/paper_files/paper/2024/file/e635a25e49e73adc51f76aef462ff2f8-Paper-Conference.pdf) | include | [full_text_02](../screening/full_text_02.json) |
| P027 | [SR+Codec: a Benchmark of Super-Resolution for Video Compression Bitrate Reduction](https://bmva-archive.org.uk/bmvc/2024/papers/Paper_959/paper.pdf) | include | [full_text_07](../screening/full_text_07.json) |
| P028 | [Scaling Up to Excellence: Practicing Model Scaling for Photo-Realistic Image Restoration In the Wild](https://arxiv.org/html/2401.13627v1) | include | [full_text_06](../screening/full_text_06.json) |
| P029 | [Robust Unrolled Network for Lensless Imaging with Enhanced Resistance to Model Mismatch and Noise](https://www.researchgate.net/publication/382193237_Robust_unrolled_network_for_lensless_imaging_with_enhanced_resistance_to_model_mismatch_and_noise) | include | [full_text_10](../screening/full_text_10.json) |
| P030 | [Empirical Bayesian Imaging With Large-Scale Push-Forward Generative Priors](https://doi.org/10.1109/LSP.2024.3361806) | include | [full_text_11](../screening/full_text_11.json) |
| P031 | [The Troublesome Kernel: On Hallucinations, No Free Lunches, and the Accuracy-Stability Tradeoff in Inverse Problems](https://arxiv.org/html/2001.01258v4) | include | [full_text_07](../screening/full_text_07.json) |
| P032 | [Uncertainty-Aware Fourier Ptychography](https://pmc.ncbi.nlm.nih.gov/articles/PMC12234902/) | include | [full_text_08](../screening/full_text_08.json) |
| P033 | [Unsupervised Detection of Distribution Shift in Inverse Problems Using Diffusion Models](https://arxiv.org/html/2505.11482v1) | include | [full_text_02](../screening/full_text_02.json) |
| P034 | [Towards Distribution-Shift Uncertainty Estimation for Inverse Problems with Generative Priors](https://arxiv.org/html/2510.10947v1) | include | [full_text_02](../screening/full_text_02.json) |
| P035 | [Mitigating Forward Model Mismatch in Inverse Problems via Learned Residuals and Diffusion Priors](https://doi.org/10.1117/12.3098133) | pending | Full text pending |
| P036 | [InverseNet: Benchmarking Operator Mismatch and Calibration Across Compressive Imaging Modalities](https://arxiv.org/html/2603.04538v1) | include | [full_text_02](../screening/full_text_02.json) |
| P037 | [On Hallucinations in Inverse Problems: Fundamental Limits and Provable Assessment Methods](https://arxiv.org/html/2605.13146v1) | include | [full_text_02](../screening/full_text_02.json) |
| P038 | [PRISM: Probabilistic and Robust Inverse Solver with Measurement-Conditioned Diffusion Prior for Blind Inverse Problems](https://arxiv.org/html/2509.16106v1) | include | [full_text_01](../screening/full_text_01.json) |
| P039 | [Adaptive Blind All-in-One Image Restoration](https://arxiv.org/html/2411.18412v1) | include | [full_text_02](../screening/full_text_02.json) |
| P040 | [Video Diffusion Posterior Sampling for Seeing Beyond Dynamic Scattering Layers](https://doi.org/10.1109/TPAMI.2025.3598457) | include | [full_text_11](../screening/full_text_11.json) |
| P041 | [Uncertainty Quantification in HSI Reconstruction using Physics-Aware Diffusion Priors and Optics-Encoded Measurements](https://arxiv.org/html/2511.18473v1) | include | [full_text_03](../screening/full_text_03.json) |
| P042 | [No-Harm Physics-Informed Inverse Learning with Residual-Calibrated Uncertainty](https://arxiv.org/html/2606.07153v1) | include | [full_text_01](../screening/full_text_01.json) |
| P043 | [Model Adaptation for Inverse Problems in Imaging](https://arxiv.org/pdf/2012.00139v2) | include | [full_text_08](../screening/full_text_08.json) |
| P044 | [Robust Lensless Image Reconstruction via PSF Estimation](https://openaccess.thecvf.com/content/WACV2021/papers/Rego_Robust_Lensless_Image_Reconstruction_via_PSF_Estimation_WACV_2021_paper.pdf) | include | [full_text_09](../screening/full_text_09.json) |
| P045 | [Block Coordinate Plug-and-Play Methods for Blind Inverse Problems](https://proceedings.neurips.cc/paper_files/paper/2023/file/f810c2ba07bae78dfe9d25c5d40c5536-Paper-Conference.pdf) | include | [full_text_02](../screening/full_text_02.json) |
| P046 | [Training Adaptive Reconstruction Networks for Blind Inverse Problems](https://arxiv.org/pdf/2202.11342v3) | include | [full_text_08](../screening/full_text_08.json) |
| P047 | [Solving Inverse Problems with Model Mismatch using Untrained Neural Networks within Model-based Architectures](https://arxiv.org/html/2403.04847v1) | include | [full_text_02](../screening/full_text_02.json) |
| P048 | [Plug-and-Play Posterior Sampling under Mismatched Measurement and Prior Models](https://proceedings.iclr.cc/paper_files/paper/2024/file/2a2874875861f6a6436b505dd77683d1-Paper-Conference.pdf) | include | [full_text_01](../screening/full_text_01.json) |
| P049 | [DeepVibes: Correcting Micro-Vibrations in Satellite Imaging With Pushbroom Cameras](https://doi.org/10.1109/TGRS.2024.3415372) | include | [full_text_11](../screening/full_text_11.json) |
| P050 | [Blind Inverse Problem Solving Made Easy by Text-to-Image Latent Diffusion](https://arxiv.org/html/2412.00557v1) | include | [full_text_03](../screening/full_text_03.json) |
| P051 | [ADOBI: Adaptive Diffusion Bridge For Blind Inverse Problems with Application to MRI Reconstruction](https://arxiv.org/html/2411.16535v1) | include | [full_text_03](../screening/full_text_03.json) |
| P052 | [Resolving Blind Inverse Problems under Dynamic Range Compression via Structured Forward Operator Modeling](https://arxiv.org/html/2603.01890v1) | include | [full_text_03](../screening/full_text_03.json) |
| P053 | [FaverNet: All-in-One Video Restoration via Frequency-Discriminative Conditioning](https://doi.org/10.1007/s11263-026-02977-y) | include | [full_text_11](../screening/full_text_11.json) |
| P054 | [Towards Real-world Event-guided Low-light Video Enhancement and Deblurring](https://arxiv.org/html/2408.14916v1) | include | [full_text_04](../screening/full_text_04.json) |
| P055 | [LEDNet: Joint Low-Light Enhancement and Deblurring in the Dark](https://arxiv.org/pdf/2202.03373) | include | [full_text_09](../screening/full_text_09.json) |
| P056 | [Investigating Tradeoffs in Real-World Video Super-Resolution](https://arxiv.org/html/2111.12704v1) | include | [full_text_04](../screening/full_text_04.json) |
| P057 | [Expanding Synthetic Real-World Degradations for Blind Video Super Resolution](https://arxiv.org/pdf/2305.02660) | include | [full_text_04](../screening/full_text_04.json) |
| P058 | [Real-world Video Super-resolution: A Benchmark Dataset and a Decomposition Based Learning Scheme](https://openaccess.thecvf.com/content/ICCV2021/papers/Yang_Real-World_Video_Super-Resolution_A_Benchmark_Dataset_and_a_Decomposition_Based_ICCV_2021_paper.pdf) | include | [full_text_09](../screening/full_text_09.json) |
| P059 | [Real-World Video Deblurring: A Benchmark Dataset and an Efficient Recurrent Neural Network](https://arxiv.org/pdf/2106.16028v2) | include | [full_text_08](../screening/full_text_08.json) |
| P060 | [CQAD: An Image Quality Assessment Dataset for CCTV](https://www.jmis.org/archive/view_article?pid=jmis-12-3-81) | exclude | [full_text_01](../screening/full_text_01.json) |
| P061 | [S3-CLIP: Video Super Resolution for Person-ReID](https://arxiv.org/pdf/2601.08807v1) | include | [full_text_08](../screening/full_text_08.json) |
| P062 | [How to Trust Your Diffusion Model: A Convex Optimization Approach to Conformal Risk Control](https://proceedings.mlr.press/v202/teneggi23a/teneggi23a.pdf) | include | [full_text_02](../screening/full_text_02.json) |
| P063 | [Task-Driven Uncertainty Quantification in Inverse Problems via Conformal Prediction](https://arxiv.org/html/2405.18527v1) | include | [full_text_02](../screening/full_text_02.json) |
| P064 | [Learning-Based Approaches for Reconstructions With Inexact Operators in nanoCT Applications](https://arxiv.org/pdf/2307.10474) | include | [full_text_01](../screening/full_text_01.json) |
| P065 | [Conformalized Generative Bayesian Imaging: An Uncertainty Quantification Framework for Computational Imaging](https://arxiv.org/html/2504.07696v1) | include | [full_text_02](../screening/full_text_02.json) |
| P066 | [Self-supervised Conformal Prediction for Uncertainty Quantification in Imaging Problems](https://arxiv.org/html/2502.05127v1) | include | [full_text_01](../screening/full_text_01.json) |
| P067 | [QUTCC: Quantile Uncertainty Training and Conformal Calibration for Imaging Inverse Problems](https://arxiv.org/html/2507.14760v1) | include | [full_text_02](../screening/full_text_02.json) |
| P068 | [Correction Filter for Single Image Super-Resolution: Robustifying Off-the-Shelf Deep Super-Resolvers](https://openaccess.thecvf.com/content_CVPR_2020/papers/Abu_Hussein_Correction_Filter_for_Single_Image_Super-Resolution_Robustifying_Off-the-Shelf_Deep_Super-Resolvers_CVPR_2020_paper.pdf) | include | [full_text_08](../screening/full_text_08.json) |
| P069 | [Blind Image Deconvolution Using Deep Generative Priors](https://arxiv.org/pdf/1802.04073v4) | include | [full_text_07](../screening/full_text_07.json) |
| P070 | [Grounding Degradations in Natural Language for All-In-One Video Restoration](https://arxiv.org/html/2507.14851v1) | include | [full_text_06](../screening/full_text_06.json) |
| P071 | [All-in-One Image Restoration for Unknown Degradations Using Adaptive Discriminative Filters for Specific Degradations](https://openaccess.thecvf.com/content/CVPR2023/papers/Park_All-in-One_Image_Restoration_for_Unknown_Degradations_Using_Adaptive_Discriminative_Filters_CVPR_2023_paper.pdf) | include | [full_text_08](../screening/full_text_08.json) |
| P072 | [PromptRestorer: A Prompting Image Restoration Method with Degradation Perception](https://proceedings.neurips.cc/paper_files/paper/2023/file/1c364d98a5cdc426fd8c76fbb2c10e34-Paper-Conference.pdf) | include | [full_text_01](../screening/full_text_01.json) |
| P073 | [AutoDIR: Automatic All-in-One Image Restoration with Latent Diffusion](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/05684.pdf) | include | [full_text_09](../screening/full_text_09.json) |
| P074 | [Controlling Vision-Language Models for Multi-Task Image Restoration](https://arxiv.org/html/2310.01018v2) | include | [full_text_05](../screening/full_text_05.json) |
| P075 | [Multimodal Prompt Perceiver: Empower Adaptiveness, Generalizability and Fidelity for All-in-One Image Restoration](https://arxiv.org/html/2312.02918v1) | include | [full_text_05](../screening/full_text_05.json) |
| P076 | [InstructIR: High-Quality Image Restoration Following Human Instructions](https://arxiv.org/html/2401.16468v1) | include | [full_text_05](../screening/full_text_05.json) |
| P077 | [RestoreAgent: Autonomous Image Restoration Agent via Multimodal Large Language Models](https://proceedings.neurips.cc/paper_files/paper/2024/file/c78f639424b8d89ceb4f2efbb4dfe4f4-Paper-Conference.pdf) | include | [full_text_06](../screening/full_text_06.json) |
| P078 | [DreamClear: High-Capacity Real-World Image Restoration with Privacy-Safe Dataset Curation](https://arxiv.org/html/2410.18666v1) | include | [full_text_06](../screening/full_text_06.json) |
| P079 | [Taming Generative Diffusion Prior for Universal Blind Image Restoration](https://arxiv.org/html/2408.11287v1) | include | [full_text_05](../screening/full_text_05.json) |
| P080 | [Generative Diffusion Prior for Unified Image Restoration and Enhancement](https://arxiv.org/html/2304.01247v1) | include | [full_text_04](../screening/full_text_04.json) |
| P081 | [A Modular Conditional Diffusion Framework for Image Reconstruction](https://arxiv.org/html/2411.05993v1) | include | [full_text_05](../screening/full_text_05.json) |
| P082 | [Solving Inverse Problems via Diffusion Optimal Control](https://proceedings.neurips.cc/paper_files/paper/2024/file/86655bc516148e311bcfcf88f1744de7-Paper-Conference.pdf) | include | [full_text_01](../screening/full_text_01.json) |
| P083 | [Provably Robust Score-Based Diffusion Posterior Sampling for Plug-and-Play Image Reconstruction](https://arxiv.org/html/2403.17042v1) | include | [full_text_05](../screening/full_text_05.json) |
| P084 | [Unleashing the Denoising Capability of Diffusion Prior for Solving Inverse Problems](https://proceedings.neurips.cc/paper_files/paper/2024/file/54fa8255cdf30736ecad38e842725e7f-Paper-Conference.pdf) | include | [full_text_01](../screening/full_text_01.json) |
| P085 | [InvFusion: Bridging Supervised and Zero-shot Diffusion for Inverse Problems](https://arxiv.org/html/2504.01689v1) | include | [full_text_05](../screening/full_text_05.json) |
| P086 | [Solving Inverse Problems with FLAIR](https://arxiv.org/html/2506.02680v1) | include | [full_text_01](../screening/full_text_01.json) |
| P087 | [Linearly Constrained Diffusion Implicit Models](https://arxiv.org/html/2411.00359v2) | include | [full_text_01](../screening/full_text_01.json) |
| P088 | [Exploiting Diffusion Prior for Real-World Image Super-Resolution](https://arxiv.org/pdf/2305.07015v4) | include | [full_text_07](../screening/full_text_07.json) |
| P089 | [SeeSR: Towards Semantics-Aware Real-World Image Super-Resolution](https://arxiv.org/pdf/2311.16518) | include | [full_text_06](../screening/full_text_06.json) |
| P090 | [Upscale-A-Video: Temporal-Consistent Diffusion Model for Real-World Video Super-Resolution](https://openaccess.thecvf.com/content/CVPR2024/papers/Zhou_Upscale-A-Video_Temporal-Consistent_Diffusion_Model_for_Real-World_Video_Super-Resolution_CVPR_2024_paper.pdf) | include | [full_text_08](../screening/full_text_08.json) |

## Reproduce

```bash
python scripts/build_synthesis_snapshot.py --check
```

Run without `--check` to regenerate this inventory and `evidence_snapshot_01.json`. The script verifies cumulative counts against the latest assessment checkpoint and retains per-field provenance. It does not update screening decisions or the workbook.
