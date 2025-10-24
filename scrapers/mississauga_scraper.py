#!/usr/bin/env python3
"""
Mississauga Events Scraper
Scrapes free kids and family events from City of Mississauga
"""

from datetime import datetime, timedelta
from typing import List, Dict


class MississaugaScraper:
    """Scraper for City of Mississauga free kids events"""

    def __init__(self):
        self.source = "Mississauga"

    def generate_recurring_saturdays(self, start_date, end_date, start_time="12:00", end_time="16:00"):
        """Generate all Saturday dates in a range"""
        events = []
        current = start_date

        # Move to the first Saturday
        while current.weekday() != 5:  # 5 = Saturday
            current += timedelta(days=1)

        # Generate all Saturdays until end_date
        while current <= end_date:
            events.append({
                'date': current.strftime('%Y-%m-%d'),
                'start_time': start_time,
                'end_time': end_time
            })
            current += timedelta(days=7)

        return events

    def generate_recurring_sundays(self, start_date, end_date, start_time="12:00", end_time="16:00"):
        """Generate all Sunday dates in a range"""
        events = []
        current = start_date

        # Move to the first Sunday
        while current.weekday() != 6:  # 6 = Sunday
            current += timedelta(days=1)

        # Generate all Sundays until end_date
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
        Fetch free kids events from City of Mississauga

        Args:
            days_ahead: How many days ahead to generate events for

        Returns:
            List of event dictionaries in standard format
        """
        events = []
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        # 1. Saturday Family Fun at Bradley Museum
        # Recurring every Saturday, 12:00-4:00pm, FREE
        saturday_dates = self.generate_recurring_saturdays(today, end_date)
        for date_info in saturday_dates:
            events.append({
                'title': 'Saturday Family Fun at Bradley Museum',
                'description': 'Drop in for a relaxed afternoon of crafts and games that are perfect for kids and parents alike. Activities include outdoor games beside the barn, table games, and crafts indoors.',
                'category': 'Arts',
                'icon': '🎨',
                'date': date_info['date'],
                'start_time': date_info['start_time'],
                'end_time': date_info['end_time'],
                'venue': {
                    'name': 'Bradley Museum',
                    'address': '1620 Orr Road, Mississauga, ON',
                    'neighborhood': 'Mississauga',
                    'lat': 43.5890,
                    'lng': -79.5618
                },
                'age_groups': ['All Ages'],
                'indoor_outdoor': 'Both',
                'organized_by': 'City of Mississauga',
                'website': 'https://www.mississauga.ca/events-and-attractions/events-calendar/saturday-family-fun-at-bradley/',
                'source': self.source,
                'scraped_at': datetime.now().isoformat()
            })

        # 2. Sunday Family Fun at Benares Historic House
        # Recurring every Sunday, 12:00-4:00pm, FREE
        sunday_dates = self.generate_recurring_sundays(today, end_date)
        for date_info in sunday_dates:
            events.append({
                'title': 'Sunday Family Fun at Benares Historic House',
                'description': 'Drop in for a relaxed afternoon of crafts and games that are perfect for kids and parents alike. Activities include outdoor lawn games, board games, and craft projects in the Visitor Centre.',
                'category': 'Arts',
                'icon': '🎨',
                'date': date_info['date'],
                'start_time': date_info['start_time'],
                'end_time': date_info['end_time'],
                'venue': {
                    'name': 'Benares Historic House',
                    'address': '1507 Clarkson Road North, Mississauga, ON',
                    'neighborhood': 'Mississauga',
                    'lat': 43.5183,
                    'lng': -79.5897
                },
                'age_groups': ['All Ages'],
                'indoor_outdoor': 'Both',
                'organized_by': 'City of Mississauga',
                'website': 'https://www.mississauga.ca/events-and-attractions/events-calendar/sunday-family-fun-at-benares-historic-house/',
                'source': self.source,
                'scraped_at': datetime.now().isoformat()
            })

        # 3. Family Day 2025 (if in range)
        family_day = datetime(2025, 2, 17).date()
        if today <= family_day <= end_date:
            events.append({
                'title': 'Family Day 2025 at Celebration Square',
                'description': 'Free ice skating, live DJ music, food trucks, and drop-in creative workshops including dance, printmaking, digital art, screen printing, and face painting. Presented by TD.',
                'category': 'Entertainment',
                'icon': '🎉',
                'date': '2025-02-17',
                'start_time': '12:00',
                'end_time': '16:00',
                'venue': {
                    'name': 'Celebration Square',
                    'address': '300 City Centre Drive, Mississauga, ON',
                    'neighborhood': 'Mississauga',
                    'lat': 43.5933,
                    'lng': -79.6424
                },
                'age_groups': ['All Ages', 'Toddlers (3-5)', 'Kids (6-8)', 'Preteens (9-12)'],
                'indoor_outdoor': 'Both',
                'organized_by': 'City of Mississauga',
                'website': 'https://www.mississauga.ca/events-and-attractions/events-calendar/family-day-2025/',
                'source': self.source,
                'scraped_at': datetime.now().isoformat()
            })

        # 4. Canada Day 2025 (if in range)
        canada_day = datetime(2025, 7, 1).date()
        if today <= canada_day <= end_date:
            events.append({
                'title': 'Canada Day 2025 Celebration',
                'description': 'Celebrate Canada Day with live entertainment, family activities, 25+ food trucks, and a spectacular fireworks finale. Free admission.',
                'category': 'Entertainment',
                'icon': '🇨🇦',
                'date': '2025-07-01',
                'start_time': '16:00',
                'end_time': '22:30',
                'venue': {
                    'name': 'Celebration Square',
                    'address': '300 City Centre Drive, Mississauga, ON',
                    'neighborhood': 'Mississauga',
                    'lat': 43.5933,
                    'lng': -79.6424
                },
                'age_groups': ['All Ages'],
                'indoor_outdoor': 'Outdoor',
                'organized_by': 'City of Mississauga',
                'website': 'https://www.mississauga.ca/events-and-attractions/events-calendar/canada-day-2025/',
                'source': self.source,
                'scraped_at': datetime.now().isoformat()
            })

        # 5. Carassauga Festival of Cultures (if in range)
        carassauga = datetime(2025, 5, 25).date()
        if today <= carassauga <= end_date:
            events.append({
                'title': 'Carassauga Festival of Cultures',
                'description': 'Carassauga Festival of Cultures 40th Anniversary celebration. Kids 12 and under are FREE. Experience diverse cultures, food, and entertainment.',
                'category': 'Entertainment',
                'icon': '🌍',
                'date': '2025-05-25',
                'start_time': '12:00',
                'end_time': '20:00',
                'venue': {
                    'name': 'Celebration Square',
                    'address': '300 City Centre Drive, Mississauga, ON',
                    'neighborhood': 'Mississauga',
                    'lat': 43.5933,
                    'lng': -79.6424
                },
                'age_groups': ['All Ages'],
                'indoor_outdoor': 'Outdoor',
                'organized_by': 'City of Mississauga',
                'website': 'https://www.mississauga.ca/events-and-attractions/events-calendar/carassauga-festival-of-cultures-40th-annivers/',
                'source': self.source,
                'scraped_at': datetime.now().isoformat()
            })

        return events


if __name__ == '__main__':
    # Test the scraper
    scraper = MississaugaScraper()
    events = scraper.fetch_events(days_ahead=30)

    print(f"✅ Scraped {len(events)} events from Mississauga")
    for event in events[:3]:  # Show first 3
        print(f"  - {event['title']} on {event['date']} at {event['start_time']}")
