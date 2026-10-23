#!/usr/bin/env python3
"""
tag_government_decisions.py -- tags the RELEVANT government decisions into the vocabulary buckets of results/government_tag_vocabulary_v1.md (sectors, themes, scope, persistence), from their stored SOURCE TEXT (government_decision_text), through the same Anthropic batch infrastructure as classify_decision_relevance.py.
GUARDS (all from the registered vocabulary): every sector and theme tag needs a quote of 3-25 words that must be FOUND in the text the model was shown (a tag whose quote is not found is dropped, never written); a text with no source text is tagged at confidence 'low' with no sector tags; a summary of a bill AS INTRODUCED caps confidence at 'medium'; an omnibus law (title Consolidated/Continuing/Omnibus Appropriations, or 8+ Divisions) is scope market_wide with no sector tags; a decision scoped not_company_relevant gets no sector tags; this script has its OWN parser (the 8-K parser once silently turned every verdict into 'uncertain'); a parse failure writes NOTHING for that decision (recorded in the runs table, retried next run), never a guessed tag.
Tables (see the DO block in the instructions): government_decision_tags (one row per decision, bucket_type, bucket, vocab_version) and government_decision_tag_runs (one row per decision and vocab_version: status ok | partial | invalid | parse_error | failed).
Usage:   python3 -u scripts/government_decisions/tag_government_decisions.py                       dry run: counts, a sample prompt, nothing submitted
         python3 -u scripts/government_decisions/tag_government_decisions.py --pilot 12 --live      submits 12 stratified decisions, PRINTS every result for hand reading, writes nothing
         python3 -u scripts/government_decisions/tag_government_decisions.py --live --apply         everything not yet tagged under this vocabulary version
"""
import os, sys, re, json, random, argparse, datetime, importlib.util, types, collections

VOCAB = "v1"
PROMPT_VERSION = "v1.2"
SECTORS = ("Communication Services", "Consumer Discretionary", "Consumer Staples", "Energy", "Financials", "Health Care", "Industrials", "Information Technology", "Materials", "Real Estate", "Utilities")
THEMES = ("trade_tariffs", "sanctions_foreign_policy", "taxation", "budget_appropriations", "financial_regulation", "banking_monetary", "healthcare_drug_pricing", "environment_climate", "energy_policy", "technology_ai_data", "telecom_media", "labor_employment", "antitrust_competition", "defense_procurement", "housing_real_estate", "immigration", "agriculture_food", "transportation_infrastructure", "consumer_protection", "government_operations")
SCOPES = ("market_wide", "sector_specific", "company_specific", "not_company_relevant")
PERSIST = ("one_off", "persistent_condition")
DIRECTIONS = ("benefit", "harm", "mixed", "unclear")
CONFS = ("high", "medium", "low")
PA_THEME = {"Agriculture and Food": "agriculture_food", "Armed Forces and National Security": "defense_procurement", "Commerce": "consumer_protection", "Congress": "government_operations", "Crime and Law Enforcement": "government_operations", "Economics and Public Finance": "budget_appropriations", "Education": "government_operations", "Emergency Management": "government_operations", "Energy": "energy_policy", "Environmental Protection": "environment_climate", "Families": "government_operations", "Finance and Financial Sector": "financial_regulation", "Foreign Trade and International Finance": "trade_tariffs", "Government Operations and Politics": "government_operations", "Health": "healthcare_drug_pricing", "Housing and Community Development": "housing_real_estate", "Immigration": "immigration", "International Affairs": "sanctions_foreign_policy", "Labor and Employment": "labor_employment", "Law": "government_operations", "Native Americans": "government_operations", "Public Lands and Natural Resources": "environment_climate", "Science, Technology, Communications": "technology_ai_data", "Social Welfare": "government_operations", "Taxation": "taxation", "Transportation and Public Works": "transportation_infrastructure", "Water Resources Development": "transportation_infrastructure"}
WEAK_PA = {"Commerce", "Education", "Families", "Public Lands and Natural Resources"}
WHOLE_MAX, HEAD_CHARS, MAX_HEADINGS, THIN_MAX = 6000, 5000, 60, 300
DONE = ("ok", "partial", "invalid")

