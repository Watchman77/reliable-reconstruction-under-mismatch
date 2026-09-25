# Stage 06C paired solver runner — development handoff

The [Colab notebook](../notebooks/06C_RAISE_Paired_DPIR_DiffPIR_Development.ipynb) launches the [development runner](../scripts/run_stage06c_paired_development.py). It starts with one of the three real, SHA-checked RAISE development early-stop sources (`r137bcd7at`). Change the `SOURCE_IDS` list only after the first run succeeds. This code has **not** yet completed a GPU model run; its results files do not exist in the repository.

## Inputs and operator

- The eligible-source manifest and independently audited CSV must have the precise hashes from the reviewed 06B receipt. Each requested NEF and its full decoded RGB are checked against that audit before inference. Only development fit or early-stop roles are accepted. The notebook starts with a development early-stop engineering canary.
- The RAW renderer is the audited fixed 06B renderer. A fixed 256×256 centre crop is used because the selected [ImageNet class-unconditional diffusion prior](https://github.com/yuanzhi-zhu/DiffPIR/blob/2a9898129a1b274131b98746e5b364bc20adc1e1/model_zoo/README.md) is designed for 256×256 images. The inner 192×192 is measured; 16×16 nested patches give 144 patch errors per image, while the source remains the independent unit of later inference.
- The periodic Gaussian acquisition blur, `sigma=1.6`, shares the Fourier transfer used in the Stage 05 DPIR inverse and the adapted DiffPIR analytic projection. Both solvers assume the same nominal `sigma=1.0`. The JPEG and linear-light branches share the same source-specific random noise field. This matched-operator development configuration differs from the earlier reflective-edge 06C acquisition smoke; do not pool their pixel error numbers.
- Each chain × solver pair has nominal and chain-aware arms. The aware arm uses the existing pinned FBCNN model for JPEG preprocessing; for the linear-light chain only, it also inverse-transfers the observation to linear RGB before deblurring and transfers the reconstruction back for scoring. No true blur, clean reference or quality parameter is supplied to a reconstruction model.

## DiffPIR checkpoint and results

The notebook checks out DiffPIR at commit `2a9898129a1b274131b98746e5b364bc20adc1e1`, downloads the model from the [official model-zoo link](https://openaipublic.blob.core.windows.net/diffusion/jul-2021/256x256_diffusion_uncond.pt) if needed, and records its observed byte count and SHA-256. It uses **ImageNet**, because the upstream deblur demo defaults to a face prior. The digest is a record of downloaded bytes; it is not a publisher-signed value or a final training-overlap clearance. The run rejects a changed checkpoint after its first receipt. The Stage 05 DPIR and FBCNN weights are independently checked against their verified hashes.

The DiffPIR loop retains the upstream class-unconditional model architecture, time schedule and predictive prior, but replaces the demo's sampled 61×61 blur kernel in its analytic projection with the **same periodic Gaussian Fourier transfer as DPIR**. The timestep is supplied directly to the upstream `diffusion.p_sample` call to avoid the demo helper's NumPy conversion of a GPU tensor. `NFE=20`, `lambda=1`, and `zeta=0.1` are canary settings, not final Stage 06 values. The model's own sampling randomness is seeded identically for the paired arms. Source-level RGB MSE, centre detail MSE/RMSE, the 144 nested patch errors, timing, input/output hashes, solver/chain/method labels, and failure receipts are saved to a fresh run directory in the user's project Drive.

## Validation so far

- Notebook JSON validated and six Python code cells syntax-checked; the Colab `%pip` directive was excluded from the Python compiler check.
- Runner `--mode preflight` decoded and rehashed the three available audited RAISE NEFs. Attempts to pass an independent-test ID or one of the six duplicate-excluded IDs were rejected before image decoding.
- An offline operator canary confirmed deterministic JPEG observations, different sRGB/linear-light chains, and exactly zero detail error when reference equals reconstruction.
- **GPU inference has not been executed here** because no DiffPIR checkpoint or CUDA runtime exists in this workspace. After Colab execution, inspect `status.json` and `source_method_rows.json`; a partial or failed run must not be called complete. Inspect the actual paired differences before changing any development setting, and freeze all settings before independent testing.

The next research steps are the first GPU canary, broader development-fit and early-stop solver runs, and source-level analysis. The 06B checkpoint-training provenance issue still requires an explicit pre-freeze decision. Stage 06D, 06E, 06F and manuscript synthesis remain separate future gates.
