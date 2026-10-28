#!/usr/bin/env python3
"""
build_fomc_calendar.py -- builds the FOMC meeting and announcement calendar from the Federal Reserve's own pages and VALIDATES it against data already in the database. Needs network access (the Codespace has it) and, for the validation, SUPABASE_URL / SUPABASE_KEY. Writes results/fomc_meetings.csv and results/fomc_calendar_validation.txt only.
SOURCES. 1994-2020: https://www.federalreserve.gov/monetarypolicy/fomchistorical{YEAR}.htm (sections 'Month D[-D] Meeting|Conference Call - YEAR', each with an optional 'Statement' link). 2021-: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm (statement links; future meetings are listed in FUTURE below, transcribed from that page on 2026-10-23 and marked confirmed = False).
THE KEY FIELD is announcement_date = the date inside the statement link's URL, NOT the meeting date: the 2008-01-21 conference call announced on 2008-01-22, the 2008-10-07 call on 2008-10-08. A call or meeting with no statement has announcement_date NULL (no announcement). The FOMC issued a statement after EVERY meeting only from January 2000 (from February 1994 only after changes), so hold-day analyses can start in 2000.
TRAPS HANDLED. (1) a 2025-08-22 'notation vote' links a longer-run-goals statement whose URL looks like a policy statement: only a link whose text is exactly 'Statement' (historical pages), or 'HTML' with a policy-statement URL (calendar page), counts; (2) two-month and year-crossing meetings ('Apr/May 30-1'); (3) a statement URL date more than 3 days from the meeting is flagged.
VALIDATION (printed and saved): (a) 2021-2026 announcement dates against an independent list transcribed from the page; (b) meetings per year; (c) weekday of every announcement; (d) EVERY change in the target-rate series in macro_long (DFEDTAR to 2008-12-15, DFEDTARU / DFEDTARL after) classified as announced the SAME DAY, the DAY BEFORE (an effective-date convention) or neither; (e) the same for government_decisions rows with decision_type = interest_rate.
Usage:   python3 -u scripts/macro/build_fomc_calendar.py              (fetch, parse, validate, write)
         python3 -u scripts/macro/build_fomc_calendar.py --no-db      (skip the database checks)
"""
import os, re, sys, csv, time, datetime
from html.parser import HTMLParser
from urllib.parse import urljoin

BASE = "https://www.federalreserve.gov/monetarypolicy/"
UA = {"User-Agent": "Mozilla/5.0 (research script; FOMC calendar builder)"}
FIRST_YEAR, LAST_HIST = 1994, 2020
TODAY = datetime.date.today()
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT_CSV = os.path.join(ROOT, "results", "fomc_meetings.csv")
OUT_TXT = os.path.join(ROOT, "results", "fomc_calendar_validation.txt")

# announcement dates of the 2021-2026 meetings, transcribed from the Fed's calendar page on 2026-10-23 (the dates inside its statement links): the independent check
INDEPENDENT_PAST = ["2021-01-27", "2021-03-17", "2021-04-28", "2021-06-16", "2021-07-28", "2021-09-22", "2021-11-03", "2021-12-15",
                    "2022-01-26", "2022-03-16", "2022-05-04", "2022-06-15", "2022-07-27", "2022-09-21", "2022-11-02", "2022-12-14",
                    "2023-02-01", "2023-03-22", "2023-05-03", "2023-06-14", "2023-07-26", "2023-09-20", "2023-11-01", "2023-12-13",
                    "2024-01-31", "2024-03-20", "2024-05-01", "2024-06-12", "2024-07-31", "2024-09-18", "2024-11-07", "2024-12-18",
                    "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18", "2025-07-30", "2025-09-17", "2025-10-29", "2025-12-10",
                    "2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17", "2026-07-29", "2026-09-16", "2026-10-28"]
