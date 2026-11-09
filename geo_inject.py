#!/usr/bin/env python3
"""Inject GEO / AI-citation content into kidsevents index.html after each daily
aggregation. AI crawlers (ChatGPT, Perplexity, Google AI Overviews, ClaudeBot)
do NOT execute JS, so the live event list is otherwise invisible to them.
Adds: meta description, Event ItemList schema, FAQPage schema, and a crawlable
<noscript> summary of upcoming events. Idempotent (marker-wrapped)."""
import json, re, html, os
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
def load(f): return json.load(open(os.path.join(BASE, f)))
SITE = "https://joshuaopolko.com/kidsevents/"
def esc(s): return html.escape(str(s if s is not None else ''), quote=True)

meta = load('metadata.json')
data = load('events_week1.json')
events = data if isinstance(data, list) else data.get('events', data)
events = sorted(events, key=lambda e: (e.get('date',''), e.get('start_time','')))
total = meta.get('total_events', len(events))
venues = meta.get('total_venues', '')
dr = meta.get('date_range', {}); start, end = dr.get('start',''), dr.get('end','')

# ---------------------------------------------------------------------------
# Recency signal — a SELECTIVE, truthful "new this week" count. AI assistants
# (and parents) reward recency contrast far more than a static "1001 events".
# We persist a signature->first-seen map and count events first observed in the
# last NEW_WINDOW_DAYS. Cold-start guard: until the store has at least one prior
# day of depth we show nothing (otherwise day-1 would flag the whole inventory
# as "new"). No standard Event schema property fits "date added", so this lives
# in VISIBLE copy + a curated list, never the noscript-only block.
import datetime as _dt
SEEN_PATH = os.path.join(BASE, 'seen_events.json')
NEW_WINDOW_DAYS = 7
_gen = meta.get('generated_at') or f"{start}T06:00:00+00:00"
gen_date_str = (_gen[:10] or start)

def _sig(e):
    v = e.get('venue') or {}
    return "|".join([str(e.get('title') or ''), str(e.get('date') or ''),
                     str(v.get('name') or ''), str(e.get('start_time') or '')])

def _days_between(a, b):
    try: return (_dt.date.fromisoformat(b) - _dt.date.fromisoformat(a)).days
    except Exception: return 999

try: _raw_seen = json.load(open(SEEN_PATH))
except Exception: _raw_seen = {}
_prior_sigs = _raw_seen.get('sigs', {})
_first_run = _raw_seen.get('first_run', gen_date_str)
_new_sigs = {}
for _e in events:                       # carry forward first-seen; prune vanished events
    _sg = _sig(_e); _new_sigs[_sg] = _prior_sigs.get(_sg, gen_date_str)
json.dump({'first_run': _first_run, 'sigs': _new_sigs}, open(SEEN_PATH, 'w'))
_trust_recency = _days_between(_first_run, gen_date_str) >= 1   # need >=1 day of history
new_events = ([e for e in events if _days_between(_new_sigs[_sig(e)], gen_date_str) <= NEW_WINDOW_DAYS]
              if _trust_recency else [])
new_events = sorted(new_events, key=lambda e: (e.get('date',''), e.get('start_time','')))
n_new = len(new_events)

meta_desc = (f"Hand-picked kids and family events in Toronto this week: {total} museum days, "
             f"gallery and nature programs, festivals and family outings worth the trip at {venues} "
             f"venues ({start} to {end}). Free and low-cost, updated daily.")

def event_ld(e):
    v = e.get('venue') or {}
    d = {"@type":"Event","name":e.get('title'),
         "startDate":f"{e.get('date')}T{e.get('start_time') or '09:00'}:00-04:00",
         "eventStatus":"https://schema.org/EventScheduled",
         "eventAttendanceMode":"https://schema.org/OfflineEventAttendanceMode",
         "location":{"@type":"Place","name":v.get('name') or 'Toronto',
            "address":{"@type":"PostalAddress","streetAddress":v.get('address') or 'Toronto, ON',
            "addressLocality":"Toronto","addressRegion":"ON","addressCountry":"CA"}},
         "isAccessibleForFree":True,
         "organizer":{"@type":"Organization","name":e.get('organized_by') or 'Community'}}
    if e.get('end_time'): d["endDate"]=f"{e.get('date')}T{e['end_time']}:00-04:00"
    if e.get('description'): d["description"]=e['description'][:300]
    if e.get('website'): d["url"]=e['website']
    return d

