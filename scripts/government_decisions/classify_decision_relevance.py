"""
classify_decision_relevance.py

Real step 2 of the government_decisions relevance scoping (Galen,
2026-10-08): step 1 (populate_executive_orders.py, populate_enacted_laws.py)
ingested the raw, complete set of federal executive orders and
Congressional enacted laws with NO filtering. This script judges which
of those actually touch something that matters for a stock-research
database tracking real companies -- company/economic/health regulation,
budget/appropriations, trade, labor -- versus something with no real
economic relevance (a commemorative bill naming a post office, a
resolution honoring a sports team, a narrow symbolic action).

FOMC rows are NEVER sent here -- interest-rate decisions are relevant
by definition, always.

Reuses the proven batch-submission/polling/fetch infrastructure from
classify_8k_filings_batch_v2.py directly (via importlib, not
reimplemented) rather than risk a subtly different, unproven copy.

Real scale check before building: 7,992 real rows need review (1,570
EOs + 6,422 laws), just under MAX_BATCH_SIZE (8,000) -- fits in a
single real batch submission.

Writes back into government_decisions.structured_data (now a real,
correctly-typed jsonb object, not a double-encoded string -- see this
morning's fix) -- relevance_reviewed flips to true,
relevance_verdict ("relevant"/"not_relevant") and relevance_reasoning
are added.

Usage:
    python classify_decision_relevance.py --dry-run
    python classify_decision_relevance.py --live
"""
import os
import sys
import json
import importlib.util
from supabase import create_client

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from model_config import MODEL_VERSION

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ANTHROPIC_HEADERS = {
    "x-api-key": ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}

# Real reuse of the proven batch-submission/polling/fetch functions --
# import, don't reimplement.
spec = importlib.util.spec_from_file_location(
    "classify_8k_filings_batch_v2",
    os.path.join(os.path.dirname(__file__), "..", "classification", "classify_8k_filings_batch_v2.py"),
)
batch_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch_module)


def parse_relevance_result(raw_text):
    """Real, correct parser for THIS script's own simple schema --
    verdict/reasoning only, no confidence field, verdict in
    relevant/not_relevant. Does NOT reuse
    batch_module.parse_classification_result, which is hardcoded for
    the 8-K classifier's different schema (requires a confidence field,
    only accepts real_event/likely_noise/uncertain as valid verdicts) --
    confirmed the hard way: reusing it silently forced every real
    relevant/not_relevant verdict to "uncertain", corrupting an entire
    7,992-row write-back before being caught and fixed via a direct
    database spot-check."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return {"verdict": None, "reasoning": f"MALFORMED: {raw_text[:300]}"}
    return {"verdict": parsed.get("verdict"), "reasoning": parsed.get("reasoning")}

RELEVANCE_PROMPT = """You are screening a federal government decision (an \
executive order or an enacted law) for relevance to a stock-research \
database that tracks real, publicly-traded companies and their stock \
price reactions to real-world events.

RELEVANT means the decision plausibly touches: company regulation \
(any industry), economic policy, trade, taxation, labor/employment law, \
healthcare regulation, financial sector regulation, energy policy, \
appropriations/budget, or any other matter with a real, non-trivial \
economic or regulatory effect on businesses.

