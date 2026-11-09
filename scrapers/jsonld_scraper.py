#!/usr/bin/env python3
"""Generic scraper for venues that publish schema.org Event JSON-LD on their own event pages (any platform: WordPress, Tessitura, Wix...).
Config: jsonld_venues.json -> {host, name, pages[], family?}. Same kid/adult rules as tribe_scraper (one definition of 'kid event')."""
import html, json, re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import requests
from robots_util import allowed
from geocode_util import geocode
from tribe_scraper import KID_TITLE, BAD_TITLE, AGE_RANGE, TribeScraper, _txt

UA = {"User-Agent": "TorontoKidsEvents/1.0 (mjopolko@gmail.com)"}
LD = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.I | re.S)


def _events(node, out):
    if isinstance(node, list):
        for x in node: _events(x, out)
    elif isinstance(node, dict):
        ts = node.get("@type"); ts = ts if isinstance(ts, list) else [ts]
        if any(isinstance(t, str) and t.endswith("Event") for t in ts) and node.get("startDate"): out.append(node)
        for k in ("@graph", "itemListElement", "item", "event", "subEvent"):
            if k in node: _events(node[k], out)


class JsonLdScraper:
    def __init__(self, config=None):
        self.venues = json.load(open(config or Path(__file__).with_name("jsonld_venues.json"), encoding="utf-8"))["venues"]

    def _convert(self, e, v, today, end):
        start = str(e["startDate"])
        if not re.match(r"\d{4}-\d{2}-\d{2}", start): return None
        d = start[:10]
        if d < today or d > end: return None
        if "Cancel" in str(e.get("eventStatus", "")) or "Postpone" in str(e.get("eventStatus", "")): return None
        if "Online" in str(e.get("eventAttendanceMode", "")) and "Offline" not in str(e.get("eventAttendanceMode", "")) and "Mixed" not in str(e.get("eventAttendanceMode", "")): return None
        title, desc = _txt(e.get("name")), _txt(e.get("description"))[:400]
        if not title or BAD_TITLE.search(title): return None
        lo = hi = None
        m = AGE_RANGE.search(title + " " + desc)
        if m:
            if m.group(1): lo, hi = int(m.group(1)), int(m.group(2))
            elif m.group(3): lo = int(m.group(3)); hi = int(m.group(4)) if m.group(4) else (99 if m.group(5) else lo)
        if lo is not None and lo >= 13: return None
        if not (v.get("family") or KID_TITLE.search(title) or (lo is not None and lo <= 12 and hi <= 14)): return None
        loc = e.get("location") or {}; loc = loc[0] if isinstance(loc, list) and loc else loc
        loc = loc if isinstance(loc, dict) else {}
        addr = loc.get("address") or {}
        addr = addr if isinstance(addr, dict) else {"streetAddress": str(addr)}
        geo = loc.get("geo") or {}
        try: lat, lng = float(geo.get("latitude")), float(geo.get("longitude"))
        except (TypeError, ValueError): lat = lng = None
        if not (lat and lng and 43.3 <= lat <= 44.5 and -80.3 <= lng <= -78.5): lat, lng = None, None
        city = addr.get("addressLocality") or ""
        if not lat and addr.get("streetAddress"):
            g = geocode(", ".join(x for x in (addr.get("streetAddress"), city, addr.get("addressRegion"), addr.get("postalCode")) if x))
            if g: lat, lng = g
        if v.get("region") and city and not re.search(v["region"], city, re.I) and not re.search(v["region"], str(loc.get("name", "")) + str(e.get("name", "")), re.I): return None
        t = start[11:16] if len(start) > 10 else None
        offers = e.get("offers"); offers = offers[0] if isinstance(offers, list) and offers else (offers or {})
        price = str(offers.get("price", "")) if isinstance(offers, dict) else ""
        return {
            "title": title, "description": desc or title, "category": "Nature" if re.search(r"animal|reptil|zoo|nature", title + desc, re.I) else "Community", "icon": "🦎" if re.search(r"reptil|animal", title, re.I) else "🎈",
            "date": d, "start_time": t or None, "end_time": (str(e.get("endDate", ""))[11:16] or None) if e.get("endDate") and str(e["endDate"])[:10] == d else None,
            "venue": {"name": _txt(loc.get("name")) or v["name"], "address": ", ".join(x for x in (addr.get("streetAddress"), city) if x), "neighborhood": city or "Toronto", "lat": lat or v.get("lat"), "lng": lng or v.get("lng")},
            "age_groups": TribeScraper._ages(lo, hi, title + " " + desc), "indoor_outdoor": "Both", "organized_by": v["name"],
            "website": e.get("url") if isinstance(e.get("url"), str) else v["pages"][0], "source": "JSONLD:" + v["host"], "scraped_at": datetime.now().isoformat(),
            "is_free": True if price in ("0", "0.0", "0.00") else None,
        }

    def fetch_events(self, days_ahead: int = 90) -> List[Dict]:
        today = datetime.now().strftime("%Y-%m-%d"); end = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        out = []
        for v in self.venues:
            got = []
            for p in v["pages"]:
                if not allowed(p):
                    print(f"   (robots.txt disallows {p})"); continue
                try:
                    raw = []
                    for m in LD.finditer(requests.get(p, headers=UA, timeout=20).text):
                        try: _events(json.loads(m.group(1)), raw)
                        except Exception: pass
                    got += [c for c in (self._convert(e, v, today, end) for e in raw) if c]
                except Exception as ex:
                    print(f"   ❌ {p}: {ex}")
            uniq = {(g["title"], g["date"], g["start_time"], g["venue"]["name"]): g for g in got}
            print(f"   {v['host']:28} {len(uniq)} kept")
            out += list(uniq.values())
        return out


if __name__ == "__main__":
    ev = JsonLdScraper().fetch_events()
    json.dump(ev, open("jsonld_events.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"{len(ev)} events -> jsonld_events.json")
