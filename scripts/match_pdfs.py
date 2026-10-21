#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 内容自动识别器（v2 新增论文 PDF 自动对应）
用途：团队成员下载的 PDF 无需手动改名——把任意文件名的 PDF 丢进
      replication_package/corpus_v2_pdfs/，运行本脚本即可：
        ① 读取 PDF 首页文本与元数据 → 提取 DOI / 标题候选
        ② 匹配 Zotero 库（DOI 精确 → 标题规范化精确 → 标题模糊≥0.85）
        ③ 匹配成功 → 重命名为 <zotero_key>.pdf（原文件名记入日志）
      之后在 Zotero 跑 zotero_attach_pdfs.js 即可自动挂接。

用法：python zotero_tools/match_pdfs.py [--dry-run]
输出：zotero_export/pdf_match_log.csv（原文件名/匹配key/标题/方法/相似度）
     未匹配的文件保留原名并列入报告，供人工处理。
"""
import argparse
import csv
import re
import sqlite3
import sys
from difflib import SequenceMatcher
from pathlib import Path

WS = Path(__file__).resolve().parent.parent
PDF_DIR = WS / "replication_package" / "corpus_v2_pdfs"
SNAP = WS / "zotero_snapshot" / "zotero_copy.sqlite"
LOG = WS / "zotero_export" / "pdf_match_log.csv"

DOI_RX = re.compile(r"\b10\.\d{4,9}/[^\s\"'<>,;)\]}]+")
KEY_RX = re.compile(r"^[A-Z0-9]{8}$")


def nt(t):
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


def clean_doi(d):
    return re.sub(r"[.,;:)\]}]+$", "", d).strip().lower()


def pdf_texts(path: Path, max_pages=2):
    """返回 (首页文本, 元数据标题, 大字号标题候选)"""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        sys.exit("需要 PyMuPDF（pip install pymupdf）")
    doc = fitz.open(str(path))
    txt = ""
    title_cands = []
    try:
        meta_title = (doc.metadata or {}).get("title", "") or ""
        for pno in range(min(max_pages, len(doc))):
            page = doc[pno]
            txt += page.get_text("text") + "\n"
            if pno == 0:
                d = page.get_text("dict")
                spans = []
                for b in d.get("blocks", []):
                    for l in b.get("lines", []):
                        for s in l.get("spans", []):
                            t = (s.get("text") or "").strip()
                            if len(t) > 8:
                                spans.append((s.get("size", 0), t))
                spans.sort(key=lambda x: -x[0])
                title_cands = [t for _, t in spans[:6]]
    finally:
        doc.close()
    return txt, meta_title, title_cands


def load_library_index():
    con = sqlite3.connect(f"file:{SNAP.as_posix()}?mode=ro", uri=True)
    cur, cur2 = con.cursor(), con.cursor()
    # 语料优先集合：语料收藏夹 + v2 标记（多副本时优先挂到语料实际使用的条目）
    preferred = set()
    for cid, in cur.execute("SELECT collectionID FROM collections WHERE collectionName LIKE '1最终文献-v2%'").fetchall():
        for (iid,) in cur2.execute("SELECT itemID FROM collectionItems WHERE collectionID=?", (cid,)).fetchall():
            preferred.add(iid)
    for (iid,) in cur2.execute("""SELECT DISTINCT it.itemID FROM itemTags it JOIN tags t ON t.tagID=it.tagID
            WHERE t.name IN ('corpus-v2-new','corpus-v1','✅v2-keep')""").fetchall():
        preferred.add(iid)

    by_doi, by_title, key2title = {}, {}, {}
    rows = cur.execute("SELECT itemID, key FROM items WHERE itemID NOT IN (SELECT itemID FROM deletedItems)").fetchall()
    # 两遍：先非优先，后优先覆盖
    for pass_pref in (False, True):
        for iid, key in rows:
            if (iid in preferred) != pass_pref:
                continue
            d = cur2.execute("""SELECT v.value FROM itemData d JOIN itemDataValues v ON v.valueID=d.valueID
                JOIN fields f ON f.fieldID=d.fieldID WHERE d.itemID=? AND f.fieldName='DOI'""", (iid,)).fetchone()
            if d and d[0]:
                if pass_pref: by_doi[clean_doi(d[0])] = key
                else: by_doi.setdefault(clean_doi(d[0]), key)
            t = cur2.execute("""SELECT v.value FROM itemData d JOIN itemDataValues v ON v.valueID=d.valueID
                JOIN fields f ON f.fieldID=d.fieldID WHERE d.itemID=? AND f.fieldName='title'""", (iid,)).fetchone()
            if t and t[0]:
                key2title[key] = t[0]
                if pass_pref: by_title[nt(t[0])] = (key, t[0])
                else: by_title.setdefault(nt(t[0]), (key, t[0]))
    con.close()
    return by_doi, by_title, key2title


def match_pdf(path: Path, by_doi, by_title, key2title):
    txt, meta_title, cands = pdf_texts(path)
    txt_norm = nt(txt)
    # ① DOI
    for m in DOI_RX.finditer(txt):
        doi = clean_doi(m.group(0))
        if doi in by_doi:
            k = by_doi[doi]
            return k, key2title.get(k, ""), "doi", 1.0
    # ② 标题候选规范化精确（含文件名——覆盖扫描版 PDF）
    fname_cand = re.sub(r'[_]+', ' ', path.stem)
    fname_cand = re.sub(r'^\d+-s2\.0-[A-Z0-9]+-main$', '', fname_cand)  # Elsevier 下载名无信息
    pool = [meta_title, fname_cand] + cands + [l.strip() for l in txt.splitlines()[:25]]
    for c in pool:
        if len(nt(c)) >= 20 and nt(c) in by_title:
            k, t = by_title[nt(c)]
            return k, t, "title-exact", 1.0
    # ③ 模糊（对库内标题取最佳）
    best = (0.0, None, "")
    seen = set()
    for c in pool:
        nc = nt(c)
        if len(nc) < 18 or nc in seen:
            continue
        seen.add(nc)
        for t_key, (k, t) in by_title.items():
            if abs(len(t_key) - len(nc)) > 40:
                continue
            r = SequenceMatcher(None, nc, t_key).ratio()
            if r > best[0]:
                best = (r, k, t)
        # 包含关系加分（标题被拆行等情况）
        if best[0] < 0.9:
            for t_key, (k, t) in by_title.items():
                if len(t_key) >= 25 and t_key in txt_norm:
                    best = (0.98, k, t)
                    break
    if best[0] >= 0.85 and best[1]:
        return best[1], best[2], "title-fuzzy", best[0]
    return None, best[2], "unmatched", best[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只报告不重命名")
    args = ap.parse_args()

    if not PDF_DIR.exists():
        sys.exit(f"目录不存在: {PDF_DIR}")
    files = [p for p in PDF_DIR.glob("*.pdf") if not KEY_RX.match(p.stem)]
    print(f"待识别 PDF: {len(files)} 个（已按 key 命名的会自动跳过）")
    if not files:
        print("没有需要识别的文件。")
        return
    by_doi, by_title, key2title = load_library_index()
    print(f"库索引: DOI {len(by_doi)} / 标题 {len(by_title)}")

    rows, ok, bad = [], 0, 0
    for p in files:
        try:
            key, title, method, score = match_pdf(p, by_doi, by_title, key2title)
        except Exception as e:
            key, title, method, score = None, "", f"error:{type(e).__name__}", 0.0
        status = ""
        if key:
            target = PDF_DIR / f"{key}.pdf"
            if target.exists():
                status = "目标已存在(跳过重命名)"
            elif args.dry_run:
                status = f"将重命名为 {key}.pdf"
            else:
                p.rename(target)
                status = f"已重命名 -> {key}.pdf"
            ok += 1
        else:
            bad += 1
            status = "未匹配，请人工处理"
        rows.append({"file": p.name, "matched_key": key or "", "matched_title": title[:90],
                     "method": method, "score": f"{score:.2f}" if score else "", "status": status})
        print(f"  [{method:12s} {score:.2f}] {p.name[:60]}")
        print(f"        → {title[:80] if title else '(无)'} {('['+key+']') if key else ''}")

    with open(LOG, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\n完成: 匹配 {ok} / 未匹配 {bad}；日志: {LOG}")
    print("下一步：在 Zotero 运行 zotero_attach_pdfs.js 自动挂接。")


if __name__ == "__main__":
    main()
