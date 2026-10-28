#!/usr/bin/env python3
"""
patch_jobs_ack.py -- one-off patch of scripts/ops/jobs.py (written 2026-10-28). ALL-OR-NOTHING: it writes only if the file is exactly the version it was tested against (sha256 below) and every anchor is found exactly once.
WHY: on 2026-10-28 the monitor said 'ALL CLEAR' about a job (tagger2) that had been killed 40 hours earlier when the Codespace idled out. Failures older than 24 hours were hidden, and the age is measured from when the JOB stopped, not from when you last looked, so a job that dies while you are away ages out before you return. The same job read 'FAILED (traceback)' although it was killed: its log legitimately holds the tracebacks of crashes its restart wrapper had already handled.
CHANGES: (1) a failed or stopped job that has a status record stays under ATTENTION until you acknowledge it: python3 scripts/ops/jobs.py --ack NAME (moves its status record to data_cache/jobs/acked/, keeps the log, refuses a running job); (2) a job that failed with an exit code is no longer dropped after 72 hours; (3) a bg.sh job that died WITHOUT an end record reads STOPPED, not 'FAILED (traceback)' (bg.sh jobs that failed by themselves always have an end record). Jobs found without a status record (the KNOWN scripts) keep the 24-hour rule.
Usage (repository root):   python3 scripts/audit/patch_jobs_ack.py
"""
import sys, hashlib
EXPECTED = "cca4279a469fa2397ae1560fe1ad2e874812d605fdd078ab65d7bc2032ebcb1d"
p = sys.argv[1] if len(sys.argv) > 1 else "scripts/ops/jobs.py"
s = open(p).read()
if '"--ack"' in s:
    sys.exit("already applied: nothing written")
found = hashlib.sha256((s if s.endswith("\n") else s + "\n").encode()).hexdigest()
if found != EXPECTED:
    sys.exit("STOP: %s is not the version this patch was tested against (expected sha256 %s, found %s). Nothing written. Paste the file." % (p, EXPECTED, found))


def rep(old, new):
    global s
    if s.count(old) != 1:
        sys.exit("STOP: anchor not found exactly once, nothing written: " + old[:90])
    s = s.replace(old, new)


rep("READ-ONLY: it never starts, stops or changes anything.", "READ-ONLY, with one exception: python3 scripts/ops/jobs.py --ack NAME moves the status record of a failed or stopped job to data_cache/jobs/acked/ (the log stays) so it stops raising ATTENTION.")
rep('"detail": "", "age": None}', '"detail": "", "age": None, "from_status": bool(status)}')
rep('    elif tb:\n', '    elif tb and not status:   # a bg.sh job without an end record was KILLED (its log may hold tracebacks the wrapper already handled): it falls through to STOPPED\n')
rep("ATTENTION = a stalled job, or a failed / stopped job from the last 24 hours. Finished jobs older than 6 hours and failed / stopped ones older than 24 hours are hidden unless show_all.", "ATTENTION = a stalled job, or a failed / stopped job that has a status record (until acknowledged with --ack NAME), or one found without a status record from the last 24 hours. Finished jobs older than 6 hours are hidden unless show_all.")
rep('(r["state"].startswith("FAILED") or r["state"] in ("STOPPED", "NO LOG")) and age(r) <= 24 * hour)', '(r["state"].startswith("FAILED") or r["state"] in ("STOPPED", "NO LOG")) and (r.get("from_status") or age(r) <= 24 * hour))')
rep('RECENT_HOURS * 3600 and st.get("ended"):', 'RECENT_HOURS * 3600 and st.get("ended") and st.get("exit") == "0":')
rep('    ap.add_argument("--all", action="store_true", help="also show finished jobs older than 6 hours and old failures")\n',
    '    ap.add_argument("--all", action="store_true", help="also show finished jobs older than 6 hours and old failures")\n    ap.add_argument("--ack", metavar="NAME", help="acknowledge a failed or stopped job: moves its status record to data_cache/jobs/acked/ so it stops raising ATTENTION (the log stays)")\n')
rep('    a = ap.parse_args(argv)\n    rows, claimed = [], set()\n', '''    a = ap.parse_args(argv)
    if a.ack:
        src = os.path.join(CACHE, "jobs", a.ack + ".status")
        names = sorted(os.path.basename(x)[:-len(".status")] for x in glob.glob(os.path.join(CACHE, "jobs", "*.status")))
        if not os.path.exists(src):
            print("no status record named %r; names: %s" % (a.ack, ", ".join(names) or "(none)"))
            return []
        st = read_status(src)
        if not st.get("ended") and pid_alive(st.get("pid", 0)):
            print("refusing: %s is still running (pid %s)" % (a.ack, st.get("pid")))
            return []
        dest_dir = os.path.join(CACHE, "jobs", "acked")
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, "%s.%s.status" % (a.ack, datetime.datetime.now().strftime("%Y%m%d-%H%M%S")))
        os.rename(src, dest)
        print("acknowledged %s: its status record moved to %s (the log stays); it no longer raises ATTENTION" % (a.ack, os.path.relpath(dest, ROOT)))
        return []
    rows, claimed = [], set()
''')
compile(s, p, "exec")
open(p, "w").write(s)
print("patched %s: killed or failed jobs stay under ATTENTION until acknowledged (--ack NAME); killed bg.sh jobs read STOPPED" % p)