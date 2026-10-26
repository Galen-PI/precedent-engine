#!/usr/bin/env python3
"""
patch_tagger_baseline.py -- ONE-OFF repair (2026-10-26, version 2). Replaces ONLY compute_abnormal_return, in BOTH places it exists as the tagger's labelling function:
  scripts/tagging/tag_reaction_character.py and scripts/tagging/tag_multientity_reactions.py ("identical logic" copy)
so that the reaction label uses the SAME convention as compute_full_reaction (the saved columns) and the written project rule: the baseline is the PRIOR trading day's close, so the event day's own move is INCLUDED. Before this, the label used the first price on or after the event date as its base (the event-day close): the event-day move was excluded and 15.3% of stored labels disagreed with abnormal_return_20d.
ALL-OR-NOTHING: both files are checked first; if either is not exactly what this expects (one function with the expected signature, the old baseline line company_prices[0], and a following top-level def), nothing is written. Dry run by default (prints the diff); --apply writes both, checks that they compile, and restores both if not. Revert: git checkout -- scripts/tagging/
Run from the repository root:   python3 scripts/audit/patch_tagger_baseline.py [--apply]
"""
import sys, re, py_compile, difflib

TARGETS = ["scripts/tagging/tag_reaction_character.py", "scripts/tagging/tag_multientity_reactions.py"]
SIG = "def compute_abnormal_return(ticker: str, event_date: str, window_days: int) -> float | None:"
NEW = '''def compute_abnormal_return(ticker: str, event_date: str, window_days: int) -> float | None:
    """Abnormal return against SPY over the label window, on the SAME convention as compute_full_reaction
    (changed 2026-10-26): base = the PRIOR trading day's close (the event day's own move is INCLUDED);
    end = the window_days-th trading day on or after the event date. Before this change the base was the
    event-day close, so the label excluded the event-day move and disagreed with abnormal_return_20d in
    event_market_reactions_corrected for 15.3% of events (see CHANGELOG and docs/PROJECT_STATUS.md)."""
    _dt = __import__("datetime")
    d0 = _dt.date.fromisoformat(event_date)
    start = (d0 - _dt.timedelta(days=10)).isoformat()  # pad back so a prior close exists
    end = (d0 + _dt.timedelta(days=int(window_days * 1.6) + 12)).isoformat()  # pad for weekends and holidays

    company_prices = get_prices(ticker, start, end)
    spy_prices = get_prices("SPY", start, end)
    if len(company_prices) < 2 or len(spy_prices) < 2:
        return None

    idx = next((i for i, p in enumerate(company_prices) if p["price_date"] >= event_date), None)
    spy_idx = next((i for i, p in enumerate(spy_prices) if p["price_date"] >= event_date), None)
    if idx is None or spy_idx is None or idx == 0 or spy_idx == 0:
        return None  # no prior close, or no price on or after the event date
    # require the FULL window (a truncated window silently produced short-window labels before the 2026-09-28 fix)
    if idx + window_days >= len(company_prices) or spy_idx + window_days >= len(spy_prices):
        return None

    c0, c1 = company_prices[idx - 1]["adjusted_close"], company_prices[idx + window_days]["adjusted_close"]
    s0, s1 = spy_prices[spy_idx - 1]["adjusted_close"], spy_prices[spy_idx + window_days]["adjusted_close"]
    return (c1 / c0 - 1) - (s1 / s0 - 1)


'''


def plan(path):
    try:
        src = open(path, encoding="utf-8").read()
    except OSError as e:
        return None, "cannot read: %s" % e
    if src.count("def compute_abnormal_return(") != 1:
        return None, "expected exactly one def compute_abnormal_return"
    a = src.index("def compute_abnormal_return(")
    if not src[a:].startswith(SIG):
        return None, "the signature line is not the expected one"
    m = re.search(r"^(def |class |@)", src[a + 1:], re.M)
    if not m:
        return None, "no top-level def follows the function (cannot find where it ends)"
    end = a + 1 + m.start()
    old = src[a:end]
    if "company_prices[0]" not in old:
        return None, "the old baseline line company_prices[0] is not there (already patched?)"
    if "get_prices(" not in old:
        return None, "the old function does not call get_prices; this patch assumes it does"
    return (src, src[:a] + NEW + src[end:], old), None


def main():
    apply = "--apply" in sys.argv
    plans, bad = {}, []
    for p in TARGETS:
        r, why = plan(p)
        if r is None:
            bad.append("%s: %s" % (p, why))
        else:
            plans[p] = r
    if bad:
        raise SystemExit("REFUSED, nothing written:\n  " + "\n  ".join(bad))
    for p, (src, new_src, old) in plans.items():
        diff = list(difflib.unified_diff(src.split("\n"), new_src.split("\n"), "before", "after", lineterm="", n=0))
        print("== %s: old function %d lines, new function %d lines, diff lines %d" % (p, old.count("\n"), NEW.count("\n"), len(diff)))
        print("\n".join(diff[:50]))
    if not apply:
        print("\nDRY RUN: nothing written. Re-run with --apply."); return
    for p, (src, new_src, old) in plans.items():
        open(p, "w", encoding="utf-8").write(new_src)
    try:
        for p in plans:
            py_compile.compile(p, doraise=True)
    except py_compile.PyCompileError as e:
        for p, (src, new_src, old) in plans.items():
            open(p, "w", encoding="utf-8").write(src)
        raise SystemExit("compile failed, BOTH originals restored: %s" % e)
    print("\nWRITTEN and compile: %s. Revert with: git checkout -- scripts/tagging/" % ", ".join(plans))


if __name__ == "__main__":
    main()
