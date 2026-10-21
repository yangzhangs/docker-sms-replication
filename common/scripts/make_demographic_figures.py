# -*- coding: utf-8 -*-
"""Regenerate the Figure 3 demographic panels from study_ledger.csv.

The panels are drawn as vector PDFs with PyMuPDF and the base-14 Times-Roman
font so that they match the manuscript's serif typography.

Input : common/extraction/study_ledger.csv
Output: common/figures/fig3_demographics/plots0..plots6.pdf
"""
import csv, json, math, sys, os
from pathlib import Path
import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from venue_canon import canon

WS = Path(__file__).resolve().parents[2]
LEDGER = WS / 'common' / 'extraction' / 'study_ledger.csv'
OUT = WS / 'common' / 'figures' / 'fig3_demographics'
OUT.mkdir(parents=True, exist_ok=True)

def hx(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))

BLUE = hx('#4472C4'); ORANGE = hx('#ED7D31'); LBLUE = hx('#B4C7E7')
GRID = hx('#D9D9D9'); FRAME = hx('#BFBFBF'); DARK = hx('#333333'); WHITE = (1, 1, 1)
GREYM = hx('#D1D4DB'); BORDERM = hx('#B9BEC7')

# ---------------- Data ----------------
rows = list(csv.DictReader(open(LEDGER, encoding='utf-8-sig')))

pub = {}
for r in rows: pub[r['publisher']] = pub.get(r['publisher'], 0) + 1
pub_items = [(k, pub[k]) for k in ['IEEE', 'ACM', 'Springer', 'Elsevier', 'Wiley', 'IEICE', 'MDPI'] if pub.get(k)]

at = {}
for r in rows: at[r['author_type']] = at.get(r['author_type'], 0) + 1
vt = {}
for r in rows: vt[r['venue_type']] = vt.get(r['venue_type'], 0) + 1

ven = {}
for r in rows:
    c = canon(r['venue_name'])
    ven[c] = ven.get(c, 0) + 1
TOP = [(k, ven[k]) for k in ['ESE', 'MSR', 'ICSME', 'FSE', 'ICSE', 'SANER',
                             'IEEE Access', 'COMPSAC', 'TSE', 'SCAM', 'TOSEM', 'ASE']]

years = list(range(2017, 2027))
YC = [0] * len(years); YJ = [0] * len(years)
for r in rows:
    i = years.index(int(r['year']))
    if r['venue_type'] == 'conference': YC[i] += 1
    else: YJ[i] += 1

core = {}
for r in rows: core[r['core']] = core.get(r['core'], 0) + 1
CORE = [('A*', core['A*']), ('A', core['A']), ('B', core['B']), ('C', core['C']),
        ('/', core['not-ranked'])]

country = {}
for r in rows: country[r['country']] = country.get(r['country'], 0) + 1

# ---------------- Drawing helpers ----------------
def tl(s, fs):
    return pymupdf.get_text_length(s, fontname='tiro', fontsize=fs)

def txt(page, H, x, y_math, s, fs=9, color=DARK, align='left'):
    if align == 'center': x -= tl(s, fs) / 2
    elif align == 'right': x -= tl(s, fs)
    page.insert_text((x, H - y_math), s, fontname='tiro', fontsize=fs, color=color)

