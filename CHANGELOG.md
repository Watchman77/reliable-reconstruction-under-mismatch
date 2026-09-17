# Changelog

## 0.24.2 — 2026-09-17

- Verified the user's results ZIP: all 23 files in the completed eight-observation Learned 02 run match manifest sizes and SHA-256 hashes. The six CSVs are byte-identical to the previously reviewed exports; all four raw figures were inspected.
- Rehashed all four source images and independently recomputed errors from all eight stored nominal predictions, 24 quality rows and all 448 risk rows. Patch errors and inexpensive scores agree exactly; CSV differences are below 1.2e-16. Saved a reproducible readback script, audit, per-observation table, run metadata and a JPEG readback montage.
- Kept the older incomplete Learned 02 run separate: status records 4/8 observations and its compute.csv does not match its manifest. Verified 11/11, 11/11 and 14/14 files in the three earlier pilot folders without claiming a new full scientific review of those runs.
- Closed the completed-run raw-export verification gap while preserving the historical review/audit. Learned inference, unsaved oracle/denoising outputs and ensemble-spread construction were not independently rerun. Mixed reconstruction findings, novelty/calibration limits and the proposed JPEG-chain diagnosis remain unchanged.

## 0.24.1 — 2026-09-17

- Reviewed the user's completed Learned 02 Colab notebook: all 19 cell sources match the issued artifact; nine code cells have consecutive counts with no saved errors. CUDA/L4 evidence, eight observations, 40 quality rows, 448 risk rows and 392 experiment denoiser calls are recorded.
- Retrieved six Drive CSVs, reproduced all three embedded tables, checked source identity and the classical anchor, and inspected four embedded figures. Recorded inherited local validation/timing metadata as historical rather than treating it as the new Colab run's status.
- Preserved mixed scientific findings: nominal DPIR gains 0.494 dB over the classical comparator for linear blur/noise but loses 0.412 dB with the JPEG chain; its JPEG-chain detail MSE is 35.237% higher. Positive pooled operator-selection comparisons coexist with per-source losses, bad-detail-rate reversals and a stronger secondary RGB operator score in some JPEG comparisons.
- Saved the dated review, six CSV exports, four embedded figures, derived comparisons and reproducible review script. Raw manifest download returned HTTP 403; full separate PNG/JSON/NPZ hash verification remains pending. No full-export verification, calibration, independent-test or novelty claim is made.
- Recommended a bounded JPEG-chain failure diagnosis while retaining the classical baseline and frozen checkpoint. Original experiments, review protocol and screening decisions remain unchanged.

## 0.24.0 — 2026-09-17

- Added a self-contained learned-baseline notebook using verified official colour DRUNet weights in a declared DPIR-style adapter. Pinned upstream files and MIT licence, recorded observed checkpoint digest and training-overlap limits, and froze settings before examining learned outcomes.
- Executed one full-resolution development observation (0801, linear blur/noise) with all comparison variants and 49 experiment denoiser calls. Nominal DPIR gains 0.627 dB over the inherited classical inverse; operator detail spread gives positive comparisons against the included fixed-operator transformation/residual/gradient controls. The two larger error tolerances are uninformative in this case. No independent-test, calibration or novelty claim follows.
- Verified the dense HQS solution, official schedule, transformations, strict checkpoint load, source identity, original classical anchor, prediction/patch-error readback and all 16 exported file hashes. Inspected four figures. Recorded the separate replay of two presentation cells after final notebook readback lacked those displays; numerical inference was preserved.
- Prepared the default four-source, two-condition Colab experiment. Its remaining seven observations and Colab/GPU behaviour are not claimed as executed. Preserved the prior notebooks, literature corpus and review protocol.

## 0.23.1 — 2026-09-17