PROMPT = """You are tagging a US federal government decision (an enacted law or an executive order) for a stock-research database. The tags are used to find which sectors and themes a decision touches. Read ONLY the text supplied below; do not use outside knowledge about the decision.

DECISION TYPE: {{TYPE}}
TITLE: {{TITLE}}
CONGRESS.GOV POLICY AREA (laws only): {{PA}}
TEXT KIND: {{KIND}}
{{FEED}}

CONTROLLED VOCABULARY (use these exact strings):
SECTORS: {{SECTORS}}
THEMES, with what each one means (choose a theme only if its meaning applies; a shared word is not enough):
- trade_tariffs: tariffs, duties, quotas, import or export controls, trade agreements on goods
- sanctions_foreign_policy: sanctions, blocking of property, national emergencies against foreign parties, foreign aid, diplomatic measures
- taxation: taxes, credits, deductions, tax administration
- budget_appropriations: government spending, appropriations, authorizations of funds, the debt limit
- financial_regulation: regulation of banks, securities, insurance, lending and capital-market participants
- banking_monetary: central banking, money, payments, deposit insurance, the Federal Reserve
- healthcare_drug_pricing: health care delivery, health insurance, drugs, devices, medical programs
- environment_climate: pollution, emissions, climate, wildlife, protection of land and water
- energy_policy: oil, gas, coal, power, renewables, fuel and efficiency standards
- technology_ai_data: software, AI, data, cybersecurity, semiconductors, internet platforms
- telecom_media: telephone, broadband, spectrum, broadcasting, media
- labor_employment: private-sector wages, unions, workplace rules, hiring, employment benefits for workers (rules about the federal civil service are government_operations)
- antitrust_competition: mergers, market concentration, competition enforcement
- defense_procurement: military spending, weapons, defense contracts (civilian federal procurement and contracting preferences are government_operations)
- housing_real_estate: housing, mortgages, real estate, home construction
- immigration: visas, borders, immigration rules
- agriculture_food: farms, crops, food safety, nutrition programs
- transportation_infrastructure: roads, rail, aviation, shipping, ports, water infrastructure
- consumer_protection: rules protecting consumers in the marketplace (disclosure, fraud, product safety, pricing practices)
- government_operations: the government's own administration, federal personnel and hiring, civilian procurement, advisory bodies, procedure and organization
SCOPE: market_wide | sector_specific | company_specific | not_company_relevant
PERSISTENCE: one_off | persistent_condition
DIRECTION (of the effect on the sector's companies overall): benefit | harm | mixed
CONFIDENCE: high | medium | low

RULES:
1. scope: market_wide = affects businesses broadly (taxes, government-wide appropriations, broad regulation, trade policy across many goods); sector_specific = the text itself names an industry, a product or a type of company that is chiefly affected (for example banks, drug makers, air carriers) AND you can support at least one sector with a quote; rules that apply to all employers, all federal agencies or all contractors are market_wide; company_specific = names a particular company; not_company_relevant = commemorative, symbolic, procedural, internal government administration, personnel or advisory bodies, or anything with no plausible effect on companies.
2. persistence: persistent_condition = sets a standing rule, tax, tariff, program or regulatory condition, or permanently changes or ends one, that stays in force until changed; one_off = fixed-term or single-year funding (annual appropriations or an authorization for one fiscal year), a single payment, a one-time action, or a short extension or delay.
3. themes: 1 to 3 themes. Each needs a QUOTE: a phrase of 3 to 25 words copied EXACTLY, character for character, from the text above, that supports the theme. A quote longer than 25 words is invalid: count the words.
4. sectors: 0 to 4 sectors whose economics the decision plausibly changes. Each needs a direction (benefit, harm or mixed: if you cannot tell, omit the sector) and a QUOTE (3 to 25 words) copied exactly from the text above, and the quote must name or describe that sector's own activity: if it would apply equally to any business, do not tag the sector.
5. confidence: high if the text states the effect plainly; medium if you must infer part of it; low if the text is thin, partial, or describes only an earlier version of a bill.
6. If the text is marked PARTIAL you see only the start of a long text plus a list of its headings: tag only what you can support from what you see.

Respond with ONLY valid JSON, no markdown code fences, no other text:
{"scope": "...", "persistence": "...", "themes": [{"theme": "...", "quote": "..."}], "sectors": [{"sector": "...", "direction": "...", "quote": "..."}], "confidence": "...", "note": "<= 20 words"}"""

