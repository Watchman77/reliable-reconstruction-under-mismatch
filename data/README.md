# Data Policy

No third-party dataset is committed to this repository.

Future data directories should contain only manifests, checksums, acquisition metadata and scripts permitted by the applicable licences. Raw CCTV or surveillance material must not be committed without documented legal, ethical and privacy authorization.

Required split rule: partition by source image, video, scene or device before generating degraded derivatives. Variants of the same source must never cross training, validation and test sets.

## Development acquisition on 17 September 2026

The official DIV2K validation HR archive supplies 100 project **development-only** sources, recorded in [the manifest](manifests/div2k_development_100.json). Raw archive and crops remain ignored. Run `python scripts/prepare_div2k_development.py --download` from the repository root to reproduce acquisition and metadata.

DPIR reports training on 900 DIV2K images. These sources must not be presented as independent test data for those weights. The [dataset/baseline audit](../docs/dataset_and_baseline_audit_01.md) explains remaining checkpoint-overlap and final-split decisions. No calibration or test source has been assigned by this checkpoint.
