# -*- coding: utf-8 -*-
"""为 37 篇 v2 新论文生成 bib 条目数据：
- 从 Zotero 快照库取 作者/标题/venue/年/页码/DOI/类型
- 检查 allpapers.bib 是否已有同题条目（复用 key）
- 输出 extraction/v2_new_papers_bib.json 供生成 tex/bib 用
"""
import sqlite3, csv, json, re
from pathlib import Path

WS = Path(r'D:\research-related\Docker_sms_study')
SNAP = WS / 'zotero_snapshot' / 'zotero_copy.sqlite'
LEDGER = WS / 'extraction' / 'wp1_v2_ledger.csv'
BIB = WS / 'overleaf_repo' / 'allpapers.bib'

rows = list(csv.DictReader(open(LEDGER, encoding='utf-8-sig')))
new = [r for r in rows if r['source'] != 'v1']
print('新论文数:', len(new))

con = sqlite3.connect(SNAP)
def item_fields(key):
    r = con.execute("SELECT itemID, itemTypeID FROM items WHERE key=?", (key,)).fetchone()
    if not r: return None
    iid, tid = r
    tname = con.execute("SELECT typeName FROM itemTypes WHERE itemTypeID=?", (tid,)).fetchone()[0]
    f = {'itemType': tname}
    for fn, v in con.execute("""SELECT f.fieldName, idv.value FROM itemData id
        JOIN fields f ON f.fieldID=id.fieldID JOIN itemDataValues idv ON idv.valueID=id.valueID
        WHERE id.itemID=?""", (iid,)):
        f[fn] = v
    crs = con.execute("""SELECT c.firstName, c.lastName, ct.creatorType FROM itemCreators ic
        JOIN creators c ON c.creatorID=ic.creatorID
        JOIN creatorTypes ct ON ct.creatorTypeID=ic.creatorTypeID
        WHERE ic.itemID=? ORDER BY ic.orderIndex""", (iid,)).fetchall()
    f['creators'] = crs
    return f

# allpapers.bib 已有条目标题索引
bib = BIB.read_text(encoding='utf-8', errors='replace')
entries = re.findall(r'@(\w+)\{([^,]+),(.*?)\n\}', bib, re.S)
bib_index = []
for etype, ekey, ebody in entries:
    tm = re.search(r'title\s*=\s*\{((?:[^{}]|\{|\})*?)\}', ebody, re.S)
    title = tm.group(1) if tm else ''
    title = re.sub(r'[{}\\]', ' ', title)
    bib_index.append((ekey.strip(), etype, re.sub(r'\s+', ' ', title).strip().lower()))
print('bib 条目数:', len(bib_index))

def norm(s):
    s = re.sub(r'[^a-z0-9 ]', ' ', s.lower())
    return re.sub(r'\s+', ' ', s).strip()

out = []
for r in new:
    key = r['zotero_key']
    f = item_fields(key)
    if not f:
        print('!! 快照缺失:', key); continue
    t = norm(f.get('title', r['title']))
    # bib 同题匹配（前 60 字符）
    hit = None
    for ekey, etype, etitle in bib_index:
        if etitle and (etitle[:60] == t[:60] or etitle[:45] == t[:45]):
            hit = ekey; break
    out.append({
        'zotero_key': key, 'source': r['source'], 'existing_bib_key': hit,
        'title': f.get('title', r['title']),
        'itemType': f['itemType'],
        'venue': f.get('proceedingsTitle') or f.get('publicationTitle') or r['venue_name'],
        'date': f.get('date', r['year']), 'year': r['year'],
        'pages': f.get('pages', ''), 'volume': f.get('volume', ''),
        'doi': f.get('DOI', r['doi']), 'url': f.get('url', ''),
        'creators': [[c[0] or '', c[1] or '', c[2]] for c in f['creators']],
        'country': r['country'],
    })

json.dump(out, open(WS / 'extraction' / 'v2_new_papers_bib.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print()
print('== 37 篇新论文元数据速览（key | 已有bib key | venue | 年 | 页 | DOI有无）==')
for o in out:
    print(f"{o['zotero_key']} | {o['existing_bib_key'] or '-':28s} | {o['year']} | {(o['venue'] or '')[:38]:38s} | pp={o['pages'] or '-':12s} | doi={'Y' if o['doi'] else 'N'} | 作者数{len(o['creators'])}")
