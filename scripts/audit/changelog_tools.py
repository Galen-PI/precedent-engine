#!/usr/bin/env python3
"""
changelog_tools.py -- retires the SCRIPTS.md monolith and runs the changelog (written 2026-10-26). Run from the repository root.
  split [--apply]            reads SCRIPTS.md and builds CHANGELOG.md (every dated entry, NEWEST FIRST, a stable ID per entry, an index), docs/OPERATIONS.md (the old Part 1 reference text, verbatim, with a banner) and a retirement stub; DRY RUN unless --apply. It VERIFIES that every non-blank line of the original survives. With --apply it copies the original to docs/archive/SCRIPTS_monolith_2026-10-26.md first (refuses to overwrite anything that exists unless --force).
  add --title T [--label L] [--date YYYY-MM-DD]     adds an entry at the TOP of CHANGELOG.md from standard input (body), assigns the next ID of that date, rebuilds the index.
  check                      verifies CHANGELOG.md (IDs unique, newest first, index matches the entries).
  checkpoint --reason R      (body from standard input) adds a CHECKPOINT entry to CHANGELOG.md with the date AND TIME, and replaces the 'latest checkpoint' block of docs/START_NEW_DAY.md (created if missing): what was done, what is in flight, the exact next step. Written at every milestone, whenever the conversation may need compaction, and at the end of the day.
  retitle                    recomputes the index titles of entries that have an 'Original heading' line (cosmetic; bodies are never touched).
ID = date-sequence (2026-10-26-12): the sequence counts the entries of that date, oldest first. An entry without an exact date in its heading inherits the date of the entry before it in the source file and is marked 'date approximate'.
"""
import re, sys, os, argparse, datetime, shutil, collections, subprocess

SRC, CHANGELOG, OPS = "SCRIPTS.md", "CHANGELOG.md", "docs/OPERATIONS.md"
ARCHIVE = "docs/archive/SCRIPTS_monolith_2026-10-26.md"
START_NEW_DAY = "docs/START_NEW_DAY.md"
CP0, CP1 = "<!-- CHECKPOINT-START -->", "<!-- CHECKPOINT-END -->"
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
    t = h.strip()
    t = re.sub(r"^20\d\d-\d\d(-\d\d)?(/\d\d)?", "", t).strip()
    t = re.sub(r"^\((?:late|evening|afternoon|night|later)[^)]*\)\s*", "", t)
    t = re.sub(r"^(?:evening|night|late)\s+", "", t)
    m = re.match(r"^\(addendum \d+(?: to note \d+)?(?:,\s*([^)]*))?\)\s*[:\u2014\u2013-]*\s*", t)
    if m:
        t = ((m.group(1) + ": ") if m.group(1) else "") + t[m.end():]
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


def add_entry(title, label, date, body):
    text = open(CHANGELOG, encoding="utf-8").read(); ents = parse_changelog(text)
    n = 1 + max([int(e["id"].rsplit("-", 1)[1]) for e in ents if e["date"] == date] or [0])
    new = {"id": "%s-%02d" % (date, n), "date": date, "label": label or "", "src_line": "new", "approx": False, "title": title, "heading": None, "body": body}
    head, rest = text.split(MARK_E, 1)
    block = "\n".join(render_entry(new))
    all_ents = [new] + ents
    i0, i1 = head.index(MARK_I0), head.index(MARK_I1)
    head = head[:i0] + MARK_I0 + "\n" + "\n".join(render_index(all_ents)) + "\n" + head[i1:]
    open(CHANGELOG, "w", encoding="utf-8").write(head + MARK_E + "\n" + block + rest)
    return new["id"]


def cmd_add(title, label, date):
    body = sys.stdin.read().rstrip("\n").split("\n")
    print("added %s" % add_entry(title, label, date or datetime.date.today().isoformat(), body))


SND_HEADER = """# START NEW DAY

**The first file to read in a new session, or after a compaction.** Then docs/PROJECT_STATUS.md (current state), docs/NAMING.md, CHANGELOG.md (index first), docs/OPERATIONS.md, docs/SCRIPTS_REFERENCE.md (generated).

## How to resume (for the assistant)
1. START OF EVERY SESSION: say (a) the time now (run date -u) and the age of the LATEST CHECKPOINT below; (b) if /mnt/transcripts is mounted, how many earlier transcript segments exist and when the last compaction was (the transcripts carry an exact ISO timestamp per message; journal.txt catalogues them); (c) a fullness ESTIMATE of this conversation, labelled as an estimate: you have no gauge, but earlier segments were compacted at a median of 1.75 MB (middle half 1.65 to 1.94 MB, 31 segments), so estimate from how much text has been exchanged and the time since the last compaction; then five lines of what you understood and the next step; wait for the user to confirm before doing anything.
1b. BEFORE WRITING ANY CHECKPOINT: review the whole visible conversation since the last checkpoint; the tool appends the git log and git status itself; after a compaction, read the tail of the newest transcript and journal.txt and grep /mnt/transcripts for details instead of trusting the summary alone.
2. Do not trust any number in any document as current: re-check it against the live database. SQL for the user uses dollar-quoting ($$text$$); every long SQL goes through scripts/ops/lint_sql.py first; a multi-statement SQL run is one transaction.
3. If you are not sure how a script works, ask the user to paste the real file. Never guess an interface.
4. Never bulk-confirm or bulk-correct before reading the cases: state the rule first, keep a backup table, read a stratified sample, apply guarded.
5. Every numeric prediction is a point, a range and an anchor label (DATA, LITERATURE or NONE); score it afterwards.
6. Every step is its own block labelled FOREGROUND (this terminal), BACKGROUND (second terminal) or SQL editor. Files arrive with a tolerant hash gate: check() { [ "$(sed -e '$a\\' "$2" | sha256sum | cut -d' ' -f1)" = "$1" ] && echo "OK     $2" || { echo "FAILED $2"; return 1; }; }
7. The eight forward-test files are FROZEN until both verdicts are recorded (scripts/hooks/pre-commit enforces it). Sealed companies (table explore_sealed_tickers) stay out of every exploratory look.
8. Be honest about sample size and uncertainty, including about your own findings; when something does not add up, say so and dig.

## Checkpoints
A checkpoint is written at every milestone, whenever the conversation may need compaction, when the user says "checkpoint", and at the end of the day:
    python3 scripts/audit/changelog_tools.py checkpoint --reason "..." << 'EOF'  (body)  EOF
It adds a CHANGELOG entry (the history) AND replaces the block below (the latest state).

""" + CP0 + """
(no checkpoint yet)
""" + CP1 + "\n"


