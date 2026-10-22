# Replication Package

Data, process records, and analysis scripts for the systematic mapping study.

Search window: **2014-01-01 through 2026-09-30**.  
Final corpus: **92 primary studies**.

The package presents one final 92-study corpus. `common/` contains the search,
screening, corpus, extraction, and cross-RQ material. `RQ1/`, `RQ2/`, and `RQ3/`
contain the data and scripts behind the corresponding results.

## Directory map

```text
common/
  protocol/                  Search protocol and inclusion/exclusion criteria
  search/                    Search log, top-500 Google Scholar saturation data and figure
  screening/                 Screening flow, exclusion reasons, dual-coding worksheets,
                             page-count re-screening, and Kappa report
  corpus/                    corpus_92.csv and the 92-study PDF metadata index
  extraction/                Extraction master, coding manual, data dictionary, ledger,
                             reliability report, and Kappa tables
  tables/                    Cross-RQ result data, including Table IX and tensions
  figures/                   Figure 2 selection flow and Figure 3 demographic panels
  scripts/                   Corpus, figure, Kappa, and package-validation scripts

RQ1/
  data/                      Table III matrix, topic summaries, gap summary, temporal counts
  figures/                   Figure 4 temporal heatmap
  scripts/                   Rebuilds all RQ1 tables

RQ2/
  data/                      Tables IV-VII, contribution/combination summaries, artifact summary
  scripts/                   Validates and summarises the RQ2 tables

RQ3/
  data/                      Table VIII categories/subcategories and summaries
  scripts/                   Validates the taxonomy against the extraction master
```

`MANIFEST.csv` records byte sizes and SHA-256 checksums for every distributed file.
PDF payloads are not distributed.

## Paper-to-package map

| Paper item | Package file |
|---|---|
| Fig. 2 selection flow | `common/figures/fig2_selection.pdf`; counts in `common/screening/screening_flow.csv` |
| Fig. 3 demographics | `common/figures/fig3_demographics/plots0.pdf` ... `plots6.pdf`; ledger in `common/extraction/study_ledger.csv` |
| Table I positioning | No data export; narrative comparison in the manuscript |
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

## Key counts

- Corpus: **92 studies**; 89 from the five-library searches and short-paper
  re-screening, plus 3 from snowballing.
- Screening: 4,382 records identified; 3 identical exports merged; 652 non-archival
  records removed by the automatic bibliographic filter; **3,727 records**
  independently dual-labeled; 135 retained records; 89 studies after de-duplication;
  3 snowballing additions; **92 final studies**.
- Reporting: 50 replication packages, 24 datasets, 38 tools from 36 studies,
  10 taxonomies, 25 challenge/limitation subcategories.
- Screening Kappa: 0.872 (multi-class) and 0.707 (binary) over N = 3,727.
- Extraction Kappa: 0.683 SE concern, 0.865 Docker object, 0.696 contribution
  type, 0.586 challenge, 0.488 limitation; average 0.664.

## Common data

### Corpus and PDF policy

`common/corpus/corpus_92.csv` has one row per study with P number, Zotero key,
title, year, venue, DOI/URL, publisher, CORE rank, first-author country,
contribution flags, and PDF availability.

The public repository does not contain article PDFs. `common/corpus/pdf_index.csv`
is the complete information table for the 92 studies:

- `P`, Zotero key, title, year, venue, DOI, public URL, publisher;
- `local_pdf_available`, `pdf_filename`, `pdf_bytes`, and `pdf_sha256` for local copies.

There are 36 local copies and 56 metadata-only records. Local copies remain on the
authors' machines for verification.

### Screening

`common/screening/` contains:

- `screening_flow.csv` and `exclusion_reasons.csv`: selection counts.
- `screening_worksheet.csv`: dual-coded preliminary-screening records.
- `increment_screening_coded.csv`, `snowballing_candidates_coded.csv`: dual-coded
  update-search and snowballing candidates.
- `short_paper_rescreen.csv`, `short_paper_additions.csv`,
  `short_paper_verification.csv`: page-count re-screening.
- `page_count_verification_sample.csv`: 40-record page-count verification sample.
- `kappa_report_preliminary_3727.txt`: the reported screening Kappa.

The report includes a reference note for the larger N = 4,379 corpus; the paper's
reported statistic is the N = 3,727 one.

### Extraction

`common/extraction/extraction_master_92.csv` contains 92 rows and 34 columns:
paper ID, authors, title/year/venue, DOI/publisher/country/CORE/author type,
RQ1-RQ3 codes, artifact details, and independent coder A/B labels. The 50 studies
with a dataset, tool, or taxonomy have artifact details.

