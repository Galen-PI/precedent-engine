"""g7_patch_arm1_event_width.py (2026-10-30): the ARM 1 filter for the band_calibrate.py re-run (G7, Addendum 4). Edits ONLY the copy of
scripts/card/event_width_test.py inside a pinned git worktree (never the repository checkout): after the loader reads ev_ent, rows whose
event_id has an `exclude` row in event_exclusions are skipped, so their days stop being 'recorded event' days. The target line must match
exactly once or nothing is written; the pre-patch hash is printed for the record.
Usage: python3 scripts/audit/g7_patch_arm1_event_width.py /tmp/g7_pin_band/scripts/card/event_width_test.py"""
import hashlib, sys
p = sys.argv[1]
assert "/tmp/" in p, "refusing to patch a file outside /tmp (this patch is for the pinned worktree only)"
S = open(p, encoding="utf-8").read()
print("pre-patch sha256:", hashlib.sha256(S.encode("utf-8")).hexdigest())
old = '    for r in paged(sb, "ev_ent", "event_id,entity_id,d,ptype", ["event_id", "entity_id"]):\n'
assert "_g7_ex" not in S, "the ARM 1 filter is already present; nothing was written"
assert S.count(old) == 1, "target line not found exactly once (found %d); nothing was written" % S.count(old)
new = ('    _g7_ex = {r["event_id"] for r in paged(sb, "event_exclusions", "event_id,severity", ["event_id"]) if r.get("severity") == "exclude"}\n'
       '    _g7_rows = paged(sb, "ev_ent", "event_id,entity_id,d,ptype", ["event_id", "entity_id"])\n'
       '    _g7_keep = [r for r in _g7_rows if r["event_id"] not in _g7_ex]\n'
       '    print("G7 ARM 1: %d excluded events; %d of %d ev_ent rows removed from the recorded event days" % (len(_g7_ex), len(_g7_rows) - len(_g7_keep), len(_g7_rows)), flush=True)\n'
       '    for r in _g7_keep:\n')
open(p, "w", encoding="utf-8").write(S.replace(old, new))
print("ok   ARM 1 filter inserted; the run prints the number of ev_ent rows it removes")