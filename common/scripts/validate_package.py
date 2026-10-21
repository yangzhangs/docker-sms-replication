#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check the package against the counts reported in the manuscript."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def rows(path: str) -> list[dict]:
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL: " + message)


def main() -> None:
    corpus = rows("common/corpus/corpus_92.csv")
    pdf = rows("common/corpus/pdf_index.csv")
    flow = {r["stage"]: int(r["count"]) for r in rows("common/screening/screening_flow.csv")}
    reasons = rows("common/screening/exclusion_reasons.csv")
    master = rows("common/extraction/extraction_master_92.csv")
    agenda = rows("common/tables/table_ix_research_agenda.csv")
    gs = rows("common/search/google_scholar_top500_noncorpus_classification.csv")
    gs_segments = rows("common/search/gs_top500_saturation_segments.csv")
    rq1_gap = {r["metric"]: r["value"] for r in rows("RQ1/data/rq1_gap_summary.csv")}
    matrix = rows("RQ2/data/table_iv_contributions.csv")
    datasets = rows("RQ2/data/table_v_datasets.csv")
    tools = rows("RQ2/data/table_vi_tools.csv")
    taxonomies = rows("RQ2/data/table_vii_taxonomies.csv")
    rq3 = rows("RQ3/data/table_viii_categories.csv")

    require(len(corpus) == 92, f"corpus_92 has {len(corpus)} rows")
    require(sum(r["local_pdf_available"] == "yes" for r in corpus) == 36,
            "expected 36 active local PDFs")
    require(len(pdf) == 92, f"pdf_index has {len(pdf)} rows")
    require(sum(1 for r in pdf if r["P"]) == 92, "pdf_index must contain 92 active rows")

    require(flow["records_identified"] - flow["duplicate_exports_merged"] - flow["auto_filtered_non_archival"] == flow["preliminary_screening"],
            "selection flow does not close before screening")
    require(sum(int(r["count"]) for r in reasons) == flow["excluded_total"],
            "exclusion reasons do not sum to excluded_total")
    require(flow["preliminary_screening"] - flow["excluded_total"] == flow["retained_records"],
            "preliminary screening and retained records do not close")
    require(flow["studies_from_searches"] + flow["studies_from_snowballing"] == flow["final_primary_studies"] == 92,
            "final corpus does not close")

    require(len(master) == 92 and len({r["P"] for r in master}) == 92,
            "extraction_master_92 must contain 92 unique paper IDs")
    require(all(r["authors"].strip() for r in master),
            "every extraction-master row must include authors")
    require(all(r["doi"].strip() for r in master),
            "every extraction-master row must include a DOI")
    for col in ["concerns_A", "concerns_B", "objects_A", "objects_B", "challenges_A"]:
        require(all(r[col].strip() for r in master), f"{col} must be populated for all 92 studies")
    require(all(r["challenges_A"].strip() for r in master),
            "challenge labels must be populated for all 92 studies")
    require(len(rows("common/extraction/kappa_by_dimension.csv")) == 5,
            "kappa_by_dimension.csv must contain five dimensions")
    require(sum(bool(r["artifact_details"].strip()) for r in master) == 50,
            "artifact_details must cover the 50 artifact studies")
    require(len(agenda) == 7, "Table IX must contain 7 agenda rows")
    require(len(gs) == 213 and max(int(float(r["rank"])) for r in gs) <= 500,
            "Google Scholar non-corpus table must be restricted to the top 500")
    require(rq1_gap["populated_cells"] == "21" and rq1_gap["empty_cells"] == "3",
            "RQ1 gap summary must report 21 populated and 3 empty cells")
    require(len(gs_segments) == 5, "expected five 100-record saturation segments")
    require(sum(int(r["screened_records"]) for r in gs_segments) == 500,
            "saturation segments must cover 500 screened records")
    require(sum(int(r["noncorpus_records"]) for r in gs_segments) == len(gs),
            "saturation segment totals must match the non-corpus table")

    require(len(matrix) == 92, "Table IV must contain 92 rows")
    require(len(datasets) == 24 and len({r["P"] for r in datasets}) == 24,
            "Table V must contain 24 unique datasets")
    require(len(tools) == 38 and len({r["zotero_key"] for r in tools}) == 36,
            "Table VI must contain 38 tools from 36 studies")
    require(len(taxonomies) == 10, "Table VII must contain 10 taxonomies")
    require(sum(1 for r in rq3 if r["level"] == "category") == 7, "expected 7 categories")
    require(sum(1 for r in rq3 if r["level"] == "subcategory") == 25, "expected 25 subcategories")

    print("PASS")
    print("  92 studies; 36 local PDFs; 56 metadata-only records")
    print("  4,382 records -> 3,727 screened -> 3,592 excluded -> 135 records -> 92 studies")
    print("  24 datasets; 38 tools from 36 studies; 10 taxonomies; 7 categories / 25 subcategories")


if __name__ == "__main__":
    main()
