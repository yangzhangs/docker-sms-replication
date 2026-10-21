# Reviewer-evidence map

This file links the main revision requests to the package files that support them.
The manuscript remains the authoritative description; the files below are the
underlying data or checks.

| Reviewer item | Evidence in this package |
|---|---|
| AE-1: auditable filtering and Docker scope | `common/protocol/search_protocol.md`, `common/search/search_log.csv`, `common/screening/screening_flow.csv`, `common/screening/exclusion_reasons.csv`, `common/figures/fig2_selection.pdf` |
| AE-2 / R2-M3: analysis beyond distributions | `RQ1/data/table_iii_mapping.csv`, `RQ1/data/table_iii_topic_summary.csv`, `RQ1/data/temporal_counts.csv`, `RQ1/figures/fig4_temporal_heatmap.pdf`, `common/tables/table_ix_research_agenda.csv` |
| AE-3 / R2-M5: subcategory granularity | `RQ3/data/table_viii_categories.csv`, `RQ3/data/rq3_category_summary.csv`, `RQ3/data/rq3_subcategory_summary.csv` |
| AE-4 / R2-M4: positioning against related reviews | Table I in the manuscript; this is a narrative comparison, not an extracted dataset |
| AE-5 / R1-2: screening procedure and Kappa | `common/protocol/screening_criteria.md`, `common/screening/kappa_report_preliminary_3727.txt`, `common/screening/screening_worksheet.csv` |
| R1-1: replication package | This package; `README.md` and `common/README.md` |
| R1-3a: search fields | `common/protocol/search_protocol.md`, `common/search/search_log.csv` |
| R1-3b: replication criterion | `common/protocol/screening_criteria.md` |
| R1-4: CORE versions | `common/extraction/study_ledger.csv` (`core` column), `common/protocol/search_protocol.md` |
| R1-5/R1-6: figure totals and venues | `common/extraction/study_ledger.csv`, `common/figures/fig3_demographics/plots4.pdf`, `plots3.pdf` |
| R1-7: Other = 0 | Table III footnote in the manuscript; the RQ1 data contain only the six coded concerns and four objects |
| R1-8/R1-9/R1-10: L3, validity wording, external validity | Manuscript revisions; the extracted limitation codes are in `common/extraction/extraction_master_92.csv` |
| R2-M1: per-criterion counts and search depth | `common/screening/screening_flow.csv`, `common/screening/exclusion_reasons.csv`, `common/search/google_scholar_rank_classification.csv`, `common/search/figures/gs_saturation.pdf` |
| R2-M2: extraction reliability | `common/extraction/extraction_master_92.csv` (`*_A`/`*_B` columns), `common/extraction/reliability_and_summary.txt` |
| R2-m1 / R3-m3: figure/table presentation | Final vector figures in `common/figures/` and `RQ1/figures/`; all table data are in the RQ folders |
| R2-m2/m3: Compose terminology and example | Manuscript; `common/extraction/coding_manual.md` records the final terminology |
| R2-m5: search-string rationale | `common/protocol/search_protocol.md`; the 23-paper validation set is described there |
| R3-W1: container-ecosystem scope | `common/protocol/search_protocol.md` and the manuscript's Introduction/Scope/Threats sections |
| R3-W2: page-count re-screening | `common/screening/short_paper_rescreen.csv`, `short_paper_additions.csv`, `short_paper_verification.csv`, `page_count_verification_sample.csv`, `common/protocol/screening_summary.md` |
| R3-W3: trade-offs, conflicts, agenda | `common/tables/table_ix_research_agenda.csv`; the synthesis itself is in the manuscript |
| R3-m2: snowballing outcome | `common/protocol/search_protocol.md`, `common/screening/snowballing_candidates_coded.csv`, `common/screening/screening_flow.csv` |
