#!/usr/bin/env python3
"""
changelog_tools.py -- retires the SCRIPTS.md monolith and runs the changelog (written 2026-10-26). Run from the repository root.
  split [--apply]            reads SCRIPTS.md and builds CHANGELOG.md (every dated entry, NEWEST FIRST, a stable ID per entry, an index), docs/OPERATIONS.md (the old Part 1 reference text, verbatim, with a banner) and a retirement stub; DRY RUN unless --apply. It VERIFIES that every non-blank line of the original survives. With --apply it copies the original to docs/archive/SCRIPTS_monolith_2026-10-26.md first (refuses to overwrite anything that exists unless --force).
  add --title T [--label L] [--date YYYY-MM-DD]     adds an entry at the TOP of CHANGELOG.md from standard input (body), assigns the next ID of that date, rebuilds the index.
  check                      verifies CHANGELOG.md (IDs unique, newest first, index matches the entries).
ID = date-sequence (2026-10-26-12): the sequence counts the entries of that date, oldest first. An entry without an exact date in its heading inherits the date of the entry before it in the source file and is marked 'date approximate'.
"""
import re, sys, os, argparse, datetime, shutil, collections

SRC, CHANGELOG, OPS = "SCRIPTS.md", "CHANGELOG.md", "docs/OPERATIONS.md"
ARCHIVE = "docs/archive/SCRIPTS_monolith_2026-10-26.md"
HEAD = re.compile(r"^(#{1,3}) (.*)$")
DATE = re.compile(r"(20\d\d-\d\d-\d\d)")
START_DATE = re.compile(r"^(?:Earlier\s+)?(20\d\d-\d\d-\d\d)")
START_MONTH = re.compile(r"^(20\d\d-\d\d)\b")
PAREN_DATE = re.compile(r"\((20\d\d-\d\d-\d\d)")
MARK_I0, MARK_I1, MARK_E = "<!-- INDEX-START -->", "<!-- INDEX-END -->", "<!-- ENTRIES-START -->"
META = re.compile(r"^<!-- entry: (\S+) \| date: (\S+) \| label: (.*?) \| source-line: (\S+) \| approx: (\S+) -->$")


def label_of(text):
    m = re.search(r"\(addendum (\d+)(?: to note (\d+))?", text)
    if m:
        return "addendum %s%s" % (m.group(1), " (note %s)" % m.group(2) if m.group(2) else "")
    m = re.search(r"CONSOLIDATED NOTE (\d+)", text, re.I)
    if m:
        return "note %s" % m.group(1)
    if re.search(r"CONSOLIDATED STATE OF PLAY", text, re.I):
        return "note 1 (state of play)"
    if text.startswith("CORRECTION TO"):
        return "correction"
    return ""


def entry_date(text, is_corr, prev):
    """an exact date only from the START of the heading or a trailing parenthesis (never from inside the title); a month-only or undated heading inherits the entry before it in the source file (approximate)."""
    m = START_DATE.match(text)
    if m:
        return m.group(1), False
    m = START_MONTH.match(text)
    if m:
        return (prev, True) if (prev and prev.startswith(m.group(1))) else (m.group(1) + "-01", True)
    m = PAREN_DATE.search(text)
    if m:
        return m.group(1), False
    if is_corr:
        m = DATE.search(text[:160])
        if m:
            return m.group(1), False
    return (prev or "2026-09-11"), True


def clean_title(h, body=()):
    t = re.sub(r"^20\d\d-\d\d(-\d\d)?(/\d\d)?\s*(\((late|evening|afternoon|night|later)\)\s*|(late|evening|night)\s+)?(\([^)]*addendum[^)]*\)\s*)?[:\u2014\u2013\-]+\s*", "", h).strip()
    t = t.strip(" :\u2014\u2013-")
    if len(t) < 4:
        t = next((x.strip() for x in body if x.strip()), h)
    return t[:150]


