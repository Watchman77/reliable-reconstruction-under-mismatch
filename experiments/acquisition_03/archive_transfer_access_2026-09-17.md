# Acquisition 03: archive access and transfer helper

**Resolved:** the five transfer parts were subsequently received and the [complete raw archive audit passed](archive_verification_20260917/verification.md). No additional transfer is needed for this run. The account below records the earlier access problem and its remedy.

17 September 2026. The user supplied the dated Drive folder after two chat ZIP uploads failed to become accessible. Neither failed upload was read.

## Confirmed access

- [Result folder](https://drive.google.com/drive/folders/1tgf-S722lWgQO0EYe46k0lBhXUZnUGAb) is accessible for listing.
- Its parent listing identifies the [original ZIP](https://drive.google.com/file/d/1-BboXfpZbGEHtIVqA-JSjskjqJfvf7KN/view), `acquisition_03_20260917T160754_303637Z.zip`, as `application/zip`, 431,278,719 bytes, and the [receipt file](https://drive.google.com/file/d/1FzRFFvzNsIByom30R6jV32VZ5ZiTf6ZV/view). Receipt contents were not retrieved in this access attempt.
- Canonical raw ZIP fetch with streaming requested failed with HTTP 413: 431,278,719 bytes exceeds the connector's 268,435,456-byte limit (256 MiB).
- A canonical streamed fetch of the 6,234-byte export manifest returned a file reference, but retrieval of its bytes returned HTTP 403. No bearer URL is retained in this report.

Metadata visibility is not raw-byte verification. The 38 manifest file hashes and 48 saved learned model images remain independently unverified. The prior CSV/notebook review remains the completed evidence checkpoint.

## Transfer utility

[03A_Package_Existing_Acquisition_Results.ipynb](../../notebooks/03A_Package_Existing_Acquisition_Results.ipynb) is self-contained and uses the Python standard library plus Colab's Drive mount. It reads the existing large ZIP, validates its recorded size and SHA-256, and produces five ordinary ZIPs using 96 MiB byte segments. Each output is under 100 MiB, includes its segment index/hash, and participates in a full-stream readback that checks the original archive SHA-256. These are numbered byte segments, not standalone experiment datasets; all five are required to reconstruct the archive.

The original receipt values come from the saved Notebook 03 Section 10 output: 431,278,719 bytes and SHA-256 `902cee988b76eb982efb068eca4c821d0259b4ef06d6c6f0d09163d1117549dc`. They remain expected values until the archive is independently received. The helper stops on a mismatch instead of accepting a different archive.

Each execution creates a separate dated folder under the existing Drive results directory. No source files, numerical settings, old outputs or old archives are modified. No model inference, training, new measurements or metric recomputation occurs.

User steps: open the notebook in Colab, run all cells, authorize Drive, wait for `PASS`, then download and upload each of the five generated ZIPs individually. Downloading the entire output folder as one ZIP would recreate the size problem. The optional transfer receipt is redundant with the metadata in each part.

## Local validation and remaining execution gap

The packaging helper was tested against the prior 107,609,950-byte local archive using the same default 96 MiB chunk size. Its two produced parts reassembled byte for byte, matched the original SHA-256, and passed archive CRC checks. Missing parts, duplicate parts, corrupted chunk content and an incorrect original hash were rejected. The notebook schema and every code cell compile successfully; its embedded helper is byte-identical to the standalone script.

See [validation JSON](transfer_helper_validation_2026-09-17.json) and [script](../../scripts/package_acquisition_03_archive.py). The delivered notebook has no fabricated execution outputs. Its Drive mount and full 431 MB Colab archive path have not been executed here. Run all cells in Colab to validate that environment and create the transfer parts. This preparation does not close the outstanding scientific raw-data verification.
