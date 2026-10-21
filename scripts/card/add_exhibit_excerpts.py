#!/usr/bin/env python3
"""
add_exhibit_excerpts.py -- reads results/human_review_queue.csv, fetches each filing's COMPLETE SUBMISSION text from SEC (built from the accession folder in the primary-document URL), pulls out the first characters of the press-release exhibit
(EX-99 / EX-99.1 ...), and writes results/human_review_queue_with_excerpts.csv with two extra columns: exhibit_excerpt and keyword_hint. Nothing is written to the database. The classifier reads one URL only; for a main-document .htm the press release is a separate file,
which is why a bare 'issued a press release' 8-K looks like noise to it. keyword_hint is a crude keyword match (merger, guidance, offering, trial, lawsuit, leadership, dividend/buyback, restatement), NOT a verdict.
Every fetched filing is cached in data_cache/sec_excerpts/<accession folder>.json, so a rerun makes no new SEC requests. Be a polite client: about 5 requests a second at most (DELAY), and set SEC_USER_AGENT to a real contact (the SEC asks for one).
Usage:   python3 -u scripts/card/add_exhibit_excerpts.py [tiers, default A] [max rows, default 400]       e.g.  ... AC 600
"""
import os, sys, re, csv, json, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RESULTS = os.path.join(ROOT, "results")
CACHE = os.path.join(ROOT, "data_cache", "sec_excerpts")
UA = os.environ.get("SEC_USER_AGENT", "stock-research1 project contact@example.com")
DELAY = 0.2
MAX_BYTES = 1_500_000
EXCERPT = 4000                  # kept in the cache and used for the keyword hint; the CSV shows the first 1,200 characters
HINTS = [("merger/acquisition", r"merger|acquisition|acquire|business combination|tender offer|definitive agreement"), ("guidance/outlook", r"guidance|outlook|expects? (?:revenue|earnings|net income|eps)|preliminary (?:results|revenue)|updat\w+ (?:its )?(?:financial )?(?:guidance|outlook)"),
         ("offering/financing", r"public offering|offering of|senior notes|prices? (?:an )?offering|convertible|credit facility"), ("clinical/regulatory", r"phase [123i]|clinical|fda\b|topline|trial results"),
         ("lawsuit/investigation", r"lawsuit|complaint|settlement|subpoena|investigation|department of justice|\bdoj\b|\bsec\b investigation|civil action"), ("leadership", r"resign|appoint|names? (?:new )?(?:chief|ceo|cfo|president)|steps? down|retire"),
         ("dividend/buyback", r"dividend|repurchase|buyback"), ("restatement/accounting", r"restat|non-reliance|material weakness|impairment")]


def parse_url(url):
    m = re.search(r"/data/(\d+)/(\d{18})/", url or "")
    if not m:
        return None
    cik, a18 = m.group(1), m.group(2)
    return cik, a18, "%s-%s-%s" % (a18[:10], a18[10:12], a18[12:])


def clean(text):
    text = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;|&#160;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_exhibit(sub_text):
    """First press-release-like exhibit (TYPE EX-99*) of a complete submission; returns (type, excerpt) or (None, '')."""
    for doc in re.split(r"(?i)<DOCUMENT>", sub_text)[1:]:
        m = re.search(r"(?i)<TYPE>\s*([^\s<]+)", doc)
        if m and m.group(1).upper().startswith("EX-99"):
            body = re.split(r"(?i)<TEXT>", doc, maxsplit=1)
            return m.group(1).upper(), clean(body[1] if len(body) > 1 else doc)[:EXCERPT]
    return None, ""


def fetch_complete(cik, a18, adash):
    import requests
    url = "https://www.sec.gov/Archives/edgar/data/%s/%s/%s.txt" % (cik, a18, adash)
    last = "no attempt"
    for attempt in range(4):
        time.sleep(DELAY)
        try:
            with requests.get(url, headers={"User-Agent": UA}, timeout=30, stream=True) as r:
                if r.status_code in (403, 429, 503):
                    last = "http %d (rate limit or blocked)" % r.status_code
                    time.sleep(3 * (attempt + 1))
                    continue
                if r.status_code != 200:
                    return None, "http %d" % r.status_code
                chunks, size = [], 0
                for ch in r.iter_content(65536):
                    chunks.append(ch)
                    size += len(ch)
                    if size >= MAX_BYTES:
                        break
                return b"".join(chunks).decode(r.encoding or "latin-1", errors="replace"), "ok"
        except Exception as e:
            last = "error: %s" % str(e)[:60]
            time.sleep(3 * (attempt + 1))
    return None, "failed: " + last


def excerpt_for(url):
    p = parse_url(url)
    if not p:
        return {"type": "", "excerpt": "", "status": "no accession in URL"}
    cik, a18, adash = p
    path = os.path.join(CACHE, a18 + ".json")
    if os.path.exists(path):
        return json.load(open(path))
    text, status = fetch_complete(cik, a18, adash)
    if text is None:
        return {"type": "", "excerpt": "", "status": status}
    typ, ex = extract_exhibit(text)
    res = {"type": typ or "", "excerpt": ex, "status": "ok" if typ else "ok, no EX-99 exhibit in the submission"}
    os.makedirs(CACHE, exist_ok=True)
    json.dump(res, open(path, "w"))
    return res


def hint(text):
    low = text.lower()
    return "; ".join(name for name, pat in HINTS if re.search(pat, low))


def main():
    tiers = sys.argv[1] if len(sys.argv) > 1 else "A"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    rows = list(csv.DictReader(open(os.path.join(RESULTS, "human_review_queue.csv"))))
    todo = [r for r in rows if r["tier"] in tiers][:limit]
    out, n_ok, n_fail, t0 = [], 0, 0, time.time()
    for i, r in enumerate(todo):
        urls = re.findall(r"https?://[^\s;|]+", r["evidence"])
        res = excerpt_for(urls[0]) if urls else {"type": "", "excerpt": "", "status": "no URL"}
        n_ok += int(bool(res["excerpt"]))
        n_fail += int(not res["excerpt"])
        r = dict(r)
        r["exhibit_excerpt"] = ("[%s] " % res["type"] if res["type"] else "") + (res["excerpt"][:1200] if res["excerpt"] else "(" + res["status"] + ")")
        r["keyword_hint"] = hint(res["excerpt"])
        out.append(r)
        if (i + 1) % 25 == 0:
            print("  %d/%d | excerpts %d, none %d | %.0fs" % (i + 1, len(todo), n_ok, n_fail, time.time() - t0), flush=True)
    path = os.path.join(RESULTS, "human_review_queue_with_excerpts.csv")
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(todo[0].keys()) + ["exhibit_excerpt", "keyword_hint"] if todo else ["tier"])
        w.writeheader()
        w.writerows(out)
    print("wrote %s | rows %d | with an exhibit excerpt %d | without %d" % (path, len(out), n_ok, n_fail))
    for r in out[:6]:
        print("  %s %-6s %-12s | %s | %s" % (r["date"], r["ticker"], r["classifier_verdict"][:12], r["keyword_hint"][:40] or "-", r["exhibit_excerpt"][:110]))


if __name__ == "__main__":
    main()
