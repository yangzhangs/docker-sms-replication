#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate MANIFEST.csv for the public package.

PDF payloads are excluded because they are not distributed. Figure PDFs are
included; the corpus PDF directory is excluded entirely.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXCLUDE_DIRS = {".git", "__pycache__", "corpus_v2_pdfs", "_preview"}
EXCLUDE_FILES = {"MANIFEST.csv"}


def main() -> None:
    records = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if any(part in EXCLUDE_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.name in EXCLUDE_FILES or path.suffix == ".pyc":
            continue
        data = path.read_bytes()
        records.append((rel, len(data), hashlib.sha256(data).hexdigest()))

    out = ROOT / "MANIFEST.csv"
    with out.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.writer(fh, lineterminator="\r\n")
        writer.writerow(["path", "bytes", "sha256"])
        writer.writerows(records)
    print(f"wrote {out} ({len(records)} files)")


if __name__ == "__main__":
    main()
