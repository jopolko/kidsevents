"""Shared curation rules for kidsevents (mirrors the scoring in index.html).

Used by ics_build.py (calendar feeds) and weekly_digest.py (email).
"""
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
TZ = ZoneInfo('America/Toronto')

TIER1 = {'HighPark', 'AgaKhanMuseum', 'Harbourfront', 'ROM', 'AGO', 'MOCA', 'Museums', 'ArtGallery',
         'EvergreenBrickWorks', 'TorontoHistoryMuseums', 'BataShoeMuseum', 'GardinerMuseum', 'TextileMuseum', 'Entertainment', 'FamilyFun', 'Mississauga'}
TIER2 = {'TPL', 'KidsOutAndAbout', 'ArtsEtobicoke', 'HolisticCommunity', 'StonegateCHC', 'WestNH',
         'LikeADad', 'ChatterBlock'}
DESTINATION = re.compile(r'museum|\brom\b|science centre|gallery|zoo|aquarium|festival|exhibition|exhibit|'
                         r'luminato|planetarium|theatre|theater|concert|harbourfront|ontario science', re.I)
VAGUE = re.compile(r'various|multiple|locations|citywide|online', re.I)
AGES = {'babies': ['Babies (0-2)'], 'toddlers': ['Toddlers (3-5)'],
        'kids': ['Kids (6-8)', 'Kids (6-12)', 'Preteens (9-12)']}
KID_OK = ('Babies', 'Toddlers', 'Kids', 'Preteens')


def now_toronto():
    return datetime.now(TZ)


def tier(src):
    return 1 if src in TIER1 else 2 if src in TIER2 else 3


def is_free(e):
    p = e.get('price')
    return bool(e.get('is_free') or (isinstance(p, str) and re.search('free', p, re.I))
                or e.get('source') in ('EarlyON', 'ParksRec', 'HighPark'))


def venue(e):
    return (e.get('venue') or {}).get('name', '') or ''


def is_online(e):
    return bool(re.search(r'online|virtual|zoom', venue(e), re.I)) or not e.get('start_time') or e.get('start_time') == '00:00'


def is_mill(e):
    return tier(e.get('source')) == 3 and not DESTINATION.search(e.get('title', ''))


def is_vague(e):
    return bool(VAGUE.search(venue(e)))


def norm_title(t):
    t = re.sub(r'[^a-z ]+', ' ', (t or '').lower())
    t = re.sub(r'\b(at|the|for|with|drop|in|earlyon|centre|center|public|library|ps|caregiver|free|kids?|child|preschool)\b', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()[:32]


def age_fit(e, age):
    if not age:
        return True
    g = e.get('age_groups') or []
    if not g or 'All Ages' in g:
        return True
    return any(a in AGES[age] for a in g)


def load_events(path=None):
    d = json.loads(Path(path or ROOT / 'events.json').read_text(encoding='utf-8'))
    evs = d['events'] if isinstance(d, dict) else d
    out = []
    for e in evs:
        if not e or not e.get('date') or is_online(e):
            continue
        if 'CANCELLED' in (e.get('title') or '').upper():
            continue
        if not any(any(k in a for k in KID_OK) or a == 'All Ages' for a in (e.get('age_groups') or [])):
            continue
        out.append(e)
    out.sort(key=lambda e: (e['date'], e.get('start_time', '')))
    seen, uniq = set(), []
    for e in out:  # one per day + title + venue, like the page
        k = (e['date'], e['title'], venue(e))
        if k not in seen:
            seen.add(k)
            uniq.append(e)
    return uniq


def curated(events, age=None):
    return [e for e in events if not is_mill(e) and not is_vague(e) and age_fit(e, age)]


def scorer(events, age=None):
    freq = {}
    for e in events:
        k = norm_title(e['title'])
        freq[k] = freq.get(k, 0) + 1

    def score(e):
        s = {1: 100, 2: 45, 3: 0}[tier(e.get('source'))]
        if is_free(e):
            s += 15
        s -= min(70, (freq.get(norm_title(e['title']), 1) - 1) * 9)
        if DESTINATION.search(e.get('title', '')):
            s += 45
        if age and any(a in AGES[age] for a in (e.get('age_groups') or [])):
            s += 30
        if is_vague(e):
            s -= 80
        return s
    return score


def end_time(e):
    s = e['start_time']
    sm = int(s[:2]) * 60 + int(s[3:5])
    en = e.get('end_time')
    em = int(en[:2]) * 60 + int(en[3:5]) if en else sm + 90
    if em <= sm:
        em = sm + 90
    em = min(em, 24 * 60 - 1)
    return f'{em // 60:02d}:{em % 60:02d}'


def weekend_days(today=None):
    today = today or now_toronto().date()
    dow = (today.weekday() + 1) % 7  # Sunday=0 like JS
    if dow == 6:
        return [today, today + timedelta(days=1)]
    if dow == 0:
        return [today]
    sat = today + timedelta(days=6 - dow)
    return [sat, sat + timedelta(days=1)]
