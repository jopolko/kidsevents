#!/usr/bin/env python3
"""Build subscribable iCalendar feeds from events.json.

Writes calendar.ics (all curated picks) plus calendar-babies/-toddlers/-kids.ics
into the web root. Run daily after the scrape (see scrapers/run_daily_scrape.sh).
"""
import hashlib
import os
import shutil
from datetime import timedelta
from zoneinfo import ZoneInfo

import ke_curate as kc

FEEDS = {'': None, '-babies': 'babies', '-toddlers': 'toddlers', '-kids': 'kids'}
LABELS = {None: 'Toronto Kids Events', 'babies': 'Toronto Kids Events: Babies 0-2',
          'toddlers': 'Toronto Kids Events: Toddlers 3-5', 'kids': 'Toronto Kids Events: Kids 6-12'}
HORIZON_DAYS = 60
VTZ = ['BEGIN:VTIMEZONE', 'TZID:America/Toronto',
       'BEGIN:DAYLIGHT', 'TZOFFSETFROM:-0500', 'TZOFFSETTO:-0400', 'TZNAME:EDT',
       'DTSTART:19700308T020000', 'RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU', 'END:DAYLIGHT',
       'BEGIN:STANDARD', 'TZOFFSETFROM:-0400', 'TZOFFSETTO:-0500', 'TZNAME:EST',
       'DTSTART:19701101T020000', 'RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU', 'END:STANDARD',
       'END:VTIMEZONE']


def esc(s):
    return (str(s or '').replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,')
            .replace('\r', '').replace('\n', '\\n'))


def fold(line):
    """RFC 5545: fold content lines at 75 octets (continuations carry a leading space)."""
    if len(line.encode('utf-8')) <= 75:
        return line
    out, cur, cur_len = [], '', 0
    for ch in line:
        n = len(ch.encode('utf-8'))
        limit = 75 if not out else 74
        if cur_len + n > limit:
            out.append(cur)
            cur, cur_len = '', 0
        cur += ch
        cur_len += n
    out.append(cur)
    return '\r\n '.join(out)


def stamp(ds, t):
    return ds.replace('-', '') + 'T' + t.replace(':', '')[:4] + '00'


def build(events, age):
    now = kc.now_toronto()
    today = now.date().isoformat()
    horizon = (now.date() + timedelta(days=HORIZON_DAYS)).isoformat()
    evs = [e for e in kc.curated(events, age) if today <= e['date'] < horizon]
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Toronto Kids Events//joshuaopolko.com//EN',
             'CALSCALE:GREGORIAN', 'METHOD:PUBLISH', 'X-WR-CALNAME:' + esc(LABELS[age]),
             'X-WR-TIMEZONE:America/Toronto', 'REFRESH-INTERVAL;VALUE=DURATION:PT12H',
             'X-PUBLISHED-TTL:PT12H'] + VTZ
    dtstamp = now.astimezone(ZoneInfo('UTC')).strftime('%Y%m%dT%H%M%SZ')
    for e in evs:
        v = e.get('venue') or {}
        uid = hashlib.sha1(f"{e.get('id', '')}|{e['date']}|{e['title']}|{kc.venue(e)}".encode()).hexdigest()[:24]
        loc = ', '.join(x for x in (v.get('name'), v.get('address')) if x)
        site = e.get('website') or 'https://joshuaopolko.com/kidsevents/'
        desc = ((e.get('description') or '')[:400] + '\n\n' + site).strip()
        lines += ['BEGIN:VEVENT', f'UID:{uid}@joshuaopolko.com', f'DTSTAMP:{dtstamp}',
                  f"DTSTART;TZID=America/Toronto:{stamp(e['date'], e['start_time'])}",
                  f"DTEND;TZID=America/Toronto:{stamp(e['date'], kc.end_time(e))}",
                  f"SUMMARY:{esc(e['title'])}", f'LOCATION:{esc(loc)}', f'DESCRIPTION:{esc(desc)}',
                  f'URL:{site}', 'END:VEVENT']
    lines.append('END:VCALENDAR')
    return '\r\n'.join(fold(l) for l in lines) + '\r\n', len(evs)


def main():
    events = kc.load_events()
    for suffix, age in FEEDS.items():
        body, n = build(events, age)
        path = kc.ROOT / f'calendar{suffix}.ics'
        tmp = kc.ROOT / f'calendar{suffix}.ics.tmp'
        tmp.write_text(body, encoding='utf-8', newline='')
        os.replace(tmp, path)
        try:
            shutil.chown(path, group='www-data')
            os.chmod(path, 0o664)
        except Exception:
            pass
        print(f'ics: {path.name} {n} events')


if __name__ == '__main__':
    main()
