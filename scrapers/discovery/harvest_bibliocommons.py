"""Every BiblioCommons tenant seen by the Internet Archive, then probe each for a live events feed.  -> data/biblio_tenants.json"""
import json, re, time, httpx, concurrent.futures as cf
UA = {"User-Agent": "kidsevents-research/1.0 (venue discovery; mjopolko@gmail.com)"}
slugs, resume, fails = set(), None, 0
while fails < 8:
    p = {"url": "bibliocommons.com", "matchType": "domain", "fl": "original", "collapse": "urlkey", "filter": "original:.*/events.*", "limit": "5000", "showResumeKey": "true"}
    if resume: p["resumeKey"] = resume
    try:
        r = httpx.get("https://web.archive.org/cdx/search/cdx", params=p, headers=UA, timeout=180)
        if r.status_code != 200: raise httpx.HTTPError(str(r.status_code))
        rows = [l.strip() for l in r.text.rstrip("\n").split("\n")]
        resume = rows[-1] if len(rows) > 2 and rows[-2] == "" else None
        for u in rows:
            m = re.match(r"https?://([a-z0-9-]+)\.bibliocommons\.com", u)
            if m and m.group(1) not in ("www", "gateway", "cor-cdn-static", "api"): slugs.add(m.group(1))
        print(len(slugs), "tenants", flush=True); fails = 0
        if not resume: break
        time.sleep(1.5)
    except Exception as e:
        fails += 1; print("retry", fails, str(e)[:40], flush=True); time.sleep(min(60, 8 * fails))
# add tenants seen in our own fingerprints
for l in open("data/fp_deep.jsonl"):
    for v in json.loads(l)["vendors"]:
        m = re.match(r"([a-z0-9-]+)\.bibliocommons\.com", v)
        if m: slugs.add(m.group(1))
print("candidates:", len(slugs))
H = {"User-Agent": "Mozilla/5.0 (compatible; kidsevents-research/1.0; mjopolko@gmail.com)", "Accept": "application/json"}
def probe(s):
    try:
        r = httpx.get(f"https://gateway.bibliocommons.com/v2/libraries/{s}/events", params={"limit": 1}, headers=H, timeout=20)
        if r.status_code == 200:
            n = r.json()["events"]["pagination"]["count"]
            return s, n
    except Exception: pass
    return s, 0
live = {}
with cf.ThreadPoolExecutor(6) as ex:
    for s, n in ex.map(probe, sorted(slugs)):
        if n: live[s] = n; print(s, n, flush=True)
json.dump(live, open("data/biblio_tenants.json", "w"), indent=1)
print(len(live), "live tenants,", sum(live.values()), "events")
