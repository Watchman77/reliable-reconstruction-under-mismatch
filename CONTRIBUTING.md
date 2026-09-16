# Contributing

## Literature entries

Every added study must include a primary-source URL, publication status, evidence-verification status and a precise unresolved gap. Do not code a survey as primary evidence. Preserve preprint-to-publication lineage and avoid duplicate counting.

## Experimental changes

- Record random seeds and software versions.
- Preserve true and assumed operator parameters.
- Split sources before deriving degraded samples.
- Select thresholds and calibration mappings on validation data only.
- Do not use test labels to tune reliability or abstention rules.
- State negative and conflicting results.

## Commits

Use concise messages that state what changed, for example:

```text
literature: add blind diffusion competitors
experiment: freeze compound mismatch manifest
docs: record abstention go/no-go gate
```
