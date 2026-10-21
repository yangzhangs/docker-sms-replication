# -*- coding: utf-8 -*-
"""Wave-3 步骤2b：PRISMA 漏斗 + 饱和度曲线（修正版：ASCII 标签、两列布局、无碰撞）。"""
import csv
from collections import Counter, defaultdict
from pathlib import Path
import pymupdf

WS = Path(r'D:\research-related\Docker_sms_study')
OUT = WS / 'src' / 'plot'
PREV = WS / 'figs_work' / 'preview'

def hx(h): return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
BLUE = hx('#4472C4'); ORANGE = hx('#ED7D31'); GREY = hx('#D9D9D9'); DARK = hx('#333333')
BG = hx('#F2F6FC'); BORDER = hx('#9DB4D6'); GREEN = hx('#E2EFDA'); GB = hx('#77A85E'); RED = hx('#B03A2E')
def tl(s, fs): return pymupdf.get_text_length(s, fontname='tiro', fontsize=fs)
def txt(page, H, x, y_math, s, fs=9, color=DARK, align='left'):
    if align == 'center': x -= tl(s, fs) / 2
    elif align == 'right': x -= tl(s, fs)
    page.insert_text((x, H - y_math), s, fontname='tiro', fontsize=fs, color=color)

KEEP20 = {r['zotero_key'] for r in csv.DictReader(open(WS / 'extraction' / 'wp1_v2_ledger.csv', encoding='utf-8-sig'))
          if r['source'] == 'shortpaper'}
rel = list(csv.DictReader(open(WS / 'zotero_export' / 'v1_relabel_worksheet.csv', encoding='utf-8-sig')))
c_all = Counter(r['final_code'] for r in rel)
c_rec = Counter(r['final_code'] for r in rel if r['zotero_key'] in KEEP20)
net = {k: c_all[k] - c_rec.get(k, 0) for k in c_all}

W, H = 520, 320
doc = pymupdf.open()
pg = doc.new_page(width=W, height=H)

def box(x, y0, w, h, title, subs=(), fill=BG, border=BORDER, tfs=9.2, sfs=7.4, tcolor=DARK):
    sh = pg.new_shape(); sh.draw_rect(pymupdf.Rect(x, y0, x + w, y0 + h)); sh.finish(fill=fill, color=border, width=0.8); sh.commit()
    txt(pg, H, x + w / 2, H - (y0 + 12), title, tfs, tcolor, 'center')
    for i, s in enumerate(subs):
        txt(pg, H, x + w / 2, H - (y0 + 24 + i * 10), s, sfs, DARK, 'center')

def arrow(x, y1, y2):
    sh = pg.new_shape(); sh.draw_line((x, y1), (x, y2 - 4))
    sh.draw_line((x - 3.5, y2 - 5), (x, y2)); sh.draw_line((x + 3.5, y2 - 5), (x, y2))
    sh.finish(color=DARK, width=0.9, lineJoin=1); sh.commit()

# 左列：初始轮
box(15, 8, 232, 40, 'Records identified: 3,650',
    ('ACM 1,014 · IEEE 1,790 · Springer 258', 'ScienceDirect 441 · WILEY 147'))
arrow(131, 48, 62)
box(15, 62, 232, 30, 'Bibliographic filters: 3,013', ('subject area · language · publication type',))
arrow(131, 92, 106)
box(15, 106, 232, 48, 'Dual-author screening',
    ('two coders, full records; consensus on disagreements',
     f"Excluded (dominant reason): no SE contribution {net['ex-⑤']:,}",
     f"non-SE {net['ex-⑥']:,} · short/non-archival {net['ex-①']:,} · review {net['ex-④']:,}"),
    tfs=9.0, sfs=7.3)
arrow(131, 154, 172)
box(15, 172, 232, 28, 'Initial round: 56 primary studies')
arrow(131, 200, 258)

# 右列：修订轮
box(262, 8, 243, 40, 'Update searches: 731 → +14  (2025-12 to 2026-09)',
    ('Excluded: no SE contribution 520 · non-SE 144 · venue type 35', 'review 9 · short/non-archival 9'))
box(262, 62, 243, 54, 'Re-screening under revised criteria: +20',
    ('1,724 page-excluded records + 54 flagged short papers', 're-evaluated in full text;',
     'Excluded: no SE contribution 991 · short/non-archival 456 · non-SE 272 · review 4'), tfs=8.6)