- Reviewed the user's uploaded Baseline 01 Colab notebook: eleven consecutive execution counts, no saved error outputs, unchanged computational cells, passing numerical checks and a mounted Drive destination.
- Reconciled all three embedded tables with the seven previously retrieved Drive CSVs and inspected all four embedded figures. Confirmed the positive gradient-baseline development results while retaining the negative ridge comparisons and novelty limits.
- Documented the non-fatal pandas FutureWarning and stale metadata inherited from the local execution. Preserved the uploaded notebook and original local-run records; added a source-hashed review instead of rewriting execution history.
- Closed the saved-notebook Colab inspection gap. Did not claim live runtime control or verification of all separately exported PNG/JSON bytes and hashes. Review protocol and screening decisions remain unchanged.

## 0.23.0 — 2026-09-17

- Added and executed Baseline 01 on the same four development sources: three blur widths, two noise levels, linear/JPEG-chain conditions, two classical regularisers and source-excluded strength selection. Preserved input, smoothing and oracle-blur controls.
- Gradient regularisation improves pooled PSNR over input by 1.141 dB and 0.615 dB in the nominal-operator branch. Ridge remains weaker on average. The original fixed-ridge anchor reproduces Pilot 00's four pooled inverse PSNR values.
- Saved full tables, four inspected figures and fourteen output hashes. Added patch selection with residual, image-gradient and fixed-amplitude noise-spread controls, plus a reference-defined texture diagnostic. Recorded positive development comparisons without novelty, significance, calibration or independent-test claims.
- Preserved executed notebook outputs using a documented sequential IPython fallback after kernel socket operations were denied. Native Colab execution and Drive mounting remain unverified in this turn.
- Recorded separate experimental and scoping-review decisions. Prior-review overlap, a dated scoping protocol amendment, formal searches and human screening remain outstanding; no review decisions or protocol wording were changed.

## 0.22.0 — 2026-09-17

- Reviewed the user's saved four-source Colab execution: fifteen code cells report success, the numerical/data checks pass, and 24 reconstruction-metric rows are reported.
- Preserved code and saved text outputs in a repository notebook, with account identifiers omitted from execution metadata and a source hash recorded in the review.
- Recorded the actual negative baseline and control comparisons without claiming novelty, independent evaluation, or visual verification of inaccessible embedded figures.
- Added a final Drive export cell to preserve eleven result files with copy hashes in a dated folder. Local copy behaviour was verified; user execution in Colab and raw-result retrieval remain pending.
- Kept the 90-record review corpus, protocol, historical experiments and independent-evaluation requirements unchanged.

## 0.21.0 — 2026-09-17

- Prioritised experimental feasibility as requested; retained the original topic and all review decisions.
- Audited official dataset and baseline sources, pinned DPIR/NAFNet/GibbsDDRM/BlindDPS code snapshots, and recorded unresolved checkpoint, licence, domain and compute questions.
- Identified DPIR's reported 900-image DIV2K training overlap; acquired 100 DIV2K sources strictly for development, with archive/source/crop hashes and reproducible preparation scripts.
- Generated 24 paired float observations from 12 sources, explicitly declaring circular blur, noise, clipping, quantization and JPEG. Verified deterministic regeneration and forward-operator consistency.
- Added an executable engineering verifier. No learned reconstruction, calibration, held-out evaluation or novelty result is claimed; raw data and observation arrays are not committed.

## 0.20.0 — 2026-09-16

- Added a five-page editable research reference and Markdown source, retaining the original umbrella topic and specifying the narrower experimental working title and research question.
- Mapped the original objectives to the draft pilot and explained the closest-method overlaps, unresolved P035 and conditions for progressing or rejecting the candidate.
- Documented the recommended scoping-review workflow, human-review and software roles, with linked methodological and research sources.
- Preserved protocol v0.4, the workbook, full-text registers and all evidence counts. The document is a reference note, not a completed review, protocol amendment or novelty claim.

## 0.19.0 — 2026-09-16

- Completed a provisional narrative synthesis of the 88 AI include recommendations, with the excluded ancillary record and pending P035 kept separate.
- Added a reproducible 90-record inventory and JSON snapshot with per-feature provenance, input hashes, missing-extraction counts and explicit lineage/scope caveats. No screening or workbook decisions changed.
- Compared the closest mismatch, blind-sampling, calibration, support-assessment and temporal-restoration methods; ranked three candidate questions without asserting novelty.
- Specified a practical selective-reconstruction pilot, including information and compute matching, source-separated calibration/test splits, omitted-process stress tests and empirical risk–coverage evaluation. No new experiment was run.
- Recorded the user-sent author-copy request and moved the roadmap to synthesis/feasibility. Marked the rapid-map and canary feature-checklist rationale as historical.