# Schema carries a bounded sample (full Event objects are heavy ~450B each);
# the <noscript> below carries the COMPLETE list so non-JS AI crawlers see
# every event, not a slice. numberOfItems still reports the true total.
# Capped at 50 (was 200): 200 events inflated the inline JSON-LD to ~177KB,
# a third of the 503KB HTML and a real mobile parse/LCP cost. A 50-item
# sample is ample for structured-data eligibility, and the noscript full
# list keeps crawler coverage at 100%. (perf pass 2026-06-18)
SCHEMA_CAP = 50
itemlist = {"@context":"https://schema.org","@type":"ItemList",
    "name":f"Toronto Kids Events — {start} to {end}","numberOfItems":len(events),
    "itemListElement":[{"@type":"ListItem","position":i+1,"item":event_ld(e)} for i,e in enumerate(events[:SCHEMA_CAP])]}

faq = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
  {"@type":"Question","name":"What kids events are happening in Toronto this week?",
   "acceptedAnswer":{"@type":"Answer","text":f"This week ({start} to {end}) there are {total} hand-picked kids and family events across Toronto: museum and gallery programs, nature centres and outdoor outings, festivals, and special venue programming worth the trip. The full daily-updated listing is at {SITE}"}},
  {"@type":"Question","name":"Are kids events in Toronto free?",
   "acceptedAnswer":{"@type":"Answer","text":"Many are free: museum free days, nature walks, festivals and gallery programs. Some museums and attractions charge a small admission, often just a few dollars. Every listing names the venue so you can check before you go. The focus is on events worth a trip, free or low-cost."}},
  {"@type":"Question","name":"How often is the Toronto kids events list updated?",
   "acceptedAnswer":{"@type":"Answer","text":"The listing is rebuilt automatically every day from Toronto's museums, galleries, nature centres, festivals and cultural venues, plus City of Toronto Open Data. Past events drop off; new ones appear as venues publish them."}}]}

_new_clause = (f" <strong>{n_new} were newly added in the past week.</strong>" if n_new else "")
intro=(f"<p><strong>Toronto kids events this week:</strong> {total} hand-picked children's "
       f"and family events across Toronto from {start} to {end}, at {venues} venues.{_new_clause} Curated "
       f"daily from Toronto's museums, galleries, nature centres, festivals and cultural venues: "
       f"the outings worth the trip, free and low-cost. Browse by date, age group, "
       f"category and neighbourhood.</p>")
# FULL event list (not a slice) — this is the crawlable inventory AI assistants
# read. Each row carries title, date/time, venue, category and age groups so the
# page can answer specific "kids event in <area> for <age> on <date>" queries.
rows="\n".join(
  f"<li><strong>{esc(e.get('title'))}</strong> - {esc(e.get('date'))} {esc(e.get('start_time'))}, "
  f"{esc((e.get('venue') or {}).get('name'))} ({esc(e.get('category'))}; "
  f"{esc(', '.join(e.get('age_groups',[])))})</li>" for e in events)
noscript=("<!-- GEO-BODY:START --><noscript>"
  f"<section><h2>Upcoming Toronto Kids Events ({esc(start)} to {esc(end)})</h2>{intro}<ul>{rows}</ul>"
  "<h2>Frequently asked questions</h2>"
  f"<h3>What free kids events are happening in Toronto this week?</h3><p>{esc(faq['mainEntity'][0]['acceptedAnswer']['text'])}</p>"
  f"<h3>Where can I find free drop-in programs for toddlers in Toronto?</h3><p>{esc(faq['mainEntity'][1]['acceptedAnswer']['text'])}</p>"
  f"<h3>How often is the Toronto kids events list updated?</h3><p>{esc(faq['mainEntity'][2]['acceptedAnswer']['text'])}</p>"
  "<h2>Guides</h2><ul>"
  f'<li><a href="{SITE}free-museum-days/">Free Museum Days in Toronto for Kids</a></li>'
  f'<li><a href="{SITE}neighbourhoods/">Toronto Kids Events by Neighbourhood</a></li>'
  f'<li><a href="{SITE}methodology/">Data Sources &amp; Methodology</a></li>'
  "</ul></section></noscript><!-- GEO-BODY:END -->")

