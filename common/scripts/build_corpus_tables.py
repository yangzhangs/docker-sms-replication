#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild the public corpus table and validate the PDF metadata index.

Inputs
------
common/extraction/wp1_v2_ledger.csv
RQ2/data/table_iv_contributions.csv
common/corpus/pdf_index.csv

Output
------
common/corpus/corpus_92.csv

PDF payloads are intentionally absent from the public repository.  The
pdf_index.csv table records the local filename, size and SHA-256 for the
copies used during the study, plus DOI links for metadata-only records.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "common" / "extraction" / "wp1_v2_ledger.csv"
MATRIX = ROOT / "RQ2" / "data" / "table_iv_contributions.csv"
PDF_INDEX = ROOT / "common" / "corpus" / "pdf_index.csv"
OUT = ROOT / "common" / "corpus" / "corpus_92.csv"


def read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    ledger = {r["zotero_key"]: r for r in read(LEDGER)}
    matrix = read(MATRIX)
    pdf = {r["zotero_key"]: r for r in read(PDF_INDEX) if r.get("P")}
    if len(matrix) != 92:
        raise SystemExit(f"expected 92 studies, found {len(matrix)}")

    rows = []
    for r in matrix:
        key = r["zotero_key"]
        meta = ledger[key]
        p = pdf.get(key, {})
        rows.append({
            "P": r["P"], "zotero_key": key, "title": r["title"], "year": r["year"],
            "venue_type": meta["venue_type"], "venue_name": meta["venue_name"],
            "doi": meta["doi"], "public_url": ("https://doi.org/" + meta["doi"] if meta["doi"] else ""),
            "publisher": meta["publisher"], "core": meta["core"], "source": meta["source"],
            "first_author_country": meta["country"],
            "rep_package": r["rep_package"], "dataset": r["dataset"], "approach": r["approach"],
            "tool": r["tool"], "taxonomy": r["taxonomy"], "insight": r["insight"],
            "local_pdf_available": p.get("local_pdf_available", "no"),
            "pdf_filename": p.get("pdf_filename", ""),
            "pdf_bytes": p.get("pdf_bytes", ""),
            "pdf_sha256": p.get("pdf_sha256", ""),
            "pdf_distribution_status": p.get("pdf_status", "metadata_only_no_local_pdf"),
        })

    local = sum(r["local_pdf_available"] == "yes" for r in rows)
    if (len(rows), local) != (92, 36):
        raise SystemExit(f"unexpected corpus/PDF counts: {len(rows)} studies, {local} local PDFs")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} studies; {local} local PDFs; {len(rows) - local} metadata-only)")


if __name__ == "__main__":
    main()