def barh(W, H, labels, values, xlabel, xmax, tickstep, fs=9):
    doc = pymupdf.open()
    page = doc.new_page(width=W, height=H)
    left = max(tl(l, fs) for l in labels) + 9
    right, top, bottom = 20, 7, 27
    pw, ph = W - left - right, H - top - bottom
    sh = page.new_shape()
    t = 0
    while t <= xmax:
        gx = left + pw * t / xmax
        sh.draw_line((gx, H - top), (gx, H - top - ph))
        t += tickstep
    sh.finish(color=GRID, width=0.6)
    sh.draw_rect(pymupdf.Rect(left, H - top - ph, left + pw, H - top))
    sh.finish(color=FRAME, width=0.6)
    rowh = ph / len(labels); bh = rowh * 0.62
    for i, v in enumerate(values):
        cy = top + rowh * (i + 0.5)          # PDF coordinates (top-down)
        bw = pw * v / xmax
        sh.draw_rect(pymupdf.Rect(left, cy - bh / 2, left + bw, cy + bh / 2))
    sh.finish(fill=BLUE, color=None)
    sh.commit()
    for i, (l, v) in enumerate(zip(labels, values)):
        cym = H - (top + rowh * (i + 0.5))
        txt(page, H, left - 5, cym - 3, l, fs, DARK, 'right')
        bw = pw * v / xmax
        txt(page, H, left + bw + 2.5, cym - 3, str(v), fs, DARK)
    t = 0
    while t <= xmax:
        gx = left + pw * t / xmax
        txt(page, H, gx, 14, str(t), fs, DARK, 'center')
        t += tickstep
    txt(page, H, left + pw / 2, 3.5, xlabel, fs, DARK, 'center')
    return doc

def pie(W, H, items, cx, cy, r, fs_lab=9, fs_out=8.5):
    """items: (value, fillcolor, inside|None, outside|None)
       inside: (fr, [l1, l2])；outside: (label_ang, label_dist, [l1,l2], lead_ang)"""
    doc = pymupdf.open()
    page = doc.new_page(width=W, height=H)
    total = sum(v for v, *_ in items)
    a = 90.0
    sh = page.new_shape()
    for v, color, *_ in items:
        span = 360 * v / total
        pts = [(cx, H - cy)]
        steps = max(12, int(span / 2))
        for i in range(steps + 1):
            ang = math.radians(a + span * i / steps)
            pts.append((cx + r * math.cos(ang), H - (cy + r * math.sin(ang))))
        pts.append((cx, H - cy))
        sh.draw_polyline(pts)
        sh.finish(fill=hx(color), color=hx('#404040'), width=0.8)
        a += span
    a = 90.0
    for v, color, inside, outside in items:
        span = 360 * v / total
        am = a + span / 2
        if outside:
            lang, ldist, lines, lead = outside
            sh.draw_line((cx + r * math.cos(math.radians(lead)), H - (cy + r * math.sin(math.radians(lead)))),
                         (cx + r * ldist * math.cos(math.radians(lang)), H - (cy + r * ldist * math.sin(math.radians(lang)))))
            sh.finish(color=hx('#808080'), width=0.6)
        a += span
    sh.commit()
    a = 90.0
    for v, color, inside, outside in items:
        span = 360 * v / total
        am = a + span / 2
        if inside:
            fr, lines = inside
            x = cx + r * fr * math.cos(math.radians(am))
            y = cy + r * fr * math.sin(math.radians(am))
            for i, ln in enumerate(lines):
                txt(page, H, x, y + 3.2 - i * 12, ln, fs_lab, DARK, 'center')
        if outside:
            lang, ldist, lines, lead = outside
            lx = cx + r * ldist * math.cos(math.radians(lang))
            ly = cy + r * ldist * math.sin(math.radians(lang))
            for i, ln in enumerate(lines):
                txt(page, H, lx, ly + 3.2 - i * 11.5, ln, fs_out, DARK, 'center')
        a += span
    return doc

