#!/usr/bin/env python3
"""
earnings_role_forward_test.py -- READ-ONLY (matrices, the OHLC cache, the database for 8-K filings and recorded events, the frozen model files). Writes nothing.
Implements, WITHOUT CHANGES, the rule frozen in results/FROZEN_role_band_forward_test_2026-10-22.md (commit fdac0a2). Read that file first; this header only records how it is run.
MODES. Default = READINESS: counts only; no interval score, coverage or ratio is computed or printed (that code path is not reached). --evaluate = the verdict; run it ONCE, after prices and matrices exist through 2027-01-04 (the first trading day after the last possible release in the window).
FREEZE CHECK. The SHA-256 of every file listed in the freeze file is recomputed and compared with the recorded hash; --evaluate REFUSES to run if any differs (editing the models, earnings_roles.py, day_card.py or the walk-forward test is forbidden before the verdict). This script itself is hashed AFTER it is committed (append its hash to the freeze file under a heading 'frozen script').
IMPLEMENTATION CHOICES WHERE THE FROZEN TEXT IS SILENT (made before any outcome exists): (1) verdict precedence TOO FEW, then VOID (placebo), then NOT SHOWN, then PARTIAL, then PASS; (2) the window is by FILING DATE (2026-10-14 .. 2026-12-31 inclusive); an event is EVALUABLE only if day i+1 exists in the matrices and both band units are finite; events not yet evaluable are counted, never guessed;
(3) 'isolated' is the walk-forward's definition: a filing that carries item 2.02 counts as earnings even if it also carries 7.01; a 7.01-only filing flags days i and i+1; own recorded events come from event_width_test.load_event_info (the table ends 2026-09-11, so this is vacuous in the window, as documented); (4) habits and ties come from earnings_roles.habit_at / is_tie, exactly as on the card, with first_year 2006;
(5) POOLED half-widths = band_calibration edge_90 ('earnings window, day 0 (no event)' and 'day +1 (no event)') x earnings_band_model multipliers earnings_day0 / earnings_day1; CARD role half-widths = the role model's q90_ordinary_units for the reaction and the other day; (6) the placebo permutes habits among CLEAR-habit events (ties stay pooled), 200 shuffles, the mean ratio is used.
Usage:   python3 -u scripts/card/earnings_role_forward_test.py               readiness counts only
         python3 -u scripts/card/earnings_role_forward_test.py --evaluate    the verdict (ONCE)
"""
import os, sys, re, json, bisect, time, hashlib, warnings
from collections import defaultdict
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import day_card as dc
import unrecorded_candidates as uc
import earnings_roles as er

ROOT = er.ROOT
CACHE_FILE = uc.CACHE_FILE
ROLE_MODEL_PATH = os.path.join(ROOT, "models", "earnings_role_band_model.json")
EARN_MODEL_PATH = os.path.join(ROOT, "models", "earnings_band_model.json")
CALIB_PATH = os.path.join(ROOT, "models", "band_calibration.json")
FROZEN_DOC = os.path.join(ROOT, "results", "FROZEN_role_band_forward_test_2026-10-22.md")
OHLC_DIR = None
WINDOW_START, WINDOW_END = "2026-10-14", "2026-12-31"
EVAL_MIN_DATE = "2027-01-04"
MIN_CLEAR, RATIO_MAX, LOW, HIGH, PLACEBO_MIN = 250, 0.98, 0.86, 0.94, 0.99
SHUFFLES, BOOT, SEED, PEN, Z = 200, 2000, 20261022, 20.0, 1.96
G_P0, G_P1 = "earnings window, day 0 (no event)", "earnings window, day +1 (no event)"


def wilson(c, n):
    if n == 0:
        return float("nan"), float("nan")
    p = c / n
    d = 1 + Z * Z / n
    ctr = (p + Z * Z / (2 * n)) / d
    h = Z * np.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return ctr - h, ctr + h


def freeze_check():
    rows = []
    try:
        lines = open(FROZEN_DOC).read().splitlines()
    except OSError:
        return [("(freeze file)", "MISSING: " + FROZEN_DOC)]
    for ln in lines:
        m = re.match(r"^([0-9a-f]{64})\s+(\S+)$", ln.strip())
        if m:
            path = os.path.join(ROOT, m.group(2))
            try:
                cur = hashlib.sha256(open(path, "rb").read()).hexdigest()
            except OSError:
                rows.append((m.group(2), "MISSING"))
                continue
            rows.append((m.group(2), "ok" if cur == m.group(1) else "CHANGED"))
    return rows or [("(freeze file)", "no hash lines found")]


