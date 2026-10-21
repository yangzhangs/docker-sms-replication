#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild the RQ1 data tables from the final extracted corpus.

Inputs
------
common/extraction/extraction_master_94.csv
RQ2/data/table_iv_contributions.csv   (P-number to Zotero-key mapping)

Outputs
-------
RQ1/data/table_iii_mapping.csv         Concern x object cells (Table III)
RQ1/data/table_iii_topic_summary.csv   Seven dominant topics used in Sec. IV.A
RQ1/data/rq1_concern_summary.csv       Unique studies per SE concern
RQ1/data/rq1_object_summary.csv        Unique studies per Docker object
RQ1/data/temporal_counts.csv           Concern/object counts by year (Fig. 4)

The script uses only the files distributed in this package.
"""
from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "common" / "extraction" / "extraction_master_94.csv"
MATRIX = ROOT / "RQ2" / "data" / "table_iv_contributions.csv"
OUT = ROOT / "RQ1" / "data"

CONCERNS = ["Performance", "Maintainability", "Reliability", "Security", "Evolution", "Adoption"]
OBJECTS = ["Specification", "Build", "Image", "Container"]
TOPICS = [
    ("SM", "Specification Maintainability", "Maintainability", "Specification"),
    ("IS", "Image Security", "Security", "Image"),
    ("SP", "Specification Performance", "Performance", "Specification"),
    ("IM", "Image Maintainability", "Maintainability", "Image"),
    ("BR", "Build Reliability", "Reliability", "Build"),
    ("BP", "Build Performance", "Performance", "Build"),
    ("PI", "Image Performance", "Performance", "Image"),
]

EXPECTED_CONCERNS = {
    "Maintainability": 40, "Security": 24, "Performance": 20,
    "Adoption": 14, "Reliability": 14, "Evolution": 13,
}
EXPECTED_OBJECTS = {"Specification": 53, "Image": 45, "Build": 17, "Container": 7}
EXPECTED_TOPICS = {"SM": 38, "IS": 20, "SP": 13, "IM": 11, "BR": 10, "BP": 10, "PI": 10}


def split_tags(value: str, allowed: list[str]) -> list[str]:
    found: list[str] = []
    for part in re.split(r"[;,/]+", value or ""):
        part = part.strip()
        if part in allowed and part not in found:
            found.append(part)
    return found


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    master = {
        row["zotero_key"]: row
        for row in csv.DictReader(MASTER.open(encoding="utf-8-sig", newline=""))
        if not row.get("decision")
    }
    matrix = list(csv.DictReader(MATRIX.open(encoding="utf-8-sig", newline="")))
    if len(matrix) != 92:
        raise SystemExit(f"expected 92 active studies, found {len(matrix)}")

    cells: dict[tuple[str, str], list[str]] = defaultdict(list)
    year_concern: dict[int, Counter] = defaultdict(Counter)
    year_object: dict[int, Counter] = defaultdict(Counter)

    for row in matrix:
        key = row["zotero_key"]
        extracted = master[key]
        concerns = split_tags(extracted["concerns"], CONCERNS)
        objects = split_tags(extracted["objects"], OBJECTS)
        year = int(row["year"])
        for concern in concerns:
            year_concern[year][concern] += 1
            for obj in objects:
                cells[(concern, obj)].append(row["P"])
        for obj in objects:
            year_object[year][obj] += 1

    concern_studies = {
        c: sorted({p for o in OBJECTS for p in cells[(c, o)]}, key=lambda p: int(p[1:]))
        for c in CONCERNS
    }
    object_studies = {
        o: sorted({p for c in CONCERNS for p in cells[(c, o)]}, key=lambda p: int(p[1:]))
        for o in OBJECTS
    }

    actual_concerns = {c: len(v) for c, v in concern_studies.items()}
    actual_objects = {o: len(v) for o, v in object_studies.items()}
    if actual_concerns != EXPECTED_CONCERNS:
        raise SystemExit(f"concern counts differ from paper: {actual_concerns}")
    if actual_objects != EXPECTED_OBJECTS:
        raise SystemExit(f"object counts differ from paper: {actual_objects}")

    mapping_rows = []
    for concern in CONCERNS:
        for obj in OBJECTS:
            papers = sorted(cells[(concern, obj)], key=lambda p: int(p[1:]))
            mapping_rows.append({
                "concern": concern,
                "docker_object": obj,
                "count": len(papers),
                "papers": "; ".join(papers),
            })
    write_csv(OUT / "table_iii_mapping.csv", ["concern", "docker_object", "count", "papers"], mapping_rows)

    topic_rows = []
    for code, name, concern, obj in TOPICS:
        papers = sorted(cells[(concern, obj)], key=lambda p: int(p[1:]))
        topic_rows.append({
            "code": code, "topic": name, "concern": concern, "docker_object": obj,
            "count": len(papers), "percent_of_92": f"{len(papers) / 92 * 100:.1f}",
            "papers": "; ".join(papers),
        })
    actual_topics = {row["code"]: row["count"] for row in topic_rows}
    if actual_topics != EXPECTED_TOPICS:
        raise SystemExit(f"topic counts differ from paper: {actual_topics}")
    write_csv(OUT / "table_iii_topic_summary.csv",
              ["code", "topic", "concern", "docker_object", "count", "percent_of_92", "papers"],
              topic_rows)

    write_csv(OUT / "rq1_concern_summary.csv", ["concern", "count", "papers"],
              [{"concern": c, "count": len(concern_studies[c]), "papers": "; ".join(concern_studies[c])}
               for c in CONCERNS])
    write_csv(OUT / "rq1_object_summary.csv", ["docker_object", "count", "papers"],
              [{"docker_object": o, "count": len(object_studies[o]), "papers": "; ".join(object_studies[o])}
               for o in OBJECTS])

    temporal_rows = []
    for year in sorted(year_concern):
        for concern in CONCERNS:
            temporal_rows.append({"year": year, "dimension": "SE concern",
                                  "label": concern, "count": year_concern[year][concern]})
        for obj in OBJECTS:
            temporal_rows.append({"year": year, "dimension": "Docker object",
                                  "label": obj, "count": year_object[year][obj]})
    write_csv(OUT / "temporal_counts.csv",
              ["year", "dimension", "label", "count"], temporal_rows)

    populated = sum(1 for row in mapping_rows if row["count"] > 0)
    seven_union = {p for row in topic_rows for p in row["papers"].split("; ") if p}
    if len(seven_union) != 74:
        raise SystemExit(f"seven-topic union differs from paper: {len(seven_union)}")
    print(f"RQ1 tables written to {OUT}")
    print(f"studies={len(matrix)} populated_cells={populated}/24 seven_topic_unique={len(seven_union)}")


if __name__ == "__main__":
    main()
