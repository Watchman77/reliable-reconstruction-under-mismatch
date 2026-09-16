# Physics-Informed Deep Reconstruction Under Forward-Model Mismatch

> Historical rapid-map checkpoint. For the current full-text-supported interpretation and research decision, use [provisional synthesis 01](../literature/synthesis/provisional_gap_synthesis_01.md). Earlier feature tables are exploratory; the absence of a complete feature intersection does not establish novelty. The original umbrella topic remains in force.

## Rapid systematic gap map, 2020–16 September 2026

**Research line:** reliable reconstruction of real-world multi-degraded imagery, using surveillance/CCTV as the principal stress test  
**Publication strategy:** journal-first research programme; conference work may be derived later only where it contains a distinct contribution and does not duplicate the journal  
**Status:** 90-study seed evidence map and adversarial novelty test (Version 1.1); not yet a PRISMA systematic review or manuscript literature review

---

## 1. Executive verdict

The broad proposition—*use physics-informed deep learning to tolerate an incorrect forward model*—is important but is **not novel enough on its own**. By 2020, deep total-least-squares unrolling was already being used for kernel/model uncertainty in deconvolution. By 2021, mismatch-compensation networks had been demonstrated in lensless imaging. From 2023 onward, blind diffusion methods began jointly estimating the image and operator. By 2024–2026, EM, Gibbs sampling, latent diffusion, learned residual correction and explicit cross-modality mismatch benchmarks had substantially occupied that space.

The research line should nevertheless proceed. The defensible gap is the **joint reliability problem**:

> How can a reconstruction system operating under compound, unknown and time-varying forward-model mismatch recover an image, estimate the degradation/operator, quantify image and operator uncertainty, identify which reconstructed details are supported by the measurement, and abstain when reliable recovery is impossible?

No cornerstone work found in this first mapping unifies all of the following in a single real-world surveillance-oriented study:

1. a structured multi-stage forward model covering optics/motion, sensor noise, image-signal processing, sampling and video compression;
2. explicit operator conditioning or correction under compound mismatch;
3. joint uncertainty for the image and degradation/operator;
4. calibrated uncertainty with coverage or risk guarantees;
5. measurement-support or hallucination assessment;
6. selective reconstruction/abstention;
7. controlled OOD testing across degradation, codec, device and scene;
8. validation on real captures rather than synthetic degradation alone.

This is not a claim that the combination is automatically publishable. It is a **surviving candidate gap** that now needs a formal systematic search, full-text coding and the preregistered 100-image feasibility pilot.

### 90-study expansion note

Twenty additional studies were coded on 16 September 2026. They include universal prompt-based restoration, compound-restoration agents, operator-conditioned diffusion solvers, data-consistent flow/diffusion methods and real-world generative image/video super-resolution. These additions occupy several broad claims—particularly automatic compound restoration and degradation-aware generative inversion—but still do not provide the complete reliability intersection defined above.

### Recommended working title

**Evidence-Calibrated Deep Reconstruction Under Compound Forward-Model Mismatch for Real-World Surveillance Imaging**

An application-neutral title can be retained for the eventual journal only if experiments cover more than surveillance:

**Evidence-Calibrated Physics-Informed Reconstruction Under Compound Forward-Model Mismatch**

---

## 2. Research questions for the formal review

- **RQ1:** How has forward-model mismatch been represented: fixed error, parameter uncertainty, residual discrepancy, unknown operator, or unmodelled degradation?
- **RQ2:** Which methods explicitly use the assumed forward operator, and which are operator-oblivious?
- **RQ3:** Do methods reconstruct only the image, or jointly infer image and operator/degradation?
- **RQ4:** Is uncertainty quantified for the reconstructed image, the operator, or both?
- **RQ5:** Is uncertainty calibrated, and does it remain calibrated under distribution shift?
- **RQ6:** Are hallucinations or unsupported details measured, rather than judged visually?
- **RQ7:** Can the system detect failure or abstain when the observation is insufficient?
- **RQ8:** Are results based on synthetic mismatch, real measurements, physical hardware, or cross-device evaluation?
- **RQ9:** Do evaluations cover compound and time-varying degradations resembling CCTV/video acquisition?
- **RQ10:** Which claimed gains survive OOD conditions and downstream fidelity tests?

---

## 3. Scope and search protocol used for this map

### Inclusion window

