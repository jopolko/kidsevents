"""Toronto Parks & Recreation drop-in programs (kids), recurrence-expanded.
Rewritten 2026-06-11: old parser used only First Date, so ongoing programs that
started before today were dropped entirely and recurring ones emitted one date.
Now expands weekly recurrences within the window; caps Swim so it can't flood.
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict


class ParksRecScraper:
    DROPIN = "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/1a5be46a-4039-48cd-a2d2-8e702abf9516/resource/067b41e7-ac8a-4d3f-ad08-089f8cd70316/download/drop-in.json"
    LOCS = "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/1a5be46a-4039-48cd-a2d2-8e702abf9516/resource/87f95a5a-184f-4df5-ad37-84bcc1ea99a9/download/locations.json"
    UA = {"User-Agent": "Mozilla/5.0 (TorontoKidsEvents/1.0)"}
    SWIM_CAP = 120

    DOW = {'mon': 0, 'monday': 0, 'tue': 1, 'tues': 1, 'tuesday': 1, 'wed': 2, 'wednesday': 2,
           'thu': 3, 'thur': 3, 'thurs': 3, 'thursday': 3, 'fri': 4, 'friday': 4,
           'sat': 5, 'saturday': 5, 'sun': 6, 'sunday': 6}

    def _get(self, url):
        r = requests.get(url, headers=self.UA, timeout=90)
        d = r.json()
        return d if isinstance(d, list) else d.get('result', {}).get('records', d)

    @staticmethod
    def _int(v):
        try: return int(v)
        except Exception: return 0

    @staticmethod
    def _date(s):
        try: return datetime.strptime((s or '')[:10], '%Y-%m-%d').date()
        except Exception: return None

    def _weekdays(self, s):
        out = set()
        for tok in (s or '').replace('/', ',').replace('&', ',').replace(' and ', ',').split(','):
            t = tok.strip().lower()
            if t in self.DOW: out.add(self.DOW[t])
        return out

    def fetch_events(self, days_ahead: int = 14) -> List[Dict]:
        print("🏃 Fetching Parks & Rec drop-in programs (recurrence-expanded)...")
        try:
            programs = self._get(self.DROPIN)
            locs = {str(L.get('Location ID')): L for L in self._get(self.LOCS)}
        except Exception as e:
            print(f"   ❌ ParksRec fetch error: {e}")
            return []
        today = datetime.now().date()
        end = today + timedelta(days=days_ahead)
        events, swim = [], 0
        for p in programs:
            try:
                am = p.get('Age Max')
                if not am or am == 'None' or int(am) > 17:
                    continue
                title = (p.get('Course Title') or '').strip()
                if not title:
                    continue
                section = p.get('Section') or ''
                is_swim = 'swim' in title.lower() or 'swim' in section.lower()
                fd = self._date(p.get('First Date'))
                if not fd:
                    continue
                ld = self._date(p.get('Last Date')) or fd
                days = self._weekdays(p.get('DayOftheWeek'))
                lo, hi, occ, d = max(fd, today), min(ld, end), [], None
                d = lo
                while d <= hi:
                    if not days or d.weekday() in days:
                        occ.append(d)
                    d += timedelta(days=1)
                if not occ and today <= fd <= end:
                    occ = [fd]
                for od in occ:
                    if is_swim:
                        if swim >= self.SWIM_CAP:
                            break
                        swim += 1
                    events.append(self._mk(p, locs, od, title, section))
            except Exception:
                continue
        print(f"   ✅ Found {len(events)} Parks & Rec events ({swim} swim, capped at {self.SWIM_CAP})")
        return events

    def _mk(self, p, locs, od, title, section):
        loc = locs.get(str(p.get('Location ID')), {})
        name = loc.get('Location Name', 'Parks & Rec Centre')
        parts = [loc.get(k, '') for k in ('Street No', 'Street Name', 'Street Type', 'Street Direction')]
        addr = ' '.join(x for x in parts if x and x != 'None')

        def hm(h, m):
            try: return f"{int(h):02d}:{int(m or 0):02d}"
            except Exception: return ''
        cat, icon = self._categorize_program(title, section)
        return {
            'title': title,
            'description': f"Free drop-in program at {name}. {section}.",
            'category': cat, 'icon': icon,
            'date': od.strftime('%Y-%m-%d'),
            'start_time': hm(p.get('Start Hour'), p.get('Start Minute')) or '09:00',
            'end_time': hm(p.get('End Hour'), p.get('End Min')),
            'venue': {'name': name, 'address': f"{addr}, Toronto, ON" if addr else f"{name}, Toronto, ON",
                      'neighborhood': loc.get('District', 'Toronto'), 'lat': None, 'lng': None, 'phone': None},
            'age_groups': self._get_age_groups(self._int(p.get('Age Min')), self._int(p.get('Age Max'))),
            'indoor_outdoor': self._get_indoor_outdoor(loc.get('Location Type', '')),
            'organized_by': 'City of Toronto Parks & Recreation',
            'website': 'https://www.toronto.ca/data/parks/prd/index.html',
            'source': 'ParksRec',
            'scraped_at': datetime.now().isoformat(),
        }

    @staticmethod
    def _get_age_groups(amin, amax):
        g = []
        if amin <= 2: g.append('Babies (0-2)')
        if amin <= 5 and amax >= 3: g.append('Toddlers (3-5)')
        if amax >= 6 and amin <= 12: g.append('Kids (6-12)')
        if amax >= 13: g.append('Teens (13+)')
        return g or ['All Ages']

    @staticmethod
    def _categorize_program(title, section):
        t, s = title.lower(), section.lower()
        if any(w in t for w in ['sport', 'basketball', 'soccer', 'hockey', 'swim', 'skat', 'tennis', 'badminton', 'gym', 'ball']):
            return ('Sports', '⚽')
        if any(w in t for w in ['art', 'craft', 'paint', 'draw', 'music', 'dance', 'drama', 'theatre', 'pottery']):
            return ('Arts', '🎨')
        if any(w in t or w in s for w in ['learn', 'early years', 'homework', 'stem', 'science', 'reading', 'cooking']):
            return ('Learning', '📚')
        if any(w in t for w in ['play', 'fun', 'recreation', 'games', 'lego']):
            return ('Play', '🎮')
        if any(w in t for w in ['nature', 'outdoor', 'garden', 'hiking']):
            return ('Nature', '🌳')
        return ('Play', '🎮')

    @staticmethod
    def _get_indoor_outdoor(location_type):
        return 'Outdoor' if any(w in (location_type or '').lower() for w in ['park', 'field', 'outdoor', 'trail', 'pool']) else 'Indoor'


if __name__ == '__main__':
    import collections
    evs = ParksRecScraper().fetch_events()
    print("TOTAL:", len(evs))
    print("by category:", dict(collections.Counter(e['category'] for e in evs)))
    print("sample:", {k: evs[0][k] for k in ('title', 'date', 'start_time', 'category')} if evs else None)
