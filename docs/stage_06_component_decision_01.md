# Stage 06 component decision 01 — recommended development stack

Status: provisional development decision. It becomes confirmatory only after smoke tests, compute estimates, overlap checks, and the Stage 06 freeze.

## External source: RAISE-1k

Recommended pool: the official RAISE-1k subset, using a source-level split fixed before reconstruction outcomes are produced.

Reasons:

- RAISE images are camera-native, high-resolution RAW captures rather than web-resized derivatives.
- The official source describes 8,156 images from three cameras, four photographers, and more than 80 locations, with tagged content categories.
- The official download page provides a stratified 1,000-image subset and permits non-commercial research and educational use with citation.
- RAW provenance supports a deterministic, documented rendering step and a more realistic camera-response acquisition experiment.

Official sources:

- <https://loki.disi.unitn.it/RAISE/>
- <https://loki.disi.unitn.it/RAISE/download.html>

The dataset is not automatically considered unseen. Exact decoded-pixel hashes, file hashes, perceptual candidates, model-training provenance, and manual review must be completed. The proposed source pool is deliberately larger than the final compute set so the role allocation can be frozen by source while preserving camera/category balance.

## Second solver: DiffPIR

Recommended replication solver: the official DiffPIR plug-and-play diffusion reconstruction method with one pinned public checkpoint and configuration.

Reasons:

- it uses a diffusion generative prior rather than DPIR's discriminative Gaussian-denoiser prior;
- it exposes deblurring as a plug-and-play inverse problem and therefore permits the same frozen forward operator;
- it is strong enough to make cross-solver replication informative rather than a weak straw comparator.

Official project and code:

- <https://yuanzhi-zhu.github.io/DiffPIR/>
- <https://github.com/yuanzhi-zhu/DiffPIR>

Risk: DiffPIR's implementation is based partly on DPIR, and its diffusion checkpoint provenance must be documented. The claim is transfer across materially different priors, not complete software independence.

## Alternate acquisition stage: linear-light operator plus camera response

Recommended second mismatch family:

1. convert a deterministic sRGB reference to linear RGB;
2. apply blur and sensor-like additive noise in linear light;
3. apply the sRGB response/tone curve;
4. quantise and JPEG encode;
5. compare an inverse that incorrectly operates in sRGB with one that accounts for the response curve.

This adds a nonlinear camera-response stage that the nominal inverse omits. It tests the mechanism beyond JPEG deblocking while remaining deterministic and auditable. The candidate implementation is `experiments/stage06/acquisition_chains.py`.

## Proposed role allocation before compute reduction

Begin with the 1,000-source RAISE-1k pool and create a camera/category-stratified manifest with these source roles:

| Role | Provisional sources | Purpose |
| --- | ---: | --- |
| Development fit | 500 | fit the chain-aware reliability score |
| Development early-stop | 150 | model/configuration selection |
| Development calibration | 150 | continuous and severity calibration; freeze threshold |
| External pilot | 50 | transport and conservative event-support estimate |
| Independent test | 150 | one-time locked evaluation |

These counts are not frozen sample sizes. After a low-cost crop-level pilot, `scripts/plan_stage06_sample_size.py` must determine the independent minimum from source-level precision and conservative event support. If compute requires fewer sources, the reduction must occur before outcome inspection and preserve the calculated independent minimum.

## Decision still required before freeze

- exact RAW rendering library, version, parameters, and colour space;
- DiffPIR repository commit, checkpoint hash, number of function evaluations, and solver parameters;
- the primary alternate chain severity;
- primary operational threshold and decision interpretation;
- final source counts from the source-level design calculation;
- whether the external-pilot sources remain permanently outside confirmatory testing.

