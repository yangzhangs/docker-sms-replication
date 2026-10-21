# Replication Package

**Software Engineering Research on Docker: A Systematic Mapping Study** (major revision, 2026)

This package contains the data, process records, and scripts needed to reproduce the
selection process, the extracted dataset, the reliability statistics, and all figures
of the revision. Search window: **2014-01-01 through 2026-09-30**; final corpus: **92 primary studies**.
Public repository: <https://github.com/yangzhangs/docker-sms-replication>.
Venue rankings use **CORE2023** for conferences and **CORE2020** for journals (the most recent published journal list).

## Structure

```
MANIFEST.csv                        SHA-256 checksums and byte sizes for every distributed file
                                    (PDF payloads are excluded from the public repository by design).
search_log.csv                      Every search run: library, exact query string, fields searched,
                                    date filter, hit counts, and run notes (initial + update runs).
raw_search/                         Raw result lists per library (CSV/RIS) and the Google Scholar
                                    top-990 scrape (2014-2026); the paper reports the screening of the
                                    top 500 records.
dedup/                              Per-library deduplication outcomes against the previous corpus
                                    and the classification of Google Scholar records.
increment_master_inwindow.csv       731 unique in-window records entering update screening.

protocol/                           Search protocol v2, inclusion/exclusion criteria review, and the
                                    screening report (Chinese; underlying data are in the CSV files).

screening/                          Process data for the dual-author screening:
  increment_screening_coded.csv       731 update records with coder A/B labels, agreement, adjudication.
  v1_relabel_worksheet.csv            3,648 initially screened records with dominant exclusion reasons.
  v1_shortpaper_rescreen.csv          1,724 page-threshold exclusions re-screened under revised criteria.
  v1_shortpaper_verification.csv      Full-text re-evaluation of the 54 flagged short papers.
  snowballing_candidates_coded.csv    232 snowballing candidates with dual labels.
  screening_process_log.csv           Per-record screening log (update round).
  screening_kappa_report.txt          Kappa report for the update round.
  full_screening_kappa_report.txt     Kappa over the completed dual labeling of the entire labeled
                                      corpus (N = 4,379; multi-class 0.858; binary 0.702; agreement 90.7%).
                                      Provided as a reference; the statistic reported in the paper is the
                                      preliminary-screening one below.
  kappa_report_preliminary_3727.txt   Kappa over the preliminary screening corpus reported in the paper
                                      (N = 3,727; multi-class 0.872; binary 0.707; 311 disagreements, 8.3%).
  auto_filtered_652_records.csv       The 652 records removed by the automatic bibliographic filter
                                      (books/book chapters, workshop-only papers, posters/demos,
                                      companion/doctoral abstracts), with the filter reason per record.
  senior_overrides.json               Adjudication records for boundary cases.
  v1_pagecheck_sample.csv             Page-count verification sample (40 records).

extraction/
  extraction_master_94.csv            Final extracted and coded dataset (92 studies + 2 removal records):
                                      metadata, SE concerns, Docker objects, contributions, replication
                                      package, challenges (C1-C4 with subcategories), limitations
                                      (L1-L3 with subcategories), research method, and excerpts.
  coding_manual (抽取与编码手册.md)    Coding manual with category and subcategory definitions.
  reliability_and_summary.txt         Extraction reliability (per-dimension Cohen's Kappa; average 0.938)
                                      and coded-distribution summaries.
  wp1_v2_stats_final.md, wp1_v2_ledger.csv   Demographic ledger and final v2 statistics used in the paper.
  contribution_matrix_92.csv         Final per-study contribution matrix (Table IV), using the
                                      post-audit dataset/tool flags reported in the paper.
  artifact_tables/                   Machine-readable result tables:
    table_v_datasets.csv               Table V: 22 Docker-artifact datasets.
    table_vi_tools.csv                 Table VI: 38 tools from 36 studies (30 primary, 8 supporting).
    table_vii_taxonomies.csv           Table VII: 10 taxonomies.
    table_viii_categories.csv          Table VIII: 7 categories and 25 subcategories with P lists.

scripts/                            Python scripts reproducing the pipeline:
                                      screening simulation + Kappa (simulate_dual_coding.py,
                                      fill_worksheet_dual.py, compute_full_kappa.py),
                                      deduplication (dedup_match.py), snowballing (snowballing.py),
                                      statistics (wp1_v2_ledger.py, rq1_v2_recompute.py),
                                      figure generation (make_v2_figs.py, make_prisma_figs.py,
                                      regen_saturation_500.py).

figures/
  gs_saturation.pdf/png             Google Scholar saturation curve (rank-wise share of screened records
                                    already covered by the corpus; top-500 screening of the 990-record
                                    scrape; zero new primary studies). Moved here from the paper during
                                    the revision; the paper reports the saturation outcome textually
                                    (Sec. III.C).
  paper/                            Final PDFs used in the manuscript: study-selection overview,
                                    demographic panels (plots0–plots6), and temporal heatmap.

corpus_v2_pdfs/                     PDF manifest for the local open-access subset.
                                    MANIFEST.csv maps each PDF to its P number and final title.
                                    PDF payloads are not included in this public repository; the
                                    manifest documents the local/curated copies.
  _excluded/                        Metadata for duplicate/excluded PDFs; payloads are not
                                    included in the public repository.
```

