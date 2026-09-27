# Stage 06F: sealed independent reliability result

## Provenance and scope

The one-time Stage 06F run completed on 150 allocated independent RAISE sources, yielding 43,200 held-out patch rows (144 per chain per source). The signed freeze preceded the independent run. This document reports the already frozen primary analysis; it does not alter the Stage 05 result, Stage 06 model, thresholds, or acquisition chains. Raw RAISE files and patch-level independent predictions are not redistributed here.

- Frozen specification SHA-256: `1960525d6272e89442a31b3daccab829bfb45e17898e35c62c15d4013788f437`.
- Signed freeze receipt SHA-256: `7a751827164108f30a96630aa8d64151aa21c176c53f845c44165c199c519ae1`.
- Sealed prediction CSV SHA-256: `7f87a0a26e284abe3246c51afca1392ff52b1db4c75e30c74f4ce396af61c056`.
- Execution receipt status: `sealed_complete_unanalysed`; `independent_test_inference: true`; no recorded failures; all 150 allocated source IDs completed.
- Freeze receipt signed by Watchman77 on 2026-09-27 at 00:33 UTC; it recorded that independent outcomes had not been inspected at signing.

These three byte hashes were checked against the owner's uploaded four-file sealed output bundle before analysis. The 150 CSV source IDs exactly matched the frozen independent allocation and both execution-receipt source lists. Every row had role `independent_test`, and each source contributed 144 distinct patches for each of `linear_j75_b16_n2` and `srgb_j75_b16_n2`; there were no missing or nonfinite numeric values. Predictions for severity events lay in [0, 1].

## Frozen primary decision

For each source, calculate absolute detail-RMSE prediction error for the residual-only comparator and proposed chain-aware score, averaged across that source's 288 patches. Define its paired gain as residual-only source MAE minus chain-aware source MAE. Average the 150 paired gains with equal weight per source. The predeclared success rule requires the lower bound of a two-sided 95% source-bootstrap percentile interval to exceed zero. The bootstrap uses 20,000 resamples of 150 sources with replacement, `numpy.random.default_rng(20260926)`, and quantiles 0.025 and 0.975.

| Primary source-macro metric | Result |
| --- | ---: |
| Residual-only MAE | 0.0028508201 |
| Chain-aware MAE | 0.0024352661 |
| Mean paired gain | **0.0004155540** |
| Gain relative to residual-only MAE | **14.5766%** |
| 95% source-bootstrap interval for paired gain | **[0.00027477, 0.00058044]** |
| Sources with positive gain | 115 / 150 |
| Frozen primary decision | **Pass: lower interval bound > 0** |

Relative improvement describes this endpoint, not a separately frozen percentage gate. In particular it cannot be compared as a pass/fail outcome against the Stage 05 reconstruction experiment's 5% practical gate, which concerned a different quantity.

## Descriptive secondary findings

The chain-specific intervals below use the same source-bootstrap seed and 20,000 resamples, each over the 150 source gains for that chain. They are descriptive and do not constitute additional confirmatory tests.

| Represented acquisition chain | Residual-only source MAE | Chain-aware source MAE | Mean paired gain | Relative MAE reduction | Sources improved | Descriptive 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Linear-light JPEG | 0.00314493 | 0.00248487 | 0.00066006 | 20.988% | 110 / 150 | [0.00040627, 0.00096588] |
| sRGB JPEG | 0.00255671 | 0.00238566 | 0.00017105 | 6.690% | 93 / 150 | [0.00009163, 0.00025298] |

Across all 43,200 patches, prediction RMSE was 0.00619969 for residual-only versus 0.00519016 for chain-aware. This patch summary is descriptive; patches are nested within sources.

| Detail-RMSE event threshold | Chain | Positive patches / 21,600 | Sources with positive patches / 150 | Residual-only Brier, pooled | Chain-aware Brier, pooled |
| --- | --- | ---: | ---: | ---: | ---: |
| > 0.0075 | Linear-light JPEG | 9,169 | 126 | 0.160231 | 0.133006 |
| > 0.0075 | sRGB JPEG | 8,753 | 123 | 0.160231 | 0.133006 |
| > 0.0100 | Linear-light JPEG | 5,354 | 103 | 0.116365 | 0.099173 |
| > 0.0100 | sRGB JPEG | 4,978 | 95 | 0.116365 | 0.099173 |

The Brier scores in the last two columns pool *both chains* at each threshold and are repeated only for ease of reading; they are not chain-specific Brier scores. Both positive and negative events occurred at both thresholds. These thresholds are study endpoints, not universal definitions of operational failure.

## Interpretation and limitations

The predeclared independent comparison supports improved prediction of DPIR reconstruction detail error over the frozen residual-only comparator on these two represented acquisition chains in RAISE. The previously run development leave-one-chain-out analysis found adverse transport, especially from sRGB training to linear-light evaluation. Thus this result **does not** establish reliability on a previously unseen chain. Training-image-level overlap between RAISE and the pretrained DRUNet/FBCNN checkpoints could not be ruled out completely and was disclosed before the freeze; this limits broader external-validity claims. The Stage 06F sealed output contains reliability predictions and observed detail error, not the nominal-reconstruction output required to assert a new independent reconstruction gain over the Stage 05 practical gate.

Preserve the original sealed bundle and receipts in the owner's controlled storage. Any subsequent reconstruction analysis, calibration plot, or manuscript language must be labelled according to its actual design and must not rewrite the one-time confirmatory decision.
