"""Find iCalendar feeds on venue sites: advertised .ics/webcal links plus platform export URLs (Tribe, Ai1ec, MEC, EventON-free paths).
Keep a feed only if it returns VEVENTs dated in the future.  -> data/feeds.jsonl"""
import json, re, concurrent.futures as cf, httpx
from datetime import datetime
from urllib.parse import urljoin, urlparse
UA = {"User-Agent": "Mozilla/5.0 (compatible; kidsevents-research/1.0; mjopolko@gmail.com)"}
rows = [json.loads(l) for l in open("data/fp_deep.jsonl")]
rows = [r for r in rows if not r.get("err") and any(k in r["sig"] for k in ("ics", "ai1ec", "mec", "tribe", "eventon", "events_manager", "my_calendar", "google_cal", "drupal_calendar", "wordpress", "civicplus"))]
print(len(rows), "sites to probe")
NOW = datetime.now().strftime("%Y%m%d")
def future(txt):
    d = re.findall(r"DTSTART[^:\n]*:(\d{8})", txt)
    return sum(1 for x in d if x >= NOW), len(re.findall(r"BEGIN:VEVENT", txt))
def go(r):
    out = {"host": r["host"], "names": r["names"][:1], "lat": r["lat"], "lng": r["lng"], "feeds": []}
    try:
        with httpx.Client(headers=UA, follow_redirects=True, timeout=12) as c:
            base = f"{urlparse(r['pages'][0]).scheme}://{urlparse(r['pages'][0]).netloc}"
            cands = []
            for p in r["pages"][:3]:
                try: h = c.get(p).text
                except Exception: continue
                for m in re.finditer(r'''(?:href|src)=["']([^"']+?(?:\.ics|webcal:|ical=1|exportevents|export_events|ical)[^"']*)["']''', h, re.I):
                    u = m.group(1).replace("&amp;", "&").replace("webcal://", "https://")
                    cands.append(urljoin(p, u))
            cands += [base + x for x in ("/?post_type=tribe_events&ical=1&eventDisplay=list", "/events/?ical=1&eventDisplay=list",
                      "/?plugin=all-in-one-event-calendar&controller=ai1ec_exporter_controller&action=export_events",
                      "/?mec-ical-feed=1", "/events/?ical=1")]
            seen = set()
            for u in cands:
                if u in seen or urlparse(u).hostname and "google.com" in urlparse(u).hostname and "ical" not in u: continue
                seen.add(u)
                try:
                    x = c.get(u)
                    if x.status_code == 200 and "BEGIN:VCALENDAR" in x.text[:500]:
                        fut, tot = future(x.text)
                        if fut: out["feeds"].append({"url": u, "future": fut, "total": tot})
                except Exception: pass
                if len(out["feeds"]) >= 2: break
    except Exception as e: out["err"] = type(e).__name__
    return out
with open("data/feeds.jsonl", "w") as f, cf.ThreadPoolExecutor(8) as ex:
    for o in ex.map(go, rows):
        f.write(json.dumps(o) + "\n")
        if o["feeds"]: print(o["host"][:30].ljust(30), o["names"][0][:26].ljust(26), [(x["future"], x["url"][-50:]) for x in o["feeds"]], flush=True)