- Main evidence window: **1 January 2020–15 September 2026**.
- Pre-2020 methods are included only when required to define a baseline or concept inherited by work in the main window.
- Peer-reviewed journal and flagship-conference papers are prioritised. Recent preprints are marked explicitly and cannot carry the central novelty claim alone.

### Concept blocks

The search combined terms from four blocks:

1. **Inverse imaging:** inverse problem, image reconstruction, computational imaging, deconvolution, deblurring, super-resolution, lensless imaging, tomography, ptychography.
2. **Imperfect physics:** model mismatch, operator mismatch, kernel uncertainty, uncalibrated imaging, blind inverse problem, operator estimation, residual forward model.
3. **Learning method:** deep unrolling/unfolding, plug-and-play, score prior, diffusion posterior sampling, latent diffusion, generative prior.
4. **Reliability:** uncertainty quantification, calibration, conformal prediction, hallucination, data consistency, distribution shift, failure detection, selective prediction, abstention.

### Sources prioritised

IEEE Xplore; CVF Open Access; NeurIPS, ICML/PMLR and ICLR proceedings; SIAM; Optica/SPIE; PubMed Central for medical-imaging reliability; official author/project pages and arXiv for recent papers not yet available in publisher indexes.

### Important limitation

This is a **rapid evidence map**, not a completed PRISMA review. It identifies the intellectual terrain and tests whether the idea should be killed or developed. A journal-ready review must add database-specific query strings, deduplication, two-stage screening, exclusion reasons, full-text extraction and citation-chaining.

---

## 4. Evolution of the field

| Period | Dominant move | What became solved or partly solved | Remaining weakness |
|---|---|---|---|
| 2020–2021 | Learned regularisation, unrolling and mismatch correction | Physics can be embedded in trainable solvers; specific kernel/PSF mismatch can be mitigated | Usually one modality, one mismatch family, point estimates, limited OOD evidence |
| 2021–2022 | Reliability warnings and probabilistic reconstruction | Instability, null-space hallucination and image uncertainty are recognised; formal image intervals emerge | Reliability tools are usually separate from mismatch-aware reconstruction |
| 2022–2023 | Diffusion priors for known and blind inverse problems | Strong pretrained priors; joint image/operator estimation becomes feasible | High compute, simplified operators, weak calibration and real-device validation |
| 2023–2024 | Blind EM/Gibbs/latent approaches and all-in-one restoration | Unknown degradations can be inferred or implicitly handled; multi-task restoration improves | “Unknown corruption” is not the same as a physically interpretable compound forward model |
| 2024–2025 | Real-world generative restoration and differentiable calibration | Better perceptual realism; joint calibration in selected physical systems; stronger theory of hallucination | Perceptual quality can conflict with evidential fidelity; abstention remains uncommon |
| 2025–Sep 2026 | Mismatch benchmarks, residual correction, OOD indicators and provable hallucination assessment | Operator mismatch is quantified directly; unsupervised shift indicators and forward-model bounds appear | The pieces remain fragmented; joint image/operator calibration and failure-aware real CCTV evaluation are not established |

---

## 5. Cornerstone evidence map

Legend: **✓** explicit; **△** partial/implicit; **—** not a main contribution. “Real” means real measurements or hardware are a meaningful part of validation, not merely natural clean images synthetically degraded.

### A. Physics-informed learning, mismatch and uncalibrated imaging

