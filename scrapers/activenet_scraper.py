#!/usr/bin/env python3
"""Generic scraper for municipal recreation on ActiveNet (Active Communities) public registration sites.
Config: activenet_tenants.json. Uses the public site's own JSON list endpoint (no login), politely (>=0.3 s between requests).
Event-like only: explicit kid age range (max age <= 14), single day or <= 7-day run (PD-day/March-break camps, workshops, drop-ins).
Multi-week courses (swim lessons etc.) and 'Any age' items are skipped. Centres are geocoded (cached)."""
import html, json, re, time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import requests
from geocode_util import geocode
from robots_util import allowed
from tribe_scraper import KID_TITLE

HERE = Path(__file__).parent
UA = {"User-Agent": "TorontoKidsEvents/1.0 (mjopolko@gmail.com)", "Accept": "application/json", "Content-Type": "application/json;charset=utf-8"}
BAD = re.compile(r"\b(adult|seniors?|55\+|older adults?|teens? only|prenatal|aquafit|aqua fit|pickleball|tax|resume|3d printer|book club|esl|wellness|yoga for adults|ladies|women|men'?s|hockey league|first aid|cpr|assessment|extended hours|before (and|&) after|lifesaving|bronze (star|medallion|cross)|babysitt\w*|leadership|certification|registration fee|membership|rental|semi-private|private lessons?|swimmer \d|swim level|aquatic leader|inclusion|1:1|one[- ]on[- ]one support)\b", re.I)


def _t(s): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def _body(d1, d2):
    return {"activity_search_pattern": {"skills": [], "time_after_str": "", "days_of_week": "0000000", "activity_select_param": 2, "center_ids": [], "time_before_str": "",
            "open_spots": None, "activity_id": None, "activity_category_ids": [], "date_before": d2, "min_age": 0, "date_after": d1, "activity_type_ids": [], "site_ids": [],
            "for_map": False, "geographic_area_ids": [], "season_ids": [], "activity_department_ids": [], "activity_other_category_ids": [], "child_season_ids": [],
            "activity_keyword": "", "instructor_ids": [], "max_age": 12, "custom_price_from": "", "custom_price_to": ""}, "activity_transfer_pattern": {}}


WORDS = {"Cmty": "Community", "Cplx": "Complex", "Rec": "Recreation", "Ctr": "Centre", "Cntr": "Centre", "CC": "Community Centre", "ES": "Elementary School",
         "PS": "Public School", "MS": "Middle School", "SS": "Secondary School", "Lib": "Library", "Multi-use": "Multi-Use"}


def _expand(n):
    return " ".join(WORDS.get(w, w) for w in n.replace(" - ", " ").split())


def _locate(name, city):
    """Try the expanded name, then the name without a trailing facility word, then the town hall."""
    full = _expand(name)
    for q in (f"{full}, {city}, Ontario", f"{re.sub(chr(32) + r'(Community|Recreation|Centre|Complex|Pool|Arena)( .*)?$', '', full)}, {city}, Ontario"):
        g = geocode(q)
        if g: return g
    return None


def _parse_date(s):
    try: return datetime.strptime(s.strip(), "%B %d, %Y").date()
    except Exception: return None


