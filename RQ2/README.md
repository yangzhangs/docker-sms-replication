# RQ2: Research contributions

RQ2 covers replication packages, datasets, approaches, tools, taxonomies, and
insights. Tables IV-VII are shipped as final active-row CSVs.

## Data

- `data/table_iv_contributions.csv`: 92 studies; columns for replication package,
  dataset, approach, tool, taxonomy, and insight (`Y` or empty).
- `data/table_v_datasets.csv`: 24 datasets, with source platform, size, timestamp,
  access link, access label, and link status.
- `data/table_vi_tools.csv`: 38 tools from 36 studies (`type` is primary or
  supporting), with access links.
- `data/table_vii_taxonomies.csv`: 10 taxonomies with category counts and main categories.
- `data/rq2_contribution_summary.csv`: type-level counts and percentages.
- `data/rq2_combination_summary.csv`: distribution of 1-5 contribution types.
- `data/rq2_artifact_summary.csv`: dataset/tool/taxonomy summary metrics.

The final flags give 50 replication packages, 24 datasets, 55 approaches,
36 tool studies (38 tools), 10 taxonomies, and 67 insight studies. The
contribution-type distribution is 17/26/30/12/7 for one through five types.

Dataset note: the 24 datasets comprise 22 v2-audited Docker-artifact corpora plus
two v1-original shared build/issue collections (Shipwright and Docker Build
Faults) retained for continuity with the original submission.

## Reproduction

```bash
python RQ2/scripts/build_rq2_tables.py
```

The script validates the counts and link/type summaries and rewrites the three
summary CSVs. It does not alter the authoritative Table IV-VII exports.