## 0.18.0 — 2026-09-16

- Assessed four uploaded complete manuscripts: P030, P040, P049 and P053. Cumulative: 89 AI full-text assessments, 88 include recommendations, 1 exclude, 1 pending (P035).
- Recorded file identity, version, reading extent and SHA-256 provenance without redistributing paper PDFs.
- Distinguished image posterior sampling and variance maps from probability calibration, physical parameter estimates from operator posteriors, and intra-image attitude changes from video-frame variation.
- Confirmed the explicit AverNet–FaverNet predecessor relationship; kept both stable records and left study-level grouping for adjudication.
- Updated matrix, tracker, references and current-status documents. Preserved historical triage, formal decisions and protocol v0.4. Novelty remains unestablished.

## 0.17.0 — 2026-09-16

- Resolved P029 using complete publisher-supplied online text. Cumulative: 85 AI full-text assessments, 84 include recommendations, 1 exclude, 5 pending.
- Recorded structured mismatch-nuisance estimation and limited display-to-object transfer, without inferring calibrated operator uncertainty or selective release.
- Checked alternate primary/author locations and uploaded-file searches for all six previously pending records; documented the five remaining access gaps.
- Updated matrix, tracker, references and status documents. Preserved historical triage, formal decisions, acquisition flags and protocol v0.4. Novelty remains unestablished.

## 0.16.0 — 2026-09-16

- Attempted retrieval for all ten remaining seeds; completed four additional AI full-text assessments. Cumulative: 84 assessed, 83 include recommendations, 1 exclude, 6 pending.
- Documented access barriers, primary routes and next actions for all six pending papers without inferring decisions from abstracts, previews or code.
- Distinguished AutoDIR's categorical probabilities and clean-class stopping from physical-operator uncertainty and risk-controlled release.
- Recorded four acquired PDF versions and hashes; paper content is not redistributed.
- Updated the matrix, tracker, reference exports and current-status documents. Preserved historic triage, formal decisions, native workbook objects and protocol v0.4. Novelty remains unestablished.

## 0.15.0 — 2026-09-16

- Added ten AI full-text eligibility assessments. Cumulative: 80 assessed, 79 include recommendations, 1 exclude, 10 pending.
- Corrected UA-FP's provisional uncertainty/calibration codes using the full methods; distinguished latent/categorical degradation inference from physical-parameter uncertainty.
- Recorded operator-family training, blind-estimation failures, real-video transfer and propagation-versus-output rejection as comparison boundaries. Novelty remains unestablished.
- Retrieved nine PDFs and a public full-article XML source; recorded versions and hashes without redistributing paper content.
- Restored P068's full official proceedings title across the matrix, tracker and reference exports.
- Synchronized counts and deferred work while preserving 90 seed IDs, prior decisions, native workbook objects and protocol v0.4. Human decisions and formal searches remain pending.

## 0.14.0 — 2026-09-16

- Added ten AI full-text eligibility assessments. Cumulative: 70 assessed, 69 include recommendations, 1 exclude, 20 pending.
- Resolved the last initially unclear record (P016); all eight now have AI full-text recommendations, with historical triage preserved.
- Distinguished residual compensation, joint point estimation, approximate image posterior sampling, null-space theory and fidelity control. Novelty remains unestablished.
- Retrieved seven PDFs for assessment and recorded source hashes; no paper PDFs are redistributed. Other assessed sources were inspected online.
- Verified P069's 2020 journal lineage using publisher-deposited metadata while retaining the inspected 2019 precursor's version boundary.
- Synchronized the matrix, tracker and four reference exports; preserved all 90 seed IDs, prior decisions, workbook objects and protocol v0.4. User tasks remain deferred.

## 0.13.0 — 2026-09-16

