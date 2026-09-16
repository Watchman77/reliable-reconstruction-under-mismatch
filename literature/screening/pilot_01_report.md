# Pilot 01: preliminary screening of 20 seed records

Checked: 2026-09-16. Protocol: v0.3, working draft, not registered. Reviewer: Codex AI assistance; all human adjudication pending.

## Outcome

| Stage | Records |
|---|---:|
| Seed candidates | 90 |
| AI pilot triaged | 20 |
| Recommend full-text review | 18 |
| Unclear: resolve scope/retrieval | 2 |
| Not yet pilot-triaged | 70 |
| Formally included / excluded | 0 / 0 |

These are the first 20 stable seed IDs, not a random sample or formal database search. Seventeen complete abstracts were inspected. P001 and P013 were conservatively advanced using their titles and official author repositories; their abstracts remain to be retrieved. P016 has only partial search-result evidence. Reading P005's PDF abstract/opening page is not a full-text eligibility assessment. No human agreement statistic, full-text appraisal or definitive novelty claim can be computed from this pilot.

The initial seed matrix's feature ratings remain provisional. This checkpoint corrects metadata and evidence labels; it does not validate every pre-existing Yes/No code.

## Decisions and evidence

### P001 — Deep Learning for Handling Kernel/Model Uncertainty in Image Deconvolution

**Recommendation:** AI pilot: advance. Human adjudication: pending.

