# Literature Workspace

`evidence_matrix_2020_2026.xlsx` contains:

- a 90-study seed evidence matrix;
- summary counts and the candidate question (novelty unestablished);
- a screening tracker for formal database exports;
- the review protocol summary;
- a controlled coding dictionary.

The matrix is a living extraction file. Preserve stable study identifiers. Link preprint, conference and journal reports as one study lineage rather than counting them as independent evidence.

Do not convert `Partial` to `Yes` without full-text evidence. Do not classify a paper as calibrated merely because it displays sample variance or uncertainty maps; calibration requires empirical coverage, calibration error or an equivalent validated reliability criterion.

## Historical provisional synthesis — 16 September 2026

The [gap synthesis](synthesis/provisional_gap_synthesis_01.md) compares the main competing approaches, ranks three candidate problems and recommends an operator-sensitive selective-reconstruction pilot. The [inventory](synthesis/evidence_inventory_01.md) indexes all 90 seed records; the [JSON snapshot](synthesis/evidence_snapshot_01.json) records input hashes and feature-level provenance. Main synthesis counts use only the 88 AI include recommendations. Missing feature extractions remain missing; P060 is ancillary and P035 has no full-text contribution.

This is a provisional narrative synthesis, not a new screening stage, formal inclusion decision or meta-analysis. Study lineage and version limitations remain explicit. No new experimental result or proven novelty is asserted. The historical snapshot remains pinned to checkpoint 11. The current workbook and references advance to checkpoint 12; see the [P035 addendum](synthesis/p035_novelty_addendum_2026-09-17.md).

## Current full-text checkpoint — 17 September 2026

All 90 seed records have AI full-text assessments: 89 include recommendations, one exclude (P060), zero awaiting full text. P035 was assessed from the complete user-supplied SPIE article in checkpoint 12. See [the report](screening/full_text_12_report.md), [criterion-level register](screening/full_text_12.json), [change audit](screening/full_text_12_changes.json) and [deferred work](screening/deferred_review_tasks.md).

Summary E15 and Screening Log J reflect the completed AI reading pass. Matrix AA remains pending formal eligibility. Only explicitly recorded feature fields are verified. P035's correction mechanism and empirical reliability threshold constrain the novelty claim; its threshold is not probability calibration. The original paper is not redistributed. Historical checkpoints preserve their dated findings and access obstacles.

## Historical initial-triage checkpoint — 16 September 2026

All 90 records have preliminary AI recommendations in the Screening Log: 82 advance and 8 unclear. `AI pilot: advance` means retrieve and assess the full text, not include the study. `AI pilot: unclear` means resolve scope or retrieval before deciding. At that initial checkpoint, all 90 required human adjudication and complete full-text eligibility; zero remain untriaged by this pilot. Formal PRISMA counts remain zero.

The Evidence Matrix's legacy `Include` labels meant membership in the seed map. They have been replaced by `Pending formal eligibility` for all 90 records; this is a clarification, not 90 reversals of completed inclusion decisions. The prior values are recoverable in git and in the pilot change audit. Feature codes were unchanged by the initial pilot; checkpoint 01 now verifies the explicit subset recorded in its register.

`screening/pilot_01.json` is the record-level evidence and recommendation log; `screening/pilot_01_report.md` explains limitations and next questions; `screening/pilot_01_changes.json` records field-level metadata/status edits. No paper PDFs are redistributed here. Follow the primary or author-hosted source links for access.

The matching `pilot_02` files cover P021–P040, two unresolved revisits and targeted full-text findings. At that historical checkpoint, P032's uncertainty/calibration codes were provisional and its eligibility was pending. Checkpoint 08 now supplies a full-text eligibility recommendation and corrects P/Q/R to No: the inspected method estimates system parameters without demonstrating uncertainty distributions or probability calibration. Its PDF-acquisition field is not upgraded for XML access. Other unverified feature ratings remain provisional.

The historical `screening/pilot_03` files complete P041–P090 and revisit five older records. The report lists all eight unresolved recommendations and incomplete-source advances. Use `full_text_01` through `full_text_12` for cumulative decisions and `full_text_12_report.md` for current status; `pilot_01`, `pilot_02` and the earlier lineage audit preserve their historical results. Current metadata corrections include the LADiBI workshop venue, DA-CLIP title alias, StableSR DOI and P068’s full proceedings title.
