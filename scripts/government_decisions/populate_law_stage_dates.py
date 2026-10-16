#!/usr/bin/env python3
"""
populate_law_stage_dates.py (v2) -- stage dates and support facts for the RELEVANT enacted laws (Congress.gov API).

Per law: 2 API calls (/bill/{congress}/{type}/{number}/actions and /bill/{congress}/{type}/{number}); writes one row per law
into law_stage_dates (upsert on decision_id; laws already in the table are skipped). Only writes to law_stage_dates.

Final passage = the last passing-vote action on or before the 'Presented to President' date (passed | agreed to | concurred,
excluding procedural lines). Laws whose final passage is more than 21 days before presentment are flagged long_gap_N.

Usage:
  python3 -u scripts/government_decisions/populate_law_stage_dates.py                      # DRY RUN: 20 random laws, writes nothing
  python3 -u scripts/government_decisions/populate_law_stage_dates.py --law 118-42,109-99  # DRY RUN: those laws, with action tails
  python3 -u scripts/government_decisions/populate_law_stage_dates.py --limit 50           # dry run, 50 random laws
  python3 -u scripts/government_decisions/populate_law_stage_dates.py --live               # all relevant laws not yet done (~1 hour)
  python3 -u scripts/government_decisions/populate_law_stage_dates.py --live --limit 100
"""
import os, re, sys, json, time, random
from collections import Counter
from datetime import date
import requests
from supabase import create_client

sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
KEY = os.environ["CONGRESS_API_KEY"]
BASE = "https://api.congress.gov/v3"
DELAY = 0.35

VOTE_TYPES = ("Floor", "ResolvingDifferences")
POS = re.compile(r"\b(passed|agreed to|concurred)\b", re.I)
NEG = re.compile(r"^(motion|cloture|point of order|rule\b|rules committee|amendment)|reconsider|laid on the table|waive|\bdisagree|committee (now )?rise", re.I)
STRICT = re.compile(r"^(Passed/agreed to in|Conference report agreed to in|(Senate|House) (agreed to|concurred)|On motion that the (House|Senate) (suspend the rules and )?(agree|concur))", re.I)
VOTE_RE = re.compile(r"(\d+)\s+-\s+(\d+)")


def fetch(url, params=None, tries=6):
    p = {"api_key": KEY, "format": "json"}
    if params:
        p.update(params)
    for i in range(tries):
        try:
            r = requests.get(url, params=p, timeout=30)
        except requests.RequestException:
            time.sleep(5 * (i + 1))
            continue
        if r.status_code == 429:
            print("    rate limited, waiting", 30 * (i + 1), "s", flush=True)
            time.sleep(30 * (i + 1))
            continue
        if r.status_code == 404:
            return None
        r.raise_for_status()
        time.sleep(DELAY)
        return r.json()
    raise RuntimeError("fetch failed: " + url)


def paged(table, select, order, eqs=None):
    rows, off = [], 0
    while True:
        q = sb.table(table).select(select)
        for k, v in (eqs or []):
            q = q.eq(k, v)
        page = q.order(order).range(off, off + 999).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        off += 1000
    return rows


def all_actions(url):
    acts, off = [], 0
    while True:
        j = fetch(url + "/actions", {"limit": 250, "offset": off})
        if j is None:
            return None
        page = j.get("actions") or []
        acts.extend(page)
        if len(page) < 250:
            break
        off += 250
    return acts


def vote_info(text):
    t = text or ""
    low = t.lower()
    if "voice vote" in low:
        return "voice", None, None
    if "unanimous consent" in low:
        return "unanimous", None, None
    m = VOTE_RE.search(t)
    if m:
        return "roll", int(m.group(1)), int(m.group(2))
    if "without objection" in low:
        return "unopposed", None, None
    return "unknown", None, None


