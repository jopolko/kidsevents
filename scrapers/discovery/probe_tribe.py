"""Fingerprint each venue domain and probe its Tribe (The Events Calendar) REST feed. Resumable.
  python probe_tribe.py  -> data/probe.jsonl (one line per domain)"""
import json, re, os, time, concurrent.futures as cf, httpx
from datetime import date
UA = {"User-Agent": "Mozilla/5.0 (compatible; kidsevents-research/1.0; mjopolko@gmail.com)"}
SIG = {"tribe": r"tribe-events|the-events-calendar|tribe/events/v1", "wordpress": r"wp-content|wp-json", "squarespace": r"squarespace",
       "wix": r"wixstatic|parastorage", "eventbrite": r"eventbrite\.", "jsonld_event": r'"@type"\s*:\s*"Event"', "ics": r"\.ics|webcal:",
       "libcal": r"libcal", "amilia": r"amilia", "perfectmind": r"perfectmind", "showpass": r"showpass", "tixr": r"tixr", "meetup": r"meetup\.com",
       "modern_events": r"mec-wrap|modern-events-calendar", "eventon": r"eventon", "ticketing": r"ticketmaster|universe\.com|ticketleap|eventzilla|ticketsource|tickettailor"}
venues = json.load(open("data/osm_venues.json"))
done = set()
if os.path.exists("data/probe.jsonl"): done = {json.loads(l)["host"] for l in open("data/probe.jsonl")}
def go(item):
    host, v = item
    row = {"host": host, "url": v["url"], "names": v["names"][:2], "lat": v["lat"], "lng": v["lng"], "sig": [], "tribe_events": 0, "tribe_base": None}
    try:
        with httpx.Client(headers=UA, follow_redirects=True, timeout=12) as c:
            r = c.get(v["url"]); base = f"{r.url.scheme}://{r.url.host}"; html = r.text
            row["sig"] = [k for k, p in SIG.items() if re.search(p, html, re.I)]
            if "wordpress" in row["sig"] or "tribe" in row["sig"]:
                t = c.get(f"{base}/wp-json/tribe/events/v1/events", params={"per_page": 50, "start_date": date.today().isoformat()})
                if t.status_code == 200 and '"events"' in t.text[:200]:
                    j = t.json(); row["tribe_events"] = j.get("total", len(j["events"])); row["tribe_base"] = base
                    row["sample"] = [e["title"] for e in j["events"][:3]]
    except Exception as e:
        row["err"] = type(e).__name__
    time.sleep(0.2); return row
todo = [i for i in venues.items() if i[0] not in done]
with open("data/probe.jsonl", "a") as f, cf.ThreadPoolExecutor(6) as ex:
    for n, row in enumerate(ex.map(go, todo), 1):
        f.write(json.dumps(row) + "\n"); f.flush()
        if row["tribe_events"]: print(row["host"], row["tribe_events"], row.get("sample"), flush=True)
print("probed", len(todo))