HEAD_RE = re.compile(r"\b(Division|Title)\s+([A-Z]{1,2}|[IVXLC]{1,6}|\d{1,3})\s*:\s*(.{3,170}?)(?:\s+-\s|\s+(?=(?:Division|Title)\s+(?:[A-Z]{1,2}|[IVXLC]{1,6}|\d{1,3})\s*:))")
SEC_RE = re.compile(r"\bSec(?:tion)?\.?\s+(\d{1,2})\.\s+([A-Z][A-Za-z ,'\-]{2,80}?)\.")


def norm(s):
    s = (s or "").replace("\u201c", '"').replace("\u201d", '"').replace("\u2018", "'").replace("\u2019", "'").replace("``", '"').replace("''", '"').replace("\u2013", "-").replace("\u2014", "-")
    return " ".join(s.lower().split())


def extract_headings(body, is_order):
    seen, out = set(), []
    for m in (SEC_RE if is_order else HEAD_RE).finditer(body or ""):
        h = ("Sec. %s: %s" % (m.group(1), m.group(2))) if is_order else ("%s %s: %s" % (m.group(1), m.group(2), " ".join(m.group(3).split())))
        if h not in seen:
            seen.add(h)
            out.append(h)
        if len(out) >= MAX_HEADINGS:
            break
    return out


def omnibus_title(title):
    return bool(re.search(r"\b(consolidated|continuing|omnibus)\b[^.]{0,60}\bappropriations\b", title or "", re.I))


def is_omnibus(title, body):
    return omnibus_title(title) or len(set(re.findall(r"\bDivision\s+([A-Z]{1,2})\s*:", body or ""))) >= 8


def version_desc(note):
    """the CRS summary version stored by fetch_decision_text.py: 'version 49 | Public Law | 2014-08-07 | ...' -> 'Public Law'"""
    parts = (note or "").split(" | ")
    return parts[1] if len(parts) > 1 and parts[0].startswith("version") else None


def is_nonfinal(d, note):
    """a law whose stored summary is NOT the Public Law version (Introduced, Passed House amended, Reported...) may differ from the law as enacted"""
    v = version_desc(note)
    return d["decision_type"] == "enacted_law" and v is not None and v != "Public Law"


def build_feed(body, is_order):
    """returns (kind, shown_text, prompt_block): kind is title_only | full | partial"""
    if not body or not body.strip():
        return "title_only", "", "(no source text is available: only the title and policy area)"
    if len(body.strip()) < THIN_MAX:
        return "thin", body, "<text>\n%s\n</text>" % body
    if len(body) <= WHOLE_MAX:
        return "full", body, "<text>\n%s\n</text>" % body
    head = body[:HEAD_CHARS]
    head = head[:head.rfind(" ")] if " " in head[-60:] else head
    heads = extract_headings(body, is_order)
    block = "<text>\n%s\n</text>\nHEADINGS FROM THE FULL TEXT (%d shown; the full text has %d characters):\n%s" % (head, len(heads), len(body), "\n".join("- " + h for h in heads) or "- (none found)")
    return "partial", head + "\n" + "\n".join(heads), block


