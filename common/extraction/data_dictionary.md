# Data dictionary

## `extraction_master_92.csv`

One row per primary study. Coded fields use `;` as the multi-label separator.

| Field | Meaning |
|---|---|
| `zotero_key` | Stable Zotero item key used to join tables |
| `title`, `year`, `venue_type`, `venue_name` | Bibliographic metadata |
| `concerns` | RQ1 SE concerns |
| `objects` | RQ1 Docker objects |
| `rep_package`, `dataset`, `approach`, `tool`, `taxonomy`, `insight` | RQ2 contribution types (`Y` or empty) |
| `challenges`, `limitations` | RQ3 categories and subcategories |
| `research_method` | Method label |
| `concerns_A/B`, `objects_A/B`, `contrib_A/B`, `challenges_A/B`, `limitations_A/B` | Independent coder labels used for reliability |

## `study_ledger.csv`

One row per study with the bibliographic and demographic fields used by the paper:
title/year/venue, DOI, publisher, first-author country, CORE rank, author type,
and the final topic/contribution/challenge/limitation codes.

## `corpus_92.csv`

One row per study with P number, Zotero key, title, year, venue, DOI/URL, publisher,
CORE rank, first-author country, contribution flags, and PDF availability.

## `pdf_index.csv`

One row per study. `local_pdf_available=yes` means a local copy was used for verification;
`no` means the row has bibliographic metadata and, where available, a DOI URL.
`pdf_bytes` and `pdf_sha256` describe the local copy. No PDF payload is distributed.

## RQ data

- `RQ1/data/table_iii_mapping.csv`: concern, object, count, and semicolon-separated P list.
- `RQ1/data/table_iii_topic_summary.csv`: seven dominant topics and their P lists.
- `RQ1/data/temporal_counts.csv`: year × concern/object counts.
- `RQ2/data/table_iv_contributions.csv`: 92 studies and six contribution flags.
- `RQ2/data/table_v_datasets.csv`: dataset name, source platforms, size, timestamp, access link and status.
- `RQ2/data/table_vi_tools.csv`: tool name, purpose, type, access link and status.
- `RQ2/data/table_vii_taxonomies.csv`: taxonomy name, category counts and main categories.
- `RQ3/data/table_viii_categories.csv`: category/subcategory code, name, P list and count.

## Screening files

- `screening_flow.csv` and `exclusion_reasons.csv`: selection counts.
- `screening_worksheet.csv`: dual-coded preliminary-screening records.
- `increment_screening_coded.csv` and `snowballing_candidates_coded.csv`: dual-coded update and snowballing candidates.
- `short_paper_rescreen.csv`, `short_paper_additions.csv`, `short_paper_verification.csv`: page-count re-screening.
- `page_count_verification_sample.csv`: 40-record page-count verification sample.
- `kappa_report_preliminary_3727.txt`: reported screening Kappa.
