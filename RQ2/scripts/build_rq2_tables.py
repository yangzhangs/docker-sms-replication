#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate and summarise the RQ2 contribution data.

Inputs (authoritative data shipped with the package)
-----------------------------------------------------
RQ2/data/table_iv_contributions.csv
RQ2/data/table_v_datasets.csv
RQ2/data/table_vi_tools.csv
RQ2/data/table_vii_taxonomies.csv

Outputs
-------
RQ2/data/rq2_contribution_summary.csv
RQ2/data/rq2_combination_summary.csv
RQ2/data/rq2_artifact_summary.csv

The manuscript's Table IV-VII are direct views of the input CSVs; the
script checks the counts quoted in the paper and writes compact summaries.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "RQ2" / "data"
TYPES = ["rep_package", "dataset", "approach", "tool", "taxonomy", "insight"]
EXPECTED = {
    "rep_package": 50, "dataset": 24, "approach": 55,
    "tool": 36, "taxonomy": 10, "insight": 67,
}


def read(name: str) -> list[dict]:
    with (DATA / name).open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write(name: str, fields: list[str], rows: list[dict]) -> None:
    with (DATA / name).open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    matrix = read("table_iv_contributions.csv")
    datasets = read("table_v_datasets.csv")
    tools = read("table_vi_tools.csv")
    taxonomies = read("table_vii_taxonomies.csv")

    if len(matrix) != 92:
        raise SystemExit(f"expected 92 studies in Table IV, found {len(matrix)}")

    declared = {t: sum(1 for row in matrix if row[t].strip()) for t in TYPES}
    if declared != EXPECTED:
        raise SystemExit(f"Table IV counts differ from paper: {declared}")

    n_types = [sum(1 for t in TYPES if row[t].strip()) for row in matrix]
    distribution = Counter(n_types)
    expected_distribution = {1: 17, 2: 26, 3: 30, 4: 12, 5: 7}
    if dict(sorted(distribution.items())) != expected_distribution:
        raise SystemExit(f"contribution-type distribution differs from paper: {distribution}")

    contribution_rows = [
        {"contribution_type": t, "studies": declared[t],
         "percent_of_92": f"{declared[t] / 92 * 100:.1f}"}
        for t in TYPES
    ]
    write("rq2_contribution_summary.csv",
          ["contribution_type", "studies", "percent_of_92"], contribution_rows)

    combination_rows = [
        {"number_of_types": n, "studies": distribution[n]}
        for n in range(1, 6)
    ]
    combination_rows.extend([
        {"number_of_types": "2_or_more", "studies": sum(v for n, v in distribution.items() if n >= 2)},
        {"number_of_types": "3_or_more", "studies": sum(v for n, v in distribution.items() if n >= 3)},
        {"number_of_types": "2_or_3", "studies": distribution[2] + distribution[3]},
        {"number_of_types": "5", "studies": distribution[5]},
    ])
    write("rq2_combination_summary.csv",
          ["number_of_types", "studies"], combination_rows)

    dataset_studies = len(datasets)
    if dataset_studies != 24:
        raise SystemExit(f"expected 24 dataset rows, found {dataset_studies}")
    if len({r["P"] for r in datasets}) != 24:
        raise SystemExit("duplicate P number in Table V data")

    github = sum("GitHub" in r["source_platforms"] for r in datasets)
    docker = sum("Docker" in r["source_platforms"] for r in datasets)
    hybrid = sum("," in r["source_platforms"] for r in datasets)
    link_provided = sum(r["link_status"] in {"provided", "unreachable", "empty"} for r in datasets)
    no_link = sum(r["link_status"] == "none" for r in datasets)
    if (github, docker, hybrid, link_provided, no_link) != (20, 8, 4, 23, 1):
        raise SystemExit(f"dataset source/link counts differ: {(github, docker, hybrid, link_provided, no_link)}")

    tool_studies = len({r["zotero_key"] for r in tools})
    primary = sum(r["type"] == "primary" for r in tools)
    supporting = sum(r["type"] == "supporting" for r in tools)
    if (len(tools), tool_studies, primary, supporting) != (38, 36, 30, 8):
        raise SystemExit(f"tool counts differ: {(len(tools), tool_studies, primary, supporting)}")
    if len(taxonomies) != 10 or len({r["P"] for r in taxonomies}) != 10:
        raise SystemExit("expected 10 unique taxonomy studies")

    artifact_rows = [
        {"metric": "dataset_studies", "value": dataset_studies},
        {"metric": "dataset_github_sourced", "value": github},
        {"metric": "dataset_docker_sourced", "value": docker},
        {"metric": "dataset_hybrid", "value": hybrid},
        {"metric": "dataset_with_access_link", "value": link_provided},
        {"metric": "dataset_without_link", "value": no_link},
        {"metric": "tool_rows", "value": len(tools)},
        {"metric": "tool_studies", "value": tool_studies},
        {"metric": "tools_primary", "value": primary},
        {"metric": "tools_supporting", "value": supporting},
        {"metric": "taxonomies", "value": len(taxonomies)},
    ]
    write("rq2_artifact_summary.csv", ["metric", "value"], artifact_rows)

    print(f"RQ2 tables checked and summarised in {DATA}")
    print(f"types={declared} distribution={dict(sorted(distribution.items()))}")
    print(f"datasets={dataset_studies} tools={len(tools)}/{tool_studies} taxonomies={len(taxonomies)}")


if __name__ == "__main__":
    main()
