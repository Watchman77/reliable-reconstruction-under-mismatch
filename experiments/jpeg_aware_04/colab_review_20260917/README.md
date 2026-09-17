# Notebook 04 Colab review evidence

Read the [scientific review](../colab_execution_review_2026-09-17.md) and [machine-readable audit](audit.json). This is a curated review directory, **not the complete raw export**.

The 14 CSVs, seven result JSONs and four PNGs match 25 entries of `export_manifest.json`. The PNGs were extracted from the uploaded notebook and are byte-identical to the listed exports. All four were visually inspected. Eight original HTML tables are retained; seven result tables were reconciled numerically, while the remaining table describes the frozen design budget. The original notebook is preserved as the user attachment identified by SHA-256 in the audit; `notebook_execution_record.json` is an explicitly partial extraction, not a replacement original.

Derived comparison CSVs and `audit.json` are review outputs, not members of the original export manifest. The Drive file index contains observed file metadata and locations, without temporary download URLs. Eight NPZ predictions and four original JPEG streams are missing here. Streamed raw-part download returned HTTP 403. No neural inference or fresh learned-array readback was performed.

Run the review from repository root, supplying the original uploaded notebook and all four original source PNGs:

```bash
python scripts/review_jpeg_aware_04_colab.py --notebook /path/to/uploaded_notebook.ipynb --issued-notebook notebooks/04_DIV2K_JPEG_Aware_Baseline.ipynb --out experiments/jpeg_aware_04/colab_review_20260917 --repo . --data /path/to/source_pngs
```

Full raw verification requires all six existing parts from the exact dated Drive folder linked in the review. Do not run the complete-export validator against this partial evidence directory. Once the archive is available, use `scripts/validate_jpeg_aware_04.py` against its unmodified extracted run folder.
