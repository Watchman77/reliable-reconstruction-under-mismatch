# Pilot 02 — screening and a closer novelty check

Checked 16 September 2026 under protocol v0.3. AI-assisted convenience triage, not a completed systematic review. All recommendations await human adjudication.

| Status | This batch | Cumulative |
|---|---:|---:|
| New seed records triaged | 20 | 40 |
| Recommend full-text review | 20 | 38 |
| Unclear | 0 new; 2 revisited | 2 |
| Seed records awaiting pilot triage | — | 50 |
| Formally included / excluded | 0 / 0 | 0 / 0 |

The stable seed pool remains 90. P021–P040 were selected in ID order. No database query was executed and no discovery dates were reconstructed. This batch does not imply that all abstracts, complete papers or bibliographic fields were verified.

The [record-level log](pilot_02.json) records sources, evidence basis, scope rationale, metadata repairs and a full-text question for every new record. The [field audit](pilot_02_changes.json) records workbook/reference changes. Earlier pilot files are preserved unchanged.

## Evidence limits

- P032 was advanced conservatively using its title and indexed evidence. Its complete abstract and full text remain unavailable here. In particular, its existing positive image-uncertainty, operator-uncertainty and calibration codes are **unverified**.
- P026, P037 and P038 received targeted technical inspection. The passages below support specific findings, not complete eligibility decisions or validation of every feature code. P038 was inspected in the linked preprint version; reconcile the final conference text before full extraction.
- P040 received abstract and repository inspection. Repository experiment names establish documented configurations, not successful reproduction.
- P006 remains unclear after inspection of its experiments section. P016 remains unclear after unsuccessful retrieval retries. Neither is excluded, and neither is counted again among the 20 new records.
- The workbook's binary feature codes remain provisional. Do not aggregate them as confirmed absence/presence, convert uninspected cells to “No,” or infer a gap from missing evidence.

## Targeted extraction: what actually overlaps our idea

| Study and inspected location | Supported finding | Consequence for our proposed contribution |
|---|---|---|
| P026 AverNet, §§4.1–4.2, PDF pp. 6–7 | Randomized mixtures include three noise types, resizing/blur, JPEG and video compression; experiments vary degradation-change intervals and combinations. | Compound and time-varying video degradation is already studied. These tests alone do not establish transfer to unseen cameras or operator families. |
| P037, Remark 3.4, Proposition 3.5 and Algorithm 2 | Finite-sample feasible-set diameter is a lower approximation to the complete-set diameter. | A small sampled diameter cannot directly certify a small worst-case hallucination error. Any proposed practical certificate must address this limitation and state its assumptions. |
| P038 PRISM, §§2–3, Table 3 and Figs. 3–4 | Joint image/kernel sampling is accompanied by uncertainty diagnostics: image Gaussian NLL, image interval outliers and kernel error/standard-deviation maps. About 99% coverage is reported for one illustrated image's 3-SD intervals. | Neither dual uncertainty nor interval checking is new. The inspected evaluation uses FFHQ motion deblurring; it does not establish reliable coverage under an unseen operator family. |

Sources: [AverNet published PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/e635a25e49e73adc51f76aef462ff2f8-Paper-Conference.pdf), [hallucination assessment preprint](https://arxiv.org/html/2605.13146v1), [PRISM preprint](https://arxiv.org/html/2509.16106v1). These are scoped readings, not claims of having reproduced the experiments or proven that an unmentioned capability is absent from the full literature.

The [VDPS author repository](https://github.com/star-kwon/VDPS) also documents blind, real-input and time-varying Zernike configurations. This strengthens the need to compare against existing dynamic operator-estimation methods. A time-varying physics layer by itself is not a defensible novelty claim.

## Narrower candidate question

**Can accounting for uncertainty in an estimated forward operator improve the reliability of selectively released image detail when the true acquisition process leaves the assumed model family?**

This is a question to investigate, not an established gap. It requires a specific mechanism and measurable advantage over the nearest methods. Combining more named components is insufficient. The remaining 50 records and unresolved full texts may already address it.

A bounded feasibility comparison should separate two settings: unknown parameters within a correct family, and a deliberately omitted degradation such as compression or spatially varying blur. Freeze held-out images, degradation settings and validation-only threshold selection before testing. Compare conditional image uncertainty, propagated operator uncertainty and a simple residual-based rejection baseline under comparable budgets. Report reconstruction error, interval width/coverage and risk versus retained output, with uncertainty estimates grouped by independent image or video rather than treating neighboring pixels as independent samples.

Use ground truth for controlled evaluation, not as an input to the deployed reliability score. Do not claim an arbitrary-OOD guarantee from validation calibration. Where operator uncertainty and image content are not identifiable, the method must acknowledge that limitation. Decide on a custom architecture only after the nearest-method comparison identifies a reproducible failure and a credible way to improve it.

## Reference repairs

- P022: expanded the title and author list; added the WACV DOI.
- P024: applied the earlier verified journal lineage to the matrix and exports: 2026 IEEE TIP, one study linked to its 2024 preprint. Final DOI remains unverified.
- P025: replaced the unrelated ECCV poster link with the correct DiffBIR chapter and DOI.
- P027: replaced the unrelated arXiv SLAM link with the official BMVC SR+Codec record; corrected the complete title, venue and authors.
- P029: added the verified Optics Express DOI.
- P030: replaced incorrect Akinwande authorship with Melidonis, Holden, Altmann, Pereyra and Zygalakis.
- P031: expanded the abbreviated title.
- P035: corrected the erroneous SPIE locator to DOI 10.1117/12.3098133, corresponding to volume 14016/article 140160D. Publication year is 2026; the conference took place in 2025.

Sources for each repair are in the JSON log. Other abbreviated author lists and bibliographic fields remain draft until checked. Adding a verified DOI is not verification of every field in that record.

## Next checkpoint

Continue P041–P060 and retrieve the highest-priority reliability competitors. Obtain human adjudication of the 40 recommendations and resolve P032/P006/P016. Then complete nearest-method full-text extraction and the existing frozen natural-image pilot before making a methodological novelty claim. Formal database searches, raw exports, deduplication and two-stage eligibility remain necessary for the systematic review.