def build_prompt(d, kind, block, note):
    label = {"full": "FULL TEXT", "partial": "PARTIAL: only the start of a long text plus its headings", "title_only": "TITLE ONLY", "thin": "VERY SHORT TEXT (too thin to judge company relevance reliably)"}[kind]
    if is_nonfinal(d, note):
        label += " (NOTE: this summary describes an EARLIER VERSION of the bill, '%s', which may differ from the law as enacted)" % version_desc(note)
    return (PROMPT.replace("{{TYPE}}", d["decision_type"]).replace("{{TITLE}}", d.get("title") or "").replace("{{PA}}", d["sd"].get("policy_area") or "(none)")
            .replace("{{KIND}}", label).replace("{{FEED}}", block).replace("{{SECTORS}}", ", ".join(SECTORS)).replace("{{THEMES}}", ", ".join(THEMES)))


def parse_tag_result(raw):
    """this script's OWN parser (never the 8-K parser): returns a dict or None"""
    t = (raw or "").strip()
    if t.startswith("```"):
        t = t.split("```")[1]
        if t.startswith("json"):
            t = t[4:]
    try:
        p = json.loads(t.strip())
    except ValueError:
        i, k = t.find("{"), t.rfind("}")   # prose before or after the JSON: take the outermost braces (still strict JSON; no value is guessed)
        if i < 0 or k <= i:
            return None
        try:
            p = json.loads(t[i:k + 1])
        except ValueError:
            return None
    return p if isinstance(p, dict) else None


def quote_check(q, seen):
    """returns (problem, evidence): a quote of 3 to 60 words that is FOUND in the text shown is verified; the evidence stored is its first 25 words (the start of an exact quote is itself exact)"""
    if not isinstance(q, str):
        return "no quote", None
    w = q.split()
    if len(w) < 3:
        return "quote under 3 words", None
    if len(w) > 60:
        return "quote over 60 words", None
    if norm(q) not in seen:
        return "quote not found in the text shown", None
    return None, " ".join(w[:25])


