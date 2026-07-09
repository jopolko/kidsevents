"""Shared Jina Reader helper — proxy-fetch JS-rendered or WAF/IP-blocked pages.
Reads JINA_API_KEY from /var/secrets/nowservingto.env (group-readable by www-data)
or the JINA_API_KEY env var. Used by scrapers whose sources block the droplet.
"""
import os, json, requests

def _jina_key():
    try:
        for line in open('/var/secrets/nowservingto.env'):
            if line.startswith('JINA_API_KEY='):
                return line.split('=', 1)[1].strip()
    except Exception:
        pass
    return os.getenv('JINA_API_KEY', '')

_KEY = _jina_key()

def jina_get(url, fmt='markdown', timeout=90):
    """Fetch a URL through Jina Reader. fmt: 'markdown' | 'text' | 'html'."""
    headers = {'X-Return-Format': fmt}
    if _KEY:
        headers['Authorization'] = 'Bearer ' + _KEY
    r = requests.get('https://r.jina.ai/' + url, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.text

def jina_json(url, timeout=90):
    """Fetch a JSON endpoint through Jina (bypasses WAF/IP blocks). Robust to text wrappers."""
    txt = jina_get(url, fmt='text', timeout=timeout)
    try:
        return json.loads(txt)
    except Exception:
        starts = [p for p in (txt.find('['), txt.find('{')) if p >= 0]
        if starts:
            return json.loads(txt[min(starts):])
        raise
