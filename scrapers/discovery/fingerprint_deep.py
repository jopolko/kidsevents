"""Deep platform fingerprint: homepage + the site's own event/calendar/program links (up to 4 pages). Records signals and the vendor URLs
found (so tenant ids can be read off them).  -> data/fp_deep.jsonl"""
import json, re, os, time, concurrent.futures as cf, httpx
from urllib.parse import urljoin, urlparse
UA = {"User-Agent": "Mozilla/5.0 (compatible; kidsevents-research/1.0; mjopolko@gmail.com)"}
# signature -> regex over html. Vendor URL capture below pulls tenant ids.
SIG = {
 "bibliocommons": r"bibliocommons\.com", "libcal": r"libcal\.com|springshare", "communico": r"communico\.(co|ca|com)|libnet\.info", "evanced": r"evanced\.info|eventsmgr|evanced",
 "assabet": r"assabetinteractive", "librarymarket": r"librarymarket|lm-events", "demco": r"demcosoftware", "tribe": r"tribe-events|the-events-calendar|tribe/events/v1",
 "mec": r"mec-wrap|modern-events-calendar", "eventon": r"eventon|evo-", "ai1ec": r"ai1ec|all-in-one-event-calendar", "events_manager": r"events-manager|em-calendar",
 "my_calendar": r"my-calendar|mc-main", "amilia": r"amilia\.com", "perfectmind": r"perfectmind|PerfectMind", "activenet": r"activecommunities\.com|activenet",
 "psp_gov": r"pspsolutions|ca\.apm\.activecommunities", "eventbrite": r"eventbrite\.(ca|com)", "universe": r"universe\.com", "tixr": r"tixr\.com", "showpass": r"showpass\.com",
 "ticketmaster": r"ticketmaster|livenation", "tickettailor": r"tickettailor", "ticketsource": r"ticketsource", "ticketleap": r"ticketleap", "eventzilla": r"eventzilla",
 "audienceview": r"audienceview", "tessitura": r"tessitura|tnew\.|/tickets/", "patronmanager": r"patronmanager|ticketing\.", "ovationtix": r"ovationtix", "artsvision": r"artsvision",
 "localist": r"localist\.com|/api/2/events", "trumba": r"trumba\.com", "simpleview": r"simpleviewinc|simpleview", "civicplus": r"civicplus|civicengage|/calendar\.aspx", "granicus": r"granicus|legistar",
 "opencities": r"opencities", "drupal_calendar": r"views-calendar|calendar-view", "tockify": r"tockify", "google_cal": r"calendar\.google\.com|calendar/embed", "calendly": r"calendly",
 "jsonld_event": r'"@type"\s*:\s*"(?:\w+Event|Event)"', "ics": r"\.ics\b|webcal:", "rss_events": r"rss.*event|event.*rss|feed.*event", "squarespace": r"squarespace", "wix": r"wixstatic",
 "wordpress": r"wp-content|wp-json", "meetup": r"meetup\.com", "mindbody": r"mindbody|healcode", "bookeo": r"bookeo", "acuity": r"acuityscheduling", "fareharbor": r"fareharbor",
 "regpro/jackrabbit": r"jackrabbitclass|regpack|campbrain|campminder|jackrabbit", "daysmart": r"daysmart|dash\.?platform", "teamsnap": r"teamsnap|leagueapps|sportsengine|playwaze",
 "eventcalendarapp": r"eventcalendarapp", "calendarwiz": r"calendarwiz", "teamup": r"teamup\.com", "timely": r"time\.ly|timely\.", "stagebuddy": r"stagebuddy|ticketscene|ticketpro",
}
VENDOR = re.compile(r"https?://([a-z0-9.-]*(?:bibliocommons|libcal|communico|libnet|evanced|assabet|perfectmind|activecommunities|amilia|eventbrite|tixr|showpass|universe|ticketsource|tickettailor|ticketleap|localist|trumba|tockify|ovationtix|ticketscene|ticketpro|time\.ly|teamup|jackrabbitclass|regpack|daysmart|leagueapps|eventzilla|audienceview)[a-z0-9.-]*\.[a-z]{2,})(/[^\s\"'<>)]{0,80})?", re.I)
EVLINK = re.compile(r"event|calendar|program|whats-?on|happening|class|camp|storytime|kids|family|workshop|register", re.I)
src = {}
for f in ("data/osm_venues.json", "data/osm_libraries.json", "data/seed_kids.json"):
    src.update(json.load(open(f)))
done = set()
if os.path.exists("data/fp_deep.jsonl"): done = {json.loads(l)["host"] for l in open("data/fp_deep.jsonl")}
def go(item):
    host, v = item
    row = {"host": host, "url": v["url"], "names": v["names"][:2], "lat": v["lat"], "lng": v["lng"], "sig": [], "vendors": [], "pages": []}
    try:
        with httpx.Client(headers=UA, follow_redirects=True, timeout=12) as c:
            r = c.get(v["url"]); base = f"{r.url.scheme}://{r.url.host}"; htmls = [r.text]; row["pages"].append(str(r.url))
            links = []
            for m in re.finditer(r'<a[^>]+href=["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', r.text, re.I | re.S):
                href, txt = m.group(1), re.sub(r"<[^>]+>", " ", m.group(2))
                if EVLINK.search(href + " " + txt) and not href.startswith(("mailto:", "tel:", "javascript:")):
                    u = urljoin(base + "/", href)
                    if urlparse(u).hostname == r.url.host and u not in links: links.append(u)
            for u in links[:3]:
                try: p = c.get(u); htmls.append(p.text); row["pages"].append(u)
                except Exception: pass
            h = "\n".join(htmls)
            row["sig"] = [k for k, p in SIG.items() if re.search(p, h, re.I)]
            row["vendors"] = sorted({m.group(1).lower() + (m.group(2) or "")[:50] for m in VENDOR.finditer(h)})[:8]
    except Exception as e: row["err"] = type(e).__name__
    time.sleep(0.15); return row
todo = [i for i in src.items() if i[0] not in done]
with open("data/fp_deep.jsonl", "a") as f, cf.ThreadPoolExecutor(8) as ex:
    for n, row in enumerate(ex.map(go, todo), 1):
        f.write(json.dumps(row) + "\n"); f.flush()
print("fingerprinted", len(todo))
