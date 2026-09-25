# Reliable Reconstruction Under Forward-Model Mismatch

Research repository for a journal-first programme on evidence-calibrated image reconstruction under compound, unknown and time-varying acquisition mismatch.

## Current status

- 90-record seed evidence matrix covering 1 January 2020 to 15 September 2026.
- Systematic-review protocol v0.4, a dated working draft that is not yet registered.
- Initial triage complete for all 90 seed records: 82 advance recommendations, 8 unclear, 0 untriaged. 90 AI full-text eligibility assessments are now complete: 89 include recommendations, 1 exclude; 0 remain. Human adjudication and final formal eligibility remain pending.
- Evidence basis is recorded per study. Inspected versions, reading extent and criterion-level decisions are recorded; incomplete retrieval is flagged explicitly.
- Zero formally included studies. Only the feature fields explicitly listed in the full-text register are verified; other seed codes remain provisional.
- Rapid adversarial gap map completed.
- Provisional synthesis 01 preserves its 88-include checkpoint; a P035 addendum now incorporates the final full text and sharpens the comparison. Current reading totals are 89 include recommendations and one exclude.
- Phase-0 classical canary implemented and executed.
- Formal database screening and the 100-image pilot remain outstanding.
- Stage 05 independent evaluation is complete. All five sealed shards passed manifest verification; the one-time Stage 05E analysis inspected 40 sources across seven chains; and Stage 05F completed the locked literature/experimental synthesis. H1 passed with a 90.13% detail-MSE reduction. H2 was statistically detectable at 4.46% but failed the predeclared 5% practical gate. Positive-event calibration was not estimable because the locked event had zero positives across 286,720 patch rows. The original unified novelty claim is not established; the supported pivot is an acquisition-chain and reliability-assessment contribution.
- Stage 06 novelty-strengthening is now underway. The executed [development-only threshold audit](notebooks/06A_Development_Event_Threshold_Sensitivity.ipynb) found that the locked 0.05 event had 22.16% prevalence and appeared in all 32 calibration sources; its later absence is therefore treated as an event-support/transport shift, not as permission to redefine Stage 05. The [Stage 06 protocol](docs/stage_06_novelty_strengthening_protocol.md) freezes seven strengthening axes before any new independent outcome is inspected.
- A separate [four-source Colab pilot](experiments/colab_pilot_00/README.md) now has saved successful execution checks. Its fixed inverses underperform the degraded-input baseline, and operator spread does not beat the best simple control at 50% retention. A Drive export cell has been added; raw results and figure review remain pending.

A stage-by-stage record of committed and externally retained artifacts is maintained in the [research artifact inventory](docs/artifact_inventory.md).

The 90 studies are a seed evidence map, not a completed PRISMA corpus. The repository must not be cited as a systematic review until database searches, deduplication, two-stage screening, exclusion logging, full-text verification and citation chaining are complete.

See the [latest full-text checkpoint](literature/screening/full_text_12_report.md) and [criterion-level evidence](literature/screening/full_text_12.json), alongside [checkpoint 01](literature/screening/full_text_01_report.md), [checkpoint 02](literature/screening/full_text_02_report.md), [checkpoint 03](literature/screening/full_text_03_report.md), [checkpoint 04](literature/screening/full_text_04_report.md), [checkpoint 05](literature/screening/full_text_05_report.md), [checkpoint 06](literature/screening/full_text_06_report.md), [checkpoint 07](literature/screening/full_text_07_report.md), [checkpoint 08](literature/screening/full_text_08_report.md), [checkpoint 09](literature/screening/full_text_09_report.md), [checkpoint 10](literature/screening/full_text_10_report.md) and the preserved [first pilot](literature/screening/pilot_01_report.md). The matrix, screening log and reference exports are synchronized; bibliographic corrections are recorded in field-level audits. Reference exports remain draft metadata, not submission-ready citations. All eight initially unclear cases now have AI full-text recommendations; their historical triage labels are preserved. [Deferred work](literature/screening/deferred_review_tasks.md) remains tracked while accessible-paper assessments continue.

The original umbrella topic remains **Physics-Informed Deep Learning for Robust Image Reconstruction Under Forward-Model Mismatch**.

The [research topic and review reference](docs/research_topic_and_review_reference.md), also available as an [editable Word document](docs/research_topic_and_review_reference.docx), explains the retained topic, focused experimental question, evidence limits and recommended scoping-review workflow. The scoping designation is a recommendation pending a dated protocol amendment; protocol v0.4 and screening decisions remain unchanged.

