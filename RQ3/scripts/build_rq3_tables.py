#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the RQ3 challenge/limitation taxonomy and rebuild its summaries.

Inputs
------
RQ3/data/table_viii_categories.csv   Final Table VIII export
common/extraction/extraction_master_92.csv
RQ2/data/table_iv_contributions.csv  P-number to Zotero-key mapping

Outputs
-------
RQ3/data/rq3_category_summary.csv
RQ3/data/rq3_subcategory_summary.csv

The script checks that every subcategory P list matches the extraction
master and that each major category is the union of its subcategories.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "RQ3" / "data"
MASTER = ROOT / "common" / "extraction" / "extraction_master_92.csv"
MATRIX = ROOT / "RQ2" / "data" / "table_iv_contributions.csv"
CATEGORIES = ["C1", "C2", "C3", "C4", "L1", "L2", "L3"]
EXPECTED_CATEGORY_COUNTS = {"C1": 71, "C2": 18, "C3": 31, "C4": 19, "L1": 53, "L2": 35, "L3": 59}
EXPECTED_SUBCATEGORY_COUNTS = 25


def split_papers(value: str) -> set[str]:
    return {part.strip() for part in value.split(";") if part.strip()}


def write(name: str, fields: list[str], rows: list[dict]) -> None:
    with (DATA / name).open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = list(csv.DictReader((DATA / "table_viii_categories.csv").open(encoding="utf-8-sig", newline="")))
    categories = {r["code"]: r for r in rows if r["level"] == "category"}
    subcategories = [r for r in rows if r["level"] == "subcategory"]
    if set(categories) != set(CATEGORIES):
        raise SystemExit(f"unexpected major categories: {sorted(categories)}")
    if len(subcategories) != EXPECTED_SUBCATEGORY_COUNTS:
        raise SystemExit(f"expected 25 subcategories, found {len(subcategories)}")

    active = {
        row["zotero_key"]: row
        for row in csv.DictReader(MASTER.open(encoding="utf-8-sig", newline=""))
    }
    p_by_key = {row["zotero_key"]: row["P"]
                for row in csv.DictReader(MATRIX.open(encoding="utf-8-sig", newline=""))}

    for code, row in categories.items():
        papers = split_papers(row["papers"])
        if len(papers) != int(row["count"]):
            raise SystemExit(f"{code}: count/list mismatch")
        expected = int(EXPECTED_CATEGORY_COUNTS[code])
        if len(papers) != expected:
            raise SystemExit(f"{code}: expected {expected}, found {len(papers)}")

    # Check each subcategory list against the extraction master.
    for row in subcategories:
        code = row["code"]
        papers = split_papers(row["papers"])
        if len(papers) != int(row["count"]):
            raise SystemExit(f"{code}: count/list mismatch")
        expected = {
            p for key, study in active.items()
            if code in {x.strip() for x in (study["challenges"] + ";" + study["limitations"]).split(";")}
            for p in [p_by_key.get(key)]
            if p
        }
        if papers != expected:
            missing = sorted(expected - papers, key=lambda p: int(p[1:]))
            extra = sorted(papers - expected, key=lambda p: int(p[1:]))
            raise SystemExit(f"{code}: list differs from extraction master; missing={missing}, extra={extra}")

    # Check that category lists equal the union of their subcategory lists.
    for code in CATEGORIES:
        union = set()
        for row in subcategories:
            if row["code"].startswith(code):
                union |= split_papers(row["papers"])
        if union != split_papers(categories[code]["papers"]):
            raise SystemExit(f"{code}: category list is not the union of its subcategories")

    category_rows = [
        {"code": code, "category": categories[code]["name"],
         "count": int(categories[code]["count"]),
         "subcategories": sum(r["code"].startswith(code) for r in subcategories)}
        for code in CATEGORIES
    ]
    write("rq3_category_summary.csv", ["code", "category", "count", "subcategories"], category_rows)

    sub_rows = [
        {"code": r["code"], "subcategory": r["name"], "count": int(r["count"]),
         "papers": r["papers"]}
        for r in subcategories
    ]
    write("rq3_subcategory_summary.csv", ["code", "subcategory", "count", "papers"], sub_rows)

    print(f"RQ3 tables checked and summarised in {DATA}")
    print(f"categories={len(categories)} subcategories={len(subcategories)}")
    print("counts=" + ", ".join(f"{r['code']}={r['count']}" for r in category_rows))


if __name__ == "__main__":
    main()
