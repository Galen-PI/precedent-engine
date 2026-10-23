#!/usr/bin/env python3
"""
build_tag_review_sheet.py -- draws the REGISTERED review sample (results/PREREG_government_tag_review_v1.md) from the v1 tags and writes the sheets to read. READ-ONLY on the database; files under results/ only with --apply (a dry run prints the allocation and the counts).
Writes: results/tag_review_v1_manifest.csv, results/tag_review_v1_attributes.csv (the hidden stability column), results/tag_review_v1_primary_partNN.md and results/tag_review_v1_lowconf_partNN.md.
Usage:   python3 -u scripts/government_decisions/build_tag_review_sheet.py            dry run
         python3 -u scripts/government_decisions/build_tag_review_sheet.py --apply    writes the files
"""
import os, sys, re, csv, random, argparse, collections

VOCAB, REPEAT, SEED = "v1", "v1_rerun", 20261023
TABLE = str.maketrans({"\u201c": '"', "\u201d": '"', "\u2018": "'", "\u2019": "'", "\u2013": "-", "\u2014": "-"})


def era_of(year):
    return "<=2004" if year <= 2004 else "2005-2014" if year <= 2014 else ">=2015"


def allocate(sizes, total, minimum):
    """proportional allocation with a floor, adjusted to sum exactly to total (never above a stratum's size)"""
    keys, n = sorted(sizes), float(sum(sizes.values()))
    alloc = {k: min(sizes[k], max(minimum, int(round(total * sizes[k] / n)))) for k in keys}
    while sum(alloc.values()) > total:
        k = max((k for k in keys if alloc[k] > min(minimum, sizes[k])), key=lambda k: alloc[k] - total * sizes[k] / n)
        alloc[k] -= 1
    while sum(alloc.values()) < total:
        k = max((k for k in keys if alloc[k] < sizes[k]), key=lambda k: total * sizes[k] / n - alloc[k])
        alloc[k] += 1
    return alloc


def draw(decs, n_primary, n_low, n_user, seed, minimum):
    """decs: list of dicts with id, type, year, low (True if the decision's tags carry confidence low). Returns (primary, lowconf, user_read), each a list of ids"""
    strata = collections.defaultdict(list)
    for d in decs:
        strata[(d["type"], era_of(d["year"]))].append(d)
    alloc = allocate({k: len(v) for k, v in strata.items()}, n_primary, minimum)
    rng, primary = random.Random(seed), []
    for k in sorted(strata):
        pool = sorted(strata[k], key=lambda d: d["id"])
        rng.shuffle(pool)
        primary += [d["id"] for d in pool[:alloc[k]]]
    random.Random(seed + 10).shuffle(primary)
    chosen = set(primary)
    lowpool = sorted((d["id"] for d in decs if d["low"] and d["id"] not in chosen))
    random.Random(seed + 1).shuffle(lowpool)
    lowconf = lowpool[:n_low]
    user = sorted(random.Random(seed + 2).sample(primary, min(n_user, len(primary))), key=primary.index)
    return primary, lowconf, user, alloc


def locate(body, quote, width=150):
    """the sentence-ish context around a quote in the stored text, in the original case; None if not found"""
    clean = " ".join((body or "").split())
    qn = " ".join((quote or "").split()).translate(TABLE).lower()
    if not qn:
        return None
    i = clean.translate(TABLE).lower().find(qn[:90])
    if i < 0:
        return None
    return clean[max(0, i - width): i + len(qn) + width]


def paged(sb, table, cols, order, flt=None, size=1000):
    out, off = [], 0
    while True:
        q = sb.table(table).select(cols).order(order)
        if flt:
            q = flt(q)
        page = q.range(off, off + size - 1).execute().data
        if not page:
            break
        out += page
        if len(page) < size:
            break
        off += size
    return out


def format_decision(k, total, d, run, tags, body):
    law = d["decision_type"] == "enacted_law"
    sc = [t for t in tags if t["bucket_type"] == "scope"]
    pe = [t for t in tags if t["bucket_type"] == "persistence"]
    th = [t for t in tags if t["bucket_type"] == "theme"]
    se = [t for t in tags if t["bucket_type"] == "sector"]
    first = tags[0] if tags else {}
    out = ["### %d/%d | %s | %s | %s | %s" % (k, total, d["id"][:8], "LAW" if law else "ORDER", str(d.get("decision_date"))[:10], (d.get("title") or "")[:110]),
           "policy area: %s | text shown: %s (%s chars) | version: %s | decision confidence: %s" % ((d.get("sd") or {}).get("policy_area") or "-", run.get("input_kind"), run.get("input_chars"), first.get("text_version"), first.get("confidence")),
           "SCOPE: %s%s" % (sc[0]["bucket"] if sc else "(none written: text under 300 characters)", ("   [model note: %s]" % sc[0]["evidence"]) if sc and sc[0].get("evidence") else ""),
           "PERSISTENCE: %s" % (pe[0]["bucket"] if pe else "-")]
    for t in th + se:
        head = "THEME %s" % t["bucket"] if t["bucket_type"] == "theme" else "SECTOR %s (%s)" % (t["bucket"], t.get("direction"))
        out.append("%s: \"%s\"" % (head, t.get("evidence") or ""))
        ctx = locate(body, t.get("evidence"))
        out.append("    context: ...%s..." % ctx if ctx else "    context: (not located in the stored text)")
    if not th and not se:
        out.append("(no theme or sector tags)")
    out.append("TEXT START: %s" % " ".join((body or "").split())[:350])
    out.append("VERDICT:  scope __   persistence __   themes __   sectors __   (omitted obvious sector? __)")
    return "\n".join(out) + "\n"


