# Stage 06C — real RAISE acquisition-chain smoke test (25 September 2026)

**Scope:** engineering check on three RAISE-1k NEFs in `development_early_stop`. This run contains no solver, reconstructed image, held-out source, calibration result, or independent test outcome. It cannot establish a reconstruction improvement or the new method's novelty.

The checked-in [runner](../scripts/smoke_stage06c_raise_chains.py) accepts only the SHA-256-pinned 994-source Stage 06B eligible manifest. Before decoding it checks each requested role, source ID, filename, byte count and NEF digest against the independent Stage 06B audit. After decoding it checks the full RGB digest against that audit. The audit CSV's SHA-256 (`b33e76252c40c14416e8dfbe944404413cdd76e8d5696df566596ffa80335dec`) matches the [eligibility receipt](../experiments/stage06/manifests/RAISE_1k_eligibility_receipt_v1_20260925.json). Both an altered eligible manifest and an audit role mismatch were rejected during a negative check.

Three user-provided real NEFs (`r03d2a758t`, `r137bcd7at`, `r1a5903fct`) passed byte-level and rendered-RGB verification. The fixed 512×512 centre crop was processed twice with the same per-source noise seed and the two pre-existing [acquisition-chain configurations](../experiments/stage06/acquisition_chains.py). The linear-light chain adds blur and noise before applying the sRGB transfer function and JPEG; the comparator applies blur and noise to the rendered RGB before JPEG. The 06B renderer is assumed to provide an sRGB-like image; this approximation must be assessed before final method freeze.

| Source | Role | Between-chain pixel MSE (RGB 0–1) |
| --- | --- | ---: |
| `r03d2a758t` | development early-stop | 0.0000155544 |
| `r137bcd7at` | development early-stop | 0.000367659 |
| `r1a5903fct` | development early-stop | 0.000281566 |

Each acquisition chain produced a distinct image for each real source. This only confirms that the added stage runs on real verified RAISE images and produces a measurable perturbation. The [machine-readable source metrics](../results/stage06c_raise_acquisition_smoke/source_chain_smoke.csv) and [receipt](../results/stage06c_raise_acquisition_smoke/summary.json) record renderer settings, crop coordinates, versions, input hashes, output hashes and exact observations.

To reproduce with audited development files and the audit CSV from the Stage 06B export:

```bash
python scripts/smoke_stage06c_raise_chains.py \
  --nef /path/to/NEFs/r03d2a758t.NEF /path/to/NEFs/r137bcd7at.NEF /path/to/NEFs/r1a5903fct.NEF \
  --audit-csv /path/to/results/stage06b_external_audit/external_source_audit.csv \
  --output-dir results/stage06c_raise_acquisition_smoke
```

**Next experimental gate:** select and hash the actual DiffPIR repository/checkpoint, record its training-source limitations, and run paired nominal versus chain-aware reconstruction on permitted RAISE development images using the same reference, crop and error endpoint across DPIR and DiffPIR. The 06C solver comparison has not been run. Stage 06D modelling, 06E freeze, 06F independent test, and 06G manuscript remain later steps.
