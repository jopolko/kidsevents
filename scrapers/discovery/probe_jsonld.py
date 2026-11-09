"""Count schema.org Event JSON-LD on each venue's own event pages (the pages fingerprint_deep visited).  -> data/jsonld.jsonl"""
import json, re, concurrent.futures as cf, httpx
UA = {"User-Agent": "Mozilla/5.0 (compatible; kidsevents-research/1.0; mjopolko@gmail.com)"}
LD = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.I | re.S)
def events(node, out):
    if isinstance(node, list): [events(x, out) for x in node]
    elif isinstance(node, dict):
        t = node.get("@type"); ts = t if isinstance(t, list) else [t]
        if any(isinstance(x, str) and x.endswith("Event") for x in ts) and node.get("startDate"): out.append(node)
        for k in ("@graph", "itemListElement", "item", "event", "subEvent"): 
            if k in node: events(node[k], out)
def go(r):
    found, pages = [], []
    try:
        with httpx.Client(headers=UA, follow_redirects=True, timeout=12) as c:
            for u in r["pages"][:4]:
                try: h = c.get(u).text
                except Exception: continue
                got = []
                for m in LD.finditer(h):
                    try: events(json.loads(m.group(1)), got)
                    except Exception: pass
                if got: found += got; pages.append(u)
    except Exception: pass
    return {"host": r["host"], "names": r["names"][:1], "n": len(found), "pages": pages[:2], "sample": [(e.get("name"), e.get("startDate")) for e in found[:3]]}
rows = [json.loads(l) for l in open("data/fp_deep.jsonl")]
rows = [r for r in rows if "jsonld_event" in r["sig"] or any(k in r["sig"] for k in ("tessitura", "patronmanager", "eventbrite", "tickettailor", "showpass", "ticketmaster"))]
print(len(rows), "candidate sites")
with open("data/jsonld.jsonl", "w") as f, cf.ThreadPoolExecutor(8) as ex:
    for o in ex.map(go, rows):
        f.write(json.dumps(o) + "\n")
        if o["n"]: print(o["host"][:30].ljust(30), o["n"], o["sample"][:2], flush=True)
