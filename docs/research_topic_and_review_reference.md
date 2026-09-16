# Research topic and review plan

Prepared for Bamidele Akinwumi • 16 September 2026 • Reference note version 1.0

## The topic we are taking forward

**Physics-Informed Deep Learning for Robust Image Reconstruction Under Forward-Model Mismatch**

We retain this original topic as the umbrella for the experimental research programme. The literature investigation has sharpened the contribution to test within it. It supports proceeding to a bounded experiment; it has not established that a new method is novel or superior.

**Focused experimental working title:** Operator-Sensitive Selective Reconstruction Under Forward-Model Mismatch.

**Primary research question:** At a useful level of retained image detail, does accounting for uncertainty in the imaging operator improve error detection and selective reconstruction beyond image-only uncertainty and measurement-residual scores, especially when the true acquisition process leaves the assumed operator family?

The focused title is a working title for the first study, subject to its results. It sits within the original physics-informed deep-learning topic. Here, physics-informed means using an explicit acquisition model during reconstruction or consistency assessment; it does not require a differential-equation PINN.

## What the key terms mean

- **Forward model:** the description of how the camera turns a scene into a measurement, including blur, sampling, noise and declared processing.
- **Mismatch:** an incorrect parameter or a missing process in that description, such as compression absent from a blur-only model.
- **Operator sensitivity:** how reconstructed detail changes across plausible acquisition models. Such variation is not automatically a calibrated probability.
- **Selective reconstruction:** attaching a retain or flag decision to reconstructed regions, with both retained coverage and their measured error reported.

## What the 90 record investigation establishes

| Evidence stage | Status on 16 September 2026 |
| --- | --- |
| Seed records assembled | 90 |
| AI full-text assessments completed | 89 |
| AI recommendations | 88 include and 1 exclude |
| Full text still awaited | P035 on learned residuals and diffusion priors |
| Formal human inclusion decisions | Pending across the corpus |

These are records, not 90 independent, formally included studies. Related reports and inspected preprint versions require reconciliation. The synthesis therefore provides a provisional research direction, not an exhaustive proof of novelty. Its source-linked inventory preserves the evidence behind each assessment [1].

<!-- pagebreak -->

## What the literature has already covered

The broad proposal to combine physics, learning and mismatch compensation overlaps existing research. The following comparisons explain why we narrowed the first experiment. Findings refer to the versions inspected in our evidence register [1].

| Existing line of work | Consequence for our contribution |
| --- | --- |
| Mismatch-aware reconstruction and unrolling, including P005 [2] | Adding a physics layer or learned correction alone is insufficient. |
| Joint image and operator sampling in BlindDPS, GibbsDDRM and PRISM [3–5] | Estimating or sampling an unknown blur operator alone is insufficient. |
| Calibrated image uncertainty and conformal risk control [6–7] | Producing uncertainty intervals alone is insufficient; their target and conditions matter. |
| Certificate-based fallback in P042 [8] | A generic claim that reconstruction can fall back or reject is insufficient. |
| Learned residuals and diffusion priors in P035 [9] | This direct competitor remains unresolved until its full text is available. |

The full synthesis also covers posterior sensitivity, hallucination assessment, compound restoration and video methods. We do not infer that these areas are unsolved because a selected method lacks one feature. Nor do we treat an unextracted feature as evidence of absence.

## The specific opportunity to test

Our candidate contribution is a reproducible evaluation and a lightweight selection mechanism that uses sensitivity to plausible acquisition models to improve the fidelity of retained detail. The comparison must hold image priors, supplied information and compute budgets as equal as practicable.

For example, consider a frame blurred and then compressed. A reconstruction method assumes blur and noise but omits compression. Its output may fit that assumed model while containing incorrect fine detail. We will test whether variation across plausible operators helps identify unreliable regions better than image-only variability or measurement fit. This example motivates an experiment; it is not an observed result of the proposed method.

**The strongest counterexample:** every candidate operator can share the same missing process. Their outputs may agree confidently while wrong. The study must expose this case and report whether the proposed score helps, fails or needs redesign.

**Our defensible position:** the candidate remains worth testing after the current seed investigation. Novelty will depend on a specific mechanism and evidence beyond the closest methods, completion of the outstanding literature work, and results that survive fair comparisons. Combining several established features is not sufficient.

<!-- pagebreak -->

