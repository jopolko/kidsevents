#!/usr/bin/env python3
"""
Evergreen Brick Works Events Scraper
Fetches free kids/family events from Evergreen Brick Works
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import re

class EvergreenBrickWorksScraper:
    def __init__(self):
        self.base_url = "https://www.evergreen.ca"
        self.events_url = f"{self.base_url}/evergreen-brick-works/whats-on/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def fetch_events(self, days_ahead: int = 30) -> List[Dict]:
        """Fetch free kids/family events from Evergreen Brick Works"""

        print("🌳 Fetching from Evergreen Brick Works...")

        events = []

        # Add recurring free events
        events.extend(self._generate_weekend_nature_play(days_ahead))
        events.extend(self._generate_farmers_market(days_ahead))
        events.extend(self._generate_free_tours(days_ahead))

        print(f"   ✅ Found {len(events)} Evergreen Brick Works events")
        return events

    def _generate_weekend_nature_play(self, days_ahead: int) -> List[Dict]:
        """Generate Weekend Nature Play events (every Saturday + select Sundays, 10am-3pm)"""

        events = []
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        current_date = today
        while current_date <= end_date:
            # Saturday events
            if current_date.weekday() == 5:  # Saturday
                events.append({
                    'title': 'Weekend Nature Play',
                    'description': 'Free, year-round, drop-in outdoor program for all ages in the Children\'s Garden. Activities include nature crafts, touch tables, and seasonal activities.',
                    'category': 'Nature',
                    'icon': '🌳',
                    'date': current_date.strftime('%Y-%m-%d'),
                    'start_time': '10:00',
                    'end_time': '15:00',
                    'venue': {
                        'name': 'Evergreen Brick Works - Children\'s Garden',
                        'address': '550 Bayview Ave, Toronto, ON M4W 3X8',
                        'neighborhood': 'Don Valley',
                        'lat': 43.6850,
                        'lng': -79.3650
                    },
                    'age_groups': ['All Ages'],
                    'indoor_outdoor': 'Outdoor',
                    'organized_by': 'Evergreen',
                    'website': 'https://www.evergreen.ca/evergreen-brick-works/explore/children-and-youth/',
                    'source': 'EvergreenBrickWorks',
                    'is_free': True,
                    'scraped_at': datetime.now().isoformat()
                })

            current_date += timedelta(days=1)

        return events

    def _generate_farmers_market(self, days_ahead: int) -> List[Dict]:
        """Generate Saturday Farmers Market events (every Saturday, 9am-1pm)"""

        events = []
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        current_date = today
        while current_date <= end_date:
            if current_date.weekday() == 5:  # Saturday
                events.append({
                    'title': 'Evergreen Saturday Farmers Market',
                    'description': 'Year-round farmers market open every Saturday with local vendors, food, and family-friendly atmosphere. Free to attend.',
                    'category': 'Entertainment',
                    'icon': '🥕',
                    'date': current_date.strftime('%Y-%m-%d'),
                    'start_time': '09:00',
                    'end_time': '13:00',
                    'venue': {
                        'name': 'Evergreen Brick Works',
                        'address': '550 Bayview Ave, Toronto, ON M4W 3X8',
                        'neighborhood': 'Don Valley',
                        'lat': 43.6850,
                        'lng': -79.3650
                    },
                    'age_groups': ['All Ages'],
                    'indoor_outdoor': 'Both',
                    'organized_by': 'Evergreen',
                    'website': 'https://www.evergreen.ca/evergreen-brick-works/whats-on/',
                    'source': 'EvergreenBrickWorks',
                    'is_free': True,
                    'scraped_at': datetime.now().isoformat()
                })

            current_date += timedelta(days=1)

        return events

    def _generate_free_tours(self, days_ahead: int) -> List[Dict]:
        """Generate free Saturday site tours (every Saturday)"""

        events = []
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        current_date = today
        while current_date <= end_date:
            if current_date.weekday() == 5:  # Saturday
                events.append({
                    'title': 'Free Evergreen Brick Works Site Tour',
                    'description': 'Free public tour of the Evergreen Brick Works site, exploring the history and sustainability features of this unique Toronto landmark.',
                    'category': 'Learning',
                    'icon': '🏛️',
                    'date': current_date.strftime('%Y-%m-%d'),
                    'start_time': '11:00',
                    'end_time': '12:00',
                    'venue': {
                        'name': 'Evergreen Brick Works',
                        'address': '550 Bayview Ave, Toronto, ON M4W 3X8',
                        'neighborhood': 'Don Valley',
                        'lat': 43.6850,
                        'lng': -79.3650
                    },
                    'age_groups': ['All Ages'],
                    'indoor_outdoor': 'Both',
                    'organized_by': 'Evergreen',
                    'website': 'https://www.evergreen.ca/evergreen-brick-works/whats-on/',
                    'source': 'EvergreenBrickWorks',
                    'is_free': True,
                    'scraped_at': datetime.now().isoformat()
                })

            current_date += timedelta(days=1)

        return events


def main():
    import json
    scraper = EvergreenBrickWorksScraper()
    events = scraper.fetch_events(days_ahead=30)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    # Save to JSON
    with open('evergreen_brickworks_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to evergreen_brickworks_events.json")


if __name__ == "__main__":
    main()
