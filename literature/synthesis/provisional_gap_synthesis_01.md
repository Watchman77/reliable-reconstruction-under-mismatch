# Provisional research-gap synthesis 01

**Date:** 16 September 2026

**Basis:** eleven AI full-text checkpoints; 89 assessed seed records, comprising 88 include recommendations and one exclude recommendation. P035 awaits full text.

**Status:** a research-design synthesis of inspected evidence, not a completed systematic review, a meta-analysis, or a finding of established novelty.

## Decision

Retain **Physics-Informed Deep Learning for Robust Image Reconstruction Under Forward-Model Mismatch** as the umbrella topic. Proceed to a bounded reliability experiment before designing a large architecture.

The recommended first question is:

> At a useful level of retained image detail, does operator-sensitive uncertainty improve error detection and selective reconstruction beyond image-only uncertainty and measurement-residual scores, especially when acquisition leaves the assumed operator family?

This is a candidate contribution. Joint image/operator sampling, mismatch correction, calibration, hallucination assessment and fallback already have relevant predecessors. Their combination alone is insufficient novelty. The experiment must demonstrate a specific improvement over strong comparators and explain its mechanism and limits.

The existing single-image classical canary establishes an operational pipeline and a residual-versus-fidelity counterexample. It does not establish the new question's answer. Its compound-condition ordering was not monotonic; that result must remain visible. See [the canary report](../../experiments/phase0_canary/CANARY_RESULT.md).

## Evidence boundary and reproducibility

The [generated inventory](evidence_inventory_01.md) indexes all 90 records, and the [JSON snapshot](evidence_snapshot_01.json) identifies every extracted feature, source, locator, assessment checkpoint and input-file hash. The main provisional synthesis uses the 88 AI include recommendations. P060 remains an ancillary CCTV quality-dataset reference; it is excluded from those descriptive counts. P035 contributes no full-text conclusions.

Only explicitly extracted full-text fields are used. An unextracted field is not a negative finding. An affirmative calibration code means calibration was evaluated within the recorded scope; it does not imply successful coverage under deployment shift. Many records were assessed through specified preprint versions. Those findings are not silently promoted to final-publication evidence.

Counts concern records, not independent studies. In particular, FaverNet explicitly builds on AverNet (P053/P026); their shared experiments need adjudication before study-level synthesis. The inventory also flags P064's legacy time-variation code: its projection-dependent tomography motion is not video-sequence variation under the dictionary's literal definition. No code is silently recoded here.

Formal searches, lineage/version reconciliation and human adjudication remain in the [deferred-work list](../screening/deferred_review_tasks.md). They can proceed alongside feasibility work. Completing those tasks would finish the existing review workflow; it is not a new round of screening all 89 papers from scratch.

## Taxonomy: what problem is actually being solved?

These axes describe different assumptions, not mutually exclusive rankings of methods.

| Axis | Distinctions needed | Examples and implications |
|---|---|---|
| Operator access | Known operator; approximate supplied operator; unknown parameters within a specified family; unmodelled acquisition process | P012/P015/P016 supply the measurement map; P018/P019/P038 sample within parameterized families; P047/P079 learn discrepancy. Supplying a new correct map is different from discovering an incorrect one. |
| Mismatch | Parameter error; wrong functional family; noise/codec mismatch; prior/content shift | P048 varies a supplied blur parameter; P050 addresses a learned codec map; P033 targets content-distribution shift. These outcomes cannot be pooled as one OOD result. |
| Output uncertainty | Image samples; operator samples; neural-weight uncertainty; categorical degradation weights; deterministic sets | P018/P019/P038 provide image/operator sampling; P065 addresses image/weight uncertainty; P071/P073 supply categorical weights; P042 uses deterministic certificates. |
| Reliability claim | Measurement agreement; reference-image error; interval coverage; measurement-support assessment; selective risk | P008/P037 assess support under specified operators; P011/P062 evaluate risk-controlled sets; P042/P063/P073/P077 make different forms of fallback/stopping decisions. |
| Acquisition evidence | Simulated measurements; captured paired reference; captured unpaired image; extra sensor information | P004/P058/P059 provide paired-data routes with reference limitations; P053 uses unpaired real-video metrics; P054 has extra event measurements. These are different information budgets. |

The full record-by-record evidence is linked in the inventory. The following comparisons concentrate on the work that most directly constrains the proposed mechanism.

## Nearest-competitor comparison

Each limitation below means “not established in the inspected evidence,” not “the authors could never address it.” Statements about what our experiment should do are our design inferences.

