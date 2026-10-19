#!/usr/bin/env python3
"""
compare_pilot_runs.py -- READ-ONLY. Compares two finished label batches that covered the same events (for example two pilot runs):
how often do the labels agree, and are there any good <-> bad flips? Writes nothing to the database.

Usage (from scripts/classification):
    python3 -u compare_pilot_runs.py BATCH_ID_1 BATCH_ID_2

Fetches each batch's results through the same helper the labeler uses (poll_batches_until_all_done returns at once for a finished batch),
parses them with the labeler's own parser, and reports:
  - how many results each batch has and whether the raw output contained a 'timing' key (tells the old prompt from the new one)
  - label agreement on the events both batches labeled, a confusion table, and the good <-> bad flips with their titles
"""
import os, sys, json, importlib.util
from collections import Counter

LABELS = ("good", "bad", "mixed", "unclear")


def load_labeler():
    here = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location("label_event_direction", os.path.join(here, "label_event_direction.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fetch_results(requests, url, hdr, ld):
    resp = requests.get(url, headers=hdr, timeout=60)
    resp.raise_for_status()
    out = {}
    for line in resp.text.strip().split("\n"):
        row = json.loads(line)
        cid, res = row["custom_id"], row["result"]
        if res["type"] != "succeeded":
            out[cid] = {"label": None, "size": None, "timing_in_raw": False, "reasoning": "BATCH REQUEST FAILED: " + str(res["type"])}
            continue
        blocks = [b["text"] for b in res["message"]["content"] if b.get("type") == "text"]
        if not blocks:
            out[cid] = {"label": None, "size": None, "timing_in_raw": False, "reasoning": "EMPTY"}
            continue
        parsed = ld.parse_result(blocks[0])
        raw = blocks[0].strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            raw = raw[4:] if raw.startswith("json") else raw
        try:
            parsed["timing_in_raw"] = "timing" in json.loads(raw.strip())
        except Exception:
            parsed["timing_in_raw"] = False
        out[cid] = parsed
    return out


def compare(a, b, titles=None):
    both = [c for c in a if c in b and a[c]["label"] and b[c]["label"]]
    agree = sum(1 for c in both if a[c]["label"] == b[c]["label"])
    print("events labeled validly by both: %d" % len(both))
    if not both:
        return
    print("label agreement: %d/%d = %.1f%%" % (agree, len(both), 100.0 * agree / len(both)))
    conf = Counter((a[c]["label"], b[c]["label"]) for c in both)
    print("\nconfusion (rows = first batch, columns = second batch)")
    print("        " + "".join("%9s" % l for l in LABELS))
    for r in LABELS:
        print("%-8s" % r + "".join("%9d" % conf.get((r, k), 0) for k in LABELS))
    flips = [c for c in both if {a[c]["label"], b[c]["label"]} == {"good", "bad"}]
    print("\ngood <-> bad flips: %d of %d" % (len(flips), len(both)))
    for c in flips[:8]:
        print("  %s | %s | first: %s (%s) | second: %s (%s)" % (c[:8], (titles or {}).get(c, "?")[:70], a[c]["label"], (a[c]["reasoning"] or "")[:70], b[c]["label"], (b[c]["reasoning"] or "")[:70]))
    sz = [c for c in both if a[c]["label"] == b[c]["label"] and a[c].get("size") and b[c].get("size")]
    if sz:
        print("\namong the agreed labels, size hint agrees: %d/%d" % (sum(1 for c in sz if a[c]["size"] == b[c]["size"]), len(sz)))


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    id1, id2 = sys.argv[1], sys.argv[2]
    ld = load_labeler()
    import requests
    bm = ld.load_batch()
    hdr = {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01", "content-type": "application/json"}
    bm.ANTHROPIC_HEADERS = hdr
    final = bm.poll_batches_until_all_done([id1, id2])
    res = {}
    for bid in (id1, id2):
        url = (final.get(bid) or {}).get("results_url")
        if not url:
            sys.exit("Batch %s has no results_url (not finished?)" % bid)
        res[bid] = fetch_results(requests, url, hdr, ld)
        r = res[bid]
        valid = [v for v in r.values() if v["label"]]
        print("batch %s: %d results, %d valid, 'timing' key in raw output: %d/%d" % (bid, len(r), len(valid), sum(1 for v in valid if v["timing_in_raw"]), len(valid)))
    ids = [c for c in res[id1] if c in res[id2]]
    titles = {}
    flips = [c for c in ids if res[id1][c]["label"] and res[id2][c]["label"] and {res[id1][c]["label"], res[id2][c]["label"]} == {"good", "bad"}]
    if flips:
        sb = ld.get_sb()
        for i in range(0, len(flips), 100):
            for r in sb.table("events").select("id,title").in_("id", flips[i:i + 100]).execute().data:
                titles[r["id"]] = r["title"]
    print()
    compare(res[id1], res[id2], titles)


if __name__ == "__main__":
    main()