## Experimental objectives and first pilot

The five original objectives remain intact, with more precise tests.

| Original objective | Operational form for the first study |
| --- | --- |
| Incorporate the forward operator | Use an explicit acquisition model with frozen reconstruction methods. |
| Model acquisition uncertainty | Compare one fitted operator with several plausible operators; distinguish sensitivity from posterior sampling. |
| Compare method families | Include classical, operator-conditioned learned, operator-oblivious and blind generative methods where reproducible. |
| Evaluate distribution shifts | Separate parameter error, wrong model family and omitted processing; retain matched-condition controls. |
| Measure quality and reliable uncertainty | Evaluate PSNR and SSIM alongside error detection, calibration and selective risk at useful retained coverage. |

Start with still images. CCTV remains a motivating application and later external test, while controlled degradation provides the clean references needed to measure detail errors. Unpaired CCTV footage can illustrate behaviour but cannot establish pixel-truth accuracy or actual identity recovery.

The draft pilot [1] specifies the following sequence:

1. **Audit available implementations.** Check code, weights, input domain, licence and compute. A face-trained prior must not be treated as a general-image method without a declared domain control.
2. **Separate source images.** Use disjoint development, calibration and test partitions; initially target at least 100 unique calibration and 100 unique test sources. Keep all crops and degradation variants from each source together.
3. **Freeze acquisition conditions.** Compare correct-family parameter uncertainty against an omitted compression or resampling stage. Add spatially varying blur as a structural stress test.
4. **Compare reliability scores fairly.** Test residual-only, image-only variability, operator sensitivity and a simple combined score. Report extra operator-estimation cost and matched-compute comparisons.
5. **Evaluate retained detail.** Report risk–coverage curves, risk at 50, 75 and 90 percent retention, textured-region results and source-level uncertainty intervals. Fit choices on development data and thresholds on calibration data before test evaluation.

**Progression criterion:** the draft targets a reduction of at least two percentage points in the bad-detail rate at 50 percent retention under the omitted-process condition, supported across two reconstruction families and interpreted with paired uncertainty intervals. This is a provisional engineering gate, not a promised effect or formal guarantee.

A null result, gains that disappear against strong comparators, or useful error control only after rejecting almost everything would trigger redesign or stopping this candidate. No new architecture or multi-image pilot result is claimed yet.

<!-- pagebreak -->

## The review paper alongside the experiment

**Recommended review working title:** Reliable Deep Image Reconstruction Under Forward-Model Mismatch: A Scoping Review of Operator Uncertainty, Hallucination and Selective Reconstruction.

This review would map what has been studied, how reliability is defined, which acquisition assumptions are used, and where evidence is missing. That purpose fits a scoping review. A systematic review would be preferable for a defined comparative question requiring an appraisal and synthesis of the relevant results [10]. Both require transparent, structured methods.

Use PRISMA-ScR to report the scoping review [11]. It is a reporting guideline, not certification that a search or screening process is complete. The current protocol file remains an unregistered v0.4 draft labelled systematic review. This note records the recommended scoping direction; a dated protocol amendment must align the question, methods and reporting before the formal review is represented that way.

## The workflow to document

1. **Protocol and criteria.** Retain the current 1 January 2020 to 15 September 2026 window, with older foundations used as background. Define eligible imaging tasks, mismatch or reliability concepts, study types, languages and treatment of preprints and related reports.
2. **Searches.** Execute and save database-specific queries, search dates, fields, filters, result counts and raw exports. The source plan includes IEEE Xplore, Scopus or Web of Science where accessible, and relevant proceedings, publisher sites and preprint sources. Record access limitations and any justified substitutes.
3. **Deduplication and screening.** Preserve record provenance and distinguish duplicate citations from related publications. Conduct title and abstract screening, then full-text screening, with a specific reason for each full-text exclusion. Record inaccessible reports as not retrieved rather than irrelevant.
4. **Human review.** Plan for two human reviewers independently applying eligibility criteria, with disagreements resolved and documented. AI extractions can assist verification but do not count as a second independent human reviewer. Existing assessments remain preparatory evidence; independent decisions still need to be recorded.
5. **Chart and synthesize.** Map operator assumptions, methods, uncertainty, calibration, real-world evidence, failure handling and reproducibility. Describe technical limitations; specify any formal appraisal separately. Avoid pooling incompatible outcomes into a ranking of methods.

