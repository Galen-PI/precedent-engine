# START NEW DAY

**The first file to read in a new session, or after a compaction.** Then docs/PROJECT_STATUS.md (current state), docs/NAMING.md, CHANGELOG.md (index first), docs/OPERATIONS.md, docs/SCRIPTS_REFERENCE.md (generated).

## How to resume (for the assistant)
1. START OF EVERY SESSION: say (a) the time now (run date -u) and the age of the LATEST CHECKPOINT below; (b) if /mnt/transcripts is mounted, how many earlier transcript segments exist and when the last compaction was (the transcripts carry an exact ISO timestamp per message; journal.txt catalogues them); (c) a fullness ESTIMATE of this conversation, labelled as an estimate: you have no gauge, but earlier segments were compacted at a median of 1.75 MB (middle half 1.65 to 1.94 MB, 31 segments), so estimate from how much text has been exchanged and the time since the last compaction; then five lines of what you understood and the next step; wait for the user to confirm before doing anything.
1b. BEFORE WRITING ANY CHECKPOINT: review the whole visible conversation since the last checkpoint; the tool appends the git log and git status itself; after a compaction, read the tail of the newest transcript and journal.txt and grep /mnt/transcripts for details instead of trusting the summary alone.
2. Do not trust any number in any document as current: re-check it against the live database. SQL for the user uses dollar-quoting ($$text$$); every long SQL goes through scripts/ops/lint_sql.py first; a multi-statement SQL run is one transaction.
3. If you are not sure how a script works, ask the user to paste the real file. Never guess an interface.
4. Never bulk-confirm or bulk-correct before reading the cases: state the rule first, keep a backup table, read a stratified sample, apply guarded.
5. Every numeric prediction is a point, a range and an anchor label (DATA, LITERATURE or NONE); score it afterwards.
6. Every step is its own block labelled FOREGROUND (this terminal), BACKGROUND (second terminal) or SQL editor. Files arrive with a tolerant hash gate: check() { [ "$(sed -e '$a\' "$2" | sha256sum | cut -d' ' -f1)" = "$1" ] && echo "OK     $2" || { echo "FAILED $2"; return 1; }; }
7. The eight forward-test files are FROZEN until both verdicts are recorded (scripts/hooks/pre-commit enforces it). Sealed companies (table explore_sealed_tickers) stay out of every exploratory look.
8. Be honest about sample size and uncertainty, including about your own findings; when something does not add up, say so and dig.

## Checkpoints
A checkpoint is written at every milestone, whenever the conversation may need compaction, when the user says "checkpoint", and at the end of the day:
    python3 scripts/audit/changelog_tools.py checkpoint --reason "..." << 'EOF'  (body)  EOF
It adds a CHANGELOG entry (the history) AND replaces the block below (the latest state).

<!-- CHECKPOINT-START -->
### Latest checkpoint: 2026-10-26 20:08 +0000 (20:08 UTC) | CHANGELOG 2026-10-26-23 | reason: milestone: tagger guard resolved (7,282 = exact count); next: pilot the live tagger on one ticker

WRITTEN BY THE ASSISTANT at about 20:08 UTC (sandbox clock). ESTIMATE: this segment is about three quarters full (range 60 to 90%); the last compaction was 18:22:32 UTC; 31 earlier segments in /mnt/transcripts.
STATE: tagger convention fixed and committed (6615ec5); explore-set labels relabeled and confirmed, 0 mismatches (changelog entry d191e38); START_NEW_DAY and the changelog tools built (dcd7736); the guard result is in the changelog.
GUARD RESOLVED: the tagger's dry run (python3 scripts/tagging/tag_reaction_character.py --dry-run) finds 7,282 events; the exact SQL count of untagged events that have a linked SECURITY is also 7,282. The other 286 untagged events link only to entities with no securities row (get_untagged_events drops them by design: its last line keeps events that have a ticker) and 34 have no entity link: 7,602 untagged = 7,282 + 286 + 34. The 7,657 events without a reaction row = 7,602 untagged + 55 tagged events lacking a row. No pagination loss was seen.
PLAN NOW: (1) pilot the live tagger on ONE ticker (CPRT): dry run with timing, live run, then a SQL check that every CPRT label agrees with its saved column and that the tagged-event and reaction-row counts rose by exactly the number tagged; (2) from the pilot's time per event, decide how to run the 7,282 (background with scripts/ops/bg.sh and python3 -u; resume-safe because tagged events drop out of the list; watch the Codespace idle timeout); (3) repair event_entity_reactions (124 rows, 49 events, 44 entities, computed on the old convention): backup table, a script that prints all 124 rows old versus new for reading, then a guarded update; (4) pre-context for the new events (populate_pre_context.py), then the diverged step with a deterministic same-company firm-state join; (5) rerun scripts/models/audit_pattern_significance.py on the corrected labels, then D3 and D4; (6) documents: PROJECT_STATUS v1 (needs the table inventory and ledger queries, never pasted), README, the PROJECT_PLAN status table, file renames, the Project knowledge refresh, the repo-root tidy. The Phase 4 name (News Ingestion or External Conditions) is NOT yet decided.
DATED: Wed 2026-10-28 after the FOMC meeting: runbook 3c (build_fomc_calendar.py, read the validation, load_fomc_meetings.py --apply); after 2026-10-31 (Mon 11-02): October sentiment top-up (runbook 8); January runbook after 2027-01-05.
RE-VERIFY LIVE: events 23,554; reaction rows 15,897; reaction-tagged 15,952; pre-context 16,413 (all 2026-10-26). Label convention: 20 trading days, baseline PRIOR close (event-day move included), SPY benchmark, +-3%; diverged = rewarded with a weakening or deteriorating firm state, or punished with a strong or improving one, the SAME company's, latest computed.
OTHER OPEN: the tagger's 'primary company' for a multi-entity event is the first link of an unordered read (nondeterministic; 49 multi-entity events among the old tagged, few among the new); get_untagged_events pagination is unordered (patch only if a count ever disagrees); five functions are named compute_abnormal_return; the tagger skips renamed or reorganized tickers (EXE for Chesapeake, HWM for Alcoa: predecessor-ticker price gaps, already on the docket); three runtime checkpoint files sit in the repo root; README, PROJECT_PLAN and THEORY are stale.
HOW THE USER WORKS: pastes the output after each block; every step is its own labelled block; the assistant cannot write to the repo.

COMMITS SINCE THE PREVIOUS CHECKPOINT (since 2026-10-26 20:00 +0000), from git log, objective:
  5c2f009 2026-10-26 20:07 Changelog: tagger dry run found 7,282 against an exact count of 7,568; investigating before any real run
  d191e38 2026-10-26 20:01 Changelog: reaction labels relabeled to the prior-close convention (rule, readings, revert path)
  dcd7736 2026-10-26 20:00 Checkpoint protocol v3: checkpoint command (appends git log and status), docs/START_NEW_DAY.md, retitle fix; first checkpoint

UNCOMMITTED (git status --short):
  ?? results/tag_review_v1_galen.txt
<!-- CHECKPOINT-END -->
