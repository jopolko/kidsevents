"""Ontario public libraries + municipal rec/culture venues with websites (OSM). -> data/osm_libraries.json"""
import json, time, httpx
from urllib.parse import urlparse
Q = """[out:json][timeout:240];
area["name"="Ontario"]["admin_level"="4"]->.o;
( nwr(area.o)["website"]["amenity"="library"]; );
out tags center;"""
for i in range(6):
    ep = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter", "https://overpass.private.coffee/api/interpreter"][i % 3]
    try:
        r = httpx.post(ep, data={"data": Q}, timeout=300, headers={"User-Agent": "kidsevents-research/1.0 (mjopolko@gmail.com)"}); r.raise_for_status(); break
    except Exception as e: print("retry", ep, str(e)[:50]); time.sleep(10)
else: raise SystemExit("overpass down")
d = {}
for e in r.json()["elements"]:
    t = e["tags"]; u = t["website"]; u = u if "//" in u else "https://" + u
    h = (urlparse(u).hostname or "").removeprefix("www.")
    if not h or any(x in h for x in ("facebook.", "instagram.", "wikipedia")): continue
    c = e.get("center") or e
    d.setdefault(h, {"url": u, "names": [], "lat": c.get("lat"), "lng": c.get("lon")})["names"].append(t.get("name", ""))
json.dump(d, open("data/osm_libraries.json", "w"), indent=0)
print(len(r.json()["elements"]), "libraries ->", len(d), "domains")
