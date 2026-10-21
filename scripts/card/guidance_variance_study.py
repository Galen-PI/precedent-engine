#!/usr/bin/env python3
"""
guidance_variance_study.py -- READ-ONLY (local matrices; the database is read for 8-K filings and recorded events; SEC is fetched through add_exhibit_excerpts.excerpt_for, cached in data_cache/sec_excerpts). Writes results/guidance_variance_sample.csv.
THE QUESTION. The classifier calls quantified guidance revisions and earnings warnings that arrive as press-release exhibits under Items 8.01 / 7.01 NOISE, and the review of the top big-miss filings suggests they are events. Policy (Galen): such filings should count as events, but first see how the
VARIANCE is affected. The 25 reviewed rows were chosen BECAUSE the stock moved a lot, so they cannot answer that. This study samples by CONTENT, not by reaction.
POPULATION. Every 8-K filing from 2006 with Item 8.01 or 7.01 and NO Item 2.02, for a stock in the matrices, ISOLATED: no Item 2.02 filing of the stock within 3 trading days either side of its day i (the first trading day on or after the filing date), no other filing of the stock on days i-1..i+1, no
recorded-event day on days i-1..i+2. A seeded random SAMPLE of 1,500 is drawn without looking at any price move.
CLASSIFICATION (crude and stated plainly): each sampled filing's first EX-99 exhibit (first 1,200 characters of cleaned text) is sorted into E = an earnings-results headline (reports/announces ... first|second|third|fourth quarter, fiscal year results, full-year results), else G = guidance, outlook or warning language
(guidance/outlook/forecast/expects/anticipates/projects within 150 characters of a number AND an earnings word; 'below consensus / expectations'; preliminary results; revises guidance), else O = other exhibit, and N = no exhibit in the submission.
MEASURE. For each filing the 2-DAY MEAN squared band unit over days i and i+1 (band units on the ordinary scale), because the release time is unknown. MULTIPLIER of a group = sqrt(mean of that 2-day mean / the mean squared band unit on QUIET stock-days), where quiet = no filing of the stock on days t-1..t, no recorded event on
t-1..t+1 and no Item 2.02 within 3 days either side. Intervals resample calendar MONTHS (500 resamples). Reference: Item 2.02 filings measured the same way. CONTRIBUTION: filings of the group in the whole population = population count x the group's share in the sample; each adds 2 stock-days with extra squared miss
(multiplier^2 - 1) x the quiet mean; the share of the ORDINARY POOL's total squared miss (all stock-days from 2006 outside earnings windows and recorded events) they account for is that sum over the pool's total.
PRE-SET RULE: GUIDANCE-TYPE FILINGS ARE A MATERIAL VARIANCE SOURCE if (i) the G multiplier is at least 1.5x the multiplier of the O + N filings (ratio at least 1.5 with the 95% interval's lower end above 1.2) AND (ii) G filings account for at least 1.0% of the ordinary pool's total squared miss.
PREDICTIONS (before the real run): E about 5-10% of the sample and G about 5-10%; exhibits found for 70-85% of filings; multipliers E 2.0-3.0x, G 1.5-2.5x, O + N 1.05-1.2x (a 2.02 reference of about 2.6x); G accounts for 0.5-2% of the ordinary pool's squared miss, E for 0.5-2%;
MATERIAL with probability about 40%. The keyword classes are crude: they are checked by printing examples, not by a score.
Usage:   export SEC_USER_AGENT="stock-research1 you@yourdomain.com"      then      python3 -u scripts/card/guidance_variance_study.py        (the first run fetches about 1,500 exhibits: roughly 10 minutes; later runs use the cache)
"""
import os, sys, re, csv, time, bisect, random, warnings
from collections import defaultdict, Counter
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import day_card as dc
import unrecorded_candidates as uc
import add_exhibit_excerpts as ae

