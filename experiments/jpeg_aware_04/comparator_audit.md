# FBCNN comparator audit — 17 September 2026

The comparator is the established colour FBCNN from Jiang, Zhang and Timofte, *Towards Flexible Blind JPEG Artifacts Removal* (ICCV 2021). This audit checks the primary paper's relevant method/training description and the official implementation and release; it is not a claim to reproduce the paper's benchmark or to have reviewed every related method.

## Identity and loading

- Official repository: https://github.com/jiaxi-jiang/FBCNN
- Pinned commit: `54d1831927506b3247e2d4d245abb4f4dab1a1cd`.
- Official colour checkpoint: https://github.com/jiaxi-jiang/FBCNN/releases/download/v1.0/fbcnn_color.pth
- Observed size: 287,755,111 bytes.
- Observed SHA-256: `8b0e4ef23d59cf7ac934a342cb31a17619e4fa4a0b3374a9d78c5174312387e8`. No publisher-signed digest was provided; this pins the downloaded bytes, not independent authorship certification.
- Architecture follows `main_test_fbcnn_color.py`: RGB in/out, widths 64/128/256/512, four blocks and `act_mode='R'`. Test-time architecture takes precedence over the example training configuration.
- The checkpoint loads strictly as a tensor state dictionary with `weights_only=True`; 71,921,796 parameters. The original vendor files and Apache 2.0 licence are preserved byte for byte and hashed in `fbcnn_provenance.json`.
- The network file imports `torchvision.models` but never uses its `models` alias. An AST check verifies this before removing only that unused import in memory, avoiding an unnecessary torchvision binary dependency. Network operations are unchanged.

## Information and adaptation

FBCNN predicts its quality-control scalar from the decoded image. The official dataset uses `q=(100-quality)/100`; the notebook logs `100*(1-q)` for readability. No true JPEG quality, clean target or manually selected quality value is supplied during operational inference. A small test checks automatic inference against reusing that same predicted scalar; this checks wiring, not restoration quality.

The adapter uses one full-tensor pass and clips its output to [0,1] without uint8 rounding before downstream inversion. This differs from saving a display PNG and then rereading it. The same clipping rule applies to all FBCNN branches. Rotated controls rerun FBCNN on the rotated observation, so their cost is reported separately from the shared preprocessing used across operator hypotheses.

The paper's Section 4.1 reports DIV2K and Flickr2K training and MATLAB JPEG generation over quality 10–95. The current pinned repository's dataset instead uses OpenCV and a training draw from 8–96; the official test also uses OpenCV. These are documented source differences; the precise released checkpoint training recipe cannot be inferred solely from the sample configuration. Our inherited Pillow Q75, 4:4:4 acquisition is frozen. Codec differences, blur/noise before JPEG and uncompressed inputs can all be outside the checkpoint's effective training distribution.

Both model families have unresolved image-level DIV2K overlap. Sources 0801–0804 remain exposed development data. FBCNN is a JPEG artifact-removal model, not a joint deblurring/noise/JPEG solver. Its composition with the fixed inverse is a declared baseline adapter, not a novel architecture, optimal cascade, exact JPEG likelihood or paper reproduction.

## Why retain six main comparisons?

FBCNN-only shows whether any improvement comes from preprocessing alone. FBCNN + classical tests whether the pretrained preprocessing benefits a simple inverse too. The raw input/classical/DPIR controls preserve historical comparisons. Running all six on uncompressed 8-bit observations records damage caused by unnecessary preprocessing. Separate operator and whole-pipeline rotation ensembles assess the proposed heuristic without claiming comparison against trained uncertainty estimation.

Sources: [primary paper](https://arxiv.org/pdf/2109.14573), [pinned official test](https://github.com/jiaxi-jiang/FBCNN/blob/54d1831927506b3247e2d4d245abb4f4dab1a1cd/main_test_fbcnn_color.py), [pinned network](https://github.com/jiaxi-jiang/FBCNN/blob/54d1831927506b3247e2d4d245abb4f4dab1a1cd/models/network_fbcnn.py), [pinned dataset](https://github.com/jiaxi-jiang/FBCNN/blob/54d1831927506b3247e2d4d245abb4f4dab1a1cd/data/dataset_jpeg.py).

## Colab bootstrap

FBCNN includes linear layers in its quality prediction/embedding branches. The notebook sets `CUBLAS_WORKSPACE_CONFIG=:4096:8` before importing Torch to support deterministic CUDA matrix operations on runtimes such as those covered by the [PyTorch 2.8 deterministic-algorithms documentation](https://docs.pytorch.org/docs/2.8/generated/torch.use_deterministic_algorithms.html). This is a runtime compatibility setting, not a model/hyperparameter change. Local validation uses CPU and does not validate CUDA or Drive mounting.
