# RQ3: Challenges and limitations

RQ3 uses seven major categories and 25 subcategories. Every coded study carries
at least one subcategory for each category to which it is mapped.

## Data

- `data/table_viii_categories.csv`: 32 rows (7 category rows, 25 subcategory rows)
  with code, name, P list, and count.
- `data/rq3_category_summary.csv`: category counts and number of subcategories.
- `data/rq3_subcategory_summary.csv`: subcategory counts and P lists.

Category counts are C1 71, C2 18, C3 31, C4 19, L1 53, L2 35, L3 59. The
subcategory lists are checked against the `challenges` and `limitations` fields in
`common/extraction/extraction_master_92.csv`.

## Reproduction

```bash
python RQ3/scripts/build_rq3_tables.py
```

The script verifies that each subcategory P list matches the extraction master,
that each major category is the union of its subcategories, and that the
category counts match the paper. It rewrites the two summary CSVs.