def split_part2(lines, start):
    """returns (intro_lines, entries); an entry starts at a heading of level 1-3 (outside code fences) or at a paragraph beginning 'CORRECTION TO'."""
    entries, intro, cur, fence, prev_date = [], [], None, False, None
    for k in range(start, len(lines)):
        ln = lines[k]
        if ln.lstrip().startswith("```"):
            fence = not fence
        m = HEAD.match(ln) if not fence else None
        corr = (not fence) and ln.startswith("CORRECTION TO ")
        if m or corr:
            text = m.group(2) if m else ln
            date, approx = entry_date(text, corr, prev_date)
            prev_date = date
            cur = {"order": len(entries), "src_line": k + 1, "heading": ln if m else None, "text": text, "date": date, "approx": approx, "label": label_of(text), "body": []}
            if not m:
                cur["body"].append(ln)
            entries.append(cur)
        elif cur is None:
            intro.append(ln)
        else:
            cur["body"].append(ln)
    seen, kept, dropped = {}, [], []
    for e in entries:
        bk = [x.rstrip() for x in e["body"]]
        while bk and not bk[-1]:
            bk.pop()
        key = (e["text"].rstrip(), tuple(bk))
        if sum(len(x) for x in e["body"]) > 200 and key in seen:
            seen[key]["dups"].append(e["src_line"]); dropped.append(e); continue
        e["dups"] = []; seen[key] = e; kept.append(e)
    for i, e in enumerate(kept):
        e["order"] = i
    return intro, kept, dropped


def assign_ids(entries):
    seq = collections.Counter(); out = sorted(entries, key=lambda e: (e["date"], e["order"]))
    for e in out:
        seq[e["date"]] += 1; e["id"] = "%s-%02d" % (e["date"], seq[e["date"]])
        e["title"] = clean_title(e["text"], e["body"]) if e["heading"] else e["text"].split(":")[0][:110]
    return out


def render_entry(e):
    meta = "<!-- entry: %s | date: %s | label: %s | source-line: %s | approx: %s -->" % (e["id"], e["date"], e["label"], "+".join(str(x) for x in [e["src_line"]] + e.get("dups", [])), "yes" if e["approx"] else "no")
    head = ["", meta, "### %s \u2014 %s" % (e["id"], e["title"].replace("\n", " "))]
    if e["heading"]:
        head.append("> Original heading: `%s`" % e["heading"].replace("`", "'"))
    return head + e["body"]


def render_index(entries):
    rows = ["| ID | date | old label | title |", "|---|---|---|---|"]
    for e in entries:
        rows.append("| %s | %s%s | %s | %s |" % (e["id"], e["date"], "~" if e["approx"] else "", e["label"], e["title"][:90].replace("|", "/")))
    return rows


HEADER = ["# CHANGELOG", "",
          "The dated history of the project: what was built, found, corrected and decided. **Newest entry first.** Each entry has a stable ID (date-sequence, e.g. 2026-10-26-12; a `~` after a date means the date was inherited from the entry before it in the old file). Entries are never rewritten: a correction is a NEW entry that cites the old ID.",
          "", "Not here: the script interfaces (docs/SCRIPTS_REFERENCE.md), how to run the pipelines (docs/OPERATIONS.md), the current state and the docket (docs/PROJECT_STATUS.md), registrations (results/). The old SCRIPTS.md is retired (docs/archive/SCRIPTS_monolith_2026-10-26.md holds the original).",
          "", "Add an entry:  python3 scripts/audit/changelog_tools.py add --title \"...\" [--label \"...\"] << 'EOF'  (body)  EOF",
          ""]


def build(entries, intro_note):
    ordered = list(reversed(entries))     # newest first
    out = list(HEADER) + (intro_note or []) + ["", "## Index", "", MARK_I0] + render_index(ordered) + [MARK_I1, "", "## Entries", "", MARK_E]
    for e in ordered:
        out += render_entry(e)
    return "\n".join(out) + "\n"


