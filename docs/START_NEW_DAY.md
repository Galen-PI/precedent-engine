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
### Latest checkpoint: 2026-10-30 14:41 +0000 (14:41 UTC) | CHANGELOG 2026-10-30-14 | reason: orientation after the 8-K timing work and a context compaction; replaces the stale 2026-10-29-15 checkpoint

CHECKPOINT 2026-10-30 (written after the 8-K timing work and a context compaction; it replaces the stale 2026-10-29-15 orientation, which still says Arm 1 is next)

STATE OF THE REPO (all pushed): cfddac7 event_timing definition; 4c1c0d9 lag-split result; d64c3dd lag-split registration; dff440f sec_8k_report_dates definition; 004ee80 8-K lag measured and the script; 6b9daf5 Tier 1 window nulls saved. Changelog 224 entries, CHECK OK, at cfddac7. Untracked: results/tag_review_v1_galen.txt (the user's own, leave alone).

NEW IN THE DATABASE TODAY (both additive; sec_8k_filings untouched; tables now 166):
- sec_8k_report_dates: 155,969 rows (security_id, accession_number, filing_date, report_date, acceptance_datetime, items; PRIMARY KEY (security_id, accession_number)). Loaded by scripts/ingestion/pull_8k_report_dates.py --from-csv --apply from data_cache/8k_report_dates.csv (untracked). Every one of the 155,141 filings in sec_8k_filings has a row. The SEC feed carries reportDate and acceptanceDateTime; the old importer dropped them.
- event_timing: 22,385 rows, one per event with a source 8-K (event_id, ticker, accession_number, filing_date, report_date, td_lag, report_is_trading_day, report_dow, acceptance_datetime, accepted_et_time, accepted_bucket, items, k_star). td_lag counts SPY trading days after the report date up to the filing date; k_star is that lag aligned to the first trading day on or after a non-trading report date. The daily event data (event_daily_abn) runs only from day -5 to +39.

FINDINGS TODAY (numbers are in the changelog entries 2026-10-30-01 to -13 and the files under results/):
1. G7 Tier 1 window nulls re-run: event_pre_days_m4_m1 meets its rule (cleaned sample 1.054 z 4.95 and 1.043 z 3.23); event_lasting_days_6_20 stays null.
2. Across 155,969 8-Ks, 55.0 percent are filed the day of the event and 45.0 percent a day or more late (earnings 13.2 percent late, other required items 76.2, voluntary-only 40.7).
3. Lag-split test (results/PREREG_g7_pre_window_lag_split_2026-10-30.md, output results/g7_rerun/lag_split_results_2026-10-30.out): decision rule SUPPORTED. Same-day filings pre-window 1.024 (z 1.81); pooled lags 1-4 1.068; difference +0.044 (t 2.55, thin margin on the 0.04 bar); sealed set alone not significant (+0.022, t 0.71). The lag mix explains about 53 percent of the overall rise (1.051); a residual of +0.024 remains in same-day filings (z 1.81). The burst at the filing date falls with the lag (1.405, 1.351, 1.269, 1.179, 1.099). Numeric 9 of 11 inside their 80 percent intervals. As registered: the Tier 1 candidate stays null (ledger note to read: largely explained by the 8-K filing lag; residual not distinguishable from zero) and its January forward check is dropped.
4. Lag 1 broke the prediction (pre-window 1.015 against 1.065; burst 1.351).
5. Acceptance times (Eastern) of the 22,385 event 8-Ks: 32.6 percent before 09:30, 18.2 percent during the session, 49.2 percent after 16:00. EDGAR's 5:30 PM rule holds (only 128 events, 0.6 percent, were accepted after 17:30 without moving to the next business day) but it is small: 1,314 events (5.9 percent) rolled, 799 of the 5,658 lag-1 events (14.1 percent). Lag 1 is 39.8 percent filed before the open (2,250), 28.9 percent after the close but not rolled (1,637), 17.2 percent intraday (972). About 9,700 events (43 percent) were accepted between 16:00 and 17:30 and not rolled: for those the market reaction falls on the day AFTER the filing date.
   CORRECTION to changelog entry 2026-10-30-13 (entries are append-only): it floated the 5:30 PM rollover as an untested explanation for lag 1; the counts show the rule is real but covers only 14 percent of lag 1, so it cannot explain the anomaly alone.

PLAN, IN ORDER (the user asked for all three; nothing below has been registered yet):
 a. REGISTER (predictions first, repo template, checker) the REACTION-DAY PROFILE: day-by-day ratio (days -5 to +5 over days 25 to 39) by group: lag 0 by acceptance window, lag 1 by acceptance window, rolled lag 1. Predictions: the peak day per group and its ratio (prior: lag 0 intraday and pre-open peak day 0; lag 0 after-close peak day +1; lag 1 rolled and pre-open peak day 0). Power warning to state in the registration: the window-average difference the filing windows predict inside lag 1 is only about 0.03 with an SE of about 0.03 (assistant's estimate), so the day-by-day profile is the instrument, not window averages.
 b. REGISTER the RE-CENTERED BURST: the burst at the true event day (offsets -k to -k+1 with k = k_star 0 to 5), isolation widened to 14 calendar days before the event; it measures the share phi of late filings whose news became public only at the filing (lag-split model: phi about 0.5, event-day ratio 1.4 to 1.6; the lag-1 numbers suggest phi near 0.9 there and about 0.5 at lags 2 to 4); add the share of events with a 2x spike (mixture versus dampening).
 c. DECISION (item 3): whether to adopt a re-dated or two-sided day 0 (report date, filing date, acceptance window) for timing-dependent flags. Do not decide before a and b; do not re-run any flag before a decision is written. I may recommend against a single re-dated day 0.
 d. REMAINING G7 PROVEN FLAGS, each needing its own dated addendum BEFORE it runs: earnings_role_bands_walk_forward (earnings_role_band_test.py, MUST pin 63e08d84), event_earnings_window_width (earnings_thread_test.py; output results/2026-10-19/earnings_thread_full.out), event_label_direction_sign (direction_test.py on the frozen snapshot; check whether labels include excluded events), event_premium_20d (rebuild into a NEW table; the combining query and the events_ratio definition still not recovered), event_daily_range_coverage (not located). Then: the ledger evidence backfill and notes in one batch (backup flag_ledger_backup_20261029 exists), the ACTUAL-TABLE for the proven-flags PREREG and scripts/ops/score_predictions.py, README and docs/PROJECT_STATUS.md refresh (tables 166, entries 224).
 e. Mon 2026-11-02: October sentiment top-up (runbook step 8). After 2026-11-28: drop the eight backup and scratch tables listed in the 2026-10-29 checkpoint. January: results/JANUARY_2027_RUNBOOK.md (ingestion resumes before the forward tests at step 7; the new report-date script covers new filings with one request per company).

NOTES DEBT AT THIS CHECKPOINT: the flag_ledger table does not yet carry today's lag finding; the proven-flags ACTUAL-TABLE is not appended; README and STATUS are stale since 10-29; the SQL for event_premium_20d and event_daily_range_coverage is still missing; unresolved items from earlier: the 2003-09-15 FOMC row (needs build_fomc_calendar.py), the ADBE 2026-05-29 sec_filings row, why curated duplicates are absent from ev_ent.

CALIBRATION OF MY CHAT CALLS SINCE 10-29 (partial): hits: event and lag-1 counts, report-date coverage, linked-sample stop thresholds, the 5:30 PM rule check, the decision verdict (called supported at 50 percent), lag-0 rolled share under 3 percent. Misses: the same-day share of 8-Ks (called 84, actual 55), the start of the daily data (called -8 to -15, actual -5), the same-trading-day share of events (58 to 70, actual 39.7), acceptance windows (intraday called 33 to 52, actual 18), rolled share (called 35 percent, actual 5.9), the linked sample (11,150 against 9,500 to 10,800), the earnings same-day share. Pattern: I anchor on a remembered number from a small hand-picked set, or on a rule's wording instead of its volume. Before a call, run a base-rate query first.

STANDING RULES UNCHANGED: one step per block labelled FOREGROUND or SQL editor; SQL with $$ quoting through the linter and given inline; never guess a script's interface; new style (one paste block per file, hash-checked, changelog entry, commit and push with retries); every numeric prediction is a point, a range and an anchor and is scored; honest sample sizes.

COMMITS SINCE THE PREVIOUS CHECKPOINT (since 2026-10-29 16:22 +0000), from git log, objective:
  cfddac7 2026-10-30 14:38 event_timing created; its definition recorded as a file
  4c1c0d9 2026-10-30 14:32 G7: lag-split result saved (the 8-K filing lag explains most of the pre-window rise; SUPPORTED)
  d64c3dd 2026-10-30 14:28 G7: lag-split test of the pre-window candidate registered before any run
  dff440f 2026-10-30 14:23 sec_8k_report_dates created and loaded; the table definition recorded as a file
  004ee80 2026-10-30 14:17 8-K report dates pulled from the SEC feed: the lag between event and filing measured (45 percent late)
  6b9daf5 2026-10-30 13:52 G7 Tier 1: window nulls re-run saved (pre-window meets its rule: a candidate; lasting stays null)
  1e476b7 2026-10-30 13:43 G7 Tier 1 window nulls registered before any run; Addendum 6 corrects the sealed-ticker statement
  22cbc76 2026-10-30 13:36 G7 findings: ev_ent insulation, ratio_period and events_ratio recorded
  7611c35 2026-10-30 13:34 G7: event_day_width_own_events re-run saved (Arm 0 exact; Arm 1 changes about 10 event days; claim SUPPORTED)
  e126b4b 2026-10-30 13:26 G7 Addendum 5: event_day_width_own_events procedure registered before the run
  2c3fe75 2026-10-30 13:21 G7: band_edge_calibration_90 re-run saved (Arm 0 exact, Arm 1 negligible effect, all CALIBRATED)
  25b459a 2026-10-30 13:17 G7 Addendum 4a: failed first attempt, cause, fix and a new rule, recorded before the retry
  52550ee 2026-10-30 13:12 G7 Addendum 4: band_calibrate procedure registered before the run
  0e32a66 2026-10-29 16:22 G7 by-type run complete (steps 1 to 4 saved verbatim); stopping-point checkpoint 2026-10-29

UNCOMMITTED (git status --short):
  ?? results/tag_review_v1_galen.txt
<!-- CHECKPOINT-END -->