**Evidence basis:** Title and official author repository; abstract not retrieved. [Inspected source](https://github.com/ysnan/NBD_KerUnc).

The title explicitly concerns kernel/model uncertainty. The author repository identifies Nan and Ji, CVPR 2020, and provides synthetic kernel-error and real-image experiments.

**Scope signal:** Kernel/model uncertainty.

**Full-text question:** Verify the abstract, correction mechanism and kernel-error distribution; distinguish parameter uncertainty from wrong-family mismatch.

### P002 — NETT: Solving Inverse Problems with Deep Neural Networks

**Recommendation:** AI pilot: advance. Human adjudication: pending.

**Evidence basis:** Author preprint abstract. [Inspected source](https://arxiv.org/abs/1803.00092).

NETT combines a learned regularizer with data consistency and convergence analysis. Its abstract reports reconstruction of unknowns that differ from the training-image type.

**Scope signal:** Potential OOD reconstruction reliability.

**Full-text question:** Does the full evaluation operationalize distribution shift relevant to this review, or is this a background regularization method only? The 2018 preprint and 2020 journal report are one lineage.

### P003 — On Instabilities of Deep Learning in Image Reconstruction and the Potential Costs of AI

**Recommendation:** AI pilot: advance. Human adjudication: pending.

**Evidence basis:** Author preprint abstract. [Inspected source](https://arxiv.org/abs/1902.05300).

The abstract studies sensitivity to small image or sampling perturbations, loss of small structural changes, and cases where additional samples reduce reconstruction quality.

**Scope signal:** Reconstruction instability and missing structure.

**Full-text question:** Separate adversarial perturbation, acquisition mismatch and missing-structure tests; record perturbation scales and comparator access. Link the 2019 preprint to the 2020 journal report.

### P004 — Real-World Blur Dataset for Learning and Benchmarking Deblurring Algorithms

**Recommendation:** AI pilot: advance. Human adjudication: pending.

**Evidence basis:** Publisher abstract. [Inspected source](https://link.springer.com/chapter/10.1007/978-3-030-58595-2_12).

RealBlur introduces paired real sharp/blurred images using a capture and postprocessing pipeline, motivated by the gap between synthetic blur benchmarks and real acquisition.

**Scope signal:** Real blur and synthetic-to-real degradation gap.

**Full-text question:** Inspect alignment, exposure and pairing limitations; assess whether it supports controlled mismatch tests. RealBlur is not a CCTV-specific benchmark.

### P005 — Robust Reconstruction With Deep Learning to Handle Model Mismatch in Lensless Imaging

**Recommendation:** AI pilot: advance. Human adjudication: pending.

**Evidence basis:** Author-hosted published PDF abstract and opening page. [Inspected source](https://www.eee.hku.hk/optima/pub/journal/2109_TCI.pdf).

The model-mismatch compensation network combines an unrolled model-based branch with a learned correction branch and evaluates lensless reconstruction under an imperfect forward model.

**Scope signal:** Explicit forward-model mismatch compensation.

**Full-text question:** Extract exactly what is corrected and what mismatch is held out; test whether uncertainty, measurement support or abstention are actually evaluated. Only the opening material was inspected here.

### P006 — Deep Equilibrium Architectures for Inverse Problems in Imaging

**Recommendation:** AI pilot: unclear. Human adjudication: pending.

**Evidence basis:** Author preprint abstract. [Inspected source](https://arxiv.org/abs/2102.07944).

The abstract motivates deep-equilibrium inverse solvers through fixed-point reconstruction, accuracy and computational properties. An explicit mismatch or reliability evaluation is not established by this abstract.

**Scope signal:** Not established from abstract.

**Full-text question:** Locate a criterion-3 experiment or claim. If none exists, retain as architectural background rather than an included primary study. Do not exclude on this pilot alone.

### P007 — Deep Probabilistic Imaging: Uncertainty Quantification and Multi-modal Solution Characterization for Computational Imaging

**Recommendation:** AI pilot: advance. Human adjudication: pending.

**Evidence basis:** Official proceedings abstract. [Inspected source](https://ojs.aaai.org/index.php/AAAI/article/view/16366).

Deep Probabilistic Imaging uses a generative variational approach to characterize posterior uncertainty and multimodal reconstructions in computational imaging, including interferometry and MRI.

**Scope signal:** Image posterior uncertainty and multimodal solutions.

**Full-text question:** Distinguish approximate posterior diversity from empirical calibration; determine whether the operator is fixed or uncertain.

### P008 — On Hallucinations in Tomographic Image Reconstruction

**Recommendation:** AI pilot: advance. Human adjudication: pending.

**Evidence basis:** Author preprint abstract. [Inspected source](https://arxiv.org/abs/2012.00646).

The paper introduces a framework and hallucination maps for tomographic reconstruction, relating learned-prior failures to measurement and null-space components, with numerical demonstrations.

**Scope signal:** Hallucination and measurement/null-space analysis.

**Full-text question:** Which maps require the unknown ground truth? Separate retrospective assessment from a deployable hallucination detector and inspect sensitivity to an incorrect operator.

### P009 — Designing a Practical Degradation Model for Deep Blind Image Super-Resolution

**Recommendation:** AI pilot: advance. Human adjudication: pending.

**Evidence basis:** Author preprint abstract. [Inspected source](https://arxiv.org/abs/2103.14006).

BSRGAN uses a practical randomized degradation design spanning blur, downsampling, noise and compression, including shuffled processing order and camera-processing effects.

**Scope signal:** Blind restoration with compound degradation.

**Full-text question:** Extract training/test degradation overlap and real-image evaluation; do not treat visual realism as measurement faithfulness or calibrated uncertainty.

### P010 — Real-ESRGAN: Training Real-World Blind Super-Resolution With Pure Synthetic Data

**Recommendation:** AI pilot: advance. Human adjudication: pending.

**Evidence basis:** Author preprint abstract. [Inspected source](https://arxiv.org/abs/2107.10833).

Real-ESRGAN trains from synthetic pairs using a high-order degradation process and models ringing and overshoot artifacts to address practical blind super-resolution.

**Scope signal:** Blind super-resolution with high-order degradation.

**Full-text question:** Identify which degradation combinations are evaluated rather than simulated only; separate perceptual restoration from identity/detail recovery.

### P011 — Image-to-Image Regression with Distribution-Free Uncertainty Quantification and Applications in Imaging

**Recommendation:** AI pilot: advance. Human adjudication: pending.

**Evidence basis:** Official proceedings abstract. [Inspected source](https://proceedings.mlr.press/v162/angelopoulos22a.html).

The paper constructs image-valued prediction intervals with statistical guarantees and demonstrates the approach on imaging applications including MRI, phase imaging and electron microscopy.

**Scope signal:** Calibrated image prediction intervals.

**Full-text question:** Record the coverage unit, calibration split and exchangeability assumptions; determine which claims survive operator or device shift. Distribution-free does not mean valid under arbitrary shift.

### P012 — Denoising Diffusion Restoration Models

**Recommendation:** AI pilot: advance. Human adjudication: pending.

**Evidence basis:** Official proceedings abstract. [Inspected source](https://proceedings.neurips.cc/paper_files/paper/2022/hash/95504595b6169131b6ed6cd72eb05616-Abstract-Conference.html).

DDRM uses a pretrained diffusion model for linear inverse problems and describes posterior-based restoration and transfer beyond the training-image distribution.

**Scope signal:** Posterior reconstruction and transfer across image distributions.

**Full-text question:** Determine known-operator and noise assumptions, posterior approximation error and whether calibration is tested; sample diversity alone is not calibration.

### P013 — All-in-One Image Restoration for Unknown Corruption

**Recommendation:** AI pilot: advance. Human adjudication: pending.

**Evidence basis:** Title and official author repository; abstract not retrieved. [Inspected source](https://github.com/XLearning-SCU/2022-CVPR-AirNet).

The AirNet title explicitly targets unknown corruption. Its official repository documents all-in-one and individual denoising, deraining and dehazing training/evaluation modes.

**Scope signal:** Unknown corruption and all-in-one restoration.

**Full-text question:** Retrieve the abstract and paper. Does one model handle separate task families, simultaneous compound corruption, unseen severity, or all of these? Do not equate all-in-one with compound-chain evaluation.

### P014 — Conffusion: Confidence Intervals for Diffusion Models

**Recommendation:** AI pilot: advance. Human adjudication: pending.

**Evidence basis:** Preprint abstract; peer review not established. [Inspected source](https://arxiv.org/abs/2211.09795).

Conffusion adapts pretrained diffusion models to predict confidence intervals for image reconstruction, including super-resolution and inpainting.

**Scope signal:** Diffusion-based confidence intervals.

**Full-text question:** Extract interval construction, calibration assumptions and OOD evaluation. Keep preprint status unless a corresponding peer-reviewed version is verified.

### P015 — Diffusion Posterior Sampling for General Noisy Inverse Problems

**Recommendation:** AI pilot: advance. Human adjudication: pending.

**Evidence basis:** Author preprint abstract. [Inspected source](https://arxiv.org/abs/2209.14687).

DPS approximates posterior sampling for noisy linear and nonlinear inverse problems, including settings with Gaussian or Poisson noise.

**Scope signal:** Approximate posterior reconstruction under noise.

**Full-text question:** Separate known functional form from genuinely unknown operators; record any empirical uncertainty calibration rather than assuming it follows from posterior terminology.

### P016 — Pseudoinverse-Guided Diffusion Models for Inverse Problems

**Recommendation:** AI pilot: unclear. Human adjudication: pending.

**Evidence basis:** Official search snippet only; full abstract not retrieved. [Inspected source](https://openreview.net/forum?id=9_gsMA8MRKQ).

The retrieved record identifies Pseudoinverse-Guided Diffusion Models for Inverse Problems, but page challenges and failed author-PDF retrieval prevented inspection of the complete abstract.

**Scope signal:** Cannot adjudicate from retrieved evidence.

**Full-text question:** Obtain the abstract/full text and test criterion 3. Access failure is not an exclusion reason at this stage; no substantive method coding was verified in this pilot.

### P017 — Zero-Shot Image Restoration Using Denoising Diffusion Null-Space Model

**Recommendation:** AI pilot: advance. Human adjudication: pending.

**Evidence basis:** Author preprint abstract. [Inspected source](https://arxiv.org/abs/2212.00490).

DDNM describes zero-shot restoration by refining the null-space component with a pretrained diffusion model while maintaining a data-consistency construction, with an extension for noisy observations.

**Scope signal:** Range/null-space reconstruction and measurement consistency.

**Full-text question:** Check when the consistency claim holds and whether null-space detail is supported by evidence. Data consistency alone does not identify the true image or prevent plausible hallucination.

### P018 — Parallel Diffusion Models of Operator and Image for Blind Inverse Problems

**Recommendation:** AI pilot: advance. Human adjudication: pending.

**Evidence basis:** Author preprint abstract. [Inspected source](https://arxiv.org/abs/2211.10656).

BlindDPS uses parallel diffusion models for the image and forward operator, with demonstrations in blind deblurring and turbulence reconstruction.

**Scope signal:** Joint image/operator inference in blind reconstruction.

**Full-text question:** Extract which operator functional forms remain assumed, training requirements for operator priors, identifiability limits and calibration evidence.

### P019 — GibbsDDRM: A Partially Collapsed Gibbs Sampler for Solving Blind Inverse Problems with Denoising Diffusion Restoration

**Recommendation:** AI pilot: advance. Human adjudication: pending.

**Evidence basis:** Official proceedings abstract. [Inspected source](https://proceedings.mlr.press/v202/murata23a.html).

GibbsDDRM proposes a partially collapsed Gibbs sampler for joint signal/operator inference using a diffusion restoration prior; blind image deblurring is among its applications.

**Scope signal:** Joint posterior inference for blind inverse problems.

**Full-text question:** Extract operator prior/family, sampler approximation and posterior calibration tests. Its additional audio experiments do not negate the central imaging application.

### P020 — PromptIR: Prompting for All-in-One Image Restoration

**Recommendation:** AI pilot: advance. Human adjudication: pending.

**Evidence basis:** Official proceedings abstract. [Inspected source](https://proceedings.neurips.cc/paper_files/paper/2023/hash/e187897ed7780a579a0d76fd4a35d107-Abstract-Conference.html).

PromptIR uses prompts to condition restoration on degradation information and evaluates denoising, deraining and dehazing under an all-in-one restoration design.

**Scope signal:** Unknown degradation types and levels.

**Full-text question:** Distinguish multiple separate tasks from simultaneous compound chains and unseen operators. The proceedings title omits 'Blind', which appears in the preprint title; this is not a separate study.

## Metadata and status repairs

- P001: replaced incorrect Dong authorship with Yuesong Nan and Hui Ji.
- P004: corrected CVPR to ECCV 2020 and replaced the erroneous CVF link with the publisher DOI; added the verified author list.
- P007: replaced the unrelated AAAI page ending 16430 with 16366; added the complete title, authors and DOI.
- P017/P019: replaced abbreviated DDNM and GibbsDDRM labels with complete titles.
- P020: corrected the NeurIPS proceedings hash and used its proceedings title; the differently worded preprint title belongs to the same lineage.
- All 90: changed seed-map Include labels to Pending formal eligibility. The original values and exact changes are in pilot_01_changes.json and git history.
- Protocol: reconciled the workbook's inconsistent 1.1 label with the authoritative v0.3 working-draft amendment; matched its query summary to the protocol without executing new database searches.

## Next actions

1. A human reviewer adjudicates all 20 recommendations, prioritizing unclear P006 and P016 and the abstract-access gaps P001/P013. Recheck borderline NETT P002 against criterion 3.
2. Retrieve and fully extract the nearest-method set P001, P005, P008, P011, P018 and P019, retaining page/section evidence for each capability and limitation.
3. Execute database-adapted queries, retaining raw exports, exact query syntax, dates, filters and counts. Reconcile seed IDs and preprint/proceedings/journal lineages against those exports.
4. Continue triage of P021–P090, without imposing a target number of inclusions. The earlier lineage-verification audit remains separate and must be reconciled during report-level deduplication.
5. Test a precise contribution against the nearest competitors. Failure to find one paper containing every desired feature is not evidence of novelty.