# WebPage schema: carries the freshness (dateModified = today's scrape) and
# author-entity (sameAs) signals that Event/ItemList/FAQPage cannot. AI search
# weights both heavily; without this the page has no machine-readable date.
generated = meta.get('generated_at', f"{start}T06:00:00+00:00")
author = {"@type":"Person","name":"Joshua Opolko",
    "url":"https://joshuaopolko.com/",
    "sameAs":["https://www.linkedin.com/in/joshua-opolko/",
              "https://x.com/JoshuaOpolko",
              "https://github.com/jopolko"]}
webpage = {"@context":"https://schema.org","@type":"WebPage",
    "@id":SITE,"url":SITE,
    "name":"Toronto Kids Events - Weekly Listings",
    "description":meta_desc,
    "inLanguage":"en-CA",
    "datePublished":"2025-10-31",
    "dateModified":generated,
    "author":author,"publisher":author,
    "isPartOf":{"@type":"WebSite","name":"Joshua Opolko","url":"https://joshuaopolko.com/"}}

head=("<!-- GEO-HEAD:START -->"
  f'<meta name="description" content="{esc(meta_desc)}">'
  f'<link rel="canonical" href="{SITE}">'
  f'<script type="application/ld+json">{json.dumps(webpage)}</script>'
  f'<script type="application/ld+json">{json.dumps(itemlist)}</script>'
  f'<script type="application/ld+json">{json.dumps(faq)}</script>'
  "<!-- GEO-HEAD:END -->")

s=open(os.path.join(BASE,'index.html')).read()
s=re.sub(r'<!-- GEO-HEAD:START -->.*?<!-- GEO-HEAD:END -->','',s,flags=re.S)
s=re.sub(r'<!-- GEO-BODY:START -->.*?<!-- GEO-BODY:END -->','',s,flags=re.S)
# Target the </head> immediately before <body> (avoids </head> inside HTML comments)
# Use lambda so json \uXXXX sequences in head aren't misread as regex backreferences
s=re.sub(r'</head>(\s*<body)',lambda m: head+'</head>'+m.group(1),s,count=1)
s=s.replace('<body>','<body>'+noscript,1)
# Bake real stats into the week-range header slot: non-JS crawlers otherwise
# see the placeholder "Loading...". Format matches updateDateRangeHeader()'s
# JS output exactly so hydration causes no visible change or layout shift.
hr = meta.get('human_readable', {})
baked = f"<strong>{hr.get('venues', venues)} venues</strong> • {hr.get('events', total)} events this week"
s = re.sub(r'(<div id="week-range"[^>]*>).*?(</div>)', lambda m: m.group(1)+baked+m.group(2), s, count=1, flags=re.S)
open(os.path.join(BASE,'index.html'),'w').write(s)
print(f"GEO injected: {total} events total, {len(events[:SCHEMA_CAP])} in schema, "
      f"3 FAQ + noscript ({len(events)} events listed — full inventory), "
      f"WebPage dateModified={generated}, week-range baked")

# ---------------------------------------------------------------------------
# Guide pages: refresh marker-wrapped LIVE blocks daily so the editorial
# shelf carries genuinely current data (and an honest dateModified).
# Skips silently when a guide file is absent.
from collections import Counter
import datetime as _dt

hr = meta.get('human_readable', {})
today_human = hr.get('date_generated') or start
gen_date = (generated or '')[:10] or start

def _district(e):
    v = e.get('venue') or {}
    blob = f"{v.get('neighborhood','') or ''} {v.get('address','') or ''}".lower()
    if 'scarborough' in blob: return 'Scarborough'
    if 'north york' in blob: return 'North York'
    if 'etobicoke' in blob or 'york,' in blob: return 'Etobicoke York'
    return 'Toronto & East York'

def _fill(slug, blocks):
    p = os.path.join(BASE, slug, 'index.html')
    if not os.path.exists(p): return False
    s = open(p).read()
    blocks = dict(blocks)
    blocks['DATE'] = esc(today_human)
    for key, content in blocks.items():
        s = re.sub(rf'(<!-- LIVE:{key}:START -->).*?(<!-- LIVE:{key}:END -->)',
                   lambda m: m.group(1) + content + m.group(2), s, count=1, flags=re.S)
    s = re.sub(r'"dateModified": "[^"]*"', f'"dateModified": "{gen_date}"', s, count=1)
    open(p, 'w').write(s)
    return True

