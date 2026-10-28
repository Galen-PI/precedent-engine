#!/usr/bin/env python3
"""
import_plan_addenda.py -- moves the seven correction / addendum sections of the ORIGINAL PROJECT_PLAN.md into CHANGELOG.md as entries at their TRUE dates (the date each section was first committed to the plan, from git log -S on 2026-10-28). Written 2026-10-28. Run from the repository root.
It INSERTS by text: no existing entry is touched (verified: every existing entry's lines are compared before and after). Each new entry keeps its original heading ('Original heading' line) and its text verbatim except that markdown headings inside it are demoted three levels (capped at 6) so they nest under the entry; '#' lines inside code fences are left alone. IDs follow the tool's rule (date-sequence; newest first within a date). Label = PROJECT_PLAN.
DRY RUN by default: prints where each entry would go and runs every check. --apply writes CHANGELOG.md only if all checks pass (and then runs the tool's own check).
The source must be the ORIGINAL plan (sha256 gate). Default: docs/archive/PROJECT_PLAN_pre_rewrite_2026-10-28.md if it exists, else PROJECT_PLAN.md (use --plan PATH to name another).
Usage:   python3 scripts/audit/import_plan_addenda.py            (dry run)      |      python3 scripts/audit/import_plan_addenda.py --apply
"""
import sys, os, re, hashlib, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import changelog_tools as C

PLAN_SHA = "2a54625a2a70c2b36d7331e9978b487f2c08b5f183dd7243d98d05653ad959ea"
SECTIONS = [("## Correction (verified this session)", "2026-09-08"), ("## Addendum 2:", "2026-09-15"), ("## Addendum 3:", "2026-09-22"),
            ("## Addendum: Macro Data Placement", "2026-09-29"), ("## Addendum: Government Decisions", "2026-09-29"),
            ("## Addendum: Population/Consumer Sentiment", "2026-09-29"), ("## Addendum: XOM's Quarterly Gap", "2026-09-30")]
MOVED = "> Moved from PROJECT_PLAN.md on 2026-10-28"
NOTE = MOVED + " (the section was first committed to the plan on %s). Text unchanged except that its headings are demoted three levels so they nest under this entry. The whole original file is in the git history and in docs/archive/PROJECT_PLAN_pre_rewrite_2026-10-28.md."


def demote(lines):
    out, fence = [], False
    for l in lines:
        if l.strip().startswith("```"):
            fence = not fence
            out.append(l)
            continue
        m = re.match(r"^(#{1,6}) (.*)$", l)
        out.append(("#" * min(6, len(m.group(1)) + 3) + " " + m.group(2)) if (m and not fence) else l)
    return out


def norm(l):
    return re.sub(r"^#{1,6} ", "", l.rstrip())


def split_plan(lines):
    heads = [i for i, l in enumerate(lines) if l.startswith("## ")]
    out = []
    for prefix, date in SECTIONS:
        i = next((k for k in heads if lines[k].startswith(prefix)), None)
        if i is None:
            sys.exit("STOP: section not found in the plan: " + prefix)
        j = next((k for k in heads if k > i), len(lines))
        body = lines[i + 1:j]
        while body and not body[-1].strip():
            body.pop()
        while body and not body[0].strip():
            body.pop(0)
        out.append({"heading": lines[i][3:].strip(), "date": date, "orig": body, "line": i + 1})
    return out


def trimmed(raw):
    r = list(raw)
    while r and not r[-1].strip():
        r.pop()
    return r


def insert_entry(text, sec):
    ents = C.parse_changelog(text)
    n = 1 + max([int(e["id"].rsplit("-", 1)[1]) for e in ents if e["date"] == sec["date"]] or [0])
    new = {"id": "%s-%02d" % (sec["date"], n), "date": sec["date"], "label": "PROJECT_PLAN", "src_line": "PLAN:%d" % sec["line"], "approx": False, "title": sec["heading"], "heading": sec["heading"], "body": [NOTE % sec["date"], ""] + demote(sec["orig"])}
    lines = text.split("\n")
    target = next((e for e in ents if e["date"] <= sec["date"]), None)
    block = C.render_entry(new)
    if target is None:
        idx, before = (len(lines) - 1 if lines and lines[-1] == "" else len(lines)), "(end of file: older than every entry)"
    else:
        m = next(k for k, l in enumerate(lines) if (C.META.match(l) and C.META.match(l).group(1) == target["id"]))
        if lines[m - 1] != "":
            sys.exit("STOP: unexpected layout before entry " + target["id"])
        idx, before = m - 1, target["id"]
    lines[idx:idx] = block
    return "\n".join(lines), new, before


