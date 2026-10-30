"""g7_patch_arm1_direction_v1.py (2026-10-30): the ARM 1 filter for the direction_test.py re-run (G7, Addendum 9; flag event_label_direction_sign).
Edits ONLY the copy of scripts/card/direction_test.py inside a pinned git worktree under /tmp (never the repository checkout): right after
load_events reads event_direction_labels, labels whose event_id has an `exclude` row in event_exclusions are removed, BEFORE the sample is built
and thinned to one event per ticker per week, so an excluded event cannot block a neighbour; the number of labels removed is printed.
The target text must match exactly once and the file must not already carry the filter, or nothing is written; the pre-patch hash is printed.
Usage: python3 scripts/audit/g7_patch_arm1_direction_v1.py /tmp/g7_pin_dir/scripts/card/direction_test.py"""
import hashlib, sys
p = sys.argv[1]
assert "/tmp/" in p, "refusing to patch a file outside /tmp (this patch is for a pinned worktree only)"
S = open(p, encoding="utf-8").read()
print("pre-patch sha256:", hashlib.sha256(S.encode("utf-8")).hexdigest())
assert "_g7_ex" not in S, "the file already carries the ARM 1 filter; nothing was written"
old = '    labels = {r["event_id"]: r for r in paged(sb, "event_direction_labels", "event_id,ticker,ptype,event_date,label,size,timing", ["event_id"])}\n'
assert S.count(old) == 1, "target line not found exactly once (found %d); nothing was written" % S.count(old)
new = (old +
       '    _g7_ex = {r["event_id"] for r in paged(sb, "event_exclusions", "event_id,severity", ["event_id"]) if r.get("severity") == "exclude"}\n'
       '    _g7_before = len(labels)\n'
       '    labels = {k: v for k, v in labels.items() if k not in _g7_ex}\n'
       '    print("G7 ARM 1: %d excluded events; %d of %d labels removed before the sample is built" % (len(_g7_ex), _g7_before - len(labels), _g7_before), flush=True)\n')
open(p, "w", encoding="utf-8").write(S.replace(old, new))
print("ok   ARM 1 filter inserted; the run prints the number of labels removed")