ey = [e for e in events if e.get('source') == 'EarlyON']
ey_centres = Counter((e.get('venue') or {}).get('name') for e in ey)
ey_rows = "".join(f"<tr><td>{esc(n)}</td><td>{c} sessions</td></tr>"
                  for n, c in ey_centres.most_common(8))
earlyon_block = (
    f"<p><strong>This week ({esc(start)} to {esc(end)}):</strong> {len(ey)} EarlyON drop-in "
    f"sessions at {len(ey_centres)} centres across Toronto are on the "
    f"<a href='https://joshuaopolko.com/kidsevents/'>tracker</a>.</p>"
    + (f"<table><tr><th>Most active centres this week</th><th>Sessions</th></tr>{ey_rows}</table>" if ey_rows else ""))

MUSEUM_SRC = {'AgaKhanMuseum', 'TorontoHistoryMuseums', 'Museums', 'MuseumFreeDays',
              'HighPark', 'EvergreenBrickWorks', 'Harbourfront'}
mu = [e for e in events if e.get('source') in MUSEUM_SRC][:6]
mu_rows = "".join(
    f"<tr><td>{esc(e.get('date'))}</td><td>{esc(e.get('title'))}</td>"
    f"<td>{esc((e.get('venue') or {}).get('name'))}</td></tr>" for e in mu)
museums_block = (
    f"<table><tr><th>Date</th><th>Upcoming museum &amp; attraction events</th><th>Venue</th></tr>{mu_rows}</table>"
    if mu_rows else "<p>New museum events are added to the tracker as sources publish them.</p>")

dist = Counter(_district(e) for e in events)
dist_rows = "".join(f"<tr><td>{esc(d)}</td><td>{c}</td></tr>" for d, c in dist.most_common())
districts_block = (
    f"<p><strong>This week's {len(events)} events by district</strong> (approximate, derived from venue records):</p>"
    f"<table><tr><th>District</th><th>Events this week</th></tr>{dist_rows}</table>")

src_count = len(set(e.get('source') for e in events))
stats_block = (
    f"<p><strong>Right now the tracker holds {hr.get('events', total)} events at "
    f"{hr.get('venues', venues)} venues</strong> from {src_count} active sources, covering "
    f"{esc(start)} to {esc(end)}. Last full rebuild: {esc(today_human)}, 6&nbsp;AM ET.</p>")

pr = [e for e in events if e.get('source') == 'ParksRec']
pr_cat = Counter(e.get('category') for e in pr)
pr_rows = "".join(f"<tr><td>{esc(c)}</td><td>{n}</td></tr>" for c, n in pr_cat.most_common())
parksrec_block = (
    f"<p><strong>This week:</strong> {len(pr)} City of Toronto Parks &amp; Recreation drop-ins on the tracker.</p>"
    f"<table><tr><th>Category</th><th>Drop-ins this week</th></tr>{pr_rows}</table>" if pr else
    "<p>Parks &amp; Recreation drop-in counts refresh every morning at 6&nbsp;AM.</p>")

done = [slug for slug, blocks in [
    ('free-museum-days', {'MUSEUMS': museums_block}),
    ('neighbourhoods',   {'DISTRICTS': districts_block}),
    ('methodology',      {'STATS': stats_block}),
] if _fill(slug, blocks)]
print(f"guides refreshed: {', '.join(done) if done else 'none found'}")

# Daily stats snapshot — accumulates history for the State-of report.
try:
    full = load('events.json')
    fev = full.get('events', full) if isinstance(full, dict) else full
except Exception:
    fev = events
snap = {"date": gen_date, "total_events": len(fev), "venues": len(set((e.get('venue') or {}).get('name') for e in fev)),
        "by_source": dict(Counter(e.get('source') for e in fev)),
        "by_category": dict(Counter(e.get('category') for e in fev)),
        "by_district": dict(Counter(_district(e) for e in fev)),
        "indoor_outdoor": dict(Counter(e.get('indoor_outdoor') for e in fev))}
hist_path = os.path.join(BASE, 'stats_history.jsonl')
lines = [l for l in (open(hist_path).read().splitlines() if os.path.exists(hist_path) else [])
         if not l.startswith('{"date": "%s"' % gen_date)]
