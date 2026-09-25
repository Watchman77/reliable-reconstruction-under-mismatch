# Stage 06B RAISE-1k integrity and overlap review (25 September 2026)

Status: **source identity resolved; provenance gate pending**. This record uses source metadata, stored-file hashes, and visual review. No Stage 06 reconstruction outcome or independent-test performance was inspected. Stage 05 remains sealed.

## Evidence

The executed `06Ba_RAISE_1k_Integrity_Provenance_and_Overlap_Audit (1).ipynb` checked all 20 download receipt pairs, compared the 1,000 stored NEF files (18,298,872,365 bytes) to their recorded SHA-256 digests, and decoded every RAW using repository commit `7b682f75fbcd46b885cebba5f3a7272e0f13311a`. Renderer script SHA-256: `0867eafaa99cc7e4e15bd9ca05594eb4df3e5a20a0619237b93d04ef00f85bbe`; environment: Python 3.13.15, rawpy 0.27.1, Pillow 11.3.0, numpy 2.1.3, pandas 2.2.3. The Stage 05 identity reference comprised 100 DIV2K development and 40 TESTIMAGES independent originals with verified archive/file hashes.

Audit artifacts are in the project Drive folder `results/stage06b_external_audit/`: `external_source_audit.csv` (SHA-256 `b33e76252c40c14416e8dfbe944404413cdd76e8d5696df566596ffa80335dec`), `external_overlap_pairs.csv` (SHA-256 `7a54f41c976e686b1c206175b477fa0593af4917ad310fd14bb0bb3dfded2416`), `external_audit_summary.json`, and `export_manifest.json`. The original public role manifest has SHA-256 `fa4fe1272edae7f18e6d831d4e5878433413e26afe38997c15b4a7cd7ff77bf7`. The Drive role manifest intentionally includes download URLs and has a different SHA-256; do not publish that URL-bearing copy.

The 14 overlap rows represent **six unique exact-duplicate pairs** reported by both file and decoded-RGB hashes, plus **two perceptual candidates**. The six pairs and their deterministic keep/exclude decisions are in `experiments/stage06/manifests/RAISE_1k_overlap_decisions_v1_20260925.csv`. Prefer calibration or early-stop over fit if a duplicate crosses roles; within one role retain the lexically first source ID. All six decisions use the source-only audit. Three exact pairs cross roles; none includes external pilot or independent test.

The two dHash-distance-3 candidates connect three early-stop sources. Reduced previews of the original NEFs were inspected: `r03d2a758t` shows a backlit church window, `r137bcd7at` a patterned domed ceiling, and `r1a5903fct` a sunset over water. These are distinct scenes; both candidate alerts are false positives. No RAISE-versus-Stage 05 exact or dHash-near pairs were reported by this screen. This method cannot exclude all cropped/altered-image or pretrained-data overlaps.

The original 1,000-source manifest and stored files are unchanged. The versioned eligible-role manifest contains **994 sources**: development fit 495, early-stop 150, calibration 149, external pilot 50, independent test 150. Its SHA-256 and the hashes of all inputs and the ledger are recorded in `RAISE_1k_eligibility_receipt_v1_20260925.json`. Use this eligible manifest as the **source allowlist** in every later Stage 06 data loader. A loader must fail if an excluded ID appears; retaining the original file or role record does not make it eligible. Further exclusions need a documented v2 manifest made before relevant outcomes are inspected.

To reproduce the versioned manifest after obtaining the three Drive audit files and original public manifest:

```bash
python scripts/build_stage06b_eligibility.py \
  --original experiments/stage06/manifests/RAISE_1k_source_roles_seed_20260925.csv \
  --audited /path/to/external_source_audit.csv \
  --overlaps /path/to/external_overlap_pairs.csv \
  --decisions experiments/stage06/manifests/RAISE_1k_overlap_decisions_v1_20260925.csv \
  --eligible /path/to/RAISE_1k_eligible_roles_v1_20260925.csv \
  --receipt /path/to/RAISE_1k_eligibility_receipt_v1_20260925.json
```

Compare the regenerated outputs' SHA-256 values with the committed eligibility receipt. The builder rejects changed original manifests or audit evidence, unreviewed overlap categories, invalid pair decisions, retained exact duplicates, and role-count changes.

## Provenance still required

- RAISE's [official download page](https://loki.disi.unitn.it/RAISE/download.html) and [guide](https://loki.disi.unitn.it/RAISE/guide.html) describe RAISE-1k, limit use to non-commercial research/education, and require citation of Dang-Nguyen et al., *RAISE — A Raw Images Dataset for Digital Image Forensics*, ACM MMSys 2015. Record retrieval date/access conditions and avoid redistributing NEFs. The official CSV manifest ZIP SHA-256 is `2bf21449ed458502c09407cd9260b5d91fe27e7bc9e98f33bd108bbd8e40f8dc`.
- Identify the actual checkpoints and training datasets for each proposed pretrained solver and assess whether RAISE images could be present. This cannot be inferred from the Stage 05 overlap screen.
- Keep the RAW renderer and colour settings in the Stage 06E freeze. Perform the source-level sample-size calculation before deciding that 150 independent sources suffice.

**Do not declare 06B clear or open independent outcomes** until model-training provenance and all remaining source/licence documentation are resolved. Do not silently use the 1,000-row original role file for modeling.