# scheduled, not yet held (tentative until confirmed): (first day, last day)
FUTURE = [("2026-10-27", "2026-10-28"), ("2026-12-08", "2026-12-09"), ("2027-01-26", "2027-01-27"), ("2027-03-16", "2027-03-17"), ("2027-04-27", "2027-04-28"), ("2027-06-08", "2027-06-09"), ("2027-07-27", "2027-07-28"), ("2027-09-14", "2027-09-15"), ("2027-10-26", "2027-10-27"), ("2027-12-07", "2027-12-08")]
MONTHS = {m.lower()[:3]: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], 1)}
HEAD = re.compile(r"^\s*(?P<m1>[A-Za-z]+)\.?(?:\s*/\s*(?P<mb>[A-Za-z]+)\.?)?\s+(?P<d1>\d{1,2})(?:\s*[-\u2013\u2014/]\s*(?:(?P<m2>[A-Za-z]+)\.?\s+)?(?P<d2>\d{1,2}))?\s+(?:\((?P<note>[^)]*)\)\s+)?(?:(?P<un>Unscheduled|Emergency)\s+)?(?P<kind>Meeting|Conference Call)\s*[-\u2013\u2014]\s*(?P<year>\d{4})\s*$")
UNMATCHED = []
POLICY_PR = re.compile(r"/pressreleases/monetary(\d{8})a\.htm$")


class Walker(HTMLParser):
    """document-order tokens: ('h', text) for headings, ('a', href, text) for links"""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tokens, self._h, self._a, self._href = [], None, None, None

    def handle_starttag(self, tag, attrs):
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._h = []
        elif tag == "a":
            self._a, self._href = [], dict(attrs).get("href")

    def handle_endtag(self, tag):
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._h is not None:
            self.tokens.append(("h", " ".join("".join(self._h).split())))
            self._h = None
        elif tag == "a" and self._a is not None:
            self.tokens.append(("a", self._href or "", " ".join("".join(self._a).split())))
            self._a = None

    def handle_data(self, data):
        if self._h is not None:
            self._h.append(data)
        if self._a is not None:
            self._a.append(data)


def tokens_of(html):
    w = Walker()
    w.feed(html)
    return w.tokens


def month_num(s):
    return MONTHS.get(s.strip(".").lower()[:3])


def is_statement(href, text):
    t = text.strip()
    if t == "Statement":
        return True      # exact text only: the longer-run-goals link has a longer title; 1994-1999 statements are not under /monetary/
    if t == "HTML" and POLICY_PR.search(href):
        return True
    return t in ("Press Release", "Policy Statement") and "monetary" in href


def ann_from_url(href, end):
    """the 8-digit date in the URL that lies within 3 days of the meeting's last day; (date or None, flag)"""
    cands = []
    for tok in re.findall(r"(?<!\d)(\d{8})(?!\d)", href):
        try:
            cands.append(datetime.date(int(tok[:4]), int(tok[4:6]), int(tok[6:])))
        except ValueError:
            pass
    near = [c for c in cands if abs((c - end).days) <= 3]
    if near:
        return near[0], ""
    return (cands[0], "URL DATE MORE THAN 3 DAYS FROM THE MEETING") if cands else (None, "NO DATE IN THE STATEMENT URL")


