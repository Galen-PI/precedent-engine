"""Offline test of a text guard for CEO/CFO/President/Chair changes in 5.02 filings. No Anthropic cost."""
import os, re, sys, time
sys.path.insert(0, "scripts/classification")
from supabase import create_client
from classify_8k_filings_batch_v2 import fetch_filing_text

REAL = [("MCO","2018-01-29"),("PEP","2014-11-06"),("MSCI","2019-03-06"),("ALL","2022-08-18"),("D","2018-10-09"),
 ("DGX","2013-07-17"),("CVS","2009-11-06"),("CBRE","2019-01-07"),("BEN","2013-06-13"),("DG","2026-02-03"),
 ("KO","2008-07-21"),("LMT","2012-11-27"),("PG","2026-07-29"),("WFC","2017-08-15"),("ADBE","2005-12-15"),
 ("ABBV","2018-10-19"),("ABNB","2023-12-08"),("ERIE","2026-05-21"),("LHX","2014-02-11"),("DTE","2020-03-24")]
ROUTINE = [("EBAY","2021-09-10"),("EG","2017-11-20"),("DLR","2021-08-27"),("FIS","2008-05-07"),("LDOS","2020-10-20"),
 ("NI","2020-10-23"),("CRM","2015-06-26"),("EIX","2022-04-29"),("ERIE","2019-10-21"),("DPZ","2020-09-21"),
 ("DRI","2015-12-18"),("MA","2008-01-17"),("DTE","2008-10-01"),("ELV","2008-03-12"),("NCLH","2021-11-08"),
 ("DECK","2021-09-28"),("COP","2013-07-15"),("PG","2014-06-25"),("DGX","2019-03-04"),("MTD","2010-12-02"),
 ("AXP","2012-02-13"),("ES","2007-01-04"),("EXC","2009-07-31"),("ADBE","2024-07-18"),("HD","2007-12-17"),
 ("LLY","2005-10-17"),("HD","2007-03-19"),("MSFT","2005-11-14"),("MSFT","2006-02-03"),("MSFT","2014-03-20"),
 ("NKE","2007-08-10"),("QCOM","2024-12-12"),("RTX","2024-07-17"),("XOM","2007-02-28"),("GE","2007-12-14"),
 ("GE","2008-04-30"),("VZ","2009-02-25"),("ORCL","2017-07-28"),("PFE","2012-05-23"),("ADBE","2022-01-18")]
DOT = r"(?:[^.]|\b[A-Z]\.|\b(?:Mr|Ms|Mrs|Dr|Jr|Sr|Inc|Corp|Co)\.)"
ROLE = r"(chief executive officer|chief financial officer|\bceo\b|\bcfo\b|chairman|chairwoman|chairperson|chair of the board|\bchair\b|\bpresident\b)"
ACT = r"(resign|retir|step(?:s|ped|ping)? down|depart|succe|replac|appoint|promot|interim|\bnamed\b|\belect|\bbecame\b|\bassum|transition|designat)"
P1 = re.compile(ROLE + DOT + r"{0,100}?" + ACT, re.I)
P2 = re.compile(ACT + DOT + r"{0,100}?" + ROLE, re.I)

def guard(text):
    t = re.sub(r"(executive |senior |group |assistant )?vice[- ](president|chairman|chairwoman)", "VP", text, flags=re.I)
    t = re.sub(r"chair(?:man|woman|person)? of the [A-Za-z&,\- ]{2,50}? committee", "CMTE", t, flags=re.I)
    m = re.search(r"item\s*5\.02", t, re.I)
    seg = t[m.start(): m.start() + 8000] if m else t[:8000]
    return bool(P1.search(seg) or P2.search(seg))

sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
tp = fp = fn = tn = 0
for label, rows in ((1, REAL), (0, ROUTINE)):
    for t, d in rows:
        r = sb.table("filing_ai_classifications").select("primary_document_url").eq("ticker", t).eq("filing_date", d).limit(1).execute().data
        if not r:
            print(f"{t} {d}: no row"); continue
        try:
            hit = guard(fetch_filing_text(r[0]["primary_document_url"]))
        except Exception as e:
            print(f"{t} {d}: fetch error {str(e)[:60]}"); continue
        time.sleep(0.2)
        tp += (label == 1 and hit); fn += (label == 1 and not hit); fp += (label == 0 and hit); tn += (label == 0 and not hit)
        print(f"{t:5s} {d} label={label} guard_hit={int(hit)}")
print(f"\nrecall (real caught): {tp}/{tp+fn}   false alarms on routine: {fp}/{fp+tn}")
