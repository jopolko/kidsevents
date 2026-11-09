"""Venue universe from OpenStreetMap (Overpass): GTA places likely to run kids/family events, with their websites.
  python osm_venues.py  -> data/osm_venues.json"""
import json, httpx
from urllib.parse import urlparse
Q = """[out:json][timeout:180];
area["name"="Toronto"]["admin_level"="6"]->.t;
(area["name"~"^(Mississauga|Brampton|Vaughan|Markham|Richmond Hill|Oakville|Burlington|Pickering|Ajax|Whitby|Oshawa|Milton|Aurora|Newmarket)$"]["boundary"="administrative"]->.g;);
(
 nwr(area.t)["website"]["amenity"~"^(community_centre|arts_centre|theatre|library|social_centre|childcare|cinema)$"];
 nwr(area.t)["website"]["tourism"~"^(museum|zoo|aquarium|theme_park|gallery|attraction)$"];
 nwr(area.t)["website"]["leisure"~"^(playground|sports_centre|ice_rink|swimming_pool|nature_reserve|park|garden|fitness_centre|trampoline_park|indoor_play|amusement_arcade)$"];
 nwr(area.g)["website"]["amenity"~"^(community_centre|arts_centre|theatre|library)$"];
 nwr(area.g)["website"]["tourism"~"^(museum|zoo|aquarium|theme_park|gallery|attraction)$"];
 nwr(area.t)["website"]["shop"="books"];
);
out tags center;"""
import time
for attempt in range(6):
    ep = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter", "https://overpass.private.coffee/api/interpreter"][attempt % 3]
    try:
        r = httpx.post(ep, data={"data": Q}, timeout=240, headers={"User-Agent": "kidsevents-research/1.0 (mjopolko@gmail.com)"})
        r.raise_for_status(); break
    except Exception as e:
        print("retry", ep, str(e)[:60]); time.sleep(10)
else: raise SystemExit("overpass unavailable")
doms = {}
for e in r.json()["elements"]:
    t = e["tags"]; u = t["website"]
    if "//" not in u: u = "https://" + u
    h = (urlparse(u).hostname or "").removeprefix("www.")
    if not h or any(x in h for x in ("facebook.", "instagram.", "toronto.ca", "torontopubliclibrary", "tpl.ca", "ymca", "wikipedia")): continue
    c = e.get("center") or e
    doms.setdefault(h, {"url": u, "names": [], "lat": c.get("lat"), "lng": c.get("lon")})["names"].append(t.get("name", ""))
json.dump(doms, open("data/osm_venues.json", "w"), indent=0)
print(len(r.json()["elements"]), "elements ->", len(doms), "domains")
