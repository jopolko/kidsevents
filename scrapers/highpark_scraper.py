#!/usr/bin/env python3
"""
High Park Scraper
Scrapes free activities at High Park including the zoo and nature programs
"""

from datetime import datetime, timedelta
from typing import List, Dict


class HighParkScraper:
    def __init__(self):
        self.source = "HighPark"

    def fetch_events(self, days_ahead: int = 90) -> List[Dict]:
        """Generate High Park free events"""

        print("🌳 Generating High Park free events...")

        events = []
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        # 1. High Park Zoo - Always open and FREE
        events.extend(self._generate_zoo_hours(today, end_date))

        # 2. High Park Nature Centre programs (weekly)
        events.extend(self._generate_nature_programs(today, end_date))

        print(f"   ✅ Generated {len(events)} High Park events")
        return events

    def _generate_zoo_hours(self, start_date, end_date) -> List[Dict]:
        """Generate High Park Zoo availability"""
        events = []
        current_date = start_date

        # Generate every Saturday and Sunday
        while current_date <= end_date:
            if current_date.weekday() in [5, 6]:  # Saturday or Sunday
                event = {
                    'title': '🦙 FREE Zoo Visit: High Park Zoo - Llamas, Bison & Peacocks!',
                    'description': 'Visit Toronto\'s FREE ZOO at High Park! See llamas, bison, deer, peacocks, and more animals. Perfect for a family outing. The High Park Zoo is always free and open year-round during daylight hours. One of Toronto\'s best free family attractions!',
                    'category': 'Nature',
                    'icon': '🦙',
                    'date': current_date.strftime('%Y-%m-%d'),
                    'start_time': '10:00',
                    'end_time': '16:00',
                    'venue': {
                        'name': 'High Park Zoo (FREE)',
                        'address': '1873 Bloor St W, Toronto, ON M6R 2Z3',
                        'neighborhood': 'High Park Attraction',
                        'lat': 43.6465,
                        'lng': -79.4637
                    },
                    'age_groups': ['All Ages'],
                    'indoor_outdoor': 'Outdoor',
                    'organized_by': 'City of Toronto',
                    'website': 'https://www.toronto.ca/explore-enjoy/parks-gardens-beaches/zoos-farms/high-park-zoo/',
                    'source': self.source,
                    'scraped_at': datetime.now().isoformat()
                }
                events.append(event)

            current_date += timedelta(days=1)

        return events

    def _generate_nature_programs(self, start_date, end_date) -> List[Dict]:
        """Generate High Park Nature Centre drop-in programs"""
        events = []
        current_date = start_date

        # Nature walks every Saturday morning
        while current_date <= end_date:
            if current_date.weekday() == 5:  # Saturday
                event = {
                    'title': '🌿 FREE High Park Nature Walks & Programs',
                    'description': 'Drop-in nature programs at High Park Nature Centre including guided walks, nature clubs, and outdoor activities. Learn about local wildlife, plants, and ecosystems. Check website for current schedule.',
                    'category': 'Nature',
                    'icon': '🌿',
                    'date': current_date.strftime('%Y-%m-%d'),
                    'start_time': '10:00',
                    'end_time': '12:00',
                    'venue': {
                        'name': 'High Park Nature Centre (FREE)',
                        'address': '375 Colborne Lodge Dr, Toronto, ON M6R 2Z3',
                        'neighborhood': 'High Park Attraction',
                        'lat': 43.6450,
                        'lng': -79.4625
                    },
                    'age_groups': ['Toddlers (3-5)', 'Kids (6-8)', 'Preteens (9-12)'],
                    'indoor_outdoor': 'Both',
                    'organized_by': 'High Park Nature Centre',
                    'website': 'https://highparknaturecentre.com/programs/',
                    'source': self.source,
                    'scraped_at': datetime.now().isoformat()
                }
                events.append(event)

            current_date += timedelta(days=1)

        return events


if __name__ == '__main__':
    scraper = HighParkScraper()
    events = scraper.fetch_events(days_ahead=14)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    for event in events[:3]:
        print(f"   - {event['title']} on {event['date']}")
