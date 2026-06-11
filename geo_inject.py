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

meta_desc = (f"Free and low-cost kids events in Toronto this week: {total} events at {venues} "
             f"venues ({start} to {end}) — EarlyON drop-ins, library storytimes, Parks & "
             f"Recreation programs, museum free days and more. Updated daily.")

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
SCHEMA_CAP = 200
itemlist = {"@context":"https://schema.org","@type":"ItemList",
    "name":f"Toronto Kids Events — {start} to {end}","numberOfItems":len(events),
    "itemListElement":[{"@type":"ListItem","position":i+1,"item":event_ld(e)} for i,e in enumerate(events[:SCHEMA_CAP])]}

faq = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
  {"@type":"Question","name":"What free kids events are happening in Toronto this week?",
   "acceptedAnswer":{"@type":"Answer","text":f"There are {total} free and low-cost kids and family events across Toronto this week ({start} to {end}) at {venues} venues, including EarlyON drop-in programs, Toronto Public Library storytimes and crafts, City Parks & Recreation drop-ins, and museum free days. The full daily-updated listing is at {SITE}"}},
  {"@type":"Question","name":"Where can I find free drop-in programs for toddlers in Toronto?",
   "acceptedAnswer":{"@type":"Answer","text":"Free drop-in programs for babies and toddlers (ages 0-6) run daily at Toronto's 200+ EarlyON Child and Family Centres, plus Toronto Public Library branches and City community centres. This listing aggregates them by date, age group, and neighbourhood, updated every day."}},
  {"@type":"Question","name":"How often is the Toronto kids events list updated?",
   "acceptedAnswer":{"@type":"Answer","text":"The listing is rebuilt automatically every day from official sources: the City of Toronto Open Data recreation drop-in feed, Toronto Public Library, EarlyON centres, museums, and community organizations."}}]}

intro=(f"<p><strong>Toronto kids events this week:</strong> {total} free and low-cost children's "
       f"and family events across Toronto from {start} to {end}, at {venues} venues. Aggregated "
       f"daily from official sources — EarlyON drop-in centres, Toronto Public Library, City of "
       f"Toronto Parks &amp; Recreation, museums and community groups. Browse by date, age group, "
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
  "</section></noscript><!-- GEO-BODY:END -->")

head=("<!-- GEO-HEAD:START -->"
  f'<meta name="description" content="{esc(meta_desc)}">'
  f'<script type="application/ld+json">{json.dumps(itemlist)}</script>'
  f'<script type="application/ld+json">{json.dumps(faq)}</script>'
  "<!-- GEO-HEAD:END -->")

s=open(os.path.join(BASE,'index.html')).read()
s=re.sub(r'<!-- GEO-HEAD:START -->.*?<!-- GEO-HEAD:END -->','',s,flags=re.S)
s=re.sub(r'<!-- GEO-BODY:START -->.*?<!-- GEO-BODY:END -->','',s,flags=re.S)
s=s.replace('</head>',head+'</head>',1)
s=s.replace('<body>','<body>'+noscript,1)
open(os.path.join(BASE,'index.html'),'w').write(s)
print(f"GEO injected: {total} events total, {len(events[:SCHEMA_CAP])} in schema, "
      f"3 FAQ + noscript ({len(events)} events listed — full inventory)")
