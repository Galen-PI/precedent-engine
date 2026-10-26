#!/usr/bin/env python3
"""
repair_entity_reactions.py -- recompute the OLD event_entity_reactions rows on the prior-close convention (written 2026-10-26).
WHY: those rows (written before 2026-10-26) were computed from the event-day close, so the event-day move was missing; the project rule and the saved columns use the PRIOR close. The tagger was fixed in commit 6615ec5; rows it writes from now on are already right.
WHICH ROWS: exactly the rows in the backup table event_entity_reactions_backup_20261026 (a copy of the old rows, made before this script runs). Rows the tagger adds later are never touched.
DEFAULT = DRY RUN: prints EVERY row, old label and return versus new, with flags, and changes nothing. Read every line first.
FLAGS: FLIP = the label moved between rewarded and punished; NODATA = the new return cannot be computed, the row is kept as is; main-ok = the new return equals the saved column of the event's main reaction row for the same ticker; HOLD (never applied) = the live row no longer equals the backup, or the new return disagrees with that saved column (usually a date-corrected event: read it by hand).
--apply updates only OK rows that are not on HOLD and whose label or return changed, then re-reads them and verifies.
Uses compute_abnormal_return and classify from scripts/tagging/tag_reaction_character.py (the fixed versions), so it cannot drift from the tagger.
Usage (repository root):   python3 scripts/audit/repair_entity_reactions.py     |     python3 scripts/audit/repair_entity_reactions.py --apply
"""
import os, sys, argparse, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tagging"))
import tag_reaction_character as T

BACKUP, LIVE, TOL = "event_entity_reactions_backup_20261026", "event_entity_reactions", 0.0005
COLS = "event_id,entity_id,ticker,relationship_type,reaction,abnormal_return_20d"


def read_all(table, cols, order_cols):
    rows, off = [], 0
    while True:
        q = T.supabase.table(table).select(cols)
        for c in order_cols:
            q = q.order(c)
        page = q.range(off, off + 999).execute().data
        rows.extend(page)
        if len(page) < 1000:
            return rows
        off += 1000


def in_chunks(table, cols, key, values, size=100):
    out = []
    for i in range(0, len(values), size):
        out.extend(T.supabase.table(table).select(cols).in_(key, values[i:i + size]).execute().data)
    return out


def pct(x):
    return "   n/a" if x is None else "%+6.1f%%" % (x * 100)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    try:
        old = read_all(BACKUP, COLS, ["event_id", "entity_id"])
    except Exception as ex:
        sys.exit("STOP: cannot read %s (%s). Create the backup table first." % (BACKUP, str(ex)[:150]))
    if not old:
        sys.exit("STOP: the backup table is empty.")
    live = {(r["event_id"], r["entity_id"]): r for r in read_all(LIVE, COLS, ["event_id", "entity_id"])}
    ev_ids = sorted({r["event_id"] for r in old})
    dates = {e["id"]: str(e["event_date"])[:10] for e in in_chunks("events", "id,event_date", "id", ev_ids)}
    mains = collections.defaultdict(list)
    for m in in_chunks("event_market_reactions_corrected", "event_id,ticker,abnormal_return_20d", "event_id", ev_ids):
        mains[m["event_id"]].append(m)
    print("backup rows: %d (%d events); live rows now: %d; mode: %s" % (len(old), len(ev_ids), len(live), "APPLY" if args.apply else "DRY RUN"))
    rows = []
    for r in old:
        key = (r["event_id"], r["entity_id"])
        o_ar = None if r["abnormal_return_20d"] is None else float(r["abnormal_return_20d"])
        flags, hold = [], False
        lv = live.get(key)
        if lv is None or lv["reaction"] != r["reaction"] or (lv["abnormal_return_20d"] is None) != (o_ar is None) or (o_ar is not None and abs(float(lv["abnormal_return_20d"]) - o_ar) > 1e-9):
            flags.append("LIVE-CHANGED")
            hold = True
        d = dates.get(r["event_id"])
        n_ar = T.compute_abnormal_return(r["ticker"], d, T.DEFAULT_WINDOW_DAYS) if d else None
        if n_ar is None:
            status, n_label = "NODATA", r["reaction"]
            flags.append("NODATA")
        else:
            status, n_label = "OK", T.classify(n_ar)
            for m in mains.get(r["event_id"], []):
                if m["ticker"] == r["ticker"] and m["abnormal_return_20d"] is not None:
                    if abs(float(m["abnormal_return_20d"]) - n_ar) > TOL:
                        flags.append("MAIN-MISMATCH(%+.1f%%)" % (float(m["abnormal_return_20d"]) * 100))
                        hold = True
                    else:
                        flags.append("main-ok")
            if {r["reaction"], n_label} == {"rewarded", "punished"}:
                flags.append("FLIP")
        changed = status == "OK" and (n_label != r["reaction"] or o_ar is None or abs(n_ar - o_ar) > 1e-9)
        rows.append({"r": r, "o_ar": o_ar, "n_ar": n_ar, "n_label": n_label, "status": status, "flags": flags, "hold": hold, "changed": changed})
    for x in rows:
        r = x["r"]
        print("%-8s %-6s %-12s %-9s %s -> %-9s %s  %s%s" % (r["event_id"][:8], r["ticker"], (r["relationship_type"] or "")[:12], r["reaction"], pct(x["o_ar"]), x["n_label"], pct(x["n_ar"]), " ".join(x["flags"]), "  [HOLD]" if x["hold"] else ""))
    ok = [x for x in rows if x["status"] == "OK"]
    trans = collections.Counter((x["r"]["reaction"], x["n_label"]) for x in ok)
    todo = [x for x in rows if x["status"] == "OK" and not x["hold"] and x["changed"]]
    print("\nrows %d | recomputed %d | no data %d | label changed %d | FLIPs %d | HOLD %d | would update %d" % (len(rows), len(ok), len(rows) - len(ok), sum(1 for x in ok if x["n_label"] != x["r"]["reaction"]), sum(1 for x in rows if "FLIP" in x["flags"]), sum(1 for x in rows if x["hold"]), len(todo)))
    print("old -> new label counts: " + ", ".join("%s>%s %d" % (a, b, n) for (a, b), n in sorted(trans.items())))
    if not args.apply:
        print("DRY RUN: nothing written. Read every line above, then run again with --apply.")
        return
    for x in todo:
        r = x["r"]
        T.supabase.table(LIVE).update({"reaction": x["n_label"], "abnormal_return_20d": x["n_ar"]}).eq("event_id", r["event_id"]).eq("entity_id", r["entity_id"]).execute()
    after = {(r["event_id"], r["entity_id"]): r for r in read_all(LIVE, COLS, ["event_id", "entity_id"])}
    bad = [x for x in todo if (lambda a: a is None or a["reaction"] != x["n_label"] or abs(float(a["abnormal_return_20d"]) - x["n_ar"]) > 1e-9)(after.get((x["r"]["event_id"], x["r"]["entity_id"])))]
    print("updated %d rows; verified %d of %d; live rows before %d, after %d" % (len(todo), len(todo) - len(bad), len(todo), len(live), len(after)))
    if bad or len(after) != len(live):
        sys.exit("VERIFICATION FAILED: do not continue; the backup table holds the old rows")


if __name__ == "__main__":
    main()