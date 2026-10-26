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
### Latest checkpoint: 2026-10-26 20:00 +0000 (20:00 UTC) | CHANGELOG 2026-10-26-20 | reason: milestone: tagger fixed, labels relabeled and confirmed; next: record the relabel, entity-reaction repair, tagger run

WRITTEN BY THE ASSISTANT at about 20:00 UTC (sandbox clock). Context: this conversation has been compacted 31 times since 2026-09-21 (transcripts in /mnt/transcripts, median 1.75 MB at compaction, per-message ISO timestamps inside); the last compaction was 18:22:32 UTC today; fullness of the current segment is an ESTIMATE of about two thirds (range 50 to 85%).

DONE SINCE THE SCRIPTS.md RETIREMENT (commit hashes and times are appended below from git log):
- SCRIPTS.md retired into CHANGELOG.md (171 entries, verified line for line), docs/OPERATIONS.md, an archive copy and a stub; generated docs/SCRIPTS_REFERENCE.md; docs/NAMING.md and docs/PROJECT_STATUS.md (draft v0) added; scripts/audits merged into scripts/audit; the empty file named = removed.
- TAGGER FIXED: compute_abnormal_return now uses the PRIOR-close baseline in tag_reaction_character.py and tag_multientity_reactions.py (scripts/audit/patch_tagger_baseline.py v2; live check scripts/audit/check_tagger_convention.py: 100 of 100 labels agree, PASS). Cause: the label used the event-day close as its base, so the event-day move was excluded; the saved columns and the written rule use the prior close.
- RELABEL DONE (SQL, not in git): event_tags_backup_20261026 (17,703 rows) and scratch_reaction_relabel_20261026 (15,897 proposal rows, 2,435 changes); 70 cases read including all 36 wrong-sign events, every one followed the rule; the guarded update applied the changes and its in-transaction check passed; the 9 held events (6 direction flips, 2 multi-entity, 1 null firm state) were read and applied. CONFIRMED, explore set: rewarded 2,520, punished 2,529, muted 4,024, diverged 1,630, every label consistent with the saved column (0 mismatches; it was 15.3%).
- The 7,568 events the tagger will find were counted exactly in SQL (7,602 untagged minus 34 with no entity link).
- TOOLS: scripts/audit/changelog_tools.py v3: add, check, retitle, checkpoint (writes CHANGELOG.md and docs/START_NEW_DAY.md; appends the git log since the previous checkpoint and git status).

DECISIONS (by the user): phase names 1 to 8 stay with the principles and tracks of docs/NAMING.md (Phase 4 "News Ingestion" is flagged as too narrow; renaming it to External Conditions is NOT yet decided); relabel to the prior-close convention (done); process the unprocessed events (approved); rerun the significance audit on corrected labels (approved); merge the audit folders (done); checkpoints for compaction, written to the changelog and docs/START_NEW_DAY.md, with a fullness estimate at the start of each session (approved).

NEXT, IN ORDER:
1. Record the relabel in the changelog: rule (label from the saved prior-close abnormal_return_20d, +-3%; diverged = rewarded with weakening or deteriorating, punished with strong or improving, firm state of the SAME company, latest computed), the backup table name, the revert path (delete the four reaction-tag names from event_tags, reinsert those rows from event_tags_backup_20261026).
2. event_entity_reactions: its multi-entity rows were computed with the OLD convention; get a row count first (SELECT COUNT(*), COUNT(DISTINCT event_id) FROM event_entity_reactions), then repair with the patched function.
3. Tagger run for the 7,568 unprocessed events: first patch get_untagged_events to add ORDER BY to its two unordered paginations (event_tags and event_entity_relationships) with an all-or-nothing patcher; the dry run (python3 scripts/tagging/tag_reaction_character.py --dry-run) must report EXACTLY 7,568; then run it in the background with scripts/ops/bg.sh (resume-safe: tagged events drop out of the list).
4. Pre-context for the new events (populate_pre_context.py), then the diverged step with a deterministic same-company firm-state join (the old backfill_diverged_from_fundamentals.py takes the first pre-context row with no tie-break).
5. Rerun scripts/models/audit_pattern_significance.py on the corrected labels; then D3 and D4 (PROJECT_PLAN.md section 6) on corrected labels with a matched baseline and the two dumb baselines.
6. Finish the documents: PROJECT_STATUS.md v1 (the [PENDING] slots need the table inventory and the ledger queries, never pasted); refresh the Project knowledge (it still holds the September snapshot); check file names after every upload.
7. Dated: Wed 2026-10-28 after the FOMC meeting: runbook 3c (build_fomc_calendar.py, read the validation, load_fomc_meetings.py --apply); after 2026-10-31 (Mon 11-02): October sentiment top-up (runbook 8); January runbook after 2027-01-05.

