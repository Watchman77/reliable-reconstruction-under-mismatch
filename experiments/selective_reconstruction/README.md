# Selective reconstruction pilot preparation

This directory begins implementation of [pilot v0.1](../../docs/selective_reconstruction_pilot_spec.md). Current scope is development data and controlled forward measurements. No learned method, uncertainty score or selection rule has run.

## Reproduce the development checkpoint

From the repository root, install `requirements.txt` in your project environment, then:

```bash
python scripts/prepare_div2k_development.py --download
python experiments/selective_reconstruction/prepare_observations.py --limit 12
python experiments/selective_reconstruction/verify_preparation.py
```

The first command downloads about 449 MB from the official DIV2K host, checks the archive, and records 100 native-resolution centre crops in `data/manifests/div2k_development_100.json`. Every source is **development-only** because DPIR's paper reports training on 900 DIV2K images. The manifest does not establish any other checkpoint's independence.

Raw archives, crops and measurement arrays are ignored by Git; scripts and metadata reproduce them. The [dataset and baseline audit](../../docs/dataset_and_baseline_audit_01.md) records sources, terms, pinned baseline repositories and outstanding evaluation-data checks.

The second command writes 12 NPZ files and a manifest under `data/processed/development_observations/`. Each has:

| Array | Meaning |
| --- | --- |
| `clean` | Float32 RGB crop divided by 255 |
| `blur_noise` | Circular Gaussian blur plus unbounded additive Gaussian noise |
| `omitted_processing` | Same noisy observation after clipping, uint8 rounding and JPEG |

The NPZ files contain ground truth for development convenience. Future inference adapters must receive only the permitted observed array and nominal metadata; never pass the clean target or true acquisition metadata into a practical reconstruction or confidence score.

Parameters and colour/boundary assumptions are declared in the generated manifest. Source-dependent seeds prevent changing the image limit from changing previously generated noise. Centre crops are a plumbing choice, not evidence of representative scene coverage.

The [engineering check 01](engineering_check_01.json) verifies image identities, crop hashes, repeatable paired observations, constant preservation, the Gaussian operator's adjoint and agreement with its FFT representation. These checks concern the forward operator only. They do not validate a reconstruction result, statistical calibration or novelty.

Next: consistent classical solver and a DPIR adapter; weight checks and measured runtime; independent calibration/test data selection; then score comparisons and risk–coverage evaluation. Preserve the previous canary results as historical evidence.
