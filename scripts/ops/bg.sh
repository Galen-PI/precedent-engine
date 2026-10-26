#!/usr/bin/env bash
# bg.sh NAME command args...   starts a command in the background, logs to data_cache/NAME.log, and records how it ENDS in data_cache/jobs/NAME.status
# (pid, start, end time and exit code), so scripts/ops/jobs.py can tell FINISHED from FAILED from STOPPED (the session died or the job was killed).
# GUARDS (added 2026-10-26): a second start under the SAME name is REFUSED while the first is still running (the double-launch class of incident); a finished or dead run's log is kept as NAME.log.prev so each run has its own log.
if [ "$#" -lt 2 ]; then echo "usage: scripts/ops/bg.sh NAME command [args...]"; exit 2; fi
name="$1"; shift
mkdir -p data_cache/jobs
log="data_cache/${name}.log"; st="data_cache/jobs/${name}.status"
if [ -f "$st" ]; then
  oldpid=$(grep '^pid=' "$st" | head -1 | cut -d= -f2)
  if [ -n "$oldpid" ] && ! grep -q '^ended=' "$st" && kill -0 "$oldpid" 2>/dev/null; then
    state=$(sed 's/.*) //' "/proc/$oldpid/stat" 2>/dev/null | cut -c1)
    if [ "$state" != "Z" ]; then
      echo "REFUSED: a job named '$name' is still running (pid $oldpid). Wait for it, or use another name."; exit 3
    fi
  fi
  [ -f "$log" ] && mv "$log" "${log}.prev"
fi
nohup bash -c '
  st="$1"; shift
  { echo "pid=$$"; echo "started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "cmd=$*"; } > "$st"
  "$@"; code=$?
  { echo "ended=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "exit=$code"; } >> "$st"
' _ "$st" "$@" >> "$log" 2>&1 &
echo "started $name (pid $!); log: $log; check with: python3 scripts/ops/jobs.py"
