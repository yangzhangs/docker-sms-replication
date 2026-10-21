# Common data and process records

This directory contains the material shared by RQ1-RQ3 and the inputs to the
paper's selection flow.

## corpus/

- `corpus_92.csv`: one row per primary study with P number, Zotero key, title,
  year, venue, DOI/URL, publisher, CORE rank, selection channel, first-author country,
  contribution flags, and PDF availability.
- `pdf_index.csv`: PDF information table for the 92 studies (36 with a local
  copy, 56 metadata-only). `pdf_bytes` and `pdf_sha256` describe the local copies
  used during the study; no PDF payload is distributed.

`local_pdf_available=yes` means a copy existed on the authors' machine for
verification. `pdf_status=metadata_only_no_local_pdf` means the study has a
bibliographic record and DOI/URL but no local PDF in the curated set.

## screening/

- `screening_flow.csv`: the complete funnel used in Fig. 2.
- `exclusion_reasons.csv`: per-criterion counts that sum to 3,592.
- `auto_filtered_652_records.csv`: records removed by the automatic bibliographic filter.
- `kappa_report_preliminary_3727.txt`: the Kappa report reported in the paper.
- `screening_worksheet.csv`, `increment_screening_coded.csv`,
  `snowballing_candidates_coded.csv`: dual-coded screening worksheets.
- `short_paper_rescreen.csv`, `short_paper_additions.csv`,
  `short_paper_verification.csv`, `page_count_verification_sample.csv`: page-count
  re-screening and the 40-record verification sample.

The reported Kappa is the preliminary-screening statistic over N = 3,727
(multi-class 0.872; binary 0.707; 311 disagreements, 8.3%). The report includes a reference note for the larger N = 4,379
corpus; the paper's reported statistic is the N = 3,727 one.

## extraction/

- `extraction_master_92.csv`: final extraction for the full 92-study corpus.
- `study_ledger.csv`: demographic and bibliographic ledger for the 92 studies.
- `demographic_statistics.md`: demographic statistics used in the paper.
- `coding_manual.md`: coding definitions and subcategory rules.
- `reliability_and_summary.txt`: per-dimension extraction reliability and coded
  distributions.
- `data_dictionary.md`: field-level definitions for the extraction and result tables.

## search/

`search_log.csv` records the library-level queries, fields, date filters, and hit
counts. `google_scholar_rank_classification.csv` supports the saturation check.
The saturation figure is in `figures/`. Intermediate raw exports and dedup files
are not needed to reproduce the reported tables.

## tables/ and figures/

`table_ix_research_agenda.csv` is the data behind Table IX. `figures/` contains
the final Fig. 2 selection PDF and the Fig. 3 demographic panels. The Google
Scholar saturation figure is under `search/figures/`.

## scripts/

- `build_corpus_tables.py`: rebuilds `corpus/corpus_92.csv` from the ledger and
  checks the 92-study/36-local-PDF counts.
- `make_demographic_figures.py`: regenerates the Fig. 3 panels from the ledger.
- `regen_saturation_500.py`: regenerates the Google Scholar saturation curve.
- `venue_canon.py`: venue-name normalization used by the demographic figure script.
- `validate_package.py`: checks the screening flow, RQ table counts, PDF-index
  shape, and package-level consistency.