def parse_year_page(html, year, url):
    out, cur, minutes = [], None, set()
    for tk in tokens_of(html):
        if tk[0] == "h":
            m = HEAD.match(tk[1])
            if not m:
                if re.search(r"Meeting|Conference", tk[1], re.I) and re.search(r"(?<!\d)(19|20)\d{2}(?!\d)", tk[1]):
                    UNMATCHED.append((year, tk[1]))
                cur = None
                continue
            m1 = month_num(m.group("m1"))
            if m1 is None:
                cur = None
                continue
            y = int(m.group("year"))
            try:
                start = datetime.date(y, m1, int(m.group("d1")))
                end = start
                if m.group("d2"):
                    m2 = month_num(m.group("m2")) if m.group("m2") else (month_num(m.group("mb")) if m.group("mb") else m1)
                    yy = y
                    if m2 == m1 and int(m.group("d2")) < start.day:
                        m2 += 1
                    elif m2 < m1:
                        yy = y + 1
                    if m2 > 12:
                        m2, yy = 1, y + 1
                    end = datetime.date(yy, m2, int(m.group("d2")))
            except (ValueError, TypeError):
                UNMATCHED.append((year, tk[1] + " [INVALID DATE]"))
                cur = None
                continue
            note = (m.group("note") or "").lower()
            kind = "meeting" if m.group("kind") == "Meeting" else "conference_call"
            if "cancel" in note:
                kind = "cancelled"
            cur = {"year": y, "kind": kind, "start_date": start, "end_date": end, "announcement_date": None, "statement_url": "", "flags": (("UNSCHEDULED" if (m.group("un") or "unsched" in note) else "") + (" CANCELLED" if kind == "cancelled" else "")).strip(), "source_url": url, "confirmed": True}
            out.append(cur)
        elif tk[0] == "a" and "minutes" in tk[1].lower():
            for tok in re.findall(r"(?<!\d)(\d{8})(?!\d)", tk[1]):
                try:
                    d_ = datetime.date(int(tok[:4]), int(tok[4:6]), int(tok[6:]))
                except ValueError:
                    continue
                if d_.year == year:
                    minutes.add(d_)
        elif tk[0] == "a" and cur is not None and not cur["statement_url"] and is_statement(tk[1], tk[2]):
            cur["statement_url"] = urljoin(url, tk[1])
            cur["announcement_date"], fl = ann_from_url(tk[1], cur["end_date"])
            cur["flags"] = (cur["flags"] + " " + fl).strip()
    # second, independent signal: a minutes link is dated by the meeting's last day; a minutes date with no parsed meeting is a meeting the heading parser missed
    for md in sorted(minutes):
        if not any(abs((r["end_date"] - md).days) <= 2 for r in out):
            out.append({"year": md.year, "kind": "meeting", "start_date": md - datetime.timedelta(days=1), "end_date": md, "announcement_date": md, "statement_url": "", "flags": "FROM MINUTES LINK ONLY: announcement date ASSUMED = last day, VERIFY", "source_url": url, "confirmed": True})
    return out


def parse_calendar_page(html, url):
    out, seen = [], set()
    for tk in tokens_of(html):
        if tk[0] == "a" and tk[2].strip() == "HTML":
            m = POLICY_PR.search(tk[1])
            if m and m.group(1) not in seen:
                seen.add(m.group(1))
                a = datetime.date(int(m.group(1)[:4]), int(m.group(1)[4:6]), int(m.group(1)[6:]))
                out.append({"year": a.year, "kind": "meeting", "start_date": a - datetime.timedelta(days=1), "end_date": a, "announcement_date": a, "statement_url": urljoin(url, tk[1]), "flags": "START DAY INFERRED (two-day meeting)", "source_url": url, "confirmed": True})
    return out


def future_rows(known):
    out = []
    for s, e in FUTURE:
        s_, e_ = datetime.date.fromisoformat(s), datetime.date.fromisoformat(e)
        if e_ in known:
            continue
        out.append({"year": e_.year, "kind": "meeting", "start_date": s_, "end_date": e_, "announcement_date": e_, "statement_url": "", "flags": "SCHEDULED, NOT YET HELD" if e_ > TODAY else "EXPECTED STATEMENT NOT ON THE PAGE YET (rerun)", "source_url": BASE + "fomccalendars.htm", "confirmed": False})
    return out


def fetch(url):
    import requests
    r = requests.get(url, headers=UA, timeout=40)
    r.raise_for_status()
    return r.text


