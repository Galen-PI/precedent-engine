#!/usr/bin/env python3
"""
probe_unadjusted_prices.py -- READ-ONLY, two vendor requests, writes nothing. Does the vendor (Twelve Data) return AS-QUOTED prices with adjust=none on this plan?
Expected if it does: AAPL close 2020-08-28 = 499.23 and 2020-08-31 = 129.04 (the 4-for-1 split took effect on 2020-08-31), values recalled from memory: verify against any quote site. The stored series (adjust=all) shows 120.935 and 125.036 for the same days.
The key is read from TWELVE_DATA_API_KEY (as refresh_market_prices.py does) and never printed.
"""
import os, json, requests
key = os.environ["TWELVE_DATA_API_KEY"]
r = requests.get("https://api.twelvedata.com/time_series", timeout=60, params={"symbol": "AAPL", "interval": "1day", "start_date": "2020-08-26", "end_date": "2020-09-01", "adjust": "none", "outputsize": 20, "apikey": key})
print("time_series HTTP", r.status_code)
print(json.dumps(r.json(), indent=1)[:1500])
u = requests.get("https://api.twelvedata.com/api_usage", params={"apikey": key}, timeout=30)
print("api_usage:", json.dumps(u.json())[:400])
