# Systematic Review Protocol

## Working title

**Reliable Deep Image Reconstruction Under Forward-Model Mismatch: A Systematic Review of Operator Uncertainty, Hallucination and Selective Reconstruction (2020–2026)**

Protocol version: 0.3 (working draft, amended 16 September 2026; not registered)  
Search window: 1 January 2020 to 15 September 2026  
Historical exception: seminal pre-2020 work may be cited for conceptual background but is not included in the primary evidence synthesis.

## Rationale

Modern inverse-imaging systems increasingly combine learned priors with an explicit or implicit forward model. Performance can deteriorate when the deployed acquisition process differs from the assumed operator. Related work spans model-mismatch compensation, blind inverse problems, all-in-one restoration, posterior sampling, uncertainty quantification, hallucination analysis, out-of-distribution detection and selective prediction. These strands are commonly evaluated separately, making it difficult to determine whether any existing system provides end-to-end reliability under compound, unknown or time-varying mismatch.

## Primary review question

To what extent do learning-based image or video reconstruction methods remain accurate, calibrated and evidentially faithful when the true acquisition operator differs from the assumed forward model?

## Secondary questions

1. Which forms of operator mismatch are represented: parameter error, wrong operator family, unmodelled processing, compound degradation or temporal variation?
2. Are the latent image and operator estimated jointly?
3. Is uncertainty quantified for the image, the operator or both?
4. Is uncertainty empirically calibrated under in-distribution and out-of-distribution conditions?
5. Are unsupported or hallucinated details assessed against the measurement process?
6. Can the method detect failure or abstain from reconstruction?
7. Are claims validated using real measurements, physical hardware or cross-device/cross-dataset testing?
8. Which methods and benchmarks are reproducible from public code, weights and data?

## Eligibility framework

### Population/domain

Computational image or video reconstruction and restoration, including deblurring, super-resolution, tomography, MRI, microscopy, lensless imaging, compressive imaging, inverse scattering, low-light imaging and surveillance-oriented degradation.

### Eligible interventions

- model-based deep learning and unrolled optimization;
- plug-and-play or regularization-by-denoising approaches;
- discriminative restoration networks;
- diffusion, score-based or other generative inverse solvers;
- blind or joint image/operator estimation;
- differentiable calibration and operator learning;
- uncertainty, calibration, hallucination, OOD or selective-reconstruction methods tied to inverse imaging.

### Comparators

- correct versus perturbed or misspecified operators;
- known versus unknown operators;
- operator-oblivious versus operator-conditioned models;
- fixed versus jointly estimated operators;
- learned methods versus classical reconstructions;
- accepted versus selectively rejected reconstructions;
- synthetic versus real acquisition conditions.

### Outcomes

- full-reference and perceptual image quality;
- operator-parameter recovery;
- data consistency and measurement residual;
- robustness versus mismatch severity;
- uncertainty coverage, calibration and sharpness;
- OOD/failure detection;
- hallucination or measurement-support assessment;
- risk-coverage or abstention performance;
- external and real-hardware transfer;
- computational cost and reproducibility.

## Inclusion criteria

1. Primary technical research published or posted within the search window.
2. An image/video inverse problem or restoration task is central.
3. At least one of the following is explicit: forward-model mismatch, blind/unknown operator, joint calibration, compound degradation, time-varying degradation, reconstruction uncertainty, hallucination/measurement support, OOD reliability or selective abstention.
4. The work reports a method, benchmark, theorem with operational assessment, dataset or reproducible evaluation relevant to the review questions.
5. Full text is available in English.

## Exclusion criteria

- non-imaging inverse problems without a clearly transferable reconstruction method;
- enhancement papers that do not define or evaluate degradation/reconstruction;
- commentary, tutorials, editorials and non-primary summaries;
- duplicate reports of the same study, retaining the most complete peer-reviewed version and linking earlier preprints;
- papers using “physics-informed” only as a broad label without an imaging forward model or reconstruction relevance;
- papers for which neither full text nor sufficient technical evidence can be obtained.

## Information sources

- IEEE Xplore
- Scopus
- Web of Science
- ScienceDirect
- SpringerLink
- ACM Digital Library
- CVF Open Access
- NeurIPS proceedings
- ICLR/OpenReview
- ICML/PMLR
- SIAM journals
- Optica Publishing Group
- SPIE Digital Library
- arXiv for recent or not-yet-peer-reviewed work

Backward and forward citation chaining will be performed for all nearest competitors and landmark studies.

## Core search concepts

### Query A: operator mismatch

```text
("forward model mismatch" OR "operator mismatch" OR "model uncertainty" OR
 miscalibrat* OR "unknown operator" OR "blind inverse") AND
("image reconstruction" OR "video reconstruction" OR "inverse imaging" OR
 deblurring OR restoration)
```

### Query B: compound real-world degradation

```text
(restoration OR deblurring OR super-resolution OR surveillance OR CCTV) AND
(compound OR composite OR mixed OR unknown OR "time-varying") AND
(degradation OR operator OR acquisition) AND
(uncertainty OR calibration OR hallucination OR reliability OR robustness)
```

### Query C: reliability and abstention