lines.append(json.dumps(snap))
open(hist_path, 'w').write('\n'.join(lines) + '\n')
print(f"stats snapshot appended for {gen_date} ({len(lines)} days in history)")

# ---------------------------------------------------------------------------
# Editorial section — injected into the visible page between the events grid
# and the footer. Grounded in real parental search patterns; gives Google/AI
# substantial prose without touching the live-listing UX.
# ---------------------------------------------------------------------------
ey_count  = len([e for e in events if e.get('source') == 'EarlyON'])
ey_centres_count = len(set((e.get('venue') or {}).get('name') for e in events if e.get('source') == 'EarlyON'))
tpl_count = len([e for e in events if 'Library' in (e.get('source') or '')])
pr_count  = len([e for e in events if e.get('source') == 'ParksRec'])
mu_count  = len([e for e in events if e.get('source') in MUSEUM_SRC])
free_count = len([e for e in events if e.get('is_free') or e.get('price') in (None, '', '0', 'Free', 'free')])
district_counts = Counter(_district(e) for e in events)
top_district, top_district_n = district_counts.most_common(1)[0] if district_counts else ('Toronto', len(events))

stat_card = lambda n, label, sub='': (
    f'<div style="background:rgba(255,255,255,0.92);border-radius:18px;padding:20px 16px;text-align:center;'
    f'box-shadow:0 4px 20px rgba(99,102,241,0.1);border:1.5px solid rgba(99,102,241,0.1);">'
    f'<div style="font-size:2.2rem;font-weight:900;color:#4F46E5;line-height:1;">{n}</div>'
    f'<div style="font-size:0.78rem;font-weight:800;color:#6366F1;margin-top:6px;letter-spacing:.03em;text-transform:uppercase;">{label}</div>'
    + (f'<div style="font-size:0.72rem;color:#64748B;margin-top:4px;">{sub}</div>' if sub else '')
    + '</div>')

outdoor_count = len([e for e in events if (e.get('indoor_outdoor') or '').lower() == 'outdoor'])
stats_row = (
    f'<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:14px;margin-bottom:36px;">'
    + stat_card(mu_count,  'Museum &amp; arts', 'galleries, science, history')
    + stat_card(outdoor_count, 'Outdoor &amp; nature', 'parks, ravines, farms')
    + stat_card(free_count, 'Free this week',   'no admission')
    + stat_card(len(events), 'Total this week', f'{start} to {end}')
    + '</div>')

guide_card = lambda href, title, desc: (
    f'<a href="{href}" style="display:block;background:rgba(255,255,255,0.9);border-radius:16px;padding:18px 20px;'
    f'text-decoration:none;border:1.5px solid rgba(99,102,241,0.12);transition:box-shadow .2s;'
    f'box-shadow:0 2px 12px rgba(99,102,241,0.07);" '
    f'onmouseover="this.style.boxShadow=\'0 6px 24px rgba(99,102,241,0.18)\'" '
    f'onmouseout="this.style.boxShadow=\'0 2px 12px rgba(99,102,241,0.07)\'">'
    f'<div style="font-size:0.92rem;font-weight:800;color:#312E81;margin-bottom:6px;">{title}</div>'
    f'<div style="font-size:0.8rem;color:#475569;line-height:1.55;">{desc}</div>'
    f'</a>')

guides_grid = (
    f'<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin-bottom:36px;">'
    + guide_card(f'{SITE}free-museum-days/',
        '🏛️ Free Museum Days',
        'ROM third Tuesdays, AGO first Wednesdays, and other museum free-admission programs.')
    + guide_card(f'{SITE}neighbourhoods/',
        '📍 Events by Neighbourhood',
        f'How free programming is distributed across the city this week — {top_district} has the most at {top_district_n} events.')
    + '</div>')

faq_item = lambda q, a: (
    f'<div style="border-bottom:1px solid rgba(99,102,241,0.1);padding:18px 0;">'
    f'<div style="font-size:0.95rem;font-weight:800;color:#1E293B;margin-bottom:8px;">{q}</div>'
    f'<div style="font-size:0.88rem;color:#334155;line-height:1.65;">{a}</div>'
    f'</div>')

