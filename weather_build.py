#!/usr/bin/env python3
"""Fetch the Toronto daily forecast from Open-Meteo and write weather.json.

Run every few hours from cron. The page reads weather.json (same origin) to flag
wet / cold / hot days and to lead with indoor or outdoor picks accordingly.

Open-Meteo free tier is for non-commercial use and requires CC-BY 4.0 attribution
(the page shows "Weather data by Open-Meteo.com").
"""
import json
import os
import shutil
import sys
from datetime import datetime, timezone

import requests

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'weather.json')
URL = 'https://api.open-meteo.com/v1/forecast'
PARAMS = {
    'latitude': 43.6532, 'longitude': -79.3832, 'timezone': 'America/Toronto', 'forecast_days': 16,
    'daily': 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,snowfall_sum',
}

# WMO weather interpretation codes -> (icon, label)
WMO = {
    0: ('☀️', 'Sunny'), 1: ('🌤️', 'Mostly sunny'), 2: ('⛅', 'Partly cloudy'), 3: ('☁️', 'Cloudy'),
    45: ('🌫️', 'Fog'), 48: ('🌫️', 'Fog'),
    51: ('🌦️', 'Light drizzle'), 53: ('🌦️', 'Drizzle'), 55: ('🌧️', 'Heavy drizzle'),
    56: ('🌧️', 'Freezing drizzle'), 57: ('🌧️', 'Freezing drizzle'),
    61: ('🌦️', 'Light rain'), 63: ('🌧️', 'Rain'), 65: ('🌧️', 'Heavy rain'),
    66: ('🌧️', 'Freezing rain'), 67: ('🌧️', 'Freezing rain'),
    71: ('🌨️', 'Light snow'), 73: ('🌨️', 'Snow'), 75: ('❄️', 'Heavy snow'), 77: ('🌨️', 'Snow grains'),
    80: ('🌦️', 'Showers'), 81: ('🌧️', 'Showers'), 82: ('🌧️', 'Heavy showers'),
    85: ('🌨️', 'Snow showers'), 86: ('❄️', 'Heavy snow showers'),
    95: ('⛈️', 'Thunderstorms'), 96: ('⛈️', 'Thunderstorms'), 99: ('⛈️', 'Thunderstorms'),
}


def classify(hi, lo, pop, mm, snow, code):
    wet = ((pop or 0) >= 60 and (mm or 0) >= 1) or (mm or 0) >= 2 or (snow or 0) >= 1 or code in (65, 66, 67, 82, 95, 96, 99)
    cold = hi is not None and hi <= 0
    hot = hi is not None and hi >= 30
    if wet:
        kind = 'snow' if (snow or 0) >= 1 or code in (71, 73, 75, 77, 85, 86) else 'rain'
    else:
        kind = None
    return wet, cold, hot, kind


def main():
    r = requests.get(URL, params=PARAMS, timeout=20, headers={'User-Agent': 'TorontoKidsEvents/1.0 (+https://joshuaopolko.com/kidsevents/)'})
    r.raise_for_status()
    d = r.json()['daily']
    days = {}
    for i, ds in enumerate(d['time']):
        hi, lo = d['temperature_2m_max'][i], d['temperature_2m_min'][i]
        pop, mm = d['precipitation_probability_max'][i], d['precipitation_sum'][i]
        snow, code = d['snowfall_sum'][i], d['weather_code'][i]
        icon, label = WMO.get(code, ('', ''))
        wet, cold, hot, kind = classify(hi, lo, pop, mm, snow, code)
        days[ds] = {'hi': round(hi) if hi is not None else None, 'lo': round(lo) if lo is not None else None,
                    'pop': pop, 'mm': mm, 'icon': icon, 'label': label, 'wet': wet, 'cold': cold, 'hot': hot, 'kind': kind}
    out = {'generated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
           'source': 'Open-Meteo.com (CC BY 4.0)', 'days': days}
    tmp = OUT + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(out, f, separators=(',', ':'), ensure_ascii=False)
    os.replace(tmp, OUT)
    try:
        shutil.chown(OUT, group='www-data')
        os.chmod(OUT, 0o664)
    except Exception:
        pass
    print(f'weather: {len(days)} days written')


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:  # keep the previous file on failure
        print(f'weather: failed ({ex})', file=sys.stderr)
        sys.exit(1)
