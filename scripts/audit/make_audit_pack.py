#!/usr/bin/env python3
"""
make_audit_pack.py -- bundles the TEXT files of results/, docs/ and the root documents into audit_pack.zip, with a MANIFEST.txt (path | bytes | last commit date | first line) for the master audit. READ-ONLY on the repository; writes only audit_pack.zip in the current directory (do NOT commit it; delete it afterwards). Skips binary and large files and says what it skipped.
Run from the repository root:   python3 scripts/audit/make_audit_pack.py
"""
import os, sys, subprocess, zipfile, collections

ROOT_DIRS = ["results", "docs"]
ROOT_FILES = ["PROJECT_PLAN.md", "README.md", "THEORY.md", "SCRIPTS.md", "PROJECT_HANDOFF.md"]
LIMIT = {".md": 4_000_000, ".txt": 500_000, ".sql": 500_000, ".json": 250_000, ".csv": 250_000, ".tsv": 250_000}


def last_commit(path):
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%ad", "--date=short", "--", path], capture_output=True, text=True, timeout=20).stdout.strip()
        return out or "untracked"
    except Exception:
        return "unknown"


def first_line(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                s = line.strip()
                if s:
                    return s.lstrip("# ").replace("|", "/")[:110]
    except Exception:
        pass
    return ""


def main():
    files = [f for f in ROOT_FILES if os.path.isfile(f)]
    for d in ROOT_DIRS:
        for dp, dn, fn in os.walk(d):
            dn[:] = [x for x in dn if not x.startswith(".")]
            files += [os.path.join(dp, f) for f in fn if not f.startswith(".")]
    keep, skipped = [], []
    for p in sorted(files):
        ext = os.path.splitext(p)[1].lower(); size = os.path.getsize(p)
        if ext not in LIMIT:
            skipped.append((p, size, "type " + (ext or "none")))
        elif size > LIMIT[ext]:
            skipped.append((p, size, "too large"))
        else:
            keep.append((p, size))
    lines = ["path | bytes | last commit | first line"]
    for p, s in keep:
        lines.append("%s | %d | %s | %s" % (p, s, last_commit(p), first_line(p)))
    lines.append("")
    lines.append("SKIPPED (%d files):" % len(skipped))
    for p, s, why in skipped:
        lines.append("%s | %d | %s" % (p, s, why))
    with zipfile.ZipFile("audit_pack.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for p, s in keep:
            z.write(p, p)
        z.writestr("MANIFEST.txt", "\n".join(lines) + "\n")
    by_ext = collections.Counter(os.path.splitext(p)[1].lower() for p, s in keep)
    print("audit_pack.zip written: %d files, %.1f MB uncompressed, %.1f MB zipped" % (len(keep), sum(s for p, s in keep) / 1e6, os.path.getsize("audit_pack.zip") / 1e6))
    print("kept by type:", dict(by_ext))
    print("skipped: %d files (largest: %s)" % (len(skipped), ", ".join("%s %.1fMB (%s)" % (p, s / 1e6, why) for p, s, why in sorted(skipped, key=lambda t: -t[1])[:6])))
    print("by folder:", dict(collections.Counter(os.path.dirname(p) or "(root)" for p, s in keep)))


if __name__ == "__main__":
    main()
