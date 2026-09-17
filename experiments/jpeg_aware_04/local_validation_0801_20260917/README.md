# Source-0801 local execution evidence

This folder is a curated repository copy of the local run's tables, figures, metadata and exact executed notebook. It omits the large predictions and codec-input directories. The original `export_manifest.json` describes the complete raw run, not this curated folder; the executed notebook and export receipt are additional checkpoint evidence.

For full saved-array readback, extract the raw archive identified by `export_receipt.json` and run `scripts/validate_jpeg_aware_04.py` against that extracted run and the original source PNGs. The complete raw archive is preserved separately. The main notebook under `notebooks/` is the clean four-source Colab version; this executed notebook is historical one-source CPU evidence before the documented Colab bootstrap/description adjustments.