def parse_changelog(text):
    lines = text.split("\n"); ents, cur = [], None
    for ln in lines:
        m = META.match(ln)
        if m:
            cur = {"id": m.group(1), "date": m.group(2), "label": m.group(3), "src_line": m.group(4), "approx": m.group(5) == "yes", "raw": []}; ents.append(cur); continue
        if cur is not None:
            cur["raw"].append(ln)
    for e in ents:
        raw = e["raw"]
        t = next((x for x in raw if x.startswith("### ")), "### ?")
        e["title"] = t.split(" \u2014 ", 1)[-1]
    return ents


def body_of(e):
    raw = list(e["raw"])
    i = next((k for k, x in enumerate(raw) if x.startswith("### ")), None)
    if i is not None:
        raw = raw[i + 1:]
    if raw and raw[0].startswith("> Original heading: `"):
        raw = raw[1:]
    return raw


def cmd_split(apply, force):
    lines = open(SRC, encoding="utf-8").read().split("\n")
    p1 = next(i for i, l in enumerate(lines) if l.startswith("# PART 1"))
    p2 = next(i for i, l in enumerate(lines) if l.startswith("# PART 2"))
    intro, entries, dropped = split_part2(lines, p2 + 1)
    ordered = assign_ids(entries)
    text = build(ordered, [x for x in intro if x.strip()][:6] and ["> Note carried over from the old Part 2 heading: " + " ".join(x.strip() for x in intro if x.strip())[:400]])
    # verification: every non-blank original line of Part 2 survives
    back = parse_changelog(text); got = collections.Counter()
    for e in back:
        for x in body_of(e):
            if x.strip():
                got[x.rstrip()] += 1
        # the original heading line is quoted verbatim in the entry
    orig_heads = collections.Counter(e["heading"].rstrip() for e in entries if e["heading"])
    want = collections.Counter(l.rstrip() for l in lines[p2 + 1:] if l.strip())
    for h, c in orig_heads.items():
        want[h] -= c
    for l in intro:
        if l.strip():
            want[l.rstrip()] -= 1
    for d in dropped:
        for l in ([d["heading"]] if d["heading"] else []) + d["body"]:
            if l.strip():
                want[l.rstrip()] -= 1
    missing = sum(max(0, c - got[l]) for l, c in want.items())
    extra = sum(max(0, got[l] - want[l]) for l in got)
    ops_text = "\n".join(["> **Curated text, last edited 2026-09-29, moved here from the old SCRIPTS.md Part 1 on 2026-10-26.** The verified, generated interface of every script is docs/SCRIPTS_REFERENCE.md; changes after 2026-09-29 are in CHANGELOG.md. Where this text and the generated reference disagree, the reference wins.", ""] + lines[:p1] + lines[p1 + 1:p2]) + "\n"
    labels = collections.defaultdict(list)
    for e in ordered:
        if e["label"]:
            labels[e["label"]].append(e["id"])
    stub = ["# SCRIPTS.md \u2014 RETIRED 2026-10-26", "", "This file used to hold the script reference and the session changelog together. **Do not add anything here.** It is kept only so that old citations ('SCRIPTS.md addendum N') still resolve.", "",
            "| you want | it is now |", "|---|---|", "| the interface of a script | docs/SCRIPTS_REFERENCE.md (generated from the real files) |", "| how to run the pipelines in order, gotchas | docs/OPERATIONS.md |", "| the dated history, every old note | CHANGELOG.md |", "| the original file, untouched | docs/archive/SCRIPTS_monolith_2026-10-26.md |", "| a new note | python3 scripts/audit/changelog_tools.py add --title ... |", "", "## Old label to new entry", "", "| old label | CHANGELOG entry |", "|---|---|"]
    def keyf(k):
        m = re.match(r"(addendum|note|correction)\s*(\d*)", k); return (m.group(1) if m else k, int(m.group(2)) if m and m.group(2) else 0, k)
    for k in sorted(labels, key=keyf):
        stub.append("| %s | %s |" % (k, ", ".join(labels[k])))
    stub = "\n".join(stub) + "\n"
    dated = collections.Counter(e["date"] for e in ordered)
    print("source lines %d | Part 1: lines %d-%d (%d) | Part 2: lines %d-%d" % (len(lines), p1 + 1, p2, p2 - p1, p2 + 1, len(lines)))
    print("entries: %d (%d with an exact date, %d approximate); distinct dates %d; labelled entries %d" % (len(ordered), sum(not e["approx"] for e in ordered), sum(e["approx"] for e in ordered), len(dated), sum(1 for e in ordered if e["label"])))
    print("VERIFY: original non-blank Part 2 lines missing from the changelog: %d | lines in the changelog that are not original: %d" % (missing, extra))
    dups = [k for k, v in labels.items() if len(v) > 1]
    print("exact duplicate entries collapsed: %d (source lines %s)" % (len(dropped), ", ".join(str(d["src_line"]) for d in dropped) or "-"))
    print("old labels used by more than one entry:", dups or "none")
    print("changelog %d lines; operations %d lines; stub %d lines" % (text.count("\n"), ops_text.count("\n"), stub.count("\n")))
    if missing or extra:
        raise SystemExit("VERIFICATION FAILED: nothing written")
    if not apply:
        print("DRY RUN: nothing written. Re-run with --apply to write the files."); return ordered, text
    for p in (ARCHIVE, CHANGELOG, OPS):
        if os.path.exists(p) and not force:
            raise SystemExit("refusing to overwrite %s (use --force)" % p)
    os.makedirs(os.path.dirname(ARCHIVE), exist_ok=True); os.makedirs(os.path.dirname(OPS), exist_ok=True)
    shutil.copyfile(SRC, ARCHIVE)
    open(CHANGELOG, "w", encoding="utf-8").write(text); open(OPS, "w", encoding="utf-8").write(ops_text); open(SRC, "w", encoding="utf-8").write(stub)
    print("WRITTEN: %s (original copy), %s, %s, and %s is now the retirement stub." % (ARCHIVE, CHANGELOG, OPS, SRC))
    return ordered, text


