# RQ1: Research topics

RQ1 uses the two-dimensional framework of six SE concerns and four Docker objects.

## Data

- `data/table_iii_mapping.csv`: all 24 concern-object cells with P lists and counts.
- `data/table_iii_topic_summary.csv`: the seven dominant topics used in Sec. IV.A:
  SM 38, IS 20, SP 13, IM 11, BR 10, BP 10, PI 10; union = 74 studies.
- `data/rq1_concern_summary.csv`: unique studies and P lists per SE concern.
- `data/rq1_object_summary.csv`: unique studies and P lists per Docker object.
- `data/temporal_counts.csv`: concern/object counts by year, source for Fig. 4.
- `figures/fig4_temporal_heatmap.pdf`: temporal heatmap used in the paper.

## Reproduction

```bash
python RQ1/scripts/build_rq1_tables.py
```

The script joins `common/extraction/extraction_master_94.csv` to the final P-number
mapping in `RQ2/data/table_iv_contributions.csv`. It checks the key paper counts:
21 of 24 cells populated; 40 Maintainability, 24 Security, 20 Performance,
14 Adoption, 14 Reliability, 13 Evolution; 53 Specification, 45 Image, 17 Build,
7 Container; and 74 unique studies across the seven dominant topics.
