#!/usr/bin/env python3
"""
load_fomc_meetings.py -- loads results/fomc_meetings.csv (from build_fomc_calendar.py) into the table fomc_meetings. DRY RUN unless --apply. Upserts on (kind, start_date, end_date), so it is safe to rerun after every FOMC meeting (rerun build_fomc_calendar.py first).
GUARDS: refuses to load if fewer than 300 rows; refuses rows whose announcement date was ASSUMED from a minutes link (flag 'FROM MINUTES LINK ONLY') unless --allow-assumed; prints the counts it would write.
Table (create it first, in the SQL editor):
  CREATE TABLE IF NOT EXISTS fomc_meetings (year int NOT NULL, kind text NOT NULL, start_date date NOT NULL, end_date date NOT NULL, announcement_date date, has_statement boolean NOT NULL, statement_url text, source_url text NOT NULL, confirmed boolean NOT NULL, flags text, PRIMARY KEY (kind, start_date, end_date));
announcement_date is the day the decision was PUBLIC (the date in the statement URL), not the meeting date; NULL = no announcement; kind is meeting | conference_call | cancelled.
"""
import os, sys, csv

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "..", "..", "results", "fomc_meetings.csv")


def to_row(r):
    return {"year": int(r["year"]), "kind": r["kind"], "start_date": r["start_date"], "end_date": r["end_date"],
            "announcement_date": r["announcement_date"] or None, "has_statement": r["has_statement"] == "True",
            "statement_url": r["statement_url"] or None, "source_url": r["source_url"], "confirmed": r["confirmed"] == "True", "flags": r["flags"] or None}


def main(argv=None, sb=None):
    argv = sys.argv[1:] if argv is None else argv
    rows = [to_row(r) for r in csv.DictReader(open(CSV_PATH))]
    if len(rows) < 300:
        print("only %d rows in the CSV: refusing to load (expected about 310)" % len(rows))
        return 1
    assumed = [r for r in rows if r["flags"] and "FROM MINUTES LINK ONLY" in r["flags"]]
    if assumed and "--allow-assumed" not in argv:
        print("%d rows have an ASSUMED announcement date (from a minutes link): refusing; review them or pass --allow-assumed: %s" % (len(assumed), [r["end_date"] for r in assumed][:10]))
        return 1
    by_kind = {}
    for r in rows:
        by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1
    print("rows %d | by kind %s | with an announcement date %d | not yet held %d | flagged %d" % (len(rows), by_kind, sum(1 for r in rows if r["announcement_date"]), sum(1 for r in rows if not r["confirmed"]), sum(1 for r in rows if r["flags"])))
    if "--apply" not in argv:
        print("DRY RUN: nothing written (add --apply)")
        return 0
    if sb is None:
        from supabase import create_client
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    for i in range(0, len(rows), 200):
        sb.table("fomc_meetings").upsert(rows[i:i + 200], on_conflict="kind,start_date,end_date").execute()
    print("upserted %d rows into fomc_meetings" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
