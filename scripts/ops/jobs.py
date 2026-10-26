#!/usr/bin/env python3
"""
jobs.py -- one screen that shows how every background job is doing: RUNNING (with a progress bar and an ETA), FINISHED OK, FAILED, STOPPED (it died without a finish line: the session stopped or it was killed) or STALLED (alive but the log has not moved).
It finds jobs two ways: (1) jobs started with scripts/ops/bg.sh, which record how they ended; (2) the known scripts below, found by process name and log file, so jobs started the old way are visible too.
Usage:   python3 scripts/ops/jobs.py          once        |        watch -c -n 20 python3 scripts/ops/jobs.py          refreshes every 20 seconds
READ-ONLY: it never starts, stops or changes anything.
"""
import os, re, sys, glob, time, subprocess, datetime

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
CACHE = os.path.join(ROOT, "data_cache")
RECENT_HOURS = 72
KNOWN = [
    {"name": "prices (as-quoted)", "pattern": "fetch_asquoted_factors", "logs": ["asquoted_run.log"], "finish": r"^requests used \d+ \|", "header": r"(\d+) tickers selected, \d+ already done, (\d+) to fetch", "total_group": 2, "item": r"^  \S+\s+(ok|flagged|ERROR)", "stall_min": 10},
    {"name": "CRS subjects", "pattern": "fetch_crs_subjects", "logs": ["crs_subjects_run.log"], "finish": r"^ok \d+ \| none \d+ \| error \d+", "header": r"relevant laws \d+ \| already done \d+ \| to fetch (\d+)", "total_group": 1, "item": r"^  (ok|none|error)\s+\d+ terms", "stall_min": 5},
    {"name": "decision text", "pattern": "fetch_decision_text", "logs": ["decision_text_run.log"], "finish": r"^ok \d+ \| no_text \d+ \| error \d+", "header": r"relevant decisions \d+ \| already done \d+ \| to fetch (\d+)", "total_group": 1, "item": r"^  (enacted_law|executive_order)\s", "stall_min": 5},
    {"name": "government tagger", "pattern": "tag_government_decisions", "logs": ["tag_*.log"], "finish": r"^(wrote \d+ tag rows|nothing written|REFUSING|DRY RUN: nothing submitted)", "header": r"to tag (\d+) \|", "total_group": 1, "item": None, "stall_min": 15},
]
G, Y, R, D, X = "\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[0m"


def tail_text(path, nbytes=3000000):
    with open(path, "rb") as fh:
        fh.seek(0, os.SEEK_END)
        size = fh.tell()
        fh.seek(max(0, size - nbytes))
        return fh.read().decode("utf-8", "replace")


def pids_matching(pattern):
    # only real python invocations of the script FILE count: a shell, an editor or a grep that merely mentions the name must not look like a running job
    r = subprocess.run(["pgrep", "-f", r"python3?\b.*%s\.py" % re.escape(pattern)], capture_output=True, text=True)
    return [int(x) for x in r.stdout.split() if x.isdigit() and int(x) != os.getpid()]


def pid_alive(pid):
    try:
        os.kill(int(pid), 0)
    except (OSError, ValueError):
        return False
    try:
        with open("/proc/%d/stat" % int(pid)) as fh:
            return fh.read().rsplit(")", 1)[1].split()[0] != "Z"   # a zombie (dead, not yet cleaned up) is not alive
    except (OSError, IndexError):
        return True


def elapsed_seconds(pid):
    r = subprocess.run(["ps", "-o", "etimes=", "-p", str(pid)], capture_output=True, text=True)
    return int(r.stdout.strip()) if r.stdout.strip().isdigit() else None


def newest(patterns):
    files = [f for p in patterns for f in glob.glob(os.path.join(CACHE, p))]
    return max(files, key=os.path.getmtime) if files else None


