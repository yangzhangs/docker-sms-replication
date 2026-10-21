# -*- coding: utf-8 -*-
"""Regenerate the Google Scholar saturation curve (screened depth: top 500) into figures/.

Input : common/search/dedup/GoogleScholar_top990_notincorpus_classified.csv
Output: common/search/figures/gs_saturation.pdf + .png
Requires: Python 3 + PyMuPDF (pymupdf).
"""
import csv
from collections import defaultdict
from pathlib import Path
import pymupdf

PKG = Path(__file__).resolve().parents[2]

def hx(h): return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
BLUE = hx('#4C72B0'); ORANGE = hx('#C44E52'); GREY = hx('#E8E8E8'); DARK = hx('#333333'); NUM = (0, 0, 0)

def txt(page, H, x, y_math, s, fs=8.5, color=DARK, align='left'):
    if align == 'center': x -= pymupdf.get_text_length(s, fontname='tiro', fontsize=fs) / 2
    elif align == 'right': x -= pymupdf.get_text_length(s, fontname='tiro', fontsize=fs)
    page.insert_text((x, H - y_math), s, fontname='tiro', fontsize=fs, color=color)

cls = list(csv.DictReader(open(PKG / 'common' / 'search' / 'dedup' / 'GoogleScholar_top990_notincorpus_classified.csv', encoding='utf-8-sig')))
notin = defaultdict(int)
for r in cls:
    notin[(int(float(r['rank'])) - 1) // 100] += 1
NDEC = 5  # top-500 screened depth, 100-record segments
segs = [(d * 100 + 1, 100 - notin.get(d, 0)) for d in range(NDEC)]

W2, H2 = 310, 162
doc = pymupdf.open(); pg = doc.new_page(width=W2, height=H2)
left, right, top, bottom = 34, 14, 22, 26
pw, ph = W2 - left - right, H2 - top - bottom
sh = pg.new_shape()
for gy in range(0, 101, 25):
    y = H2 - bottom - ph * gy / 100
    sh.draw_line((left, y), (left + pw, y))
sh.finish(color=GREY, width=0.6)
sh.draw_rect(pymupdf.Rect(left, H2 - bottom - ph, left + pw, H2 - bottom)); sh.finish(color=hx('#BFBFBF'), width=0.6)
sh.commit()
pts = []
for i, (a, pct) in enumerate(segs):
    x = left + pw * (i + 0.5) / NDEC
    pts.append((x, H2 - bottom - ph * pct / 100))
sh = pg.new_shape(); sh.draw_line(pts[0], pts[0])
for i in range(len(pts) - 1):
    sh.draw_line(pts[i], pts[i + 1])
sh.finish(color=BLUE, width=1.5); sh.commit()
sh = pg.new_shape()
for (x, y) in pts:
    sh.draw_circle(pymupdf.Point(x, y), 2.0)
sh.finish(fill=BLUE, color=BLUE); sh.commit()
for (x, y), (a, pct) in zip(pts, segs):
    txt(pg, H2, x + 5, H2 - y + 1, f'{pct:.0f}', 8, NUM)
for gy in range(0, 101, 25):
    y = bottom + ph * gy / 100
    txt(pg, H2, left - 4, y - 3, f'{gy}%', 8, NUM, 'right')
for i in range(NDEC):
    x = left + pw * (i + 0.5) / NDEC
    txt(pg, H2, x, 13, f'{i*100+1}', 8, NUM, 'center')
txt(pg, H2, left + pw / 2, 3.5, 'Google Scholar rank (decile start)', 8, DARK, 'center')
for pos, lab in ((2.0, 'top-200'), (5.0, 'top-500')):
    x = left + pw * pos / NDEC
    sh = pg.new_shape(); sh.draw_line((x, H2 - bottom - ph + 2), (x, bottom)); sh.finish(color=ORANGE, width=0.7, dashes='[2 2] 0'); sh.commit()
    txt(pg, H2, x - 1.5 if pos > 4 else x + 1.5, 134, lab, 6.6, ORANGE, 'right' if pos > 4 else 'left')
txt(pg, H2, W2 / 2, 152, 'Google Scholar saturation \u2014 screened depth: top 500; no new primary studies at any rank', 7.2, DARK, 'center')
(PKG / 'common' / 'search' / 'figures').mkdir(parents=True, exist_ok=True)
doc.save(str(PKG / 'common' / 'search' / 'figures' / 'gs_saturation.pdf'))
pix = doc[0].get_pixmap(dpi=300); pix.save(str(PKG / 'common' / 'search' / 'figures' / 'gs_saturation.png'))
print('common/search/figures/gs_saturation.pdf + .png regenerated (top-500 screening)')