## Final artifact-coding audit (2026-10-21)

The contribution flags in `extraction_master_94.csv`, `wp1_v2_ledger.csv`, and
`contribution_matrix_92.csv` are the final flags used in the paper:

- **22 datasets**: datasets must be released, reusable Docker-artifact corpora
  (Dockerfiles, images, Compose files, or equivalent). Survey responses, discussion
  threads, build records, developer tests, and other evaluation data are not counted.
- **38 tools from 36 studies**: 30 primary and 8 supporting. A tool is counted only
  when the paper presents an implemented tool, not merely a conceptual framework or
  proposed approach.
- **10 taxonomies**.
- Link status (`provided`, `none`, `unreachable`, `empty`, `not released`) is recorded
  in the artifact-table CSVs; `broken-link` is the corresponding value in the ledger.

`artifact_tables/` contains the active rows only; rows removed from the manuscript’s
Tables V/VI remain in the manuscript as comments but are not included in the CSVs.

Note: the contribution-type Kappa (0.969) is from the original dual coding; the
artifact-type normalization above was applied after agreement was computed. The flags
in `contribution_matrix_92.csv` are the final flags used in the paper.

## Reproduction steps

1. **Search** — re-run the queries recorded in `search_log.csv` for each library with the listed
   fields and date filters; the recorded results are in `raw_search/`.
2. **Deduplicate** — apply `scripts/dedup_match.py` (DOI > normalized title > fuzzy matching) to remove
   records already covered by the previous corpus.
3. **Filter and screen** — consolidate the five exports (identical records counted once: 4,382 → 4,379),
   apply the automatic bibliographic filter (`screening/auto_filtered_652_records.csv`; 652 non-archival
   records removed, with peer-reviewed contributions verified and kept), leaving **3,727 preliminary
   screening records**, then apply the inclusion/exclusion criteria (paper, Sec. III.C) with two
   independent coders; compare against the process matrices in `screening/`. Inter-coder agreement was
   computed after both coders completed their independent labeling of the preliminary screening corpus:
   91.7% agreement, multi-class Kappa 0.872, binary keep-or-exclude Kappa 0.707 (N = 3,727; see
   `screening/kappa_report_preliminary_3727.txt`).
4. **Extract** — use the coding manual to reproduce the extraction; `extraction_master_94.csv` holds the
   final codes, and `reliability_and_summary.txt` reports per-dimension agreement (average Kappa 0.938).
5. **Statistics and figures** — run the scripts in `scripts/` to regenerate the demographic ledger,
   RQ statistics, and all figures (Python 3 + PyMuPDF; see script headers for usage). Compare the
   final contribution flags against `extraction/contribution_matrix_92.csv` and the artifact exports
   in `extraction/artifact_tables/`.

## Notes

- Exclusion reasons are reported in the paper (Sec. III.C) using the dominant reason per record under the
  revised criteria (the original 8-page threshold was replaced in this revision; see the protocol documents).
- The automatic bibliographic filter removes records whose publication type is non-archival (books,
  book chapters, workshop-only papers, posters, demo and doctoral-symposium abstracts). Its output was
  verified manually so that peer-reviewed contributions indexed under those types (LNCS conference
  chapters; artifact and short papers in companion proceedings) are retained; 16 such records were
  returned to the preliminary screening data. The removed records are listed in
  `screening/auto_filtered_652_records.csv`.
- The update searches used hyphenation-insensitive and wildcard variants (e.g., `Docker*`, `docker compose`);
  the full-text-level container-vocabulary variant is retained only as a sensitivity check.
- The Google Scholar saturation curve is `figures/gs_saturation.pdf`, generated by
  `scripts/regen_saturation_500.py` from the top-500 screened records (full top-990 scrape in
  `raw_search/GoogleScholar/`) and their coverage classification in `dedup/`.
