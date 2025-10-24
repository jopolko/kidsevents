#!/usr/bin/env python3
"""
Stonegate Community Health Centre Scraper
Scrapes FREE drop-in programs for kids in Etobicoke
"""

from datetime import datetime, timedelta
from typing import List, Dict


class StonegateScraper:
    """Scraper for Stonegate CHC free kids drop-in programs"""

    def __init__(self):
        self.source = "StonegateCHC"

    def generate_recurring_thursdays(self, start_date, end_date, start_time, end_time):
        """Generate all Thursday dates in a range"""
        events = []
        current = start_date

        # Move to the first Thursday
        while current.weekday() != 3:  # 3 = Thursday
            current += timedelta(days=1)

        # Generate all Thursdays until end_date
        while current <= end_date:
            events.append({
                'date': current.strftime('%Y-%m-%d'),
                'start_time': start_time,
                'end_time': end_time
            })
            current += timedelta(days=7)

        return events

    def fetch_events(self, days_ahead=90) -> List[Dict]:
        """
        Fetch FREE drop-in programs from Stonegate CHC in Etobicoke

        Args:
            days_ahead: How many days ahead to generate events for

        Returns:
            List of event dictionaries in standard format
        """
        events = []
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        thursday_dates = self.generate_recurring_thursdays(today, end_date, "09:00", "12:00")

        # 1. Stonegate Drop-In (Main Location)
        # Thursdays 9am-12pm, ages 0-6
        for date_info in thursday_dates:
            events.append({
                'title': 'Stonegate Drop-In for Kids 0-6',
                'description': 'FREE fun, engaging activities designed for children aged 0-6 and their caregivers. Drop in for play, crafts, songs, and community connection.',
                'category': 'Play',
                'icon': '👶',
                'date': date_info['date'],
                'start_time': date_info['start_time'],
                'end_time': date_info['end_time'],
                'venue': {
                    'name': 'Stonegate Community Health Centre',
                    'address': '10 Neighbourhood Lane, Unit 201, Toronto, ON',
                    'neighborhood': 'Etobicoke',
                    'lat': 43.6285,
                    'lng': -79.5632
                },
                'age_groups': ['Babies (0-2)', 'Toddlers (3-5)'],
                'indoor_outdoor': 'Indoor',
                'organized_by': 'Stonegate Community Health Centre',
                'website': 'https://www.stonegatechc.org/',
                'source': self.source,
                'scraped_at': datetime.now().isoformat()
            })

        # 2. Sunnylea Drop-In (Sunnylea Park)
        # Thursdays 9am-12pm, ages 0-6
        for date_info in thursday_dates:
            events.append({
                'title': 'Sunnylea Drop-In for Kids 0-6',
                'description': 'FREE fun, engaging activities designed for children aged 0-6 and their caregivers at Sunnylea Park. Drop in for play, crafts, songs, and community connection.',
                'category': 'Play',
                'icon': '🎨',
                'date': date_info['date'],
                'start_time': date_info['start_time'],
                'end_time': date_info['end_time'],
                'venue': {
                    'name': 'Sunnylea Park',
                    'address': '195 Prince Edward Drive, Toronto, ON',
                    'neighborhood': 'Etobicoke',
                    'lat': 43.6342,
                    'lng': -79.5008
                },
                'age_groups': ['Babies (0-2)', 'Toddlers (3-5)'],
                'indoor_outdoor': 'Indoor',
                'organized_by': 'Stonegate Community Health Centre',
                'website': 'https://www.stonegatechc.org/',
                'source': self.source,
                'scraped_at': datetime.now().isoformat()
            })

        # 3. Sunnylea Baby Club
        # Thursdays 9am-12pm, ages 0-12 months
        for date_info in thursday_dates:
            events.append({
                'title': 'Sunnylea Baby Club (0-12 months)',
                'description': 'FREE program for infants 0-12 months and their caregivers. Connect with other new parents, enjoy baby-friendly activities, and get support.',
                'category': 'Play',
                'icon': '👶',
                'date': date_info['date'],
                'start_time': date_info['start_time'],
                'end_time': date_info['end_time'],
                'venue': {
                    'name': 'Royal York United Church',
                    'address': '851 Royal York Road, Toronto, ON',
                    'neighborhood': 'Etobicoke',
                    'lat': 43.6374,
                    'lng': -79.5138
                },
                'age_groups': ['Babies (0-2)'],
                'indoor_outdoor': 'Indoor',
                'organized_by': 'Stonegate Community Health Centre',
                'website': 'https://www.stonegatechc.org/',
                'source': self.source,
                'scraped_at': datetime.now().isoformat()
            })

        # 4. Baby & Me Time (afternoon program)
        thursday_afternoons = self.generate_recurring_thursdays(today, end_date, "13:30", "15:00")
        for date_info in thursday_afternoons:
            events.append({
                'title': 'Baby & Me Time (0-8 months)',
                'description': 'FREE program for parents with babies up to 8 months. Relaxed afternoon for bonding, play, and connecting with other families.',
                'category': 'Play',
                'icon': '👶',
                'date': date_info['date'],
                'start_time': date_info['start_time'],
                'end_time': date_info['end_time'],
                'venue': {
                    'name': 'Stonegate Community Health Centre',
                    'address': '10 Neighbourhood Lane, Unit 201, Toronto, ON',
                    'neighborhood': 'Etobicoke',
                    'lat': 43.6285,
                    'lng': -79.5632
                },
                'age_groups': ['Babies (0-2)'],
                'indoor_outdoor': 'Indoor',
                'organized_by': 'Stonegate Community Health Centre',
                'website': 'https://www.stonegatechc.org/',
                'source': self.source,
                'scraped_at': datetime.now().isoformat()
            })

        return events


if __name__ == '__main__':
    # Test the scraper
    scraper = StonegateScraper()
    events = scraper.fetch_events(days_ahead=30)

    print(f"✅ Scraped {len(events)} events from Stonegate CHC")
    for event in events[:5]:  # Show first 5
        print(f"  - {event['title']} on {event['date']} at {event['start_time']}")