CACHE_FILE = uc.CACHE_FILE
RESULTS = ae.RESULTS
TEST_START = 2006
SAMPLE_N = 1500
SEED = 20261021
N_BOOT = 500
SHOW = 1200
GROUPS = ["E", "G", "O", "N"]
NUM = r"(?:\$\s?\d|\d+(?:\.\d+)?\s?(?:percent|%))"
EARN = r"(?:earnings|eps|income|revenue|revenues|sales|profit|per share)"
GUIDE = r"(?:guidance|outlook|forecast|expects?|anticipates?|projects?)"
RE_RESULTS = re.compile(r"(?:reports?|announces?)[^.]{0,60}?(?:(?:first|second|third|fourth)\s+quarter|fiscal\s+(?:year\s+)?\d{4}|full[- ]year|year[- ]end|q[1-4])[^.]{0,40}?results|(?:first|second|third|fourth)\s+quarter\s+(?:\d{4}\s+)?(?:financial\s+)?results", re.I)
RE_WARN = re.compile(r"(?:below|lower than|less than|short of|miss\w*)\s+(?:the\s+)?(?:analyst|analysts|street|consensus|expectations|prior guidance|previous guidance|its guidance)|shortfall|revis\w+\s+(?:its\s+|our\s+)?(?:\w+\s+)?(?:guidance|outlook|forecast)|preliminary\s+(?:\w+\s+)?(?:results|revenue|earnings)|pre-?announce", re.I)
RE_GUIDE = re.compile(GUIDE + r"[^.]{0,150}?" + NUM + r"|" + NUM + r"[^.]{0,150}?" + GUIDE, re.I)


def classify(text):
    t = text[:SHOW]
    if RE_RESULTS.search(t):
        return "E"
    if RE_WARN.search(t) or (RE_GUIDE.search(t) and re.search(EARN, t, re.I)):
        return "G"
    return "O"


def pct(x):
    return "%5.1f%%" % (100.0 * x) if np.isfinite(x) else "  n/a "


