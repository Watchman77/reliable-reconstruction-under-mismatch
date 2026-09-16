# Research Decisions

## 16 September 2026 — Scope decision

**Decision:** retain 2020–2026 as the primary evidence window. Use older work only for conceptual and mathematical background.

**Reason:** this window captures the transition from learned regularisation and mismatch-aware unrolling to blind diffusion, operator inference, uncertainty calibration and reliability-aware reconstruction without turning the review into a history of inverse problems.

## 16 September 2026 — Corpus target

**Decision:** expand the seed map from 70 to 90 studies.

**Reason:** the additional 20 papers stress-test the candidate novelty using universal restoration, compound-restoration agents, operator-conditioned diffusion solvers and real-world generative super-resolution. Ninety is a planning target, not an eligibility quota.

## 16 September 2026 — PRISMA status boundary

**Decision:** treat all 90 coded papers as seed candidate records until they pass the registered search, deduplication, title/abstract screening and full-text eligibility workflow.

**Current status:** 90 seed candidates; 0 formally screened; 0 formally included. The seed matrix supports gap mapping and search design, but it is not yet the final PRISMA corpus.

## 16 September 2026 — Novelty boundary

The project will not claim novelty for any component alone:

- physics-informed reconstruction;
- model-mismatch compensation;
- joint image/kernel estimation;
- diffusion-based blind inversion;
- time-varying restoration;
- image or operator uncertainty alone;
- compound synthetic degradation;
- data-consistency loss;
- visually sharper CCTV output.

The candidate contribution must identify a specific limitation relative to the closest methods and demonstrate a reproducible improvement. Combining compound mismatch, dual uncertainty and selective output is not by itself evidence of novelty.

## 16 September 2026 — Architecture gate

**Decision:** do not build a large custom neural architecture yet.

**Required evidence:** nearest-method full-text comparisons must substantiate a specific unresolved limitation; controlled experiments must show a reproducible failure under a defined mismatch; and the proposed mechanism must improve a predeclared reliability outcome at useful retained coverage. A missing seven-feature intersection or a failing weak baseline is insufficient. This replaces the earlier checklist-based gate.

## 16 September 2026 — Second pilot and narrower question

**Checkpoint:** 40/90 preliminary recommendations (38 advance, 2 unclear), 50 awaiting pilot triage. No formal inclusions. P006 and P016 remain unresolved; P032 still needs complete text.

**Evidence:** targeted readings show that AverNet evaluates compound/time-varying video degradation and PRISM evaluates image and kernel uncertainty, including image interval diagnostics. The VDPS repository also documents time-varying blind Zernike reconstruction. A hallucination-assessment preprint explicitly cautions against treating its sampled feasible-set diameter as a pointwise upper certificate. See [the source-backed batch report](../literature/screening/pilot_02_report.md) for locations and limits.

**Candidate question:** can propagating estimated-operator uncertainty improve the reliability of selectively released image detail when the true acquisition process leaves the assumed family?

**Decision:** continue the review and the bounded baseline comparison. Do not claim that this question is unsolved until the closest reliability methods, unresolved papers and remaining seed records are assessed. Validate thresholds on a separate split and distinguish empirical behavior under chosen shifts from an arbitrary-OOD guarantee.

## 16 September 2026 — Forensic boundary

The research may improve visibility and quantify recoverability. It must not describe plausible generated faces, text or number plates as recovered truth when the observation does not contain adequate supporting information.

## 16 September 2026 — Complete initial seed triage

**Checkpoint:** all 90 seed records have an initial recommendation: 82 advance, 8 unclear, zero untriaged. P006/P016 remain unresolved; the six new unclear cases are P060/P072/P082/P084/P086/P087. No complete formal full-text eligibility assessments or final inclusion/exclusion decisions are claimed.

**Decision:** retain the original umbrella title, **Physics-Informed Deep Learning for Robust Image Reconstruction Under Forward-Model Mismatch**. Continue to treat the selective-detail/operator-uncertainty question as a candidate, with novelty unestablished.

**New evidence:** P042 already proposes certificate-based fallback, P048 analyzes posterior sensitivity to measurement/prior mismatch, and P066 calibrates uncertainty from noisy data without clean targets. P064 joins inexact operators and uncertainty; further video and conformal competitors narrow any defensible claim. Primary sources and evidence limits are in `literature/screening/pilot_03_report.md`.

**Next gate:** complete full-text eligibility and source-supported extraction, resolve possible P026/P053 lineage, and compare the exact operator assumptions and reliability guarantees. Do not restart the seed list or add papers merely to reach a round number. Formal searches and citation chaining may legitimately add relevant records.

## 16 September 2026 — First complete AI full-text eligibility decisions

**Checkpoint:** 12 assessed, 11 include recommendations, 1 exclude, 78 pending. Human adjudication and final formal inclusion remain pending. Seven initially unclear records now have decisions; P016 is still an access problem. Preserve the historical initial-triage column and all 90 seed IDs.

**Decision:** assess eligibility and extract technical evidence together. Record the version/read extent and verify only source-supported feature fields. Use separate counters for completed AI decisions and formal inclusion, so actual progress is visible without overstating PRISMA completion. Protocol v0.4 documents this convention without changing eligibility.

**Implication:** the evidence distinguishes several kinds of mismatch and reliability. The candidate research question survives as a question to investigate, not as proven novelty. Continue the remaining full-text assessments and closest-method comparisons. See [the full-text report](../literature/screening/full_text_01_report.md) and its primary-source register.

## 16 September 2026 — Second AI full-text checkpoint

**Checkpoint:** 12 additional assessments, all include recommendations. Cumulative: 24 assessed, 23 include, 1 exclude, 66 pending. Formal database-search accounting and human adjudication remain outstanding.

**Decision:** retain the umbrella topic and candidate question. Operator point estimation, residual correction, image uncertainty and calibration already have relevant competitors; the contribution must specify what is estimated, which uncertainty is covered and under which acquisition shifts. No corpus-wide novelty conclusion is warranted yet.

**Evidence limits:** inspected versions and exact feature corrections are recorded in [checkpoint 02](../literature/screening/full_text_02_report.md). Retrieval failures remain pending. P026/P053 and the P065 precursor need lineage resolution. Version-specific quantitative/theoretical questions require reconciliation before reuse.

**Next gate:** continue the same full-text workflow for all 66 remaining seed records. Preserve the first 24 decisions, stable IDs and earlier audits; do not restart screening.