def validate(p, shown_text, kind, omnibus, intro_only, force_one_off=False):
    """returns None if the core (scope, persistence, at least one theme) is unusable, else {status, rows, dropped, confidence}"""
    seen, dropped, rows = norm(shown_text), [], []
    scope, pers = p.get("scope"), p.get("persistence")
    if scope not in SCOPES or pers not in PERSIST:
        return {"status": "invalid", "rows": [], "dropped": ["scope or persistence not in the vocabulary: %r, %r" % (scope, pers)], "confidence": None}
    if omnibus:
        scope = "market_wide"
    if force_one_off:
        pers = "one_off"   # an annual omnibus or continuing appropriations law (identified by its title) is fixed-term funding
    themes = []
    for t in (p.get("themes") if isinstance(p.get("themes"), list) else []):
        if not isinstance(t, dict) or t.get("theme") not in THEMES:
            dropped.append("theme %r not in the vocabulary" % (t.get("theme") if isinstance(t, dict) else t))
            continue
        why, ev = quote_check(t.get("quote"), seen)
        if why:
            dropped.append("theme %s: %s" % (t["theme"], why))
        elif t["theme"] not in [x[0] for x in themes]:
            themes.append((t["theme"], ev))
    if len(themes) > 3:
        dropped.append("themes beyond the third dropped: %s" % [x[0] for x in themes[3:]])
        themes = themes[:3]
    if omnibus and "budget_appropriations" not in [x[0] for x in themes]:
        themes.append(("budget_appropriations", "RULE: omnibus appropriations law (title or 8+ divisions)"))
    if not themes:
        return {"status": "invalid", "rows": [], "dropped": dropped + ["no theme with a verifiable quote"], "confidence": None}
    sectors = []
    sec_in = p.get("sectors") if isinstance(p.get("sectors"), list) else []
    if kind in ("title_only", "thin") or omnibus or scope == "not_company_relevant":
        if sec_in:
            dropped.append("sector tags dropped by rule (%s)" % ("title only" if kind == "title_only" else "text under %d characters" % THIN_MAX if kind == "thin" else "omnibus law" if omnibus else "not_company_relevant"))
    else:
        for s in sec_in:
            if not isinstance(s, dict) or s.get("sector") not in SECTORS or s.get("direction") not in DIRECTIONS:
                dropped.append("sector entry not in the vocabulary: %r" % (s,))
                continue
            if s.get("direction") == "unclear":
                dropped.append("sector %s: direction unclear (a sector tag needs benefit, harm or mixed)" % s["sector"])
                continue
            why, ev = quote_check(s.get("quote"), seen)
            if why:
                dropped.append("sector %s: %s" % (s["sector"], why))
            elif s["sector"] not in [x[0] for x in sectors]:
                sectors.append((s["sector"], s["direction"], ev))
        if len(sectors) > 4:
            dropped.append("sectors beyond the fourth dropped")
            sectors = sectors[:4]
    if scope == "sector_specific" and not sectors:
        dropped.append("scope sector_specific but no sector survived the checks")
    conf = p.get("confidence") if p.get("confidence") in CONFS else "low"
    if kind in ("title_only", "thin"):
        conf = "low"
    elif intro_only and conf == "high":
        conf = "medium"
    if kind == "partial" and scope == "not_company_relevant" and conf != "low":
        conf = "low"
        dropped.append("scope not_company_relevant rests on a partial text: confidence set to low")
    if kind == "thin":
        dropped.append("scope not written: the text is under %d characters, so company relevance is unassessed" % THIN_MAX)
    else:
        rows.append({"bucket_type": "scope", "bucket": scope, "direction": None, "evidence": (p.get("note") or "")[:200] or None, "quote_verified": None})
    rows.append({"bucket_type": "persistence", "bucket": pers, "direction": None, "evidence": None, "quote_verified": None})
    rows += [{"bucket_type": "theme", "bucket": t, "direction": None, "evidence": q, "quote_verified": not q.startswith("RULE:")} if not q.startswith("RULE:") else {"bucket_type": "theme", "bucket": t, "direction": None, "evidence": q, "quote_verified": None} for t, q in themes]
    rows += [{"bucket_type": "sector", "bucket": s, "direction": d, "evidence": q, "quote_verified": True} for s, d, q in sectors]
    return {"status": "partial" if dropped else "ok", "rows": rows, "dropped": dropped, "confidence": conf}