def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def main():
    t0 = time.time()
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, ids, E_, SD = d["dates"], d["ids"].tolist(), d["E"], d["SD"]
    N, n = E_.shape
    dl = [str(x) for x in dates]
    years = np.array([int(x[:4]) for x in dl])
    months = np.array([(int(x[:4]) - TEST_START) * 12 + int(x[5:7]) - 1 for x in dl])
    M = int(months.max()) + 1
    with np.errstate(invalid="ignore", divide="ignore"):
        Zsq = (E_.astype(np.float64) / SD.astype(np.float64)) ** 2
    valid = np.isfinite(Zsq)
    S = np.where(valid, Zsq, 0.0).sum(axis=0)
    cnt = valid.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        qo = (S[None, :] - np.where(valid, Zsq, 0.0)) / (cnt[None, :] - 1)
        bu2 = Zsq / qo
    bu2[~((cnt[None, :] > 20) & np.isfinite(bu2))] = np.nan
    fin = np.isfinite(bu2)

    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids)}
    einfo, use_labels, nlab = ew.load_event_info(sb, dl, set(ids))
    EV = np.zeros((N, n), dtype=bool)
    for sid, days in einfo.items():
        k = idx.get(sid)
        if k is not None:
            for t in days:
                EV[k, t] = True
    filings = []                                                       # (k, i, items set, url, accession)
    for r in uc.paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes,accession_number,primary_document_url").order("id")):
        k = idx.get(r["security_id"])
        if k is None:
            continue
        i = bisect.bisect_left(dl, str(r["filing_date"])[:10])
        if i < n:
            filings.append((k, i, set(dc.parse_items(r.get("item_codes"))), r.get("primary_document_url") or "", r.get("accession_number") or ""))
    any_days, eps_days = defaultdict(list), defaultdict(list)
    touched = np.zeros((N, n), dtype=bool)
    earn_win = np.zeros((N, n), dtype=bool)
    for k, i, items, url, acc in filings:
        any_days[k].append(i)
        touched[k, max(i - 1, 0): i + 1] = True                       # a filing on day i touches days i-1..i (quiet = no filing on t-1..t)
        if "2.02" in items:
            eps_days[k].append(i)
            earn_win[k, i: min(i + 2, n)] = True
    for k in list(any_days):
        any_days[k].sort()
        eps_days[k].sort()
    evn = EV.copy()
    evn[:, 1:] |= EV[:, :-1]
    evn[:, :-1] |= EV[:, 1:]
    eps_near = np.zeros((N, n), dtype=bool)
    for k, ds in eps_days.items():
        for i in ds:
            eps_near[k, max(i - 3, 0): i + 4] = True
    quiet = fin & ~touched & ~evn & ~eps_near & (years >= TEST_START)[None, :]
    base = float(bu2[quiet].mean())
    base_med = float(np.median(bu2[quiet]))
    ordinary = fin & ~earn_win & ~EV & (years >= TEST_START)[None, :]
    tot_sq, n_ord = float(bu2[ordinary].sum()), int(ordinary.sum())

    def count_in(lst, a, b):
        return bisect.bisect_right(lst, b) - bisect.bisect_left(lst, a)
    pop = []
    for k, i, items, url, acc in filings:
        if years[i] < TEST_START or i + 1 >= n or "2.02" in items or not (items & {"8.01", "7.01"}):
            continue
        if count_in(eps_days.get(k, []), i - 3, i + 3) or count_in(any_days[k], i - 1, i + 1) != 1 or EV[k, max(i - 1, 0): i + 3].any():
            continue
        if not (fin[k, i] and fin[k, i + 1]):
            continue
        pop.append((k, i, url, acc))
    rng = random.Random(SEED)
    smp = rng.sample(pop, min(SAMPLE_N, len(pop)))
    print("quiet-day mean squared band unit %.3f (median %.3f) | ordinary pool %d stock-days | eligible isolated 8.01/7.01 filings %d | sample %d | %.0fs" % (base, base_med, n_ord, len(pop), len(smp), time.time() - t0), flush=True)

    ua_ok = ("@" in ae.UA) and not any(w in ae.UA for w in ("example.com", "YOUR_REAL", "your"))
    rows, nfail = [], 0
    for j, (k, i, url, acc) in enumerate(smp):
        need = ae.parse_url(url)
        cached = need is not None and os.path.exists(os.path.join(ae.CACHE, need[1] + ".json"))
        if need is not None and not cached and not ua_ok:
            sys.exit("Set SEC_USER_AGENT to a real contact first (the SEC blocks made-up ones), e.g.  export SEC_USER_AGENT=\"stock-research1 you@yourdomain.com\"")
        res = ae.excerpt_for(url) if need is not None else {"type": "", "excerpt": "", "status": "no accession in URL"}
        if not res["excerpt"] and res["status"].startswith(("failed", "http")) and "no EX-99" not in res["status"]:
            nfail += 1
        g = classify(res["excerpt"]) if res["excerpt"] else "N"
        m = (bu2[k, i] + bu2[k, i + 1]) / 2.0
        rows.append((g, float(m), int(months[i]), dl[i], ids[k], res["excerpt"][:160], acc))
        if (j + 1) % 250 == 0:
            print("  %d/%d | %.0fs" % (j + 1, len(smp), time.time() - t0), flush=True)
    print("fetched: %d filings | fetch failures (not 'no exhibit') %d" % (len(rows), nfail))
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "guidance_variance_sample.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["group", "two_day_mean_bu2", "date", "security_id", "excerpt_start", "accession_number"])
        for g, m, mo, dt, sid, ex, acc_ in rows:
            w.writerow([g, "%.3f" % m, dt, sid, ex, acc_])

    # reference: item 2.02 filings measured the same way
    ref = [(bu2[k, i] + bu2[k, i + 1]) / 2.0 for k, i, items, url, acc in filings if "2.02" in items and years[i] >= TEST_START and i + 1 < n and fin[k, i] and fin[k, i + 1]]
    print("reference (all Item 2.02 filings, same 2-day method): n %d, multiplier %.2fx\n" % (len(ref), np.sqrt(np.mean(ref) / base)))

    arr_g = np.array([r[0] for r in rows])
    arr_m = np.array([r[1] for r in rows])
    arr_mo = np.array([r[2] for r in rows])
    nS = len(rows)
    print("GROUP  %6s %9s %17s | %10s %17s | %s" % ("n", "share", "95% interval", "multiplier", "95% interval", "median-based multiplier"))
    sums = {g: np.bincount(arr_mo[arr_g == g], weights=arr_m[arr_g == g], minlength=M) for g in GROUPS + ["ON"]}
    cnts = {g: np.bincount(arr_mo[arr_g == g], minlength=M).astype(float) for g in GROUPS}
    sums["ON"] = sums["O"] + sums["N"]
    cnts["ON"] = cnts["O"] + cnts["N"]
    allc = np.bincount(arr_mo, minlength=M).astype(float)
    live = np.where(allc > 0)[0]
    brng = np.random.RandomState(SEED)
    W = [np.bincount(brng.choice(live, size=len(live)), minlength=M).astype(float) for _ in range(N_BOOT)]
    def mult(g, w):
        den = w @ cnts[g]
        return np.sqrt((w @ sums[g]) / den / base) if den > 0 else float("nan")
    for g in GROUPS:
        k_ = int((arr_g == g).sum())
        lo, hi = wilson(k_, nS)
        bs = np.nanpercentile([mult(g, w) for w in W], [2.5, 97.5])
        med = np.sqrt(np.median(arr_m[arr_g == g]) / base_med) if k_ else float("nan")
        print("%-5s %6d %9s [%5.1f%%, %5.1f%%] | %9.2fx [%5.2f, %5.2f] | %.2fx" % (g, k_, pct(k_ / nS), 100 * lo, 100 * hi, mult(g, np.ones(M)), bs[0], bs[1], med))
    mON = mult("ON", np.ones(M))
    print("O + N %5d %9s %-17s | %9.2fx" % (int((arr_g == "O").sum() + (arr_g == "N").sum()), pct(float(np.mean((arr_g == "O") | (arr_g == "N")))), "", mON))
    ratios = [mult("G", w) / mult("ON", w) for w in W]
    r_pt, r_lo, r_hi = mult("G", np.ones(M)) / mON, np.nanpercentile(ratios, 2.5), np.nanpercentile(ratios, 97.5)
    print("\nG multiplier / (O + N) multiplier = %.2f [%.2f, %.2f]" % (r_pt, r_lo, r_hi))

    def contrib(g, w):
        share = (w @ cnts[g]) / max(w @ allc, 1.0)
        m = mult(g, w)
        return len(pop) * share * 2.0 * base * (m * m - 1.0) / tot_sq if np.isfinite(m) else float("nan")
    out = {}
    for g in ("G", "E"):
        pt = contrib(g, np.ones(M))
        bs = np.nanpercentile([contrib(g, w) for w in W], [2.5, 97.5])
        out[g] = (pt, bs[0], bs[1])
        print("CONTRIBUTION of %s filings to the ordinary pool's total squared miss: %.2f%% [%.2f%%, %.2f%%]  (population %d filings x share x 2 days x extra squared miss / pool total)" % (g, 100 * pt, 100 * bs[0], 100 * bs[1], len(pop)))
    material = (r_pt >= 1.5 and r_lo > 1.2) and out["G"][0] >= 0.01
    print("\nVERDICT (pre-set: ratio >= 1.5 with the lower end above 1.2, AND G accounts for >= 1.0%% of the pool's squared miss): GUIDANCE-TYPE FILINGS ARE %s" % ("A MATERIAL VARIANCE SOURCE" if material else "NOT shown to be a material variance source"))
    try:                                                           # descriptive only (added after the first run; nothing above depends on it)
        labs, accs = {}, sorted({r[6] for r in rows if r[6]})
        for i0 in range(0, len(accs), 100):
            for q in sb.table("filing_ai_classifications").select("accession_number,ai_verdict").in_("accession_number", accs[i0:i0 + 100]).execute().data:
                labs[q["accession_number"]] = q["ai_verdict"]
        print("\nCLASSIFIER VERDICT BY GROUP (the sample's accession numbers joined to filing_ai_classifications; descriptive):")
        for g in GROUPS:
            vs_ = [labs.get(r[6], "(no label)") for r in rows if r[0] == g]
            c = Counter(vs_)
            print("  %s n %3d: %s" % (g, len(vs_), ", ".join("%s %d (%.0f%%)" % (k_, v_, 100.0 * v_ / max(len(vs_), 1)) for k_, v_ in c.most_common())))
    except Exception as e:
        print("classifier labels not available: %s" % str(e)[:100])
    rr = random.Random(SEED + 1)
    for g in ("G", "E", "O"):
        ex = [r for r in rows if r[0] == g]
        print("\nfive random %s excerpts (the classes are crude; read them):" % g)
        for r in rr.sample(ex, min(5, len(ex))):
            print("  %s %.1f | %s" % (r[3], r[1], r[5][:140]))
    print("\ntotal %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
