"""patch_docs_ledger_repair.py (2026-10-29): brings THEORY.md (section 8) and docs/PROJECT_STATUS.md in line with the ledger repair of
2026-10-29 and the morning findings (ingestion paused since 2026-10-22). Both files are gated on their exact hashes; nothing is
written unless every replacement matches exactly once.  Usage: python3 scripts/audit/patch_docs_ledger_repair.py [THEORY.md] [docs/PROJECT_STATUS.md]"""
import hashlib, sys
def sha(s): return hashlib.sha256((s if s.endswith("\n") else s + "\n").encode("utf-8")).hexdigest()
tp = sys.argv[1] if len(sys.argv) > 1 else "THEORY.md"
sp = sys.argv[2] if len(sys.argv) > 2 else "docs/PROJECT_STATUS.md"
T = open(tp, encoding="utf-8").read(); S = open(sp, encoding="utf-8").read()
assert sha(T) == "2125cbeb70ede4110fe760c713c664f133b001e41adc357582fc6ead65b2a6ff", "THEORY is not the expected version; nothing changed"
assert sha(S) == "0bed0effca5a3cc13c15508de85a542d87cf93c61a20793b4745bfed0adbb542", "PROJECT_STATUS is not the expected v1.1; nothing changed"
def sub(text, old, new, label):
    n = text.count(old); assert n == 1, "%s: expected exactly 1 match, found %d; nothing was written" % (label, n); print("ok  ", label); return text.replace(old, new)

SEC8 = """## 8. Where the ledger is stale or disagrees

**Repaired 2026-10-29** (append-only notes, no status changed; backup table flag_ledger_backup_20261029, to be dropped after 2026-11-28; see CHANGELOG): `fed_state` (the Fed raised the target range on 2026-09-16 and the view correctly reads tightening), `news_sentiment_gdelt` (its note now points to the two GDELT tests of 2026-10-22 and the table sizes; it stays untested), `government_decisions_day_level` (FOMC days and executive orders have since been tested), the three "uses the pooled number" rows (rerun numbers added; each note now says what proven means there), and the three rows that cited the retired SCRIPTS.md.

**Still open:**
1. **"proven" for a type that only "uses the pooled number"** (`event_type_acquisition`, `event_type_leadership_change`, `event_type_strategic_partnership`) is a different claim from the substantive findings. Each note now says so, but the status vocabulary still hides it inside the count of 15. Changing it may affect code that reads the status values, so the decision waits for gate G7.
2. **`fomc_pre_announcement_drift`** is null although the historical effect replicated; its note already says "REPLICATES, FADED", so no edit was needed.
3. **`storm_tier_large`:** the evidence unit is inferred and the original result file was not found (stated in its evidence row).
4. **Duplicated sentences** remain in the notes of `earnings_surprise_sign_operating_income_forward` (a frozen forward-test row, left untouched on purpose) and `longhist_oil_shock_oil_industry` (cosmetic).
5. **The tag-significance audit has no ledger row.** Adding one needs the audit's primary numbers, which have not been re-read (gate G7).

"""
a = T.index("## 8. Where the ledger is stale or disagrees (to fix, not yet fixed)"); b = T.index("## 9. What would change this picture")
T2 = T[:a] + SEC8 + T[b:]; print("ok   THEORY section 8")
T2 = sub(T2, "the row is stale (Section 8)", "its note was updated 2026-10-29", "THEORY cell 1")
T2 = sub(T2, "the row is stale: two GDELT tests ran on 2026-10-22 (both null)", "its note now points to the two GDELT tests of 2026-10-22 (both null)", "THEORY cell 2")

S2 = sub(S, "# PROJECT STATUS (v1.1, 2026-10-28 evening)", "# PROJECT STATUS (v1.2, 2026-10-29)", "status title")
S2 = sub(S2, "| 1 Data Foundation | `[PENDING]` (G8) | unmeasured; known gaps: EA and AVB have no prices; 8-K predecessor-CIK gaps; pre-2004 8-K coverage unreliable |",
    "| 1 Data Foundation | `[PENDING]` (G8) | unmeasured; known gaps: EA and AVB have no prices; 8-K predecessor-CIK gaps; pre-2004 8-K coverage unreliable; **ingestion is paused since 2026-10-22 by decision (history-first plan): the nightly classification schedule is disabled, 8-Ks after 2026-09-18 and prices after 2026-10-13 are not loaded, only the daily news job runs; the price refresh is a manual script** [LIVE 10-29] |", "phase 1 row")
S2 = sub(S2, "(b) ten stale or inconsistent ledger rows (THEORY section 8: fed_state says easing but the Fed raised the target range on 2026-09-16; news_sentiment_gdelt is untested though two tests ran; three proven type rows carry first-run numbers; and others);",
    "(b) the ledger repair of 2026-10-29 fixed five of the ten stale rows (THEORY section 8 lists what was repaired and the five that remain, none urgent);", "inconsistency b")
S2 = sub(S2, "| after 2026-11-28 | drop the scratch and backup tables: fomc_meetings_backup_20261028, event_ripple_timeline_backup_20261028, scratch_diverged_new_20261028, scratch_diverged_v2_20261028 (G10) | CHANGELOG |",
    "| after 2026-11-28 | drop the scratch and backup tables: fomc_meetings_backup_20261028, event_ripple_timeline_backup_20261028, flag_ledger_backup_20261029, scratch_diverged_new_20261028, scratch_diverged_v2_20261028 (G10) | CHANGELOG |\n| before 2027-01-05 | the forward-test windows need ingestion resumed: 8-K item 2.02 filings dated 2026-10-14 to 2026-12-31 and prices after 2026-10-13 (the frozen file was written BEFORE either was loaded). `[PENDING]` find which January runbook step does this; the runbook text has not been read | results/FROZEN_role_band_forward_test_2026-10-22.md |", "calendar rows")
S2 = sub(S2, "*v1.1, 2026-10-28 evening. Update at the end of every session and add a CHANGELOG entry. Next revision: fill the `[PENDING]` slots (table inventory, Phase 1-4 gate checks), then G4, G5 and G7.*",
    "*v1.2, 2026-10-29. Update at the end of every session and add a CHANGELOG entry. Next revision: fill the `[PENDING]` slots (table inventory, Phase 1-4 gate checks, the runbook's ingestion step), then G4, G5 and G7.*", "footer")
open(tp, "w", encoding="utf-8").write(T2); open(sp, "w", encoding="utf-8").write(S2)
print("THEORY  sha256", sha(T2), "|", T2.count("\n"), "lines"); print("STATUS  sha256", sha(S2), "|", S2.count("\n"), "lines")