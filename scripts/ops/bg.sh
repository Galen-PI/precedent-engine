#!/usr/bin/env bash
# bg.sh NAME command args...   starts a command in the background, logs to data_cache/NAME.log, and records how it ENDS in data_cache/jobs/NAME.status
# (pid, start, end time and exit code), so scripts/ops/jobs.py can tell FINISHED from FAILED from STOPPED (the session died or the job was killed).
if [ "$#" -lt 2 ]; then echo "usage: scripts/ops/bg.sh NAME command [args...]"; exit 2; fi
name="$1"; shift
mkdir -p data_cache/jobs
log="data_cache/${name}.log"; st="data_cache/jobs/${name}.status"
nohup bash -c '
  st="$1"; shift
  { echo "pid=$$"; echo "started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "cmd=$*"; } > "$st"
  "$@"; code=$?
  { echo "ended=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "exit=$code"; } >> "$st"
' _ "$st" "$@" >> "$log" 2>&1 &
echo "started $name (pid $!); log: $log; check with: python3 scripts/ops/jobs.py"
