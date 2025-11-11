#!/usr/bin/env python3
"""
Royal Ontario Museum (ROM) Free Events Scraper
Generates ROM's recurring free events for kids/families
"""

from datetime import datetime, timedelta
from typing import List, Dict

class ROMScraper:
    def __init__(self):
        pass

    def fetch_events(self, days_ahead: int = 90) -> List[Dict]:
        """Generate ROM free events"""

        print("🏛️  Fetching from Royal Ontario Museum...")

        events = []
        events.extend(self._generate_third_tuesday_nights(days_ahead))

        print(f"   ✅ Found {len(events)} ROM free events")
        return events

    def _generate_third_tuesday_nights(self, days_ahead: int) -> List[Dict]:
        """Generate Third Tuesday Nights Free (3rd Tuesday of each month, 4:30-8:30 PM)"""

        events = []
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        # Check each month in the range
        current_date = today.replace(day=1)  # Start of current month

        while current_date <= end_date:
            # Find third Tuesday of the month
            first_day = current_date.replace(day=1)
            # Find first Tuesday
            days_until_tuesday = (1 - first_day.weekday()) % 7
            first_tuesday = first_day + timedelta(days=days_until_tuesday)
            # Third Tuesday is 14 days after first Tuesday
            third_tuesday = first_tuesday + timedelta(days=14)

            # Only add if it's in our date range and not in the past
            if today <= third_tuesday <= end_date:
                events.append({
                    'title': 'Third Tuesday Nights Free at ROM',
                    'description': 'Free admission to the Royal Ontario Museum on the third Tuesday evening of each month. Explore world cultures, natural history, and special exhibitions with your family.',
                    'category': 'Learning',
                    'icon': '🏛️',
                    'date': third_tuesday.strftime('%Y-%m-%d'),
                    'start_time': '16:30',
                    'end_time': '20:30',
                    'venue': {
                        'name': 'Royal Ontario Museum',
                        'address': '100 Queens Park, Toronto, ON M5S 2C6',
                        'neighborhood': 'Downtown',
                        'lat': 43.6677,
                        'lng': -79.3948
                    },
                    'age_groups': ['All Ages'],
                    'indoor_outdoor': 'Indoor',
                    'organized_by': 'ROM',
                    'website': 'https://www.rom.on.ca/whats-on/special-programs/third-tuesday-nights-free',
                    'source': 'ROM',
                    'is_free': True,
                    'scraped_at': datetime.now().isoformat()
                })

            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

        return events


def main():
    import json
    scraper = ROMScraper()
    events = scraper.fetch_events(days_ahead=90)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")
    for event in events:
        print(f"   {event['icon']} {event['title']} - {event['date']}")

    # Save to JSON
    with open('rom_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to rom_events.json")


if __name__ == "__main__":
    main()
