# Reliable Reconstruction Under Forward-Model Mismatch

Research repository for a journal-first programme on evidence-calibrated image reconstruction under compound, unknown and time-varying acquisition mismatch.

## Current status

- 90-record seed evidence matrix covering 1 January 2020 to 15 September 2026.
- Systematic-review protocol v0.4, a dated working draft that is not yet registered.
- Initial triage complete for all 90 seed records: 82 advance recommendations, 8 unclear, 0 untriaged. 89 AI full-text eligibility assessments are now complete: 88 include recommendations, 1 exclude; 1 remains. Human adjudication and final formal eligibility remain pending.
- Evidence basis is recorded per study. Inspected versions, reading extent and criterion-level decisions are recorded; incomplete retrieval is flagged explicitly.
- Zero formally included studies. Only the feature fields explicitly listed in the full-text register are verified; other seed codes remain provisional.
- Rapid adversarial gap map completed.
- Provisional full-text synthesis completed using the 88 AI include recommendations, with a source-linked 90-record inventory and three ranked candidate problems.
- Phase-0 classical canary implemented and executed.
- Formal database screening and the 100-image pilot remain outstanding.
- Experimental work is now the user's priority. An initial dataset/baseline audit is complete; 100 DIV2K sources are acquired for development only, with 24 paired observations generated from 12 sources. Independent calibration/test evaluation has not run; the learned-baseline development checkpoint below now covers four previously exposed sources.
- A separate [four-source Colab pilot](experiments/colab_pilot_00/README.md) has saved successful execution checks. Its fixed inverses underperform the degraded-input baseline on average, and operator spread does not beat the best simple control at 50% pixel retention. The dated Drive export has since been located; the earlier review is retained as a historical checkpoint.
- [Baseline 01](experiments/baseline_01/README.md) now has a saved, executed development notebook, result tables and four inspected figures. Across 48 simulated combinations of the same four sources, source-excluded tuning gives the nominal gradient-regularised inverse pooled gains of 1.141 dB and 0.615 dB over input for linear and JPEG-chain conditions. Ridge remains weaker on average. Patch-level operator spread improves over the included controls in pooled comparisons; these are development findings, not novelty or independent-test claims. The initial execution used in-process IPython. The [subsequent saved Colab run is now reviewed](experiments/baseline_01/colab_execution_review_2026-09-17.md), including eleven code cells, three reconciled tables and four embedded figures. The [uploaded results archive](experiments/learned_02/archive_verification_20260917/verification.md) subsequently confirms all 14 exported file hashes for this Colab run.

- [Learned baseline 02](experiments/learned_02/README.md) now has a [reviewed eight-observation Colab run](experiments/learned_02/colab_execution_review_2026-09-17.md) on the same four development sources. Nine unchanged code cells report successful CUDA execution, 40 quality rows, 448 risk rows and 392 experiment denoiser calls. Six retrieved CSVs reproduce three displayed tables; four embedded figures were inspected. Nominal DPIR improves over the classical comparator by 0.494 dB for linear blur/noise but loses by 0.412 dB with the JPEG chain; its JPEG-chain detail MSE is 35.237% higher. Operator sensitivity gives positive pooled mean-error comparisons with source-specific and bad-detail-rate exceptions. The original one-case checkpoint remains preserved. The [completed-run archive verification](experiments/learned_02/archive_verification_20260917/verification.md) now confirms all 23 exported file hashes, eight saved nominal predictions and all 448 risk rows; four raw figures and the saved JPEG predictions were inspected. An older partial run is separately flagged and excluded. Independent calibration/testing and novelty remain unestablished.

- [Acquisition-stage diagnosis 03](experiments/acquisition_03/README.md) adds a frozen four-stage experiment separating clipping, 8-bit rounding and JPEG processing while preserving all five Learned 02 quality comparators. The [completed 16-observation Colab run is now reviewed](experiments/acquisition_03/colab_execution_review_2026-09-17.md): nine CSVs reproduce six tables; all 16 regenerated observation hashes and 32 input/classical quality rows agree. The nominal reconstruction gap worsens at JPEG processing across all four sources in detail MSE. Four embedded figures were inspected. The [complete raw archive audit](experiments/acquisition_03/archive_verification_20260917/verification.md) now verifies the reconstructed ZIP, all 38 export hashes, all 80 saved metric rows, all 160 patch-error vectors and all 240 full-coverage tail rates. Nine CSVs and four raw figures match the prior review byte for byte; a new fixed-inset montage covers all four sources. No further archive upload is required for this run. No new solver, tuning, novelty or calibration claim is introduced.

The 90 studies are a seed evidence map, not a completed PRISMA corpus. The repository must not be cited as a systematic review until database searches, deduplication, two-stage screening, exclusion logging, full-text verification and citation chaining are complete.

See the [latest full-text checkpoint](literature/screening/full_text_11_report.md) and [criterion-level evidence](literature/screening/full_text_11.json), alongside [checkpoint 01](literature/screening/full_text_01_report.md), [checkpoint 02](literature/screening/full_text_02_report.md), [checkpoint 03](literature/screening/full_text_03_report.md), [checkpoint 04](literature/screening/full_text_04_report.md), [checkpoint 05](literature/screening/full_text_05_report.md), [checkpoint 06](literature/screening/full_text_06_report.md), [checkpoint 07](literature/screening/full_text_07_report.md), [checkpoint 08](literature/screening/full_text_08_report.md), [checkpoint 09](literature/screening/full_text_09_report.md), [checkpoint 10](literature/screening/full_text_10_report.md) and the preserved [first pilot](literature/screening/pilot_01_report.md). The matrix, screening log and reference exports are synchronized; bibliographic corrections are recorded in field-level audits. Reference exports remain draft metadata, not submission-ready citations. All eight initially unclear cases now have AI full-text recommendations; their historical triage labels are preserved. [Deferred work](literature/screening/deferred_review_tasks.md) remains tracked while accessible-paper assessments continue.

