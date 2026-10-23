import csv, os
SRC = "results/human_review_queue_with_excerpts.csv"
DST = "results/human_review_queue_prescreened.csv"
COL = "reviewer_decision (event / not an event / need more)"
S = {  # (date, ticker): (decision, note)  -- Claude's suggestions against the materiality rubric; a person confirms or overrides each one
("2010-04-09", "CASY"): ("event", "Couche-Tard unsolicited $36/share proposal: named counterparty + price"),
("2016-03-04", "UDR"): ("not an event", "standalone equity offering tied to S&P 500 inclusion, no deal purpose (rubric: routine); check use of proceeds"),
("2008-03-11", "ELV"): ("event", "FY2008 EPS guidance cut to $5.76-6.01 from $6.41; stock -28%; rubric core test says yes, classifier rule on guidance says noise"),
("2007-07-17", "AIZ"): ("need more", "CEO and CFO named in something the excerpt cuts off; if it is an SEC notice it is an event"),
("2006-06-27", "TTWO"): ("event", "grand jury subpoenas from the Manhattan DA about option practices: formal investigation"),
("2006-01-20", "FAST"): ("not an event", "routine $0.20 dividend declaration; the -8.8% likely has another cause (check earnings)"),
("2024-08-21", "BEN"): ("event", "Western Asset CIO transition, Leech on leave: leadership of a major subsidiary"),
("2006-05-26", "COO"): ("need more", "34 positions is trivial by the rubric, but -8% on 13x volume: read why the market cared"),
("2006-09-21", "CVS"): ("not an event", "routine director appointment; the -8% has another cause"),
("2011-04-15", "AME"): ("event", "Q1 EPS pre-announcement $0.55-0.56 vs prior guidance $0.46-0.48"),
("2008-03-31", "VRTX"): ("event", "telaprevir (VX-950) preliminary study results; +28%"),
("2007-03-20", "HAL"): ("event", "Q1 earnings warning: below consensus"),
("2011-01-06", "TGT"): ("need more", "monthly sales release; an event only if the rest of it changes guidance"),
("2007-02-09", "MTD"): ("event", "Q4 2006 results + raised 2007 outlook, filed under a non-2.02 item: check the earnings flag"),
("2013-12-18", "F"): ("event", "2013 results preview + 2014 outlook with figures"),
("2006-11-17", "PPG"): ("event", "Q4 chlor-alkali earnings outlook: segment guidance, -5%"),
("2007-11-14", "AVY"): ("not an event", "pro forma financials for the already-disclosed Paxar acquisition (rubric: duplicate)"),
("2020-01-31", "IBM"): ("event", "CEO change: Krishna CEO, Rometty executive chairman"),
("2016-03-18", "REG"): ("not an event", "standalone common stock offering (rubric: routine); check use of proceeds"),
("2017-06-16", "WMT"): ("not an event", "debt tender offers are routine; the -4.7% matches Amazon-Whole Foods the same day (from memory): a cross-company move"),
("2016-12-23", "CTAS"): ("event", "FQ2 2017 earnings release filed under a non-2.02 item: check the earnings flag"),
("2014-04-09", "ISRG"): ("event", "preliminary Q1 results ahead of the April 22 release"),
("2012-10-01", "TAP"): ("need more", "new Europe segment + division-level CEO appointments: a judgment call per the rubric"),
("2013-09-04", "LDOS"): ("event", "FQ2 2014 results release filed under a non-2.02 item: check the earnings flag"),
("2007-03-21", "EXR"): ("not an event", "exchangeable notes for general purposes and property acquisitions: generic, not a named deal"),
}
rows = list(csv.DictReader(open(SRC)))
hit = skipped = 0
for r in rows:
    k = (r["date"], r["ticker"])
    if k in S:
        if r.get(COL, "").strip():
            skipped += 1
            continue
        r[COL], r["notes"] = S[k][0], "prescreened: " + S[k][1]
        hit += 1
with open(DST, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
from collections import Counter
c = Counter(S[k][0] for k in S)
print("suggestions written for %d rows (%d already had a human decision and were left alone); %d of %d suggestions found no matching row" % (hit, skipped, len(S) - hit - skipped, len(S)))
print("suggested: " + ", ".join("%s %d" % kv for kv in c.most_common()) + " | file: " + DST + " (the main file is untouched)")
