#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compute extraction reliability from the independent coder columns."""
from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "common" / "extraction" / "extraction_master_92.csv"
OUT_DIR = ROOT / "common" / "extraction"
CONCERNS = ["Performance", "Maintainability", "Reliability", "Security", "Evolution", "Adoption"]
OBJECTS = ["Specification", "Build", "Image", "Container"]
CONTRIB = ["rep_package", "dataset", "approach", "tool", "taxonomy", "insight"]
CHALLENGES = ["C1a", "C1b", "C1c", "C1d", "C1e", "C2a", "C2b", "C2c", "C3a", "C3b", "C3c", "C4a", "C4b", "C4c"]
LIMITATIONS = ["L1a", "L1b", "L1c", "L1d", "L2a", "L2b", "L2c", "L3a", "L3b", "L3c", "L3d"]


def labels(value: str) -> set[str]:
    return {part.strip() for part in re.split(r"[;,]", value or "") if part.strip()}


def contrib(value: str) -> set[str]:
    """Treat both a verified link (Y) and a declared-but-broken link as a declaration."""
    found = set()
    for part in (value or "").split(","):
        if ":" not in part:
            continue
        name, status = part.split(":", 1)
        if status.strip() not in ("", "-"):
            found.add(name.strip())
    return found


def kappa(pairs: list[tuple[bool, bool]]) -> tuple[float, float, int]:
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca = Counter(a for a, _ in pairs)
    cb = Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0, po, n


def main() -> None:
    rows = list(csv.DictReader(MASTER.open(encoding="utf-8-sig", newline="")))
    dimensions = {
        "SE concern": (CONCERNS, lambda r: labels(r["concerns_A"]), lambda r: labels(r["concerns_B"])),
        "Docker object": (OBJECTS, lambda r: labels(r["objects_A"]), lambda r: labels(r["objects_B"])),
        "Contribution type": (CONTRIB, lambda r: contrib(r["contrib_A"]), lambda r: contrib(r["contrib_B"])),
        "Challenge subcategory": (CHALLENGES, lambda r: labels(r["challenges_A"]), lambda r: labels(r["challenges_B"])),
        "Limitation subcategory": (LIMITATIONS, lambda r: labels(r["limitations_A"]), lambda r: labels(r["limitations_B"])),
    }
    dimension_rows = []
    label_rows = []
    means = []
    for dimension, (codes, get_a, get_b) in dimensions.items():
        pairs = []
        for code in codes:
            code_pairs = [(code in get_a(r), code in get_b(r)) for r in rows]
            k, po, n = kappa(code_pairs)
            label_rows.append({"dimension": dimension, "label": code, "kappa": f"{k:.6f}",
                               "agreement": f"{po:.6f}", "judgments": n})
            pairs.extend(code_pairs)
        k, po, n = kappa(pairs)
        dimension_rows.append({"dimension": dimension, "kappa": f"{k:.6f}",
                               "agreement": f"{po:.6f}", "judgments": n})
        means.append(k)

    with (OUT_DIR / "kappa_by_dimension.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=["dimension", "kappa", "agreement", "judgments"])
        writer.writeheader()
        writer.writerows(dimension_rows)
    with (OUT_DIR / "kappa_by_label.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=["dimension", "label", "kappa", "agreement", "judgments"])
        writer.writeheader()
        writer.writerows(label_rows)

    print("kappa_by_dimension.csv")
    for row in dimension_rows:
        print(f"  {row['dimension']}: Kappa={row['kappa']} agreement={row['agreement']} n={row['judgments']}")
    print(f"  average Kappa={sum(means) / len(means):.6f}")


if __name__ == "__main__":
    main()
