#!/usr/bin/env python3
"""
exhibit_reclass_test.py -- re-classifies a small, fixed set of 8-K filings under four conditions (plus a replicate that measures noise) to separate the effect of the INPUT from the effect of the RULE. It never writes to the database and never imports the classifier module (that file has no __main__ guard, so importing it would run the job):
only KNOWN_ROUTINE_PATTERNS, build_batch_request, parse_classification_result and get_recent_event_titles are pulled out of its syntax tree and executed in a private namespace.
ARMS:  A = exactly what the classifier sees today (body text only);  B = the body (first 10,000 characters) plus the first 4,000 characters of the filing's EX-99 press-release exhibit;  C = B with the guidance-via-exhibit rule REMOVED from the system prompt;
       A2 = an exact REPLICATE of A (only metadata.user_id differs) that measures the model's run-to-run noise;  D = B with that rule REPLACED by an explicit one: quantified earnings-guidance revisions, pre-announcements and earnings warnings are real events (financial_result); routine reaffirmations, earnings-date notices and call-scheduling notices stay noise.
GROUPS: G = the 50 'guidance-type' filings of the content-blind sample (results/guidance_variance_sample.csv; 19 read as true guidance, 16 as not, 15 unjudgeable: my reading, recorded in GUIDE below);  O = a seeded random 50 'other exhibit' filings of the same sample (CONTROL);
        R = filings with a human decision in review_queue_decisions (event / not an event; the decisions are still tagged 'prescreened' and PROVISIONAL, so agreement with them is not a score against ground truth).
RECORDED OUTPUT: results/exhibit_reclass_test.csv (one row per filing and arm); each API reply is cached in data_cache/reclass_test, so an interrupted run never pays twice.
MEASURES: (1) replication: arm A vs the stored verdict (setup is faithful if about 85% or more agree; recent events are fetched LIVE, so some drift is expected); (2) share real_event / uncertain / noise by group and arm; G split by my reading; (3) R: agreement with the decisions; (4) flips from A on the control.
PRE-SET RULE (revised BEFORE any real run: a mock showed that a control of 50 filings moves about 6 points by sampling noise alone, so a 'under 5 points' control criterion was too tight, and the model itself is not deterministic): THE EXHIBIT INPUT HELPS if, on the true-guidance G filings plus the R rows decided 'event', the share called real_event rises from A to B by at least 20 points AND
the A -> A2 noise on the same filings is under 10 points. THE RULE CHANGE HELPS if D exceeds B by at least 15 points on the same filings AND the control O's real_event share rises by no more than 8 points from A to D AND the R rows decided 'not an event' rise by no more than 15 points (n is only a handful: reported, weakly informative). Small n (about 19 true-guidance filings): counts are printed beside every share and nothing is concluded from a difference of fewer than 4 filings.
PREDICTIONS (before any run): A2 differs from A on 5-12% of the filings (the noise floor); A replicates the stored verdicts on at least 85%; B lifts real_event on the true-guidance filings from about 15% to 40-55%; C is within 10 points of B; D reaches 60-80%; the control's real_event share moves by under 8 points in every arm; R events flagged (real_event or uncertain) go from about 60% in A to about 75% in B and 85% in D;
'not an event' rows called real_event rise by 5-15 points in D.
Usage:   python3 -u scripts/classification/exhibit_reclass_test.py                 (prints the cost estimate and stops)
         python3 -u scripts/classification/exhibit_reclass_test.py --pilot --yes    (3 filings per group, 5 arms: results/exhibit_reclass_test_pilot.csv)
         python3 -u scripts/classification/exhibit_reclass_test.py --yes            (the full run)
Needs ANTHROPIC_API_KEY, SUPABASE_URL, SUPABASE_KEY and, for filings not yet cached, SEC_USER_AGENT with a real contact.
"""
import os, sys, re, csv, json, ast, time, hashlib, random, argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts", "card"))
import requests
import event_width_test as ew
import unrecorded_candidates as uc
import add_exhibit_excerpts as ae

