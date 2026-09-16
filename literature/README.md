# Literature Workspace

`evidence_matrix_2020_2026.xlsx` contains:

- a 90-study seed evidence matrix;
- summary counts and the candidate question (novelty unestablished);
- a screening tracker for formal database exports;
- the review protocol summary;
- a controlled coding dictionary.

The matrix is a living extraction file. Preserve stable study identifiers. Link preprint, conference and journal reports as one study lineage rather than counting them as independent evidence.

Do not convert `Partial` to `Yes` without full-text evidence. Do not classify a paper as calibrated merely because it displays sample variance or uncertainty maps; calibration requires empirical coverage, calibration error or an equivalent validated reliability criterion.

## Current full-text checkpoint — 16 September 2026

Twelve AI full-text assessments are complete: 11 include recommendations and 1 exclude; 78 remain. See [the report](screening/full_text_01_report.md), [criterion-level register](screening/full_text_01.json) and [change audit](screening/full_text_01_changes.json). Summary E15 counts completed AI decisions. Screening Log J records those decisions; Matrix AA remains pending final formal eligibility. Only explicitly listed feature fields are verified.

## Historical initial-triage checkpoint — 16 September 2026

All 90 records have preliminary AI recommendations in the Screening Log: 82 advance and 8 unclear. `AI pilot: advance` means retrieve and assess the full text, not include the study. `AI pilot: unclear` means resolve scope or retrieval before deciding. At that initial checkpoint, all 90 required human adjudication and complete full-text eligibility; zero remain untriaged by this pilot. Formal PRISMA counts remain zero.

The Evidence Matrix's legacy `Include` labels meant membership in the seed map. They have been replaced by `Pending formal eligibility` for all 90 records; this is a clarification, not 90 reversals of completed inclusion decisions. The prior values are recoverable in git and in the pilot change audit. Feature codes were unchanged by the initial pilot; checkpoint 01 now verifies the explicit subset recorded in its register.

`screening/pilot_01.json` is the record-level evidence and recommendation log; `screening/pilot_01_report.md` explains limitations and next questions; `screening/pilot_01_changes.json` records field-level metadata/status edits. No paper PDFs are redistributed here. Follow the primary or author-hosted source links for access.

The matching `pilot_02` files cover P021–P040, two unresolved revisits and targeted full-text findings. P032's positive uncertainty/calibration codes and other unverified feature ratings must not be used as established capabilities. Partial technical inspection does not constitute complete full-text eligibility; the Screening Log's full-text decision remains pending. Its acquisition field continues to record local full-paper acquisition, not merely remote access to selected passages.

The historical `screening/pilot_03` files complete P041–P090 and revisit five older records. The report lists all eight unresolved recommendations and incomplete-source advances. Use `full_text_01` for current status; `pilot_01`, `pilot_02` and the earlier lineage audit preserve their historical results. Current metadata corrections include the LADiBI workshop venue, DA-CLIP title alias and StableSR DOI.