box(262, 130, 243, 44, 'Snowballing (backward / forward): 232 → +3',
    ('Excluded: no SE contribution 151 · short 40 · venue type 16', 'review 13 · non-SE 8'))
box(262, 188, 243, 44, 'Google Scholar extension: 990 → +0',
    ('corpus overlap decays 74% → 11% across rank segments;', 'no additional primary studies'))

# 底部汇总
sh = pg.new_shape(); sh.draw_rect(pymupdf.Rect(120, 258, 400, 300)); sh.finish(fill=GREEN, color=GB, width=1.0); sh.commit()
txt(pg, H, 260, H - 274, 'Final corpus: 92 primary studies', 10, DARK, 'center')
txt(pg, H, 260, H - 288, '56 − 1 (conference version replaced by journal extension) + 14 + 20 + 3', 7.4, DARK, 'center')
arrow(131, 236, 258)
doc.save(str(OUT / 'process.pdf')); doc.close()
print('process.pdf 重绘完成')

# 饱和度曲线
cls = list(csv.DictReader(open(WS / 'replication_package' / 'dedup' / 'GoogleScholar_top990_notincorpus_classified.csv', encoding='utf-8-sig')))
notin = defaultdict(int)
for r in cls:
    notin[(int(float(r['rank'])) - 1) // 100] += 1
segs = []
for d in range(10):
    seg = 100 if d < 9 else 90
    segs.append((d * 100 + 1, seg - notin.get(d, 0), 100 * (seg - notin.get(d, 0)) / seg))

W2, H2 = 310, 150
doc = pymupdf.open(); pg = doc.new_page(width=W2, height=H2)
left, right, top, bottom = 30, 14, 8, 26
pw, ph = W2 - left - right, H2 - top - bottom
sh = pg.new_shape()
for gy in range(0, 101, 25):
    y = H2 - bottom - ph * gy / 100
    sh.draw_line((left, y), (left + pw, y))
sh.finish(color=GREY, width=0.6)
sh.draw_rect(pymupdf.Rect(left, H2 - bottom - ph, left + pw, H2 - bottom)); sh.finish(color=hx('#BFBFBF'), width=0.6)
sh.commit()
pts = []
for i, (a, inn, pct) in enumerate(segs):
    x = left + pw * (i + 0.5) / 10
    pts.append((x, H2 - bottom - ph * pct / 100))
sh = pg.new_shape()
sh.draw_line(pts[0], pts[0])
for i in range(len(pts) - 1):
    sh.draw_line(pts[i], pts[i + 1])
sh.finish(color=BLUE, width=1.5); sh.commit()
sh = pg.new_shape()
for (x, y) in pts:
    sh.draw_circle(pymupdf.Point(x, y), 2.0)
sh.finish(fill=BLUE, color=BLUE); sh.commit()
for (x, y), (a, inn, pct) in zip(pts, segs):
    txt(pg, H2, x + 5, H2 - y + 1, f'{pct:.0f}', 7, DARK)
for gy in range(0, 101, 25):
    y = bottom + ph * gy / 100
    txt(pg, H2, left - 4, y - 3, f'{gy}%', 7.5, DARK, 'right')
for i in range(10):
    x = left + pw * (i + 0.5) / 10
    if i % 2 == 0:
        txt(pg, H2, x, 12, f'{i*100+1}', 7, DARK, 'center')
txt(pg, H2, left + pw / 2, 2.5, 'Google Scholar rank (decile start)', 7.5, DARK, 'center')
for pos, lab in ((2.0, 'top-200'), (5.0, 'top-500')):
    x = left + pw * pos / 10
    sh = pg.new_shape(); sh.draw_line((x, H2 - bottom - ph + 2), (x, bottom)); sh.finish(color=ORANGE, width=0.7, dashes='[2 2] 0'); sh.commit()
    txt(pg, H2, x + 1.5, H2 - top - 12, lab, 6.6, ORANGE)
doc.save(str(OUT / 'saturation.pdf')); doc.close()
print('saturation.pdf 重绘完成')

for name in ['process', 'saturation']:
    d = pymupdf.open(str(OUT / f'{name}.pdf')); d[0].get_pixmap(dpi=150).save(str(PREV / f'{name}_v2.png')); d.close()
print('预览已更新')