## Software and immediate next actions

Use **Zotero** for references, PDFs, notes, tags and citations [12]. Review its proposed duplicates manually [13]. Keep our matrix and GitHub records for extraction and the audit trail. Covidence or Rayyan can support collaborative screening [14–15]; choose one if it simplifies the human workflow. Mendeley is an alternative reference manager, not an additional methodological requirement.

Next, align the review protocol and reviewer arrangements, import the existing draft RIS into Zotero, and start the baseline feasibility audit. Formal searches may add records; 90 is not a quota. The review and experiment can progress alongside the pending author-copy request for P035.

<!-- pagebreak -->

## Reference sources and project records

Paper IDs refer to our evidence matrix. Listed sources identify the inspected versions or, for P035, the pending publication. They are a selected reading route; the repository holds the full 90-record index. Bibliographic exports remain draft metadata.

[1] Project evidence and design. [Provisional gap synthesis 01](https://github.com/Watchman77/reliable-reconstruction-under-mismatch/blob/main/literature/synthesis/provisional_gap_synthesis_01.md), [90-record evidence inventory](https://github.com/Watchman77/reliable-reconstruction-under-mismatch/blob/main/literature/synthesis/evidence_inventory_01.md) and [pilot specification v0.1](https://github.com/Watchman77/reliable-reconstruction-under-mismatch/blob/main/docs/selective_reconstruction_pilot_spec.md). Snapshot dated 16 September 2026; synthesis release commit 61148107292c17e1a480f2ea5d7df4b3a2bbdec2.

[2] P005. Robust Reconstruction With Deep Learning to Handle Model Mismatch in Lensless Imaging. IEEE TCI, 2021. [Author-hosted final PDF](https://www.eee.hku.hk/optima/pub/journal/2109_TCI.pdf).

[3] P018. Parallel Diffusion Models of Operator and Image for Blind Inverse Problems, known as BlindDPS. [Inspected arXiv v1, 2022](https://arxiv.org/html/2211.10656v1); final CVPR 2023 text not compared.

[4] P019. GibbsDDRM: A Partially Collapsed Gibbs Sampler for Solving Blind Inverse Problems with Denoising Diffusion Restoration. [ICML 2023 proceedings](https://proceedings.mlr.press/v202/murata23a/murata23a.pdf).

[5] P038. PRISM: Probabilistic and Robust Inverse Solver with Measurement-Conditioned Diffusion Prior for Blind Inverse Problems. [Inspected arXiv v1, 2025](https://arxiv.org/html/2509.16106v1); final ICASSP 2026 text not compared.

[6] P011. Image-to-Image Regression with Distribution-Free Uncertainty Quantification and Applications in Imaging. [ICML 2022 proceedings](https://proceedings.mlr.press/v162/angelopoulos22a/angelopoulos22a.pdf).

[7] P062. How to Trust Your Diffusion Model: A Convex Optimization Approach to Conformal Risk Control. [ICML 2023 proceedings](https://proceedings.mlr.press/v202/teneggi23a/teneggi23a.pdf).

[8] P042. No-Harm Physics-Informed Inverse Learning with Residual-Calibrated Uncertainty. [Inspected arXiv v1, 2026](https://arxiv.org/html/2606.07153v1).

[9] P035. Lee and Jang. Mitigating forward model mismatch in inverse problems via learned residuals and diffusion priors. SPIE, 2026. [DOI 10.1117/12.3098133](https://doi.org/10.1117/12.3098133). Full text pending; no full-text findings attributed here.

[10] Munn et al. Systematic review or scoping review? Guidance for authors when choosing between a systematic review or scoping review approach. BMC Medical Research Methodology, 2018. [DOI 10.1186/s12874-018-0611-x](https://doi.org/10.1186/s12874-018-0611-x).

[11] PRISMA. [PRISMA extension for scoping reviews](https://www.prisma-statement.org/scoping). Reporting checklist and explanation.

[12] Zotero. [The Basics](https://www.zotero.org/support/quick_start_guide). [13] Zotero. [Duplicate Detection](https://www.zotero.org/support/duplicate_detection).

[14] Covidence. [Reviewers](https://www.covidence.org/reviewers/). [15] Rayyan. [Official platform overview](https://www.rayyan.ai/). Software documentation checked 16 September 2026; no subscription or connection is assumed.
