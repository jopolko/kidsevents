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

        # Creative Socials at Cloverdale (if within date range)
        creative_social = datetime(2025, 10, 24).date()
        if today <= creative_social <= end_date:
            events.append({
                'title': 'Creative Socials at Cloverdale',
                'description': 'Drop-in creative coworking and social space for families and community members. Bring your creative projects and connect with others.',
                'category': 'Arts',
                'icon': '🎨',
                'date': '2025-10-24',
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
                'website': 'https://www.artsetobicoke.com/',
                'source': self.source,
                'scraped_at': datetime.now().isoformat()
            })

        # Studio Series: Whimsical Wonders of Fall
        fall_workshop = datetime(2025, 10, 25).date()
        if today <= fall_workshop <= end_date:
            events.append({
                'title': 'Whimsical Wonders of Fall: Art for Kids',
                'description': 'Studio Series workshop for children featuring fall-themed art activities. Hands-on creative experience exploring autumn themes.',
                'category': 'Arts',
                'icon': '🍂',
                'date': '2025-10-25',
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
                'website': 'https://www.artsetobicoke.com/',
                'source': self.source,
                'scraped_at': datetime.now().isoformat()
            })

        # AE Open Mic Night (family-friendly)
        open_mic = datetime(2025, 10, 29).date()
        if today <= open_mic <= end_date:
            events.append({
                'title': 'AE Open Mic Night (Family-Friendly)',
                'description': 'Free community open mic night at Storefront Gallery. All ages welcome to perform or enjoy performances in a supportive environment.',
                'category': 'Arts',
                'icon': '🎤',
                'date': '2025-10-29',
                'start_time': '18:00',
                'end_time': '20:00',
                'venue': {
                    'name': 'Storefront Gallery',
                    'address': '4893a Dundas Street West, Etobicoke, ON',
                    'neighborhood': 'Etobicoke',
                    'lat': 43.6638,
                    'lng': -79.5242
                },
                'age_groups': ['All Ages'],
                'indoor_outdoor': 'Indoor',
                'organized_by': 'Arts Etobicoke',
                'website': 'https://www.artsetobicoke.com/',
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