CLASSIFIER = os.path.join(HERE, "classify_8k_filings_batch_v2.py")
RESULTS = os.path.join(ROOT, "results")
CACHE = os.path.join(ROOT, "data_cache", "reclass_test")
SEED = 20261021
ARMS = ["A", "A2", "B", "C", "D"]
RULE_RE = re.compile(r"- Earnings guidance revisions disclosed only via a press-release exhibit\s+reference, with no acquisition, divestiture, leadership change, or\s+settlement context stated in the filing text itself\.\n?")
NEW_RULE = ("- Quantified earnings guidance revisions, pre-announcements and earnings warnings ARE real events (suggested_event_type financial_result) when the press-release text states figures that raise, lower or newly set guidance, "
            "or says results will fall short of or exceed expectations. Routine reaffirmations of unchanged guidance, earnings-date notices and conference-call scheduling notices remain noise.\n")
# my reading of the 50 G filings of the first real run (date, text that appears in the exhibit's first 160 characters, reading): 'guidance' / 'not'; anything unmatched is 'unknown'
GUIDE = [("2011-06-08", "TI updates", "guidance"), ("2011-03-08", "TI updates", "guidance"), ("2008-09-09", "TI updates", "guidance"), ("2017-07-05", "Delta expects", "guidance"), ("2019-04-02", "Delta expects", "guidance"), ("2013-12-03", "Yum! Brands Expects", "guidance"),
         ("2020-12-16", "QUEST DIAGNOSTICS RAISES", "guidance"), ("2016-01-12", "Ford Expects Record", "guidance"), ("2008-12-03", "Schlumberger Comments on Outlook", "guidance"), ("2012-09-13", "Steel Dynamics Provides", "guidance"), ("2018-06-28", "MCKESSON REAFFIRMS", "guidance"),
         ("2012-10-16", "Kroger Outlines", "guidance"), ("2017-09-26", "reiterates full-year 2017", "guidance"), ("2006-03-14", "Harris Corporation Provides", "guidance"), ("2007-12-19", "UAL Investor Update", "guidance"), ("2012-05-09", "Trading Update", "guidance"),
         ("2025-01-13", "Updates Revenue and Earnings", "guidance"), ("2015-09-18", "NRG Reset", "guidance"), ("2014-07-25", "ONEOK", "guidance"),
         ("2015-07-09", "ACCEPTS COTY", "not"), ("2009-04-08", "PULTE AND CENTEX", "not"), ("2015-12-11", "Shareholders Approve Merger", "not"), ("2015-03-16", "Prices Public Offering", "not"), ("2010-12-14", "Proposed Private Offering", "not"), ("2015-10-13", "Announces Pricing", "not"),
         ("2012-05-22", "Adjusts Proposed Refinancing", "not"), ("2023-08-16", "Sacituzumab", "not"), ("2016-01-07", "Mark-to-Market", "not"), ("2010-05-21", "OPERATING DATA", "not"), ("2014-07-25", "Reportable Segments", "not"), ("2018-12-10", "CECL", "not"),
         ("2015-10-02", "Annual Report 2015", "not"), ("2016-06-29", "CCAR", "not"), ("2019-12-02", "TO DISCUSS BUSINESS OUTLOOK", "not"), ("2012-01-10", "EXITS FORWARD", "not")]


def load_pieces(sb):
    """Pull the four needed names out of the classifier's syntax tree (never executes main())."""
    try:
        from model_config import MODEL_VERSION
    except ImportError:
        found_ = []
        for dp, dn, fn in os.walk(ROOT):
            dn[:] = [d for d in dn if d not in (".git", "node_modules", "data_cache", "__pycache__", "results")]
            if "model_config.py" in fn:
                found_.append(dp)
        if len(found_) != 1:
            sys.exit("model_config.py found in %d places (%s). Tell me which one the classifier uses (or paste lines 55-70 of the classifier)." % (len(found_), ", ".join(found_) or "none"))
        sys.path.insert(0, found_[0])
        from model_config import MODEL_VERSION
        print("model_config found in %s" % found_[0])
    tree = ast.parse(open(CLASSIFIER).read())
    want_assign, want_func = {"KNOWN_ROUTINE_PATTERNS"}, {"build_batch_request", "parse_classification_result", "get_recent_event_titles"}
    picked, found = [], set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in want_assign for t in node.targets):
            picked.append(node); found.add("KNOWN_ROUTINE_PATTERNS")
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id in want_assign:
            picked.append(node); found.add(node.target.id)
        elif isinstance(node, ast.FunctionDef) and node.name in want_func:
            picked.append(node); found.add(node.name)
    missing = (want_assign | want_func) - found
    if missing:
        sys.exit("Not found in the classifier file: %s" % ", ".join(sorted(missing)))
    ns = {"json": json, "re": re, "os": os, "time": time, "MODEL_VERSION": MODEL_VERSION, "supabase": sb}
    try:
        exec(compile(ast.Module(body=picked, type_ignores=[]), CLASSIFIER, "exec"), ns)
    except NameError as e:
        sys.exit("The extracted pieces need another name from the classifier file (%s): paste its definition and I will add it." % e)
    return ns