def fmt_dur(sec):
    if sec is None:
        return "?"
    sec = int(sec)
    return "%dh%02dm" % (sec // 3600, sec % 3600 // 60) if sec >= 3600 else "%dm%02ds" % (sec // 60, sec % 60) if sec >= 60 else "%ds" % sec


def bar(done, total, width=20):
    frac = 0 if not total else min(1.0, done / float(total))
    n = int(round(frac * width))
    return "[" + "\u2588" * n + "\u2591" * (width - n) + "] %3d%%" % int(frac * 100)


def analyze(job, status=None):
    """job: a KNOWN entry; status: parsed bg.sh status file or None. Returns a dict for display."""
    log = os.path.join(CACHE, "%s.log" % status["name"]) if status else newest(job["logs"])
    out = {"name": status["name"] if status else job["name"], "state": None, "colour": Y, "line": "", "bar": "", "detail": "", "age": None}
    if not log or not os.path.exists(log):
        out.update(state="NO LOG", detail="no log file found")
        return out
    text = tail_text(log)
    age = time.time() - os.path.getmtime(log)
    pids = [int(status["pid"])] if status and pid_alive(status.get("pid", 0)) else ([] if status else pids_matching(job["pattern"]))
    alive = bool(pids)
    hdr = [m for m in re.finditer(job["header"], text, re.M)] if job.get("header") else []
    pos = hdr[-1].start() if hdr else 0
    run = text[pos:]
    total = int(hdr[-1].group(job["total_group"])) if hdr else 0
    done = len(re.findall(job["item"], run, re.M)) if job.get("item") and hdr else 0
    fin = re.search(job["finish"], run, re.M)
    tb = "Traceback (most recent call last)" in run
    lines = [l for l in run.splitlines() if l.strip()]
    out["line"] = (lines[-1] if lines else "")[:110]
    out["age"] = age
    if hdr and job.get("item"):
        out["bar"] = "%s %d/%d" % (bar(done, total), done, total)
    if status and status.get("ended"):
        code = status.get("exit", "?")
        out.update(state="FINISHED OK" if code == "0" else "FAILED (exit %s)" % code, colour=G if code == "0" else R)
    elif alive:
        stalled = age > job.get("stall_min", 10) * 60
        out.update(state="STALLED" if stalled else "RUNNING", colour=Y if stalled else G)
        el = elapsed_seconds(pids[0])
        eta = ("  eta ~%s" % fmt_dur(el / float(done) * (total - done))) if (el and done and total and done < total) else ""
        out["detail"] = "elapsed %s%s  last log activity %s ago%s" % (fmt_dur(el), eta, fmt_dur(age), "  <- no new log lines: check it" if stalled else "")
    elif fin and not status:   # for jobs started by bg.sh the launcher's record is the only authority: a killed job has no 'ended' line and must read STOPPED
        note = " (budget reached: run again after the daily reset)" if re.search(r"budget reached", run) else ""
        out.update(state="FINISHED OK", colour=G, detail="finished %s ago%s" % (fmt_dur(age), note))
        out["line"] = fin.group(0)[:110]
    elif tb:
        out.update(state="FAILED (traceback in the log)", colour=R, detail="stopped %s ago" % fmt_dur(age))
    else:
        out.update(state="STOPPED", colour=Y, detail="not running and no finish line: the session stopped or it was killed %s ago; rerun the same command (the job resumes)" % fmt_dur(age))
    return out


def read_status(path):
    kv = {}
    for l in open(path).read().splitlines():
        if "=" in l:
            k, v = l.split("=", 1)
            kv[k] = v
    kv["name"] = os.path.basename(path)[:-len(".status")]
    return kv


def main():
    rows, claimed = [], set()
    for sp in sorted(glob.glob(os.path.join(CACHE, "jobs", "*.status"))):
        st = read_status(sp)
        job = next((j for j in KNOWN if j["pattern"] in st.get("cmd", "")), {"name": st["name"], "pattern": st["name"], "finish": r"(?!)", "header": None, "stall_min": 10})
        if time.time() - os.path.getmtime(sp) > RECENT_HOURS * 3600 and st.get("ended"):
            continue
        rows.append(analyze(job, st))
        claimed.add(job["pattern"])
    for job in KNOWN:
        if job["pattern"] in claimed:
            continue
        log = newest(job["logs"])
        if pids_matching(job["pattern"]) or (log and time.time() - os.path.getmtime(log) < RECENT_HOURS * 3600):
            rows.append(analyze(job))
    print("JOBS (as of %s)" % datetime.datetime.now().strftime("%a %H:%M:%S"))
    if not rows:
        print("  no background jobs found")
    for r in rows:
        print("  %s%-20s %-30s%s %s" % (r["colour"], r["name"], r["state"], X, r["bar"]))
        if r["detail"]:
            print("      %s%s%s" % (D, r["detail"], X))
        print("      %slast: %s%s" % (D, r["line"], X))
    return rows


if __name__ == "__main__":
    main()