def load_halfwidths():
    rm, em, cal = (json.load(open(p)) for p in (ROLE_MODEL_PATH, EARN_MODEL_PATH, CALIB_PATH))
    R, O = rm["groups"][er.REACTION]["q90_ordinary_units"], rm["groups"][er.OTHER]["q90_ordinary_units"]
    P0 = cal["edge_90"][G_P0] * em["multipliers_vs_ordinary_day"]["earnings_day0"]
    P1 = cal["edge_90"][G_P1] * em["multipliers_vs_ordinary_day"]["earnings_day1"]
    return R, O, P0, P1


def IS(x, h):
    return 2.0 * h + PEN * np.maximum(x - h, 0.0)


def decide(n_clear, ratio, ub, covR, covO, plc):
    if n_clear < MIN_CLEAR:
        return "TOO FEW"
    a = ratio <= RATIO_MAX and ub < 1.0
    b = LOW <= covR <= HIGH and LOW <= covO <= HIGH
    c = plc >= PLACEBO_MIN
    if not c:
        return "VOID"
    if not a:
        return "NOT SHOWN"
    return "PASS" if b else "PARTIAL"


def collect(sb, dl, ids, bu):
    n, N = len(dl), len(ids)
    idx = {sid: k for k, sid in enumerate(ids)}
    einfo, _, _ = ew.load_event_info(sb, dl, set(ids))
    oth = np.zeros((N, n), dtype=bool)
    for sid, days in einfo.items():
        k = idx.get(sid)
        if k is not None:
            for t in days:
                oth[k, t] = True
    ev, win = defaultdict(list), []
    for r in uc.paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes").order("id")):
        k = idx.get(r["security_id"])
        if k is None:
            continue
        its = dc.parse_items(r.get("item_codes"))
        date = str(r["filing_date"])[:10]
        i = bisect.bisect_left(dl, date)
        if "2.02" in its:
            ev[k].append(i)
            if WINDOW_START <= date <= WINDOW_END:
                win.append((k, i, date))
        elif "7.01" in its and i < n:
            oth[k, i] = True
            if i + 1 < n:
                oth[k, i + 1] = True
    first_i = next((j for j, x in enumerate(dl) if int(x[:4]) >= 2006), 0)
    cnt = defaultdict(int)
    cnt["window_filings"] = len(win)
    cnt["securities_with_a_window_release"] = len({k for k, _, _ in win})
    rows, zg_cache = [], {}
    for k, i0, date in sorted(win):
        if i0 + 1 >= n:
            cnt["not_yet_evaluable (day i+1 beyond the price data)"] += 1
            continue
        if oth[k, i0] or oth[k, i0 + 1]:
            cnt["not isolated (7.01 or recorded event)"] += 1
            continue
        if not (np.isfinite(bu[k, i0]) and np.isfinite(bu[k, i0 + 1])):
            cnt["band units not finite"] += 1
            continue
        if k not in zg_cache:
            oc = er.load_one_ohlc(ids[k], dl, OHLC_DIR)
            zg_cache[k] = None if oc is None else er.gap_z_1d(*oc)
        if zg_cache[k] is None:
            cnt["no OHLC history"] += 1
            continue
        hab = er.habit_at(ev[k], zg_cache[k], i0, n, first_i)
        if hab is None:
            cnt["no forward habit (fewer than 4 classifiable earlier quarters, or thinned)"] += 1
            continue
        tie = er.is_tie(hab)
        cnt["tie (2-2): pooled band"] += int(tie)
        cnt["clear habit"] += int(not tie)
        rows.append((abs(float(bu[k, i0])), abs(float(bu[k, i0 + 1])), hab["habit"], tie))
    return rows, cnt


def evaluate(rows, R, O, P0, P1):
    b0, b1 = np.array([r[0] for r in rows]), np.array([r[1] for r in rows])
    hab, tie = np.array([r[2] for r in rows]), np.array([r[3] for r in rows])
    clear = ~tie

    def card_is(h):
        h0 = np.where(tie, P0, np.where(h == 0, R, O))
        h1 = np.where(tie, P1, np.where(h == 1, R, O))
        return IS(b0, h0) + IS(b1, h1)
    pooled = IS(b0, P0) + IS(b1, P1)
    card = card_is(hab)
    ratio = float(card.sum() / pooled.sum())
    rng = np.random.RandomState(SEED)
    bs = np.empty(BOOT)
    for j in range(BOOT):
        ix = rng.randint(0, len(b0), len(b0))
        bs[j] = card[ix].sum() / pooled[ix].sum()
    lo_, hi_ = np.percentile(bs, [2.5, 97.5])
    cl = np.where(clear)[0]
    xr = np.where(hab[cl] == 0, b0[cl], b1[cl])
    xo = np.where(hab[cl] == 0, b1[cl], b0[cl])
    cR, cO = int((xr <= R).sum()), int((xo <= O).sum())
    prng = np.random.RandomState(SEED + 1)
    plc = []
    for _ in range(SHUFFLES):
        h = hab.copy()
        h[cl] = prng.permutation(hab[cl])
        plc.append(card_is(h).sum() / pooled.sum())
    return dict(n=len(b0), n_clear=len(cl), ratio=ratio, lo=float(lo_), hi=float(hi_), covR=cR / max(len(cl), 1), covO=cO / max(len(cl), 1), cR=cR, cO=cO, plc=float(np.mean(plc)))