| Year | Work | Main contribution | Mismatch | Joint image/operator | UQ | Real | Reliability gap left open |
|---|---|---|---:|---:|---:|---:|---|
| 2020 | [Deep Learning for Handling Kernel/Model Uncertainty in Image Deconvolution](https://doi.org/10.1109/CVPR42600.2020.00246) | Error-in-variables/total-least-squares unrolling for inaccurate blur kernels | ✓ | △ | — | △ | No calibrated image/operator uncertainty or compound pipeline |
| 2020 | [NETT: Solving Inverse Problems with Deep Neural Networks](https://doi.org/10.1088/1361-6420/ab6d57) | Learned regulariser with convergence analysis | △ | — | — | △ | Not designed around unknown compound mismatch or failure decisions |
| 2020 | [On Instabilities of Deep Learning in Image Reconstruction](https://doi.org/10.1073/pnas.1907377117) | Demonstrates perturbation and structural instabilities in learned reconstruction | △ | — | — | △ | Diagnoses failures rather than providing a unified corrective system |
| 2021 | [Robust Reconstruction With Deep Learning to Handle Model Mismatch in Lensless Imaging](https://doi.org/10.1109/TCI.2021.3114542) | Unrolled reconstruction plus learned mismatch compensation for lensless PSF/model error | ✓ | △ | — | ✓ | Modality-specific; no calibrated UQ, support map or abstention |
| 2021 | [Deep Equilibrium Architectures for Inverse Problems in Imaging](https://doi.org/10.1109/TCI.2021.3118944) | Fixed-point/infinite-depth physics-aware reconstruction | △ | — | — | △ | Assumes usable known forward model; reliability under mismatch not central |
| 2022/2024 | [Differentiable Uncalibrated Imaging](https://arxiv.org/abs/2211.10525) | Jointly optimises unknown measurement coordinates and reconstruction | ✓ | ✓ | — | △ | Handles selected calibration variables, not multi-stage video degradation or calibrated failure |
| 2024 | [Robust Unrolled Network for Lensless Imaging with Mismatch](https://opg.optica.org/oe/abstract.cfm?uri=oe-32-17-30267) | Further robust lensless unrolling under forward-model errors | ✓ | △ | — | ✓ | Still modality- and mismatch-specific |
| 2025 | [Uncertainty-Aware Fourier Ptychography](https://doi.org/10.1038/s41377-025-01915-w) | Simultaneously addresses optical aberration, misalignment and low-quality data with uncertainty awareness | ✓ | ✓ | ✓ | ✓ | Strong closest analogue, but not compound surveillance/codec degradation or selective evidential restoration |
| 2026 | [Mitigating Forward Model Mismatch via Learned Residuals and Diffusion Priors](https://www.spiedigitallibrary.org/conference-proceedings-of-spie/13849/1384908/) | Learns residual measurement discrepancy during diffusion-based inversion | ✓ | △ | △ | △ | Residual correction does not itself establish calibrated joint uncertainty or abstention |
| 2026 | [InverseNet: Benchmarking Operator Mismatch and Calibration Across Compressive Imaging Modalities](https://arxiv.org/abs/2603.04538) *(preprint)* | Cross-modality mismatch benchmark; reports large performance losses and calibration recovery | ✓ | △ | — | ✓ | Compressive modalities; no hallucination-aware uncertainty or surveillance compound degradation |

### B. Diffusion and blind inverse solvers

| Year | Work | Main contribution | Operator assumed | Joint image/operator | Posterior/UQ | Real | Reliability gap left open |
|---|---|---|---:|---:|---:|---:|---|
| 2022 | [Denoising Diffusion Restoration Models (DDRM)](https://proceedings.neurips.cc/paper_files/paper/2022/hash/95504595b6169131b6ed6cd72eb05616-Abstract-Conference.html) | Spectral diffusion restoration for linear inverse problems | Known | — | △ | △ | Sensitive to incorrect operator; no operator uncertainty |
| 2023 | [Diffusion Posterior Sampling for General Noisy Inverse Problems](https://openreview.net/forum?id=OnD9zGAGT0k) | Posterior sampling for noisy linear/nonlinear inverse problems | Known | — | △ | △ | Samples are not automatically calibrated; mismatch not solved |
| 2023 | [Pseudoinverse-Guided Diffusion Models for Inverse Problems](https://openreview.net/forum?id=9_gsMA8MRKQ) | Uses pseudoinverse guidance to improve data consistency | Known | — | △ | △ | Requires forward operator; no mismatch/UQ guarantee |
| 2023 | [Denoising Diffusion Null-Space Model](https://openreview.net/forum?id=mRieQgMtNTQ) | Range/null-space decomposition for data-consistent restoration | Known | — | △ | △ | Useful for support analysis, but blind compound mismatch remains open |
| 2023 | [Parallel Diffusion Models of Operator and Image for Blind Inverse Problems (BlindDPS)](https://openaccess.thecvf.com/content/CVPR2023/html/Chung_Parallel_Diffusion_Models_of_Operator_and_Image_for_Blind_Inverse_Problems_CVPR_2023_paper.html) | Parallel score priors jointly estimate image and operator | Unknown functional parameters | ✓ | △ | △ | Operator prior/training burden; no calibrated joint UQ or abstention |
| 2023 | [GibbsDDRM](https://proceedings.mlr.press/v202/murata23a.html) | Partially collapsed Gibbs sampler for blind linear inverse problems | Unknown parameters | ✓ | ✓ | △ | Simplified forward families; compute and calibration under real compound mismatch remain |
| 2024 | [Fast Diffusion EM](https://openaccess.thecvf.com/content/WACV2024/html/Laroche_Fast_Diffusion_EM_A_Diffusion_Model_for_Blind_Inverse_Problems_WACV_2024_paper.html) | EM alternation for image and blur-kernel estimation | Unknown blur | ✓ | △ | △ | Deblurring focus; no calibrated operator/image uncertainty or failure policy |
| 2024 | [Blind Image Restoration via Fast Diffusion Inversion (BIRD)](https://proceedings.neurips.cc/paper_files/paper/2024/hash/3d13d910b48ac2e672a32cfdf98be1bf-Abstract-Conference.html) | Optimises diffusion input noise and degradation parameters without changing reverse sampling | Unknown parameters | ✓ | △ | △ | Evaluates standard restoration tasks, not full acquisition-chain mismatch and abstention |
| 2024/2026 | [Blind Inversion Using Latent Diffusion Priors (LatentDEM)](https://arxiv.org/abs/2407.01027) | Variational EM with latent diffusion for 2D blind deblurring and 3D inverse rendering | Unknown parameters | ✓ | △ | △ | Strongly occupies basic joint inversion; lacks evidence calibration and surveillance stress testing |
| 2026 | [PRISM](https://doi.org/10.1109/ICASSP55912.2026.11462668) | Measurement-conditioned diffusion prior for blind reconstruction and kernel recovery | Unknown blur | ✓ | ✓ | △ | Deblurring focus; failure/abstention and compound real-device mismatch remain open |

### C. Real-world, blind and all-in-one restoration

| Year | Work | Main contribution | Compound/unknown degradation | Explicit physics | UQ | Real | Reliability gap left open |
|---|---|---|---:|---:|---:|---:|---|
| 2020 | [Real-World Blur Dataset](https://openaccess.thecvf.com/content_CVPR_2020/html/Rim_Real-World_Blur_Dataset_for_Learning_and_Benchmarking_Deblurring_Algorithms_CVPR_2020_paper.html) | Paired real blurred/sharp images and benchmark | △ | — | — | ✓ | Blur-specific; does not provide the full CCTV acquisition chain |
| 2021 | [Designing a Practical Degradation Model for Deep Blind Image Super-Resolution (BSRGAN)](https://openaccess.thecvf.com/content/ICCV2021/html/Zhang_Designing_a_Practical_Degradation_Model_for_Deep_Blind_Image_Super-Resolution_ICCV_2021_paper.html) | Randomised shuffled degradation pipeline for blind SR | ✓ | △ | — | ✓ | Strong synthetic pipeline, but no operator recovery, calibration or evidence support |
| 2021 | [Real-ESRGAN](https://openaccess.thecvf.com/content/ICCV2021W/AIM/html/Wang_Real-ESRGAN_Training_Real-World_Blind_Super-Resolution_With_Pure_Synthetic_Data_ICCVW_2021_paper.html) | High-order synthetic degradations for real-world blind SR | ✓ | △ | — | ✓ | Perceptual restoration can invent detail; no calibrated fidelity controls |
| 2022 | [AirNet: All-in-One Image Restoration for Unknown Corruption](https://openaccess.thecvf.com/content/CVPR2022/html/Li_All-in-One_Image_Restoration_for_Unknown_Corruption_CVPR_2022_paper.html) | Contrastive degradation representation and one model for multiple corruptions | ✓ | — | — | △ | Unknown task class, but not explicit operator estimation or uncertainty |
| 2023 | [PromptIR](https://proceedings.neurips.cc/paper_files/paper/2023/hash/e187897ed7780a17bb69ab19f3be921f-Abstract-Conference.html) | Degradation prompts guide all-in-one blind restoration | ✓ | — | — | △ | Strong implicit conditioning; no physics-based traceability or calibrated failure |
| 2024 | [DiffBIR](https://eccv.ecva.net/virtual/2024/poster/2315) | Two-stage restoration with generative diffusion prior | ✓ | — | — | ✓ | Optimises perception; measurement-supported detail and abstention are not central |
| 2024 | [AverNet: All-in-One Video Restoration for Time-Varying Unknown Degradations](https://proceedings.neurips.cc/paper_files/paper/2024/hash/e635a25e49e73adc51f76aef462ff2f8-Abstract-Conference.html) | Video restoration under multiple temporally varying degradation types | ✓ | — | — | △ | Very close application competitor; its reported experiments use two synthesised datasets and it lacks explicit forward mismatch, joint UQ and evidence calibration |
| 2024 | [SR+Codec Benchmark](https://arxiv.org/abs/2412.02506) | Benchmarks super-resolution under video compression across models/codecs | ✓ | — | — | ✓ | Benchmark only; blur/noise/operator uncertainty and abstention are not unified |
| 2024 | [SUPIR: Scaling-Up to Excellence in Real-World Image Restoration](https://arxiv.org/abs/2401.13627) | Large generative restoration model with strong perceptual quality | ✓ | — | — | ✓ | High realism does not establish evidential faithfulness |
| 2025 | [DynamicDPS](https://arxiv.org/abs/2503.01075) *(preprint)* | Reduces hallucinations in conditional medical reconstruction using adaptive posterior sampling | △ | ✓ | △ | ✓ | Medical modality; no operator uncertainty or multi-stage surveillance degradation |
| 2026 | [Adaptive Blind All-in-One Image Restoration](https://doi.org/10.1016/j.cviu.2026.104795) | Adaptive unified restoration across seen, unseen and composite degradations | ✓ | — | — | △ | Reinforces that all-in-one restoration is crowded; reliability remains separate |

### D. Uncertainty, hallucination and failure awareness

| Year | Work | Main contribution | Calibrated | OOD | Operator UQ | Abstain | Gap left open |
|---|---|---|---:|---:|---:|---:|---|
| 2021 | [Deep Probabilistic Imaging](https://ojs.aaai.org/index.php/AAAI/article/view/16430) | Variational posterior and multimodal solution characterisation | △ | — | — | — | Image posterior only; operator mismatch not jointly represented |
| 2021 | [On Hallucinations in Tomographic Image Reconstruction](https://doi.org/10.1109/TMI.2021.3077857) | Measurement/null-space decomposition and hallucination maps | — | ✓ | — | — | Diagnostic framework, not a compound mismatch-aware reconstruction system |
| 2022 | [Image-to-Image Regression with Distribution-Free UQ](https://proceedings.mlr.press/v162/angelopoulos22a.html) | Distribution-free pixel-wise intervals with formal marginal coverage | ✓ | △ | — | △ | Requires suitable calibration and does not infer unknown operators |
| 2022 | [Conffusion](https://arxiv.org/abs/2211.09795) | Fast confidence intervals for diffusion outputs | ✓ | △ | — | — | Generic diffusion intervals; not physics/operator-aware |
| 2024 | [Empirical Bayesian Imaging with Large-Scale Push-Forward Generative Priors](https://doi.org/10.1109/LSP.2024.3361806) | Scalable posterior sampling and uncertainty for deblurring | △ | — | — | — | Underestimation/calibration and operator mismatch remain concerns |
| 2025 | [The Troublesome Kernel](https://doi.org/10.1137/23M1568739) | No-free-lunch results for hallucination and accuracy–stability trade-offs | — | ✓ | — | △ | Theoretical boundary; motivates support-aware failure detection |
| 2025 | [Unsupervised Detection of Distribution Shift in Inverse Problems Using Diffusion Models](https://arxiv.org/abs/2505.11482) *(preprint)* | Measurement-only score metric approximating distribution shift and helps alignment | △ | ✓ | — | △ | Shift indicator is not joint image/operator calibration |
| 2025 | [Towards Distribution-Shift UQ for Inverse Problems with Generative Priors](https://arxiv.org/abs/2510.10947) *(preprint)* | Reconstruction instability under measurement variation as a calibration-free OOD indicator | △ | ✓ | — | ✓ | Does not model compound physical mismatch or operator uncertainty |
| 2026 | [On Hallucinations in Inverse Problems: Fundamental Limits and Provable Assessment Methods](https://arxiv.org/abs/2605.13146) *(preprint)* | Forward-model-dependent bounds and input-level faithfulness assessment | ✓ | ✓ | △ | ✓ | Provides a potential assessment component, not the full reconstruction architecture |

---

## 6. What is already solved—and must not be claimed as our novelty

The eventual proposal and paper must **not** claim any of the following as new:

- embedding a known forward operator in an unrolled neural network;
- adding a data-consistency loss to a restoration network;
- training with random blur/noise/JPEG degradation;
- jointly estimating a clean image and one blur kernel;
- using diffusion as an image prior for a blind inverse problem;
- producing multiple posterior samples and calling their variance “uncertainty”;
- evaluating only PSNR, SSIM and LPIPS under mild synthetic mismatch;
- demonstrating that a standard restoration model degrades under OOD corruption;
- sharpening a CCTV face or number plate visually;
- adding MC dropout alone and labelling the system trustworthy.

These can be components or baselines, not headline contributions.

---

## 7. The surviving research gap

### 7.1 Forward process

A realistic surveillance observation should be represented as a composition, not a single convolution:

\[
y_t = \mathcal{Q}_{\psi_t}\!\left[
\mathcal{C}_{\gamma_t}\!\left(
\mathcal{S}_{\eta_t}\!\left(
\mathcal{H}_{\theta_t}(x_t) + n_t
\right)\right)\right],
\]

where:

- \(\mathcal{H}_{\theta_t}\): spatially varying motion/defocus/optical blur;
- \(n_t\): signal-dependent shot noise, read noise and low-light noise;
- \(\mathcal{S}_{\eta_t}\): sensor/ISP response, clipping, demosaicing, tone mapping and sharpening;
- \(\mathcal{C}_{\gamma_t}\): spatial/temporal resampling and camera processing;
- \(\mathcal{Q}_{\psi_t}\): codec, bitrate, quantisation and group-of-pictures effects;
- the parameters may change through time.

The reconstruction model will only have an approximate nominal operator \(\mathcal{A}_{\phi}\). The discrepancy is therefore structured:

\[
\mathcal{A}_{\text{true},t}=\mathcal{A}_{\phi_t}+\Delta\mathcal{A}_{t},
\]

with both parametric uncertainty in \(\phi_t\) and non-parametric residual mismatch \(\Delta\mathcal{A}_{t}\).

### 7.2 Required output

The system should not output only a sharpened image. It should return:

\[
(\hat{x},\hat{\phi},U_x,U_{\phi},S,R),
\]

where:

- \(\hat{x}\): reconstruction;
- \(\hat{\phi}\): estimated interpretable degradation/operator parameters;
- \(U_x\): calibrated spatial reconstruction uncertainty;
- \(U_{\phi}\): operator/degradation uncertainty;
- \(S\): measurement-support or faithfulness map;
- \(R\): reliability/abstention decision.

### 7.3 Core novelty hypothesis

The central hypothesis is not merely that the method obtains a higher average PSNR. It is:

> Explicitly separating parametric operator uncertainty from residual model discrepancy, and calibrating both reconstruction and operator uncertainty, will improve OOD risk control and enable the system to reject unsupported reconstructions under compound real-world degradation.

This claim is falsifiable. It can fail if operator estimates are unidentifiable, uncertainty remains miscalibrated under shift, or a simpler all-in-one restoration model matches the risk–coverage performance.

---

## 8. Three candidate journal problems

Scores are provisional, from 1 (low) to 10 (high). “Practicality” includes public data, compute burden and feasibility for a small research team.

| Rank | Candidate problem | Novelty | Scientific depth | Practicality | Risk | Verdict |
|---:|---|---:|---:|---:|---:|---|
| 1 | **Evidence-calibrated reconstruction under compound mismatch**: joint image/operator inference, support maps, calibrated UQ and abstention | 9.0 | 9.5 | 7.0 | 8.0 | Best master journal problem |
| 2 | **SurvMismatch benchmark and protocol**: controlled synthetic-to-real CCTV degradation, operator annotations, hallucination and risk–coverage evaluation | 8.5 | 8.0 | 8.0 | 6.5 | Strong enabling paper; should be part of Candidate 1 if resources permit |
| 3 | **Time-varying operator-aware video solver**: real-time unrolling plus temporal operator tracking and UQ | 7.5 | 9.0 | 5.5 | 9.0 | Valuable second-stage paper; too large for the first implementation |

### Recommended programme

Combine Candidates 1 and 2 in the master journal programme:

1. create the benchmark/protocol needed to expose failure;
2. propose the reliability-aware reconstruction method;
3. compare it with classical, discriminative, all-in-one and generative baselines;
4. test whether the method knows when it does not know.

Keep full real-time video optimisation for a later derivative study unless the pilot demonstrates sufficient compute and data.

---

## 9. Proposed architecture—concept, not yet a novelty claim

1. **Degradation encoder:** infers interpretable parameters and a latent residual-mismatch code.
2. **Operator-conditioned unrolled solver:** alternates learned prior/proximal updates with data-consistency updates using the approximate differentiable forward model.
3. **Residual forward corrector:** models discrepancy that cannot be expressed by the nominal operator parameters; regularised to prevent it from explaining away arbitrary image content.
4. **Generative prior:** optional diffusion/score prior used only for ambiguous high-frequency components.
5. **Joint posterior head:** approximates uncertainty over image and operator; ensembles or conditional posterior sampling can be compared.
6. **Calibration layer:** split-conformal or risk-controlling calibration on held-out devices/degradations, with explicit ID and OOD protocols.
7. **Measurement-support analyser:** combines forward reprojection residuals, range/null-space decomposition where available, and perturbation/stability tests.
8. **Selective output:** returns the reconstruction only when estimated risk is below a pre-defined level; otherwise returns an abstention plus the best-supported low-frequency reconstruction.

The method must prevent a flexible residual corrector or diffusion prior from trivially satisfying the loss while inventing content. This identifiability problem is one of the main scientific risks and must be handled through constrained parameterisation, priors, ablation and synthetic ground truth.

---

## 10. Experimental design required for a journal-grade claim

### 10.1 Data tiers

**Tier 1 — controlled synthetic:** clean image/video sources degraded through a fully recorded forward pipeline. This provides exact image, operator and mismatch ground truth.

**Tier 2 — established real restoration data:** RealBlur and real-world SR/low-light/video datasets, used without pretending that all operator ground truth is known.

**Tier 3 — controlled surveillance capture:** a modest original dataset captured with reproducible blur, lighting, distance and codec settings. A paired or near-paired high-quality reference camera is needed. This is the most important evidence that synthetic trends transfer to physical measurements.

**Tier 4 — unconstrained CCTV:** public or ethically obtained surveillance clips used only for no-reference stress testing, downstream task stability and qualitative failure analysis. These cannot support claims of true-detail recovery without ground truth.

### 10.2 Mismatch axes

- blur kernel family, length, direction and spatial variation;
- defocus radius and depth variation;
- Poisson–Gaussian versus heavy-tailed/signal-dependent noise;
- exposure, clipping, tone mapping and sharpening;
- downsampling kernel and scale;
- JPEG versus H.264/H.265, bitrate, quantisation and GOP structure;
- unseen combinations and orderings of degradation;
- device/camera shift;
- time-varying degradation in video;
- scene-content shift, especially text, faces and small repeated structures.

### 10.3 Baselines

- classical Wiener/Tikhonov/total variation;
- generic U-Net/Restormer/SwinIR-type restoration;
- AirNet and PromptIR-type all-in-one restoration;
- BSRGAN/Real-ESRGAN degradation-trained SR;
- DiffBIR/SUPIR-type generative restoration;
- one physics-unrolled reconstruction baseline;
- BlindDPS, Fast Diffusion EM, BIRD or LatentDEM on the compatible blind-deblurring subset;
- uncertainty baselines: deep ensembles, MC dropout, posterior samples and conformalised intervals.

### 10.4 Metrics

**Reconstruction:** PSNR, SSIM, LPIPS/DISTS, temporal consistency for video.  
**Operator:** parameter error, kernel distance, trajectory/angle error and operator-reprojection error.  
**Uncertainty:** empirical coverage, mean interval width, coverage gap, calibration error, negative log likelihood where valid, error–uncertainty correlation.  
**Selective reliability:** risk–coverage curve, area under the risk–coverage curve, failure-detection AUROC/AUPRC and risk at fixed coverage.  
**Hallucination/faithfulness:** measurement-space consistency, null-space/support maps, perturbation stability, change in small-object/text identity across posterior samples, and task-consistency checks.  
**Downstream:** OCR/ANPR, face verification and object detection may be secondary tests, never proof that unobserved details were recovered.

### 10.5 Mandatory evaluation rules

- split by source video/scene/device to prevent frame leakage;
- tune thresholds and calibration only on validation data;
- include matched, mild, moderate, severe and unknown mismatch;
- hold out at least one degradation family, codec and device;
- report bootstrap confidence intervals and paired significance tests where appropriate;
- report compute, memory, latency and failure cases;
- conduct ablations for operator conditioning, residual correction, generative prior, UQ, calibration and abstention;
- compare perceptual quality against factual/measurement fidelity rather than presenting them as interchangeable.

---

## 11. Adversarial novelty test

### Claims most likely to be rejected by reviewers

1. **“First physics-informed method robust to model mismatch.”** False; prior work exists from at least 2020–2021.
2. **“First joint image and blur-kernel reconstruction using diffusion.”** False; BlindDPS, GibbsDDRM, Fast Diffusion EM, BIRD, LatentDEM and PRISM occupy this area.
3. **“First all-in-one model for mixed degradations.”** False; AirNet, PromptIR, AverNet and related work already address it.
4. **“Uncertainty-aware because we use posterior variance/MC dropout.”** Insufficient without calibration, OOD testing and decision utility.
5. **“Hallucination-free.”** Scientifically indefensible for a severely ill-posed observation; theory now gives strong reasons to avoid this wording.
6. **“Forensic recovery.”** Dangerous unless each claimed detail is demonstrably supported by the measurement and the chain of custody/processing is controlled.

### Claim that may survive

> A unified, evidence-calibrated reconstruction framework and benchmark for compound forward-model mismatch, jointly evaluating image recovery, operator inference, uncertainty calibration, measurement support and selective failure on controlled synthetic-to-real surveillance data.

This wording should remain provisional until full-text coding and the pilot are complete.

---

## 12. Go/no-go pilot before full model development

### Pilot objective

Determine whether the proposed reliability contribution is measurable with available data and compute before committing to a large architecture.

### Minimum pilot

1. Build a reproducible compound degradation simulator for blur + signal-dependent noise + downsampling + JPEG/H.264 compression.
2. Train or reuse three baselines: an operator-oblivious restoration network, an operator-conditioned unrolled network and a generative restoration model.
3. Evaluate on matched degradation and three held-out mismatch axes.
4. Add a simple operator estimator, deep-ensemble image uncertainty and split-conformal calibration.
5. Measure risk–coverage and hallucination/support behaviour on small text or plate-like targets.
6. Capture a small real sequence set under known settings to test synthetic-to-real transfer.

### Go criteria

- operator-conditioned modelling materially improves OOD risk–coverage, not merely average PSNR;
- uncertainty ranks reconstruction failures and remains calibratable on held-out degradation;
- support/faithfulness measures distinguish plausible invented detail from stable observed detail;
- real-capture trends broadly agree with controlled simulation;
- compute is manageable without relying on a prohibitively large diffusion model for every experiment.

### No-go or pivot criteria

- operator and image are too non-identifiable for the selected degradation pipeline;
- calibration collapses under realistic shift and cannot support useful abstention;
- all-in-one baselines match the proposed method after fair tuning;
- real data cannot provide defensible reference or acquisition metadata;
- the project becomes only perceptual enhancement with no scientifically verifiable fidelity claim.

If a no-go criterion is met, pivot to the benchmark/reliability-assessment paper rather than forcing an architecture claim.

---

## 13. Immediate next research actions

1. Register a review protocol and exact database strings.
2. Expand the seed set through backward and forward citation chaining to approximately 60–100 screened papers.
3. Extract full-text evidence into a structured matrix with the fields: modality, forward model, mismatch type, operator access, solver, physics integration, joint estimation, UQ target, calibration, OOD, real hardware, hallucination test, abstention, code/data and limitation.
4. Give special attention to the nearest competitors: UA-FP, BlindDPS, GibbsDDRM, Fast Diffusion EM, BIRD, LatentDEM, PRISM, AverNet, InverseNet and the 2026 hallucination-assessment work.
5. Write the pilot specification and dataset licence/ethics plan.
6. Run the pilot before writing the journal abstract or claiming a final architecture.

---

## 14. Bottom line

**Proceed—but proceed with the upgraded problem.**

The publishable target is not “make blurry CCTV clear.” It is not even “make a physics-informed model robust to mismatch.” It is:

> Build and rigorously evaluate a reconstruction system that separates what is plausible from what is supported, quantifies uncertainty in both the reconstructed image and the imperfect forward model, and refuses to assert detail when the observation cannot justify it.

That is a deeper, safer and more defensible research identity: **reliable computational imaging under imperfect physics**.
