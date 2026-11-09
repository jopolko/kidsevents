#!/usr/bin/env python3
"""Generic scraper for public libraries on BiblioCommons Events (public JSON gateway). Config: biblio_libraries.json.
Quality signal: BiblioCommons tags every event with audiences; only Kids / Children / Baby / Toddler / Family / All Ages events are kept.
Cancelled and virtual-only events are dropped. Branch addresses are geocoded (Nominatim, cached in biblio_geocode_cache.json)."""
import html, json, re, time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import requests

HERE = Path(__file__).parent
UA = {"User-Agent": "TorontoKidsEvents/1.0 (mjopolko@gmail.com)", "Accept": "application/json"}
KID_AUD = re.compile(r"kid|child|baby|babies|toddler|preschool|famil|all ages|tween|early", re.I)
ADULT_ONLY = re.compile(r"^(adults?|seniors?|teens?|older adults?|newcomers?)$", re.I)
BAD = re.compile(r"\b(book club|adult|seniors?|tax clinic|esl|job|resume|knitting circle|chair yoga|tech help|genealogy)\b", re.I)


def _txt(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


class BiblioScraper:
    def __init__(self, config=None):
        self.libs = json.load(open(config or HERE / "biblio_libraries.json", encoding="utf-8"))["libraries"]
        self.cache_path = HERE / "biblio_geocode_cache.json"
        try: self.cache = json.load(open(self.cache_path, encoding="utf-8"))
        except Exception: self.cache = {}

    def _geocode(self, addr: str):
        if addr in self.cache: return self.cache[addr]
        try:
            r = requests.get("https://nominatim.openstreetmap.org/search", params={"q": addr, "format": "json", "limit": 1, "countrycodes": "ca"}, headers=UA, timeout=20)
            j = r.json(); self.cache[addr] = [float(j[0]["lat"]), float(j[0]["lon"])] if j else None
        except Exception:
            return None
        json.dump(self.cache, open(self.cache_path, "w", encoding="utf-8"))
        time.sleep(1.1)
        return self.cache[addr]

    def _pull(self, slug: str, days: int) -> dict:
        ents, items, page = {}, [], 1
        end = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        while page <= 40:
            r = requests.get(f"https://gateway.bibliocommons.com/v2/libraries/{slug}/events", headers=UA, timeout=30, params={"limit": 100, "page": page})
            if r.status_code != 200: break
            j = r.json(); e = j["entities"]
            for k, v in e.items():
                ents.setdefault(k, {}).update(v) if isinstance(v, dict) else None
            items += j["events"]["items"]
            if page >= j["events"]["pagination"]["pages"]: break
            page += 1
        return {"ents": ents, "items": items, "end": end}

    def _convert(self, lib, ev, ents, end):
        d = ev["definition"]
        if d.get("isCancelled") or ev.get("isFull") and False: return None
        start = d["start"]
        if start[:10] > end or start[:10] < datetime.now().strftime("%Y-%m-%d"): return None
        auds = [ents["eventAudiences"][a]["name"] for a in d.get("audienceIds", []) if a in ents.get("eventAudiences", {})]
        types = [ents["eventTypes"][a]["name"] for a in d.get("typeIds", []) if a in ents.get("eventTypes", {})]
        title, desc = _txt(d["title"]), _txt(d.get("description"))[:400]
        if not auds or not any(KID_AUD.search(a) for a in auds): return None
        if any(ADULT_ONLY.match(a.strip()) for a in auds) and not any(re.search(r"kid|child|baby|toddler|famil|all ages", a, re.I) for a in auds): return None
        if BAD.search(title): return None
        if d.get("isVirtual") and not d.get("branchLocationId"): return None
        loc = ents.get("locations", {}).get(d.get("branchLocationId") or "", {})
        a = loc.get("address") or {}
        addr = ", ".join(x for x in (f'{a.get("number","")} {a.get("street","")}'.strip(), a.get("city"), a.get("state")) if x)
        coords = self._geocode(addr) if addr else None
        blob = " ".join(auds + types + [title, desc])
        ages = []
        if re.search(r"0-5|baby|babies|infant|toddler|preschool|early", blob, re.I): ages += ["Babies (0-2)", "Toddlers (3-5)"] if re.search(r"baby|babies|infant|0-2", blob, re.I) else ["Toddlers (3-5)"]
        if re.search(r"5\+|6-12|school|children|kids", blob, re.I): ages.append("Kids (6-12)")
        ages = list(dict.fromkeys(ages)) or ["All Ages"]
        if "All Ages" in auds and not ages == ["All Ages"]: ages = ["All Ages"]
        reg = d.get("registrationInfo") or {}
        return {
            "title": title, "description": desc or title,
            "category": "Learning", "icon": "📚",
            "date": start[:10], "start_time": start[11:16], "end_time": (d.get("end") or "")[11:16] or None,
            "venue": {"name": loc.get("name") or lib["name"], "address": addr, "neighborhood": a.get("city") or lib.get("city", ""),
                      "lat": coords[0] if coords else None, "lng": coords[1] if coords else None},
            "age_groups": ages, "indoor_outdoor": "Indoor", "organized_by": lib["name"],
            "website": f"https://{lib['slug']}.bibliocommons.com/events/{ev['id']}", "source": "Biblio:" + lib["slug"],
            "scraped_at": datetime.now().isoformat(), "is_free": True,
            "registration_required": bool(reg.get("enabledMethods") or reg.get("cap")),
        }

    def fetch_events(self, days_ahead: int = 60) -> List[Dict]:
        out = []
        for lib in self.libs:
            try:
                p = self._pull(lib["slug"], days_ahead)
                got = [c for c in (self._convert(lib, e, p["ents"], p["end"]) for e in p["items"] if e in p["ents"]["events"] for e in [p["ents"]["events"][e]]) if c]
                print(f"   {lib['slug']:20} {len(p['items'])} total -> {len(got)} kept")
                out += got
            except Exception as ex:
                print(f"   ❌ {lib['slug']}: {ex}")
        return out


if __name__ == "__main__":
    ev = BiblioScraper().fetch_events()
    json.dump(ev, open("biblio_events.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"{len(ev)} events -> biblio_events.json")
