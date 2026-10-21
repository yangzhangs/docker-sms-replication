#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WP0.5 滚雪球（v2）：
  前向：语料 90 篇的被引文献（v1 的 56 篇限新窗口 2025-12-20 起；34 篇新论文查全周期）
  后向：34 篇新论文的参考文献
  去重基准：Zotero 库（3,648 v1 池 + 731 增量 + 语料）+ GS 990
  筛查：复用双人编码规则（含 ≥5 页门槛：有页数即校验，无则标 page-verify）
输出（zotero_export/）：
  snowballing_forward_raw.csv / snowballing_backward_raw.csv   （原始抓取）
  snowballing_candidates_coded.csv                              （去重+编码后候选）
  snowballing_summary.txt
"""
import csv
import json
import re
import sqlite3
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
import sys

WS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WS / "zotero_tools"))
from dual_coding_and_verify import feats, code_A, code_B, adjudicate, nt, load_overrides  # noqa

SNAP = WS / "zotero_snapshot" / "zotero_copy.sqlite"
OUT = WS / "zotero_export"
UA = {"User-Agent": "DockerSMS-revision/1.0 (mailto:research@example.org)"}
MAILTO = "research@example.org"
NEW_WINDOW_START = "2025-12-20"


def http_json(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fix_doi(d):
    d = (d or "").strip()
    if not d:
        return ""
    if re.match(r"^978-", d):
        return "10.1007/" + d
    return d


def openalex_work(doi):
    try:
        return http_json(f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}?mailto={MAILTO}")
    except Exception:
        return None


def fetch_batch(ids):
    """按 openalex id 批量取元数据（每批50）"""
    out = []
    ids = [i.replace("https://openalex.org/", "") for i in ids]
    for k in range(0, len(ids), 50):
        chunk = "|".join(ids[k:k + 50])
        try:
            j = http_json(f"https://api.openalex.org/works?filter=openalex_id:{chunk}"
                          f"&per-page=50&select=id,doi,title,publication_year,type,primary_location,authorships,abstract_inverted_index,biblio&mailto={MAILTO}")
            out.extend(j.get("results", []))
        except Exception:
            pass
        time.sleep(0.3)
    return out


def norm_work(w):
    loc = w.get("primary_location") or {}
    src = (loc.get("source") or {})
    auths = [a.get("author", {}).get("display_name", "") for a in (w.get("authorships") or [])][:6]
    bib = w.get("biblio") or {}
    return {
        "title": (w.get("title") or "").strip(),
        "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
        "year": str(w.get("publication_year") or ""),
        "type": w.get("type") or "",
        "venue": (src.get("display_name") or "")[:90],
        "authors": "; ".join(auths),
        "first_page": bib.get("first_page") or "",
        "last_page": bib.get("last_page") or "",
        "abstract": (lambda inv: "" if not inv else " ".join(
            inv_w for _, inv_w in sorted((i, wd) for wd, idxs in inv.items() for i in idxs)))(
                w.get("abstract_inverted_index")),
    }


def main():
    # ---------- 语料 90 篇 ----------
    corpus = []
    v1 = list(csv.DictReader(open(OUT / "final_56_primary_studies.csv", encoding="utf-8-sig")))
    for r in v1:
        corpus.append({"title": r["title"], "doi": fix_doi(r.get("doi", "")), "grp": "v1"})
    inc = [r for r in csv.DictReader(open(OUT / "increment_screening_coded.csv", encoding="utf-8-sig"))
           if r["final_code"] == "keep"]
    for r in inc:
        corpus.append({"title": r["title"], "doi": fix_doi(r.get("doi", "")), "grp": "new"})
    adds = list(csv.DictReader(open(OUT / "v1_shortpaper_additions.csv", encoding="utf-8-sig")))
    for r in adds:
        corpus.append({"title": r["title"], "doi": fix_doi(r.get("doi", "")), "grp": "new"})
    print(f"语料: {len(corpus)} 篇（v1 {sum(1 for c in corpus if c['grp']=='v1')} + 新 {sum(1 for c in corpus if c['grp']=='new')}）")

    # ---------- 去重基准（Zotero 全部标题/DOI + GS990）----------
    con = sqlite3.connect(f"file:{SNAP.as_posix()}?mode=ro", uri=True)
    cur, cur2 = con.cursor(), con.cursor()
    known_doi, known_title = set(), set()
    for iid in [r[0] for r in cur.execute("SELECT itemID FROM items WHERE itemID NOT IN (SELECT itemID FROM deletedItems)").fetchall()]:
        d = cur2.execute("""SELECT v.value FROM itemData d JOIN itemDataValues v ON v.valueID=d.valueID
            JOIN fields f ON f.fieldID=d.fieldID WHERE d.itemID=? AND f.fieldName='DOI'""", (iid,)).fetchone()
        if d and d[0]:
            known_doi.add(d[0].strip().lower())
        t = cur2.execute("""SELECT v.value FROM itemData d JOIN itemDataValues v ON v.valueID=d.valueID
            JOIN fields f ON f.fieldID=d.fieldID WHERE d.itemID=? AND f.fieldName='title'""", (iid,)).fetchone()
        if t and t[0]:
            known_title.add(nt(t[0]))
    con.close()
    for r in csv.DictReader(open(OUT.parent / "replication_package/raw_search/GoogleScholar/GoogleScholar_top990_2014-2026.csv", encoding="utf-8-sig")):
        known_title.add(nt(r["title"]))
    print(f"去重基准: DOI {len(known_doi)} / 标题 {len(known_title)}")

    corpus_titles = {nt(c["title"]) for c in corpus}

    # ---------- 前向引用 ----------
    fwd_raw, fwd_cands = [], []
    for i, c in enumerate(corpus):
        if not c["doi"]:
            continue
        w = openalex_work(c["doi"])
        time.sleep(0.15)
        if not w:
            continue
        wid = (w.get("id") or "").split("/")[-1]
        if not wid:
            continue
        cited_by = ("https://api.openalex.org/works?filter=cites:" + wid)
        page = 1
        while page <= 5:
            try:
                j = http_json(cited_by + f"&per-page=100&page={page}&select=id,doi,title,publication_year,type,primary_location,authorships,biblio,abstract_inverted_index")
            except Exception:
                break
            res = j.get("results", [])
            if not res:
                break
            for ww in res:
                nw = norm_work(ww)
                nw["source_paper"] = c["title"]
                nw["source_grp"] = c["grp"]
                # v1 论文：仅新窗口；新论文：全周期
                if c["grp"] == "v1" and nw["year"] and nw["year"] < "2025":
                    continue
                fwd_raw.append(nw)
            if len(res) < 100:
                break
            page += 1
            time.sleep(0.3)
        if (i + 1) % 20 == 0:
            print(f"  前向进度 {i+1}/{len(corpus)}")
    # 去重
    seen = set()
    for w in fwd_raw:
        key = (w["doi"] or nt(w["title"])).lower()
        if not key or key in seen:
            continue
        seen.add(key)
        in_known = (w["doi"] and w["doi"].lower() in known_doi) or nt(w["title"]) in known_title or nt(w["title"]) in corpus_titles
        if not in_known and w["title"]:
            fwd_cands.append({**w, "direction": "forward"})
    print(f"前向: 原始 {len(fwd_raw)} → 去重 {len(seen)} → 新候选 {len(fwd_cands)}")

    # ---------- 后向引用（34 篇新论文）----------
    bwd_raw, bwd_cands = [], []
    new_papers = [c for c in corpus if c["grp"] == "new"]
    for i, c in enumerate(new_papers):
        if not c["doi"]:
            continue
        w = openalex_work(c["doi"])
        time.sleep(0.15)
        if not w:
            continue
        refs = w.get("referenced_works") or []
        if not refs:
            continue
        for ww in fetch_batch(refs):
            nw = norm_work(ww)
            nw["source_paper"] = c["title"]
            bwd_raw.append(nw)
        if (i + 1) % 10 == 0:
            print(f"  后向进度 {i+1}/{len(new_papers)}")
    seen2 = set()
    for w in bwd_raw:
        key = (w["doi"] or nt(w["title"])).lower()
        if not key or key in seen2:
            continue
        seen2.add(key)
        in_known = (w["doi"] and w["doi"].lower() in known_doi) or nt(w["title"]) in known_title or nt(w["title"]) in corpus_titles
        # 后向仅保留 Docker/容器 相关标题（初筛惯例）
        dockerish = bool(re.search(r"docker|container", w["title"], re.I))
        if not in_known and w["title"] and dockerish:
            bwd_cands.append({**w, "direction": "backward"})
    print(f"后向: 原始 {len(bwd_raw)} → 去重 {len(seen2)} → Docker相关新候选 {len(bwd_cands)}")

    # ---------- 存储原始 ----------
    cols = ["direction", "title", "doi", "year", "type", "venue", "authors",
            "first_page", "last_page", "abstract", "source_paper"]
    for name, data in (("snowballing_forward_raw.csv", fwd_raw), ("snowballing_backward_raw.csv", bwd_raw)):
        with open(OUT / name, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for r in data:
                w.writerow({k: r.get(k, "") for k in cols})

    # ---------- 双人编码 ----------
    overrides = load_overrides()
    coded = []
    for cand in fwd_cands + bwd_cands:
        f = feats(cand)  # 使用标题(+摘要)
        a, b = code_A(f), code_B(f)
        fin, note = adjudicate(f, a, b)
        # 页数门槛（有页数即校验）
        pages = None
        m = re.match(r"^\d{1,6}$", str(cand.get("first_page") or ""))
        if m and cand.get("last_page"):
            try:
                pages = int(cand["last_page"]) - int(cand["first_page"]) + 1
            except Exception:
                pages = None
        flag = ""
        if pages is not None and pages < 5:
            fin = "ex-①"
            note = (note + "; " if note else "") + f"页数门槛: {pages}页<5"
        elif pages is None and fin == "keep":
            flag = "page-verify"
        ov = overrides.get((cand.get("doi") or "").lower())
        if ov:
            fin = ov["code"]
            note = (note + "; " if note else "") + "senior: " + ov.get("note", "")
        coded.append({
            "direction": cand["direction"], "title": cand["title"], "doi": cand["doi"],
            "year": cand["year"], "venue": cand["venue"], "pages": pages if pages else "",
            "coder_A": a, "coder_B": b, "agree": "Y" if a == b else "N",
            "final_code": fin, "flag": flag,
            "resolution": (note + f"; source-cited-by: {cand.get('source_paper','')[:60]}" if cand["direction"] == "forward"
                           else note + f"; source-references-of: {cand.get('source_paper','')[:60]}"),
        })
    if not coded:
        print("⚠ 新候选为 0（候选可能已导入库中致去重归零），为保护既有结果，跳过 coded CSV 写入。")
        return
    with open(OUT / "snowballing_candidates_coded.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(coded[0].keys()) if coded else
                           ["direction", "title", "doi", "year", "venue", "pages",
                            "coder_A", "coder_B", "agree", "final_code", "flag", "resolution"])
        w.writeheader()
        w.writerows(coded)

    keeps = [c for c in coded if c["final_code"] == "keep"]
    summary = [
        f"前向: 原始被引 {len(fwd_raw)} → 新候选 {len(fwd_cands)} → 纳入 {sum(1 for c in keeps if c['direction']=='forward')}",
        f"后向: 原始参考 {len(bwd_raw)} → Docker相关新候选 {len(bwd_cands)} → 纳入 {sum(1 for c in keeps if c['direction']=='backward')}",
        f"合计候选 {len(coded)}，纳入 {len(keeps)}",
        "纳入清单:",
    ] + [f"  [{c['direction']}] {c['title'][:80]} ({c['year']}, {c['venue'][:40]}) [{c['flag'] or 'ok'}]"
         for c in keeps]
    (OUT / "snowballing_summary.txt").write_text("\n".join(summary), encoding="utf-8")
    print("\n".join(summary))
    print("输出: snowballing_candidates_coded.csv / *_raw.csv / snowballing_summary.txt")


if __name__ == "__main__":
    main()
