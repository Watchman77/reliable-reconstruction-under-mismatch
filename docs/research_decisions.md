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
