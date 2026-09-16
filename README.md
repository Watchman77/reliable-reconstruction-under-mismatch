# Reliable Reconstruction Under Forward-Model Mismatch

Research repository for a journal-first programme on evidence-calibrated image reconstruction under compound, unknown and time-varying acquisition mismatch.

## Current status

- 90-record seed evidence matrix covering 1 January 2020 to 15 September 2026.
- Systematic-review protocol v0.3, a dated working draft that is not yet registered.
- Initial triage complete for all 90 seed records: 82 advance recommendations, 8 unclear, 0 untriaged. Every record still requires human adjudication and complete formal full-text eligibility assessment.
- Evidence basis is recorded per study. Selected close competitors received targeted technical inspection; incomplete retrieval is flagged explicitly.
- Zero formally included studies. Seed feature codes remain provisional, not full-text-verified extraction.
- Rapid adversarial gap map completed.
- Phase-0 classical canary implemented and executed.
- Formal database screening and the 100-image pilot remain outstanding.

The 90 studies are a seed evidence map, not a completed PRISMA corpus. The repository must not be cited as a systematic review until database searches, deduplication, two-stage screening, exclusion logging, full-text verification and citation chaining are complete.

See the [latest screening and novelty check](literature/screening/pilot_03_report.md) and [record-level evidence](literature/screening/pilot_03.json), alongside the preserved [first pilot](literature/screening/pilot_01_report.md). The matrix, screening log and reference exports are synchronized; bibliographic corrections are recorded in field-level audits. Reference exports remain draft metadata, not submission-ready citations. Eight unresolved recommendations and incomplete-source advances are listed in the latest report.

The original umbrella topic remains **Physics-Informed Deep Learning for Robust Image Reconstruction Under Forward-Model Mismatch**.

## Candidate research gap

The broad claim that physics-informed learning can improve reconstruction under an imperfect operator is already occupied. AverNet, PRISM and VDPS overlap compound/time-varying restoration, joint operator inference and uncertainty evaluation. The completed pass also identifies posterior-mismatch theory, certificate-based fallback and self-supervised conformal calibration (P048/P042/P066). Our narrower candidate question is:

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
