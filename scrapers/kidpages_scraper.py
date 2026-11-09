#!/usr/bin/env python3
"""
Kid events read from venue pages (nothing generated):
  - Arts Etobicoke: children's / after-school classes (event list + each event's detail page)
  - Evergreen Brick Works: Children's Garden "garden parties" (dates listed on the garden page)
Every event must have a date that the venue's own page states.
"""
import html
import re
import time
from datetime import date, datetime
from typing import Dict, List

import requests

UA = 'TorontoKidsEventsBot/1.0 (+https://joshuaopolko.com/kidsevents/)'
MONTHS = {m: i + 1 for i, m in enumerate(
    ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'])}
KID_TITLE = re.compile(r'\b(child|children|kids?|after[- ]school|little|toddler|baby|family)\b', re.I)


def _text(s: str) -> str:
    s = re.sub(r'(?s)<(script|style|noscript|svg)[^>]*>.*?</\1>', '', s)
    t = html.unescape(re.sub(r'<[^>]+>', '\n', s))
    return re.sub(r'\n\s*\n+', '\n', re.sub(r'[ \t]+', ' ', t)).strip()


def _t24(s: str) -> str:
    m = re.match(r'(\d{1,2})(?::(\d{2}))?\s*([ap])m', s.strip(), re.I)
    h, mi = int(m.group(1)) % 12, int(m.group(2) or 0)
    if m.group(3).lower() == 'p':
        h += 12
    return f'{h:02d}:{mi:02d}'


def _ages(lo: int, hi: int) -> List[str]:
    out = []
    if lo <= 2:
        out.append('Babies (0-2)')
    if lo <= 5 and hi >= 3:
        out.append('Toddlers (3-5)')
    if lo <= 8 and hi >= 6:
        out.append('Kids (6-8)')
    if hi >= 10:
        out.append('Preteens (9-12)')
    return out or ['All Ages']


class KidPagesScraper:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers['User-Agent'] = UA

    def _get(self, url: str) -> str:
        time.sleep(1.0)
        r = self.s.get(url, timeout=20)
        r.raise_for_status()
        return r.text

    # ---- Arts Etobicoke -------------------------------------------------
    def arts_etobicoke(self, today: date) -> List[Dict]:
        base = 'https://www.artsetobicoke.com/ae-events/'
        links = sorted(set(re.findall(r'href="(https://www\.artsetobicoke\.com/events/[^"]+)"', self._get(base))))
        out = []
        for url in links:
            slug = url.rstrip('/').rsplit('/', 1)[-1].replace('-', ' ')
            if not KID_TITLE.search(slug) or re.search(r'senior|youth music', slug, re.I):
                continue
            t = _text(self._get(url))
            title_m = re.search(r'^(.*?)\s+-\s+(?:Spring|Fall|Winter|Summer)', t.split('\n')[1] if '\n' in t else '', re.I)
            head = t.split('\n')[1] if '\n' in t else slug
            title = re.sub(r'\s+\|\s+Arts Etobicoke$', '', re.sub(r'\s+-\s+(Spring|Fall|Winter|Summer)\s+\d{4}$', '', head)).strip() or slug.title()
            age_m = re.search(r'ages?\s+(\d+)\s*[–-]\s*(\d+)', t, re.I)
            lo, hi = (int(age_m.group(1)), int(age_m.group(2))) if age_m else (4, 12)
            when = re.search(r'When:\s*\n?\s*[A-Za-z]+,?\s*([A-Za-z0-9 ,]+?),\s*(\d{1,2}(?::\d{2})?\s*[ap]m)\s*(?:to|[–-])\s*(\d{1,2}(?::\d{2})?\s*[ap]m)', t)
            if when:
                yr = int((re.search(r'\n(20\d\d)\n', t) or re.search(r'(20\d\d)', t)).group(1))
                dts, mth = [], None
                for tok in re.findall(r'[A-Za-z]+|\d{1,2}', when.group(1)):
                    if tok.lower() in MONTHS:
                        mth = MONTHS[tok.lower()]
                    elif tok.isdigit() and mth:
                        dts.append(date(yr, mth, int(tok)))
                cost = re.search(r'Cost:\s*\n?\s*([^\n]+)', t)
                ages2 = re.search(r'Ages?:\s*(\d+)\s*(?:to|[–-])\s*(\d+)', t)
                lo2, hi2 = (int(ages2.group(1)), int(ages2.group(2))) if ages2 else (lo, hi)
                desc2 = re.search(r'\n(In this[^\n]{40,300}|[^\n]{80,300})\n', t)
                for d in dts:
                    if d >= today:
                        out.append({
                            'title': title, 'description': (desc2.group(1) if desc2 else title)[:300], 'category': 'Arts', 'icon': '🎨',
                            'date': d.isoformat(), 'start_time': _t24(when.group(2)), 'end_time': _t24(when.group(3)),
                            'venue': {'name': 'Arts Etobicoke Storefront Gallery', 'address': '4893A Dundas St W, Etobicoke, ON M9A 1B2',
                                      'neighborhood': 'Etobicoke', 'lat': 43.6504, 'lng': -79.5262},
                            'age_groups': _ages(lo2, hi2), 'indoor_outdoor': 'Indoor', 'organized_by': 'Arts Etobicoke',
                            'website': url, 'price': ('Series: ' + cost.group(1).strip()) if cost else None, 'is_free': False if cost else None,
                            'source': 'ArtsEtobicoke', 'scraped_at': datetime.now().isoformat(),
                        })
                continue
            time_m = re.search(r'Time:\s*\n?\s*(\d{1,2}(?::\d{2})?\s*[ap]m)\s*[–-]\s*(\d{1,2}(?::\d{2})?\s*[ap]m)', t, re.I)
            if not time_m:
                continue
            tail = t.split('Upcoming Dates:')[1] if 'Upcoming Dates:' in t else ''
            tail = tail.split('Registration is still open')[0]
            dates = []
            for d, mth, y in re.findall(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', tail):
                if mth.lower() in MONTHS:
                    dates.append(date(int(y), MONTHS[mth.lower()], int(d)))
            desc_m = re.search(r'\n([^\n]{60,400})\n', t)
            desc = desc_m.group(1) if desc_m else title
            for d in dates:
                if d < today:
                    continue
                out.append({
                    'title': title, 'description': desc[:300], 'category': 'Arts', 'icon': '🎨',
                    'date': d.isoformat(), 'start_time': _t24(time_m.group(1)), 'end_time': _t24(time_m.group(2)),
                    'venue': {'name': 'Arts Etobicoke Storefront Gallery', 'address': '4893A Dundas St W, Etobicoke, ON M9A 1B2',
                              'neighborhood': 'Etobicoke', 'lat': 43.6504, 'lng': -79.5262},
                    'age_groups': _ages(lo, hi), 'indoor_outdoor': 'Indoor', 'organized_by': 'Arts Etobicoke',
                    'website': url, 'price': None, 'is_free': None, 'source': 'ArtsEtobicoke',
                    'scraped_at': datetime.now().isoformat(),
                })
        return out

    # ---- Evergreen Children's Garden -----------------------------------
    def evergreen_garden(self, today: date) -> List[Dict]:
        url = 'https://www.evergreen.ca/evergreen-brick-work/activities/the-childrens-garden/'
        t = _text(self._get(url))
        i = t.find('garden parties')
        seg = t[i:i + 600] if i >= 0 else ''
        out = []
        for mth, d, y, a, b in re.findall(
                r'(?:Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day,\s+([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})\s+from\s+(\d{1,2}(?::\d{2})?\s*[ap]m)-(\d{1,2}(?::\d{2})?\s*[ap]m)', seg):
            if mth.lower() not in MONTHS:
                continue
            dt = date(int(y), MONTHS[mth.lower()], int(d))
            if dt < today:
                continue
            out.append({
                'title': "Garden Party: seasonal crafts & play at the Children's Garden",
                'description': "Seasonal crafts and play in the Children's Garden at Evergreen Brick Works.",
                'category': 'Nature', 'icon': '🌱', 'date': dt.isoformat(), 'start_time': _t24(a), 'end_time': _t24(b),
                'venue': {'name': "Children's Garden, Evergreen Brick Works", 'address': '550 Bayview Ave, Toronto, ON M4W 3X8',
                          'neighborhood': 'Don Valley', 'lat': 43.6847, 'lng': -79.3659},
                'age_groups': ['Toddlers (3-5)', 'Kids (6-8)', 'Preteens (9-12)'], 'indoor_outdoor': 'Outdoor',
                'organized_by': 'Evergreen', 'website': url, 'price': None, 'is_free': None, 'source': 'EvergreenBrickWorks',
                'scraped_at': datetime.now().isoformat(),
            })
        return out

    def fetch_by_source(self) -> Dict[str, List[Dict]]:
        today = date.today()
        res = {}
        for name, fn in (('ArtsEtobicoke', self.arts_etobicoke), ('EvergreenBrickWorks', self.evergreen_garden)):
            try:
                res[name] = fn(today)
                print(f'   ✅ {name}: {len(res[name])} events')
            except Exception as e:
                print(f'   ❌ {name}: {e}')
                res[name] = []
        return res


if __name__ == '__main__':
    for src, evs in KidPagesScraper().fetch_by_source().items():
        print(src, len(evs))
        for e in evs:
            print('  ', e['date'], e['start_time'], e['end_time'], e['title'], e['age_groups'])
