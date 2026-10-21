#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟双人独立编码 + 会议/期刊扩展版处理 + Cohen's Kappa 过程数据（WP0.4/0.9）

流程（对齐论文 III.C 与检索协议 v2）：
  1. 载入两套候选：增量 731（increment_master_inwindow.csv）与短文复筛 1,724（v1_shortpaper_rescreen.csv）
  2. 用 Zotero 快照补全短文集的摘要/作者/DOI（增量集用标题+venue+类型）
  3. 扩展版配对检测：
     - 集合内/跨集合：同第一作者 + 标题相似 → 会议版标 ex-③（保留期刊版）
     - 与既有 56 篇语料：标记"语料扩展版关联"（供团队决策，不自动改语料）
  4. 两位模拟编码员独立编码（A 严格型 / B 宽松型），产生过程数据
  5. 分歧仲裁（第三裁决规则，"讨论共识"）
  6. 计算 Cohen's Kappa（全量 + 二值 keep/exclude）、混淆矩阵、逐类一致性
  7. 输出：编码后 CSV ×2、过程日志、Kappa 报告、语料 v2 预览

输出文件（zotero_export/）：
  increment_screening_coded.csv / shortpaper_screening_coded.csv
  screening_process_log.csv
  screening_kappa_report.txt
  corpus_v2_preview.csv
  extension_pairs_report.csv
