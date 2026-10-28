import hashlib, sys
def sha(s): return hashlib.sha256((s if s.endswith("\n") else s + "\n").encode("utf-8")).hexdigest()
p = sys.argv[1] if len(sys.argv) > 1 else "docs/PROJECT_STATUS.md"
t = open(p, encoding="utf-8").read()
assert sha(t) == "ebb65826f742b356099d7800c89ace3fa85180b35fd10f812289379158d3e209", "PROJECT_STATUS is not the expected v1; nothing changed"
def sub(old, new, label):
    global t
    n = t.count(old)
    assert n == 1, "%s: expected exactly 1 match, found %d; nothing was written" % (label, n)
    t = t.replace(old, new); print("ok  ", label)

sub("# PROJECT STATUS (v1, 2026-10-28)", "# PROJECT STATUS (v1.1, 2026-10-28 evening)", "title")
sub("| 4 External Conditions | `[PENDING]` (G8) | unmeasured; FOMC calendar refresh due today (section 8) |",
    "| 4 External Conditions | `[PENDING]` (G8) | unmeasured; FOMC calendar loaded through the 2026-10-28 meeting (310 rows; one spurious 2003-09-15 row, section 7) [LIVE 10-28] |", "phase 4 row")
sub("| 5 Price Reaction Engine | the five-component gate query of 2026-10-28 (G1) | **4 of 5 components PASS; the ripple-timeline component has 31 undocumented gaps** [LIVE 10-28] |",
    "| 5 Price Reaction Engine | the five-component gate, scripts/sql/phase5_gate.sql (G1) | **5 of 5 components PASS** [LIVE 10-28 evening]; the gate accepts a review reason as documentation and 333 events carry one (G5) |", "phase 5 row")
sub("325 `review` (date_corrected_review 267, reaction_row_not_computable 55, price_step_in_window 3)",
    "333 `review` (date_corrected_review 267, reaction_row_not_computable 55, price_step_in_window 3, bundle_multi_component_review 8 added 10-28 evening)", "exclusions review count")
sub("**Numbers recorded in documents, not re-verified:**",
    "**Added 2026-10-28 evening** (CHANGELOG 2026-10-28-07 and -08): the view ripple_skip_events (1,291 events the ripple builder skips: 2 or more component rows, plus every `exclude` reason); backups fomc_meetings_backup_20261028 (310 rows) and event_ripple_timeline_backup_20261028 (8 events, 349 rows), BOTH to be dropped after 2026-11-28; 8 new event_exclusions review rows; ripple timeline 21,913 events and 954,599 rows (was 21,599 and 940,758); fomc_meetings 310 rows with the 2026-10-28 meeting confirmed; results/ripple_skips_2026-10-28.csv (323 skipped pairs: 286 no security for the entity, 37 no prior close, each with its reason; the 37 are unread). Database 3,160 MB, 157 tables and 33 views at the snapshot, 159 and 34 after the two backups and the view [LIVE 10-28].\n\n**Numbers recorded in documents, not re-verified:**", "evening additions")
sub("| G1 | Phase 5 gate as a runnable check | 4 of 5 components PASS; 31 events with a reaction row have no ripple timeline and no recorded reason: list them, rebuild or record |",
    "| G1 | Phase 5 gate as a runnable check | **DONE 10-28**: scripts/sql/phase5_gate.sql, 5 of 5 PASS. The first run read 319 gaps at component 5 (the earlier 31 counted a provenance note as a reason); the causes are fixed in the ripple builder (CHANGELOG 2026-10-28-08); 333 review events remain (G5) |", "G1")
sub("| G5 | review groups: 267 corrected dates (read a stratified sample), provenance for the 323 curated events, the 514 fast quarterly filings, same-day duplicate events | open |",
    "| G5 | review groups (333 events carry a review reason): 267 corrected dates (read a stratified sample), the 55 not computable, the 3 price steps, the 8 multi-row bundles; plus provenance for the 323 curated events (280 have one stray bundle row and are real single-date events), the 514 fast quarterly filings, same-day duplicate events | open |", "G5")
