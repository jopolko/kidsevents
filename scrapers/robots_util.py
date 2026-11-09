"""robots.txt gate shared by the platform connectors: fetch only what the site permits (matches prod's tribe_venues_scraper)."""
import urllib.robotparser
from urllib.parse import urlparse
import requests
UA = "TorontoKidsEvents/1.0 (mjopolko@gmail.com)"
_cache = {}

def allowed(url: str) -> bool:
    u = urlparse(url); host = u.netloc
    if host not in _cache:
        rp = urllib.robotparser.RobotFileParser()
        try:
            r = requests.get(f"{u.scheme}://{host}/robots.txt", headers={"User-Agent": UA}, timeout=10)
            rp.parse(r.text.splitlines() if r.status_code < 400 and "<html" not in r.text[:200].lower() else [])
        except Exception:
            rp.parse([])
        _cache[host] = rp
    return _cache[host].can_fetch(UA, url) or _cache[host].can_fetch("*", url)