def main():
    t0 = time.time()
    do_eval = "--evaluate" in sys.argv
    print("FREEZE CHECK (SHA-256 of the frozen files against %s):" % os.path.basename(FROZEN_DOC))
    fc = freeze_check()
    for p, s in fc:
        print("  %-48s %s" % (p, s))
    ok = all(s == "ok" for _, s in fc)
    if do_eval and not ok:
        print("\nREFUSING --evaluate: a frozen file changed or is missing. Restore it (git checkout) or record in the ledger why the deployed logic changed; the verdict is only valid for the frozen files.")
        sys.exit(2)
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, ids, E_, SD = d["dates"], d["ids"].tolist(), d["E"].astype(np.float64), d["SD"].astype(np.float64)
    dl = [str(x) for x in dates]
    with np.errstate(invalid="ignore", divide="ignore"):
        Zsq = (E_ / SD) ** 2
    valid0 = np.isfinite(Zsq)
    S = np.where(valid0, Zsq, 0.0).sum(axis=0)
    cn = valid0.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        bu = np.sqrt(Zsq / ((S[None, :] - np.where(valid0, Zsq, 0.0)) / (cn[None, :] - 1)))
    bu[~((cn[None, :] > 20) & np.isfinite(bu))] = np.nan
    print("\nmatrices end %s | window %s..%s (by filing date)" % (dl[-1], WINDOW_START, WINDOW_END), flush=True)
    if do_eval and dl[-1] < EVAL_MIN_DATE:
        print("NOT EVALUATING: the matrices end %s, before %s (the first trading day after the last possible release). Refresh prices, the caches and the matrices first." % (dl[-1], EVAL_MIN_DATE))
        sys.exit(3)
    sb = ew.get_sb()
    rows, cnt = collect(sb, dl, ids, bu)
    print("\nCOUNTS")
    for k_, v_ in sorted(cnt.items(), key=lambda kv: -kv[1]):
        print("  %-72s %d" % (k_, v_))
    print("  %-72s %d" % ("EVALUATED events with a forward habit (clear + tie)", len(rows)))
    if not do_eval:
        print("\nReadiness only: no interval score, coverage or ratio was computed. Minimum for a verdict: %d evaluated clear-habit events. Run with --evaluate ONCE after the matrices reach %s. Total %.0fs" % (MIN_CLEAR, EVAL_MIN_DATE, time.time() - t0))
        return cnt, None
    R, O, P0, P1 = load_halfwidths()
    res = evaluate(rows, R, O, P0, P1)
    lR, uR = wilson(res["cR"], res["n_clear"])
    lO, uO = wilson(res["cO"], res["n_clear"])
    print("\nHALF-WIDTHS (ordinary band units): pooled day 0 %.3f, day +1 %.3f | role reaction %.3f, other %.3f" % (P0, P1, R, O))
    print("RESULT: %d evaluated events (%d clear habit)" % (res["n"], res["n_clear"]))
    print("  interval-score ratio CARD / POOLED %.3f  [95%% bootstrap %.3f, %.3f]   (rule: <= %.2f and upper bound < 1.00)" % (res["ratio"], res["lo"], res["hi"], RATIO_MAX))
    print("  CARD coverage on reaction days %.1f%% [%.1f, %.1f], other days %.1f%% [%.1f, %.1f]   (rule: %.0f-%.0f%% on both)" % (100 * res["covR"], 100 * lR, 100 * uR, 100 * res["covO"], 100 * lO, 100 * uO, 100 * LOW, 100 * HIGH))
    print("  PLACEBO mean ratio (200 shuffles) %.3f   (rule: >= %.2f)" % (res["plc"], PLACEBO_MIN))
    v = decide(res["n_clear"], res["ratio"], res["hi"], res["covR"], res["covO"], res["plc"])
    print("\nVERDICT (frozen rule, precedence TOO FEW > VOID > NOT SHOWN > PARTIAL > PASS): %s" % v)
    print("total %.0fs" % (time.time() - t0))
    return cnt, (res, v)


if __name__ == "__main__":
    main()
