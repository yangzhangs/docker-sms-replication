# Artifact table exports

These CSVs are machine-readable exports of the manuscript’s result tables (active rows only).

| File | Manuscript table | Rows | Notes |
|---|---|---:|---|
| `table_v_datasets.csv` | Table V | 22 | Docker-artifact datasets; `link_status` ∈ `provided`, `none`, `unreachable`, `empty` |
| `table_vi_tools.csv` | Table VI | 38 | 36 unique studies; `type` ∈ `primary`, `supporting`; same link-status vocabulary |
| `table_vii_taxonomies.csv` | Table VII | 10 | taxonomy category counts and main categories |
| `table_viii_categories.csv` | Table VIII | 32 | 7 categories + 25 subcategories; `papers` is a semicolon-separated P list |

The per-study contribution matrix used by Table IV is `../contribution_matrix_92.csv`.

Dataset definition: released, reusable Docker-artifact corpora (Dockerfiles, images, Compose files, or
equivalent). Survey responses, discussion threads, build records, developer tests, and other evaluation
data are not counted as datasets. Tool definition: an implemented tool; conceptual frameworks and
proposed approaches are recorded as approaches, not tools.

Rows removed from the manuscript tables are retained in the manuscript as LaTeX comments (or
`\iffalse` cell marks) but are not included in these active-row CSV exports.
