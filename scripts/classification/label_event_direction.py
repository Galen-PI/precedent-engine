#!/usr/bin/env python3
"""
label_event_direction.py -- labels the NEWS CONTENT of each company event as good / bad / mixed / unclear FOR THE COMPANY, from the event's
title and description only. The labeler never sees a price, a return or any outcome. Sentences that mention a stock or share-price move are
removed from the description before it is sent (the 'scrubbed' column records when that happened), so the labels cannot be circular.

Writes ONLY to a NEW table, event_direction_labels (nothing existing is changed). Create it first, once, in the SQL editor:

    CREATE TABLE IF NOT EXISTS event_direction_labels (
      event_id uuid PRIMARY KEY,
      entity_id uuid,
      ticker text,
      ptype text,
      event_date date,
      label text NOT NULL,
      size text,
      timing text,
      reasoning text,
      scrubbed boolean DEFAULT false,
      model text,
      prompt_version text,
      labeled_at timestamptz DEFAULT now()
    );

Events come from ev_ent (non-bundled company events with their sector; the first entity per event). Reuses the proven batch helpers of
classify_8k_filings_batch_v2.py (imported, not reimplemented), exactly as classify_decision_relevance.py does.

Usage:
    python3 label_event_direction.py                        dry run: counts, leakage check, cost estimate, one sample request
    python3 label_event_direction.py --pilot 300 --live     stratified pilot (by event type and era), then hand-read about 100 labels
    python3 label_event_direction.py --all --live           every event not yet labeled with this prompt version
    python3 label_event_direction.py --all --live --resume-batches ID1,ID2,...   collect the results of batches already submitted (no new submission)
"""
import os, sys, json, re, random, importlib.util

PROMPT_VERSION = "dir_v1"
LABELS = ("good", "bad", "mixed", "unclear")
SIZES = ("large", "moderate", "small", "unknown")
TIMINGS = ("new", "previously_announced", "unknown")
VERBS = r"(rose|fell|jumped|dropped|surged|plunged|climbed|declined|gained|slid|tumbled|rallied|sank|soared|slumped|tanked)"
PRICE_RE = re.compile(r"\b(shares?|stocks?)\b[^.]{0,60}\b" + VERBS + r"\b|\b" + VERBS + r"\b[^.]{0,40}\b(shares?|stocks?)\b|\bshare price\b|\bstock price\b", re.I)
IN_PRICE, OUT_PRICE = 0.10, 0.50       # USD per million tokens (claude-haiku-5-5, per model_config.py)

DIRECTION_PROMPT = """You are labeling the NEWS CONTENT of a corporate event for one company. Judge ONLY the business news described in \
the text: is it, by its content, good, bad, or mixed for the value of THIS company's shareholders, or can the direction not be told from the text?

Ignore any mention of a stock or share-price move, analyst reaction or market commentary, even if the text contains one. Do not guess how \
the market reacted.

COMPANY: {ticker} (sector: {sector})
EVENT CATEGORY (our own label): {ptype}
DATE: {date}
TITLE: {title}
DESCRIPTION: {description}

LABELS:
- good: the text describes something that raises this company's expected earnings, cash or strategic position, or removes a risk (for example a \
major contract win, an approval, a favorable settlement, a buyback or dividend increase, a financing on clearly good terms, being acquired at a premium).
- bad: the text describes something that lowers them (for example a charge or loss, a lost lawsuit, a guidance cut, a recall, a regulatory penalty, \
an abrupt executive exit under pressure, a default).
- mixed: material good and bad elements in the same event.
- unclear: the direction cannot be told from the text (routine or administrative items, or terms not given). When in doubt between a direction and \
unclear, choose unclear.

SIZE: how large the effect looks for a company of this kind, from the text only: large, moderate, small, or unknown.

TIMING: "previously_announced" if the text itself says this completes, follows through on, or is a scheduled step of something already announced \
or planned (for example the closing of a deal announced earlier, a scheduled payment or vote); "new" if it reports something not previously \
disclosed; "unknown" if the text does not say.

Respond with ONLY valid JSON, no markdown code fences, no other text:
{{
  "label": "good" | "bad" | "mixed" | "unclear",
  "size": "large" | "moderate" | "small" | "unknown",
  "timing": "new" | "previously_announced" | "unknown",
  "reasoning": "<1-2 sentences>"
}}"""


def get_sb():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


