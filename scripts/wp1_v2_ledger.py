#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WP1 阶段二：v2（92 篇）数字台账
- DOI 前缀 → 出版商（IEEE/ACM/Springer/Elsevier/Wiley/其他）
- PDF 首页文本 → 第一作者国家（常规国家词表，首个命中；扫描版标 manual）
- venue → CORE 排名映射（CORE 2023 为主，未知标注供团队补）
- 汇总：年份/venue 类型/出版商/国家/top 场馆/CORE/贡献等全部 v2 统计
输出：extraction/wp1_v2_ledger.txt + extraction/wp1_v2_ledger.csv
"""
import csv, json, os, re, sqlite3
from collections import Counter, defaultdict
from pathlib import Path
import fitz

WS = Path(__file__).resolve().parent.parent
MASTER = WS / "extraction" / "extraction_master_94.csv"
SNAP = WS / "zotero_snapshot" / "zotero_copy.sqlite"
STORAGE = r"C:\Users\Administrator\Zotero\storage"

PUB = {"10.1109": "IEEE", "10.1145": "ACM", "10.1007": "Springer", "10.1016": "Elsevier",
       "10.1002": "Wiley", "10.3390": "MDPI", "10.21105": "JOSS", "10.1088": "IOP",
       "10.21122": "Science&Technique", "10.1371": "PLOS", "10.5281": "Zenodo"}

CORE = {
    "Empirical Software Engineering": "A*", "IEEE Transactions on Software Engineering": "A*",
    "ACM Transactions on Software Engineering and Methodology": "A*",
    "IEEE/ACM International Conference on Software Engineering (ICSE)": "A*",
    "ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering (ESEC/FSE)": "A*",
    "International Conference on Automated Software Engineering (ASE)": "A*",
    "International Conference on Mining Software Repositories (MSR)": "A*",
    "International Symposium on Software Testing and Analysis (ISSTA)": "A*",
    "Proceedings of the ACM on Software Engineering": "A*",
    "IEEE International Conference on Software Maintenance and Evolution (ICSME)": "A",
    "IEEE International Conference on Software Analysis, Evolution and Reengineering (SANER)": "A",
    "International Conference on Software and System Processes (ICSSP)": "B",
    "International Symposium on Empirical Software Engineering and Measurement (ESEM)": "A",
    "IEEE International Symposium on Software Reliability Engineering (ISSRE)": "A",
    "Asia-Pacific Software Engineering Conference (APSEC)": "B",
    "IEEE International Conference on Source Code Analysis and Manipulation (SCAM)": "B",
    "IEEE Annual Computers, Software, and Applications Conference (COMPSAC)": "B",
    "Software: Practice and Experience": "A", "IEEE Access": "B",
    "Journal of Computer Science and Technology": "B", "Science of Computer Programming": "B",
    "Software and Systems Modeling": "A", "IEICE Transactions on Information and Systems": "C",
}

COUNTRY = ["China", "Chinese", "United States", "USA", "U.S.A", "Canada", "Italy", "Germany",
           "France", "Japan", "Korea", "Brazil", "Spain", "United Kingdom", "UK", "England",
           "Netherlands", "Switzerland", "Sweden", "Norway", "Finland", "Belgium", "Portugal",
           "Australia", "India", "Singapore", "Ireland", "Israel", "Poland", "Austria", "Greece",
           "Turkey", "Russia", "Mexico", "Chile", "Argentina", "Colombia", "Denmark", "Czech",
           "Romania", "Hungary", "Iran", "Pakistan", "Malaysia", "Thailand", "Vietnam", "Indonesia",
           "Saudi Arabia", "Egypt", "South Africa", "New Zealand", "Luxembourg", "Qatar", "UAE",
           "United Arab Emirates", "Morocco", "Tunisia", "Belarus", "Ukraine", "Bangladesh", "Sri Lanka"]
CN = {"USA": "United States", "U.S.A": "United States", "UK": "United Kingdom", "England": "United Kingdom",
      "Korea": "South Korea", "Chinese": "China"}

con = sqlite3.connect(f"file:{SNAP.as_posix()}?mode=ro", uri=True)
cur, cur2 = con.cursor(), con.cursor()
def get(itemid, field):
    r = cur2.execute("""SELECT v.value FROM itemData d JOIN itemDataValues v ON v.valueID=d.valueID
        JOIN fields f ON f.fieldID=d.fieldID WHERE d.itemID=? AND f.fieldName=?""", (itemid, field)).fetchone()
    return r[0] if r else ""

def canon(v):
    v = v or ""
    for kw, name in [
        ("Empirical Software Engineering", "ESE"), ("Empirical Software Eng", "ESE"),
        ("IEEE/ACM International Conference on Software Engineering", "ICSE"),
        ("International Conference on Software Engineering", "ICSE"),
        ("Conference on Mining Software Repositories", "MSR"),
        ("Symposium on the Foundations of Software Engineering", "FSE"), ("Joint European Software Engineering", "FSE"), ("Foundations of Software Engineering", "FSE"),
        ("Automated Software Engineering", "ASE"),
        ("Software Maintenance and Evolution", "ICSME"),
        ("Software Analysis, Evolution and Reengineering", "SANER"), ("Software Analysis", "SANER"),
        ("Source Code Analysis and Manipulation", "SCAM"),
        ("Computers, Software, and Applications Conference", "COMPSAC"),
        ("IEEE Transactions on Software Engineering", "TSE"),
        ("ACM Transactions on Software Engineering and Methodology", "TOSEM"),
        ("Proceedings of the ACM on Software Engineering", "PACMSE"),
        ("IEEE Access", "IEEE Access"), ("SoftwareX", "SoftwareX"),
        ("Journal of Computer Science and Technology", "JCST"),
        ("Science of Computer Programming", "SCP"),
        ("Software and Systems Security Modeling", "SoSyM"), ("Software and Systems Modeling", "SoSyM"),
        ("Software: Practice and Experience", "SPE"),
        ("International Symposium on Software Reliability Engineering", "ISSRE"),
        ("International Conference on Software and System Processes", "ICSSP"),
        ("Empirical Software Engineering and Measurement", "ESEM"),
        ("Asia-Pacific Software Engineering Conference", "APSEC"),
        ("Cluster Computing", "CLUSTER"), ("Internetware", "Internetware"),
        ("Intelligent Computing", "ICIC"), ("Software and Systems Reuse", "ICSR"),
        ("Symposium on Security and Privacy", "S&P"), ("Dependable and Secure Computing", "TDSC"),
        ("IEICE Transactions", "IEICE"), ("Applied Sciences", "Applied Sciences"),
        ("Intelligent Systems & Security", "NISS"), ("Secure Development", "SecDev"),
        ("Ubiquitous Computing", "UEMCON"), ("Computer and Communication", "ICCCS"),
        ("Source Code Analysis", "SCAM"), ("Offshore", "IGNORE"),
    ]:
        if kw.lower() in v.lower():
            return name
    return v[:40]

rows = [r for r in csv.DictReader(open(MASTER, encoding="utf-8-sig")) if r["concerns"]]
ledger = []
for r in rows:
    key = r["zotero_key"]
    iid = cur.execute("SELECT itemID FROM items WHERE key=?", (key,)).fetchone()
    doi, pdf = "", None
    if iid:
        doi = get(iid[0], "DOI")
        for aid, path in cur.execute("SELECT itemID, path FROM itemAttachments WHERE parentItemID=? AND contentType='application/pdf'", (iid[0],)).fetchall():
            akey = cur2.execute("SELECT key FROM items WHERE itemID=?", (aid,)).fetchone()[0]
            p = os.path.join(STORAGE, akey, path[len('storage:'):]) if path and path.startswith('storage:') else None
            if p and os.path.exists(p): pdf = p; break
    pub = PUB.get(doi[:7]) or PUB.get(".".join(doi.split(".")[:2])) or ""
    if not pub:
        vtxt = (r["venue_name"] or "") + " " + (r.get("notes") or "")
        for kw, name in [("IEEE", "IEEE"), ("ACM", "ACM"), ("Springer", "Springer"), ("LNCS", "Springer"),
                          ("Elsevier", "Elsevier"), ("SoftwareX", "Elsevier"), ("Wiley", "Wiley"),
                          ("MDPI", "MDPI"), ("Applied Sciences", "MDPI"), ("IOP", "IOP"),
                          ("Zenodo", "Zenodo"), ("JOSS", "JOSS"), ("IEICE", "IEICE"), ("PLOS", "PLOS")]:
            if kw.lower() in vtxt.lower():
                pub = name
                break
    country = ""
    if pdf:
        try:
            doc = fitz.open(pdf)
            head = doc[0].get_text("text")[:6000]
            doc.close()
            for c in COUNTRY:
                if re.search(r"\b" + re.escape(c), head):
                    country = CN.get(c, c)
                    break
        except Exception:
            country = "?"
    if not country and not pdf:
        country = "manual"
    venue = r["venue_name"] or ""
    core = ""
    for k, v in CORE.items():
        if k.lower()[:30] in venue.lower() or venue.lower()[:25] in k.lower():
            core = v
            break
    ledger.append({**r, "doi": doi, "publisher": pub, "country": country, "core": core or "?"})
con.close()


out = WS / "extraction" / "wp1_v2_ledger.csv"
with open(out, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(ledger[0].keys()), extrasaction="ignore")
    w.writeheader(); w.writerows(ledger)

L = ["WP1 阶段二：语料 v2（92 篇）数字台账", "=" * 62]
L.append(f"出版商: {dict(Counter(x['publisher'] or '未知' for x in ledger))}")
L.append(f"国家(首作者): {dict(Counter(x['country'] for x in ledger).most_common(15))}")
cn = Counter(x['country'] for x in ledger)
L.append(f"国家总数: {len([c for c in cn if c not in ('', 'manual', '?')])} (manual: {cn.get('manual',0)})")
L.append(f"CORE: {dict(Counter(x['core'] for x in ledger))}")
L.append(f"venue 类型: {dict(Counter(x['venue_type'] for x in ledger))}")
by_year = defaultdict(Counter)
for x in ledger:
    by_year[x['year']][x['venue_type']] += 1
L.append("逐年（会议/期刊）:")
for y in sorted(by_year):
    if y:
        c, j = by_year[y]['conference'], by_year[y]['journal']
        L.append(f"  {y}: 会议 {c} | 期刊 {j} | 小计 {c+j}")
venue_c = Counter(canon(x['venue_name']) for x in ledger if x['venue_name'])
L.append("场馆 top-15:")
for k, n in venue_c.most_common(15):
    L.append(f"  {n:2d}  {k}")
(WS / "extraction" / "wp1_v2_ledger.txt").write_text("\n".join(L), encoding="utf-8")
print("\n".join(L))
print(f"\n输出: {out}")
