"""g7_patch_arm1_event_width_v2.py (2026-10-30): the ARM 1 filter for the earnings_role_band_test.py re-run (G7, Addendum 7). Edits ONLY the copy of
scripts/card/event_width_test.py inside a pinned git worktree under /tmp (never the repository checkout): after the loader reads ev_ent, rows whose
event_id has an `exclude` row in event_exclusions are skipped, so their days stop being 'recorded event' days, and the number of skipped rows is
printed when the loop ends. Both target texts must match exactly once and the file must not already carry the filter, or nothing is written;
the pre-patch hash is printed. Differences from g7_patch_arm1_event_width.py (used for band_calibrate.py and event_width_test.py): v2 refuses a
second application and prints the skipped-row count.
Usage: python3 scripts/audit/g7_patch_arm1_event_width_v2.py /tmp/g7_pin_role/scripts/card/event_width_test.py"""
import hashlib, sys
p = sys.argv[1]
assert "/tmp/" in p, "refusing to patch a file outside /tmp (this patch is for a pinned worktree only)"
S = open(p, encoding="utf-8").read()
print("pre-patch sha256:", hashlib.sha256(S.encode("utf-8")).hexdigest())
assert "_g7_ex" not in S, "the file already carries the ARM 1 filter; nothing was written"
old1 = '    for r in paged(sb, "ev_ent", "event_id,entity_id,d,ptype", ["event_id", "entity_id"]):\n'
old2 = '    info = {}\n    for sid, days in cand.items():\n'
assert S.count(old1) == 1, "first target not found exactly once (found %d); nothing was written" % S.count(old1)
assert S.count(old2) == 1, "second target not found exactly once (found %d); nothing was written" % S.count(old2)
new1 = ('    _g7_ex = {r["event_id"] for r in paged(sb, "event_exclusions", "event_id,severity", ["event_id"]) if r.get("severity") == "exclude"}\n'
        '    print("G7 ARM 1: %d excluded events are removed from the recorded event days" % len(_g7_ex), flush=True)\n'
        '    _g7_dropped = 0\n'
        + old1 +
        '        if r["event_id"] in _g7_ex:\n'
        '            _g7_dropped += 1\n'
        '            continue\n')
new2 = '    print("G7 ARM 1: %d ev_ent rows were skipped as excluded events" % _g7_dropped, flush=True)\n' + old2
open(p, "w", encoding="utf-8").write(S.replace(old1, new1).replace(old2, new2))
print("ok   ARM 1 filter inserted; the run prints the skipped-row count")