def year_stacked(W, H):
    doc = pymupdf.open()
    page = doc.new_page(width=W, height=H)
    left, right, top, bottom = 20, 8, 22, 20
    pw, ph = W - left - right, H - top - bottom
    ymax, tick = 18, 4
    sh = page.new_shape()
    t = 0
    while t <= ymax:
        gy = H - bottom - ph * t / ymax
        sh.draw_line((left, gy), (left + pw, gy))
        t += tick
    sh.finish(color=GRID, width=0.6)
    sh.draw_rect(pymupdf.Rect(left, H - top - ph, left + pw, H - bottom))
    sh.finish(color=FRAME, width=0.6)
    n = len(years); slot = pw / n; bw = slot * 0.62
    for i in range(n):
        x0 = left + slot * i + (slot - bw) / 2
        h1 = ph * YC[i] / ymax; h2 = ph * YJ[i] / ymax
        ybase = H - bottom
        if YC[i]:
            sh.draw_rect(pymupdf.Rect(x0, ybase - h1, x0 + bw, ybase))
        if YJ[i]:
            sh.draw_rect(pymupdf.Rect(x0, ybase - h1 - h2, x0 + bw, ybase - h1))
    sh.commit()
    # In-bar values
    for i in range(n):
        x0 = left + slot * i + (slot - bw) / 2
        h1 = ph * YC[i] / ymax; h2 = ph * YJ[i] / ymax
        ybase = H - bottom
        if YC[i] >= 2:
            txt(page, H, x0 + bw / 2, bottom + h1 / 2 - 3, str(YC[i]), 8, DARK, 'center')
        if YJ[i] >= 2:
            txt(page, H, x0 + bw / 2, bottom + h1 + h2 / 2 - 3, str(YJ[i]), 8, DARK, 'center')
    t = 0
    while t <= ymax:
        gyy = bottom + ph * t / ymax
        txt(page, H, left - 4, gyy - 3, str(t), 8.5, DARK, 'right')
        t += tick
    for i, y in enumerate(years):
        txt(page, H, left + slot * (i + 0.5), 6.5, str(y), 8, DARK, 'center')
    # Legend (top center)
    items = [('Conference', ORANGE), ('Journal', BLUE)]
    wds = [10 + tl(t, 8.5) for t, _ in items]
    x0 = left + pw / 2 - (sum(wds) + 10) / 2
    yl = H - 13   # math y of square bottom
    for (t, c), wd in zip(items, wds):
        page.draw_rect(pymupdf.Rect(x0, H - yl - 7, x0 + 7, H - yl), fill=c, color=None)
        txt(page, H, x0 + 10, yl + 0.5, t, 8.5, DARK)
        x0 += wd + 10
    return doc

# ---------------- Generate the seven panels ----------------
cn_sorted = sorted(country.items(), key=lambda x: (-x[1], x[0]))
TOP_CN = [(k, v) for k, v in cn_sorted if v >= 2]
OTH_N = len(cn_sorted) - len(TOP_CN)
CN_LABELS = [k for k, _ in TOP_CN] + [f'Others ({OTH_N} countries)']
CN_VALUES = [v for _, v in TOP_CN] + [OTH_N]

jobs = {
    'plots0': barh(470, 150, CN_LABELS, CN_VALUES, '# Primary studies', 31, 5, fs=10),
    'plots1': barh(224, 158, [k for k, _ in pub_items], [v for _, v in pub_items],
                   '# Primary studies', 52, 10),
    'plots2': pie(175, 158,
                  [(at['Academia'], '#4472C4', (0.48, ['Academia', '91.3%']), None),
                   (at['Both'], '#B4C7E7', None, (120, 1.28, ['Both', '7.6%'], 107.7)),
                   (at['Industry'], '#FFFFFF', None, (165, 1.38, ['Industry', '1.1%'], 92))],
                  95, 80, 54),
    'plots3': barh(221, 158, [k for k, _ in TOP], [v for _, v in TOP],
                   '# Primary studies', 8, 2),
    'plots4': pie(146, 158,
                  [(vt['journal'], '#4472C4', (0.5, ['Journal', '26.1%']), None),
                   (vt['conference'], '#ED7D31', (0.5, ['Conference', '73.9%']), None)],
                  73, 79, 60, fs_lab=9.5),
    'plots5': year_stacked(220, 158),
    'plots6': barh(221, 158, [k for k, _ in CORE], [v for _, v in CORE],
                   '# Primary studies', 42, 10),
}
for name, d in jobs.items():
    d.save(str(OUT / f'{name}.pdf'))
    d.close()
# Selection figure (Fig. 2) is distributed as a final PDF; no process copy needed here.

print('Generated:', ', '.join(jobs))
print('Value check: publisher', pub_items, '| author', at, '| venue_type', vt)
print('top venues', TOP)
print('years conf', YC, 'jour', YJ)
print('core', CORE, '| countries', sorted(country.items(), key=lambda x: -x[1]))
