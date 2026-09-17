# Pilot 00 — saved Colab run review

Reviewed 17 September 2026. This is a four-source development diagnostic, separate from the repository's earlier 12-source observation preparation. Settings, crops and noise levels differ; their results must not be pooled.

## Evidence and status

The user ran [the notebook in Colab](https://colab.research.google.com/drive/1TqsS_EZDL0Yt4Jdi-XZ7iya3RFUr0z93). The reviewed Drive revision was modified at 09:05:31.727 UTC. Fifteen code cells have saved successful execution metadata; none contains an error output. The final output reports four sources, 24 reconstruction-metric rows and successful numerical/data checks. The ridge normal-equation residual is approximately 2.82e-16.

The saved code and text outputs were inspected. This is not an independent rerun by the reviewing assistant or proof of a clean-runtime, top-to-bottom execution. Execution counts have gaps. Figure output is stored in a Colab external package; the connector returned a hidden-output placeholder, and that package was not accessible for visual inspection. Raw CSVs and figure files have not yet been retrieved. The user-supplied source images have not been matched against the official archive's decoded-pixel hashes.

## Reported results

Pooled-MSE PSNR in dB, from the saved printed output; higher is better:

| Observation | Degraded input | Assumed blur inverse | Known blur diagnostic |
|---|---:|---:|---:|
| Blur + noise | 29.74379 | 25.19469 | 29.10481 |
| Blur + noise + JPEG processing | 29.67759 | 27.69682 | 28.10548 |

The fixed inverses lose to the degraded-input baseline in both conditions. At 50% pixel retention, operator spread reports a 9.9% and 40.2% MSE reduction against expected random selection, respectively. It does not beat the best simple operational control: measurement residual wins in the blur/noise case and the image-gradient heuristic wins in the JPEG case. These values match the earlier uploaded pilot's printed values at displayed precision; this is not a bytewise comparison of raw result arrays.

There is no demonstrated novel advantage, calibrated uncertainty, learned reconstruction or independent-test result. Known blur is an oracle diagnostic. JPEG processing also includes clipping and 8-bit quantisation. Pixel selection and RGB MSE are not the proposed patch-level bad-detail endpoint.

## Persistence repair

The executed setup used `OUTPUT_DIR = Path("results")`, a relative Colab-runtime directory. Saving the notebook to Drive does not establish that its separate result files were saved there. A targeted listing of the project folder did not show a results folder at review time.

The [repository notebook](../../notebooks/00_DIV2K_Operator_Mismatch_Pilot.ipynb) preserves all original code and saved outputs and appends **Section 10: Save this run to Google Drive**. Account identifiers were removed from execution metadata. The new cell copies eleven named CSV/JSON/PNG files into a unique dated project folder, verifies each copy by SHA-256, and writes an export manifest. Earlier runs are not overwritten. The helper's syntax and copy behaviour were checked locally using disposable fixtures; it has not run in the user's Colab session.

Run Section 10 in the existing live session. If its variables or files have expired, rerun the notebook first. Review the exported CSVs and figures before further numerical or visual claims. The historical authoring note and `pilot_validation` metadata describe the original preparation environment; [saved_run_review.json](saved_run_review.json) records the subsequent Colab execution evidence separately.

## Next experimental decision

Develop the reconstruction baseline on development sources: compare regularisation settings and baselines across several blur/noise conditions, retaining the degraded input as a control. Then compare operator sensitivity against matched simple controls and an image-only uncertainty baseline. Do not use these four development sources as final calibration or test data. The broader [pilot specification](../../docs/selective_reconstruction_pilot_spec.md) and [dataset/baseline audit](../../docs/dataset_and_baseline_audit_01.md) still govern the independent evaluation design.