def build(fetcher=fetch, first=FIRST_YEAR, last=LAST_HIST, pause=1.0):
    rows = []
    for y in range(first, last + 1):
        url = "%sfomchistorical%d.htm" % (BASE, y)
        rows += parse_year_page(fetcher(url), y, url)
        time.sleep(pause)
    cal_url = BASE + "fomccalendars.htm"
    past = parse_calendar_page(fetcher(cal_url), cal_url)
    rows += past
    rows += future_rows({r["end_date"] for r in past})
    for r in rows:
        if r["kind"] == "meeting" and r["year"] >= 2000 and "URL DATE MORE THAN 3 DAYS" in r["flags"]:
            r["announcement_date"] = r["end_date"]
            r["flags"] += " | ANNOUNCEMENT SET TO THE LAST DAY (the statement link pointed to a different date)"
    for r in rows:
        r["has_statement"] = r["announcement_date"] is not None
    rows.sort(key=lambda r: (r["start_date"], r["kind"]))
    return rows


def classify(d, ann):
    if d in ann:
        return "same_day"
    if d - datetime.timedelta(days=1) in ann:
        return "day_after"
    if d.weekday() == 0 and d - datetime.timedelta(days=3) in ann:
        return "day_after"
    return "other"


def fetch_series(sb, sid):
    rows, off = [], 0
    while True:
        page = sb.table("macro_long").select("obs_date,value").eq("series_id", sid).order("obs_date").range(off, off + 999).execute().data
        if not page:
            break
        rows += page
        if len(page) < 1000:
            break
        off += 1000
    return rows


def change_dates(rows):
    out, prev = [], None
    for r in rows:
        if r.get("value") is None:
            continue
        v = float(r["value"])
        if prev is not None and abs(v - prev) > 1e-9:
            out.append((datetime.date.fromisoformat(str(r["obs_date"])[:10]), prev, v))
        prev = v
    return out