- Added seven AI full-text eligibility assessments. Cumulative: 60 assessed, 59 include recommendations, 1 exclude, 30 pending.
- Recorded instability/semantic-fidelity tests, temporal compound restoration and rollback comparators, with source versions and criterion-level evidence.
- Preserved the original topic and candidate question; novelty remains unestablished. Distinguished rollback, prompt selection and training-data filtering from calibrated selective reconstruction.
- Recorded unresolved retrievals and 2020 journal lineages for inspected older NETT/instability preprints.
- Synchronized matrix, tracker and four reference exports; retained all 90 IDs, earlier decisions, workbook objects and protocol v0.4. User tasks remain deferred.

## 0.12.0 — 2026-09-16

- Added nine AI full-text eligibility assessments, all include recommendations. Cumulative: 53 assessed, 52 include, 1 exclude, 37 pending.
- Recorded source versions, reading extent and criterion-level evidence for prompted/compound restoration and conditional diffusion methods. Updated only explicitly verified feature fields.
- Distinguished degradation embeddings, physical point estimates, operator uncertainty, image sampling and calibrated reliability. Novelty remains unestablished.
- Explicitly corrected checkpoint 04’s P017 retrieval locator without altering its pending status or historical log. Recorded alternate-source resolutions and new failed routes.
- Synchronized the matrix, tracker and four reference exports; preserved workbook objects, all seed IDs, earlier decisions, protocol v0.4 and the date window. User tasks remain deferred.

## 0.11.0 — 2026-09-16

- Added eight AI full-text eligibility assessments, all include recommendations. Cumulative: 44 assessed, 43 include, 1 exclude, 46 pending.
- Recorded exact source versions, reading extent, criterion-level evidence and selected feature corrections for lensless mismatch, hallucination maps, calibrated intervals, diffusion inversion and compound video restoration.
- Distinguished sampled images from calibrated uncertainty, physical-operator inference from feature correction, and real-video quality from reference-verified detail. Novelty remains unestablished.
- Logged four unresolved retrieval cases and two alternate-source resolutions; pending user work remains deferred.
- Synchronized the matrix, screening log and four reference exports, with native workbook objects and earlier decisions preserved. Protocol v0.4 and the date window are unchanged.

## 0.10.0 — 2026-09-16

- Added 12 AI full-text eligibility assessments, all include recommendations. Cumulative: 36 assessed, 35 include, 1 exclude, 54 pending.
- Recorded criterion-level evidence, inspected versions and feature corrections for posterior sampling, operator point estimation, image coverage and nonlinear/compound restoration.
- Preserved version and method assumptions instead of equating uncertainty maps, physical calibration and calibrated coverage. Novelty remains unestablished.
- Logged two unresolved access attempts and three successful alternate-source resolutions. Deferred user-side work remains listed without blocking accessible assessments.
- Synchronized the matrix, tracker and reference exports; preserved prior decisions, stable IDs, historical triage, formal counters and native workbook objects.
- Eligibility criteria, search window and protocol v0.4 are unchanged.

## 0.9.0 — 2026-09-16

- Added 12 AI full-text eligibility assessments, all include recommendations. Cumulative: 24 assessed, 23 include, 1 exclude, 66 pending; human adjudication remains outstanding.
- Recorded inspected versions, criterion-level evidence and selected feature corrections for operator estimation, distribution shift, compound restoration and uncertainty calibration.
- Logged six unresolved retrieval attempts and two publication-lineage checks without excluding or merging records on incomplete evidence.
- Flagged version-specific numerical/guarantee questions for reconciliation before quantitative synthesis. Novelty remains unestablished.
- Synchronized the matrix, tracker and reference exports; preserved historical triage, formal decisions, formulas, native tables, chart and validation rules.
- Eligibility criteria, search window and protocol v0.4 are unchanged.

## 0.8.0 — 2026-09-16

