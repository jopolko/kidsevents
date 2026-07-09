"""Toronto Public Library kids/family events via CKAN datastore_search API.
Rewritten 2026-06-11: the old /datastore/dump parse returned 0; datastore_search
gives clean named-field dict records (8,500+ rows).
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict


class TPLAPIScraper:
    RESOURCE_ID = "c73bbe54-3a48-4ada-8eef-a1a2864021e4"
    API = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/datastore_search"
    UA = {"User-Agent": "Mozilla/5.0 (compatible; TorontoKidsEvents/1.0)"}

    KID_TERMS = ['baby', 'babies', 'child', 'children', 'family', 'families', 'kid',
                 'toddler', 'preschool', 'teen', 'youth', 'all ages', 'junior',
                 'school age', 'tween', 'parent', 'storytime', 'lego']

    def fetch_events(self, days_ahead: int = 45) -> List[Dict]:
        print("📚 Fetching from Toronto Public Library (datastore API)...")
        today = datetime.now().date()
        end = today + timedelta(days=days_ahead)
        records, offset = [], 0
        try:
            while True:
                r = requests.get(self.API, headers=self.UA, timeout=60,
                                 params={'resource_id': self.RESOURCE_ID, 'limit': 5000, 'offset': offset})
                j = r.json()
                if not j.get('success'):
                    break
                batch = j['result']['records']
                records.extend(batch)
                if len(batch) < 5000 or offset > 60000:
                    break
                offset += 5000
        except Exception as e:
            print(f"   ❌ TPL fetch error: {e}")
            return []

        events = []
        for rec in records:
            try:
                title = (rec.get('Title') or '').strip()
                if not title:
                    continue
                aud = (rec.get('Audiences') or '').lower()
                etypes = rec.get('EventTypes') or ''
                hay = f"{aud} {etypes.lower()} {title.lower()}"
                if not any(t in hay for t in self.KID_TERMS):
                    continue
                # drop adult-only
                if 'adult' in aud and not any(t in aud for t in
                        ('child', 'family', 'all ages', 'teen', 'youth', 'baby', 'toddler', 'kid')):
                    continue
                d = (rec.get('StartDateLocal') or '')[:10]
                try:
                    ed = datetime.strptime(d, '%Y-%m-%d').date()
                except Exception:
                    continue
                if ed < today or ed > end:
                    continue
                if (rec.get('Status') or '').lower() in ('cancelled', 'canceled'):
                    continue
                st = rec.get('StartTime') or ''
                et = rec.get('EndTime') or ''
                loc = (rec.get('LocationName') or 'Toronto Public Library').strip()
                events.append({
                    'title': title,
                    'description': f"{etypes} at {loc}." + (f" Audiences: {rec.get('Audiences')}." if rec.get('Audiences') else ''),
                    'category': self._category(etypes),
                    'icon': '📚',
                    'date': d,
                    'start_time': st[11:16] if 'T' in st else '10:00',
                    'end_time': et[11:16] if 'T' in et else '',
                    'venue': {'name': loc, 'address': f"{loc}, Toronto, ON",
                              'neighborhood': 'Toronto', 'lat': None, 'lng': None, 'phone': None},
                    'age_groups': self._ages(aud),
                    'indoor_outdoor': 'Indoor',
                    'organized_by': 'Toronto Public Library',
                    'website': 'https://www.torontopubliclibrary.ca/programs-and-classes/',
                    'source': 'TPL',
                    'scraped_at': datetime.now().isoformat(),
                })
            except Exception:
                continue
        print(f"   ✅ Found {len(events)} TPL events")
        return events

    @staticmethod
    def _category(etypes: str) -> str:
        e = etypes.lower()
        if any(w in e for w in ('story', 'read', 'book', 'literacy', 'learn', 'stem', 'science', 'coding', 'workshop', 'class')):
            return 'Learning'
        if any(w in e for w in ('craft', 'art', 'music', 'dance', 'creat')):
            return 'Arts'
        if any(w in e for w in ('game', 'play', 'lego', 'movie', 'film')):
            return 'Play'
        return 'Learning'

    @staticmethod
    def _ages(aud: str) -> List[str]:
        a, ages = aud.lower(), []
        if any(w in a for w in ('baby', 'babies', '0-2', 'infant')):
            ages.append('Babies (0-2)')
        if any(w in a for w in ('toddler', 'preschool', '3-5')):
            ages.append('Toddlers (3-5)')
        if any(w in a for w in ('child', 'kid', 'school age', '6-12', 'grade')):
            ages.append('Kids (6-12)')
        if any(w in a for w in ('teen', 'youth', 'tween', '13')):
            ages.append('Teens (13+)')
        return ages or ['All Ages']


if __name__ == '__main__':
    evs = TPLAPIScraper().fetch_events()
    print(f"TOTAL: {len(evs)}")
    if evs:
        import json
        print(json.dumps(evs[0], indent=2)[:500])