def main(argv=None, sb=None, outdir=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--primary", type=int, default=150)
    ap.add_argument("--lowconf", type=int, default=100)
    ap.add_argument("--user-read", type=int, default=30)
    ap.add_argument("--per-part", type=int, default=25)
    ap.add_argument("--min-stratum", type=int, default=15)
    a = ap.parse_args(argv)
    if sb is None:
        from supabase import create_client
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    outdir = outdir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "results")
    runs = {str(r["decision_id"]): r for r in paged(sb, "government_decision_tag_runs", "decision_id,status,input_kind,input_chars", "decision_id", lambda q: q.eq("vocab_version", VOCAB)) if r["status"] in ("ok", "partial")}
    tags = collections.defaultdict(list)
    for t in paged(sb, "government_decision_tags", "decision_id,bucket_type,bucket,direction,confidence,evidence,text_version", "decision_id", lambda q: q.eq("vocab_version", VOCAB)):
        tags[str(t["decision_id"])].append(t)
    rep = {(str(t["decision_id"]), t["bucket_type"], t["bucket"]) for t in paged(sb, "government_decision_tags", "decision_id,bucket_type,bucket", "decision_id", lambda q: q.eq("vocab_version", REPEAT))}
    rep_dec = {str(r["decision_id"]) for r in paged(sb, "government_decision_tag_runs", "decision_id,status", "decision_id", lambda q: q.eq("vocab_version", REPEAT)) if r["status"] in ("ok", "partial")}
    decs = {str(d["id"]): d for d in paged(sb, "government_decisions", "id,title,decision_type,decision_date,structured_data", "id") if str(d["id"]) in runs}
    for d in decs.values():
        sd = d.get("structured_data")
        d["sd"] = sd if isinstance(sd, dict) else {}
    pool = [{"id": i, "type": d["decision_type"], "year": int(str(d.get("decision_date") or "0")[:4] or 0), "low": any(t.get("confidence") == "low" for t in tags.get(i, []))} for i, d in decs.items() if tags.get(i)]
    primary, lowconf, user, alloc = draw(pool, a.primary, a.lowconf, a.user_read, SEED, a.min_stratum)
    print("usable decisions with tags %d | primary %d | low-confidence %d | independent read %d" % (len(pool), len(primary), len(lowconf), len(user)))
    print("allocation (type, era): %s" % {"%s/%s" % k: v for k, v in sorted(alloc.items())})
    print("Galen reads these PRIMARY numbers (independently, before seeing any verdict): %s" % [primary.index(i) + 1 for i in user])
    if not a.apply:
        print("DRY RUN: no files written (add --apply)")
        return primary, lowconf, user
    ids = primary + lowconf
    bodies = {}
    for i in range(0, len(ids), 20):
        for r in sb.table("government_decision_text").select("decision_id,body").in_("decision_id", ids[i:i + 20]).execute().data:
            bodies[str(r["decision_id"])] = r.get("body") or ""
    os.makedirs(outdir, exist_ok=True)
    manifest, attrs = [], []
    for sample, lst in (("primary", primary), ("lowconf", lowconf)):
        for p0 in range(0, len(lst), a.per_part):
            part = lst[p0: p0 + a.per_part]
            text = "# Tag review v1, %s sample, part %02d (decisions %d-%d of %d). Read against the rubric in PREREG_government_tag_review_v1.md.\n\n" % (sample, p0 // a.per_part + 1, p0 + 1, p0 + len(part), len(lst))
            text += "\n".join(format_decision(p0 + j + 1, len(lst), decs[i], runs[i], tags[i], bodies.get(i, "")) for j, i in enumerate(part))
            with open(os.path.join(outdir, "tag_review_v1_%s_part%02d.md" % (sample, p0 // a.per_part + 1)), "w") as fh:
                fh.write(text)
        for k, i in enumerate(lst):
            d = decs[i]
            manifest.append({"sample": sample, "order": k + 1, "decision_id": i, "decision_type": d["decision_type"], "era": era_of(int(str(d.get("decision_date"))[:4])), "user_read": "Y" if (sample == "primary" and i in user) else "N"})
            for t in tags[i]:
                attrs.append({"sample": sample, "decision_id": i, "bucket_type": t["bucket_type"], "bucket": t["bucket"], "direction": t.get("direction") or "", "confidence": t.get("confidence"), "input_kind": runs[i].get("input_kind"), "text_version": t.get("text_version"), "stable_in_repeat": ("Y" if (i, t["bucket_type"], t["bucket"]) in rep else "N") if i in rep_dec else "NA"})
    for name, rows in (("manifest", manifest), ("attributes", attrs)):
        with open(os.path.join(outdir, "tag_review_v1_%s.csv" % name), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    print("wrote %d decision sheets in %d part files plus the manifest (%d rows) and the hidden attributes (%d rows) under %s" % (len(ids), -(-len(primary) // a.per_part) + -(-len(lowconf) // a.per_part), len(manifest), len(attrs), outdir))
    return primary, lowconf, user


if __name__ == "__main__":
    main()
