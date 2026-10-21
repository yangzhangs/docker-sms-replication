# Replication Package

Data, process records, and analysis scripts for the systematic mapping study.

Search window: **2014-01-01 through 2026-09-30**.  
Final corpus: **92 primary studies**. 

This package is organized around the three research questions. `common/`
contains the search, screening, corpus, extraction, and cross-RQ material. `RQ1/`,
`RQ2/`, and `RQ3/` contain the data and scripts behind the corresponding results.
`common/extraction/data_dictionary.md` defines the data fields.

## Directory map

```text
common/
  protocol/                  Search protocol, inclusion/exclusion review, screening notes
  search/                    Search log, top-500 Google Scholar saturation data, and saturation figure
  screening/                 Screening flow, per-criterion exclusions, dual-coding worksheets,
                             page-count re-screening data, Kappa report
  corpus/                    corpus_92.csv and the complete PDF metadata index
  extraction/                Final extraction, coding manual, ledger, reliability report
  tables/                    Cross-RQ result data, including Table IX research agenda
  figures/                   Figure 2 (selection) and Figure 3 demographic panels
  scripts/                   Corpus/figure builders and package validation

RQ1/
  data/                      Table III matrix, seven-topic summary, concern/object summaries,
                             and year-by-concern/object counts
  figures/                   Figure 4 temporal heatmap
  scripts/                   Rebuilds all RQ1 tables from the final extraction

RQ2/
  data/                      Tables IV-VII, contribution/combination summaries, artifact summary
  scripts/                   Validates and summarises the RQ2 tables

RQ3/
  data/                      Table VIII categories/subcategories and subcode evidence
  scripts/                   Validates the taxonomy against the extraction master
```

`MANIFEST.csv` records byte sizes and SHA-256 checksums for every distributed file.
PDF payloads are **not** distributed; see the PDF policy below.

## Paper-to-package map

| Paper item | Package file |
|---|---|
| Fig. 2 selection flow | `common/figures/fig2_selection.pdf`; counts in `common/screening/screening_flow.csv` |
| Fig. 3 demographics | `common/figures/fig3_demographics/plots0.pdf` ... `plots6.pdf`; ledger in `common/extraction/study_ledger.csv` |
| Table I positioning | No data export; a narrative comparison of secondary studies |
| Table II extraction schema | `common/extraction/coding_manual.md` |
| Table III topic map | `RQ1/data/table_iii_mapping.csv` |
| Table IV contributions | `RQ2/data/table_iv_contributions.csv` |
| Table V datasets | `RQ2/data/table_v_datasets.csv` |
| Table VI tools | `RQ2/data/table_vi_tools.csv` |
| Table VII taxonomies | `RQ2/data/table_vii_taxonomies.csv` |
| Table VIII challenges/limitations | `RQ3/data/table_viii_categories.csv` |
| Table IX research agenda | `common/tables/table_ix_research_agenda.csv` |
| Cross-study tensions (Sec. V) | `common/tables/cross_study_tensions.csv` |
| Fig. 4 temporal heatmap | `RQ1/figures/fig4_temporal_heatmap.pdf`; counts in `RQ1/data/temporal_counts.csv` |

The seven dominant RQ1 topics are listed in
`RQ1/data/table_iii_topic_summary.csv`: SM 38, IS 20, SP 13, IM 11, BR 10, BP 10,
and PI 10. Their union covers 74 of the 92 studies.

## Key counts

- Corpus: **92 studies**; 89 from the five-library searches and short-paper
  re-screening, plus 3 from snowballing.
- Screening: 4,382 records identified; 3 identical exports merged; 652 non-archival
  records removed by the automatic bibliographic filter; **3,727 records**
  independently dual-labeled; 135 retained records; 89 studies after de-duplication;
  3 snowballing additions; **92 final studies**.
- Reporting: 50 replication packages, 24 datasets, 38 tools from 36 studies,
  10 taxonomies, 25 challenge/limitation subcategories.
- Kappa: screening 0.872 (multi-class) / 0.707 (binary) over N = 3,727;
  extraction dimensions average 0.938 (see `common/extraction/reliability_and_summary.txt`).

## PDF policy

The public repository does **not** contain article PDFs, to respect publisher
copyright. `common/corpus/pdf_index.csv` is the complete information table:

- one row for each of the 92 active studies;
- `P`, Zotero key, title, year, venue, DOI, public URL, and publisher;
- `local_pdf_available`, `pdf_filename`, `pdf_bytes`, and `pdf_sha256` for every
  local copy used during the study;

The 36 local copies are retained only on the authors' machines for verification.
All 92 studies have a bibliographic record and, where available, a DOI URL in the table.

## Reproduction

Requirements: Python 3.10+ and PyMuPDF for the vector figure scripts.

```bash
python -m pip install -r requirements.txt

# Cross-RQ corpus table and PDF-index check
python common/scripts/build_corpus_tables.py

# RQ1 tables
python RQ1/scripts/build_rq1_tables.py

# RQ2 checks and summaries (uses the final Table IV-VII CSVs)
python RQ2/scripts/build_rq2_tables.py

# RQ3 taxonomy checks and summaries
python RQ3/scripts/build_rq3_tables.py

# Figures
python common/scripts/make_demographic_figures.py
python common/scripts/regen_saturation_500.py

# Full package integrity check
python common/scripts/validate_package.py
```

The scripts use only files in this package. They re-check the counts quoted in the
paper and fail if a data table drifts from those counts.

## Google Scholar saturation

The paper reports the top 500 Google Scholar records screened by relevance. The
package table `common/search/google_scholar_top500_noncorpus_classification.csv`
has **213 rows**, not 500, because it contains only the top-500 records that are
not already covered by the corpus. The other 287 records were already in the
corpus and therefore required no manual classification. The five 100-record
segments are summarized in `common/search/gs_top500_saturation_segments.csv`;
the figure is `common/search/figures/gs_saturation.pdf`, generated by
`common/scripts/regen_saturation_500.py`.

## Search and screening data

`common/search/` retains the search log, the top-500 Google Scholar saturation
data and figure, and the rank-segment summary. `common/screening/`
retains the dual-coding worksheets, page-count re-screening data, and the
preliminary-screening Kappa report. The report includes a reference note for the
larger N = 4,379 corpus; the paper's reported statistic is the N = 3,727 one.

## Notes

- The paper's exclusion criterion uses archival status and a five-page minimum;
  the page-count re-screening data are in `common/screening/`.
- Contribution flags are the final post-audit flags. Dataset declarations include
  two shared build/issue collections; see
  `RQ2/README.md` and the extraction notes.
- `common/extraction/extraction_master_92.csv` contains the 92-study full corpus.