def validate(rows, sb, log):
    P = lambda s="": log.append(s)
    ann_rows = [r for r in rows if r["announcement_date"] and r["confirmed"]]
    ann = {r["announcement_date"] for r in ann_rows}
    P("FOMC CALENDAR: %d rows (%d meetings, %d conference calls); %d announcements (statement dates, confirmed); %d scheduled and not yet held" % (len(rows), sum(r["kind"] == "meeting" for r in rows), sum(r["kind"] == "conference_call" for r in rows), len(ann_rows), sum(not r["confirmed"] for r in rows)))
    flagged = [r for r in rows if r["flags"] and r["confirmed"] and "INFERRED" not in r["flags"]]
    P("  rows with a flag (excluding the inferred start day of 2021+ meetings): %d" % len(flagged))
    for r in flagged[:15]:
        P("     %s %s %s: %s  %s" % (r["kind"], r["start_date"], r["end_date"], r["flags"], r["statement_url"][-70:]))
    ind = set(datetime.date.fromisoformat(x) for x in INDEPENDENT_PAST)
    got = {a for a in ann if a.year >= 2021}
    P("\n(a) 2021-2026 announcement dates vs the independent transcription: %d expected, %d parsed; missing %s; extra %s" % (len(ind), len(got), sorted(str(x) for x in ind - got) or "none", sorted(str(x) for x in got - ind) or "none"))
    by = {}
    for r in rows:
        if r["confirmed"] and r["kind"] != "cancelled":
            by.setdefault(r["year"], [0, 0, 0])[0 if r["kind"] == "meeting" else 1] += 1
            by[r["year"]][2] += 1 if r["announcement_date"] else 0
    P("\n(b) per year: meetings / conference calls / announcements   [regular years have 8 meetings; years outside 8 are listed after]")
    P("   " + " | ".join("%d: %d/%d/%d" % (y, *by[y]) for y in sorted(by)))
    P("   years with a meeting count other than 8: " + (", ".join("%d (%d)" % (y, by[y][0]) for y in sorted(by) if by[y][0] != 8) or "none"))
    wd = {}
    for a in ann:
        wd[a.strftime("%a")] = wd.get(a.strftime("%a"), 0) + 1
    P("\n(c) weekday of the announcements: " + ", ".join("%s %d" % (k, wd[k]) for k in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun") if k in wd))
    P("    announcements on a weekend: " + (", ".join(str(a) for a in sorted(ann) if a.weekday() >= 5) or "none"))
    post2000_missing = [r for r in rows if r["kind"] == "meeting" and r["confirmed"] and r["year"] >= 2000 and not r["announcement_date"]]
    P("    meetings from 2000 without a statement link (expected none; each is a parse gap or a real exception): %d  %s" % (len(post2000_missing), [str(r["start_date"]) for r in post2000_missing][:12]))
    synth = [r for r in rows if "FROM MINUTES LINK ONLY" in r["flags"]]
    P("\n(b2) meetings synthesized from a minutes link because no section heading parsed (announcement date ASSUMED = last day; verify): %d  %s" % (len(synth), [str(r["end_date"]) for r in synth][:24]))
    P("     headings mentioning Meeting or Conference Call that did NOT parse: %d  %s" % (len(UNMATCHED), UNMATCHED[:14]))
    if sb is None:
        return
    P("\n(d) CHANGES IN THE TARGET-RATE SERIES (macro_long) vs the announcement dates (only changes on or after the calendar's first day)")
    for sid in ("DFEDTAR", "DFEDTARU", "DFEDTARL"):
        try:
            ch_all = change_dates(fetch_series(sb, sid))
            lo_ = min(r["start_date"] for r in rows)
            ch = [c for c in ch_all if c[0] >= lo_]
        except Exception as e:
            P("   %s: could not read (%s)" % (sid, str(e)[:80]))
            continue
        cnt = {"same_day": 0, "day_after": 0, "other": 0}
        oth = []
        for d, a, b in ch:
            k = classify(d, ann)
            cnt[k] += 1
            if k == "other":
                oth.append("%s %+.2f" % (d, b - a))
        P("   %-9s %3d changes: same day %3d | the day after an announcement %3d | neither %3d%s" % (sid, len(ch), cnt["same_day"], cnt["day_after"], cnt["other"], ("   neither: " + ", ".join(oth[:14])) if oth else ""))
        P("      (%d earlier changes before %s are outside the calendar and not classified)" % (len(ch_all) - len(ch), lo_))
    P("\n(e) government_decisions rows with decision_type = interest_rate vs the announcement dates")
    try:
        gd = sb.table("government_decisions").select("decision_date").eq("decision_type", "interest_rate").order("decision_date").execute().data
        cnt = {"same_day": 0, "day_after": 0, "other": 0}
        oth = []
        for r in gd:
            d = datetime.date.fromisoformat(str(r["decision_date"])[:10])
            k = classify(d, ann)
            cnt[k] += 1
            if k == "other":
                oth.append(str(d))
        P("   %d rows: same day %d | the day after an announcement %d | neither %d%s" % (len(gd), cnt["same_day"], cnt["day_after"], cnt["other"], ("   neither: " + ", ".join(oth)) if oth else ""))
    except Exception as e:
        P("   could not read government_decisions (%s)" % str(e)[:80])


def write_outputs(rows, log):
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    cols = ["year", "kind", "start_date", "end_date", "announcement_date", "has_statement", "statement_url", "source_url", "confirmed", "flags"]
    with open(OUT_CSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: (r[c].isoformat() if isinstance(r[c], datetime.date) else r[c]) for c in cols})
    open(OUT_TXT, "w").write("\n".join(log) + "\n")


def main():
    no_db = "--no-db" in sys.argv
    sb = None
    if not no_db:
        from supabase import create_client
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    rows = build()
    log = []
    validate(rows, sb, log)
    write_outputs(rows, log)
    print("\n".join(log))
    print("\nwrote %s and %s" % (OUT_CSV, OUT_TXT))
    return rows, log


if __name__ == "__main__":
    main()