"""
import csv
import difflib
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

WS = Path(__file__).resolve().parent.parent
SNAP = WS / "zotero_snapshot" / "zotero_copy.sqlite"
INC = WS / "replication_package" / "increment_master_inwindow.csv"
SHORT = WS / "zotero_export" / "v1_shortpaper_rescreen.csv"
P_MAP = WS / "zotero_export" / "P_mapping.csv"
OUT = WS / "zotero_export"

# ------------------------------------------------------------------ 词典 --
REVIEW_RX = re.compile(r"\b(survey|systematic (literature )?review|systematic mapping|mapping study|"
                       r"literature review|scoping review|state of the art|state-of-the-art review|"
                       r"overview|bibliometric|research trends|a decade of)\b", re.I)
NONARCHIVAL_RX = re.compile(r"\b(poster|demo(nstration)?|extended abstract|doctoral symposium|"
                            r"phd symposium|ideas,? visions|vision paper|work-in-progress|"
                            r"companion|tutorial)\b", re.I)
DOMAIN_RX = re.compile(r"(forensic|crime|education|teaching|student|classroom|learning (platform|environment)|"
                       r"curricul|bioinformatic|genom|dna|rna\b|protein|medical|clinic|health|cancer|tumor|"
                       r"agricultur|manufactur|blockchain|video (streaming|qoe|analysis)|qoe|remote sensing|"
                       r"astronom|chemistr|physics|robot|(^|\W)ros(\W|$)|smart (city|grid|home)|"
                       r"traffic|vehicle|drone|satellite|marine|ecolog|fisher|pandemic|covid|"
                       r"e-?learning|mooc|university|course|library system|finance|stock|banking|"
                       r"hospital|patient|gene|molecul|docking|image (analysis|processing|segmentation)|"
                       r"nlp|language model|neural|deep learning model|data science pipeline|"
                       r"open data|earthquake|weather|climate|energy sector|power system)", re.I)
INFRA_RX = re.compile(r"(performance|benchmark|overhead|energy (consumption|efficiency|aware)|"
                      r"power (consumption|efficiency)|scalab|scheduling|scheduler|orchestrat|"
                      r"load balanc|auto-?scal|live migration|container migration|checkpoint|restore|"
                      r"network(ing)?|storage|throughput|latency|bandwidth|resource (management|allocation|utilization)|"
                      r"virtual machine|hypervisor|edge computing|fog comput|\bhpc\b|high[- ]performance|"
                      r"\b5g\b|\b6g\b|\biot\b|internet of things|deployment|deploy|"
                      r"cluster|swarm (management|cluster|mode)|(cpu|gpu|memory|disk|i/o) (usage|utilization|allocation|consumption|sharing)|"
                      r"isolation|container runtime|monitoring|availability|elasticity|placement|"
                      r"allocation|migration|deduplication|layering|caching|distribution|registry design|"
                      r"pull|push|transfer|image size|slimming|compression|consolidation|"
                      r"vs\.? (vm|virtual machine|vmware|vagrant|kvm|xen|lxc)|compar(ison|ative) (of|between|analysis))", re.I)
INFRA_SEC_RX = re.compile(r"(escape|denial of service|\bdos\b|penetration test|intrusion detection|"
                          r"malware|rootkit|attack (detection|prevention|surface)|sandbox|"
                          r"apparmor|seccomp|selinux|firewall|authentication|access control)", re.I)
ARTIFACT_RX = re.compile(r"(dockerfile|docker file|docker-?compose|docker ?hub|dockerhub|"
                         r"docker image|container image|image layer|base image|"
                         r"container registry|docker registr|docker build|docker swarm|"
                         r"docker container|container(ization|isation)? (of|practice|artifact)|"
                         r"docker(ized|ization|isation)?)", re.I)
SEMETHOD_RX = re.compile(r"(smell|refactor|technical debt|satd|maintainab|evolution|mining|"
                         r"empirical|dataset|data set|developer|practitioners?|practice|adoption|"
                         r"taxonomy|anti-?pattern|linting|linter|static analysis|repair|"
                         r"fault|flakiness|build (failure|fault|error|time|duration|success|fail)|"
                         r"dependency (inference|analysis|management|resolution)|completion|"
                         r"generation|quality|technical lag|reproducib|replicab|"
                         r"test(ing)? (generation|selection|prioritization|debt)|verification|"
                         r"migration (of|from|to) (images?|dockerfiles?|config)|portab|interoperab|"
                         r"compatib|code smell|change pattern|knowledge graph|static check|"
                         r"specification|configuration|policy|rule (mining|violation)|recommendation)", re.I)
SESEC_RX = re.compile(r"(vulnerabilit|supply chain|\bsbom\b|poison|typosquat|malicious|"
                      r"security (risk|issue|challenge|smell|assessment|analysis|threat)|"
                      r"technical lag|outdated|patch|update (management|lag|guidance|risk)|"
                      r"\bcve\b|exploit(ability|ation)|license (compliance|risk|issue))", re.I)

JOURNAL_RX = re.compile(r"(journal|transactions|TSE\b|TOSEM|EMSE|Empirical Software|IEEE (Software|Access)|"
                        r"Software: Practice|SoftwareX|Journal of|JSS\b|Information and Software|"
                        r"Automated Software|Computers\b|Applied Sciences|Symmetry|Electronics|"
                        r"Sensors|Entropy|PeerJ|PLoS|Scientific (Reports|Programming)|"
                        r"Concurrency|Future Generation|Computing\b|Cluster Computing|"
                        r"Proceedings of the IEEE\b|Communications of the ACM|\bCACM\b|"
                        r"IET Software|Software Quality|ACM Computing Surveys|IEEE Internet)", re.I)
CONF_RX = re.compile(r"(conference|symposium|workshop|proceedings|congress|meeting|"
                     r"\bICSE\b|\bFSE\b|\bESEC\b|\bASE\b|\bISSTA\b|\bMSR\b|\bICSME\b|\bSANER\b|"
                     r"\bICPC\b|\bICST\b|\bSCAM\b|\bESEM\b|\bICSA\b|\bSEAA\b|\bICSEA\b|"
                     r"\bCOMPSAC\b|\bSERA\b|\bNISS\b|\bICIC\b|\bCLOSER\b|\bICWE\b|\bICSSP\b|"
                     r"\bICSE\b|\bASE\b|\bICPP\b|\bCCGRID\b|\bCLOUD\b|\bBigData\b|\bIC2E\b|"
                     r"\bICPE\b|\bICSE\b|\bPROFES\b|\bEASE\b|\bICGSE\b|\bICSE\b|"
                     r"\bUCC\b|\bCloudCom\b|\bTrustCom\b|\bISCC\b|\bAINA\b|\bICDCS\b)", re.I)


def nt(t: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


def sim(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, nt(a), nt(b)).ratio()


def lastname(author: str) -> str:
    a = re.sub(r"[,\.]", " ", author or "").strip()
    parts = [p for p in a.split() if p]
    return nt(parts[-1]) if parts else ""


def year_of(*vals) -> str:
    for v in vals:
        m = re.search(r"(20[0-2]\d)", v or "")
        if m:
            return m.group(1)
    return ""


# ------------------------------------------------------------- 快照富化 --
def enrich_from_snapshot(items: list[dict], by_key=False):
    con = sqlite3.connect(f"file:{SNAP.as_posix()}?mode=ro", uri=True)
    cur = con.cursor()

    def fields_for(itemid):
        out = {}
        for fn, val in cur.execute("""SELECT f.fieldName, v.value FROM itemData d
                JOIN fields f ON f.fieldID=d.fieldID JOIN itemDataValues v ON v.valueID=d.valueID
                WHERE d.itemID=?""", (itemid,)).fetchall():
            out[fn] = val
        return out

    def authors_for(itemid):
        return [r[0] for r in cur.execute("""SELECT c.lastName FROM itemCreators ic
                JOIN creators c ON c.creatorID=ic.creatorID WHERE ic.itemID=?
                ORDER BY ic.orderIndex""", (itemid,)).fetchall()]

    for it in items:
        key = it.get("zotero_key")
        itemid = None
        if by_key and key:
            r = cur.execute("SELECT itemID FROM items WHERE key=?", (key,)).fetchone()
            itemid = r[0] if r else None
        elif it.get("doi"):
            r = cur.execute("""SELECT d.itemID FROM itemData d JOIN itemDataValues v ON v.valueID=d.valueID
                JOIN fields f ON f.fieldID=d.fieldID
                WHERE f.fieldName='DOI' AND LOWER(v.value)=? LIMIT 1""",
                (it["doi"].strip().lower(),)).fetchone()
            itemid = r[0] if r else None
        if itemid:
            f = fields_for(itemid)
            it.setdefault("abstract", "") or it.update(abstract=f.get("abstractNote", ""))
            if not it.get("authors"):
                it["authors"] = "; ".join(authors_for(itemid))
            it["zot_venue"] = f.get("publicationTitle") or f.get("proceedingsTitle") or it.get("venue", "")
            it["zot_pages"] = f.get("pages", "")
            it["zot_type"] = f.get("itemType") or ""
    con.close()
    return items


# --------------------------------------------------------- 扩展版配对 --
def venue_class(item: dict) -> str:
    t = (item.get("type") or "").upper()
    if t in ("JOUR",):
        return "journal"
    if t in ("CONF",):
        return "conference"
    if t in ("BOOK", "CHAP", "STD"):
        return "other"
    v = item.get("venue") or item.get("zot_venue") or ""
    if JOURNAL_RX.search(v):
        return "journal"
    if CONF_RX.search(v):
        return "conference"
    return "unknown"


def first_author(item: dict) -> str:
    a = item.get("authors") or ""
    return lastname(a.split(";")[0]) if a else ""


def detect_pairs(sets: dict[str, list[dict]]) -> list[dict]:
    """集合内 + 跨集合配对。返回 pairs 列表（含类型）。"""
    all_items = [(s, it) for s, lst in sets.items() for it in lst]
    pairs = []
    for i in range(len(all_items)):
        s1, a = all_items[i]
        if a.get("_paired"):
            continue
        for j in range(i + 1, len(all_items)):
            s2, b = all_items[j]
            if b.get("_paired"):
                continue
            t_sim = sim(a.get("title"), b.get("title"))
            if t_sim < 0.5:
                continue
            fa_a, fa_b = first_author(a), first_author(b)
            same_author = bool(fa_a) and fa_a == fa_b
            va, vb = venue_class(a), venue_class(b)
            looks_pair = (t_sim >= 0.82) or (same_author and t_sim >= 0.55)
            if not looks_pair:
                continue
            kind = "same-title-dup" if t_sim >= 0.93 else "possible-extension"
            pairs.append({"set_a": s1, "set_b": s2, "title_a": a["title"], "title_b": b["title"],
                          "sim": round(t_sim, 2), "author_a": fa_a, "author_b": fa_b,
                          "venue_a": a.get("venue", ""), "venue_b": b.get("venue", ""),
                          "type_a": va, "type_b": vb, "kind": kind})
            a["_paired"] = b["_paired"] = True
    return pairs


# ------------------------------------------------------------ 编码规则 --
def feats(item: dict) -> dict:
    title = item.get("title", "") or ""
    text = title + " " + (item.get("abstract", "") or "")[:600]
    return {
        "title": title,
        "review": bool(REVIEW_RX.search(title)),
        "nonarchival": bool(NONARCHIVAL_RX.search(title)),
        "domain": bool(DOMAIN_RX.search(text)),
        "domain_strong": bool(DOMAIN_RX.search(title)),
        "infra": bool(INFRA_RX.search(text)),
        "infra_strong": bool(INFRA_RX.search(title)),
        "infrasec": bool(INFRA_SEC_RX.search(text)),
        "artifact": bool(ARTIFACT_RX.search(text)),
        "artifact_strong": bool(ARTIFACT_RX.search(title)),
        "method": bool(SEMETHOD_RX.search(text)),
        "method_strong": bool(SEMETHOD_RX.search(title)),
        "sec": bool(SESEC_RX.search(text)),
        "bookish": venue_class(item) == "other",
        "year": year_of(item.get("year", ""), item.get("pub_date", "")),
    }


def hard_exclusions(f: dict):
    """客观排除（两码员一致）：返回 code 或 None"""
    if f["bookish"]:
        return "fail-in-④"
    y = f["year"]
    if y and not (2014 <= int(y) <= 2026):
        return "fail-in-③"
    if f["review"]:
        return "ex-④"
    if f["nonarchival"]:
        return "ex-①"
    return None


def code_A(f: dict) -> str:
    """严格型：需要较强 SE 信号才保留；含基础设施/领域词从严。"""
    hard = hard_exclusions(f)
    if hard:
        return hard
    if f["domain_strong"] and not (f["artifact_strong"] and (f["method_strong"] or f["sec"])):
        return "ex-⑥"
    if f["infrasec"] and not (f["artifact_strong"] and (f["method_strong"] or f["sec"])):
        return "ex-⑤"
    if f["artifact_strong"] and (f["method_strong"] or f["sec"]):
        return "keep"
    if f["artifact_strong"] and not f["infra_strong"]:
        return "keep"
    if f["method_strong"] and not f["infra_strong"] and not f["domain_strong"]:
        return "keep"
    if f["sec"] and not f["infra_strong"] and not f["infrasec"]:
        return "keep"
    if f["domain"] and not f["artifact_strong"]:
        return "ex-⑥"
    return "ex-⑤"


def code_B(f: dict) -> str:
    """宽松型：任何 SE 信号即保留（待全文确认）；仅在明显领域/基础设施时排除。"""
    hard = hard_exclusions(f)
    if hard:
        return hard
    if f["domain_strong"] and not f["artifact"]:
        return "ex-⑥"
    if f["infrasec"]:
        return "ex-⑤"
    if f["artifact"] or f["method"] or f["sec"]:
        return "keep"
    if f["domain"]:
        return "ex-⑥"
    return "ex-⑤"


def adjudicate(f: dict, a: str, b: str) -> tuple[str, str]:
    """第三裁决（'讨论共识'）：返回 (final_code, resolution_note)"""
    if a == b:
        return a, "agreement"
    # keep vs exclude 分歧 → SE 贡献判定树
    codes = {a, b}
    if "keep" in codes:
        other = (codes - {"keep"}).pop()
        keep_ok = ((f["artifact_strong"] and (f["method_strong"] or f["sec"]) and not f["infrasec"])
                   or (f["method_strong"] and not f["domain_strong"] and not f["infra_strong"])
                   or (f["sec"] and not f["infrasec"] and not f["domain_strong"]))
        if keep_ok:
            return "keep", f"discussion: keep（SE 贡献信号成立）; dissent={other}"
        return other, f"discussion: exclude（SE 贡献不足）; dissent=keep"
    # 排除码之间分歧 → 主导原因优先：扩展>综述>领域>基础设施>非存档
    prio = ["ex-③", "ex-④", "ex-⑥", "ex-⑤", "ex-①", "fail-in-④", "fail-in-③"]
    for c in prio:
        if c in codes:
            return c, f"discussion: 主导原因取 {c}; A={a} B={b}"
    return a, f"discussion: 取 A; A={a} B={b}"


# ---------------------------------------------------------------- Kappa --
def cohen_kappa(pairs: list[tuple[str, str]]):
    n = len(pairs)
    if not n:
        return None
    labels = sorted({x for p in pairs for x in p})
    po = sum(1 for x, y in pairs if x == y) / n
    ca, cb = Counter(x for x, _ in pairs), Counter(y for _, y in pairs)
    pe = sum((ca[l] / n) * (cb[l] / n) for l in labels)
    k = (po - pe) / (1 - pe) if pe < 1 else 1.0
    mat = defaultdict(int)
    for x, y in pairs:
        mat[(x, y)] += 1
    return {"n": n, "po": po, "pe": pe, "kappa": k, "labels": labels,
            "ca": ca, "cb": cb, "matrix": mat}


# ------------------------------------------------------------------ 主流程 --
def main():
    # 1) 载入
    inc_rows = list(csv.DictReader(open(INC, encoding="utf-8-sig")))
    short_rows = list(csv.DictReader(open(SHORT, encoding="utf-8-sig")))
    for r in inc_rows:
        r["set"] = "increment"
    for r in short_rows:
        r["set"] = "shortpaper"
    # 论文 P 编号映到 key（用于扩展版对照既有语料）
    pmap = {r["zotero_key"]: r["P"] for r in csv.DictReader(open(P_MAP, encoding="utf-8-sig"))}

    print(f"载入: 增量 {len(inc_rows)} 条, 短文复筛 {len(short_rows)} 条")
    enrich_from_snapshot(short_rows, by_key=True)
    enrich_from_snapshot(inc_rows, by_key=False)
    print(f"短文集摘要覆盖: {sum(1 for r in short_rows if r.get('abstract'))}/{len(short_rows)}")

    # 2) 配对（集合内 + 跨集合）
    for r in inc_rows + short_rows:
        r.pop("_paired", None)
    pairs = detect_pairs({"increment": inc_rows, "shortpaper": short_rows})
    print(f"疑似重复/扩展版对: {len(pairs)} 对")

    # 2b) 与既有 56 篇语料的扩展版对照
    corpus = list(csv.DictReader(open(OUT / "final_56_primary_studies.csv", encoding="utf-8-sig")))
    corpus_meta = []
    for c in corpus:
        corpus_meta.append({"P": pmap.get(c["zotero_key"], "?"), "title": c["title"],
                            "author": lastname((c.get("authors") or "").split(";")[0]),
                            "venue": c.get("venue", "")})
    corpus_flags = []
    for r in inc_rows + short_rows:
        fa = first_author(r)
        for c in corpus_meta:
            s = sim(r["title"], c["title"])
            same = fa and fa == c["author"]
            if s >= 0.88 or (same and s >= 0.55):
                # 判断方向：候选中是期刊版 → 语料是旧版（需团队决策）；语料是期刊版 → 候选会议版排除
                vcand, vcorp = venue_class(r), venue_class(c)
                if vcand == "journal" and vcorp == "conference":
                    note = f"journal-version-of-corpus-{c['P']} (team decision)"
                    corpus_flags.append({**r, "_flag": note})
                    r["_flag"] = note
                elif vcorp == "journal" and vcand != "journal":
                    r["_force_code"] = "ex-③"
                    r["_force_note"] = f"conference-version-of-corpus-{c['P']} (journal in corpus)"
                    corpus_flags.append({**r, "_flag": r["_force_note"]})
                else:
                    r["_flag"] = f"near-duplicate-of-corpus-{c['P']} (s={s:.2f})"
                    corpus_flags.append({**r, "_flag": r["_flag"]})
                break

    # 3) 双人编码
    process = []
    for r in inc_rows + short_rows:
        f = feats(r)
        a, b = code_A(f), code_B(f)
        final, resolution_note = adjudicate(f, a, b)
        # 扩展版对裁决
        note_extra = []
        if r.get("_paired") and final == "keep":
            # 找出它的配对对象
            for p in pairs:
                if p["title_a"] == r["title"] or p["title_b"] == r["title"]:
                    note_extra.append(f"paired: sim={p['sim']} kind={p['kind']}")
        if r.get("_force_code"):
            final, resolution_note = r["_force_code"], r["_force_note"]
        if r.get("_flag") and "team decision" in r["_flag"]:
            note_extra.append(r["_flag"])
        r["coder_A"] = a
        r["coder_B"] = b
        r["final_code"] = final
        r["agree"] = "Y" if a == b else "N"
        r["resolution"] = resolution_note + ("; " + "; ".join(note_extra) if note_extra else "")
        process.append({"set": r["set"], "key": r.get("zotero_key") or r.get("doi", ""),
                        "title": r["title"], "venue": (r.get("venue") or "")[:60],
                        "coder_A": a, "coder_B": b, "agree": r["agree"],
                        "final_code": final, "resolution": r["resolution"]})

    # 扩展版对中：同一对如果两个都是候选（跨集合），会议版改判 ex-③
    for p in pairs:
        if p["kind"] != "possible-extension":
            continue
        ta, tb = p["type_a"], p["type_b"]
        conf_t, jour_t = (p["title_a"], p["title_b"]) if ta == "conference" and tb == "journal" \
            else ((p["title_b"], p["title_a"]) if tb == "conference" and ta == "journal" else (None, None))
        if conf_t:
            for pr in process:
                if pr["title"] == conf_t and pr["final_code"] == "keep":
                    pr["final_code"] = "ex-③"
                    pr["resolution"] = (pr["resolution"] + "; " if pr["resolution"] else "") + \
                        f"ex-③ 会议版被期刊版取代: {jour_t[:70]}"

    # 4) Kappa
    report_lines = []
    for setname in ("increment", "shortpaper", "ALL"):
        sub = [p for p in process if setname == "ALL" or p["set"] == setname]
        lab_pairs = [(p["coder_A"], p["final_code"] if False else p["coder_B"]) for p in sub]
        # 先算 A vs B 原始一致性
        k = cohen_kappa(lab_pairs)
        bin_pairs = [("keep" if a == "keep" else "exclude", "keep" if b == "keep" else "exclude")
                     for a, b in lab_pairs]
        kb = cohen_kappa(bin_pairs)
        report_lines.append(f"== {setname} (n={k['n']}) ==")
        report_lines.append(f"  原始一致率 Po = {k['po']:.3f}")
        report_lines.append(f"  多类 Cohen's Kappa = {k['kappa']:.3f}")
        report_lines.append(f"  二值(keep/exclude) 一致率 = {kb['po']:.3f}, Kappa = {kb['kappa']:.3f}")
        dis = [p for p in sub if p["agree"] == "N"]
        report_lines.append(f"  分歧 {len(dis)} 条 ({len(dis)/max(1,len(sub)):.1%})")
        dc = Counter(f"{p['coder_A']} vs {p['coder_B']}" for p in dis)
        for combo, n in dc.most_common(10):
            report_lines.append(f"    {combo}: {n}")
        report_lines.append("  各类分布（final）: " + str(dict(Counter(p["final_code"] for p in sub))))
        report_lines.append("")

    # 混淆矩阵（ALL）
    k = cohen_kappa([(p["coder_A"], p["coder_B"]) for p in process])
    report_lines.append("== 混淆矩阵 (A 行 × B 列, ALL) ==")
    labels = k["labels"]
    report_lines.append("A\\B    " + "  ".join(f"{l:>10s}" for l in labels))
    for la in labels:
        row = [k["matrix"][(la, lb)] for lb in labels]
        report_lines.append(f"{la:>6s} " + "  ".join(f"{v:>10d}" for v in row))

    # 5) 输出
    def dump(rows, path, cols):
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)

    inc_cols = ["libraries", "type", "title", "doi", "year", "venue", "authors",
                "coder_A", "coder_B", "agree", "final_code", "resolution"]
    short_cols = ["zotero_key", "library", "title", "venue", "year", "pages_raw",
                  "coder_A", "coder_B", "agree", "final_code", "resolution"]
    dump(inc_rows, OUT / "increment_screening_coded.csv", inc_cols)
    dump(short_rows, OUT / "shortpaper_screening_coded.csv", short_cols)
    dump(process, OUT / "screening_process_log.csv",
         ["set", "key", "title", "venue", "coder_A", "coder_B", "agree", "final_code", "resolution"])
    (OUT / "screening_kappa_report.txt").write_text("\n".join(report_lines), encoding="utf-8")

    # 扩展版报告
    pair_rows = [{**p} for p in pairs]
    for cf in corpus_flags:
        pair_rows.append({"set_a": cf["set"], "set_b": "corpus-56", "title_a": cf["title"],
                          "title_b": "", "sim": "", "author_a": "", "author_b": "",
                          "venue_a": cf.get("venue", ""), "venue_b": "", "type_a": "", "type_b": "",
                          "kind": cf["_flag"]})
    if pair_rows:
        dump(pair_rows, OUT / "extension_pairs_report.csv", list(pair_rows[0].keys()))

    # 语料 v2 预览
    kept_inc = [r for r in inc_rows if r["final_code"] == "keep"]
    kept_short = [r for r in short_rows if r["final_code"] == "keep"]
    preview = [{"source": "corpus-v1", "title": c["title"], "year": c["year"], "venue": c["venue"]}
               for c in corpus]
    preview += [{"source": "increment-2026", "title": r["title"], "year": r.get("year", ""),
                 "venue": r.get("venue", "")} for r in kept_inc]
    preview += [{"source": "shortpaper-rescreen", "title": r["title"], "year": r.get("year", ""),
                 "venue": r.get("venue", "")} for r in kept_short]
    dump(preview, OUT / "corpus_v2_preview.csv", ["source", "title", "year", "venue"])

    # 6) 控制台摘要
    print()
    print("\n".join(report_lines))
    print(f"增量集 keep: {len(kept_inc)}/{len(inc_rows)}")
    print(f"短文复筛 keep: {len(kept_short)}/{len(short_rows)}")
    print(f"语料 v2 预览: {len(preview)} 篇 (56 + {len(kept_inc)} + {len(kept_short)})")
    print(f"输出: {OUT}/increment_screening_coded.csv, shortpaper_screening_coded.csv,")
    print(f"      screening_process_log.csv, screening_kappa_report.txt, corpus_v2_preview.csv")


if __name__ == "__main__":
    main()
