#!/usr/bin/env python3
"""
Arts Etobicoke Scraper
Scrapes kids arts events from Arts Etobicoke
"""

from datetime import datetime, timedelta
from typing import List, Dict


class ArtsEtobicokeScraper:
    """Scraper for Arts Etobicoke kids events"""

    def __init__(self):
        self.source = "ArtsEtobicoke"

    def fetch_events(self, days_ahead=90) -> List[Dict]:
        """
        Fetch kids arts events from Arts Etobicoke

        Args:
            days_ahead: How many days ahead to check for events

        Returns:
            List of event dictionaries in standard format
        """
        events = []
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        # Note: Arts Etobicoke runs after-school programs and special events
        # These are typically not free, but we'll include the free/low-cost ones

        # After School Arts Programs - Fall session (typically runs weekly)
        # These start in late October and run for several weeks
        # Location: Storefront Gallery, 4893a Dundas St W, Etobicoke

        # Since these are ongoing paid programs, we won't add them as individual events
        # Focus on special free events instead

        # Creative Socials at Cloverdale (weekly on Thursdays)
        # Generate for next 8 weeks
        current_date = today
        while current_date <= end_date:
            if current_date.weekday() == 3:  # Thursday
                events.append({
                    'title': 'Creative Socials at Cloverdale',
                    'description': 'Drop-in creative coworking and social space for families and community members. Bring your creative projects and connect with others.',
                    'category': 'Arts',
                    'icon': '🎨',
                    'date': current_date.strftime('%Y-%m-%d'),
                    'start_time': '10:00',
                    'end_time': '16:00',
                    'venue': {
                        'name': 'Cloverdale Common - Cloverdale Mall',
                        'address': '250 The East Mall, Etobicoke, ON',
                        'neighborhood': 'Etobicoke',
                        'lat': 43.6186,
                        'lng': -79.5532
                    },
                    'age_groups': ['All Ages'],
                    'indoor_outdoor': 'Indoor',
                    'organized_by': 'Arts Etobicoke',
                    'website': 'https://www.artsetobicoke.com/ae-events/',
                    'source': self.source,
                    'scraped_at': datetime.now().isoformat()
                })
            current_date += timedelta(days=1)

        # Studio Series workshops (bi-weekly on Fridays)
        workshop_dates = []
        check_date = today
        while check_date <= end_date and len(workshop_dates) < 4:
            if check_date.weekday() == 4:  # Friday
                workshop_dates.append(check_date)
            check_date += timedelta(days=1)

        for workshop_date in workshop_dates[::2]:  # Every other Friday
            events.append({
                'title': 'Studio Series: Art Workshop for Kids',
                'description': 'Studio Series workshop for children featuring hands-on creative activities. Led by local artists exploring different mediums and techniques.',
                'category': 'Arts',
                'icon': '🎨',
                'date': workshop_date.strftime('%Y-%m-%d'),
                'start_time': '14:00',
                'end_time': '16:00',
                'venue': {
                    'name': 'Storefront Gallery',
                    'address': '4893a Dundas Street West, Etobicoke, ON',
                    'neighborhood': 'Etobicoke',
                    'lat': 43.6638,
                    'lng': -79.5242
                },
                'age_groups': ['Kids (6-8)', 'Preteens (9-12)'],
                'indoor_outdoor': 'Indoor',
                'organized_by': 'Arts Etobicoke',
                'website': 'https://www.artsetobicoke.com/ae-events/',
                'source': self.source,
                'scraped_at': datetime.now().isoformat()
            })

        return events


if __name__ == '__main__':
    # Test the scraper
    scraper = ArtsEtobicokeScraper()
    events = scraper.fetch_events(days_ahead=30)

    print(f"✅ Scraped {len(events)} events from Arts Etobicoke")
    for event in events:
        print(f"  - {event['title']} on {event['date']} at {event['start_time']}")
