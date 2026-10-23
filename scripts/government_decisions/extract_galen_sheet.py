#!/usr/bin/env python3
"""
extract_galen_sheet.py -- collects the decisions Galen reads INDEPENDENTLY (manifest rows with sample = primary and user_read = Y) into ONE file, data_cache/tag_review_v1_galen_sheet.md, and writes a blank verdict template, results/tag_review_v1_galen.txt, ONLY if that file does not exist yet (it never overwrites verdicts). Reads only the frozen sheets and the manifest; touches nothing registered.
Usage:   python3 scripts/government_decisions/extract_galen_sheet.py
"""
import os, re, csv, glob


def main(res=None, cache=None):
    here = os.path.dirname(os.path.abspath(__file__))
    res = res or os.path.join(here, "..", "..", "results")
    cache = cache or os.path.join(here, "..", "..", "data_cache")
    man = list(csv.DictReader(open(os.path.join(res, "tag_review_v1_manifest.csv"))))
    want = sorted(int(r["order"]) for r in man if r["sample"] == "primary" and r["user_read"] == "Y")
    blocks = {}
    for f in sorted(glob.glob(os.path.join(res, "tag_review_v1_primary_part*.md"))):
        for chunk in re.split(r"\n(?=### )", open(f).read()):
            m = re.match(r"### (\d+)/(\d+) ", chunk)
            if m:
                blocks[int(m.group(1))] = chunk.strip()
    missing = [n for n in want if n not in blocks]
    assert not missing, "decisions not found in the sheets: %s" % missing
    os.makedirs(cache, exist_ok=True)
    out = os.path.join(cache, "tag_review_v1_galen_sheet.md")
    with open(out, "w") as fh:
        fh.write("# Galen's independent read: %d decisions from the frozen primary sample. Verdicts go in results/tag_review_v1_galen.txt, one line per decision number, BEFORE seeing any verdict of Claude's.\n"
                 "# Key: c = correct, w = wrong, u = unsure, - = no tags of that kind. For themes and sectors, c = every tag correct, w = at least one wrong (say which in the note).\n"
                 "# Rubric: results/PREREG_government_tag_review_v1.md. For a sector_specific decision with no sector tag, answer omitted_sector=y if an obvious sector was missed, n if not.\n\n" % len(want))
        fh.write("\n\n".join(blocks[n] for n in want) + "\n")
    tmpl = os.path.join(res, "tag_review_v1_galen.txt")
    if os.path.exists(tmpl):
        print("verdict file already exists, left untouched: %s" % tmpl)
    else:
        with open(tmpl, "w") as fh:
            fh.write("# one line per decision number; c = correct, w = wrong, u = unsure, - = none; notes after 'note:'\n" + "".join("%d scope=_ persistence=_ themes=_ sectors=_ omitted_sector=_ note:\n" % n for n in want))
        print("wrote the blank verdict template: %s" % tmpl)
    print("wrote %d decision sheets to %s" % (len(want), out))
    return want, blocks


if __name__ == "__main__":
    main()
