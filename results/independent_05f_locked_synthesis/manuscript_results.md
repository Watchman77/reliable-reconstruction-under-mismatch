# Locked literature and experimental synthesis

## Scope

This synthesis uses the one-time independent analysis of 40 sealed sources across seven acquisition chains and the literature snapshot locked to 15 September 2026. No post-test threshold, endpoint, method, or hypothesis was changed.

## Confirmatory reconstruction result

On the primary JPEG chain (`j75_b16_n2`), FBCNN preprocessing followed by nominal DPIR reduced source-level detail MSE by **90.13%** relative to nominal DPIR alone. The mean paired difference was -0.000116743531, with a 95% source-bootstrap interval of [-0.000167013163, -7.4384089e-05] and Holm-adjusted one-sided p = 1.99998e-05. The predeclared reconstruction gate passed.

The secondary chain analysis was directionally coherent: the serial FBCNN+DPIR pipeline improved detail MSE on every JPEG chain, while the uncompressed control changed by -2.53%. This pattern supports an acquisition-chain interpretation rather than a universal advantage.

## Confirmatory selection result

At 50% coverage on the primary chain, operator-spread selection reduced source retained-patch detail risk by **4.46%** relative to image-transform spread. The paired 95% bootstrap interval for the absolute difference was [-5.13609192e-07, -8.98451127e-08], and the Holm-adjusted one-sided p-value was 1.99998e-05. The statistical gate passed, but the predeclared 5% practical gate did not; therefore the confirmatory selection claim was not established.

Descriptively, the 50%-coverage detail risks were 4.91009752e-06 for the oracle, 5.55516233e-06 for operator spread, 5.81473454e-06 for image-transform spread, 7.52514134e-06 for the trained PatchErrorNet ensemble, and 1.27836051e-05 for random retention. These comparisons are secondary and do not override the failed practical gate.

## Calibration boundary

Across 286,720 calibration patch rows, no reliability-bin event exceeded the locked threshold of centre-patch detail RMSE > 0.05. Consequently, positive-event calibration and discrimination could not be validated. The non-zero predicted probabilities indicate overprediction of this locked failure event. Brier-score rankings are descriptive only because no formal pairwise calibration comparison was predeclared.

## Literature boundary and final claim decision

The locked evidence snapshot contains 90 studies, including 81 peer-reviewed works and 62 coded closest competitors. It establishes that physics-informed mismatch handling, blind image/operator inference, all-in-one restoration, diffusion priors, and uncertainty estimation are not individually novel.

Because the combined experimental novelty gate did not pass, the original unified evidence-calibrated selective-reconstruction novelty claim is **not established**. The supportable contribution is narrower: an independently audited demonstration that JPEG-aware deblocking can substantially improve detail fidelity before mismatch-aware DPIR on compressed acquisition chains, together with a transparent reliability assessment showing that operator-spread selection was statistically detectable but practically subthreshold and that the locked calibration event was too rare to validate.

## Permitted claim

> In the locked independent experiment, JPEG-aware deblocking before mismatch-aware DPIR produced large detail-fidelity gains across compressed acquisition chains, while offering no benefit on the uncompressed control. Operator-spread uncertainty yielded a statistically detectable but subthreshold selective-risk improvement, and positive-event calibration could not be established at the predeclared failure threshold.

## Prohibited claims

- first physics-informed reconstruction method robust to mismatch;
- first blind or joint image/operator reconstruction system;
- fully calibrated uncertainty or guaranteed abstention;
- hallucination-free or forensic recovery;
- practical superiority of operator-spread selection under the predeclared 5% gate.

## Recommended paper direction

Proceed as an acquisition-chain and reliability-assessment paper or a rigorous benchmark/protocol contribution. Preserve the negative H2 practical-gate result and calibration boundary as central findings. A future confirmatory study may define a better-powered failure event and broader real-device transfer protocol, but it must be preregistered and reported as a new experiment.