KEY FACTS TO RE-VERIFY LIVE (2026-10-26): events 23,554; reaction rows 15,897; reaction-tagged 15,952; pre-context 16,413; unprocessed: the Oct 3 promotion cohort 3,133 of 3,139, the Oct 15 waves 3,662 of 3,662, plus 862 older gaps (807 untagged, 34 without an entity link). Label convention: 20 trading days, baseline PRIOR close (event-day move included), SPY benchmark, +-3%.
OTHER OPEN: five functions share the name compute_abnormal_return (two conventions); get_untagged_events has an indentation oddity (line 112) and unordered pagination; three runtime checkpoint files are tracked in the repo root (.populate_sectors_checkpoint unexplained); README, PROJECT_PLAN and THEORY are stale; uploaded files arrive without their final newline (the tolerant gate handles it).
HOW THE USER WORKS: pastes the output after each block; every step is its own labelled block; the assistant cannot write to the repo, so every record is a block the user pastes.

COMMITS SINCE THE PREVIOUS CHECKPOINT (last 24 hours; no earlier checkpoint), from git log, objective:
  6cfea7e 2026-10-26 19:46 Merge scripts/audits into scripts/audit (no collisions, no code references; the 13 earlier hits were SEC text in data_cache);
  629335a 2026-10-26 19:45 Changelog: tagger convention finding and fix (2026-10-26)
  6615ec5 2026-10-26 19:43 Tagger: compute_abnormal_return uses the prior-close baseline (the written rule) in both copies; one-off patch and live check
  3606fec 2026-10-26 19:39 Add NAMING.md and PROJECT_STATUS.md draft v0
  e8d6eed 2026-10-26 19:10 Remove the empty stray file named =
  4bf1a3f 2026-10-26 19:10 Generated scripts reference: every script's purpose, flags and the tables it reads and writes
  4010f0b 2026-10-26 19:10 Retire the SCRIPTS.md monolith: CHANGELOG.md (dated entries, verified line for line), docs/OPERATIONS.md, archived original, 
  6975084 2026-10-26 18:51 Audit pack builder: text files of results, docs and root documents into one zip with a dated manifest
  c0960e2 2026-10-26 18:51 Correction: D3/D4 are defined in PROJECT_PLAN.md section 6 (prediction contract and walk-forward harness)
  194debb 2026-10-26 18:51 Correction: D3/D4 are defined in PROJECT_PLAN.md section 6 (prediction contract and walk-forward harness)
  5d85a62 2026-10-26 18:41 Addendum 29: tags disagree with the current return columns for 15.3% of events; calmer-than-random gap and implied-sealed sha
  9deb3f2 2026-10-26 18:32 Reaction explorer (sealed 30% of companies, logged looks, thin-cell stars); notes addendum 28: the four reasons the percents 
  fd6d822 2026-10-26 18:20 Footing simulation (old test calls random groups significant: 6.4 of 13 against the real 6); user decisions: D3/D4 reworked n
  66e90e8 2026-10-26 18:10 Correction to addendum 26: counts vintage, D3/D4 are recommendations, fatigue withdrawn, calmer-events gap unexplained
  5b184f8 2026-10-26 18:08 Audit: pattern-significance tests against the overall reaction mix (0 of 13 survive); D3/D4 retired; Phase 6 docket restated
  8aa2634 2026-10-26 17:54 Notes addendum 25 (anchors baked into the process); runbook: hook note for the frozen day_card edits, descriptive coverage an
  b5bf14f 2026-10-26 17:54 Bake the external anchors into the process: registration template, checker, prediction scorer, and a pre-commit hook (frozen 
  306ef9f 2026-10-26 17:50 ANCHORS.md: published magnitudes and standard methods verified by search (FOMC drift, price clustering, multiple-testing hurd
  fd5a6c0 2026-10-26 17:46 Notes addendum 24: predictions carry an anchor label; anchor slice before thresholds are fixed
  096c883 2026-10-26 17:43 SQL linter: parentheses and dollar-quote tags, including inside DO blocks
  14be36c 2026-10-26 17:36 Round-number cents diagnostic read (exploratory) and disposition; runbook step 13 (free forward check)
  ef5926e 2026-10-26 17:29 Round-number tests: registered results (both NULL by the registered rules; clustering calibration failed), predictions scored
  0071773 2026-10-26 17:26 Job monitor: one-line verdict (ALL CLEAR / ATTENTION), old finished jobs hidden unless --all
  5c74681 2026-10-26 15:33 Round-number outcome script (registered tests; tested on planted effects, null, one-era effect, stop rule, pre-flight and res
  0f53c94 2026-10-26 15:27 Pre-registration: round-number clustering and threshold tests (confirmatory scope from the outcome-free counts; pass lines, c
  f7b14db 2026-10-26 15:22 Notes addendum 20: outcome-free counts for the round-number tests, calls scored, decisions for the registration, an explorato
  e1751dd 2026-10-26 15:01 Outcome-free counts for the round-number tests: order-of-magnitude classes, matched placebo neighbours per threshold, resumab
  7beff3a 2026-10-26 14:56 Price foundation closed: final state and use rule (addendum 6), runbook 3b3 correction (a full refetch would undo the class C
  7bd2132 2026-10-26 14:51 wait_job.sh: wait for a background job and chain the next command only if it exited 0
  a255bf9 2026-10-26 14:48 Class C repair prepared: fetcher --tol and --force (tested), valid-from --only, rebuild results and the departure from the do
  c14bcd2 2026-10-26 14:42 Valid-from addendum 4: classifier results on the 15 post-2005 losses, decisions for A, B and C registered before any repair
  1331491 2026-10-26 14:40 bg.sh: refuse a same-name start while the first runs; keep each finished run's log as NAME.log.prev
  4e1b3a0 2026-10-26 14:37 Valid-from script: --since scope and a rule_version column (tested on planted cases)
  8eceb01 2026-10-26 14:37 Valid-from addendum 3: profile results scored, pre-2001 levels out of scope (scope reduction, taken after the profile), rebui
  2d44914 2026-10-26 14:33 Grid profile (fractions-to-pennies diagnostic) and a classifier --after filter
  e05a091 2026-10-26 14:33 Valid-from addendum 2: LOSS list read, hold on the pre-2005 cluster, grid-profile test and predictions registered before read
  f271202 2026-10-26 14:29 Loss-ticker classifier: applies the registered A/B/C rule, one vendor request per ticker, resume-safe (tested on planted case
  2b6166d 2026-10-26 14:24 Notes addendum 18: three mechanisms behind valid-from losses, decision rule fixed before the LOSS list, tariff design correct
  fca626a 2026-10-26 14:20 Notes addendum 17: foundation check rule before any new build or registration; circular tariff design corrected; limit of the
  7c22859 2026-10-26 14:20 Compare our reconstructed as-quoted closes with the vendor's current unadjusted closes (read-only, one request)
  0ea0bd4 2026-10-26 14:15 Valid-from dry run: results versus predictions, the registration's wording flaw and the intended LOSS measure fixed before co
  8ff0bd1 2026-10-26 14:11 Notes addendum 16: plan to return to the Phase 6 docket (time-box, parked validation, order and dates)
  046c67f 2026-10-26 13:58 Runbook: valid-from table rebuild after the January price refresh (3b2); FOMC announcement-day lane after the role-band verdi
  733f4a4 2026-10-26 13:52 Design addendum: stratified false-accept by law size (before the verifier is built); notes addendum 15: subject terms, as-quo
  d4ba4a2 2026-10-26 13:50 Script applying the registered levels-valid-from rule (tested on planted cases; not yet run on data)
  f3788fe 2026-10-26 13:46 Accuracy scan: retry transient database errors, save each ticker as it finishes (resume), per-year profile for every ticker, 
  e579f38 2026-10-26 13:44 Pre-registration: per-ticker levels-valid-from rule for the as-quoted prices (written before the all-ticker scan list was rea
  a751694 2026-10-26 13:39 Probe: is the vendor's unadjusted series really as-traded around a corporate action (penny-grid runs and the flip)
  70d265b 2026-10-26 13:35 Acceptance test: 1/32 grid column, all-ticker scan with PROGRESS lines, list of every failing ticker, per-year diagnostic
  6d450ea 2026-10-26 13:34 Job monitor: PROGRESS done/total convention for any script; record the completed as-quoted download (492 ok, 5 flagged, 2 err
  4f3577a 2026-10-26 13:32 Acceptance test for the as-quoted prices: decimalization grids (1/16 before 2001, pennies after) as a fact the vendor never s
  97bf0f0 2026-10-26 13:26 Job visibility: bg.sh launcher that records how a job ends, and a one-screen monitor (running, stalled, finished, failed, sto
  500c186 2026-10-26 13:18 Subject fetcher: write every 100 laws (terms before run rows) so a stopped session loses at most 100
  c3f5cde 2026-10-26 13:13 As-quoted factors: ratio decreases under 0.5% are informational (splice-scale noise); merger-sized decreases still flag
  b1d6a1b 2026-10-26 13:12 Subject fetcher: the API count includes the policy area; up to 40 pages for omnibus-sized bills
  7b31212 2026-10-26 13:09 Congress subject-term fetcher (design step 2): policy area and legislative subjects per relevant law, paged, resume-safe

UNCOMMITTED (git status --short):
  M CHANGELOG.md
   M scripts/audit/changelog_tools.py
  ?? results/tag_review_v1_galen.txt
<!-- CHECKPOINT-END -->
