# Publication-lineage verification

Audit date: 2026-09-16 (historical checkpoint, before pilot 03)

**Later evidence:** pilot 03 found an explicit [coauthor announcement of ICML 2026 acceptance for P052](https://iwuqing.github.io/). Final proceedings metadata remain pending. The P052 conclusions below and the accompanying CSV describe the earlier audit, not the latest acceptance evidence. See [pilot_03_report.md](../screening/pilot_03_report.md) for current metadata corrections and the P026/P053 lineage question.

## Purpose

This audit determines which bibliographic version should represent each study in the PRISMA workflow. A preprint and its later journal or conference article are one study, not two included studies. Earlier versions remain linked for provenance, but only the most authoritative verified version is counted.

## Outcome

| Decision | Records | Study IDs |
|---|---:|---|
| Peer-reviewed version verified | 7 | P024, P038, P051, P063, P064, P065, P073 |
| Conference lineage located; final publisher metadata pending | 1 | P034 |
| Preprint only / no later peer-reviewed version located | 6 | P014, P033, P036, P037, P041, P042 |
| Venue claim not verified; treat as preprint | 1 | P052 |
| OpenReview submission present; acceptance not verified | 1 | P067 |
| **Total audited** | **16** | |

## Consequence for study counts

- The audit does **not** remove any of the 16 candidate studies.
- It prevents double-counting when an arXiv version and a publisher version refer to the same work.
- Seven records should be cited and counted through their verified journal or conference versions.
- P034 remains a single study with provisional conference lineage until its final publisher record is confirmed.
- P052 must not presently be labelled or counted as an ICML conference paper.
- P067 must not presently be labelled as an accepted peer-reviewed paper solely because an OpenReview page exists.
- The seed library remains **90 candidate records**, not 90 formally included PRISMA studies. Formal inclusion follows deduplication, title/abstract screening, full-text eligibility assessment, and exclusion logging.

## Canonical representation rules

1. Prefer the version of record: journal article first, otherwise proceedings paper, otherwise preprint.
2. Keep earlier preprints as lineage links; do not create a second study row for them.
3. Do not infer peer review from arXiv, a project website, an author CV, or an OpenReview submission alone.
4. Mark unresolved venue claims explicitly and revisit them before locking the included-study count.
5. Preserve every decision and source in `publication_lineage_verification.csv` for reproducibility.

## Verified version-of-record decisions

| Study ID | Canonical version |
|---|---|
| P024 | IEEE Transactions on Image Processing (2026) |
| P038 | IEEE ICASSP 2026 |
| P051 | IEEE Transactions on Computational Imaging (2026) |
| P063 | ECCV 2024, Springer LNCS 15118 |
| P064 | IEEE Transactions on Computational Imaging, vol. 10 (2024) |
| P065 | IEEE Transactions on Computational Imaging (2025) |
| P073 | ECCV 2024, Springer LNCS |

The record-level source links and notes are in the accompanying CSV.
