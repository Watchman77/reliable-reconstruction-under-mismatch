# Full-text checkpoint 11 — 16 September 2026

**89 of 90 seed records now have AI full-text eligibility assessments: 88 include recommendations, 1 exclude recommendation (P060), and 1 pending (P035).** Four complete manuscripts supplied by the user were verified and assessed in this checkpoint. Human adjudication and formal inclusion remain pending.

The [criterion-level register](full_text_11.json) records publication identity, source filename, SHA-256, version, reading extent and verified feature fields. The [change audit](full_text_11_changes.json) records workbook changes and validation. The paper PDFs are not redistributed in this repository.

## Uploaded papers assessed

| ID | Supplied file | Decision | Main extraction and limit |
|---|---|---|---|
| P030 | `IEEE_Empirical_Bayesian.pdf` | AI include recommendation | Empirical-Bayes image posterior sampling with a point estimate of a low-resolution conditioning image. Standard-deviation/error maps support an uncertainty comparison, but no probability-coverage calibration is demonstrated. [Publication](https://doi.org/10.1109/LSP.2024.3361806). |
| P040 | `Video_Diffusion_Posterior_Sampling_for_Seeing_Beyond_Dynamic_Scattering_Layers.pdf` | AI include recommendation | Joint video and changing physical-parameter estimation, with captured optical measurements. Image sampling and tolerance-based parameter accuracy do not establish an operator posterior or calibrated uncertainty. [Publication](https://doi.org/10.1109/TPAMI.2025.3598457). |
| P049 | `accepted_version.pdf` | AI include recommendation | DeepVibes estimates satellite attitude and then reconstructs through an unrolled method. It exposes identifiability limits and prior-generated high frequencies. Its real-data example uses camera adaptation and lacks ground truth. [Publication](https://doi.org/10.1109/TGRS.2024.3415372). |
| P053 | `s11263-026-02977-y.pdf` | AI include recommendation | FaverNet conditions video restoration with frequency prompts and tests compound changing degradations. VideoLQ supplies real-video evaluation; no-reference quality scores do not establish faithful detail recovery. [Publication](https://doi.org/10.1007/s11263-026-02977-y). |

P030 and P049 are repository/accepted manuscript versions; equivalence with the final publisher reports was not assumed. P040 and P053 are publisher PDFs. Reading supports the stated eligibility and extraction decisions, not independent reproduction of every equation, numerical result or supplement.

## Coding distinctions

- **Image uncertainty:** P030 and P040 support image posterior sampling. Neither demonstrates calibrated probability coverage in the inspected evaluation.
- **Operator uncertainty:** estimating a physical parameter, or initializing a parameter network with Gaussian noise, does not establish a posterior over the forward operator. P040's parameter-tolerance accuracy measures estimation error, not calibration.
- **Time variation:** DeepVibes varies camera attitude during the acquisition of one pushbroom image. Its video-variation column is `No` under the existing dictionary, which requires changing degradation across a video sequence.
- **Learned prompts:** FaverNet's frequency prompts do not recover an explicit physical operator. Its Bayesian MAP formulation alone does not imply uncertainty quantification.
- **Unsupported detail:** statements about identifiability or prior-generated detail are recorded, but they are not automatically coded as a hallucination-detection experiment.

Only the feature fields listed in this checkpoint's register are verified. Other legacy fields remain provisional. `No` means not demonstrated in the inspected version.

## AverNet–FaverNet relationship

FaverNet explicitly identifies AverNet (P026) as the authors' previous work, describes its architectural differences, uses the earlier common-degradation synthesis approach, and compares their results. The predecessor relationship is therefore confirmed by P053, pp. 4–5 and §4.1. Both stable records remain in the seed map. Shared experiments and study-level grouping still require adjudication; no automatic merger or claim of independent evidence is made.

## Only P035 remains inaccessible

**Chanseok Lee and Mooseok Jang (2026), “Mitigating forward model mismatch in inverse problems via learned residuals and diffusion priors,” Proceedings of SPIE 14016, 140160D.** [DOI](https://doi.org/10.1117/12.3098133), [KAIST record](https://pure.kaist.ac.kr/en/publications/mitigating-forward-model-mismatch-in-inverse-problems-via-learned/).

The supplied SPIE full-article link could not be retrieved. Search indexed a PDF snippet, but the complete PDF timed out on opening. Targeted searches did not locate an accessible author manuscript. This is an access limitation, not an exclusion decision or a claim that no copy exists.

Two practical routes remain:

1. Request an author manuscript from co-author Mooseok Jang at **mooseok@kaist.ac.kr**. This public address is printed in the supplied P040 publisher PDF, p. 1. No message has been sent.
2. Request the paper through institutional library access or document delivery, using DOI **10.1117/12.3098133**.

The indexed snippet, institutional abstract and related papers have not been substituted for the missing full text. P035's decision and acquisition flag remain pending/unchanged.

## Research implication

Retain **Physics-Informed Deep Learning for Robust Image Reconstruction Under Forward-Model Mismatch** and the narrower reliability question. The new evidence strengthens the need to distinguish physical-parameter estimation, image sampling and probability calibration in our baselines. Joint estimation and temporal modeling are already demonstrated by close comparators. Novelty remains unestablished, and P035 can still affect the overlap analysis.

This leaves one manuscript to assess within the existing 90-record seed set. Human adjudication, publication-version reconciliation, source-specific quality checks and formal search accounting remain in [deferred work](deferred_review_tasks.md). No new seed quota or screening stage was introduced.