faq_block = (
    '<div style="background:rgba(255,255,255,0.88);border-radius:20px;padding:8px 24px 16px;margin-bottom:36px;">'
    '<h2 style="font-size:1.1rem;font-weight:900;color:#312E81;padding:18px 0 4px;letter-spacing:-.01em;">Common questions from Toronto parents</h2>'
    + faq_item(
        'What kind of events are on this list?',
        'Hand-picked kids and family outings across Toronto: museum and gallery programs, science and nature centres, '
        'festivals, and special venue events. This is not every drop-in in the city, it is the ones worth leaving the '
        'house for, refreshed daily.')
    + faq_item(
        'Are the events free?',
        f'Many are. This week {free_count} of {len(events)} listed events are free or no-admission. '
        'Some museums and attractions charge a small admission, usually a few dollars. Each listing names the venue '
        'so you can check before you go.')
    + faq_item(
        'How far ahead are events listed?',
        f'The current listing runs {start} to {end}. '
        'The tracker rebuilds every morning at 6 AM from Toronto\'s museums, galleries, nature centres and cultural venues. '
        'Events that have passed drop off automatically; new ones appear as venues publish them.')
    + faq_item(
        'What age groups are covered?',
        'All ages, from toddlers to teens. Every event is tagged with its age range, '
        'so use the age filter at the top of the listing to narrow down.')
    + faq_item(
        'Can I find events in my specific neighbourhood?',
        'Yes. Use the search bar to type your neighbourhood, intersection, or venue name. '
        f'Events are tagged with their venue address. This week the busiest area is {top_district} with {top_district_n} events, '
        f'followed by {", ".join(d for d, _ in district_counts.most_common(3)[1:])}.')
    + faq_item(
        'How is this different from just searching online?',
        'Most listings are either a firehose of every drop-in or a single venue\'s calendar. This one curates across all of '
        'Toronto\'s museums, galleries, nature centres and cultural venues and surfaces the distinctive things worth a trip, '
        'so you do not have to dig through a dozen sites.')
    + '</div>')

about_block = (
    '<div style="background:rgba(255,255,255,0.88);border-radius:20px;padding:24px 28px;margin-bottom:36px;">'
    '<h2 style="font-size:1.1rem;font-weight:900;color:#312E81;margin-bottom:14px;letter-spacing:-.01em;">About this listing</h2>'
    f'<p style="font-size:0.9rem;color:#334155;line-height:1.7;margin-bottom:12px;">'
    f'Toronto is full of great things to do with kids, but the good stuff is scattered across dozens of museum, '
    f'gallery, nature-centre and festival websites. This tracker pulls from those sources daily and surfaces the '
    f'outings worth the trip in one place: {len(events)} hand-picked events at {venues} venues this week.'
    f'</p>'
    f'<p style="font-size:0.9rem;color:#334155;line-height:1.7;margin-bottom:12px;">'
    f'It rebuilds every morning at 6 AM. Past events drop off automatically, and new ones appear as venues publish '
    f'them. No registration or account is required to use it.'
    f'</p>'
    f'<p style="font-size:0.9rem;color:#475569;line-height:1.7;">'
    f'Built and maintained by <a href="https://joshuaopolko.com/" style="color:#4F46E5;font-weight:700;text-decoration:none;">Joshua Opolko</a>. '
    f'Data sourced from Toronto\'s museums, galleries, nature centres and cultural venues, plus City of Toronto Open Data. '
    f'<a href="{SITE}methodology/" style="color:#4F46E5;text-decoration:none;">Full methodology →</a>'
    f'</p>'
    '</div>')

# --- Per-category editorial colour: ONE specific, data-grounded line each.
# Strictly derived from this week's records — no hype adjectives, no fabrication.
# Specific + factual is what AI assistants preferentially quote.
_color = []
_busiest_ey = ey_centres.most_common(1) if ey_centres else []
if _busiest_ey and _busiest_ey[0][1] >= 2:
    _color.append(f"Busiest EarlyON this week: <strong>{esc(_busiest_ey[0][0])}</strong> with {_busiest_ey[0][1]} drop-in sessions.")
_soon_mu = mu[0] if mu else None        # mu is already date-ordered (events are globally sorted)
if _soon_mu:
    _color.append(f"Next museum &amp; arts date: <strong>{esc(_soon_mu.get('title'))}</strong> at {esc((_soon_mu.get('venue') or {}).get('name'))} on {esc(_soon_mu.get('date'))}.")