def analyze(dec, acts, bill):
    sd = dec["structured_data"]
    if isinstance(sd, str):
        sd = json.loads(sd)
    notes = []
    txt = lambda a: (a.get("text") or "")
    dated = sorted([a for a in acts if a.get("actionDate")], key=lambda a: (a["actionDate"], a.get("actionTime") or ""))
    intro = next((a["actionDate"] for a in dated if txt(a).startswith("Introduced in")), None) or (dated[0]["actionDate"] if dated else None)
    presented = next((a["actionDate"] for a in dated if txt(a).strip().startswith("Presented to President")), None)
    signed = next((a["actionDate"] for a in dated if a.get("type") == "BecameLaw"), None)
    if signed is None:
        signed = next((a["actionDate"] for a in dated if "Became Public Law" in txt(a)), None)
    passes = [a for a in dated if a.get("type") in VOTE_TYPES and POS.search(txt(a)) and not NEG.search(txt(a))]
    cutoff = presented or signed
    before = [a for a in passes if cutoff and a["actionDate"] <= cutoff]
    final = before[-1] if before else None
    first = passes[0] if passes else None
    if presented is None:
        notes.append("no_presented")
    if final is None:
        notes.append("no_final_passage")
    if signed is None:
        notes.append("no_signed")
    elif str(dec["decision_date"])[:10] != signed:
        notes.append("signed_ne_decision_date")
    if final and cutoff:
        gap = (date.fromisoformat(cutoff) - date.fromisoformat(final["actionDate"])).days
        if gap > 21:
            notes.append("long_gap_%d" % gap)
    if final and not STRICT.search(txt(final)):
        notes.append("loose_final")
    chain = [d for d in (intro, first["actionDate"] if first else None, final["actionDate"] if final else None, presented, signed) if d]
    if chain != sorted(chain):
        notes.append("order_violation")
    kind, yeas, nays = vote_info(txt(final)) if final else (None, None, None)
    b = bill or {}
    cs = b.get("cosponsors")
    spons = (b.get("sponsors") or [{}])[0]
    tail = [(a["actionDate"], a.get("type"), txt(a)[:120]) for a in dated
            if a.get("type") in VOTE_TYPES and (cutoff is None or a["actionDate"] <= cutoff)][-6:]
    return {
        "decision_id": dec["id"], "congress": int(sd.get("congress")), "bill_type": str(sd.get("bill_type")),
        "bill_number": int(sd.get("bill_number")), "law_number": sd.get("law_number"),
        "introduced_date": intro, "first_passage_date": first["actionDate"] if first else None,
        "final_passage_date": final["actionDate"] if final else None, "presented_date": presented, "signed_date": signed,
        "final_passage_text": txt(final)[:200] if final else None, "final_vote_kind": kind, "final_yeas": yeas, "final_nays": nays,
        "sponsor_party": spons.get("party"), "cosponsor_count": cs.get("count") if isinstance(cs, dict) else None,
        "committee_count": (b.get("committees") or {}).get("count") if isinstance(b.get("committees"), dict) else None,
        "n_actions": len(dated), "parse_notes": ";".join(notes) or None, "_tail": tail,
        "final_tail": " || ".join("%s %s" % (t[0], t[2][:90]) for t in tail),
    }


def main():
    args = sys.argv[1:]
    live = "--live" in args
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else (None if live else 20)
    wanted = set(args[args.index("--law") + 1].split(",")) if "--law" in args else None
    laws = [d for d in paged("government_decisions", "id,decision_date,structured_data", "id", [("decision_type", "enacted_law")])
            if (d["structured_data"] or {}).get("relevance_verdict") == "relevant"]
    done = {r["decision_id"] for r in paged("law_stage_dates", "decision_id", "decision_id")}
    if wanted:
        todo = [d for d in laws if (d["structured_data"] or {}).get("law_number") in wanted]
        limit = None
    else:
        todo = [d for d in laws if d["id"] not in done]
    print("relevant enacted laws: %d | already in law_stage_dates: %d | selected: %d" % (len(laws), len(done), len(todo)), flush=True)
    if live:
        todo.sort(key=lambda d: str(d["decision_date"]))
    elif not wanted:
        random.shuffle(todo)
    if limit:
        todo = todo[:limit]
    print("%s: processing %d laws" % ("LIVE" if live else "DRY RUN (writes nothing)", len(todo)), flush=True)
    batch, stats, failed = [], Counter(), 0
    for i, dec in enumerate(todo, 1):
        sd = dec["structured_data"]
        try:
            u = "%s/bill/%d/%s/%d" % (BASE, int(sd["congress"]), str(sd["bill_type"]).lower(), int(sd["bill_number"]))
            acts = all_actions(u)
            if acts is None:
                print("  NOT FOUND:", u, flush=True)
                failed += 1
                continue
            bill = (fetch(u) or {}).get("bill")
            row = analyze(dec, acts, bill)
        except Exception as e:
            print("  FAILED %s: %s: %s" % (dec["id"], type(e).__name__, e), flush=True)
            failed += 1
            continue
        tail = row.pop("_tail")
        for n in (row["parse_notes"] or "ok").split(";"):
            stats[re.sub(r"_\d+$", "", n)] += 1
        stats["vote:" + str(row["final_vote_kind"])] += 1
        if not live:
            print("%s %s | intro %s | first %s | FINAL %s [%s %s-%s] | pres %s | signed %s | %s cos=%s com=%s | %s" % (
                str(dec["decision_date"])[:10], row["law_number"], row["introduced_date"], row["first_passage_date"], row["final_passage_date"],
                row["final_vote_kind"], row["final_yeas"], row["final_nays"], row["presented_date"], row["signed_date"],
                row["sponsor_party"], row["cosponsor_count"], row["committee_count"], row["parse_notes"] or "ok"))
            print("      final text:", (row["final_passage_text"] or "")[:130])
            if row["parse_notes"] or wanted:
                for t in tail:
                    print("        tail:", t[0], t[1], t[2])
            sys.stdout.flush()
        else:
            pass
        if live:
            batch.append(row)
            if len(batch) >= 25:
                sb.table("law_stage_dates").upsert(batch, on_conflict="decision_id").execute()
                batch = []
            if i % 50 == 0:
                print("  ...%d/%d done" % (i, len(todo)), flush=True)
    if live and batch:
        sb.table("law_stage_dates").upsert(batch, on_conflict="decision_id").execute()
    print("\nSUMMARY (%d laws, %d failed):" % (len(todo), failed))
    for k, v in sorted(stats.items()):
        print("  %-28s %d" % (k, v))


if __name__ == "__main__":
    main()
