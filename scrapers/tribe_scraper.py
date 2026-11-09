#!/usr/bin/env python3
"""Generic scraper for venues running The Events Calendar (Tribe) WordPress plugin.
One config file (tribe_venues.json), one connector. Add a venue = add a line. Discover candidates with discovery/."""
import html, json, re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import requests
from robots_util import allowed

# Strong kid signal: must appear in the title or the event's own categories/tags, or be an explicit age range <= 12 in the text.
KID_TITLE = re.compile(r"\b(kids?|child(ren)?('?s)?|famil(y|ies)|toddlers?|babies|baby|infants?|preschool(ers?)?|tots?|storytime|story ?time|stories|march break|winter break|pd day|summer camp|camp|puppet|magic show|santa|little|junior|jr\.?|mini|for (the )?little|young (readers|artists|scientists)|ages? ?\d)\b", re.I)
# Anything here in the title drops the event even if a kid word is present.
BAD_TITLE = re.compile(r"\b(closed|cancel+ed|postponed|sold out|full|seniors?|older adults?|55\+|(1[89]|2[01])\+|adults? only|lecture|curator|reception|panel|symposium|webinar|virtual|online|zoom|clinic|meeting|agm|newcomers?|networking|forum|lagers|wine|beer|cocktail|date night|ladies|women|men'?s|prenatal|perinatal|resume|financial|employment|mental health|support group|beginner|intermediate|advanced|all levels|seminar|talk)\b", re.I)
AGE_RANGE = re.compile(r"(?<![\d$:.])(\d{1,2}) ?(?:-|–|to) ?(\d{1,2})(?![\d:.]) ?(?:\+ ?)?(?:yrs?\b|years?\b|y/?o\b)|\bages?:? ?(\d{1,2})(?: ?(?:-|–|to) ?(\d{1,2}))?(?![\d:.])( ?\+|\s*and (?:up|under)|\s*& up)?", re.I)
UA = {"User-Agent": "TorontoKidsEvents/1.0 (+https://github.com; mjopolko@gmail.com)"}


def _txt(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


class TribeScraper:
    def __init__(self, config: str = None):
        self.venues = json.load(open(config or Path(__file__).with_name("tribe_venues.json"), encoding="utf-8"))["venues"]

    def _fetch(self, host: str, days: int) -> List[dict]:
        out, page = [], 1
        end = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        if not allowed(f"https://{host}/wp-json/tribe/events/v1/events"):
            print(f"   (robots.txt disallows {host})"); return out
        while page <= 10:
            r = requests.get(f"https://{host}/wp-json/tribe/events/v1/events", headers=UA, timeout=20,
                             params={"per_page": 50, "page": page, "start_date": datetime.now().strftime("%Y-%m-%d"), "end_date": end})
            if r.status_code != 200:
                break
            j = r.json()
            out += j.get("events", [])
            if page >= j.get("total_pages", 1):
                break
            page += 1
        return out

    @staticmethod
    def _ages(lo, hi, text):
        if lo is not None:
            out = [n for n, a, b in (("Babies (0-2)", 0, 2), ("Toddlers (3-5)", 3, 5), ("Kids (6-12)", 6, 12)) if lo <= b and hi >= a]
            return out if len(out) < 3 else ["All Ages"]
        out = [n for n, p in (("Babies (0-2)", r"(babies|baby|infants?)"), ("Toddlers (3-5)", r"(toddlers?|preschool\w*|tots?)"),
                              ("Kids (6-12)", r"(kids?|children|child|school[- ]age)")) if re.search(p, text, re.I)]
        return out or ["All Ages"]

    def _convert(self, e: dict, v: dict) -> Dict:
        title, desc = _txt(e["title"]), _txt(e.get("excerpt") or e.get("description"))[:400]
        cats = [_txt(c["name"]) for c in e.get("categories", [])] + [_txt(t["name"]) for t in e.get("tags", [])]
        blob = " ".join([title, desc, *cats])
        strong = " ".join([title, *cats])
        lo = hi = None
        for m in AGE_RANGE.finditer(blob):
            if m.group(1):
                x, y = int(m.group(1)), int(m.group(2))
                if 0 <= x < y <= 19: lo, hi = x, y
            elif m.group(3) and int(m.group(3)) <= 19:
                lo = int(m.group(3)); hi = int(m.group(4)) if m.group(4) else (99 if m.group(5) else lo)
            if lo is not None: break
        if BAD_TITLE.search(title) or (lo is not None and lo >= 13):
            return None
        if not (KID_TITLE.search(strong) or (lo is not None and lo <= 12 and hi <= 14)):
            return None
        if re.search(r"\b(virtual|online|zoom)\b", desc[:200], re.I) and not re.search(r"in[- ]person", desc, re.I):
            return None
        vn = e.get("venue") or {}
        vn = vn if isinstance(vn, dict) else {}
        lat, lng = vn.get("geo_lat"), vn.get("geo_lng")
        try:
            lat, lng = float(lat), float(lng)
        except (TypeError, ValueError):
            lat = lng = None
        if not (lat and lng and 43.3 <= lat <= 44.3 and -80.3 <= lng <= -78.6):  # also rejects the plugin's 55.0 default
            lat, lng = v.get("lat"), v.get("lng")
        m = re.search(r"(?<!\d)ages?:?\s*(\d{1,2})(?!\d)|(?<!\d)(\d{1,2}) ?(?:-|to) ?\d{1,2}(?!\d)\s*(?:yrs?|years)", blob, re.I)
        if m and int(m.group(1) or m.group(2)) >= 13:
            return None  # teen/adult-only (stated minimum age 13+)
        cost = _txt(e.get("cost") or "")
        ages = self._ages(lo, hi, strong + " " + desc)
        return {
            "title": title, "description": desc or title,
            "category": "Arts" if re.search(r"(art|craft|paint|clay|music|dance|puppet|magic|theatre|story)\w*", blob, re.I) else ("Nature" if re.search(r"(nature|bird|walk|garden|hike)\w*", blob, re.I) else "Community"),
            "icon": "🏛️" if v.get("family") else "🎈",
            "date": e["start_date"][:10], "start_time": None if e.get("all_day") else e["start_date"][11:16],
            "end_time": None if e.get("all_day") else e["end_date"][11:16],
            "venue": {"name": _txt(vn.get("venue")) or v["name"], "address": ", ".join(x for x in (vn.get("address"), vn.get("city")) if x),
                      "neighborhood": vn.get("city") or "Toronto", "lat": lat, "lng": lng},
            "age_groups": ages, "indoor_outdoor": "Both",
            "organized_by": v["name"], "website": e.get("url"), "source": "Tribe:" + v["host"],
            "scraped_at": datetime.now().isoformat(),
            "is_free": bool(re.search(r"free|no charge|pwyc|by donation", cost + " " + title, re.I)) or None,
        }

    def fetch_events(self, days_ahead: int = 90) -> List[Dict]:
        events = []
        for v in self.venues:
            try:
                got = [c for c in (self._convert(e, v) for e in self._fetch(v["host"], days_ahead)) if c]
                print(f"   {v['host']:30} {len(got)} kept")
                events += got
            except Exception as ex:
                print(f"   ❌ {v['host']}: {ex}")
        return events


if __name__ == "__main__":
    ev = TribeScraper().fetch_events()
    json.dump(ev, open("tribe_events.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"{len(ev)} events -> tribe_events.json")
