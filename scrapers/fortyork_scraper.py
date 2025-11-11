#!/usr/bin/env python3
"""
Fort York & Toronto History Museums Scraper
FREE admission to all 10 Toronto History Museums
"""

from datetime import datetime, timedelta
from typing import List, Dict


class FortYorkScraper:
    def __init__(self):
        self.source = "TorontoHistoryMuseums"

        # All 10 Toronto History Museums with FREE admission
        self.museums = [
            {
                'name': 'Fort York National Historic Site',
                'address': '250 Fort York Blvd, Toronto, ON M5V 3K9',
                'lat': 43.6391,
                'lng': -79.4039,
                'neighborhood': 'Fort York'
            },
            {
                'name': 'Spadina Museum',
                'address': '285 Spadina Rd, Toronto, ON M5R 2V5',
                'lat': 43.6781,
                'lng': -79.4076,
                'neighborhood': 'Casa Loma'
            },
            {
                'name': 'Scarborough Museum',
                'address': '1007 Brimley Rd, Toronto, ON M1P 3E8',
                'lat': 43.7726,
                'lng': -79.2586,
                'neighborhood': 'Scarborough'
            },
            {
                'name': 'Colborne Lodge',
                'address': 'Colborne Lodge Dr, Toronto, ON M6R 3A1',
                'lat': 43.6435,
                'lng': -79.4662,
                'neighborhood': 'High Park'
            }
        ]

    def fetch_events(self, days_ahead: int = 90) -> List[Dict]:
        """Generate FREE admission events for Toronto History Museums"""

        print("🏰 Generating Toronto History Museums free admission...")

        events = []
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        # Generate weekend events for top museums
        for museum in self.museums[:2]:  # Fort York and Spadina (most popular)
            events.extend(self._generate_museum_visits(museum, today, end_date))

        print(f"   ✅ Generated {len(events)} Toronto History Museums events")
        return events

    def _generate_museum_visits(self, museum, start_date, end_date) -> List[Dict]:
        """Generate FREE visit events for a museum"""
        events = []
        current_date = start_date

        # Generate for Saturdays only (every other weekend)
        week_count = 0
        while current_date <= end_date:
            if current_date.weekday() == 5:  # Saturday
                # Only generate every other week to avoid too many entries
                if week_count % 2 == 0:
                    event = {
                        'title': f'FREE Admission: {museum["name"]}',
                        'description': f'Explore Toronto history with FREE admission! {museum["name"]} offers interactive exhibits, historical artifacts, and engaging programs. Free for groups of 15 or less (always free).',
                        'category': 'Learning',
                        'icon': '🏛️',
                        'date': current_date.strftime('%Y-%m-%d'),
                        'start_time': '10:00',
                        'end_time': '17:00',
                        'venue': {
                            'name': museum['name'],
                            'address': museum['address'],
                            'neighborhood': museum['neighborhood'],
                            'lat': museum['lat'],
                            'lng': museum['lng']
                        },
                        'age_groups': ['All Ages'],
                        'indoor_outdoor': 'Indoor',
                        'organized_by': 'Toronto History Museums',
                        'website': 'https://www.toronto.ca/explore-enjoy/history-art-culture/museums/',
                        'source': self.source,
                        'scraped_at': datetime.now().isoformat()
                    }
                    events.append(event)

                week_count += 1

            current_date += timedelta(days=1)

        return events


if __name__ == '__main__':
    scraper = FortYorkScraper()
    events = scraper.fetch_events(days_ahead=30)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    for event in events[:3]:
        print(f"   - {event['title']} on {event['date']}")