| Existing work | What the assessed evidence establishes | Remaining comparison we must make |
|---|---|---|
| P001/P005/P029: mismatch-aware unrolling | Kernel-error compensation and lensless correction already exist, including captured-image experiments. P029 estimates a structured nuisance term, not a physical PSF posterior. [P001](https://raw.githubusercontent.com/ysnan/NBD_KerUnc/master/paper/kn.pdf), [P005](https://www.eee.hku.hk/optima/pub/journal/2109_TCI.pdf), [P029 record](../screening/full_text_10.json). | Include mismatch compensation as a baseline; ask whether residual fitting improves retained-detail fidelity as well as observation fit. |
| P018/P019/P038: BlindDPS, GibbsDDRM, PRISM | Joint image/operator sampling is established. PRISM uses a measurement-conditioned kernel prior; the inspected report evaluates motion blur and specified Gaussian noise. These are the principal comparators for adding operator uncertainty. [BlindDPS](https://arxiv.org/html/2211.10656v1), [GibbsDDRM](https://proceedings.mlr.press/v202/murata23a/murata23a.pdf), [PRISM](https://arxiv.org/html/2509.16106v1). | Test selected-detail error at matched retained coverage under an omitted acquisition process; keep within-family and outside-family shifts separate. A new sampler is not required to test this. |
| P022/P024/P045/P046: EM, latent inference and joint point estimation | Several methods infer an operator point estimate. P046's inspected blind-deblurring example also records kernel collapse, illustrating an identifiability issue. [P022](https://arxiv.org/html/2309.00287v2), [P024](https://arxiv.org/html/2407.01027v1), [P045](https://proceedings.neurips.cc/paper_files/paper/2023/file/f810c2ba07bae78dfe9d25c5d40c5536-Paper-Conference.pdf), [P046](https://arxiv.org/pdf/2202.11342v3). | Hold image prior and inference budget fixed when comparing a point operator with multiple plausible operators; disclose failures and extra compute. |
| P047/P050/P052/P079/P080: flexible or structured operator correction | Learned residuals, learned nonlinear maps, monotone intensity operators and image-sized additive masks already support blind reconstruction. [P047](https://arxiv.org/html/2403.04847v1), [LADiBI](https://arxiv.org/html/2412.00557v1), [P052](https://arxiv.org/html/2603.01890v1), [P079](https://arxiv.org/html/2408.11287v1), [GDP](https://arxiv.org/html/2304.01247v1). | Distinguish compensating for mismatch from identifying its physical cause. Our inference: a flexible residual may improve fit without resolving truth. P035 is an unresolved direct competitor to this route. |
| P048: posterior sensitivity under mismatch | Bounds address changes in sampling distributions under assumed denoiser/operator perturbations, with stated regularity conditions; supplied-operator deblurring experiments are included. [ICLR paper](https://proceedings.iclr.cc/paper_files/paper/2024/file/2a2874875861f6a6436b505dd77683d1-Paper-Conference.pdf). | Distribution-distance bounds are not automatically bounds on retained-region error. Any new theoretical claim must specify the uncertainty set, sampling approximation and selection rule. |
| P008/P031/P037: hallucination and recoverability analysis | Known-operator support assessment and accuracy/stability limits already exist. P037's feasible-set search approximates diameter from below; finding little disagreement does not produce an upper error certificate. [P008](https://arxiv.org/html/2012.00646v3), [P031](https://arxiv.org/html/2001.01258v4), [P037](https://arxiv.org/html/2605.13146v1). | Keep reference-based error evaluation separate from deployable support evidence; account for uncertain operators without assuming a finite candidate search is exhaustive. |
| P011/P014/P062/P063/P065/P066/P067: calibrated imaging uncertainty | Image-set calibration, diffusion intervals, task-specific intervals and self-supervised calibration already exist. P066 requires a known full-rank linear map and specified Gaussian noise; SURE substitution needs care. [P011](https://proceedings.mlr.press/v162/angelopoulos22a/angelopoulos22a.pdf), [P062](https://proceedings.mlr.press/v202/teneggi23a/teneggi23a.pdf), [P066](https://arxiv.org/html/2502.05127v1). | Evaluate coverage after selection and under acquisition shift separately. A matched-distribution marginal guarantee does not automatically survive either change. Other source/version details are in the inventory. |
| P042: certificate-based fallback | A baseline-certificate comparison and fallback rule already exist. The weighted operational score differs from the theoretical radius, and numerical candidates are constructed using perturbed truth. Uncertain observation operators are an explicit limitation. [Inspected preprint](https://arxiv.org/html/2606.07153v1). | Use actual reconstruction algorithms as candidates; compare with a plainly labelled residual/fallback adaptation. Do not describe an adaptation as a reproduction of the theorem. |
| P026/P040/P049/P053/P056/P070: changing acquisition and video restoration | VDPS jointly estimates images and changing physical parameters; DeepVibes estimates intra-image camera attitude; AverNet/FaverNet and other video methods address changing compound degradation. [VDPS record](../screening/full_text_11.json), [FaverNet](https://doi.org/10.1007/s11263-026-02977-y), [AverNet](https://proceedings.neurips.cc/paper_files/paper/2024/file/e635a25e49e73adc51f76aef462ff2f8-Paper-Conference.pdf). | Temporal modelling itself is occupied. Test reliability after a degradation change, and separate temporal consistency from fidelity. Treat the AverNet/FaverNet lineage as related evidence. |
| P073/P077 and strong general restorers | Clean-class stopping and tool rollback already offer forms of failure handling. Compound, prompted and generative restoration are well represented by P009/P010/P020/P039/P055/P074–P090. [AutoDIR](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/05684.pdf), [RestoreAgent](https://proceedings.neurips.cc/paper_files/paper/2024/file/c78f639424b8d89ceb4f2efbb4dfe4f4-Paper-Conference.pdf). | Compare against simple confidence/stopping baselines where reproducible. Better appearance, prompt agreement or task scores alone do not certify image detail. |

## What is established, conditional, or unresolved?

| Question | Position supported by this seed synthesis |
|---|---|
| Can learned reconstruction incorporate physics and compensate for some operator error? | Established in specific settings. It is not our novelty claim. |
| Can image and operator be inferred jointly, including through sampling? | Established within specified families. Unknown parameters are different from an unknown functional form. |
| Can an imaging method produce calibrated sets? | Established under specified targets and statistical conditions. Image-level, pixel-average, task-score and selected-region coverage must be distinguished. |
| Can methods handle compound or temporally changing degradation? | Established for several simulated and captured settings. This does not settle faithful recovery under every device/codec shift. |
| Does operator-sensitive information add useful selective fidelity beyond strong uncertainty and residual baselines under omitted acquisition processes? | A testable candidate question. The current evidence does not establish the answer or novelty. |
| Can arbitrary lost detail be certified from one severely degraded observation? | No such universal claim is justified. Equivalent or near-equivalent observations can remain ambiguous within and outside a fitted model family. |

## Three candidate problems, ranked for the next experiment

The rankings are research judgments based on the recorded comparisons, not measured probabilities of publication.

| Rank | Candidate problem | Novelty opportunity and strongest overlap | Difficulty / practicality | Decision |
|---|---|---|---|---|
| 1 | Operator-sensitive selective reconstruction under an omitted acquisition process | A specific incremental reliability effect may remain to demonstrate against PRISM/BlindDPS/GibbsDDRM, calibrated intervals and fallback. Joint sampling or variance decomposition alone is established methodology. | Medium to high; most practical first test because it can wrap frozen reconstructions and use paired synthetic data. | Start the pilot in the linked specification. |
| 2 | Constraining learned discrepancy so that improved data fit does not conceal incorrect detail | A mechanism tying discrepancy capacity to identifiability and reliable release could matter. P047/P050/P052/P079/P080 overlap strongly; pending P035 can materially change this route. | High; requires a constrained correction model and careful ambiguity analysis. | Defer architecture design until P035 is read and rank 1 exposes a concrete failure to fix. |
| 3 | Selective video reconstruction after changes in acquisition, with temporal dependence accounted for | Reliable retention and recovery after degradation changes may be useful. VDPS, AverNet/FaverNet, RealBasicVSR, Ronin and existing stopping methods preclude a generic temporal-restoration claim. | High; least practical first because temporal calibration, scene separation and paired/cross-device data increase scope. | Extend rank 1 only after a still-image mechanism proves useful. |

## Proposed contribution and falsification

**Working contribution, conditional on evidence:** a reproducible evaluation and lightweight selection mechanism that uses sensitivity to plausible acquisition models to improve fidelity of retained image detail, with separately reported limits when all candidate models are misspecified.

Proceed only if the mechanism improves over the best matched-budget image-only and residual baselines at useful coverage, across more than one reconstruction family. A result on one weak classical method would justify further diagnosis, not a journal-method claim.

Reject or redesign this candidate if:

- a closest competitor already supplies the same mechanism and evidence under equivalent assumptions;
- the operator-sensitive score adds no reproducible benefit at matched coverage and compute;
- gains disappear after controlling for image quality, image prior, prompts or oracle operator information;
- useful error control requires rejecting nearly all informative regions;
- the rule needs unavailable clean truth or true acquisition parameters at deployment;
- common misspecification makes image and operator samples agree confidently while wrong, and the proposed diagnostic cannot help.

The final case is an expected stress test, not a result to conceal. Failure could motivate candidate 2, or a benchmark/negative-result contribution if the evidence is sufficiently strong and novel. It does not automatically justify another architecture.

## Immediate execution and outstanding evidence

1. Use the [pilot specification](../../docs/selective_reconstruction_pilot_spec.md) to freeze the information budget, image splits, acquisition regimes, retained-detail target and comparison rules before a substantive run.
2. Audit one operator-conditioned learned implementation and one blind sampler for code, weights, licence, input domain and feasible compute. The named papers are comparator requirements; none is claimed reproduced in this synthesis.
3. Build the multi-image experiment from the existing canary infrastructure. The first run is a feasibility study, not a confirmatory result or a formal risk guarantee.
4. Incorporate P035 when received. The user has sent an author-copy request; no response or full text is inferred. The school-mail connection required administrator approval and is not needed for the research workflow.
5. Complete deferred searches, adjudication and relevant source/version checks before a definitive novelty statement or systematic-review manuscript.

The earlier [rapid map](../../docs/rapid_gap_map_2020_2026.md) is retained as exploratory history. This synthesis supersedes its feature-intersection rationale for choosing the next research step.