def load_batch():
    spec = importlib.util.spec_from_file_location("classify_8k_filings_batch_v2", os.path.join(os.path.dirname(os.path.abspath(__file__)), "classify_8k_filings_batch_v2.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def paginated(sb, table, cols, orders, filters=()):
    rows, off = [], 0
    while True:
        q = sb.table(table).select(cols)
        for f in filters:
            q = f(q)
        for o in orders:
            q = q.order(o)
        page = q.range(off, off + 999).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        off += 1000
    return rows


def scrub(text):
    """Remove sentences that mention a stock or share-price move. Returns (clean text, whether anything was removed)."""
    if not text:
        return "", False
    sents = re.split(r"(?<=[.!?])\s+", text.strip())
    kept = [s for s in sents if not PRICE_RE.search(s)]
    return " ".join(kept), len(kept) != len(sents)


def build_request(custom_id, ticker, sector, ptype, date, title, description, model):
    prompt = DIRECTION_PROMPT.format(ticker=ticker, sector=sector or "unknown", ptype=ptype, date=date, title=title, description=description or "(none)")
    return {"custom_id": custom_id, "params": {"model": model, "max_tokens": 250, "thinking": {"type": "disabled"},
                                               "messages": [{"role": "user", "content": prompt}]}}


def parse_result(raw_text):
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    try:
        p = json.loads(cleaned.strip())
    except json.JSONDecodeError:
        return {"label": None, "size": None, "reasoning": "MALFORMED: " + raw_text[:300]}
    label, size, timing = p.get("label"), p.get("size"), p.get("timing")
    if label not in LABELS:
        return {"label": None, "size": None, "reasoning": "BAD LABEL: " + str(p)[:300]}
    return {"label": label, "size": size if size in SIZES else "unknown", "timing": timing if timing in TIMINGS else "unknown", "reasoning": p.get("reasoning")}


def stratified(todo, n, seed=7):
    """n events, spread evenly over (event type, era) cells; era split at 2019-01-01."""
    rng = random.Random(seed)
    cells = {}
    for c in todo:
        cells.setdefault((c["ptype"], "B" if str(c["d"]) >= "2019-01-01" else "A"), []).append(c)
    for v in cells.values():
        rng.shuffle(v)
    out, keys = [], sorted(cells)
    while len(out) < n and any(cells[k] for k in keys):
        for k in keys:
            if cells[k] and len(out) < n:
                out.append(cells[k].pop())
    return out


def main():
    live = "--live" in sys.argv
    pilot = int(sys.argv[sys.argv.index("--pilot") + 1]) if "--pilot" in sys.argv else None
    do_all = "--all" in sys.argv
    resume_ids = sys.argv[sys.argv.index("--resume-batches") + 1].split(",") if "--resume-batches" in sys.argv else None
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shared"))
    from model_config import MODEL_VERSION
    sb = get_sb()

    secs = {r["entity_id"]: r for r in paginated(sb, "securities", "entity_id,ticker,sector", ["entity_id"])}
    raw = paginated(sb, "ev_ent", "event_id,entity_id,sector,d,ptype,gov", ["event_id", "entity_id"])
    first = {}
    for r in raw:
        first.setdefault(r["event_id"], r)
    cands = list(first.values())
    done = {r["event_id"] for r in paginated(sb, "event_direction_labels", "event_id,prompt_version", ["event_id"]) if r.get("prompt_version") == PROMPT_VERSION}
    todo = [c for c in cands if c["event_id"] not in done]
    print("events in ev_ent: %d | already labeled with %s: %d | to label: %d" % (len(cands), PROMPT_VERSION, len(done), len(todo)), flush=True)
    if not todo:
        print("Nothing to do.")
        return

    if pilot:
        chosen = stratified(todo, pilot)
    elif do_all:
        chosen = todo
    else:
        chosen = random.Random(3).sample(todo, min(300, len(todo)))
    texts = {}
    ids = [c["event_id"] for c in chosen]
    for i in range(0, len(ids), 100):
        for r in sb.table("events").select("id,title,description").in_("id", ids[i:i + 100]).execute().data:
            texts[r["id"]] = r

    reqs, meta, n_scrub, n_title_price, chars = [], {}, 0, 0, 0
    for c in chosen:
        t = texts.get(c["event_id"])
        if not t or not t.get("title"):
            continue
        desc, was = scrub((t.get("description") or "")[:1500])
        n_scrub += was
        n_title_price += bool(PRICE_RE.search(t["title"]))
        s = secs.get(c["entity_id"], {})
        req = build_request(c["event_id"], s.get("ticker") or "(unknown)", s.get("sector") or c.get("sector"), c["ptype"], c["d"], t["title"], desc, MODEL_VERSION)
        reqs.append(req)
        chars += len(req["params"]["messages"][0]["content"])
        meta[c["event_id"]] = (c, was)
    n = len(reqs)
    est_in = chars / 4.0
    est_cost = (est_in * IN_PRICE + n * 90 * OUT_PRICE) / 1e6
    print("%d requests prepared | descriptions with a price-move sentence removed: %d (%.1f%%) | titles that mention a price move: %d" % (
        n, n_scrub, 100.0 * n_scrub / max(1, n), n_title_price))
    print("approximate cost of this set: $%.2f (about %.0f input tokens per request)" % (est_cost, est_in / max(1, n)))
    if not live:
        print("\nDRY RUN -- nothing submitted. Pass --pilot N --live or --all --live.")
        print("Sample request:\n" + json.dumps(reqs[0], indent=2)[:2500])
        return
    if not (pilot or do_all):
        sys.exit("Live runs need --pilot N or --all.")

    import requests
    bm = load_batch()
    hdr = {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01", "content-type": "application/json"}
    bm.ANTHROPIC_HEADERS = hdr
    if resume_ids:
        # RECOVERY: submit nothing; read the results of batches that already exist at Anthropic (same --pilot/--all selection as the original run)
        print("RESUMING: submitting nothing; reading the results of %d existing batch(es)." % len(resume_ids), flush=True)
        batch_ids = resume_ids
    else:
        chunks = bm.chunk_list(reqs, bm.MAX_BATCH_SIZE)
        print("Submitting %d batch job(s)..." % len(chunks), flush=True)
        batch_ids = [bm.submit_batch(c) for c in chunks]
        print("BATCH IDS (the recovery handle; save them): " + ",".join(batch_ids), flush=True)
    final = bm.poll_batches_until_all_done(batch_ids)

    results = {}
    for bid, batch in final.items():
        url = batch.get("results_url")
        if not url:
            print("  WARNING: batch %s has no results_url, skipping" % bid)
            continue
        resp = requests.get(url, headers=hdr, timeout=60)
        resp.raise_for_status()
        for line in resp.text.strip().split("\n"):
            row = json.loads(line)
            cid, res = row["custom_id"], row["result"]
            if res["type"] != "succeeded":
                results[cid] = {"label": None, "size": None, "reasoning": "BATCH REQUEST FAILED: " + str(res["type"])}
                continue
            blocks = [b["text"] for b in res["message"]["content"] if b.get("type") == "text"]
            results[cid] = parse_result(blocks[0]) if blocks else {"label": None, "size": None, "reasoning": "EMPTY RESPONSE CONTENT"}
    print("\n%d results fetched. Writing to event_direction_labels..." % len(results), flush=True)

    rows_out, bad = [], []
    dist, by_type, tdist = {}, {}, {}
    for cid, r in results.items():
        if cid not in meta:
            continue
        c, was = meta[cid]
        if r["label"] is None:
            bad.append((cid, r["reasoning"]))
            continue
        dist[r["label"]] = dist.get(r["label"], 0) + 1
        tdist[r.get("timing")] = tdist.get(r.get("timing"), 0) + 1
        by_type.setdefault(c["ptype"], {}).setdefault(r["label"], 0)
        by_type[c["ptype"]][r["label"]] += 1
        rows_out.append({"event_id": cid, "entity_id": c["entity_id"], "ticker": (secs.get(c["entity_id"], {}) or {}).get("ticker"), "ptype": c["ptype"],
                         "event_date": c["d"], "label": r["label"], "size": r["size"], "timing": r.get("timing"), "reasoning": r["reasoning"], "scrubbed": was,
                         "model": MODEL_VERSION, "prompt_version": PROMPT_VERSION})
    for i in range(0, len(rows_out), 200):
        sb.table("event_direction_labels").upsert(rows_out[i:i + 200], on_conflict="event_id").execute()
    print("Written: %d rows. Not written (malformed or failed): %d" % (len(rows_out), len(bad)))
    for cid, why in bad[:5]:
        print("   ", cid, why[:140])
    print("Label distribution: %s | timing: %s" % (dist, tdist))
    for t, d in sorted(by_type.items(), key=lambda kv: -sum(kv[1].values()))[:12]:
        print("   %-24s %s" % (t, d))


if __name__ == "__main__":
    main()
