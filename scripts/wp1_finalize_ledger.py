# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
"""WP1 阶段二终版：
1. 写入 author_type / author_evidence（人工裁定后的结果）
2. 修正国家 I3F27YWX: China->United States；W63WUQ47: Canada->Switzerland
3. 修正 CORE：QMUM5QD7=ICSOC 2020 -> A；AG7QMZEA=ICPADS 2020 -> B
4. 输出全部聚合统计 + venue 归一化的 top-15
5. 写 extraction/wp1_v2_stats_final.md
"""
import csv, re
from pathlib import Path
from collections import Counter
WS = Path(r'D:\research-related\Docker_sms_study')
LEDGER = WS / 'extraction' / 'wp1_v2_ledger.csv'
rows = list(csv.DictReader(open(LEDGER, encoding='utf-8-sig')))

BOTH = {'J5GRW3LM', '8GTK9IUC', 'MESDXCFG', 'YGZZA8WT', 'BC3IEXSR', '74KFZIN9', 'I3F27YWX'}
INDUSTRY = {'QMUM5QD7'}
# 证据备注
EV = {
    'J5GRW3LM': 'UZH + IBM T.J. Watson Research (witternj@us.ibm.com)',
    '8GTK9IUC': 'UW-Madison/Colorado State/Penn State + Tala Security (talasecurity.io)',
    'MESDXCFG': 'Virginia Tech + IBM Research Almaden + Apple',
    'YGZZA8WT': 'Univ. of Maryland + Google Research (osuciu@google.com)',
    'BC3IEXSR': 'UW-Madison + Microsoft Research (Christian.Bird@microsoft.com)',
    '74KFZIN9': 'UMONS/URJC + Bitergia (valcos@bitergia.com)',
    'I3F27YWX': 'UW-Madison + Microsoft Research (ICSE 2020; 注意：现附件PDF为错误论文)',
    'QMUM5QD7': 'FUJITSU LABORATORIES LTD. 全员 (kitajima.shinya/sekia@fujitsu.com)',
    '32U23T23': '国家级研究机构(中国计算机系统工程研究所)，按v1口径计入Academia [团队可复核]',
}

for r in rows:
    k = r['zotero_key']
    r['author_type'] = 'Industry' if k in INDUSTRY else ('Both' if k in BOTH else 'Academia')
    r['author_evidence'] = EV.get(k, '')
    if k == 'I3F27YWX':
        r['country'] = 'United States'
        r['notes'] = (r['notes'] + ' | 国家修正: 首作者 Henkel@UW-Madison 美国；原China系误读错误附件PDF' ).strip(' |')
    if k == 'W63WUQ47':
        r['country'] = 'Switzerland'
    if k == 'QMUM5QD7':
        r['core'] = 'A'   # ICSOC 2020
    if k == 'AG7QMZEA':
        r['core'] = 'B'   # ICPADS 2020

with open(LEDGER, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), extrasaction='ignore')
    w.writeheader()
    w.writerows(rows)

# ---------- aggregates ----------
pub = Counter(r['publisher'] for r in rows)
vt = Counter(r['venue_type'] for r in rows)
at = Counter(r['author_type'] for r in rows)
cn = Counter(r['country'] for r in rows)
core = Counter(r['core'] for r in rows)
yr = Counter(int(r['year']) for r in rows)
yr_vt = Counter((int(r['year']), r['venue_type']) for r in rows)
src = Counter(r['source'] for r in rows)

# venue canon（顺序敏感：长/特化规则在前）
from venue_canon import canon

ven = Counter(canon(r['venue_name']) for r in rows)

def pct(n, d=92): return f'{n} ({n/d*100:.1f}%)'

lines = []
lines.append('# WP1 阶段二：v2 数字台账终版（92 篇，数据源 extraction_master_94.csv + wp1_v2_ledger.csv）\n')
lines.append('## 0. 语料构成（PRISMA）')
lines.append(f'- 总样本：{sum(src.values())} 篇 = v1 保留 {src.get("v1",0)} + 增量检索 {src.get("increment",0)} + 短文重筛 {src.get("shortpaper",0)} + 滚雪球 {src.get("snowball",0)}')
lines.append('- 注：v1 56 篇中 P43 因期刊扩展版替换会议版被剔除（ex-③），v1 实计 55 篇；新增 2026 在线发表 11 篇。\n')
lines.append('## 1. 出版商 (Publisher)')
for k, v in pub.most_common():
    lines.append(f'- {k}: {pct(v)}')
lines.append('')
lines.append('## 2. 作者类型 (Author type)')
for k in ['Academia', 'Both', 'Industry']:
    lines.append(f'- {k}: {pct(at.get(k,0))}')
lines.append('')
lines.append('## 3. 场馆类型 (Venue type)')
lines.append(f'- Conference: {pct(vt.get("conference",0))}')
lines.append(f'- Journal: {pct(vt.get("journal",0))}')
lines.append('')
lines.append('## 4. 国家 (首作者单位, 共 %d 国)' % len(cn))
for k, v in cn.most_common():
    lines.append(f'- {k}: {v}')
top4 = sum(v for _, v in cn.most_common(4))
lines.append(f'- 前四国合计：{top4} ({top4/92*100:.1f}%)')
lines.append('')
lines.append('## 5. 年份 × 场馆类型')
for y in sorted(yr):
    c = yr_vt.get((y, 'conference'), 0)
    j = yr_vt.get((y, 'journal'), 0)
    lines.append(f'- {y}: {yr[y]} （会 {c} / 刊 {j}）')
lines.append('')
lines.append('## 6. 场馆 Top-15')
for k, v in ven.most_common(15):
    lines.append(f'- {k}: {v}')
top10 = sum(v for _, v in ven.most_common(10))
lines.append(f'- Top-10 合计：{top10} ({top10/92*100:.1f}%)')
lines.append('')
lines.append('## 7. CORE 等级')
for k, v in core.most_common():
    lines.append(f'- {k}: {pct(v)}')
lines.append('')
txt = '\n'.join(lines)
(WS / 'extraction' / 'wp1_v2_stats_final.md').write_text(txt, encoding='utf-8')
print(txt)
