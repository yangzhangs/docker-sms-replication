# -*- coding: utf-8 -*-
"""RQ1 v2 全量重算：映射(zotero_key->P编号) + 6x4 矩阵 + 六主题 + 空胞/稀疏胞 + 时间趋势。
输出 extraction/rq1_v2_stats.json + 控制台摘要。"""
import csv, json, re
from collections import Counter, defaultdict
from pathlib import Path

WS = Path(r'D:\research-related\Docker_sms_study')
OUT = WS / 'extraction' / 'rq1_v2_stats.json'

# 1) label -> P 编号（v2 列表顺序）
body = (WS / 'extraction' / 'v2_paperslist_body.tex').read_text(encoding='utf-8')
labels = re.findall(r'\\item \\label\{([^}]+)\}', body)
label2p = {k: i + 1 for i, k in enumerate(labels)}
assert len(labels) == 92

# 2) zotero_key -> label
pc = [it for it in json.load(open(WS / 'extraction' / 'p_citations.json', encoding='utf-8')) if it['key'] != 'paper:1']
newdata = json.load(open(WS / 'extraction' / 'v2_new_papers_bib.json', encoding='utf-8'))
newmap = {o['zotero_key']: o['new_key'] for o in newdata}

def norm(s):
    s = re.sub(r'[^a-z0-9 ]', ' ', s.lower())
    s = re.sub(r'\s+', ' ', s).strip()
    return s.replace('delta ', '').replace('delta', '')  # \delta-Scalpel 归一化

tex_title2key = {norm(it['title']): it['key'] for it in pc}

rows = [r for r in csv.DictReader(open(WS / 'extraction' / 'extraction_master_94.csv', encoding='utf-8-sig'))
        if not r.get('decision')]
CONC = ['Performance', 'Maintainability', 'Reliability', 'Security', 'Evolution', 'Adoption']
OBJ = ['Specification', 'Build', 'Image', 'Container']

key2label, unmatched = {}, []
for r in rows:
    k = r['zotero_key']
    if k in newmap:
        key2label[k] = newmap[k]
        continue
    t = norm(r['title'])
    hit = tex_title2key.get(t)
    if not hit:
        for kk, v in tex_title2key.items():
            if kk.startswith(t[:55]) or t.startswith(kk[:55]):
                hit = v; break
    if hit:
        key2label[k] = hit
    else:
        unmatched.append((k, r['title'][:60]))
print('映射完成:', len(key2label), '/ 92 | 未匹配:', unmatched)

def tags(s, pool):
    out = set()
    for part in re.split(r'[;,/\s]+', s or ''):
        part = part.strip(';')
        if part in pool:
            out.add(part)
    return out

# 3) 矩阵
matrix = defaultdict(list)      # (concern, object) -> [P...]
concern_p = defaultdict(list); object_p = defaultdict(list)
year_obj = defaultdict(Counter); year_conc = defaultdict(Counter)
no_code = []
for r in rows:
    k = r['zotero_key']; label = key2label.get(k); P = label2p.get(label)
    if P is None:
        print('!! 无 P 的行:', k, '| label=', label, '|', r['title'][:65])
        continue
    cs = tags(r['concerns'], set(CONC)); os_ = tags(r['objects'], set(OBJ))
    if not cs or not os_: no_code.append((k, r['title'][:50], sorted(cs), sorted(os_)))
    for c in cs: concern_p[c].append(P)
    for o in os_: object_p[o].append(P)
    for c in cs:
        for o in os_: matrix[(c, o)].append(P)
    y = r['year']
    if y:
        for o in os_: year_obj[int(y)][o] += 1
        for c in cs: year_conc[int(y)][c] += 1

print('无编码行:', no_code if no_code else '无（Other=0 可说明）')
print()
print('== 6x4 矩阵（计数）==')
print(f'{"":16s}' + ''.join(f'{o[:6]:>8s}' for o in OBJ) + '   row累计(unique)')
row_uniq = {}
for c in CONC:
    row_uniq[c] = set(P for o in OBJ for P in matrix[(c, o)])
    line = f'{c:16s}' + ''.join(f'{len(matrix[(c,o)]):>8d}' for o in OBJ) + f'   {len(row_uniq[c]):>3d}'
    print(line)
print(f'{"col unique":16s}' + ''.join(f'{len(set(P for c in CONC for P in matrix[(c,o)])):>8d}' for o in OBJ))

populated = [(c, o, len(matrix[(c, o)])) for c in CONC for o in OBJ if matrix[(c, o)]]
print()
print('已填充胞数:', len(populated), '/24')
print('空胞:', [f'{c}x{o}' for c in CONC for o in OBJ if not matrix[(c, o)]])
print('稀疏胞(1-2篇):', [f'{c}x{o}={len(matrix[(c,o)])}' for c in CONC for o in OBJ if 0 < len(matrix[(c, o)]) <= 2])
print()
print('== 六大主题（v1 口径: SM/IS/IA/BR/BP/SE）v2 计数 ==')
TOPICS = [('SM', 'Maintainability', 'Specification'), ('IS', 'Security', 'Image'),
          ('IA', 'Adoption', 'Image'), ('BR', 'Reliability', 'Build'),
          ('BP', 'Performance', 'Build'), ('SE', 'Evolution', 'Specification')]
topic_counts = {}
for name, c, o in TOPICS:
    n = len(matrix[(c, o)])
    topic_counts[name] = n
    print(f'  {name}: {n} ({n/92*100:.1f}%)')
others = [(c, o, len(matrix[(c, o)])) for c in CONC for o in OBJ
          if (c, o) not in [(c2, o2) for _, c2, o2 in TOPICS] and len(matrix[(c, o)]) >= 5]
print('  其他 >=5 的胞:', [f'{c}x{o}={n}' for c, o, n in sorted(others, key=lambda x: -x[2])])
print()
print('== 时间趋势（object by year）==')
years = sorted(year_obj)
for y in years:
    row = year_obj[y]
    print(f'  {y}: ' + ' '.join(f'{o[:4]}={row.get(o,0)}' for o in OBJ) + '  | ' + ' '.join(f'{c[:4]}={year_conc[y].get(c,0)}' for c in CONC))

# 输出 JSON（含每胞 P 列表，写表格用）
dump = {
    'labels': labels,
    'matrix': {f'{c}|{o}': sorted(v) for (c, o), v in matrix.items()},
    'concern_p': {c: sorted(concern_p[c]) for c in CONC},
    'object_p': {o: sorted(object_p[o]) for o in OBJ},
    'row_uniq': {c: len(row_uniq[c]) for c in CONC},
    'topic_counts': topic_counts,
    'year_obj': {str(y): dict(v) for y, v in year_obj.items()},
    'year_conc': {str(y): dict(v) for y, v in year_conc.items()},
}
json.dump(dump, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print()
print('已写', OUT)
