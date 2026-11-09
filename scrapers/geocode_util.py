"""Cached Nominatim geocoding (1 req/s, polite UA). Cache: biblio_geocode_cache.json (shared by all platform connectors)."""
import json, time
from pathlib import Path
import requests
_P = Path(__file__).with_name("biblio_geocode_cache.json")
try: _C = json.load(open(_P, encoding="utf-8"))
except Exception: _C = {}

def geocode(addr: str):
    if not addr: return None
    if addr in _C: return _C[addr]
    try:
        j = requests.get("https://nominatim.openstreetmap.org/search", params={"q": addr, "format": "json", "limit": 1, "countrycodes": "ca"},
                         headers={"User-Agent": "TorontoKidsEvents/1.0 (mjopolko@gmail.com)"}, timeout=20).json()
    except Exception:
        return None
    _C[addr] = [float(j[0]["lat"]), float(j[0]["lon"])] if j else None
    json.dump(_C, open(_P, "w", encoding="utf-8")); time.sleep(1.1)
    return _C[addr]