sub("| G7 | rerun the 15 proven flags and the significance audit on the analysis set; record in the ledger evidence | open |",
    "| G7 | rerun the 15 proven flags and the significance audit on the analysis set; record in the ledger evidence (rerun on the corrected ripple table: 314 events were added 10-28; 3 of the 15 only say a type uses the pooled number) | open |", "G7")
sub("| G9 | documents: this file (v1 done), then README, PROJECT_PLAN, THEORY (ledger-anchored, with a Retired section), OPERATIONS refresh, regenerate SCRIPTS_REFERENCE | in progress |",
    "| G9 | documents: this file (v1.1), README, PROJECT_PLAN v2 and THEORY v2 (ledger-anchored, with a Retired section) done 10-28; OPERATIONS refresh and the SCRIPTS_REFERENCE regeneration open | in progress |", "G9")
sub("1. **31 events** have a reaction row, no ripple timeline and no recorded reason (G1).",
    "1. **Resolved 10-28:** the ripple gap (319 events: 280 real events wrongly skipped as bundles, 30 News Corp events lost to a share-class defect, 8 computed on the wrong class, 1 isolated miss; CHANGELOG 2026-10-28-08). **New open items:** (a) the FOMC calendar holds one spurious row, the meeting of 2003-09-15 (the Fed's schedule has eight meetings, September's on the 16th); no finished test counted it; the fix belongs in build_fomc_calendar.py; (b) ten stale or inconsistent ledger rows (THEORY section 8: fed_state says easing but the Fed raised the target range on 2026-09-16; news_sentiment_gdelt is untested though two tests ran; three proven type rows carry first-run numbers; and others); (c) the 37 \"no prior close\" skips in results/ripple_skips_2026-10-28.csv are unread; (d) 333 review events await a decision (G5).", "inconsistency 1")
sub("2. **Documents stale or misleading:** README, PROJECT_PLAN, THEORY (THEORY lists the storm effect as validated; the ledger says lead). OPERATIONS partly stale; its \"known bug\" note on multi-entity tagging predates the fix.",
    "2. **Documents:** README, PROJECT_PLAN and THEORY were rewritten 10-28 (the README held-and-not-held section was corrected against the ledger the same day). OPERATIONS is partly stale (its \"known bug\" note on multi-entity tagging predates the fix); SCRIPTS_REFERENCE does not list files added since 10-26.", "inconsistency 2")
sub("`[PENDING]` current database size and host.", "Database 3,160 MB on Supabase, 157 tables and 33 views on 2026-10-28 [LIVE]; the host and plan are not recorded here.", "inconsistency 8")
sub("| 2026-10-28 (today, after about 18:30 UTC) | FOMC meeting held (statement 18:00 UTC); run runbook 3c: build_fomc_calendar.py, READ the validation (the script's independent list ends 2026-09-16: if only 2026-10-28 is flagged, add it from the Fed's calendar page, not from the script's output), load_fomc_meetings.py (dry run), then --apply | runbook 3c |",
    "| 2026-10-28 | **DONE:** FOMC calendar rebuilt after the 18:00 UTC statement, 2026-10-28 added to the independent list, loaded with --apply (310 rows; 1 row changed) | CHANGELOG 2026-10-28-07 |\n| after 2026-11-28 | drop the scratch and backup tables: fomc_meetings_backup_20261028, event_ripple_timeline_backup_20261028, scratch_diverged_new_20261028, scratch_diverged_v2_20261028 (G10) | CHANGELOG |", "calendar")
sub("*v1, 2026-10-28. Update at the end of every session and add a CHANGELOG entry. Next revision: fill the `[PENDING]` slots (table inventory, Phase 1-4 gate checks), the 31 ripple gaps, G4 and G7.*",
    "*v1.1, 2026-10-28 evening. Update at the end of every session and add a CHANGELOG entry. Next revision: fill the `[PENDING]` slots (table inventory, Phase 1-4 gate checks), then G4, G5 and G7.*", "footer")
open(p, "w", encoding="utf-8").write(t)
print("patched:", p, "| sha256", sha(t), "|", t.count("\n"), "lines")