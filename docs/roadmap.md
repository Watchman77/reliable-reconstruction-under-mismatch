# Roadmap

## Current checkpoint — 17 September 2026

Completed: initial triage of 90 seeds; 89 AI full-text assessments (88 include recommendations, one exclude); a provisional synthesis and source-linked inventory. P035 remains pending after the user sent an author-copy request. The classical single-image canary has run; the multi-image reliability pilot has not.

The user prioritised the experimental track. The first static [dataset/baseline audit](dataset_and_baseline_audit_01.md) is complete: 100 development-only sources acquired, 24 controlled observations generated, no learned reconstruction or independent evaluation run. DPIR training overlap and diffusion-prior domains must be handled before freezing evaluation data. Review work remains deferred apart from evidence directly relevant to the experimental decision.

| Track | Next concrete task | Deliverable / completion evidence |
|---|---|---|
| Feasibility — active | Implement consistent classical and DPIR adapters; obtain/check weights and measure per-image inference cost using the initial audit. | Matched forward/adjoint implementation, checkpoint hashes, runtime and memory measurements. |
| Feasibility — next | Freeze source-separated development/calibration/test manifests and implement the declared acquisition regimes and selection scores. | Runnable multi-image pilot, source-level evaluation and a dated design freeze. |
| Feasibility — evaluate | Compare selective error at matched coverage, information and compute, including a shared omitted-process stress condition. | All-condition report with uncertainty intervals, failures and a go/redesign/stop decision. |
| Evidence — pending access | Assess P035 when the author or another legitimate route supplies full text. | One criterion-level recommendation, source/version evidence and an updated cumulative checkpoint. |
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
