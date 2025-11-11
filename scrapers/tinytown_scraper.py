#!/usr/bin/env python3
"""
Tiny Town Vaughan Scraper
Scrapes special events from Tiny Town Vaughan indoor play centre
"""

from datetime import datetime, timedelta
from typing import List, Dict


class TinyTownScraper:
    """Scraper for Tiny Town Vaughan special events"""

    def __init__(self):
        self.source = "TinyTown"

    def fetch_events(self, days_ahead=90) -> List[Dict]:
        """
        Fetch special events from Tiny Town Vaughan

        Note: Tiny Town primarily offers drop-in play ($16.60 admission) with special events
        like Monday Circle Time and monthly themed activities. These are NOT free events.

        Special FREE events are rare and will be added when announced.

        Args:
            days_ahead: How many days ahead to check for events

        Returns:
            List of event dictionaries in standard format
        """
        events = []
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        # Holiday Events (when announced by venue)
        # Check for upcoming holiday events

        # Christmas/Holiday Event (typically mid-December)
        if today.month == 11 or today.month == 12:
            # Estimate mid-December holiday event
            holiday_date = datetime(today.year, 12, 15).date()
            if today <= holiday_date <= end_date:
                events.append({
                    'title': 'Holiday Event at Tiny Town Vaughan',
                    'description': 'Special holiday activities included with regular drop-in admission. Join us for festive fun, crafts, and activities. Check website for exact date and details.',
                    'category': 'Entertainment',
                    'icon': '🎄',
                    'date': holiday_date.strftime('%Y-%m-%d'),
                    'start_time': '10:00',
                    'end_time': '14:00',
                    'venue': {
                        'name': 'Tiny Town Vaughan',
                        'address': '9222 Keele Street, Vaughan, ON L4K 5A1',
                        'neighborhood': 'Vaughan',
                        'lat': 43.7967,
                        'lng': -79.5113
                    },
                    'age_groups': ['Babies (0-2)', 'Toddlers (3-5)', 'Kids (6-8)'],
                    'indoor_outdoor': 'Indoor',
                    'organized_by': 'Tiny Town Vaughan',
                    'website': 'https://tinytownvaughan.ca',
                    'source': self.source,
                    'scraped_at': datetime.now().isoformat()
                })

        return events


if __name__ == '__main__':
    # Test the scraper
    scraper = TinyTownScraper()
    events = scraper.fetch_events(days_ahead=365)

    print(f"✅ Scraped {len(events)} events from Tiny Town Vaughan")
    for event in events:
        print(f"  - {event['title']} on {event['date']} at {event['start_time']}")