def fetch_body(url):
    """Same cleaning as the classifier's fetch_filing_text."""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, "body_" + re.sub(r"\W", "_", url)[-120:] + ".txt")
    if os.path.exists(path):
        return open(path).read()
    if "@" not in ae.UA or any(w in ae.UA for w in ("example.com", "YOUR_REAL", "your")):
        sys.exit("Set SEC_USER_AGENT to a real contact first.")
    with requests.get(url, headers={"User-Agent": ae.UA}, timeout=30, stream=True) as r:
        r.raise_for_status()
        enc, chunks, size = r.encoding or "latin-1", [], 0
        for ch in r.iter_content(65536):
            chunks.append(ch); size += len(ch)
            if size >= 2_000_000:
                break
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", b"".join(chunks).decode(enc, errors="replace"))).strip()
    open(path, "w").write(text)
    time.sleep(ae.DELAY)
    return text


def in_chunks(sb, table, cols, col, vals):
    out = []
    vals = sorted(set(v for v in vals if v))
    for i in range(0, len(vals), 100):
        out += sb.table(table).select(cols).in_(col, vals[i:i + 100]).execute().data
    return out


def call_api(params, key):
    h = {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    for attempt in range(7):
        try:
            r = requests.post("https://api.anthropic.com/v1/messages", headers=h, json=params, timeout=120)
        except Exception:
            time.sleep(2 ** attempt); continue
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429, 500, 502, 503, 529):
            time.sleep(2 ** attempt + random.random()); continue
        raise RuntimeError("API %d: %s" % (r.status_code, r.text[:200]))
    raise RuntimeError("API failed after retries")