def git_lines(args, limit):
    try:
        out = subprocess.run(["git"] + args, capture_output=True, text=True, timeout=30).stdout.strip().split("\n")
    except Exception:
        return ["(git not available)"]
    out = [x for x in out if x.strip()]
    return out[:limit] + (["... and %d more" % (len(out) - limit)] if len(out) > limit else [])


def cmd_checkpoint(reason):
    now = datetime.datetime.now().astimezone()
    stamp = now.strftime("%Y-%m-%d %H:%M %z"); utc = now.astimezone(datetime.timezone.utc).strftime("%H:%M UTC")
    body = sys.stdin.read().rstrip("\n").split("\n")
    prev = None
    if os.path.exists(START_NEW_DAY):
        m = re.search(r"### Latest checkpoint: (\d{4}-\d\d-\d\d \d\d:\d\d [+-]\d{4})", open(START_NEW_DAY, encoding="utf-8").read())
        prev = m.group(1) if m else None
    commits = git_lines(["log", "--since=" + (prev or "24 hours ago"), "--date=format:%Y-%m-%d %H:%M", "--pretty=format:%h %ad %s"], 60)
    status = git_lines(["status", "--short"], 20)
    body = body + ["", "COMMITS SINCE THE PREVIOUS CHECKPOINT (%s), from git log, objective:" % (("since " + prev) if prev else "last 24 hours; no earlier checkpoint")] + ["  " + x[:150] for x in (commits or ["(none)"])] + ["", "UNCOMMITTED (git status --short):"] + ["  " + x for x in (status or ["(clean)"])]
    eid = add_entry("CHECKPOINT %s (%s)" % (now.strftime("%Y-%m-%d %H:%M"), reason), "checkpoint", now.date().isoformat(), ["Written %s (%s). Reason: %s." % (stamp, utc, reason), ""] + body)
    txt = open(START_NEW_DAY, encoding="utf-8").read() if os.path.exists(START_NEW_DAY) else SND_HEADER
    if CP0 not in txt or CP1 not in txt:
        txt = txt.rstrip("\n") + "\n\n" + CP0 + "\n(no checkpoint yet)\n" + CP1 + "\n"
    a, b = txt.index(CP0), txt.index(CP1)
    block = ["### Latest checkpoint: %s (%s) | CHANGELOG %s | reason: %s" % (stamp, utc, eid, reason), ""] + body
    txt = txt[:a] + CP0 + "\n" + "\n".join(block) + "\n" + txt[b:]
    os.makedirs(os.path.dirname(START_NEW_DAY), exist_ok=True)
    open(START_NEW_DAY, "w", encoding="utf-8").write(txt)
    print("checkpoint %s written to %s and %s" % (eid, CHANGELOG, START_NEW_DAY))


def cmd_retitle():
    text = open(CHANGELOG, encoding="utf-8").read(); lines = text.split("\n"); changed = []
    for i, ln in enumerate(lines):
        if ln.startswith("### ") and i > 0 and META.match(lines[i - 1]) and i + 1 < len(lines) and lines[i + 1].startswith("> Original heading: `"):
            eid = META.match(lines[i - 1]).group(1)
            orig = lines[i + 1][len("> Original heading: `"):-1]; hm = HEAD.match(orig)
            if not hm:
                continue
            j, body = i + 2, []
            while j < len(lines) and not META.match(lines[j]):
                body.append(lines[j]); j += 1
            new = clean_title(hm.group(2), body); cur = ln.split(" \u2014 ", 1)[1] if " \u2014 " in ln else ""
            if new != cur:
                lines[i] = "### %s \u2014 %s" % (eid, new); changed.append((eid, cur, new))
    text2 = "\n".join(lines); ents = parse_changelog(text2)
    head, rest = text2.split(MARK_E, 1); i0, i1 = head.index(MARK_I0), head.index(MARK_I1)
    head = head[:i0] + MARK_I0 + "\n" + "\n".join(render_index(ents)) + "\n" + head[i1:]
    open(CHANGELOG, "w", encoding="utf-8").write(head + MARK_E + rest)
    for eid, cur, new in changed:
        print("%s: %s  ->  %s" % (eid, cur[:60], new[:70]))
    print("retitled %d of %d entries" % (len(changed), len(ents)))


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
    c = sub.add_parser("checkpoint"); c.add_argument("--reason", required=True)
    sub.add_parser("retitle")
    r = ap.parse_args()
    if r.cmd == "split": cmd_split(r.apply, r.force)
    elif r.cmd == "add": cmd_add(r.title, r.label, r.date)
    elif r.cmd == "checkpoint": cmd_checkpoint(r.reason)
    elif r.cmd == "retitle": cmd_retitle()
    else: sys.exit(cmd_check())