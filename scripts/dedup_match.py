#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增量检索结果去重匹配工具（WP0.3）。

输入：任一数字库重检索导出的结果文件（RIS 或 BibTeX，自动识别）。
对照：Zotero 快照中 v1+v2 检索子树的全部既有条目（约 3,648+）。
输出（--out-prefix 前缀）：
  <prefix>_matched.csv        已存在于 Zotero 的记录（含匹配方式与对应条目键）
  <prefix>_new_candidates.csv 真正的新候选（待导入 Zotero 并筛选）
  <prefix>_summary.txt        统计摘要

用法：
  python zotero_tools/dedup_match.py --input ieee2026.ris --out-prefix zotero_export/dedup_ieee2026

匹配顺序：DOI 精确 > 标题规范化精确 > 标题模糊（>=0.93，需人工复核）。
"""
import argparse
import csv
import difflib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zotero_export import connect, subtree_ids, fetch_items  # noqa: E402

WORKSPACE = Path(__file__).resolve().parent.parent


def norm_doi(d: str) -> str:
    d = (d or "").strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    return d.strip()


def norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


# ------------------------------------------------------------------ parsers --
def parse_ris(text: str) -> list[dict]:
    recs, cur, last_tag = [], None, None
    for line in text.splitlines():
        m = re.match(r"^([A-Z][A-Z0-9])  - ?(.*)$", line)
        if m:
            tag, val = m.group(1), m.group(2).strip()
            if tag == "TY":
                cur = {"type": val, "title": "", "doi": "", "year": "", "venue": ""}
            elif tag == "ER":
                if cur:
                    recs.append(cur)
                cur, last_tag = None, None
            elif cur is not None:
                if tag in ("TI", "T1") and not cur["title"]:
                    cur["title"], last_tag = val, "title"
                elif tag == "DO" and not cur["doi"]:
                    cur["doi"], last_tag = val, "doi"
                elif tag == "PY" and not cur["year"]:
                    cur["year"], last_tag = val[:4], "year"
                elif tag in ("JO", "JA", "JF", "T2") and not cur["venue"]:
                    cur["venue"], last_tag = val, "venue"
        elif cur is not None and line.strip() and last_tag:
            cur[last_tag] += " " + line.strip()
    return recs


def _bibtex_field(entry: str, name: str) -> str:
    m = re.search(name + r"\s*=\s*[{\"](.+?)[}\"]\s*,?\s*\n", entry, re.S | re.I)
    if not m:
        return ""
    return re.sub(r"[{}]", "", m.group(1)).strip()


def parse_bibtex(text: str) -> list[dict]:
    recs = []
    for e in re.split(r"\n(?=@)", text):
        m = re.match(r"@(\w+)\s*[{\(]\s*([^,\s]+)\s*,", e)
        if not m:
            continue
        recs.append({
            "type": m.group(1),
            "title": _bibtex_field(e, "title"),
            "doi": _bibtex_field(e, "doi"),
            "year": (_bibtex_field(e, "year") or _bibtex_field(e, "date"))[:4],
            "venue": _bibtex_field(e, "booktitle") or _bibtex_field(e, "journal"),
        })
    return recs


# ------------------------------------------------------------------- match --
def build_inventory(cur):
    ids = subtree_ids(cur, 41) + subtree_ids(cur, 78)
    items = fetch_items(cur, ids)
    by_doi, by_title, titles = {}, {}, []
    for it in items:
        d, t = norm_doi(it["doi"]), norm_title(it["title"])
        if d:
            by_doi.setdefault(d, it)
        if t:
            by_title.setdefault(t, it)
            titles.append((t, it))
    return items, by_doi, by_title, titles


def match_records(records, inv, by_doi, by_title, titles):
    out = []
    for r in records:
        d, t = norm_doi(r["doi"]), norm_title(r["title"])
        if d and d in by_doi:
            hit = by_doi[d]
            out.append({**r, "match": "doi", "score": "1.00", **_hitcols(hit)})
            continue
        if t and t in by_title:
            hit = by_title[t]
            out.append({**r, "match": "title", "score": "1.00", **_hitcols(hit)})
            continue
        if t:
            best, bs = None, 0.0
            for nt, it in titles:
                s = difflib.SequenceMatcher(None, t, nt).ratio()
                if s > bs:
                    best, bs = it, s
                if bs > 0.995:
                    break
            if bs >= 0.93:
                out.append({**r, "match": "fuzzy", "score": f"{bs:.2f}", **_hitcols(best)})
                continue
        out.append({**r, "match": "new", "score": "", "zotero_key": "", "zotero_title": "", "zotero_year": ""})
    return out


def _hitcols(hit):
    return {"zotero_key": hit["zotero_key"], "zotero_title": hit["title"], "zotero_year": hit["year"]}


COLS = ["type", "title", "doi", "year", "venue", "match", "score",
        "zotero_key", "zotero_title", "zotero_year"]


def parse_csv_file(path: Path) -> list[dict]:
    recs = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            row = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items() if k}
            title = row.get("title") or row.get("ti") or ""
            year = row.get("year") or ""
            if not year:
                m = re.search(r"(\d{4})", row.get("pub_date", "") or row.get("date", ""))
                year = m.group(1) if m else ""
            recs.append({"type": row.get("type", ""), "title": title,
                         "doi": row.get("doi", ""), "year": year,
                         "venue": row.get("venue", "")})
    return recs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="RIS / BibTeX / CSV 结果文件")
    ap.add_argument("--out-prefix", required=True)
    args = ap.parse_args()

    in_path = Path(args.input)
    text = in_path.read_text(encoding="utf-8", errors="replace")
    if in_path.suffix.lower() == ".csv":
        records = parse_csv_file(in_path)
    elif text.lstrip().startswith("TY"):
        records = parse_ris(text)
    else:
        records = parse_bibtex(text)
    if not records:
        sys.exit("未能从输入文件解析出任何记录（支持 RIS / BibTeX / CSV）")

    con = connect()
    cur = con.cursor()
    inv, by_doi, by_title, titles = build_inventory(cur)
    con.close()
    results = match_records(records, inv, by_doi, by_title, titles)

    prefix = WORKSPACE / args.out_prefix
    prefix.parent.mkdir(parents=True, exist_ok=True)
    for suffix, subset in (("_matched.csv", lambda r: r["match"] != "new"),
                           ("_new_candidates.csv", lambda r: r["match"] == "new")):
        with open(prefix.with_name(prefix.name + suffix), "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore")
            w.writeheader()
            w.writerows([r for r in results if subset(r)])
    summary = [
        f"输入记录: {len(results)}",
        f"既有对照条目: {len(inv)}",
        f"已存在(matched): {sum(1 for r in results if r['match'] != 'new')}"
        f"  (doi={sum(1 for r in results if r['match']=='doi')},"
        f" title={sum(1 for r in results if r['match']=='title')},"
        f" fuzzy={sum(1 for r in results if r['match']=='fuzzy')})",
        f"新候选(new): {sum(1 for r in results if r['match'] == 'new')}",
    ]
    prefix.with_name(prefix.name + "_summary.txt").write_text("\n".join(summary), encoding="utf-8")
    print("\n".join(summary))
    print(f"输出: {prefix}_matched.csv / _new_candidates.csv / _summary.txt")


if __name__ == "__main__":
    main()