def pct(k, n):
    return "%3d%% (%d/%d)" % (round(100.0 * k / n), k, n) if n else "  n/a"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--pilot", action="store_true")
    a = ap.parse_args()
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    sb = ew.get_sb()
    ns = load_pieces(sb)
    rng = random.Random(SEED)
    sample = list(csv.DictReader(open(os.path.join(RESULTS, "guidance_variance_sample.csv"))))
    G = [r for r in sample if r["group"] == "G" and r["accession_number"]]
    O = rng.sample([r for r in sample if r["group"] == "O" and r["accession_number"]], 50)
    dec = [r for r in uc.paged(lambda: sb.table("review_queue_decisions").select("accession_number,ticker,miss_date,decision").order("id")) if r["decision"] in ("event", "not_an_event")]
    if a.pilot:
        G, O, dec = G[:3], O[:3], dec[:3]
    items = [("G", r["accession_number"], r) for r in G] + [("O", r["accession_number"], r) for r in O] + [("R", r["accession_number"], r) for r in dec]
    accs = [x[1] for x in items]
    fil = {r["accession_number"]: r for r in in_chunks(sb, "sec_8k_filings", "accession_number,filing_date,item_codes,primary_document_url,security_id", "accession_number", accs)}
    tick = {r["id"]: r["ticker"] for r in uc.paged(lambda: sb.table("securities").select("id,ticker").order("id"))}
    stored = {r["accession_number"]: r for r in in_chunks(sb, "filing_ai_classifications", "accession_number,ai_verdict,ai_confidence", "accession_number", accs)}
    recent = {}
    reqs, meta = [], []
    for grp, acc, r in items:
        f = fil.get(acc)
        if not f:
            continue
        tk = tick.get(f["security_id"], "")
        if tk not in recent:
            try:
                recent[tk] = ns["get_recent_event_titles"](tk)
            except Exception:
                recent[tk] = []
        body = fetch_body(f["primary_document_url"])
        ex = ae.excerpt_for(f["primary_document_url"]).get("excerpt", "")
        has_ex = bool(ex) and ex[:200] not in body
        text_b = body[:10000] + ("\n\n[EXHIBIT 99 TEXT, first 4,000 characters]\n" + ex if has_ex else "")
        label = ""
        if grp == "R":
            label = r["decision"]
        elif grp == "G":
            label = next((l for d, s, l in GUIDE if d == r["date"] and s.lower() in r["excerpt_start"].lower()), "unknown")
        for arm in ARMS:
            req = ns["build_batch_request"](acc + "|" + arm, tk, str(f["filing_date"])[:10], f["item_codes"], body if arm in ("A", "A2") else text_b, recent[tk])
            p = req["params"]
            sysd = p["system"][0]
            if arm in ("C", "D"):
                if len(RULE_RE.findall(sysd["text"])) != 1:
                    sys.exit("The guidance rule was not found exactly once in the system prompt: nothing was sent. Paste lines 184-192 of the classifier and I will adjust the pattern.")
                sysd["text"] = RULE_RE.sub(NEW_RULE if arm == "D" else "", sysd["text"])
            if arm == "A2":
                p["metadata"] = {"user_id": "replicate-2"}                       # identical request: a fresh sample, to measure run-to-run noise
            reqs.append(p)
            meta.append({"group": grp, "accession": acc, "ticker": tk, "date": str(f["filing_date"])[:10], "arm": arm, "label": label, "has_exhibit_text": int(has_ex),
                         "stored": (stored.get(acc) or {}).get("ai_verdict", "")})
    ntok = sum((len(p["system"][0]["text"]) + len(p["messages"][0]["content"])) / 4.0 for p in reqs)
    todo = [i for i, p in enumerate(reqs) if not os.path.exists(os.path.join(CACHE, hashlib.sha1(json.dumps(p, sort_keys=True).encode()).hexdigest() + ".json"))]
    print("filings %d (G %d, O %d, R %d) x 5 arms = %d requests | not yet cached %d | about %.2f million input tokens in all (system prompt included in every request; it is sent with cache_control) | up to 1,000 output tokens each" % (
        len(reqs) // len(ARMS), sum(m["group"] == "G" for m in meta) // len(ARMS), sum(m["group"] == "O" for m in meta) // len(ARMS), sum(m["group"] == "R" for m in meta) // len(ARMS), len(reqs), len(todo), ntok / 1e6))
    if not a.yes:
        print("nothing sent: add --yes to run (add --pilot --yes first for a small trial)")
        return
    if not key:
        sys.exit("ANTHROPIC_API_KEY is not set.")
    os.makedirs(CACHE, exist_ok=True)

    def run(i):
        p = reqs[i]
        path = os.path.join(CACHE, hashlib.sha1(json.dumps(p, sort_keys=True).encode()).hexdigest() + ".json")
        if os.path.exists(path):
            return i, json.load(open(path))
        data = call_api(p, key)
        text = next((b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"), "")
        res = ns["parse_classification_result"](text)
        json.dump(res, open(path, "w"))
        return i, res
    t0, results = time.time(), {}
    with ThreadPoolExecutor(max_workers=4) as ex_:
        for n_done, (i, res) in enumerate(ex_.map(run, range(len(reqs))), 1):
            results[i] = res
            if n_done % 50 == 0:
                print("  %d/%d | %.0fs" % (n_done, len(reqs), time.time() - t0), flush=True)
    out = os.path.join(RESULTS, "exhibit_reclass_test_pilot.csv" if a.pilot else "exhibit_reclass_test.csv")
    rows = []
    for i, m in enumerate(meta):
        r = results[i]
        rows.append(dict(m, verdict=r.get("verdict", ""), confidence=r.get("confidence", ""), event_type=r.get("suggested_event_type") or "", reasoning=(r.get("reasoning") or "")[:300]))
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print("wrote %s | %d rows | %.0fs\n" % (out, len(rows), time.time() - t0))
    summarize(rows)


def summarize(rows):
    by = defaultdict(dict)
    for r in rows:
        by[(r["group"], r["accession"])][r["arm"]] = r
    A = [d for d in by.values() if "A" in d]
    ag = [d["A"]["verdict"] == d["A"]["stored"] for d in A if d["A"]["stored"]]
    print("REPLICATION: arm A agrees with the stored verdict on %s" % pct(sum(ag), len(ag)))
    print("\nSHARE CALLED real_event (and uncertain) BY GROUP AND ARM")
    def cell(ds, arm):
        v = [d[arm]["verdict"] for d in ds if arm in d]
        return "%s | unc %d" % (pct(sum(x == "real_event" for x in v), len(v)), sum(x == "uncertain" for x in v))
    groups = [("G all", [d for (g, _), d in by.items() if g == "G"]), ("G true guidance (my reading)", [d for (g, _), d in by.items() if g == "G" and d["A"]["label"] == "guidance"]),
              ("G not guidance (my reading)", [d for (g, _), d in by.items() if g == "G" and d["A"]["label"] == "not"]), ("G unknown", [d for (g, _), d in by.items() if g == "G" and d["A"]["label"] == "unknown"]),
              ("O control", [d for (g, _), d in by.items() if g == "O"]), ("R decided event", [d for (g, _), d in by.items() if g == "R" and d["A"]["label"] == "event"]),
              ("R decided not an event", [d for (g, _), d in by.items() if g == "R" and d["A"]["label"] == "not_an_event"])]
    for name, ds in groups:
        if ds:
            print("  %-30s n %3d | " % (name, len(ds)) + " | ".join("%s: %s" % (arm, cell(ds, arm)) for arm in ARMS))
    ev = groups[1][1] + groups[5][1]
    def sh(ds, arm): return sum(d[arm]["verdict"] == "real_event" for d in ds) / max(len(ds), 1)
    if ev:
        a_, b_, d_ = sh(ev, "A"), sh(ev, "B"), sh(ev, "D")
        ctrl = groups[4][1]
        ne = groups[6][1]
        print("\nRULE: true-guidance + R-event filings (n %d): real_event A %.0f%% -> B %.0f%% (+%.0f points) -> D %.0f%% (D - B %+.0f points)" % (len(ev), 100 * a_, 100 * b_, 100 * (b_ - a_), 100 * d_, 100 * (d_ - b_)))
        print("      control O: A %.0f%% -> D %.0f%% (%+.0f points) | R decided not an event: A %.0f%% -> D %.0f%% (%+.0f points)" % (100 * sh(ctrl, "A"), 100 * sh(ctrl, "D"), 100 * (sh(ctrl, "D") - sh(ctrl, "A")), 100 * sh(ne, "A"), 100 * sh(ne, "D"), 100 * (sh(ne, "D") - sh(ne, "A"))))
        noise = abs(sh(ev, "A2") - a_)
        print("      run-to-run NOISE: A -> A2 on the same filings moves real_event by %.0f points (control O: %+.0f points; filings whose verdict differs between A and A2: %d of %d)" % (100 * noise, 100 * (sh(ctrl, "A2") - sh(ctrl, "A")), sum(1 for d in by.values() if d["A"]["verdict"] != d["A2"]["verdict"]), len(by)))
        print("      THE EXHIBIT INPUT HELPS (B - A >= 20 points and the noise < 10): %s | THE RULE CHANGE HELPS (D - B >= 15, control O A -> D <= 8 points, R not-an-event A -> D <= 15 points): %s" % (
            "YES" if (b_ - a_ >= 0.20 and noise < 0.10) else "NO", "YES" if (d_ - b_ >= 0.15 and sh(ctrl, "D") - sh(ctrl, "A") <= 0.08 and sh(ne, "D") - sh(ne, "A") <= 0.15) else "NO"))
    print("\nFLIPS FROM A (real_event in the arm, not in A), by group")
    for name, ds in groups:
        if ds:
            print("  %-30s " % name + " | ".join("%s: %d" % (arm, sum(1 for d in ds if d[arm]["verdict"] == "real_event" and d["A"]["verdict"] != "real_event")) for arm in ARMS if arm != "A"))
    print("\nR: events FLAGGED for review (real_event or uncertain) per arm: " + " | ".join("%s %s" % (arm, pct(sum(d[arm]["verdict"] in ("real_event", "uncertain") for d in groups[5][1]), len(groups[5][1]))) for arm in ARMS if groups[5][1]))


if __name__ == "__main__":
    main()
