#!/usr/bin/env python3
"""
Art Gallery of Ontario (AGO) Free Events Scraper
Generates AGO's recurring free events for kids/families
"""

from datetime import datetime, timedelta
from typing import List, Dict

class AGOScraper:
    def __init__(self):
        pass

    def fetch_events(self, days_ahead: int = 90) -> List[Dict]:
        """Generate AGO free events"""

        print("🎨 Fetching from Art Gallery of Ontario...")

        events = []
        events.extend(self._generate_first_wednesday_nights(days_ahead))

        print(f"   ✅ Found {len(events)} AGO free events")
        return events

    def _generate_first_wednesday_nights(self, days_ahead: int) -> List[Dict]:
        """Generate First Wednesday Night Free (1st Wednesday of each month, 6-9 PM)"""

        events = []
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        # Check each month in the range
        current_date = today.replace(day=1)  # Start of current month

        while current_date <= end_date:
            # Find first Wednesday of the month
            first_day = current_date.replace(day=1)
            # Find first Wednesday
            days_until_wednesday = (2 - first_day.weekday()) % 7
            first_wednesday = first_day + timedelta(days=days_until_wednesday)

            # Only add if it's in our date range and not in the past
            if today <= first_wednesday <= end_date:
                events.append({
                    'title': 'First Wednesday Night Free at AGO',
                    'description': 'Free admission to the Art Gallery of Ontario on the first Wednesday evening of each month. Explore art collections and exhibitions perfect for families. Kids under 9 always free!',
                    'category': 'Arts',
                    'icon': '🎨',
                    'date': first_wednesday.strftime('%Y-%m-%d'),
                    'start_time': '18:00',
                    'end_time': '21:00',
                    'venue': {
                        'name': 'Art Gallery of Ontario',
                        'address': '317 Dundas St W, Toronto, ON M5T 1G4',
                        'neighborhood': 'Downtown',
                        'lat': 43.6536,
                        'lng': -79.3925
                    },
                    'age_groups': ['All Ages'],
                    'indoor_outdoor': 'Indoor',
                    'organized_by': 'AGO',
                    'website': 'https://ago.ca/visit/free-wednesday-nights',
                    'source': 'AGO',
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
    scraper = AGOScraper()
    events = scraper.fetch_events(days_ahead=90)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")
    for event in events:
        print(f"   {event['icon']} {event['title']} - {event['date']}")

    # Save to JSON
    with open('ago_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to ago_events.json")


if __name__ == "__main__":
    main()