def rebuild_index(text):
    head, rest = text.split(C.MARK_E, 1)
    i0, i1 = head.index(C.MARK_I0), head.index(C.MARK_I1)
    ents = C.parse_changelog(text)
    head = head[:i0] + C.MARK_I0 + "\n" + "\n".join(C.render_index(ents)) + "\n" + head[i1:]
    return head + C.MARK_E + rest


def check_text(text):
    ents = C.parse_changelog(text); ids = [e["id"] for e in ents]; probs = []
    if len(set(ids)) != len(ids):
        probs.append("duplicate IDs")
    ds = [e["date"] for e in ents]
    if ds != sorted(ds, reverse=True):
        probs.append("entries are not newest first")
    idx = text.split(C.MARK_I0)[1].split(C.MARK_I1)[0]
    if any(("| %s |" % i) not in idx for i in ids):
        probs.append("index is missing an entry")
    return probs, len(ents)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true"); ap.add_argument("--plan", default=""); a = ap.parse_args()
    plan = a.plan or next((p for p in ("docs/archive/PROJECT_PLAN_pre_rewrite_2026-10-28.md", "PROJECT_PLAN.md") if os.path.exists(p)), "")
    raw = open(plan, encoding="utf-8").read() if plan else ""
    got = hashlib.sha256((raw if raw.endswith("\n") else raw + "\n").encode()).hexdigest()
    if got != PLAN_SHA:
        sys.exit("STOP: %s is not the original PROJECT_PLAN.md (expected sha256 %s, found %s). Nothing written." % (plan or "(no plan file)", PLAN_SHA[:16], got[:16]))
    text0 = open(C.CHANGELOG, encoding="utf-8").read()
    old = C.parse_changelog(text0)
    if any(MOVED in "\n".join(e["raw"]) for e in old):
        sys.exit("STOP: the plan sections were already imported. Nothing written.")
    secs = split_plan(raw.split("\n"))
    text, news, plan_rows = text0, [], []
    for s in secs:
        text, new, before = insert_entry(text, s)
        news.append((s, new)); plan_rows.append((new["id"], new["date"], before, len(s["orig"]), s["heading"][:70]))
    text = rebuild_index(text)
    print("source: %s (original, sha256 verified); changelog entries before: %d" % (plan, len(old)))
    for r in plan_rows:
        print("  %s  %s  inserted before %-38s %3d lines  %s" % r)
    problems, n_after = check_text(text)
    after = {e["id"]: e for e in C.parse_changelog(text)}
    changed = [e["id"] for e in old if trimmed(after[e["id"]]["raw"]) != trimmed(e["raw"])] if all(e["id"] in after for e in old) else ["<missing>"]
    print("existing entries kept byte-identical: %s (%d of %d compared)" % ("YES" if not changed else "NO " + str(changed[:5]), len(old) - len(changed), len(old)))
    lost = 0
    for s, new in news:
        body = [l for l in C.body_of(after[new["id"]])]
        mine = [norm(l) for l in body if l.strip()][1:]   # drop the 'Moved from' note
        want = [norm(l) for l in s["orig"] if l.strip()]
        if mine != want:
            lost += 1
            print("  TEXT MISMATCH in", new["id"])
    print("original text of the 7 sections present line for line (headings demoted): %s" % ("YES" if not lost else "NO"))
    print("tool-style check on the result: %s (entries after: %d)" % ("OK" if not problems else "FAILED: " + "; ".join(problems), n_after))
    if problems or changed or lost:
        sys.exit("STOP: a check failed. Nothing written.")
    if not a.apply:
        print("DRY RUN: nothing written (add --apply)")
        return
    open(C.CHANGELOG, "w", encoding="utf-8").write(text)
    print("wrote %s" % C.CHANGELOG)
    sys.exit(C.cmd_check())


if __name__ == "__main__":
    main()