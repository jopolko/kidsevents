#!/usr/bin/env python3
"""
Toronto Public Library Web Scraper
Scrapes additional events from TPL branch websites and event pages
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from typing import List, Dict
import re
import time

class TPLWebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Try multiple TPL event pages
        self.event_urls = [
            'https://www.torontopubliclibrary.ca/programs-and-classes/',
            'https://www.torontopubliclibrary.ca/programs-and-classes/featured/',
            'https://www.torontopubliclibrary.ca/programs-and-classes/babies-toddlers-preschoolers/',
            'https://www.torontopubliclibrary.ca/programs-and-classes/children/',
            'https://www.torontopubliclibrary.ca/programs-and-classes/teens/',
        ]

        # Branch coordinates from API scraper
        self.branch_coords = {
            "Agincourt": {"lat": 43.7856, "lng": -79.2787},
            "Albion": {"lat": 43.7372, "lng": -79.5496},
            "Albert Campbell": {"lat": 43.7748, "lng": -79.2305},
            "Alderwood": {"lat": 43.6032, "lng": -79.5479},
            "Annette Street": {"lat": 43.6644, "lng": -79.4815},
            "Barbara Frum": {"lat": 43.7284, "lng": -79.4127},
            "Beaches": {"lat": 43.6687, "lng": -79.2981},
            "Bendale": {"lat": 43.7632, "lng": -79.2518},
            "Black Creek": {"lat": 43.7566, "lng": -79.5234},
            "Bloor/Gladstone": {"lat": 43.6563, "lng": -79.4507},
            "Brentwood": {"lat": 43.6829, "lng": -79.5734},
            "Bridlewood": {"lat": 43.7729, "lng": -79.2824},
            "Broadway": {"lat": 43.7094, "lng": -79.3928},
            "Cedarbrae": {"lat": 43.7631, "lng": -79.2259},
            "Centennial": {"lat": 43.6431, "lng": -79.5360},
            "City Hall": {"lat": 43.6534, "lng": -79.3839},
            "College/Shaw": {"lat": 43.6541, "lng": -79.4196},
            "Danforth/Coxwell": {"lat": 43.6868, "lng": -79.3218},
            "Deer Park": {"lat": 43.6880, "lng": -79.3955},
            "Fort York": {"lat": 43.6391, "lng": -79.4030},
            "High Park": {"lat": 43.6544, "lng": -79.4657},
            "Lillian H. Smith": {"lat": 43.6577, "lng": -79.4000},
            "North York Central Library": {"lat": 43.7675, "lng": -79.4129},
            "Palmerston": {"lat": 43.6651, "lng": -79.4144},
            "Parkdale": {"lat": 43.6396, "lng": -79.4390},
            "Toronto Reference Library": {"lat": 43.6719, "lng": -79.3864},
            "Yorkville": {"lat": 43.6710, "lng": -79.3906}
        }

    def fetch_events(self, days_ahead: int = 60) -> List[Dict]:
        """Fetch events from TPL web pages"""
        print("📚 Fetching from TPL web pages...")

        all_events = []

        # Try the main events calendar/listings
        try:
            # Note: Since direct scraping is blocked, we're relying on the API
            # This is a placeholder for when/if we find accessible web endpoints
            print("   ⚠️  TPL website blocks scraping - relying on API data")
            return []

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []

    def _get_branch_coords(self, library: str) -> Dict:
        """Get coordinates for a library branch"""
        if library in self.branch_coords:
            return self.branch_coords[library]

        for branch, coords in self.branch_coords.items():
            if branch.lower() in library.lower() or library.lower() in branch.lower():
                return coords

        return {"lat": 43.6532, "lng": -79.3832}


def main():
    scraper = TPLWebScraper()
    events = scraper.fetch_events(days_ahead=60)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    if events:
        with open('tpl_web_events.json', 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved to tpl_web_events.json")
    else:
        print("   ℹ️  No additional events found from web scraping")


if __name__ == "__main__":
    main()