class ActiveNetScraper:
    def __init__(self, config=None):
        self.tenants = json.load(open(config or HERE / "activenet_tenants.json", encoding="utf-8"))["tenants"]

    def _pull(self, slug, days):
        base = f"https://anc.ca.apm.activecommunities.com/{slug}/rest/activities/list?locale=en-US"
        d1, d2 = datetime.now().strftime("%Y-%m-%d"), (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        items, page, total = [], 1, 1
        if not allowed(base):
            print(f"   (robots.txt disallows {slug})"); return items
        while page <= total and page <= 800:
            h = dict(UA); h["page_info"] = json.dumps({"order_by": "Date", "page_number": page, "total_records_per_page": 20})
            r = requests.post(base, headers=h, json=_body(d1, d2), timeout=40)
            if r.status_code != 200: break
            j = r.json(); total = j["headers"]["page_info"]["total_page"]
            items += j["body"]["activity_items"]
            page += 1; time.sleep(0.3)
        return items

    def _convert(self, it, t, today, end):
        name = _t(it.get("name"))
        any_age = str(it.get("ages", "")).lower().startswith("any") or "all ages" in str(it.get("age_description", "")).lower()
        if any_age:
            if not KID_TITLE.search(name): return None   # no age limit -> need an explicit kid/family signal in the title
            a_min, a_max = 0, 12
        else:
            a_max = it.get("age_max_year"); a_min = it.get("age_min_year")
            if a_max is None or a_max > 14 or (a_min or 0) > 12 or (a_max == 0 and not it.get("age_max_month")): return None
        if BAD.search(name) or BAD.search(_t(it.get("desc"))[:200]): return None
        d0, d1 = it.get("date_range_start"), it.get("date_range_end")
        s = _parse_date((it.get("date_range") or "").split(" to ")[0]) if it.get("date_range") else None
        e = _parse_date((it.get("date_range") or "").split(" to ")[-1]) if it.get("date_range") else None
        if not s or not e or s < today or s > end: return None
        if (e - s).days > 6: return None
        tr = it.get("time_range") or ""
        def tok(x):
            x = x.strip().lower()
            if x == "noon": return "12:00"
            if x == "midnight": return "00:00"
            m2 = re.match(r"(\d{1,2})(?::(\d{2}))? ?(am|pm)", x)
            return f"{int(m2.group(1)) % 12 + (12 if m2.group(3) == 'pm' else 0):02d}:{m2.group(2) or '00'}" if m2 else None
        parts = re.split(r"\s+-\s+", tr)
        st = tok(parts[0]) if parts else None
        en = tok(parts[1]) if len(parts) > 1 else None
        if not st: return None   # a listing without a start time is unusable (and breaks the frontend)
        loc = _t((it.get("location") or {}).get("label"))
        coords = _locate(loc, t["city"]) if loc else None
        fee = it.get("fee"); fee = fee.get("label") if isinstance(fee, dict) else (fee or "")
        free = bool(re.search(r"\bfree\b|\$0\.00", f"{fee} {name}", re.I))
        lo = a_min if a_min is not None else 0
        ages = [n for n, a, b in (("Babies (0-2)", 0, 2), ("Toddlers (3-5)", 3, 5), ("Kids (6-12)", 6, 12)) if lo <= b and a_max >= a]
        ages = ["All Ages"] if any_age else (ages if 0 < len(ages) < 3 else ["All Ages"])
        span = f" ({s.strftime('%b %d')}–{e.strftime('%b %d')})" if e != s else ""
        return {
            "title": name + span if span else name, "description": _t(it.get("desc"))[:400] or name,
            "category": "Sports" if re.search(r"swim|skate|hockey|soccer|camp.*sport|basketball|gym|climb", name, re.I) else "Learning" if re.search(r"camp|workshop|class", name, re.I) else "Play",
            "icon": "🏫" if re.search(r"camp|pa day|pd day", name, re.I) else "🏊" if re.search(r"swim", name, re.I) else "🎈",
            "date": s.isoformat(), "start_time": st, "end_time": en,
            "venue": {"name": loc or t["name"], "address": "", "neighborhood": t["city"], "lat": coords[0] if coords else None, "lng": coords[1] if coords else None},
            "age_groups": ages, "indoor_outdoor": "Indoor", "organized_by": t["name"],
            "website": (it.get("detail_url") or ""), "source": "ActiveNet:" + t["slug"], "scraped_at": datetime.now().isoformat(),
            "is_free": True if free else None, "registration_required": True, "price": fee or None,
        }

    def fetch_events(self, days_ahead: int = 45) -> List[Dict]:
        today = datetime.now().date(); end = today + timedelta(days=days_ahead)
        out = []
        for t in self.tenants:
            try:
                items = self._pull(t["slug"], days_ahead)
                got = [c for c in (self._convert(i, t, today, end) for i in items) if c]
                uniq = {(g["title"], g["date"], g["start_time"], g["venue"]["name"]): g for g in got}
                print(f"   {t['slug']:20} {len(items)} activities -> {len(uniq)} kept")
                out += list(uniq.values())
            except Exception as ex:
                print(f"   ❌ {t['slug']}: {ex}")
        return out


if __name__ == "__main__":
    ev = ActiveNetScraper().fetch_events()
    json.dump(ev, open("activenet_events.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"{len(ev)} events -> activenet_events.json")
