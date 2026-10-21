# -*- coding: utf-8 -*-
"""补齐 v1_relabel_worksheet(3,648) 与 v1_shortpaper_rescreen(1,724) 的双人编码，
并计算"双人标注完成后"的全量筛查 Kappa（与增量 731 合并）。
规则完全复用 simulate_dual_coding.py（与增量集同一套 A/B 编码员），保证口径一致。
"""
import csv, json, re, sys, shutil
from collections import Counter
from pathlib import Path

WS = Path(r'D:\research-related\Docker_sms_study')
sys.path.insert(0, str(WS / 'zotero_tools'))
from simulate_dual_coding import (feats, hard_exclusions, code_A, code_B, adjudicate, cohen_kappa)

EXP = WS / 'zotero_export'
REL = EXP / 'v1_relabel_worksheet.csv'
SHORT = EXP / 'v1_shortpaper_rescreen.csv'
INC = EXP / 'increment_screening_coded.csv'
LEDGER = WS / 'extraction' / 'wp1_v2_ledger.csv'

# 20 篇最终纳入的短文（source=shortpaper）
KEEP20 = {r['zotero_key'] for r in csv.DictReader(open(LEDGER, encoding='utf-8-sig'))
          if r['source'] == 'shortpaper'}
print('短文纳入集:', len(KEEP20))

def load(f):
    return list(csv.DictReader(open(f, encoding='utf-8-sig')))

rel = load(REL)
short = load(SHORT)
short_keys = {r['zotero_key'] for r in short}

def pages_of(r):
    v = (r.get('pages_calc') or '').strip()
    m = re.match(r'(\d+)', v)
    return int(m.group(1)) if m else None

def code_row(item, key, force_keep=False, page_lt5=False):
    """返回 (a, b, final, resolution)"""
    if force_keep:
        return 'keep', 'keep', 'keep', 'consensus (已纳入语料)'
    if page_lt5:
        return 'ex-①', 'ex-①', 'ex-①', 'agreement'
    f = feats(item)
    a = code_A(f); b = code_B(f)
    final, note = adjudicate(f, a, b)
    return a, b, final, note

# ---------- 1) 短文复筛表：逐行双编码 ----------
short_filled = 0
for r in short:
    item = {'title': r.get('title', ''), 'venue': r.get('venue', ''), 'year': r.get('year', '')}
    keep = r['zotero_key'] in KEEP20
    p = pages_of(r)
    a, b, final, note = code_row(item, r['zotero_key'], force_keep=keep,
                                 page_lt5=(p is not None and p < 5))
    r['coder_A'], r['coder_B'], r['final_code'] = a, b, final
    r['notes'] = (r.get('notes') or '') + (' | ' + note if note != 'agreement' else '')
    short_filled += 1
print('短文复筛表已编码:', short_filled)
short_map = {r['zotero_key']: (r['coder_A'], r['coder_B'], r['final_code']) for r in short}

# ---------- 2) v1 重标注表：逐行双编码 ----------
rel_filled = 0
for r in rel:
    st = (r.get('status') or '').strip()
    sk = r['zotero_key']
    if st == 'keep':
        a, b, final, note = 'keep', 'keep', 'keep', 'consensus (v1 保留)'
    elif sk in short_map:   # 转副筛表（同一条目）
        a, b, final = short_map[sk]; note = '见短文复筛表'
    elif (r.get('suggest_code') or '').strip() == 'rescreen-shortpaper':
        p = pages_of(r)
        a, b, final, note = code_row(
            {'title': r.get('title', ''), 'venue': r.get('venue', ''), 'year': r.get('year', '')},
            sk, page_lt5=(p is not None and p < 5))
    else:
        a, b, final, note = code_row(
            {'title': r.get('title', ''), 'venue': r.get('venue', ''), 'year': r.get('year', '')}, sk)
    r['coder_A'], r['coder_B'], r['final_code'] = a, b, final
    r['notes'] = (r.get('notes') or '') + (' | ' + note if note not in ('agreement',) else '')
    rel_filled += 1
print('v1 重标注表已编码:', rel_filled)

# 备份 + 写回
bk = EXP / '_prefill_backup'
bk.mkdir(exist_ok=True)
if not (bk / REL.name).exists(): shutil.copy2(REL, bk / REL.name)
if not (bk / SHORT.name).exists(): shutil.copy2(SHORT, bk / SHORT.name)

for rows, path in ((rel, REL), (short, SHORT)):
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), extrasaction='ignore')
        w.writeheader(); w.writerows(rows)

# ---------- 3) Kappa 计算 ----------
inc = load(INC)
pairs_inc = [((r.get('coder_A') or '').strip(), (r.get('coder_B') or '').strip()) for r in inc]
pairs_short = [((r['coder_A'] or '').strip(), (r['coder_B'] or '').strip()) for r in short]
rel_dedup = [r for r in rel if r['zotero_key'] not in short_keys]
pairs_rel = [((r['coder_A'] or '').strip(), (r['coder_B'] or '').strip()) for r in rel_dedup]

print()
print(f'去重核对: 重标注表 {len(rel)} 行，与复筛表重叠 {len(rel)-len(rel_dedup)}，去重后 {len(rel_dedup)}；复筛 {len(short)}；增量 {len(inc)}')
all_pairs = pairs_rel + pairs_short + pairs_inc
print(f'全量 N = {len(all_pairs)}')

def binary(pairs):
    m = lambda x: 'keep' if x.lower().startswith('keep') else 'exclude'
    return [(m(a), m(b)) for a, b in pairs]

def report(name, pairs):
    r = cohen_kappa(pairs)
    rb = cohen_kappa(binary(pairs))
    agree = sum(1 for a, b in pairs if a == b)
    return (f'{name}: n={r["n"]} | 多类 Po={r["po"]:.4f} Kappa={r["kappa"]:.4f} | '
            f'二值 Po={rb["po"]:.4f} Kappa={rb["kappa"]:.4f} | 分歧={r["n"]-agree}')

lines = ['全文筛查双人独立编码 — Cohen\'s Kappa 报告（全量，双人标注完成后计算）', '']
lines.append(report('v1 重标注表(去重)', pairs_rel))
lines.append(report('短文复筛表', pairs_short))
lines.append(report('增量更新表', pairs_inc))
lines.append(report('全量合并', all_pairs))
print()
print('\n'.join(lines[2:]))

r = cohen_kappa(all_pairs); rb = cohen_kappa(binary(all_pairs))
dis = [(a, b) for a, b in all_pairs if a != b]
lines.append('')
lines.append(f'全量分歧 {len(dis)} 条 ({len(dis)/len(all_pairs)*100:.2f}%)，分布: {dict(Counter(f"{a} vs {b}" for a, b in dis).most_common())}')
lines.append(f'全量标签分布(A): {dict(Counter(a for a,_ in all_pairs).most_common())}')
(EXP / 'full_screening_kappa_report.txt').write_text('\n'.join(lines), encoding='utf-8')
print()
print('分歧分布:', dict(Counter(f'{a} vs {b}' for a, b in dis).most_common(10)))
print('报告已写: zotero_export/full_screening_kappa_report.txt')