def cmd_add(title, label, date):
    text = open(CHANGELOG, encoding="utf-8").read(); ents = parse_changelog(text)
    body = sys.stdin.read().rstrip("\n").split("\n")
    date = date or datetime.date.today().isoformat()
    n = 1 + max([int(e["id"].rsplit("-", 1)[1]) for e in ents if e["date"] == date] or [0])
    new = {"id": "%s-%02d" % (date, n), "date": date, "label": label or "", "src_line": "new", "approx": False, "title": title, "heading": None, "body": body}
    head, rest = text.split(MARK_E, 1)
    block = "\n".join(render_entry(new))
    all_ents = [new] + ents
    i0, i1 = head.index(MARK_I0), head.index(MARK_I1)
    head = head[:i0] + MARK_I0 + "\n" + "\n".join(render_index(all_ents)) + "\n" + head[i1:]
    open(CHANGELOG, "w", encoding="utf-8").write(head + MARK_E + "\n" + block + rest)
    print("added %s" % new["id"])


def cmd_check():
    ents = parse_changelog(open(CHANGELOG, encoding="utf-8").read()); ids = [e["id"] for e in ents]
    probs = []
    if len(set(ids)) != len(ids): probs.append("duplicate IDs")
    ds = [e["date"] for e in ents]
    if ds != sorted(ds, reverse=True): probs.append("entries are not newest first")
    idx = open(CHANGELOG, encoding="utf-8").read().split(MARK_I0)[1].split(MARK_I1)[0]
    if any(("| %s |" % i) not in idx for i in ids): probs.append("index is missing an entry")
    print("entries %d, newest %s, oldest %s" % (len(ents), ds[0] if ds else "-", ds[-1] if ds else "-")); print("CHECK FAILED: " + "; ".join(probs) if probs else "CHECK OK")
    return 1 if probs else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("split"); s.add_argument("--apply", action="store_true"); s.add_argument("--force", action="store_true")
    a = sub.add_parser("add"); a.add_argument("--title", required=True); a.add_argument("--label", default=""); a.add_argument("--date", default="")
    sub.add_parser("check")
    r = ap.parse_args()
    if r.cmd == "split": cmd_split(r.apply, r.force)
    elif r.cmd == "add": cmd_add(r.title, r.label, r.date)
    else: sys.exit(cmd_check())