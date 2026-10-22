# Data dictionary

## `extraction_master_92.csv`

One row per primary study. Coded fields use `;` as the multi-label separator.

| Field | Meaning |
|---|---|
| `P` | Paper ID used in the manuscript |
| `zotero_key` | Stable Zotero item key used to join tables |
| `authors`, `title`, `year` | Bibliographic metadata |
| `venue_type`, `venue_name` | Publication venue |
| `doi`, `publisher`, `country`, `core`, `author_type` | Bibliographic and demographic metadata |
| `concerns` | RQ1 SE concerns |
| `objects` | RQ1 Docker objects |
| `rep_package`, `dataset`, `approach`, `tool`, `taxonomy`, `insight` | RQ2 contribution types (`Y`, `broken-link`, or empty) |
| `artifact_details` | Dataset, tool, and taxonomy names with link/type status, generated from Tables V-VII |
| `challenges`, `limitations` | RQ3 categories and subcategories |
| `research_method` | Method label, where recorded |
| `concerns_A/B`, `objects_A/B`, `contrib_A/B`, `challenges_A/B`, `limitations_A/B` | Independent coder labels, where recorded |

Blank cells mean that the field was not recorded for that study; they are not
negative labels. The artifact-details field is populated for the 50 studies with
a dataset, tool, or taxonomy. All 92 studies have independent coder A/B labels for
concerns, objects, contribution types, and challenges; limitation labels are empty
only when the study reports no limitation. `research_method` is populated where
recorded.

## `study_ledger.csv`

One row per study with `P`, bibliographic and demographic fields, and the final
topic/contribution/challenge/limitation codes.

## `corpus_92.csv`

One row per study with P number, Zotero key, title, year, venue, DOI/URL, publisher,
CORE rank, first-author country, and contribution flags.

## `pdf_index.csv`

One row per study with P number, Zotero key, title, year, venue, DOI, public URL,
and publisher. It is a bibliographic index only: no PDF payloads, local filenames,
file sizes, or checksums are distributed.

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