```text
("inverse problem" OR "image reconstruction") AND
(hallucination OR "measurement support" OR "null space" OR calibration OR
 "uncertainty quantification" OR abstention OR "selective prediction" OR
 "risk coverage" OR conformal OR OOD)
```

Database-specific syntax, fields, filters, execution date and exact result count must be retained without normalization.

## Search management and deduplication

1. Export complete metadata and abstracts from every source.
2. Preserve the raw export unchanged.
3. Assign a stable screening-record identifier.
4. Deduplicate first by DOI, then normalized title/year, then manual author-title inspection.
5. Link preprint, conference and journal versions as one study lineage while preserving every report.
6. Record the reason for every manual merge.

## Screening

Screening has two stages:

1. title/abstract eligibility;
2. full-text eligibility.

Each exclusion receives one primary reason. Ideally two reviewers screen independently; if only one reviewer is available during the exploratory phase, all nearest competitors and a random subset of at least 20% must receive independent verification before publication. Disagreements are resolved by discussion and recorded.

### Exploratory AI-assisted pilot convention (16 September 2026)

The first 20 seed records, in stable ID order, form a convenience pilot to test the criteria and repair metadata. This is not a reproducible database search or a representative sample. Codex's recommendations are labelled `AI pilot: advance` or `AI pilot: unclear`; every recommendation requires human adjudication. AI is not an independent human reviewer.

Checkpoint continuation, 16 September 2026: P021–P040 were assessed under the same convention, bringing preliminary triage to 40 records. This is an execution-status update, not an eligibility, date-window or search-method change. Targeted full-text passages may support individual findings without constituting a complete full-text eligibility assessment.

An explicit title/abstract scope signal permits conservative advancement to full-text review; it does not establish all inclusion criteria. When an abstract cannot be retrieved, the exact evidence basis is recorded (for example, title and official author repository). Missing evidence is not converted into an exclusion. Uncertainty about relevance is retained as `unclear` for retrieval/adjudication.

Formal title/abstract, full-text, inclusion and exclusion counters remain separate from pilot progress. No record receives final inclusion from this pilot. Original discovery dates remain blank where undocumented; 16 September is the verification date, not an invented search/discovery date. All seed feature codes remain provisional until full-text extraction.

The amendment does not change the date window, eligibility criteria or search concepts. It also reconciles the workbook's inconsistent `1.1` version label with this authoritative document and aligns its abbreviated query summary. A 60–100-paper estimate is a planning range, never an inclusion quota.

## Data extraction

The controlled evidence matrix records bibliographic metadata plus:

- modality and data domain;
- forward model and operator access;
- mismatch type;
- solver family and physics integration;
- joint image/operator estimation;
- image and operator uncertainty;
- calibration and OOD evaluation;
- real data/hardware;
- compound and time-varying degradation;
- hallucination/support evaluation;
- abstention/selective prediction;
- code availability;
- evidence-verification status;
- nearest-competitor classification;
- contribution and unresolved gap.

## Quality and applicability appraisal

Each included empirical study will be rated on five dimensions using explicit evidence:

1. **Operator realism:** no mismatch test; simple parameter perturbation; wrong family/compound mismatch; measured physical mismatch.
2. **Evaluation validity:** random/in-distribution only; held-out degradation; cross-dataset/device; real hardware.
3. **Reliability validity:** variance only; calibrated uncertainty; hallucination/support assessment; selective risk.
4. **Reproducibility:** unavailable; partial details; code/weights; complete code-data-config pipeline.
5. **Claim alignment:** claims supported, partly supported or unsupported by the reported design.

The appraisal is descriptive and will not be collapsed into a single opaque “quality score.”

## Synthesis

Because tasks, operators, metrics and datasets are expected to be heterogeneous, the primary synthesis will be structured and tabular rather than a pooled meta-analysis. Planned outputs are:

- chronological evolution map;
- method taxonomy;
- mismatch-versus-reliability evidence matrix;
- nearest-competitor table;
- solved/partially solved/open problem map;
- evidence-gap heatmap;
- narrative synthesis grouped by operator access and reliability capability.

A quantitative synthesis will be attempted only for genuinely comparable settings and will not combine incompatible PSNR, SSIM or task results.

## Novelty falsification rule

The proposed methodological contribution is rejected or materially redesigned if a fully verified existing study jointly demonstrates:

1. compound or time-varying operator mismatch;
2. joint image and operator inference;
3. calibrated uncertainty for both image and operator;
4. measurement-supported-detail or hallucination assessment;
5. explicit OOD evaluation;
6. selective prediction or abstention;
7. real surveillance-oriented or comparable physical validation.

Partial overlap narrows the contribution but does not alone establish duplication.

Conversely, failure to find one paper combining all seven features does not prove novelty. A defensible contribution must address a specific limitation relative to the closest methods, not merely assemble a longer feature checklist.

## Reporting and registration

The review will be reported using PRISMA 2020 and the search methods documented with PRISMA-S principles. Before formal database screening is completed, the protocol should be frozen and registered on a general-purpose repository such as OSF. Deviations from the registered protocol will be dated and justified.

## Planned updates

The evidence search will be refreshed immediately before manuscript submission. A weekly horizon scan may identify candidates, but papers enter the formal synthesis only after normal screening and verification.