_top_pr = pr_cat.most_common(1) if pr_cat else []
if _top_pr and _top_pr[0][0]:
    _color.append(f"Parks &amp; Rec leans <strong>{esc(_top_pr[0][0])}</strong> this week ({_top_pr[0][1]} drop-ins).")
_outdoor = len([e for e in events if (e.get('indoor_outdoor') or '').lower() == 'outdoor'])
if _outdoor >= 3:
    _color.append(f"<strong>{_outdoor}</strong> of this week's events are outdoors.")
highlights_block = ('<ul style="list-style:none;padding:0;margin:0 0 36px;display:grid;'
    'grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:10px;">'
    + "".join(f'<li style="background:rgba(255,255,255,0.85);border-radius:12px;padding:12px 16px;'
             f'font-size:0.85rem;color:#334155;line-height:1.5;border:1px solid rgba(99,102,241,0.1);">{c}</li>'
             for c in _color)
    + '</ul>') if _color else ''

# --- Computed "this week in numbers" insight: derived facts (information gain, not
# restated counts), a seasonal note, a day-rotated parent angle, and one weekend pick.
# Everything is computed from the live data, so it reads differently every rebuild and
# never becomes boilerplate. Sourced implicitly to the City Open Data feed.
def _age05(e):
    _ag = ' '.join(e.get('age_groups', []) or []).lower()
    return ('0-2' in _ag) or ('3-5' in _ag) or ('babies' in _ag) or ('toddler' in _ag)
_n05 = len([e for e in events if _age05(e)])
_pct05 = round(100 * _n05 / len(events)) if events else 0
_dist_sorted = district_counts.most_common()
_lead = _dist_sorted[0] if _dist_sorted else (top_district, top_district_n)
_lag = _dist_sorted[-1] if len(_dist_sorted) > 1 else None
_indoor = len(events) - _outdoor

_sentences = []
if _pct05:
    _sentences.append(f"<strong>{_pct05}%</strong> of this week's events are aimed at ages 0-5 (babies and toddlers).")
if _lag and _lag[0] != _lead[0]:
    _sentences.append(f"{esc(_lead[0])} has the most free programming this week ({_lead[1]} events); {esc(_lag[0])} the fewest ({_lag[1]}).")

try: _mo = _dt.date.fromisoformat(gen_date).month
except Exception: _mo = 0
_season = {
  9:  "Back-to-school season shifts the mix toward weekend programs and special events.",
  10: "Cooler weather is moving more programming indoors to museums and galleries.",
  11: "Late fall: indoor museum and gallery programming carries most of the week.",
  12: "Winter pushes programming indoors; museums and galleries lead the calendar.",
  1:  "Deep winter: indoor museum and gallery visits are the move right now.",
  2:  "Late winter: watch for March Break camps and one-off specials starting to appear.",
  3:  "March Break can spike one-off camps and special events this week.",
  4:  "Spring is reopening outdoor park and nature programming across the city.",
  5:  "Mild spring weather is bringing outdoor park and nature programming back.",
}.get(_mo, "")
if _outdoor and _mo in (6, 7, 8):
    _season = f"With summer underway, <strong>{_outdoor}</strong> outdoor sessions are on the calendar this week."

try: _day = _dt.date.fromisoformat(gen_date).toordinal()
except Exception: _day = 0
_angles = [f"<strong>Rainy-day plan:</strong> {_indoor} of this week's {len(events)} events are indoors."]
if _soon_mu: _angles.append(f"<strong>First free museum visit?</strong> The soonest is {esc(_soon_mu.get('title'))} on {esc(_soon_mu.get('date'))}.")
_angles.append(f"<strong>Neighbourhood spotlight:</strong> {esc(_lead[0])} families have {_lead[1]} free options this week.")
_angle = _angles[_day % len(_angles)] if _angles else ''

def _is_weekend(e):
    try: return _dt.date.fromisoformat(e.get('date')).weekday() >= 5
    except Exception: return False
_wk = [e for e in events if _is_weekend(e)]
_pick = _wk[0] if _wk else None
_pick_html = ''
if _pick:
    _pick_html = ('<p style="font-size:0.9rem;color:#334155;line-height:1.6;margin:0;">'
        f'🌟 <strong>Weekend pick:</strong> {esc(_pick.get("title"))} at '
        f'{esc((_pick.get("venue") or {}).get("name"))} — {esc(_pick.get("date"))}'
        + (f' {esc(_pick.get("start_time"))}' if _pick.get("start_time") else '') + '.</p>')

