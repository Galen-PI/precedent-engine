#!/usr/bin/env bash
# wait_job.sh NAME [timeout_seconds]   waits until the background job NAME (started with bg.sh) has ended, prints how it ended, and exits 0 ONLY if the job exited 0
# so a dependent command can be chained safely:   scripts/ops/wait_job.sh NAME && next-command
# A short grace period (WAIT_JOB_GRACE seconds, default 10) lets a job that was JUST started create its status file.
# exit codes: 0 finished OK | 1 finished with a non-zero exit | 2 no such job | 4 the job died without recording an end | 5 gave up waiting
name="$1"; limit="${2:-1800}"; st="data_cache/jobs/${name}.status"; waited=0; grace="${WAIT_JOB_GRACE:-10}"
if [ -z "$name" ]; then echo "usage: scripts/ops/wait_job.sh NAME [timeout_seconds]"; exit 2; fi
g=0
while [ ! -f "$st" ] || ! grep -q '^pid=' "$st"; do
  if [ "$g" -ge "$grace" ]; then echo "no job named '$name' (no $st after ${grace}s)"; exit 2; fi
  sleep 1; g=$((g + 1))
done
while ! grep -q '^ended=' "$st"; do
  pid=$(grep '^pid=' "$st" | head -1 | cut -d= -f2)
  alive=0
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    state=$(sed 's/.*) //' "/proc/$pid/stat" 2>/dev/null | cut -c1)
    [ "$state" != "Z" ] && alive=1
  fi
  if [ "$alive" = "0" ]; then echo "job '$name' is not running and never recorded an end (stopped or killed): NOT continuing"; exit 4; fi
  if [ "$waited" -ge "$limit" ]; then echo "gave up waiting for '$name' after ${limit}s (it is still running): NOT continuing"; exit 5; fi
  sleep 3; waited=$((waited + 3))
done
code=$(grep '^exit=' "$st" | head -1 | cut -d= -f2)
echo "job '$name' finished with exit $code"
if [ "$code" = "0" ]; then exit 0; else echo "NOT continuing"; exit 1; fi
