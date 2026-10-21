#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解析 review.tex 的 SELECTED PRIMARY STUDIES 列表 → P# → (title, venue/year 尾巴)"""
import re
from pathlib import Path

BS = chr(92)
TEX = (Path(__file__).resolve().parent.parent / "src" / "review.tex").read_text(encoding="utf-8")
body = TEX.split("SELECTED PRIMARY STUDIES", 1)[1]
pat = re.compile(BS + BS + r"item\s+" + BS + BS + r"label\{([^}]+)\}(.*?)(?=" + BS + BS + r"item\s+" + BS + BS + r"label\{|" + BS + BS + r"end\{PapersList\})", re.S)
items = []
for m in pat.finditer(body):
    key = m.group(1)
    cit = re.sub(r"\s+", " ", m.group(2))
    t = re.search(r"\u201c(.+?)(?=[,;:!?.]?\u201d)", cit)
    tail = cit.split("[Online]")[0].strip()
    items.append({"n": len(items) + 1, "key": key,
                  "title": t.group(1)[:65] if t else "", "tail": tail[-140:]})
print(f"解析 {len(items)} 篇")
for it in items:
    if it["n"] in (9, 38, 44, 48, 50, 23, 51, 27, 32, 22):
        print(f"P{it['n']} [{it['key']}]")
        print(f"   {it['title']}")
        print(f"   ...{it['tail']}")
        print()
# 同时导出全量供后续
import json
Path("extraction/p_citations.json").write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
print("全量引文已存 extraction/p_citations.json")