- Completed 12 AI full-text eligibility assessments: 11 include recommendations, 1 exclude, 78 pending. All remain subject to human adjudication.
- Resolved seven initially unclear cases; recorded P016 retrieval failure without excluding it. CQAD remains an ancillary dataset reference and a retained seed record.
- Added criterion-level evidence, inspected versions/read extent and source-backed feature corrections. Distinguished acquisition, noise and prior errors, variance, coverage and selection.
- Added a formula-driven full-text counter to the existing workbook; synchronized reference exports and preserved initial triage, formal decisions and native workbook objects.
- Protocol v0.4 documents the AI full-text convention; eligibility criteria, date window and search methods are unchanged.

## 0.7.0 — 2026-09-16

- Completed initial triage for P041–P090: 44 advance and 6 unclear recommendations; cumulative 90/90, 82 advance, 8 unclear, zero untriaged.
- Revisited five older access/scope records; preserved incomplete evidence rather than treating retrieval failure as exclusion.
- Added record-level sources and full-text questions for all remaining seeds, a complete decision register and explicit full-text work remaining.
- Inspected No-Harm discussion/limitations and documented existing posterior-mismatch theory and self-supervised calibration. Original umbrella title retained; novelty remains unestablished.
- Corrected LADiBI workshop venue, DA-CLIP title and StableSR DOI; updated CaMB-Diff acceptance evidence and flagged AverNet/FaverNet lineage for comparison.
- Synchronized the workbook and four reference exports. Preserved all native workbook objects, unrelated feature codes and zero formal eligibility counts.

## 0.6.0 — 2026-09-16

- Triaged P021–P040 with 20 preliminary advance recommendations; cumulative progress is 40/90 (38 advance, 2 unclear, 50 untriaged), with human adjudication and formal eligibility pending.
- Revisited P006/P016 without resolving their scope/access uncertainty. Recorded P032's incomplete evidence without interpreting it as exclusion.
- Inspected targeted technical sections of AverNet, hallucination assessment and PRISM; documented existing compound/time-varying degradation and dual-uncertainty evaluations.
- Replaced the feature-checklist novelty gate with a precise candidate reliability question and nearest-method comparison requirements. No novelty or complete full-text review is claimed.
- Corrected or completed eight reference records, including three erroneous source locators, one incorrect author attribution and the LatentDEM journal lineage.
- Synchronized the existing workbook and four reference exports, retained native workbook objects and all unrelated feature codes, and recorded field-level changes.

## 0.5.0 — 2026-09-16

- Triaged P001–P020 as an explicitly AI-assisted convenience pilot: 18 advance recommendations, 2 unclear, no final inclusions or exclusions.
- Recorded evidence sources, retrieval limitations, scope rationale and full-text questions for every pilot record; all require human adjudication.
- Corrected Nan/Ji authorship, RealBlur's ECCV venue, the Deep Probabilistic Imaging link/title, the PromptIR proceedings link/title, and abbreviated DDNM/GibbsDDRM titles across the workbook and reference exports.
- Replaced ambiguous seed-map `Include` labels with `Pending formal eligibility`; preserved a field-level change audit and kept all formal counters at zero.
- Added formula-driven pilot counts; retained the existing sheets, tables, chart and unrelated extraction codes.
- Reconciled the inconsistent workbook protocol `1.1` label with a dated protocol v0.3 amendment; aligned its search-query summary with the authoritative protocol. No eligibility or search-window change, and no registration claimed.

## 0.4.0 — 2026-09-16

- Transferred all 90 seed papers into the PRISMA screening log.
- Labelled seed records separately from formally screened and included studies.
- Reset formal PRISMA counters to zero pending reproducible database searches.
- Labelled the workbook protocol summary as version 1.1; this was inconsistent with the v0.2 protocol document and is corrected in 0.5.0.

## 0.3.0 — 2026-09-16

- Expanded the seed evidence matrix from 70 to 90 studies.
- Added universal restoration, compound-restoration agents, diffusion inverse solvers and generative real-world SR competitors.
- Created the initial version-controlled research repository.
- Added research decisions, roadmap, data policy and contribution rules.
- Preserved the Phase-0 canary and validated outputs.

## 0.2.0 — 2026-09-15

- Expanded the initial evidence matrix to 70 studies.
- Added the systematic-review protocol and screening tracker.
- Executed the Phase-0 compound-mismatch canary.