Other files:

- `coding_manual.md`: category and subcategory definitions.
- `data_dictionary.md`: field-level data dictionary.
- `study_ledger.csv`: demographic and bibliographic ledger.
- `demographic_statistics.md`: demographic statistics used in the paper.
- `reliability_and_summary.txt`: reliability and coded distributions.
- `kappa_by_dimension.csv`, `kappa_by_label.csv`: label-level reliability results.

### Search and Google Scholar saturation

`common/search/search_log.csv` records library-level queries, fields, date filters,
and hit counts. The top-500 Google Scholar screen has 500 records: 213 were not
already in the corpus and are listed in
`google_scholar_top500_noncorpus_classification.csv`; the other 287 were
corpus-covered. `gs_top500_saturation_segments.csv` gives the five 100-record
segments, and `figures/gs_saturation.pdf` shows the saturation curve.

## RQ1: Research topics

- `RQ1/data/table_iii_mapping.csv`: all 24 concern-object cells with P lists and counts.
- `RQ1/data/table_iii_topic_summary.csv`: the seven dominant topics: SM 38, IS 20,
  SP 13, IM 11, BR 10, BP 10, PI 10; union = 74 studies.
- `RQ1/data/rq1_concern_summary.csv`, `rq1_object_summary.csv`: unique studies and P lists.
- `RQ1/data/temporal_counts.csv`: concern/object counts by year, source for Fig. 4.
- `RQ1/data/rq1_gap_summary.csv`: empty cells, sparse cells, dense cells, and
  recent-year runtime figures.

`python RQ1/scripts/build_rq1_tables.py` rebuilds these tables and checks 21 of 24
populated cells, the concern/object counts, and the 74-study seven-topic union.

## RQ2: Research contributions

- `RQ2/data/table_iv_contributions.csv`: 92 studies and six contribution flags.
- `RQ2/data/table_v_datasets.csv`: 24 datasets with source, size, timestamp, and link status.
- `RQ2/data/table_vi_tools.csv`: 38 tools from 36 studies, with primary/supporting type.
- `RQ2/data/table_vii_taxonomies.csv`: 10 taxonomies with category counts.
- `RQ2/data/rq2_contribution_summary.csv`: type counts, percentages, and
  declared-but-unverified counts.
- `RQ2/data/rq2_combination_summary.csv`: 1-5 type distribution plus insight+approach,
  artifact+analysis, and single-type details.
- `RQ2/data/rq2_artifact_summary.csv`: dataset/tool/taxonomy metrics and link status.

The final flags give 50 replication packages, 24 datasets, 55 approaches, 36 tool
studies (38 tools), 10 taxonomies, and 67 insight studies. The distribution is
17/26/30/12/7 for one through five contribution types. The 24 datasets comprise
22 Docker-artifact corpora plus two shared build/issue collections retained for
continuity with the earlier submission.

`python RQ2/scripts/build_rq2_tables.py` validates and rewrites the three summary CSVs.

## RQ3: Challenges and limitations

- `RQ3/data/table_viii_categories.csv`: 32 rows (7 categories and 25 subcategories).
- `RQ3/data/rq3_category_summary.csv`: category counts and subcategory counts.
- `RQ3/data/rq3_subcategory_summary.csv`: subcategory counts and P lists.

Category counts are C1 71, C2 18, C3 31, C4 19, L1 53, L2 35, L3 59.
`python RQ3/scripts/build_rq3_tables.py` verifies subcategory P lists against the
extraction master and checks that each category is the union of its subcategories.

## Reproduction

Requirements: Python 3.10+ and PyMuPDF for vector figures.

```bash
python -m pip install -r requirements.txt

python common/scripts/build_corpus_tables.py
python RQ1/scripts/build_rq1_tables.py
python RQ2/scripts/build_rq2_tables.py
python RQ3/scripts/build_rq3_tables.py
python common/scripts/make_demographic_figures.py
python common/scripts/regen_saturation_500.py
python common/scripts/compute_extraction_kappa.py
python common/scripts/validate_package.py
```

The scripts use only files in this package and fail when a reported count drifts.

## Notes

- The exclusion criterion uses archival status and a five-page minimum; the
  page-count re-screening data are in `common/screening/`.
- Contribution flags are the final post-audit flags.
- `common/extraction/extraction_master_92.csv` contains the 92-study full corpus.
- Kappa values were recomputed after the second independent coding of the 55
  retained studies. Challenge and limitation agreement is lower than for concerns,
  objects, and contributions; the paper reports the recomputed values.
