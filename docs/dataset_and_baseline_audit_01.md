# Dataset and baseline audit 01

**Checkpoint:** 17 September 2026. Source inspection began 16 September. The user prioritised the experimental research over the scoping-review work. Protocol v0.4 and all screening decisions remain unchanged.

## Decision and first data

Start with controlled paired observations: a clean image is the reference, and we generate a degraded measurement using a recorded acquisition process. This makes reconstruction errors measurable. Raw CCTV without a clean reference cannot answer the first retained-detail fidelity question by itself.

The official [DIV2K page](https://data.vision.ee.ethz.ch/cvl/DIV2K/) provides 800 training HR images and 100 validation HR images; its separate challenge test HR images are not publicly supplied there. It restricts the dataset to academic research and requests dataset/challenge citations. We downloaded the official validation HR archive, **448,993,893 bytes**, and verified its 100 expected PNG members and exact decoded-image uniqueness. The observed SHA-256 is recorded in [the manifest](../data/manifests/div2k_development_100.json); this is our checksum, not a publisher-signed digest.

All 100 images are assigned to **project development**, regardless of their original dataset split name. Each has one native-resolution 256 × 256 centre crop, no resizing or black padding. This is a reproducible engineering subset, not a representative or statistically powered benchmark. Semantically related scenes have not been deduplicated.

**Training-overlap finding:** the [DPIR paper, inspected v2, section on training data](https://arxiv.org/html/2008.13751v2) reports using **900 DIV2K images** to train its denoiser. It also reports BSD, Waterloo and Flickr2K data. This is dataset-level evidence of overlap, not a recovered exact checkpoint training manifest. We therefore exclude the acquired DIV2K sources from claims of unseen-image evaluation for those weights. Merely moving an image into our test folder would not remove that overlap.

## What the first engineering run does

The [observation generator](../experiments/selective_reconstruction/prepare_observations.py) creates two paired measurements per source:

- stationary Gaussian blur with standard deviation 1.6 pixels, followed by Gaussian noise with standard deviation 0.01;
- the same noisy measurement followed by clipping, 8-bit rounding and JPEG at quality 40 with subsampling 2.

The second condition omits an entire processing chain from the assumed model. It is not labelled pure compression because clipping and quantization also change the measurement. Float measurements are stored directly; the first condition is not silently clipped to make a viewable PNG. Blur uses circular boundaries in stored RGB values: a controlled approximation, not a calibrated physical camera model.

The first run uses 12 development sources and produces 24 observations. No reconstructor, uncertainty score or selection rule is evaluated. The [engineering check](../experiments/selective_reconstruction/engineering_check_01.json) records data-integrity, deterministic-regeneration and forward-operator checks. This run does not answer the novelty question.

## Baseline implementation audit

This is a static source/configuration audit. Model weights have not been downloaded, hashed or executed. Listed default settings are inspected code settings, not recommended final hyperparameters or measured costs.

| Family and candidate | Verified implementation facts | Consequence for our pilot |
| --- | --- | --- |
| Classical Wiener/Tikhonov | Existing project canary is available. Its acquisition uses zero-padded convolution while its Fourier inverse needs an explicit boundary audit. | Preserve historical results. For new comparisons, use a consistent forward/adjoint pair; do not attribute boundary errors to operator uncertainty. |
| Operator-conditioned DPIR with DRUNet | Official MIT repository; grey and colour checkpoint links. Deblurring demo selects CPU/CUDA, supplies a kernel and noise level, and defaults to 8 iterations. | Natural-image candidate. Adapt to our supplied observations instead of regenerating measurements inside the demo. Exclude known training sources from independent evaluation; verify checkpoint and dependency compatibility. |
| Operator-oblivious NAFNet GoPro width 32 | Official GoPro training/evaluation guide, checkpoint link and test configuration. MIT plus bundled BasicSR Apache notices. The test config supports CPU mode. | Useful frozen deblurring comparator. Its acquisition training domain differs from the synthetic pilot; report that difference and audit exact data overlap. |
| Blind sampler GibbsDDRM | Official MIT repository, FFHQ/AFHQ checkpoint routes and 256-pixel configs. Inspected FFHQ config has 100 deblurring sampling steps and iterative operator updates. | First blind-sampling integration candidate. Face/dog priors do not establish general-scene performance. Runtime and memory remain unmeasured. |
| BlindDPS | Official code, FFHQ image and kernel checkpoint routes, 256-pixel image config. No top-level licence file in the inspected recursive tree. | Retain as a comparator; confirm applicable code/checkpoint terms before adaptation or redistribution. No claim that it lacks permission in every possible source. |
| PRISM | Paper remains a close comparator. No author-linked implementation was verified through this checkpoint's paper and targeted search. | Code/weights status unresolved, not proof of nonexistence. Do not claim reproduction or silently substitute another sampler. |

Pinned source snapshots:

- [DPIR](https://github.com/cszn/DPIR/tree/15bca3fcc1f3cc51a1f99ccf027691e278c19354): inspected `main_dpir_deblur.py`, `model_zoo/README.md` and `LICENSE`.
- [NAFNet](https://github.com/megvii-research/NAFNet/tree/2b4af71ebe098a92a75910c233a3965a3e93ede4): inspected `docs/GoPro.md`, `options/test/GoPro/NAFNet-width32.yml` and `LICENSE`.
- [GibbsDDRM](https://github.com/sony/gibbsddrm/tree/66d2a989af4135c4d8bfbff2d1054b32e890b437): inspected `README.md`, `LICENSE`, `configs/ffhq_256_deblur.yml` and file tree. Its README names `requirement.yml`, while the tree contains `environment.yml`; reconcile during setup.
- [BlindDPS](https://github.com/BlindDPS/blind-dps/tree/4c0af9176592655d95b7b935c969df940804291b): inspected README, recursive tree and `configs/model_config.yaml`.
- [PRISM inspected paper](https://arxiv.org/html/2509.16106v1). This audit does not change its recorded full-text version.

## Data needed for the decisive experiment

The pilot still targets **at least 100 independent calibration sources and 100 separate test sources**, plus development images. Those evaluation datasets and IDs are **not frozen or acquired by this checkpoint**. Before assigning them:

1. Verify each selected checkpoint's training sources and upstream model lineage. Document unresolved overlap explicitly.
2. Use images compatible with the image prior. A held-out face-domain panel could test the mechanism with the released diffusion priors, but would not establish general CCTV-scene performance. A general-image panel needs a suitable prior and its own overlap audit.
3. Separate original scenes/identities/sequences before making crops or degraded versions. A hundred crops of one image are one source, not a hundred independent examples.
4. Keep development, calibration and test roles distinct. Select score features on development data, thresholds on calibration data, and evaluate frozen choices on test data. Audit any face identities or scene overlap as well as exact duplicates.
5. Add paired captured images and CCTV-oriented testing only after the controlled mechanism is useful. Registration and clean-target uncertainty need their own documentation.

The scientific sequence is **reproduce baselines → show a specific reliability failure → test the proposed operator-sensitive score → compare under matched information and compute → decide whether to proceed**. Better-looking examples or changing a dataset name cannot establish novelty. P035 and closest-method checks remain relevant alongside experimentation.

## Next execution checkpoint

Implement the consistent classical solver and DPIR inference adapter on development observations, and obtain/check the selected weights. Measure single-image runtime before choosing ensemble size or scaling to hundreds of sources. In the current shell, NumPy/SciPy/Pillow are available; PyTorch is absent and no `nvidia-smi` executable was found. This is a runtime observation, not a statement about the user's computer or every connected environment. No GPU speed or memory requirement is claimed measured.

Continue the calibration/test data audit alongside these adapters. Before the decisive comparison, freeze the data/model manifests, severity ranges, information budget and metric implementation described in [pilot v0.1](selective_reconstruction_pilot_spec.md). The practical mechanism is still untested and novelty remains unestablished.
