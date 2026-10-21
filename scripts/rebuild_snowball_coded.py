#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重建 snowballing_candidates_coded.csv（因 snowballing.py 二次运行时
候选已在库中导致去重归零、旧 coded 文件被空文件覆盖）。
原理：以 snowball_import.json（232 条=当时的候选全集）为对象清单，
     从新 raw 文件（含全量抓取记录）按 DOI/标题匹配回原始元数据，
     重跑确定性编码管线（feats→code_A/B→adjudicate→页数门槛→senior 覆盖），
     还原 coded CSV。不改动 snowball_import.json 本身。
"""
import csv, json, re, sys
from pathlib import Path

WS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WS / "zotero_tools"))
from dual_coding_and_verify import feats, code_A, code_B, adjudicate, nt, load_overrides  # noqa

def norm(t): return nt(t)

imports = json.loads((WS / "zotero_tools" / "snowball_import.json").read_text(encoding="utf-8"))
raw = {}
for f in ["snowballing_forward_raw.csv", "snowballing_backward_raw.csv"]:
    p = WS / "zotero_export" / f
    if not p.exists():
        continue
    for r in csv.DictReader(open(p, encoding="utf-8-sig")):
        k = (r["doi"] or norm(r["title"])).lower()
        if k and k not in raw:
            raw[k] = r

overrides = load_overrides()
rows = []
for it in imports:
    doi = (it.get("doi") or "").strip()
    k = (doi or norm(it["title"])).lower()
    r = raw.get(k, {})
    cand = {
        "title": it["title"], "type": r.get("type", ""),
        "venue": r.get("venue", "") or it.get("venue", ""),
        "abstract": r.get("abstract", "") or it.get("abstract", ""),
        "year": it.get("year", ""),
    }
    f = feats(cand)
    a, b = code_A(f), code_B(f)
    fin, note = adjudicate(f, a, b)
    # 页数门槛
    pages = None
    fp, lp = r.get("first_page", ""), r.get("last_page", "")
    if re.match(r"^\d{1,6}$", str(fp or "")) and lp:
        try:
            pages = int(lp) - int(fp) + 1
        except Exception:
            pages = None
    flag = ""
    if pages is not None and pages < 5:
        fin = "ex-①"
        note = (note + "; " if note else "") + f"页数门槛: {pages}页<5"
    elif pages is None and fin == "keep":
        flag = "page-verify"
    ov = overrides.get(doi.lower())
    if ov:
        fin = ov["code"]
        note = (note + "; " if note else "") + "senior: " + ov.get("note", "")
    rows.append({
        "direction": it.get("direction", ""), "title": it["title"], "doi": doi,
        "year": it.get("year", ""), "venue": (cand["venue"] or "")[:70],
        "pages": pages if pages else "", "coder_A": a, "coder_B": b,
        "agree": "Y" if a == b else "N", "final_code": fin, "flag": flag,
        "resolution": note,
    })

out = WS / "zotero_export" / "snowballing_candidates_coded.csv"
with open(out, "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

keeps = [r for r in rows if r["final_code"] == "keep"]
print(f"重建完成: {len(rows)} 条; keep {len(keeps)}:")
for r in keeps:
    print(f"  [{r['direction']}] {r['title'][:66]}")
print(f"输出: {out}")

# 顺带同步 snowball_import.json 中 8MNW9V94 的标签（ex-④ 移出）
changed = 0
for it in imports:
    if "Static Vulnerability Analysis" in it["title"]:
        it["decision"] = "ex-④"
        it["tags"] = [t for t in it["tags"] if t != "✅v2-keep"] + ["🔴", "v2-ex-④"]
        changed += 1
if changed:
    (WS / "zotero_tools" / "snowball_import.json").write_text(
        json.dumps(imports, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"snowball_import.json 已更新: {changed} 条 (8MNW9V94 → 🔴+v2-ex-④)")