The original umbrella topic remains **Physics-Informed Deep Learning for Robust Image Reconstruction Under Forward-Model Mismatch**.

The [research topic and review reference](docs/research_topic_and_review_reference.md), also available as an [editable Word document](docs/research_topic_and_review_reference.docx), explains the retained topic, focused experimental question, evidence limits and recommended scoping-review workflow. The scoping designation is a recommendation pending a dated protocol amendment; protocol v0.4 and screening decisions remain unchanged.

## Current research decision

The supplied **Lee and Jang full paper (P035)** has now been read in full, including all five figures. The [paper assessment and next-step recommendation](docs/jang_paper_assessment_2026-09-17.md) identifies direct overlap with learned residual correction, distinguishes its empirical failure boundary from deployable reliability, and records an Equation 11/Figure 5b clarification. Retain the broad topic; first compare acquisition-aware reconstruction, then test whether observable sensitivity improves selective detail retention beyond strong controls. This closes the paper-access gap. The formal screening register/counts above remain the prior dated checkpoint; no eligibility or novelty decision is silently inferred from this methodological note.

The [experimental/scoping decision note](docs/research_routes_decision_2026-09-17.md) keeps the scoping-review route open independently of this candidate method. A rigorous evidence map can remain useful if an experimental mechanism fails or is already known; its added value over prior reviews and its formal methodology still need to be established. The current systematic-review protocol has not been silently renamed or amended.

The [dataset and baseline audit](docs/dataset_and_baseline_audit_01.md) identifies DPIR's reported training overlap with DIV2K and the face/dog domains of the released blind diffusion checkpoints. The [new preparation workflow](experiments/selective_reconstruction/README.md) records source identities and controlled float measurements. Final evaluation data remain to be selected after checkpoint overlap checks; these development images are not held-out evidence.

The [provisional gap synthesis](literature/synthesis/provisional_gap_synthesis_01.md) recommends a bounded first experiment: test whether operator-sensitive information improves the fidelity of selectively retained image detail beyond image-only uncertainty and residual scores, especially when an acquisition stage is absent from the assumed model. The [pilot specification](docs/selective_reconstruction_pilot_spec.md) defines the information budget, source-separated splits, comparison conditions, error target, compute controls and stop criteria. It is a design brief, not a completed experiment or registered guarantee.

The [generated evidence inventory](literature/synthesis/evidence_inventory_01.md) and [source snapshot](literature/synthesis/evidence_snapshot_01.json) preserve missing feature extractions and source/version limits. They do not count unverified seed codes as findings. Their P035 pending-access entry is historical: the supplied paper is now covered by the methodological assessment above, with formal register integration still outstanding. No additional screening stage or seed quota is introduced.

## Candidate research gap

The broad claim that physics-informed learning can improve reconstruction under an imperfect operator is already occupied. AverNet and PRISM supply assessed comparators for restoration and blind inference. VDPS now provides full-text evidence for joint video/physical-parameter estimation under time-varying acquisition. FaverNet supplies a further compound-video comparator and explicitly builds on AverNet. These findings do not establish calibrated operator uncertainty or selective release. The new P035 assessment confirms overlap with residual correction and identifies an empirical, truth-dependent boundary rather than a calibrated patch-selection rule. Earlier full-text checkpoints also identify posterior-mismatch theory, certificate-based fallback and self-supervised conformal calibration (P048/P042/P066). Our narrower candidate question is:

> Can accounting for uncertainty in an estimated forward operator improve the reliability of selectively released image detail when the true acquisition process leaves the assumed model family?

Novelty is unestablished. This requires a specific contribution against the nearest methods, not a checklist of combined features. See the linked screening report for primary sources, demonstrated overlaps and a bounded feasibility comparison.

## Repository structure

```text
docs/
  rapid_gap_map_2020_2026.md
  systematic_review_protocol.md
  research_decisions.md
  roadmap.md
  selective_reconstruction_pilot_spec.md
literature/
  evidence_matrix_2020_2026.xlsx
  synthesis/
experiments/
  phase0_canary/
    pilot.py
    README.md
    CANARY_RESULT.md
    outputs/canary/
data/
  README.md
results/
```

## Run the Phase-0 canary

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python experiments/phase0_canary/pilot.py \
  --output-dir experiments/phase0_canary/outputs/canary
```

To use a directory of clean images:

```bash
python experiments/phase0_canary/pilot.py \
  --input-dir /path/to/images \
  --output-dir results/natural_images
```

## Immediate research gate

Feasibility work can proceed while the deferred review tasks are completed. Before a custom journal architecture and definitive claims:

1. register and execute the review protocol;
2. full-text verify the nearest competitors;
3. run the frozen mismatch ladder on at least 100 held-out natural images;
4. compare classical, operator-oblivious, operator-conditioned and blind-generative baselines;
5. calibrate reliability scores on validation data only;
6. evaluate risk–coverage, unsupported-detail detection and cross-device transfer.

Reproduce the checkpoint-11 synthesis inventory with `python scripts/build_synthesis_snapshot.py --check`. The descriptive counts cover extracted evidence in the 88 include-recommended records; they are not field-wide prevalence or independent-study estimates.

## Research integrity

A visually plausible reconstruction is not proof that lost information has been recovered. Surveillance experiments must separate observation-supported detail from prior-generated content and must not make forensic identity claims from irrecoverable measurements.

## Citation

Citation metadata are provided in `CITATION.cff`. Update the repository URL and release identifier after publishing the remote repository.
