"""
model_config.py

Single, shared source of truth for which Claude model the classification/
tagging scripts use. Every script that calls the Anthropic API should
import MODEL_VERSION from here instead of hardcoding its own string --
that way, upgrading models is a one-line change in this file, not a
grep-and-replace across the whole repo (which is exactly how the
scripts drifted onto an outdated model before this file existed).

Current model: Claude Haiku 5.5
  - $0.10 / $0.50 per million input/output tokens
  - 10x cheaper than Haiku 4.5 ($1.00 / $5.00) on both axes
  - Confirmed via Anthropic's own pricing page, 2026-10-08

To upgrade: change MODEL_VERSION below, then re-check
REAL_OBSERVED_COST_PER_FILING-style constants in individual scripts,
since actual per-task cost depends on real token counts, not just the
headline per-million rate.
"""

MODEL_VERSION = "claude-haiku-5-5"
