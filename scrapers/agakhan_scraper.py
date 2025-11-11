#!/usr/bin/env python3
"""
Aga Khan Museum Scraper
Scrapes free admission days and Family Sundays from Aga Khan Museum
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
from dateutil.relativedelta import relativedelta


class AgaKhanMuseumScraper:
    def __init__(self):
        self.base_url = "https://www.agakhanmuseum.org"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def fetch_events(self, days_ahead: int = 90) -> List[Dict]:
        """Generate recurring free events at Aga Khan Museum"""

        print("🕌 Generating Aga Khan Museum free events...")

        events = []
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        # 1. BMO Free Wednesdays (every Wednesday 4-8pm)
        events.extend(self._generate_free_wednesdays(today, end_date))

        # 2. Family Sundays (every Sunday 12-4pm)
        events.extend(self._generate_family_sundays(today, end_date))

        print(f"   ✅ Generated {len(events)} Aga Khan Museum events")
        return events

    def _generate_free_wednesdays(self, start_date, end_date) -> List[Dict]:
        """Generate BMO Free Wednesday events"""
        events = []
        current_date = start_date

        while current_date <= end_date:
            if current_date.weekday() == 2:  # Wednesday
                event = {
                    'title': 'BMO Free Wednesday at Aga Khan Museum',
                    'description': 'Free general admission every Wednesday from 4-8pm. Explore Islamic arts and cultures through exhibitions, collections, and beautiful architecture. Perfect for families!',
                    'category': 'Arts',
                    'icon': '🕌',
                    'date': current_date.strftime('%Y-%m-%d'),
                    'start_time': '16:00',
                    'end_time': '20:00',
                    'venue': {
                        'name': 'Aga Khan Museum',
                        'address': '77 Wynford Drive, Toronto, ON M3C 1K1',
                        'neighborhood': 'North York',
                        'lat': 43.7255,
                        'lng': -79.3322
                    },
                    'age_groups': ['All Ages'],
                    'indoor_outdoor': 'Indoor',
                    'organized_by': 'Aga Khan Museum',
                    'website': 'https://www.agakhanmuseum.org/visit',
                    'source': 'AgaKhanMuseum',
                    'scraped_at': datetime.now().isoformat()
                }
                events.append(event)

            current_date += timedelta(days=1)

        return events

    def _generate_family_sundays(self, start_date, end_date) -> List[Dict]:
        """Generate Family Sunday events"""
        events = []
        current_date = start_date

        while current_date <= end_date:
            if current_date.weekday() == 6:  # Sunday
                event = {
                    'title': 'Family Sundays at Aga Khan Museum',
                    'description': 'Free drop-in arts and crafts activities in the Education Centre every Sunday from 12-4pm. Hands-on creative projects inspired by the museum\'s collections. No registration required!',
                    'category': 'Arts',
                    'icon': '🎨',
                    'date': current_date.strftime('%Y-%m-%d'),
                    'start_time': '12:00',
                    'end_time': '16:00',
                    'venue': {
                        'name': 'Aga Khan Museum',
                        'address': '77 Wynford Drive, Toronto, ON M3C 1K1',
                        'neighborhood': 'North York',
                        'lat': 43.7255,
                        'lng': -79.3322
                    },
                    'age_groups': ['Toddlers (3-5)', 'Kids (6-8)', 'Preteens (9-12)'],
                    'indoor_outdoor': 'Indoor',
                    'organized_by': 'Aga Khan Museum',
                    'website': 'https://www.agakhanmuseum.org/education/families',
                    'source': 'AgaKhanMuseum',
                    'scraped_at': datetime.now().isoformat()
                }
                events.append(event)

            current_date += timedelta(days=1)

        return events


if __name__ == '__main__':
    scraper = AgaKhanMuseumScraper()
    events = scraper.fetch_events(days_ahead=30)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    if events:
        print(f"\n   First event: {events[0]['title']} on {events[0]['date']}")
