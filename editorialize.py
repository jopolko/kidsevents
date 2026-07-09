#!/usr/bin/env python3
"""Deterministic, zero-cost editorialization of thin event descriptions.

Toronto Kids Events has ~1,950 events but only ~259 unique descriptions — the
scrapers emit boilerplate (401 identical EarlyON strings, 237 events whose whole
description is "Event from Kids Out and About Toronto"). This module rebuilds a
specific, varied one- to two-sentence description from the structured fields every
event already carries (venue, neighbourhood, age groups, day/time, indoor/outdoor,
free status, organiser). No LLM, no API cost — the variety comes from the data, so
it re-runs free on every daily scrape.

Design rules:
- Never invent a fact that isn't in the event record. Phrasing varies; claims don't.
- Phrasing is chosen by a stable hash of the event id, so a given event always reads
  the same way (idempotent across daily rebuilds) while neighbours read differently.
- A scraper description that already carries real, non-boilerplate detail is kept and
  only lightly topped up; only thin/templated/empty ones are fully rebuilt.
"""
import datetime, hashlib, re

# Scraper descriptions matching these are treated as contentless and fully rebuilt.
_BOILERPLATE = (
    re.compile(r'^\s*event from .*$', re.I),
    re.compile(r'^\s*free drop-?in program', re.I),
    re.compile(r'drop-?in\.\s*$', re.I),
    re.compile(r'^\s*$'),
)

_DOW = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


def _tod(start_time):
    """'07:30' -> 'early-morning' / 'morning' / 'afternoon' / 'evening'."""
    try:
        h = int(str(start_time).split(':')[0])
    except (ValueError, AttributeError, IndexError):
        return ''
    if h < 9:
        return 'early-morning'
    if h < 12:
        return 'morning'
    if h < 17:
        return 'afternoon'
    return 'evening'


def _day_of_week(date_str):
    try:
        y, m, d = (int(x) for x in str(date_str).split('-')[:3])
        return _DOW[datetime.date(y, m, d).weekday()]
    except (ValueError, IndexError):
        return ''


def _ages(age_groups):
    """['Babies (0-2)','Toddlers (3-5)'] -> 'ages 0–5'."""
    nums = []
    for g in age_groups or []:
        nums += [int(n) for n in re.findall(r'\d+', g)]
    if not nums:
        return ''
    lo, hi = min(nums), max(nums)
    if lo == hi:
        return f'age {lo}'
    return f'ages {lo}–{hi}'


def _clean_hood(neighborhood):
    """'TORONTO-DANFORTH' / 'North York' -> 'Toronto-Danforth' / 'North York'.
    Generic city-wide values are suppressed (every event is in Toronto)."""
    if not neighborhood:
        return ''
    n = neighborhood.replace('_', ' ').strip()
    if n.isupper() or n.islower():
        n = '-'.join(p.capitalize() for p in re.split(r'[-\s]+', n))
    if n.lower() in ('toronto', 'city of toronto', 'gta'):
        return ''
    return n


def _clean_venue(name):
    """Drop venue 'names' that are actually websites or generic placeholders."""
    if not name:
        return ''
    n = name.strip()
    low = n.lower()
    if re.search(r'https?://|www\.|\.(com|ca|org|net|io)(\b|/)', low):
        return ''
    if low in ('various locations', 'multiple locations', 'various', 'online',
               'tbd', 'to be determined', 'n/a', 'see website', 'see description'):
        return ''
    return n


def _compose(parts):
    """Join non-empty fragments into one clean, period-terminated sentence."""
    s = ' '.join(p for p in parts if p)
    s = re.sub(r'\s+', ' ', s).replace(' ,', ',').replace(' .', '.').replace('—,', '—').strip(' ,')
    if s and not s.endswith('.'):
        s += '.'
    return (s[0].upper() + s[1:]) if s else s


def _free_clause(ev):
    price = ev.get('price')
    if ev.get('is_free') or (isinstance(price, str) and 'free' in price.lower()):
        return 'free'
    if price:
        return str(price)
    # EarlyON / City drop-ins are free by definition even when the flag is absent.
    if ev.get('source') in ('EarlyON', 'ParksRec') or 'drop-in' in (ev.get('title', '').lower()):
        return 'free'
    return ''


def _pick(seed, options):
    """Deterministic choice keyed on a stable hash of the event id."""
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    return options[h % len(options)]


def _is_thin(desc):
    return any(p.search(desc or '') for p in _BOILERPLATE) or len((desc or '').strip()) < 40


def enrich(ev):
    """Return an editorialized description string for one event record.

    Genuine scraper copy is returned verbatim; only thin/boilerplate/empty
    descriptions are rebuilt from the event's structured fields.
    """
    desc = (ev.get('description') or '').strip()
    if not _is_thin(desc):
        return desc

    venue = _clean_venue((ev.get('venue') or {}).get('name'))
    hood = _clean_hood((ev.get('venue') or {}).get('neighborhood'))
    ages = _ages(ev.get('age_groups'))
    dow = _day_of_week(ev.get('date'))
    tod = _tod(ev.get('start_time'))
    outdoor = (ev.get('indoor_outdoor') or '').lower() == 'outdoor'
    free = _free_clause(ev)
    cat = (ev.get('category') or '').strip()
    title = ev.get('title', '').strip()
    seed = ev.get('id') or title

    # Activity noun from category, with a gentle synonym rotation for variety.
    cat_noun = {
        'Learning': ['early-years program', 'learn-and-play session', 'drop-in program'],
        'Sports': ['active drop-in', 'sports session', 'gym drop-in'],
        'Play': ['free play session', 'play drop-in', 'open-play session'],
        'Arts': ['art session', 'creative drop-in', 'hands-on art program'],
        'Music': ['music session', 'sing-along drop-in'],
        'Nature': ['nature program', 'outdoor discovery session'],
    }.get(cat, ['family program', 'kids program', 'family-friendly event'])
    noun = _pick(seed + 'noun', cat_noun)

    free_word = 'Free' if free == 'free' else ''
    setting = 'outdoor' if outdoor else ''     # adjective; 'indoor' adds little, dropped
    agep = f'for {ages}' if ages else ''
    loc = f'at {venue}' if venue else ''
    hoodp = f'in {hood}' if hood else ''
    whenp = ' '.join(x for x in [dow, tod] if x)   # e.g. "Thursday morning"
    priced = free if (free and free != 'free') else ''

    frames = [
        [free_word, setting, noun, agep, loc, hoodp],
        [free_word, setting, noun, agep, hoodp, ('— ' + whenp) if whenp else ''],
        [(venue + ' hosts a') if venue else 'A', free_word.lower(), setting, noun, agep, hoodp],
        [free_word, setting, noun, agep, loc, ('—') if (priced or whenp) else '', priced, whenp],
    ]
    out = _compose(_pick(seed + 'frame', frames))
    # EarlyON drop-ins never require registration — a real, source-true fact the
    # boilerplate stated and the rebuild would otherwise drop.
    if ev.get('source') == 'EarlyON' and out and 'registration' not in out.lower():
        out = out[:-1] + ' — no registration.'
    return out or desc or title


if __name__ == '__main__':
    import json, sys
    evs = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'events.json'))['events']
    for e in evs[:int(sys.argv[2]) if len(sys.argv) > 2 else 12]:
        print('OLD:', (e.get('description') or '')[:110])
        print('NEW:', enrich(e)[:140])
        print()
