# Roadmap

## Current checkpoint — 24 September 2026

Completed: initial triage and all 90 AI full-text assessments (89 include recommendations, one exclude), a provisional synthesis, classical and learned baselines, acquisition-chain diagnosis, the audited JPEG-aware experiment, the Stage 05 protocol/data audit, the CUDA canary, and all 12 development reconstruction shards. Human review adjudication and formal database-search accounting remain outstanding.

Latest: the returned 05C2 CUDA run passed independent readback. The outcome-blind readiness audit subsequently passed all 11 frozen requirements, and the exact Stage-05D runner is now authorized by a versioned transition. Five fixed sealed shards of eight TESTIMAGES sources are ready to run. The complete one-time Stage-05E analysis was also locked before any independent output existed. Test inference is authorized but not yet performed; performance remains unseen.

The user prioritised the experimental track. Development data are explicitly separated from the 40-source sealed TESTIMAGES cohort; documented checkpoint exposure, exact/near-duplicate checks, source partitions, metrics and statistical gates are frozen. Review work remains deferred apart from evidence directly relevant to the experimental decision.

| Track | Next concrete task | Deliverable / completion evidence |
|---|---|---|
| Feasibility — completed | Five frozen PatchErrorNet members and 11 source-equal-weighted isotonic mappings fitted on development partitions only. | 05C2 result ZIP and executed notebook passed independent readback; model receipts, mappings and diagnostics are hash-verified. |
| Feasibility — ready | Run fixed Stage-05D shard indices 0–4 without opening intermediate metrics. | Five sealed 56-observation ZIPs with exact manifests and locks. |
| Feasibility — evaluate | After all five shards verify, run the already locked Stage-05E analysis exactly once. | Source-level intervals, H1/H2 decisions, independent calibration report and bounded experimental novelty decision. |
| Evidence — completed AI assessment | Preserve P035 and all 90 criterion-level recommendations pending human adjudication. | Human decisions and formal review counts, separate from the experimental claim. |
| Evidence — deferred | Complete formal search accounting, human adjudication, necessary version checks and lineage grouping. | Auditable final review decisions and search records; no final novelty claim before sufficient evidence. |

See [provisional synthesis 01](../literature/synthesis/provisional_gap_synthesis_01.md) for the three ranked candidate problems and the explanation of what existing methods already cover. Candidate 1 is operator-sensitive selective reconstruction; constrained residual correction and temporal extension are later alternatives.

## Phase 1 — Formal evidence review

- Freeze and register the protocol.
- Execute database-specific searches.
- Preserve raw exports and exact search dates/counts.
- Deduplicate by DOI, normalized title and study lineage.
- Conduct title/abstract and full-text screening.
- Record exclusion reasons and PRISMA flow counts.
- Complete backward and forward citation chaining for nearest competitors.

## Phase 2 — Controlled feasibility benchmark

- Run at least 100 held-out natural images through a frozen degradation manifest.
- Separate blur-only, noise-only, codec-only and compound conditions.
- Add mismatch severity and wrong-operator-family tests.
- Compare Wiener/Tikhonov, operator-oblivious restoration, operator-conditioned reconstruction and blind generative reconstruction.
- Report reconstruction, operator and reliability metrics with confidence intervals.

## Phase 3 — Reliability layer

- Define image and degradation uncertainty outputs.
- Calibrate on validation data only.
- Implement observation-support or hallucination maps.
- Evaluate error detection and risk–coverage.
- Add mask/abstain decisions with preregistered operating points.

## Phase 4 — Real surveillance evaluation

- Construct or obtain ethically usable multi-device captures.
- Record camera, codec, bitrate, illumination and motion conditions where available.
- Test unseen-device, unseen-codec and unseen-composition shifts.
- Evaluate temporal stability and downstream task preservation without treating generated detail as ground truth.

## Phase 5 — Journal architecture

Design the proposed model only after Phases 1–3 satisfy the go/no-go criteria. Freeze baselines, splits, metrics and ablations before final training.
