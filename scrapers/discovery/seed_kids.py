"""Kid-focused venue seed: names from web searches -> candidate official domains -> verified by fetching and matching the name in <title>/<h1>.
Aggregator blogs are NOT used as content; only as a source of venue names.  -> data/seed_kids.json (same shape as osm_venues.json)"""
import json, re, concurrent.futures as cf, httpx
UA = {"User-Agent": "Mozilla/5.0 (compatible; kidsevents-research/1.0; mjopolko@gmail.com)"}
# name -> (candidate urls, tokens that must appear in page title/h1)
SEEDS = {
 "Young People's Theatre": (["https://youngpeoplestheatre.org"], ["young people"]),
 "LEGOLAND Discovery Centre Toronto": (["https://www.legolanddiscoverycentre.ca/toronto/"], ["legoland"]),
 "Kortright Centre for Conservation": (["https://kortright.org", "https://www.kortright.org"], ["kortright"]),
 "Mountsberg Conservation Area": (["https://conservationhamilton.ca/mountsberg", "https://www.conservationhalton.ca/"], ["mountsberg", "conservation"]),
 "Toronto Botanical Garden": (["https://torontobotanicalgarden.ca"], ["botanical"]),
 "Riverdale Farm": (["https://www.toronto.ca/explore-enjoy/parks-gardens-beaches/farms/riverdale-farm/"], ["riverdale"]),
 "Forsythe Family Farms": (["https://forsythefamilyfarms.com", "https://www.forsythefamilyfarms.com"], ["forsythe"]),
 "Lionel's Farm": (["https://lionelsfarm.com", "https://www.lionelsfarm.com"], ["lionel"]),
 "Generations Performing Arts Centre": (["https://generationspac.com", "https://www.generationspac.com", "https://generationspac.ca"], ["generations"]),
 "McMichael Canadian Art Collection": (["https://www.mcmichael.com"], ["mcmichael"]),
 "Great Big Theatre Company": (["https://greatbigtheatre.com", "https://www.greatbigtheatre.com"], ["great big"]),
 "Toronto Circus Centre": (["https://torontocircuscentre.ca", "https://www.torontocircuscentre.ca"], ["circus"]),
 "Mad Science Toronto": (["https://www.madscience.org/toronto/", "https://madscience.org"], ["mad science"]),
 "Joe Rockheads": (["https://www.joerockheads.com", "https://joerockheads.com"], ["rock"]),
 "My Gym Markham": (["https://www.my-gym.com", "https://mygym.com"], ["gym"]),
 "Canada Music Academy": (["https://canadamusicacademy.com", "https://www.canadamusicacademy.com"], ["music"]),
 "Art One Academy": (["https://artoneacademy.com", "https://www.artoneacademy.com"], ["art"]),
 "Allegro Academy of Music and Art": (["https://allegroacademy.ca", "https://www.allegroacademy.ca"], ["allegro"]),
 "Toronto Zoo": (["https://www.torontozoo.com"], ["zoo"]),
 "Ontario Science Centre": (["https://www.ontariosciencecentre.ca"], ["science"]),
 "Royal Ontario Museum": (["https://www.rom.on.ca"], ["rom", "royal ontario"]),
 "Ripley's Aquarium": (["https://www.ripleyaquariums.com/canada/", "https://www.ripleys.com/attractions/ripleys-aquarium-of-canada"], ["aquarium"]),
 "Black Creek Pioneer Village": (["https://blackcreek.ca"], ["black creek"]),
 "Todmorden Mills": (["https://www.toronto.ca/explore-enjoy/history-art-culture/museums/todmorden-mills/"], ["todmorden"]),
 "Toronto Public Library Kids": (["https://www.tpl.ca"], ["library"]),
 "Canadian Music Centre": (["https://www.musiccentre.ca"], ["music"]),
 "Tarragon / Lorraine Kimsa": (["https://www.ypt.ca"], ["theatre"]),
 "Bruce's Mill": (["https://trca.ca/conservation/green-spaces/bruces-mill/"], ["bruce"]),
 "Rattray Marsh": (["https://rattraymarsh.com", "https://www.rattraymarsh.com"], ["rattray"]),
 "Heritage Mississauga / Benares": (["https://www.heritagemississauga.com"], ["heritage"]),
 "Markham Museum": (["https://www.markhammuseum.ca"], ["markham"]),
 "Kleinburg Doll Museum / Humber Arboretum": (["https://arboretum.humber.ca"], ["arboretum"]),
 "Scarborough Museum": (["https://www.toronto.ca/explore-enjoy/history-art-culture/museums/scarborough-museum/"], ["scarborough"]),
 "Gibson House": (["https://www.toronto.ca/explore-enjoy/history-art-culture/museums/gibson-house-museum/"], ["gibson"]),
 "Montgomery's Inn": (["https://www.toronto.ca/explore-enjoy/history-art-culture/museums/montgomerys-inn/"], ["montgomery"]),
 "Spadina Museum": (["https://www.toronto.ca/explore-enjoy/history-art-culture/museums/spadina-museum/"], ["spadina"]),
 "Casa Loma": (["https://casaloma.ca"], ["casa loma"]),
 "CN Tower": (["https://www.cntower.ca"], ["cn tower"]),
 "Hockey Hall of Fame": (["https://www.hhof.com"], ["hockey"]),
 "Toronto Island Centreville": (["https://centreisland.ca"], ["centre"]),
 "Canada's Wonderland": (["https://www.canadaswonderland.com"], ["wonderland"]),
 "Sky Zone Toronto": (["https://www.skyzone.com/ca-toronto/"], ["sky zone"]),
 "Kids Fun Zone": (["https://www.happyplanetkids.com"], ["planet"]),
 "Gymboree Play & Music": (["https://www.gymboreeclasses.ca"], ["gymboree"]),
 "Kindermusik Toronto": (["https://www.kindermusik.com"], ["kindermusik"]),
 "Toronto Children's Chorus": (["https://www.torontochildrenschorus.com"], ["chorus"]),
 "Canadian Children's Opera Company": (["https://canadianchildrensopera.com"], ["opera"]),
 "Toronto Symphony Orchestra Kids": (["https://www.tso.ca"], ["tso", "symphony"]),
 "Harbourfront Centre": (["https://www.harbourfrontcentre.com"], ["harbourfront"]),
 "Stratford/Soulpepper Kids": (["https://www.soulpepper.ca"], ["soulpepper"]),
 "Theatre Direct / Lorraine Kimsa": (["https://www.theatredirect.ca", "https://www.ypt.ca"], ["theatre"]),
 "Ontario Place": (["https://ontarioplace.com"], ["ontario place"]),
 "Evergreen Brick Works": (["https://www.evergreen.ca"], ["evergreen"]),
 "Scadding Court Community Centre": (["https://www.scaddingcourt.org"], ["scadding"]),
 "The Stop": (["https://thestop.org"], ["stop"]),
 "Toronto Children's Museum": (["https://www.torontochildrensmuseum.com"], ["children"]),
 "Bata Shoe Museum": (["https://batashoemuseum.ca"], ["bata"]),
}
def check(item):
    name, (urls, toks) = item
    for u in urls:
        try:
            r = httpx.get(u, headers=UA, follow_redirects=True, timeout=12)
            if r.status_code >= 400: continue
            t = (re.search(r"<title[^>]*>(.*?)</title>", r.text, re.I | re.S) or [None, ""])[1].lower() + " " + (re.search(r"<h1[^>]*>(.*?)</h1>", r.text, re.I | re.S) or [None, ""])[1].lower() + " " + str(r.url).lower()
            if any(k in t for k in toks): return name, str(r.url)
        except Exception: pass
    return name, None
ok, bad = {}, []
with cf.ThreadPoolExecutor(8) as ex:
    for name, url in ex.map(check, SEEDS.items()):
        if url:
            h = re.sub(r"^www\.", "", httpx.URL(url).host); ok.setdefault(h, {"url": url, "names": [], "lat": None, "lng": None})["names"].append(name)
        else: bad.append(name)
json.dump(ok, open("data/seed_kids.json", "w"), indent=0)
print(len(ok), "verified domains;", len(bad), "unresolved:", bad)
