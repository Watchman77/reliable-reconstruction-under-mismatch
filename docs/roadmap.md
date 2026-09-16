# Roadmap

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