_lead_para = " ".join(_sentences + ([_season] if _season else []))
insight_block = ''
if _lead_para or _angle or _pick_html:
    insight_block = (
        '<div style="background:rgba(255,255,255,0.9);border-radius:18px;padding:18px 24px;margin-bottom:24px;border:1px solid rgba(99,102,241,0.12);">'
        + (f'<p style="font-size:0.95rem;color:#1E293B;line-height:1.65;margin:0 0 10px;">{_lead_para}</p>' if _lead_para else '')
        + (f'<p style="font-size:0.88rem;color:#475569;line-height:1.6;margin:0 0 {"8px" if _pick_html else "0"};">{_angle}</p>' if _angle else '')
        + _pick_html
        + '</div>')

# --- Visible "New this week" list — the single highest-value GEO block on the page:
# genuinely-new events (recency contrast), each carrying concrete date/venue/category
# (citable specifics), rendered in VISIBLE HTML so AI extractors that skip <noscript>
# still read them. Omitted entirely when there's nothing trustworthy to show.
_new_show = new_events[:12]
new_block = ''
if _new_show:
    _new_rows = "".join(
        f'<li style="padding:10px 0;border-bottom:1px solid rgba(99,102,241,0.1);font-size:0.88rem;color:#334155;line-height:1.5;">'
        f'<strong style="color:#1E293B;">{esc(e.get("title"))}</strong> — {esc(e.get("date"))}'
        + (f' {esc(e.get("start_time"))}' if e.get("start_time") else '')
        + f', {esc((e.get("venue") or {}).get("name"))}'
        + (f' <span style="color:#6366F1;">({esc(e.get("category"))})</span>' if e.get("category") else '')
        + '</li>'
        for e in _new_show)
    _more = f' <span style="font-weight:600;color:#64748B;">+{n_new - len(_new_show)} more</span>' if n_new > len(_new_show) else ''
    new_block = (
        '<div style="background:rgba(255,255,255,0.92);border-radius:20px;padding:8px 24px 18px;margin-bottom:36px;border:1.5px solid rgba(99,102,241,0.14);">'
        f'<h2 style="font-size:1.1rem;font-weight:900;color:#312E81;padding:18px 0 4px;letter-spacing:-.01em;">✨ New this week — {n_new} events added{_more}</h2>'
        f'<p style="font-size:0.82rem;color:#64748B;margin:0 0 8px;">Events first listed in the past 7 days, as of {esc(today_human)}.</p>'
        f'<ul style="list-style:none;padding:0;margin:0;">{_new_rows}</ul>'
        '</div>')

editorial_html = (
    '<section id="editorial" style="max-width:1400px;margin:48px auto 0;padding:0 20px;">'
    f'<h2 style="font-size:1rem;font-weight:900;color:#64748B;letter-spacing:.08em;text-transform:uppercase;margin-bottom:20px;">This week in Toronto — {esc(start)} to {esc(end)}</h2>'
    + stats_row
    + insight_block
    + highlights_block
    + new_block
    + '<h2 style="font-size:1rem;font-weight:900;color:#64748B;letter-spacing:.08em;text-transform:uppercase;margin-bottom:16px;">Guides for Toronto parents</h2>'
    + guides_grid
    + faq_block
    + about_block
    + '</section>')

idx_path = os.path.join(BASE, 'index.html')
s2 = open(idx_path).read()
s2 = re.sub(r'<!-- EDITORIAL:START -->.*?<!-- EDITORIAL:END -->', '', s2, flags=re.S)
s2 = s2.replace('<!-- Footer -->', '<!-- EDITORIAL:START -->' + editorial_html + '<!-- EDITORIAL:END -->\n\n    <!-- Footer -->', 1)
open(idx_path, 'w').write(s2)
print(f"editorial injected: {ey_count} EarlyON, {tpl_count} library, {pr_count} parks&rec, {mu_count} museum | top district: {top_district} ({top_district_n})")
print(f"recency: {n_new} new this week (trust={_trust_recency}, store_first_run={_first_run}), {len(_color)} colour lines, {len(_new_show)} shown in visible 'New this week'")
