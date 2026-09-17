# P035 addendum to provisional synthesis 01

**17 September 2026.** Read alongside the [dated synthesis](provisional_gap_synthesis_01.md). Its inventory remains a checkpoint-11 snapshot. Current seed-set reading totals are **90 assessed, 89 AI include recommendations, one exclude recommendation, zero awaiting full text**. Formal human decisions remain pending.

The final full text, Lee and Jang's [learned-residual diffusion paper](https://doi.org/10.1117/12.3098133), is assessed in [checkpoint 12](../screening/full_text_12_report.md). It strengthens the overlap for candidate 2 and adds a direct reliability-boundary comparator for candidate 1.

| Candidate | Effect of P035 | Decision |
|---|---|---|
| Operator-sensitive selective reconstruction | P035 includes an empirical model-error boundary and a prescribed valid-region recovery example. It does not demonstrate calibrated region selection using a score computed from an unknown capture alone. | Retain as a hypothesis. Compare against residual/correction scores and image uncertainty at matched coverage and cost. |
| Constrained discrepancy learning | P035 already regularises the learned residual, describes signal absorption and uses two-stage refinement. | Broad residual-correction and identifiability-awareness claims are occupied. A new constraint needs a demonstrated mechanism and benefit beyond these choices. |
| Temporal selective reconstruction | P035 evaluates static holography and scattering examples, not a time-varying video selection rule. | Keep deferred. Existing temporal comparators in synthesis 01 still apply. |

The normalised mismatch threshold near 0.1 is visually identified in its DHM study. Its definition uses true-versus-perturbed model evaluations. It is neither a transferable confidence level nor an operational patch-level threshold for our data. A learned-residual norm could be a useful observable control, but is a distinct proxy that needs validation.

The original topic remains unchanged. The next scientific step remains improving and comparing reconstruction baselines, then testing whether operator sensitivity adds reliable error ranking on independent sources. Completion of 90 readings does not demonstrate novelty or complete the scoping review. No new experiment was executed for this literature checkpoint.
