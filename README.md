# Reliable Reconstruction Under Forward-Model Mismatch

Research repository for a journal-first programme on evidence-calibrated image reconstruction under compound, unknown and time-varying acquisition mismatch.

## Current status

- 90-study seed evidence matrix covering 1 January 2020 to 15 September 2026.
- Systematic-review protocol v0.2 frozen as a working draft.
- Rapid adversarial gap map completed.
- Phase-0 classical canary implemented and executed.
- Formal database screening and the 100-image pilot remain outstanding.

The 90 studies are a seed evidence map, not a completed PRISMA corpus. The repository must not be cited as a systematic review until database searches, deduplication, two-stage screening, exclusion logging, full-text verification and citation chaining are complete.

## Candidate research gap

The broad claim that physics-informed learning can improve reconstruction under an imperfect operator is already occupied. The surviving candidate problem is narrower:

> Recover images under a compound and potentially time-varying surveillance acquisition chain; infer the degradation state; calibrate uncertainty for both image and degradation; distinguish measurement-supported from prior-generated detail; and mask or abstain when recovery is unreliable under unseen cameras, codecs and scenes.

Novelty is provisional until the formal review and larger pilot are complete.

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