NOT RELEVANT means the decision is commemorative (naming a building, \
honoring a person/group/event), narrowly symbolic, a minor \
administrative/procedural matter with no real economic substance, or \
otherwise has no plausible connection to company regulation or \
economic conditions -- even if the topic sounds serious (e.g. most \
immigration, foreign policy, or social-issue bills with no economic \
regulation component are NOT relevant for this database's purpose).

When genuinely uncertain, lean NOT RELEVANT -- this database only wants \
decisions with a real, identifiable economic/regulatory angle, not \
anything tangentially governmental.

TITLE: {title}
BODY: {body}
DECISION TYPE: {decision_type}
POLICY AREA (if known): {policy_area}

Respond with ONLY valid JSON, no markdown code fences, no other text:
{{
  "verdict": "relevant" | "not_relevant",
  "reasoning": "<1-2 sentences>"
}}"""


def build_request(custom_id, title, body, decision_type, policy_area):
    prompt = RELEVANCE_PROMPT.format(
        title=title, body=body, decision_type=decision_type,
        policy_area=policy_area or "(none)",
    )
    return {
        "custom_id": custom_id,
        "params": {
            "model": MODEL_VERSION,
            "max_tokens": 300,
            "thinking": {"type": "disabled"},
            "messages": [{"role": "user", "content": prompt}],
        },
    }


def paginated(table, select, order_by, filters=None):
    rows, offset = [], 0
    while True:
        q = supabase.table(table).select(select).order(order_by)
        if filters:
            for f in filters:
                q = f(q)
        page = q.range(offset, offset + 999).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        offset += 1000
    return rows


def main():
    live = "--live" in sys.argv

    print("Fetching real government_decisions rows needing relevance review...")
    rows = paginated(
        "government_decisions",
        "id,title,body,decision_type,structured_data",
        "id",
        [lambda q: q.neq("decision_type", "interest_rate")],
    )
    to_review = [r for r in rows if not r["structured_data"].get("relevance_reviewed")]
    print(f"  {len(rows)} real non-FOMC rows total, {len(to_review)} need review.\n")

    if not to_review:
        print("Nothing to do.")
        return

    requests_list = []
    row_by_id = {}
    for r in to_review:
        custom_id = r["id"]
        policy_area = r["structured_data"].get("policy_area")
        req = build_request(custom_id, r["title"], r["body"], r["decision_type"], policy_area)
        requests_list.append(req)
        row_by_id[custom_id] = r

    print(f"{len(requests_list)} real requests prepared.")
    if not live:
        print("\nDRY RUN -- nothing submitted. Pass --live to submit.")
        print("Sample request:", json.dumps(requests_list[0], indent=2))
        return

    batch_module.ANTHROPIC_HEADERS = ANTHROPIC_HEADERS
    chunks = batch_module.chunk_list(requests_list, batch_module.MAX_BATCH_SIZE)
    print(f"Submitting {len(chunks)} real batch job(s)...")
    batch_ids = [batch_module.submit_batch(c) for c in chunks]
    final_batches = batch_module.poll_batches_until_all_done(batch_ids)

    import requests
    all_results = {}
    for batch_id, batch in final_batches.items():
        results_url = batch.get("results_url")
        if not results_url:
            print(f"  WARNING: batch {batch_id} has no results_url, skipping")
            continue
        resp = requests.get(results_url, headers=ANTHROPIC_HEADERS, timeout=60)
        resp.raise_for_status()
        for line in resp.text.strip().split("\n"):
            row = json.loads(line)
            custom_id = row["custom_id"]
            result = row["result"]
            if result["type"] != "succeeded":
                all_results[custom_id] = {"verdict": None, "reasoning": f"BATCH REQUEST FAILED: {result['type']}"}
                continue
            message = result["message"]
            text_blocks = [b["text"] for b in message["content"] if b.get("type") == "text"]
            if not text_blocks:
                block_types = [b.get("type") for b in message["content"]]
                all_results[custom_id] = {"verdict": None, "reasoning": f"EMPTY RESPONSE CONTENT: {block_types}"}
                continue
            all_results[custom_id] = parse_relevance_result(text_blocks[0])

    print(f"\n{len(all_results)} real results fetched. Writing back...")

    dist = {"relevant": 0, "not_relevant": 0, "error": 0}
    written = 0
    for custom_id, result in all_results.items():
        row = row_by_id.get(custom_id)
        if not row:
            continue
        verdict = result.get("verdict")
        reasoning = result.get("reasoning")
        if verdict not in ("relevant", "not_relevant"):
            dist["error"] += 1
            verdict = "relevant"  # real, deliberate safe default -- never silently drop a row from review scope on a parse failure
            reasoning = f"PARSE ERROR, defaulted to relevant for manual review: {result}"
        else:
            dist[verdict] += 1

        new_structured_data = dict(row["structured_data"])
        new_structured_data["relevance_reviewed"] = True
        new_structured_data["relevance_verdict"] = verdict
        new_structured_data["relevance_reasoning"] = reasoning

        supabase.table("government_decisions").update({
            "structured_data": new_structured_data
        }).eq("id", row["id"]).execute()
        written += 1
        if written % 500 == 0:
            print(f"  ...{written}/{len(all_results)} written")

    print(f"\nReal write complete: {written} rows updated.")
    print(f"Real relevance distribution: {dist}")


if __name__ == "__main__":
    main()
