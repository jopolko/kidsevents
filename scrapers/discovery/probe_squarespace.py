"""Probe Squarespace venues for an events collection (?format=json) with upcoming items.  -> data/probe_sqsp.jsonl"""
import json, concurrent.futures as cf, httpx
UA = {"User-Agent": "Mozilla/5.0 (compatible; kidsevents-research/1.0; mjopolko@gmail.com)"}
rows = [json.loads(l) for l in open("data/probe.jsonl", encoding="utf-8")]
hosts = [r for r in rows if "squarespace" in r["sig"] and not r.get("err")]
PATHS = ["/events", "/calendar", "/whats-on", "/upcoming-events", "/programs", "/event-calendar", "/classes", "/workshops", "/shows"]
def go(r):
    out = {"host": r["host"], "names": r["names"][:1], "lat": r["lat"], "lng": r["lng"], "feeds": []}
    try:
        with httpx.Client(headers=UA, follow_redirects=True, timeout=12) as c:
            base = str(c.get(r["url"]).url).split("/", 3)[:3]; base = "/".join(base)
            for p in PATHS:
                try:
                    x = c.get(base + p, params={"format": "json"})
                    if x.status_code == 200 and x.headers.get("content-type", "").startswith("application/json"):
                        j = x.json(); up = j.get("upcoming") or []
                        if up or j.get("collection", {}).get("typeName") == "events":
                            out["feeds"].append({"path": p, "upcoming": len(up), "sample": [i.get("title") for i in up[:3]]})
                except Exception: pass
    except Exception as e: out["err"] = type(e).__name__
    return out
with open("data/probe_sqsp.jsonl", "w") as f, cf.ThreadPoolExecutor(6) as ex:
    for o in ex.map(go, hosts):
        f.write(json.dumps(o) + "\n")
        for fd in o["feeds"]:
            if fd["upcoming"]: print(o["host"], fd["path"], fd["upcoming"], fd["sample"], flush=True)
print("probed", len(hosts))
