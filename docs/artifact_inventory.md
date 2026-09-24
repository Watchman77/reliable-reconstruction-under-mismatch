# Research artifact inventory

This index distinguishes reproducible repository assets from large raw archives. The repository is the authoritative location for code, clean notebooks, small result tables, figures, manifests, checksums, and verification receipts. Raw datasets, model weights, executed notebooks, and large ZIP/NPZ bundles are retained outside ordinary Git history and are identified by hashes in committed receipts.

## Experimental stages

| Stage | Canonical implementation | Committed evidence | Raw-artifact status |
| --- | --- | --- | --- |
| Phase-0 classical canary | `experiments/phase0_canary/pilot.py` | `experiments/phase0_canary/CANARY_RESULT.md` and compact outputs | Compact results committed |
| 00 four-source Colab pilot | `notebooks/00_DIV2K_Operator_Mismatch_Pilot.ipynb` | `experiments/colab_pilot_00/saved_run_review.json` | Executed notebook/raw export retained externally |
| 01 classical baseline | `experiments/baseline_01/baseline.py` | Reproducible implementation | No separate notebook required |
| 02 learned baseline | `experiments/learned_02/learned.py` | Reproducible implementation | Model weights excluded |
| 03 acquisition diagnosis | `experiments/acquisition_03/diagnostic.py` | Reproducible implementation | No separate notebook required |
| 04 JPEG-aware baseline | `notebooks/04_DIV2K_JPEG_Aware_Baseline.ipynb` and `experiments/jpeg_aware_04/` | `results/jpeg_aware_04_20260917T201107_721467Z/` and `docs/jpeg_aware_04_verified_checkpoint.md` | Large multipart ZIP retained externally |
| 05A protocol/data audit | `notebooks/05A_Independent_Validation_Protocol_Audit.ipynb` | Protocol, freeze receipt, data receipt and duplicate audit in `experiments/independent_05/` | Raw dataset archives excluded |
| 05C engineering canary | `notebooks/05C_Independent_Validation_Engineering_Canary.ipynb` | `canary_readback_receipt.json` and amendment 0001 | Raw canary ZIP/executed notebook retained externally |
| 05C1 development generation | `notebooks/05C1_Development_Reconstruction_Shards.ipynb` | Per-shard receipts and `development_shard_registry.json` | Shard ZIPs retained externally |
| Independent held-out evaluation | Frozen by `protocol_freeze.json` | No test result exists | Unauthorized until the explicit transition gate passes |

## Current 05C1 checkpoint

- Verified development shards: **6 of 12**.
- Shard 00: DIV2K `0805`–`0812`, **56 of 56** observations; receipt `experiments/independent_05/development_shard_00_readback_receipt.json`; received ZIP SHA-256 `4b7a011a4300417104278e673a2e61eb4a301f776a95a96259cafcecb25ea608`.
- Shard 01: DIV2K `0813`–`0820`, **56 of 56** observations; receipt `experiments/independent_05/development_shard_01_readback_receipt.json`; received ZIP SHA-256 `2e26fcd21b96a5a3360708f989f097c92c451360504cd318fe4e5c46ba63dc0d`.
- Shard 02: DIV2K `0821`–`0828`, **56 of 56** observations; receipt `experiments/independent_05/development_shard_02_readback_receipt.json`; received ZIP SHA-256 `54da48f2ee8658d5d2c8107aba54dfe6cb638cda62301585f0e929debcabb421`.
- Shard 03: DIV2K `0829`–`0836`, **56 of 56** observations; receipt `experiments/independent_05/development_shard_03_readback_receipt.json`; received ZIP SHA-256 `a63d8b69082a3b00e7e485363a73f96e4860919f11bcf30c7f300fd0bb58ef79`.
- Shard 04: DIV2K `0837`–`0844`, **56 of 56** observations; receipt `experiments/independent_05/development_shard_04_readback_receipt.json`; received ZIP SHA-256 `50428120c6b755cb246b701d4e7fbd779addf54ab94127c86e1961e735476bd6`.
- Shard 05: DIV2K `0845`–`0852`, **56 of 56** observations; receipt `experiments/independent_05/development_shard_05_readback_receipt.json`; received ZIP SHA-256 `3667e151faafd668019fa44e51e7ffc72090fc7c744047d9ae1837dcc5ca39f7`.
- Shards 01, 02, 04 and 05 have recorded outer-ZIP mismatches against notebook-reported SHA-256 values (`974aaa068a8d17f3ef554d0e88db4a5fe2a8d29d065a864016bb322e03b65681`, `e13fd2c6a9d24b0dc75d24b42274a771ba3840da150cde3ecfa1831a26506aee`, `77aa6243e100ccafcacb7abfa2a243870d489de9f75b3b40a414936427374fb3` and `228451c2f170d23615cde448ed55c3f37f8ab224ca401ab922d4fbecfe2a24ff`); all 124 internal files in each shard matched its export manifest. Shard 03 also matched all 124 internal files, but no executed notebook was received for an outer-hash comparison.
- Independent test inference remains **not authorized** and **not performed**.

## Notebook policy

Clean, self-contained notebooks are committed when a notebook is the canonical execution interface. Stages 01–03 are canonical Python modules rather than missing notebook deliverables. Exact executed notebooks are retained externally when their stored outputs materially increase size or expose environment-specific metadata; committed verification records preserve the execution evidence.

The received executed 05C canary notebook is 390,597 bytes with SHA-256 `2ee9ce03d9de8fc1448a7bf7bd669a33122a27cedcc08bece3f8b838c6c50180`; all seven code cells were executed and no error output was present. The clean canonical notebook remains the committed version. An executed 05C1 notebook was not received with shard 00, but the returned raw shard archive was independently verified. The executed shard 01 notebook was received and checked: 387,549 bytes, SHA-256 `f22dd026f06354fe13abc64abfddc37c4e5e412ab93942470f013dfbbdf50d61`, seven of seven code cells executed, and zero error outputs. The executed shard 02 notebook was also checked: 387,654 bytes, SHA-256 `e50b1ff27cab8fed9f1c1656b91487e54962c4d3c4e7c6d2744b285e675f8127`, seven of seven code cells executed, and zero error outputs. An executed shard 03 notebook was not received; its raw shard archive nevertheless passed independent payload verification. The executed shard 04 notebook was checked: 387,654 bytes, SHA-256 `47409d04eaf869f3fe4a3c9d5fa6ecb2050773823a44d2fa095b8ba5cec5417d`, seven of seven code cells executed, and zero error outputs. The executed shard 05 notebook was checked: 387,654 bytes, SHA-256 `58dbe2f7b4608ecd1ecf6f723c62ba7ea0e10de4643daa155938733c68458f63`, seven of seven code cells executed, and zero error outputs.

## Raw-artifact policy

Do not commit downloaded datasets, pretrained weights, raw ZIP archives, or large per-observation arrays to ordinary Git history. For every accepted external result archive, commit:

1. its SHA-256 and byte count;
2. its internal manifest verification result;
3. the relevant row, record and tensor counts;
4. the test-data firewall state;
5. the validator path and any limitations.

This preserves reproducibility and auditability without turning the source repository into binary storage.
