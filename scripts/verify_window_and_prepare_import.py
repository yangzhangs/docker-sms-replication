#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增量数据窗口核验（WP0 收口）：
1. 汇总五库新候选（master 745 条）；
2. 解析已抓取的精确/月级日期（ACM/SD pub_date）；
3. 对缺月份的记录用 Crossref API 按 DOI 回填精确出版日期（并发+缓存）；
4. 窗口判定：best_date ≤ 2026-09-30 保留，否则排除；
   无法判定（无 DOI 且仅年份）→ 标记 date-verify 保留待筛前复核；
5. 输出：
   replication_package/increment_master_inwindow.csv      （导入用，含 date_status）
   replication_package/increment_excluded_after_window.csv （排除清单）
   zotero_tools/increment_for_zotero.json                  （Zotero JS 导入脚本的数据源）
"""
import csv
import json
import re
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
MASTER = WORKSPACE / "replication_package" / "increment_master_20251220-20260930.csv"
OUT_IN = WORKSPACE / "replication_package" / "increment_master_inwindow.csv"
OUT_EX = WORKSPACE / "replication_package" / "increment_excluded_after_window.csv"
CACHE = WORKSPACE / "replication_package" / "crossref_date_cache.json"
JSON_OUT = WORKSPACE / "zotero_tools" / "increment_for_zotero.json"

WINDOW_END = (2026, 9, 30)
MONTHS = {m: i + 1 for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"])}


def parse_en_date(text: str):
    """'Published: 01 October 2025' / 'October 2026' / '1 September 2026' → (y,m,d|None)"""
    if not text:
        return None
    t = text.lower()
    m = re.search(r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:,)?\s+(20[0-2]\d)", t)
    if m:
        return (int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))
    m = re.search(r"(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(20[0-2]\d)", t)
    if m:
        return (int(m.group(3)), MONTHS[m.group(2)], int(m.group(1)))
    m = re.search(r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+(20[0-2]\d)", t)
    if m:
        return (int(m.group(2)), MONTHS[m.group(1)], None)
    return None


def load_crossref_cache():
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {}


def save_crossref_cache(cache):
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")


def fetch_crossref(doi: str):
    url = f"https://api.crossref.org/works/{urllib.request.quote(doi)}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "DockerSMS-revision/1.0 (metadata date verification)"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            msg = json.loads(resp.read().decode("utf-8"))["message"]
        dates = []
        for key in ("published-online", "published-print", "published", "issued"):
            parts = (msg.get(key) or {}).get("date-parts") or []
            if parts and parts[0] and parts[0][0]:
                y, m, d = (parts[0] + [None, None])[:3]
                dates.append((int(y), int(m or 1), int(d) if d else None))
        if dates:
            return min(dates)  # 取最早可用出版日期
    except Exception:
        return None
    return None


def enrich(crossref_cache):
    rows = list(csv.DictReader(open(MASTER, encoding="utf-8-sig")))
    need = [r for r in rows if r["doi"] and r["doi"] not in crossref_cache]
    print(f"需 Crossref 回填 {len(need)} 条（缓存命中 {len(rows)-len(need)}）")
    def work(r):
        time.sleep(0.15)
        return r["doi"], fetch_crossref(r["doi"])
    done = 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        for fut in as_completed([ex.submit(work, r) for r in need]):
            doi, date = fut.result()
            crossref_cache[doi] = date
            done += 1
            if done % 100 == 0:
                print(f"  Crossref 进度 {done}/{len(need)}")
    save_crossref_cache(crossref_cache)
    return rows, crossref_cache


def best_date_for(r, cache):
    """返回 ((y,m,d)|None, 来源标签)"""
    cands = []
    for src in (r.get("pub_date", ""), ):
        p = parse_en_date(src)
        if p:
            cands.append((p, f"scraped({src[:26]})"))
    doi = (r.get("doi") or "").strip()
    if doi and doi.lower() in cache and cache[doi.lower()]:
        cands.append((tuple(cache[doi.lower()]), "crossref"))
    if not cands:
        return None, ""
    cands.sort(key=lambda x: (x[0][0], x[0][1], x[0][2] or 31))
    return cands[0]


def main():
    cache = load_crossref_cache()
    # 失败(None)不缓存，允许重试
    cache = {k: v for k, v in cache.items() if v}
    rows, cache = enrich(cache)
    # 第二遍：仍缺的用慢速串行补一轮
    missing = [r["doi"] for r in rows if r["doi"] and not cache.get(r["doi"].lower())]
    if missing:
        print(f"Crossref 串行补查 {len(missing)} 条（1.0s 间隔）")
        ok = 0
        for doi in missing:
            time.sleep(1.0)
            d = fetch_crossref(doi)
            if d:
                cache[doi.lower()] = d
                ok += 1
        print(f"  补查成功 {ok}/{len(missing)}")
        save_crossref_cache(cache)

    kept, excluded, verify = [], [], []
    for r in rows:
        d, src = best_date_for(r, cache)
        year = r.get("year", "")
        if d:
            (y, m, dd) = d
            r["pub_date_best"] = f"{y:04d}-{m:02d}-{dd:02d}" if dd else f"{y:04d}-{m:02d}"
            r["date_source"] = src
            # 月精度无日时按 (y,m) 比较；日精度按 (y,m,d) 比较
            over = (y, m, dd or 1) > WINDOW_END if dd else (y, m) > WINDOW_END[:2]
            if over:
                r["exclusion_reason"] = f"出版日期 {r['pub_date_best']} 晚于 2026-09-30"
                excluded.append(r)
            else:
                r["date_status"] = "in-window"
                kept.append(r)
        elif year == "2026":
            r["date_status"] = "date-verify(2026 无月份,筛前复核)"
            r["date_source"] = "year-only"
            verify.append(r)
            kept.append(r)
        else:
            r["date_status"] = f"in-window(年份 {year or '未知'} ≤ 2026)"
            r["date_source"] = "year-only"
            kept.append(r)

    cols = ["libraries", "type", "title", "doi", "year", "venue", "authors", "pub_date",
            "pub_date_best", "date_source", "date_status", "exclusion_reason"]
    def dump(path, data):
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for r in data:
                w.writerow({k: r.get(k, "") for k in cols})

    dump(OUT_IN, kept)
    dump(OUT_EX, excluded)

    from collections import Counter
    print(f"\n窗口核验完成: 保留 {len(kept)} / 排除 {len(excluded)} / 其中待复核 {len(verify)}")
    print("排除原因分布:", dict(Counter(r["exclusion_reason"][:30] for r in excluded)))
    print("保留项 date_status 分布:", dict(Counter(r["date_status"] for r in kept)))

    # 生成 Zotero 导入 JSON
    TYPE_MAP = [
        (r"conf|poster|conference abstract", "conferencePaper"),
        (r"jour|article|review|communication|software publication|replication", "journalArticle"),
        (r"chap", "bookSection"),
        (r"^book$", "book"),
        (r"std", "standard"),
        (r"preprint", "preprint"),
    ]
    out = []
    for r in kept:
        t = (r.get("type") or "").lower()
        ztype = "journalArticle"
        for pat, zt in TYPE_MAP:
            if re.search(pat, t):
                ztype = zt
                break
        creators = [{"lastName": a.strip(), "fieldMode": 1}
                    for a in re.split(r"[;]", r.get("authors", "")) if a.strip()]
        out.append({
            "libraries": r["libraries"].split(";"),
            "itemType": ztype,
            "title": r["title"],
            "doi": r.get("doi", ""),
            "date": r.get("pub_date_best") or r.get("year", ""),
            "publicationTitle": r.get("venue", ""),
            "creators": creators,
            "url": f"https://doi.org/{r['doi']}" if r.get("doi") else "",
            "extra": f"increment window: 2025-12-20/2026-09-30 | source: {r['libraries']} | orig-type: {r.get('type','')} | {r.get('date_status','')}",
            "tags": ["increment-20251220-20260930"] + (["date-verify"] if "verify" in r.get("date_status", "") else []),
        })
    JSON_OUT.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"Zotero 导入数据: {len(out)} 条 -> {JSON_OUT}")


if __name__ == "__main__":
    main()
