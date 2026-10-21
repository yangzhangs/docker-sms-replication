#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zotero 快照导出工具（Docker SMS 修订项目专用）。

原理：Zotero 桌面版运行时其数据库 zotero.sqlite 处于占用状态，
本工具先把数据库快照复制到工作区（zotero_snapshot/），再对快照做只读分析，
因此 Zotero 可以一直开着。Zotero 里新增了条目后重新执行 refresh 即可。

用法：
  python zotero_export.py refresh
  python zotero_export.py tree [--root Docker_review]
  python zotero_export.py export --collection 57 --out-prefix zotero_export/final_56
  python zotero_export.py export --collection "1最终文献-56" --recursive --out-prefix zotero_export/xxx
"""
import argparse
import csv
import json
import re
import shutil
import sqlite3
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = WORKSPACE / "zotero_snapshot"
SNAPSHOT = SNAPSHOT_DIR / "zotero_copy.sqlite"
LIVE_DB = Path(r"C:\Users\Administrator\Zotero\zotero.sqlite")


# ---------------------------------------------------------------- snapshot --
def refresh_snapshot() -> None:
    """Copy the live Zotero DB (and its journal, if any) into the workspace."""
    if not LIVE_DB.exists():
        sys.exit(f"Zotero database not found at {LIVE_DB}")
    SNAPSHOT_DIR.mkdir(exist_ok=True)
    shutil.copy2(LIVE_DB, SNAPSHOT)
    journal = LIVE_DB.with_name(LIVE_DB.name + "-journal")
    snap_journal = SNAPSHOT.with_name(SNAPSHOT.name + "-journal")
    if journal.exists():
        shutil.copy2(journal, snap_journal)
    else:
        snap_journal.unlink(missing_ok=True)
    # Open once read-write so SQLite recovers/rolls back the copied journal.
    con = sqlite3.connect(SNAPSHOT)
    check = con.execute("PRAGMA quick_check(1)").fetchone()[0]
    con.close()
    print(f"Snapshot OK ({SNAPSHOT.stat().st_size/1e6:.0f} MB), quick_check: {check}")


def connect() -> sqlite3.Connection:
    if not SNAPSHOT.exists():
        sys.exit("No snapshot yet — run: python zotero_export.py refresh")
    con = sqlite3.connect(f"file:{SNAPSHOT.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


# ------------------------------------------------------------- collections --
def subtree_ids(cur: sqlite3.Cursor, root_id: int) -> list[int]:
    ids, frontier = [root_id], [root_id]
    while frontier:
        ph = ",".join("?" * len(frontier))
        rows = cur.execute(
            f"SELECT collectionID FROM collections WHERE parentCollectionID IN ({ph})",
            frontier).fetchall()
        nxt = [r[0] for r in rows if r[0] not in ids]
        ids.extend(nxt)
        frontier = nxt
    return ids


def print_tree(cur: sqlite3.Cursor, root_name: str) -> None:
    roots = cur.execute(
        "SELECT collectionID, collectionName FROM collections "
        "WHERE collectionName LIKE ? COLLATE NOCASE", (f"%{root_name}%",)).fetchall()
    if not roots:
        sys.exit(f"No collection matching {root_name!r}")
    for rid, rname in roots:
        print(f"[{rid}] {rname}")
        _print_children(cur, rid, "  ")


def _print_children(cur: sqlite3.Cursor, parent: int, indent: str) -> None:
    rows = cur.execute(
        "SELECT collectionID, collectionName, "
        "(SELECT COUNT(*) FROM collectionItems ci WHERE ci.collectionID=c.collectionID) n "
        "FROM collections c WHERE parentCollectionID=? ORDER BY collectionName",
        (parent,)).fetchall()
    for r in rows:
        print(f"{indent}[{r['collectionID']}] {r['collectionName']}  ({r['n']} items)")
        _print_children(cur, r["collectionID"], indent + "  ")


# ------------------------------------------------------------------ export --
CREATOR_Q = """
SELECT c.firstName, c.lastName, c.fieldMode FROM itemCreators ic
JOIN creators c ON c.creatorID = ic.creatorID
WHERE ic.itemID=? ORDER BY ic.orderIndex"""
FIELDS_Q = """
SELECT f.fieldName, v.value FROM itemData d
JOIN fields f ON f.fieldID = d.fieldID
JOIN itemDataValues v ON v.valueID = d.valueID
WHERE d.itemID=?"""
COLLS_Q = """
SELECT c.collectionID, c.collectionName FROM collectionItems ci
JOIN collections c ON c.collectionID = ci.collectionID
WHERE ci.itemID=? ORDER BY c.collectionName"""
ATTACH_Q = """
SELECT i.key AS akey, ia.linkMode, ia.contentType, ia.path
FROM itemAttachments ia JOIN items i ON i.itemID = ia.itemID
WHERE ia.parentItemID=?"""


def _year(date_str: str) -> str:
    if not date_str:
        return ""
    m = re.search(r"\d{4}", date_str)
    return m.group(0) if m else ""


def _attachment_paths(att_rows) -> list[str]:
    out = []
    for a in att_rows:
        path = a["path"] or ""
        if a["linkMode"] == 0 and path.startswith("storage:"):  # imported file
            out.append(f"storage/{a['akey']}/{path[len('storage:'):]}")
        elif path:
            out.append(path)
    return out


def fetch_items(cur: sqlite3.Cursor, coll_ids: list[int]) -> list[dict]:
    ph = ",".join("?" * len(coll_ids))
    rows = cur.execute(
        f"""
        SELECT DISTINCT i.itemID, i.key, i.dateAdded, i.dateModified
        FROM collectionItems ci
        JOIN items i ON i.itemID = ci.itemID
        WHERE ci.collectionID IN ({ph})
          AND i.itemID NOT IN (SELECT itemID FROM deletedItems)
        ORDER BY i.key""",
        coll_ids).fetchall()
    items = []
    for r in rows:
        iid = r["itemID"]
        type_name = cur.execute(
            "SELECT t.typeName FROM items i JOIN itemTypes t "
            "ON t.itemTypeID=i.itemTypeID WHERE i.itemID=?", (iid,)).fetchone()["typeName"]
        if type_name in ("attachment", "note", "annotation"):
            continue
        fields = dict(cur.execute(FIELDS_Q, (iid,)).fetchall())
        creators = cur.execute(CREATOR_Q, (iid,)).fetchall()
        authors = [
            (c["lastName"] if c["fieldMode"] == 1 else f"{c['lastName']}, {c['firstName']}").strip(", ")
            for c in creators]
        colls = cur.execute(COLLS_Q, (iid,)).fetchall()
        atts = cur.execute(ATTACH_Q, (iid,)).fetchall()
        rec = {
            "zotero_key": r["key"],
            "item_type": type_name,
            "title": fields.get("title", ""),
            "year": _year(fields.get("date", "")),
            "date_raw": fields.get("date", ""),
            "venue": fields.get("publicationTitle") or fields.get("proceedingsTitle")
                     or fields.get("conferenceName") or fields.get("publisher", ""),
            "doi": fields.get("DOI", ""),
            "url": fields.get("url", ""),
            "abstract": fields.get("abstractNote", ""),
            "authors": authors,
            "collections": [c["collectionName"] for c in colls],
            "attachment_files": _attachment_paths(atts),
            "date_added": r["dateAdded"],
            "all_fields": fields,
        }
        items.append(rec)
    return items


def cmd_export(args) -> None:
    con = connect()
    cur = con.cursor()
    sel = args.collection.strip()
    if sel.isdigit():
        row = cur.execute("SELECT collectionID, collectionName FROM collections "
                          "WHERE collectionID=?", (int(sel),)).fetchone()
    else:
        row = cur.execute("SELECT collectionID, collectionName FROM collections "
                          "WHERE collectionName LIKE ? COLLATE NOCASE",
                          (f"%{sel}%",)).fetchone()
    if not row:
        sys.exit(f"Collection {sel!r} not found")
    cid, cname = row["collectionID"], row["collectionName"]
    ids = subtree_ids(cur, cid) if args.recursive else [cid]
    if args.recursive:
        names = [r["collectionName"] for r in cur.execute(
            f"SELECT collectionName FROM collections WHERE collectionID IN ({','.join('?'*len(ids))})",
            ids).fetchall()]
        print(f"Recursive subtree of [{cid}] {cname}: {len(ids)} collections -> {names}")
    items = fetch_items(cur, ids)
    print(f"Exported {len(items)} items from [{cid}] {cname}")

    out_prefix = WORKSPACE / args.out_prefix
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = out_prefix.with_suffix(".json")
    json_path.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    csv_path = out_prefix.with_suffix(".csv")
    cols = ["zotero_key", "item_type", "year", "title", "venue", "doi", "url",
            "authors", "collections", "attachment_files", "abstract"]
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for it in items:
            row = dict(it)
            row["authors"] = "; ".join(it["authors"])
            row["collections"] = "; ".join(it["collections"])
            row["attachment_files"] = "; ".join(it["attachment_files"])
            w.writerow(row)
    print(f"Wrote {json_path}")
    print(f"Wrote {csv_path}")
    con.close()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("refresh", help="re-copy the live Zotero DB into the workspace snapshot")
    t = sub.add_parser("tree", help="show collection tree")
    t.add_argument("--root", default="Docker_review")
    e = sub.add_parser("export", help="export one collection (optionally its subtree)")
    e.add_argument("--collection", required=True, help="collection ID or name substring")
    e.add_argument("--recursive", action="store_true", help="include subcollections")
    e.add_argument("--out-prefix", required=True, help="output path prefix (.csv/.json appended)")
    args = ap.parse_args()
    if args.cmd == "refresh":
        refresh_snapshot()
        return
    con = connect()
    cur = con.cursor()
    if args.cmd == "tree":
        print_tree(cur, args.root)
    elif args.cmd == "export":
        cmd_export(args)
    con.close()


if __name__ == "__main__":
    main()
