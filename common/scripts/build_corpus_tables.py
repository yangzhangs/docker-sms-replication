#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild the public corpus table from the study ledger and contribution matrix.

Inputs
------
common/extraction/study_ledger.csv
RQ2/data/table_iv_contributions.csv

Output
------
common/corpus/corpus_92.csv
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "common" / "extraction" / "study_ledger.csv"
MATRIX = ROOT / "RQ2" / "data" / "table_iv_contributions.csv"
OUT = ROOT / "common" / "corpus" / "corpus_92.csv"


def read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    ledger = {r["zotero_key"]: r for r in read(LEDGER)}
    matrix = read(MATRIX)
    if len(matrix) != 92:
        raise SystemExit(f"expected 92 studies, found {len(matrix)}")

    rows = []
    for r in matrix:
        key = r["zotero_key"]
        meta = ledger[key]
        rows.append({
            "P": r["P"], "zotero_key": key, "title": r["title"], "year": r["year"],
            "venue_type": meta["venue_type"], "venue_name": meta["venue_name"],
            "doi": meta["doi"], "public_url": ("https://doi.org/" + meta["doi"] if meta["doi"] else ""),
            "publisher": meta["publisher"], "core": meta["core"],
            "first_author_country": meta["country"],
            "rep_package": r["rep_package"], "dataset": r["dataset"], "approach": r["approach"],
            "tool": r["tool"], "taxonomy": r["taxonomy"], "insight": r["insight"],
        })

    if len(rows) != 92:
        raise SystemExit(f"unexpected corpus size: {len(rows)} studies")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} studies)")


if __name__ == "__main__":
    main()
