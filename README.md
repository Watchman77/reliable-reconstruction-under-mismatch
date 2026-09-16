# Reliable Reconstruction Under Forward-Model Mismatch

Research repository for a journal-first programme on evidence-calibrated image reconstruction under compound, unknown and time-varying acquisition mismatch.

## Current status

- 90-record seed evidence matrix covering 1 January 2020 to 15 September 2026.
- Systematic-review protocol v0.4, a dated working draft that is not yet registered.
- Initial triage complete for all 90 seed records: 82 advance recommendations, 8 unclear, 0 untriaged. 85 AI full-text eligibility assessments are now complete: 84 include recommendations, 1 exclude; 5 remain. Human adjudication and final formal eligibility remain pending.
- Evidence basis is recorded per study. Inspected versions, reading extent and criterion-level decisions are recorded; incomplete retrieval is flagged explicitly.
- Zero formally included studies. Only the feature fields explicitly listed in the full-text register are verified; other seed codes remain provisional.
- Rapid adversarial gap map completed.
- Phase-0 classical canary implemented and executed.
- Formal database screening and the 100-image pilot remain outstanding.

The 90 studies are a seed evidence map, not a completed PRISMA corpus. The repository must not be cited as a systematic review until database searches, deduplication, two-stage screening, exclusion logging, full-text verification and citation chaining are complete.

See the [latest full-text checkpoint](literature/screening/full_text_10_report.md) and [criterion-level evidence](literature/screening/full_text_10.json), alongside [checkpoint 01](literature/screening/full_text_01_report.md), [checkpoint 02](literature/screening/full_text_02_report.md), [checkpoint 03](literature/screening/full_text_03_report.md), [checkpoint 04](literature/screening/full_text_04_report.md), [checkpoint 05](literature/screening/full_text_05_report.md), [checkpoint 06](literature/screening/full_text_06_report.md), [checkpoint 07](literature/screening/full_text_07_report.md), [checkpoint 08](literature/screening/full_text_08_report.md), [checkpoint 09](literature/screening/full_text_09_report.md) and the preserved [first pilot](literature/screening/pilot_01_report.md). The matrix, screening log and reference exports are synchronized; bibliographic corrections are recorded in field-level audits. Reference exports remain draft metadata, not submission-ready citations. All eight initially unclear cases now have AI full-text recommendations; their historical triage labels are preserved. [Deferred work](literature/screening/deferred_review_tasks.md) remains tracked while accessible-paper assessments continue.

The original umbrella topic remains **Physics-Informed Deep Learning for Robust Image Reconstruction Under Forward-Model Mismatch**.

## Candidate research gap

The broad claim that physics-informed learning can improve reconstruction under an imperfect operator is already occupied. AverNet and PRISM supply assessed comparators for restoration and blind inference. VDPS remains a potentially close comparator whose full-text eligibility is still pending; its earlier abstract-level coding must not be treated as verified capability. Earlier full-text checkpoints also identify posterior-mismatch theory, certificate-based fallback and self-supervised conformal calibration (P048/P042/P066). Our narrower candidate question is:

> Can accounting for uncertainty in an estimated forward operator improve the reliability of selectively released image detail when the true acquisition process leaves the assumed model family?

Novelty is unestablished. This requires a specific contribution against the nearest methods, not a checklist of combined features. See the linked screening report for primary sources, demonstrated overlaps and a bounded feasibility comparison.

## Repository structure

```text
docs/
  rapid_gap_map_2020_2026.md
  systematic_review_protocol.md
  research_decisions.md
  roadmap.md
literature/
  evidence_matrix_2020_2026.xlsx
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

Before designing a custom journal architecture:

1. register and execute the review protocol;
2. full-text verify the nearest competitors;
3. run the frozen mismatch ladder on at least 100 held-out natural images;
4. compare classical, operator-oblivious, operator-conditioned and blind-generative baselines;
5. calibrate reliability scores on validation data only;
6. evaluate risk–coverage, unsupported-detail detection and cross-device transfer.

## Research integrity

A visually plausible reconstruction is not proof that lost information has been recovered. Surveillance experiments must separate observation-supported detail from prior-generated content and must not make forensic identity claims from irrecoverable measurements.

## Citation

Citation metadata are provided in `CITATION.cff`. Update the repository URL and release identifier after publishing the remote repository.
