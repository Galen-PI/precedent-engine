"""ledger_snapshot_g7_1030.py (2026-10-30): READ-ONLY. Reads, over the database REST interface (SUPABASE_URL and SUPABASE_KEY from the environment, the same way
scripts/ingestion/pull_8k_report_dates.py does), the 16 flag_ledger rows touched by the G7 ledger update of 2026-10-30 and the five event_premium_20d evidence rows it added,
checks them, and writes results/g7_rerun/ledger_notes_after_2026-10-30.txt. It writes NOTHING to the database. Exit code 0 only if every check passes.
Usage: python3 scripts/audit/ledger_snapshot_g7_1030.py"""
import os, sys, hashlib, datetime
import requests
KEYS = ["band_edge_calibration_90", "band_stress_scale_median", "earnings_role_bands_walk_forward", "event_burst_day0_1", "event_daily_range_coverage", "event_day_width_own_events",
        "event_earnings_window_width", "event_label_direction_sign", "event_pre_days_m4_m1", "event_premium_20d", "event_type_acquisition", "event_type_capital_raise_no_burst",
        "event_type_leadership_change", "event_type_strategic_partnership", "fomc_announcement_day_market_move", "macro_oil_shock_energy_same_day"]
MARK = "G7 RE-RUN 2026-10-30"
OUT = "results/g7_rerun/ledger_notes_after_2026-10-30.txt"
EV_ERAS = ["g7 rerun ARM 1 2004-2007", "g7 rerun ARM 1 2008-2012", "g7 rerun ARM 1 2013-2018", "g7 rerun ARM 1 pooled 2004-2018", "g7 rerun ARM 1 pooled 2004-2018 clustered"]
def get(path, params):
    h = {"apikey": os.environ["SUPABASE_KEY"], "Authorization": "Bearer " + os.environ["SUPABASE_KEY"]}
    r = requests.get(os.environ["SUPABASE_URL"] + "/rest/v1/" + path, headers=h, params=params, timeout=60)
    r.raise_for_status(); return r.json()
def main():
    rows = get("flag_ledger", {"select": "flag_key,status,tested_on,notes", "flag_key": "in.(" + ",".join(KEYS) + ")", "order": "flag_key"})
    ev = get("flag_ledger_evidence", {"select": "flag_key,era,n,estimate,se,unit", "flag_key": "eq.event_premium_20d", "era": "like.g7 rerun*", "order": "n"})
    problems = []
    if sorted(r["flag_key"] for r in rows) != sorted(KEYS): problems.append("the 16 flag keys are not all present: got %d rows" % len(rows))
    out = ["# Ledger notes after the G7 update of 2026-10-30, read from the database over REST at %s UTC (backups: flag_ledger_backup_20261030 and flag_ledger_evidence_backup_20261030; the SQL was run in the SQL editor as one transaction)." % datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
           "# Per flag: key | status | tested_on | length of the whole notes field; then the text appended on 2026-10-30 (from the marker to the end of the field).", ""]
    n_marked = 0; n_proven = 0
    for r in sorted(rows, key=lambda x: x["flag_key"]):
        notes = r.get("notes") or ""
        if notes.count(MARK) != 1: problems.append("%s: marker occurs %d times" % (r["flag_key"], notes.count(MARK))); appended = "(marker missing or repeated)"
        else:
            n_marked += 1; appended = notes[notes.index(MARK):]
            if not (appended.endswith("Status unchanged.") or appended.endswith("Status unchanged (null).")): problems.append("%s: appended text does not end as expected" % r["flag_key"])
        if r["flag_key"] == "event_pre_days_m4_m1":
            if r["status"] != "null": problems.append("event_pre_days_m4_m1 status is %r, expected null" % r["status"])
        else:
            if r["status"] == "proven": n_proven += 1
            else: problems.append("%s status is %r, expected proven" % (r["flag_key"], r["status"]))
        out.append("%s | %s | %s | %d" % (r["flag_key"], r["status"], r["tested_on"], len(notes))); out.append(appended); out.append("")
    if sorted(e["era"] for e in ev) != sorted(EV_ERAS): problems.append("evidence rows: expected the five eras, got %s" % [e["era"] for e in ev])
    out.append("# Evidence rows added for event_premium_20d (flag_key | era | n | estimate | se | unit):")
    for e in ev: out.append("%s | %s | %s | %s | %s | %s" % (e["flag_key"], e["era"], e["n"], e["estimate"], e["se"], e["unit"]))
    text = "\n".join(out) + "\n"
    print("rows read: %d flag_ledger, %d evidence | marker present once in %d of 16 | status proven in %d of 15, null for the candidate: %s" % (len(rows), len(ev), n_marked, n_proven, any(r["flag_key"] == "event_pre_days_m4_m1" and r["status"] == "null" for r in rows)))
    if problems:
        print("PROBLEMS:"); [print("  -", p) for p in problems]; print("nothing written"); return 1
    os.makedirs(os.path.dirname(OUT), exist_ok=True); open(OUT, "w", encoding="utf-8").write(text)
    print("ok   wrote %s | %d bytes | sha256 %s" % (OUT, len(text.encode("utf-8")), hashlib.sha256(text.encode("utf-8")).hexdigest())); return 0
if __name__ == "__main__": sys.exit(main())
