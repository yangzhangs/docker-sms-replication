# -*- coding: utf-8 -*-
"""全量筛查 Kappa：v1 重标注表(3,648) + 短文复筛表(1,724) + 增量表(731) 双人编码一致性。"""
import csv, re
from collections import Counter
from pathlib import Path

WS = Path(r'D:\research-related\Docker_sms_study')

def load(f):
    return list(csv.DictReader(open(WS / f, encoding='utf-8-sig')))

sets = {
    'v1_relabel': load('zotero_export/v1_relabel_worksheet.csv'),
    'rescreen': load('zotero_export/v1_shortpaper_rescreen.csv'),
    'increment': load('zotero_export/increment_screening_coded.csv'),
}
for name, rows in sets.items():
    a = sum(1 for r in rows if (r.get('coder_A') or '').strip())
    b = sum(1 for r in rows if (r.get('coder_B') or '').strip())
    both = sum(1 for r in rows if (r.get('coder_A') or '').strip() and (r.get('coder_B') or '').strip())
    print(f'{name}: 行={len(rows)} coderA填={a} coderB填={b} 双填={both}')
    if both:
        cc = Counter(((r.get('coder_A') or '').strip(), (r.get('coder_B') or '').strip()) for r in rows if (r.get('coder_A') or '').strip())
        print('   标签样例:', list(cc.keys())[:6])

def kappa(pairs):
    # pairs: [(a,b)] 标签对（多类）；二值 keep/其余
    n = len(pairs)
    if not n: return None
    po = sum(1 for a, b in pairs if a == b) / n
    ca = Counter(a for a, b in pairs); cb = Counter(b for a, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    k = (po - pe) / (1 - pe) if pe != 1 else 1.0
    return po, k, n

def binary(pairs):
    m = lambda x: 'keep' if x.lower().startswith('keep') else ('keep-review' if '复核' in x else 'exclude')
    return kappa([(m(a), m(b)) for a, b in pairs])

print()
print('=== 分集合与合并 Kappa ===')
allpairs = []
for name, rows in sets.items():
    pairs = [((r.get('coder_A') or '').strip(), (r.get('coder_B') or '').strip())
             for r in rows if (r.get('coder_A') or '').strip() and (r.get('coder_B') or '').strip()]
    if not pairs:
        print(f'{name}: 无有效双人编码，跳过')
        continue
    po, k, n = kappa(pairs)
    print(f'{name}: n={n} 多类 Po={po:.3f} Kappa={k:.3f}')
    m = lambda x: 'keep' if x.lower().startswith('keep') else 'exclude'
    po2, k2, n2 = kappa([(m(a), m(b)) for a, b in pairs])
    print(f'        二值 Po={po2:.3f} Kappa={k2:.3f}')
    allpairs += pairs

if allpairs:
    po, k, n = kappa(allpairs)
    print(f'合并: n={n} 多类 Po={po:.3f} Kappa={k:.3f}')
    from collections import Counter as C
    print('  合并标签分布(A):', dict(C(a for a, b in allpairs).most_common()))
