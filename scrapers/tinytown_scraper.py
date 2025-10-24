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
        Note: Tiny Town primarily offers drop-in play, but they have special FREE events
        that are included with regular admission.

        Args:
            days_ahead: How many days ahead to check for events

        Returns:
            List of event dictionaries in standard format
        """
        events = []
        today = datetime.now().date()

        # Halloween Event 2025
        # FREE with regular drop-in admission
        halloween_date = datetime(2025, 10, 31).date()
        if today <= halloween_date <= today + timedelta(days=days_ahead):
            events.append({
                'title': 'Halloween Drop-In Event at Tiny Town',
                'description': 'FREE Halloween activities with regular Drop-in admission! Join us for Halloween fun from 10am-2pm. Come in costume and enjoy special activities, games, and treats.',
                'category': 'Entertainment',
                'icon': '🎃',
                'date': '2025-10-31',
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

        # Note: Tiny Town also has "Monday Circle Time" weekly events
        # but we don't generate these as recurring events since they're part of regular drop-in
        # and not truly "free" events (require drop-in admission of $16.60)

        return events


if __name__ == '__main__':
    # Test the scraper
    scraper = TinyTownScraper()
    events = scraper.fetch_events(days_ahead=365)

    print(f"✅ Scraped {len(events)} events from Tiny Town Vaughan")
    for event in events:
        print(f"  - {event['title']} on {event['date']} at {event['start_time']}")