## Current research decision

## Stage 05 final result

The independent experimental programme is closed. The [final checkpoint](docs/stage_05_final_checkpoint.md) and [manuscript draft](manuscript/manuscript_draft.md) preserve the locked decision. JPEG-aware FBCNN preprocessing before nominal DPIR reduced primary-chain source detail MSE by **90.13%** and passed H1. Operator-spread selection reduced 50%-coverage retained-patch detail risk by **4.46%** relative to image-transform spread; its statistical requirement passed but the predeclared **5%** practical requirement did not. The locked calibration event had zero positives, so positive-event calibration could not be validated.

The defensible contribution is therefore a bounded acquisition-chain and reliability assessment. It is not a first-method, universally superior, fully calibrated, hallucination-free, or forensic-recovery claim.

The [dataset and baseline audit](docs/dataset_and_baseline_audit_01.md) identifies DPIR's reported training overlap with DIV2K and the face/dog domains of the released blind diffusion checkpoints. The [new preparation workflow](experiments/selective_reconstruction/README.md) records source identities and controlled float measurements. Final evaluation data remain to be selected after checkpoint overlap checks; these development images are not held-out evidence.

The [provisional gap synthesis](literature/synthesis/provisional_gap_synthesis_01.md) recommends a bounded first experiment: test whether operator-sensitive information improves the fidelity of selectively retained image detail beyond image-only uncertainty and residual scores, especially when an acquisition stage is absent from the assumed model. The [pilot specification](docs/selective_reconstruction_pilot_spec.md) defines the information budget, source-separated splits, comparison conditions, error target, compute controls and stop criteria. It is a design brief, not a completed experiment or registered guarantee.

The [generated evidence inventory](literature/synthesis/evidence_inventory_01.md) and [source snapshot](literature/synthesis/evidence_snapshot_01.json) preserve missing feature extractions and source/version limits. They do not count unverified seed codes as findings. P035 has been received and assessed in checkpoint 12. See the [current synthesis addendum](literature/synthesis/p035_novelty_addendum_2026-09-17.md); inventory 01 remains a dated checkpoint-11 snapshot. No additional screening stage or seed quota is introduced.

## Candidate research gap

The broad claim that physics-informed learning can improve reconstruction under an imperfect operator is already occupied. AverNet and PRISM supply assessed comparators for restoration and blind inference. VDPS now provides full-text evidence for joint video/physical-parameter estimation under time-varying acquisition. FaverNet supplies a further compound-video comparator and explicitly builds on AverNet. P035 now adds full-text evidence for residual correction, prescribed valid-region recovery and an empirical failure threshold. Its true-versus-perturbed model-error score does not establish calibrated region selection from unknown captures. Earlier full-text checkpoints also identify posterior-mismatch theory, certificate-based fallback and self-supervised conformal calibration (P048/P042/P066). Our narrower candidate question is:

> Can accounting for uncertainty in an estimated forward operator improve the reliability of selectively released image detail when the true acquisition process leaves the assumed model family?

The broad unified novelty claim was not established by the locked independent experiment. The supported contribution is the acquisition-chain-specific reconstruction result and the transparent reliability boundary documented in the [Stage 05 final checkpoint](docs/stage_05_final_checkpoint.md).

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

## Immediate manuscript gate

The independent experiment is complete. Before journal submission:

1. complete human review adjudication and formal search accounting without relabelling the current evidence map as a completed systematic review;
2. insert verified citations for the nearest competitors in the manuscript draft;
3. preserve the failed H2 practical gate and the zero-event calibration boundary;
4. select a target journal and adapt length, structure, figures and reference style;
5. complete co-author review, author-contribution, funding, conflict, licence and ethics statements.

Run `python scripts/validate_independent_05f.py /path/to/stage_05f.zip` to verify the final synthesis archive. Reproduce the checkpoint-11 synthesis inventory with `python scripts/build_synthesis_snapshot.py --check` when reviewing the earlier evidence snapshot.

## Research integrity

A visually plausible reconstruction is not proof that lost information has been recovered. Surveillance experiments must separate observation-supported detail from prior-generated content and must not make forensic identity claims from irrecoverable measurements.

## Citation

Citation metadata are provided in `CITATION.cff`. Update the repository URL and release identifier after publishing the remote repository.