def load_infra():
    from supabase import create_client
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(here, "..", "shared"))
    from model_config import MODEL_VERSION
    headers = {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01", "content-type": "application/json"}
    spec = importlib.util.spec_from_file_location("classify_8k_filings_batch_v2", os.path.join(here, "..", "classification", "classify_8k_filings_batch_v2.py"))
    bm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bm)
    bm.ANTHROPIC_HEADERS = headers
    import requests
    return types.SimpleNamespace(sb=create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"]), batch=bm, headers=headers, model=MODEL_VERSION, http_get=requests.get)


def paged(sb, table, cols, order, size=1000):
    out, off = [], 0
    while True:
        page = sb.table(table).select(cols).order(order).range(off, off + size - 1).execute().data
        if not page:
            break
        out += page
        if len(page) < size:
            break
        off += size
    return out


def sd_of(r):
    sd = r.get("structured_data")
    if isinstance(sd, str):
        try:
            sd = json.loads(sd)
        except ValueError:
            return {}
    return sd if isinstance(sd, dict) else {}


def era_of(d):
    y = int(str(d.get("decision_date") or "0000")[:4] or 0)
    return "<=2004" if y <= 2004 else "2005-2014" if y <= 2014 else ">=2015"


def pilot_pick(items, n, seed=20261023):
    rng, groups = random.Random(seed), collections.defaultdict(list)
    for d in items:
        groups[(d["decision_type"], era_of(d))].append(d)
    keys = sorted(groups)
    for k in keys:
        rng.shuffle(groups[k])
    out, i = [], 0
    while len(out) < n and any(groups[k] for k in keys):
        k = keys[i % len(keys)]
        if groups[k]:
            out.append(groups[k].pop())
        i += 1
    return out


def main(argv=None, infra=None):
    """runs _main under the vocabulary label given by --label (default v1), then restores the module default"""
    global VOCAB
    saved = VOCAB
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--label", default="")
    lab = pre.parse_known_args(argv)[0].label
    try:
        if lab:
            VOCAB = lab
        return _main(argv, infra)
    finally:
        VOCAB = saved


def _main(argv=None, infra=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="", help="write under this vocabulary label instead of v1 (for example v1_rerun: a repeat of the same prompt, kept apart from the main tags)")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--pilot", type=int, default=0)
    ap.add_argument("--seed", type=int, default=20261023, help="pilot sample seed (a different seed gives a fresh stratified sample)")
    ap.add_argument("--allow-waiting", action="store_true", help="let --live run while some decisions are still waiting for source text")
    ap.add_argument("--include-submitted", action="store_true", help="also resubmit decisions that are marked as already in a submitted batch")
    ap.add_argument("--collect", default="", help="comma-separated ids of batches ALREADY submitted: fetch their results instead of submitting a new batch (recovery after a dropped session)")
    a = ap.parse_args(argv)
    if a.apply and not a.live:
        ap.error("--apply needs --live")
    if a.apply and a.pilot:
        ap.error("a pilot never writes: drop --pilot or --apply")
    if a.collect and not a.live:
        ap.error("--collect needs --live")
    infra = infra or load_infra()
    sb = infra.sb
    decs = [r for r in paged(sb, "government_decisions", "id,title,decision_type,decision_date,structured_data", "id") if r["decision_type"] in ("enacted_law", "executive_order") and sd_of(r).get("relevance_verdict") == "relevant"]
    for r in decs:
        r["sd"] = sd_of(r)
        r["id"] = str(r["id"])
    texts = {str(t["decision_id"]): t for t in paged(sb, "government_decision_text", "decision_id,status,note,body", "decision_id", 200)}
    run_state = [r for r in paged(sb, "government_decision_tag_runs", "decision_id,vocab_version,status", "decision_id") if r["vocab_version"] == VOCAB]
    submitted = {str(r["decision_id"]) for r in run_state if r["status"] == "submitted"}
    # --collect is authoritative for the decisions in the named batches, whatever their earlier status; otherwise finished AND submitted decisions are skipped
    done = set() if a.collect else {str(r["decision_id"]) for r in run_state if r["status"] in DONE or (r["status"] == "submitted" and not a.include_submitted)}
    todo = [d for d in decs if d["id"] not in done]
    # only decisions whose source text has been fetched (status ok or no_text) are taggable: a decision whose text row is missing or errored is WAITING, never tagged as 'title only' (an 'invalid' run counts as done and would never be retried)
    waiting = [d for d in todo if (texts.get(d["id"]) or {}).get("status") not in ("ok", "no_text")]
    todo = [d for d in todo if (texts.get(d["id"]) or {}).get("status") in ("ok", "no_text")]
    if a.pilot:
        todo = pilot_pick([d for d in todo if d["id"] in texts], a.pilot, a.seed)
    reqs, meta = [], {}
    for d in todo:
        t = texts.get(d["id"]) or {}
        body = t.get("body") if t.get("status") == "ok" else None
        kind, shown, block = build_feed(body, d["decision_type"] == "executive_order")
        note = t.get("note") or ""
        meta[d["id"]] = {"d": d, "kind": kind, "shown": shown, "omnibus": is_omnibus(d.get("title"), body), "omni_title": omnibus_title(d.get("title")), "intro": is_nonfinal(d, note), "desc": version_desc(note), "chars": len(shown)}
        reqs.append({"custom_id": d["id"], "params": {"model": infra.model, "max_tokens": 1000, "thinking": {"type": "disabled"}, "messages": [{"role": "user", "content": build_prompt(d, kind, block, note)}]}})
    kinds = collections.Counter(m["kind"] for m in meta.values())
    print("relevant decisions %d | already tagged or submitted (%s) %d (of which in a submitted batch %d) | waiting for source text %d | to tag %d | input kinds %s | omnibus by rule %d | non-final version only %d | %s" % (len(decs), VOCAB, len(done), len(submitted & done), len(waiting), len(todo), dict(kinds), sum(m["omnibus"] for m in meta.values()), sum(m["intro"] for m in meta.values()), "LIVE" if a.live else "DRY RUN"), flush=True)
    if not reqs:
        return {}
    if not a.live:
        print("DRY RUN: nothing submitted. About %d input tokens in total (characters / 4). Sample prompt:\n%s" % (sum(len(r["params"]["messages"][0]["content"]) for r in reqs) // 4, reqs[0]["params"]["messages"][0]["content"][:3500]))
        return {}
    if waiting and not (a.collect or a.pilot or a.allow_waiting):
        print("REFUSING to run live: %d decisions are still waiting for their source text (the text job is not finished). Run again when it is, or pass --allow-waiting to tag only the others now." % len(waiting))
        return {}
    bm = infra.batch
    if a.collect:
        ids = [x.strip() for x in a.collect.split(",") if x.strip()]
        print("Collecting the results of %d already-submitted batch(es): %s" % (len(ids), ids), flush=True)
    else:
        chunks = bm.chunk_list(reqs, bm.MAX_BATCH_SIZE)
        print("Submitting %d batch job(s)..." % len(chunks), flush=True)
        ids = [bm.submit_batch(c) for c in chunks]
        print("BATCH IDS (keep them: if this session dies before the tags are written, rerun with   --collect %s --live --apply  ): %s" % (",".join(ids), ids), flush=True)
        if a.apply:
            marks = [{"decision_id": c, "vocab_version": VOCAB, "status": "submitted", "n_tags": 0, "raw_response": ",".join(ids)[:300], "input_kind": m["kind"], "input_chars": m["chars"], "model_version": infra.model, "prompt_version": PROMPT_VERSION} for c, m in meta.items()]
            for i in range(0, len(marks), 500):
                sb.table("government_decision_tag_runs").upsert(marks[i:i + 500], on_conflict="decision_id,vocab_version").execute()
            print("marked %d decisions as submitted (a second run will skip them)" % len(marks), flush=True)
    final = bm.poll_batches_until_all_done(ids)
    raw = {}
    for bid, b in final.items():
        if not b.get("results_url"):
            print("  WARNING: batch %s has no results_url" % bid)
            continue
        resp = infra.http_get(b["results_url"], headers=infra.headers, timeout=60)
        resp.raise_for_status()
        for line in resp.text.strip().split("\n"):
            row = json.loads(line)
            res = row["result"]
            if res["type"] != "succeeded":
                raw[row["custom_id"]] = ("failed", "BATCH REQUEST FAILED: %s" % res["type"])
                continue
            blocks = [x["text"] for x in res["message"]["content"] if x.get("type") == "text"]
            raw[row["custom_id"]] = ("ok", blocks[0]) if blocks else ("failed", "EMPTY RESPONSE CONTENT")
    if a.collect:
        meta = {c: m for c, m in meta.items() if c in raw}   # only the decisions that were in the collected batches
        print("collected results for %d decisions" % len(meta), flush=True)
    tag_rows, run_rows, tally = [], [], collections.Counter()
    themes_c, sectors_c, scope_c, agree = collections.Counter(), collections.Counter(), collections.Counter(), [0, 0]
    for cid, m in meta.items():
        d, (how, text) = m["d"], raw.get(cid, ("failed", "NO RESULT RETURNED"))
        parsed = parse_tag_result(text) if how == "ok" else None
        v = validate(parsed, m["shown"], m["kind"], m["omnibus"], m["intro"], m["omni_title"]) if parsed else None
        status = "failed" if how != "ok" else "parse_error" if parsed is None else v["status"]
        tally[status] += 1
        if v and v["rows"]:
            for r in v["rows"]:
                tag_rows.append(dict(r, decision_id=cid, confidence=v["confidence"], vocab_version=VOCAB, model_version=infra.model, prompt_version=PROMPT_VERSION, text_version=("nonfinal:%s" % m["desc"]) if m["intro"] else "final_or_order" if m["kind"] != "title_only" else "title_only"))
            tb = [r["bucket"] for r in v["rows"] if r["bucket_type"] == "theme"]
            themes_c.update(tb)
            sectors_c.update(r["bucket"] for r in v["rows"] if r["bucket_type"] == "sector")
            scope_c.update(r["bucket"] for r in v["rows"] if r["bucket_type"] == "scope")
            pa = d["sd"].get("policy_area")
            if d["decision_type"] == "enacted_law" and pa in PA_THEME and pa not in WEAK_PA:
                agree[1] += 1
                agree[0] += PA_THEME[pa] in tb
        run_rows.append({"decision_id": cid, "vocab_version": VOCAB, "status": status, "n_tags": len(v["rows"]) if v else 0, "dropped": ("; ".join(v["dropped"])[:800] if v and v["dropped"] else None), "input_kind": m["kind"], "input_chars": m["chars"], "raw_response": (text or "")[:1500], "model_version": infra.model, "prompt_version": PROMPT_VERSION})
        if a.pilot:
            print("\n=== %s | %s | %s | input %s (%d chars)%s%s" % ((d.get("title") or "")[:70], d["decision_type"], str(d.get("decision_date"))[:10], m["kind"], m["chars"], " | OMNIBUS" if m["omnibus"] else "", (" | NON-FINAL VERSION: %s" % m["desc"]) if m["intro"] else ""))
            print("    status %s | confidence %s | policy area: %s" % (status, v["confidence"] if v else None, d["sd"].get("policy_area")))
            for r in (v["rows"] if v else []):
                print("    %-11s %-26s %-8s %s" % (r["bucket_type"], r["bucket"], r["direction"] or "", ("\"%s\"" % r["evidence"])[:150] if r["evidence"] else ""))
            for x in (v["dropped"] if v else []):
                print("    DROPPED: %s" % x)
            if parsed is None:
                print("    RAW: %s" % (text or "")[:1500])
    print("\nstatus %s" % dict(tally))
    if tag_rows:
        print("scope %s | themes %s | sectors %s" % (dict(scope_c), dict(themes_c.most_common(8)), dict(sectors_c.most_common(8))))
        if agree[1]:
            print("laws: the model's themes include the policy-area baseline theme in %d of %d (%.0f%%)" % (agree[0], agree[1], 100.0 * agree[0] / agree[1]))
    if a.apply:
        replace_ids = sorted(meta.keys())   # a decision's tag set is REPLACED by its newest answer, never merged with an older one: EVERY decision processed in this run, including one whose new answer is invalid or unparseable (it then has no tags, matching its run status)
        for i in range(0, len(replace_ids), 100):
            sb.table("government_decision_tags").delete().eq("vocab_version", VOCAB).in_("decision_id", replace_ids[i:i + 100]).execute()
        for i in range(0, len(tag_rows), 500):
            sb.table("government_decision_tags").upsert(tag_rows[i:i + 500], on_conflict="decision_id,bucket_type,bucket,vocab_version").execute()
        for i in range(0, len(run_rows), 500):
            sb.table("government_decision_tag_runs").upsert(run_rows[i:i + 500], on_conflict="decision_id,vocab_version").execute()
        print("wrote %d tag rows and %d run rows" % (len(tag_rows), len(run_rows)))
    else:
        print("nothing written (%s)" % ("a pilot never writes" if a.pilot else "add --apply"))
    return {"tally": tally, "tags": tag_rows, "runs": run_rows}


if __name__ == "__main__":
    main()
