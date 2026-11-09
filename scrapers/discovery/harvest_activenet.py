"""All ActiveNet (anc.ca.apm.activecommunities.com/{org}) tenants seen by the Internet Archive; probe each for kid activities in the next 60 days.
-> data/activenet_tenants.json"""
import json, re, time, httpx, concurrent.futures as cf
from datetime import date, timedelta
UA = {"User-Agent": "kidsevents-research/1.0 (venue discovery; mjopolko@gmail.com)"}
slugs, resume, fails = set(), None, 0
while fails < 8:
    p = {"url": "anc.ca.apm.activecommunities.com", "matchType": "host", "fl": "original", "collapse": "urlkey", "limit": "5000", "showResumeKey": "true"}
    if resume: p["resumeKey"] = resume
    try:
        r = httpx.get("https://web.archive.org/cdx/search/cdx", params=p, headers=UA, timeout=180)
        if r.status_code != 200: raise httpx.HTTPError(str(r.status_code))
        rows = [l.strip() for l in r.text.rstrip("\n").split("\n")]
        resume = rows[-1] if len(rows) > 2 and rows[-2] == "" else None
        for u in rows:
            m = re.match(r"https?://anc\.ca\.apm\.activecommunities\.com(?::\d+)?/([A-Za-z0-9_-]+)(?:/|$|\?)", u)
            if m and m.group(1).lower() not in ("rest", "static", "assets", "content", "images", "css", "js", "favicon.ico"): slugs.add(m.group(1))
        print(len(slugs), "tenants", flush=True); fails = 0
        if not resume: break
        time.sleep(1.5)
    except Exception as e:
        fails += 1; print("retry", fails, str(e)[:40], flush=True); time.sleep(min(60, 8 * fails))
for l in open("data/fp_deep.jsonl"):
    for v in json.loads(l)["vendors"]:
        m = re.match(r"anc\.ca\.apm\.activecommunities\.com/([A-Za-z0-9_-]+)", v)
        if m: slugs.add(m.group(1))
print("candidates:", len(slugs), sorted(slugs)[:60])
H = {"User-Agent": "Mozilla/5.0 (compatible; kidsevents-research/1.0; mjopolko@gmail.com)", "Accept": "application/json", "Content-Type": "application/json;charset=utf-8"}
def body(a, b, d1, d2):
    return {"activity_search_pattern": {"skills": [], "time_after_str": "", "days_of_week": "0000000", "activity_select_param": 2, "center_ids": [], "time_before_str": "", "open_spots": None, "activity_id": None, "activity_category_ids": [], "date_before": d2, "min_age": a, "date_after": d1, "activity_type_ids": [], "site_ids": [], "for_map": False, "geographic_area_ids": [], "season_ids": [], "activity_department_ids": [], "activity_other_category_ids": [], "child_season_ids": [], "activity_keyword": "", "instructor_ids": [], "max_age": b, "custom_price_from": "", "custom_price_to": ""}, "activity_transfer_pattern": {}}
d1, d2 = date.today().isoformat(), (date.today() + timedelta(days=60)).isoformat()
def probe(s):
    try:
        r = httpx.post(f"https://anc.ca.apm.activecommunities.com/{s}/rest/activities/list?locale=en-US", headers=H, json=body(0, 12, d1, d2), timeout=30)
        if r.status_code == 200:
            j = r.json(); n = j["headers"]["page_info"]["total_records"]
            cs = httpx.get(f"https://anc.ca.apm.activecommunities.com/{s}/rest/activities/filters?locale=en-US", headers=H, timeout=20).json()["body"].get("centers", [])
            return s, n, [c["desc"] for c in cs[:4]]
    except Exception: pass
    return s, 0, []
live = {}
with cf.ThreadPoolExecutor(5) as ex:
    for s, n, cs in ex.map(probe, sorted(slugs)):
        if n: live[s] = {"kid_activities_60d": n, "centres": cs}; print(s, n, cs[:3], flush=True)
json.dump(live, open("data/activenet_tenants.json", "w"), indent=1)
print(len(live), "live tenants")
