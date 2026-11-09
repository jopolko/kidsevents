#!/usr/bin/env python3
"""
Venue-owned event feeds (WordPress "The Events Calendar" REST API).

These museums publish their own machine-readable event list at
/wp-json/tribe/events/v1/events, so there is no HTML scraping and no third-party
aggregator involved. Only family / kids events are kept (strict filter): most of
what these venues list is adult workshops and lectures.

Adding a venue: confirm the API responds, check robots.txt allows it, add an entry to VENUES.
"""
import html
import re
import time
import urllib.robotparser
from datetime import date, datetime, timedelta
from typing import Dict, List

import requests

UA = 'TorontoKidsEventsBot/1.0 (+https://joshuaopolko.com/kidsevents/)'

VENUES = [
    {'source': 'BataShoeMuseum', 'domain': 'batashoemuseum.ca', 'name': 'Bata Shoe Museum',
     'address': '327 Bloor St W, Toronto, ON M5S 1W7', 'lat': 43.6670, 'lng': -79.4005,
     'neighborhood': 'The Annex', 'icon': '👟', 'organized_by': 'Bata Shoe Museum'},
    {'source': 'GardinerMuseum', 'domain': 'gardinermuseum.on.ca', 'name': 'Gardiner Museum',
     'address': "111 Queen's Park, Toronto, ON M5S 2C7", 'lat': 43.6685, 'lng': -79.3938,
     'neighborhood': 'Yorkville', 'icon': '🏺', 'organized_by': 'Gardiner Museum'},
    {'source': 'TextileMuseum', 'domain': 'textilemuseum.ca', 'name': 'Textile Museum of Canada',
     'address': '55 Centre Ave, Toronto, ON M5G 2H5', 'lat': 43.6545, 'lng': -79.3866,
     'neighborhood': 'Downtown', 'icon': '🧵', 'organized_by': 'Textile Museum of Canada'},
]

# Title / category signals only (descriptions are too noisy: "all ages", "families welcome" on adult events).
KID_SIGNAL = re.compile(
    r'\b(family|families|kid|kids|child|children|toddler|toddlers|baby|babies|youth|storytime|'
    r'pd day|pa day|march break|winter break|summer break|halloween|drop[- ]in activity)\b', re.I)
ADULT_CAT = re.compile(r'adult|lecture|talk|reception|gala', re.I)
MAX_SPAN_DAYS = 14


def _clean(s: str) -> str:
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s or ''))).strip()


class TribeVenuesScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers['User-Agent'] = UA

    def _allowed(self, domain: str, path: str) -> bool:
        try:
            r = self.session.get(f'https://{domain}/robots.txt', timeout=10)
            if r.status_code != 200:
                return True
            rp = urllib.robotparser.RobotFileParser()
            rp.parse(r.text.splitlines())
            return rp.can_fetch(UA, f'https://{domain}{path}') or rp.can_fetch('*', f'https://{domain}{path}')
        except Exception:
            return True

    def _fetch_raw(self, domain: str, start: date, end: date) -> List[Dict]:
        url = f'https://{domain}/wp-json/tribe/events/v1/events'
        params = {'per_page': 50, 'start_date': start.isoformat(), 'end_date': end.isoformat()}
        out, pages = [], 0
        while url and pages < 4:
            time.sleep(1.0)
            r = self.session.get(url, params=params if pages == 0 else None, timeout=20)
            r.raise_for_status()
            j = r.json()
            out.extend(j.get('events', []))
            url = j.get('next_rest_url')
            pages += 1
        return out

    @staticmethod
    def _plus(t: str, minutes: int) -> str:
        m = min(int(t[:2]) * 60 + int(t[3:5]) + minutes, 24 * 60 - 1)
        return f'{m // 60:02d}:{m % 60:02d}'

    @staticmethod
    def _is_kid_event(e: Dict) -> bool:
        title = _clean(e.get('title', ''))
        cats = [c.get('name', '') for c in e.get('categories', [])]
        if KID_SIGNAL.search(title) or any(KID_SIGNAL.search(c) for c in cats):
            return not any(ADULT_CAT.search(c) for c in cats if not KID_SIGNAL.search(c)) or bool(KID_SIGNAL.search(title))
        return False

    def _convert(self, v: Dict, e: Dict, today: date, horizon: date) -> List[Dict]:
        sd, ed = e.get('start_date_details') or {}, e.get('end_date_details') or {}
        if e.get('all_day') or not sd:
            return []
        first = date(int(sd['year']), int(sd['month']), int(sd['day']))
        last = date(int(ed.get('year', sd['year'])), int(ed.get('month', sd['month'])), int(ed.get('day', sd['day'])))
        start_t = f"{int(sd['hour']):02d}:{int(sd['minutes']):02d}"
        end_t = f"{int(ed['hour']):02d}:{int(ed['minutes']):02d}" if ed else None
        if start_t == '00:00':
            return []
        span = (last - first).days
        if span > MAX_SPAN_DAYS:          # long exhibitions are not "events"
            return []
        title = _clean(e.get('title', ''))
        desc = _clean(e.get('description') or e.get('excerpt') or '')[:300]
        cost = _clean(e.get('cost') or '')
        # A multi-day program is listed ONCE (on its first day still in the window), never expanded into
        # daily sessions: the venue only gave a start and an end, so per-day hours / closures are unknown.
        d = max(first, today)
        if d > horizon or last < today:
            return []
        if span > 0:
            title = f'{title} (through {last.strftime("%b")} {last.day})'
            desc = (desc + ' ' if desc else '') + f'Runs {first.strftime("%b")} {first.day} to {last.strftime("%b")} {last.day}; check the venue for daily hours.'
        return [{
            'title': title,
            'description': desc or f'{title} at {v["name"]}.',
            'category': 'Arts',
            'icon': v['icon'],
            'date': d.isoformat(),
            'start_time': start_t,
            'end_time': end_t if (end_t and end_t > start_t) else self._plus(start_t, 120),   # the site's card code requires an end_time
            'venue': {'name': v['name'], 'address': v['address'], 'neighborhood': v['neighborhood'],
                      'lat': v['lat'], 'lng': v['lng']},
            'age_groups': ['All Ages'],
            'indoor_outdoor': 'Indoor',
            'organized_by': v['organized_by'],
            'website': e.get('url') or f'https://{v["domain"]}/',
            'price': cost or None,
            'is_free': True if re.search(r'\bfree\b', cost, re.I) else None,   # unknown unless the venue says so
            'source': v['source'],
            'scraped_at': datetime.now().isoformat(),
        }]

    def fetch_by_venue(self, days_ahead: int = 90) -> Dict[str, List[Dict]]:
        """Return {source_name: [events]} so the aggregator can tag each venue separately."""
        today = date.today()
        horizon = today + timedelta(days=days_ahead)
        result: Dict[str, List[Dict]] = {}
        for v in VENUES:
            try:
                if not self._allowed(v['domain'], '/wp-json/tribe/events/v1/events'):
                    print(f"   ⚠️  {v['name']}: robots.txt disallows the events API, skipped")
                    result[v['source']] = []
                    continue
                raw = self._fetch_raw(v['domain'], today, horizon)
                kept = []
                for e in raw:
                    if self._is_kid_event(e):
                        kept.extend(self._convert(v, e, today, horizon))
                print(f"   ✅ {v['name']}: {len(raw)} listed, {len(kept)} kid/family event-days kept")
                result[v['source']] = kept
            except Exception as ex:
                print(f"   ❌ {v['name']}: {ex}")
                result[v['source']] = []
        return result

    def fetch_events(self, days_ahead: int = 90) -> List[Dict]:
        return [e for evs in self.fetch_by_venue(days_ahead).values() for e in evs]


if __name__ == '__main__':
    scraper = TribeVenuesScraper()
    by = scraper.fetch_by_venue(90)
    for src, evs in by.items():
        print(f'\n{src}: {len(evs)}')
        for e in evs[:12]:
            print(f"  {e['date']} {e['start_time']}-{e['end_time'] or '?'} | {e['title']} | price={e['price']}")
