# Stage 05 final independent-evaluation checkpoint

**Checkpoint date:** 25 September 2026  
**Experiment:** `independent_05`  
**Terminal stage:** `05F_locked_literature_and_experimental_synthesis`  
**Status:** completed and independently audited

## Decision

The locked independent experiment supports a narrower acquisition-chain and
reliability-assessment contribution. It does **not** establish the original
unified evidence-calibrated selective-reconstruction novelty claim.

This conclusion is fixed by the predeclared gates:

| Hypothesis | Locked result | Decision |
| --- | ---: | --- |
| H1: FBCNN + nominal DPIR versus nominal DPIR at `j75_b16_n2` | 90.13% lower source detail MSE; Holm-adjusted one-sided p = 1.99998e-05 | Confirmatory gate passed |
| H2: operator-spread versus image-transform-spread selection at 50% coverage | 4.46% lower retained-patch detail risk; Holm-adjusted one-sided p = 1.99998e-05 | Statistical gate passed; predeclared 5% practical gate failed |

The H2 estimate is 4.4640422584%. It must not be rounded to 5% for gate
interpretation. The shortfall is 0.5359577416 percentage points.

## Experimental scope

- 40 sealed independent sources.
- Seven locked acquisition chains.
- 280 source-chain observations.
- 1,680 quality rows and 33,600 risk rows.
- 10,000 paired source-bootstrap replicates.
- 100,000 paired sign-flip randomisations per confirmatory hypothesis.
- Holm multiplicity correction across H1 and H2.
- 286,720 calibration patch rows covering 11 score definitions.

No reliability-bin observation exceeded the locked event threshold of centre
16 x 16 patch detail RMSE greater than 0.05. Positive-event calibration and
discrimination are therefore not estimable for this event. Non-zero predicted
probabilities indicate overprediction; Brier-score rankings remain descriptive.

## Secondary acquisition-chain result

The serial FBCNN + DPIR pipeline reduced detail MSE for every JPEG chain in the
locked experiment: 17.81%, 95.27%, 90.13%, 81.96%, 90.05%, and 98.01%. The
uncompressed control changed by -2.53%. This supports an acquisition-chain
interpretation, not a universal superiority claim.

## Locked literature boundary

Stage 05F used the evidence snapshot locked to 15 September 2026:

- 90 studies;
- 81 peer-reviewed works;
- 62 coded closest competitors;
- canonical embedded snapshot SHA-256:
  `3596bc71e6ff585b749edafb0845dbd88a324e3c9c811b1ca395ca9ffe073387`.

The broad ideas of physics-informed mismatch handling, blind image/operator
inference, all-in-one restoration, diffusion priors, and uncertainty estimation
are already occupied. This evidence snapshot is not a completed registered
systematic review and must not be presented as one.

## Permitted manuscript claim

> In the locked independent experiment, JPEG-aware deblocking before mismatch-aware DPIR produced large detail-fidelity gains across compressed acquisition chains, while offering no benefit on the uncompressed control. Operator-spread uncertainty yielded a statistically detectable but subthreshold selective-risk improvement, and positive-event calibration could not be established at the predeclared failure threshold.

## Claims that are not permitted

- first physics-informed reconstruction method robust to mismatch;
- first blind or joint image/operator reconstruction system;
- fully calibrated uncertainty or guaranteed abstention;
- hallucination-free or forensic recovery;
- practical superiority of operator-spread selection under the predeclared 5% gate;
- a claim that the 90-study evidence map is a completed systematic review.

## Archive and notebook receipts

Google Drive re-packaged the uploaded folders. The wrapper hashes below are
retained for chain-of-custody, while the original notebook-generated archive
hashes remain the canonical outer-archive identifiers.

| Artifact | SHA-256 | Role |
| --- | --- | --- |
| Original Stage 05E archive | `6566319869d7b2c86902aa4f29d071c8a7bdbbce2bbe1b5a9649f4aaab690fa3` | Canonical 05E archive |
| Uploaded Stage 05E Drive wrapper | `dbb638d70dcca913393bb5ceb2df339d3eb2e06850a9cf1f3964e18ac1e742ca` | Verified wrapper |
| Executed Stage 05E notebook | `270f3833529f1863a405fa4c515bb154efa6cf5766e1fe35cfd66dae97f27827` | Execution record |
| Original Stage 05F archive | `3bd6e0d4207dc96ab28ea01c1ab5705d8fb98eb0b92fb2659629b69fd30e07fb` | Canonical 05F archive |
| Uploaded Stage 05F Drive wrapper | `1623b466c07d697aceb21a265ad9a90e44b75da36580b2a1e256f13c89bdd039` | Verified wrapper |
| Executed Stage 05F notebook | `b4585574899907ca4749a33ebb5becf0639a60f88a74667799c71716bf113e25` | Execution record |
| Clean Stage 05F notebook | `8c71b52d9cf0b51a656efeeff25736a06be294270fd708aa98e9ee24d6392f10` | Repository runner |

All manifest-tracked files in the uploaded Stage 05E and Stage 05F archives
passed byte-count and SHA-256 verification. The original ZIPs, wrappers, sealed
05D shards, and executed notebooks remain external research records; Git tracks
the reproducible clean notebooks, compact tables, figures, receipts, and
validation code.

## Repository disposition

The following are suitable for Git:

- clean Stage 05E and 05F notebooks;
- Stage 05F notebook builder;
- compact Stage 05E and Stage 05F result tables and JSON receipts;
- final figures;
- validation code;
- this decision checkpoint and the manuscript draft.

The five sealed Stage 05D shard ZIPs, the Stage 05E/05F ZIPs, and executed
notebook copies should remain in controlled external storage. They are large
immutable evidence objects, and their hashes above provide repository linkage.

## Next scholarly task

The experiment is closed. The next task is manuscript completion: insert
verified literature citations, select a target venue, adapt the manuscript to
that venue, and complete human co-author review without changing the locked
result interpretation.
