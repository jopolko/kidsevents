#!/usr/bin/env python3
"""
Indoor Play Centers Scraper
Generates recurring drop-in events for Toronto indoor play centers
Based on their regular operating hours
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict

class IndoorPlayCentersScraper:
    def __init__(self):
        # Indoor play centers with their schedules and details
        self.play_centers = [
            {
                "name": "Jump for Joy Play Centre",
                "address": "1379 Danforth Avenue, Toronto, ON",
                "lat": 43.6857,
                "lng": -79.3395,
                "phone": "416-466-0404",
                "website": "https://jumpforjoyplaycentre.ca/",
                "description": "Indoor play space with slides, climbing structures, and play areas for kids",
                "age_range": "0-5 years",
                "price_info": "Drop-in $22 for one child and adult",
                "schedule": {
                    "monday": [{"start": "09:00", "end": "14:00"}],
                    "tuesday": [{"start": "09:00", "end": "14:00"}],
                    "wednesday": [{"start": "09:00", "end": "14:00"}],
                    "thursday": [{"start": "09:00", "end": "14:00"}],
                    "friday": [{"start": "09:00", "end": "14:00"}],
                    "saturday": [],  # Private events only
                    "sunday": []     # Private events only
                }
            },
            {
                "name": "Kidnasium",
                "address": "1546 Avenue Road, Toronto, ON",
                "lat": 43.7247,
                "lng": -79.4103,
                "phone": "416-785-3888",
                "website": "https://kidnasium.ca/",
                "description": "Active play center with climbing, sliding, and obstacle courses for young children",
                "age_range": "0-6 years",
                "price_info": "Call ahead to book drop-in appointment",
                "schedule": {
                    "monday": [{"start": "09:00", "end": "18:00"}],
                    "tuesday": [{"start": "09:00", "end": "18:00"}],
                    "wednesday": [{"start": "09:00", "end": "18:00"}],
                    "thursday": [{"start": "09:00", "end": "18:00"}],
                    "friday": [{"start": "09:00", "end": "18:00"}],
                    "saturday": [{"start": "09:00", "end": "18:00"}],
                    "sunday": [{"start": "09:00", "end": "18:00"}]
                }
            },
            {
                "name": "Happy Kingdom",
                "address": "1980 St. Clair Avenue West, Toronto, ON",
                "lat": 43.6745,
                "lng": -79.4712,
                "phone": "416-654-3456",
                "website": "https://www.happykingdom.ca/",
                "description": "Indoor playground with play structures, toys, and activities for toddlers and young kids",
                "age_range": "0-8 years",
                "price_info": "Drop-in rates available",
                "schedule": {
                    "monday": [{"start": "11:00", "end": "19:00"}],
                    "tuesday": [{"start": "11:00", "end": "19:00"}],
                    "wednesday": [{"start": "11:00", "end": "19:00"}],
                    "thursday": [{"start": "11:00", "end": "19:00"}],
                    "friday": [{"start": "11:00", "end": "19:00"}],
                    "saturday": [{"start": "11:00", "end": "19:00"}],
                    "sunday": [{"start": "11:00", "end": "19:00"}]
                }
            },
            {
                "name": "Sprouts - Growing Bodies and Minds",
                "address": "183 Carlaw Avenue, Toronto, ON",
                "lat": 43.6678,
                "lng": -79.3456,
                "phone": "416-465-7776",
                "website": "https://www.sproutsplayce.com/",
                "description": "Active indoor play space focused on child development through movement and exploration",
                "age_range": "0-6 years",
                "price_info": "Drop-in available during open hours",
                "schedule": {
                    "monday": [{"start": "09:00", "end": "13:00"}],
                    "tuesday": [{"start": "09:00", "end": "13:00"}],
                    "wednesday": [{"start": "09:00", "end": "13:00"}],
                    "thursday": [{"start": "09:00", "end": "13:00"}],
                    "friday": [{"start": "09:00", "end": "13:00"}],
                    "saturday": [{"start": "09:00", "end": "13:00"}],
                    "sunday": [{"start": "09:00", "end": "11:00"}]
                }
            },
            {
                "name": "Playground Paradise - Flemingdon Park",
                "address": "Flemingdon Park Community Centre, 200 Grenoble Dr, Toronto, ON",
                "lat": 43.7147,
                "lng": -79.3369,
                "phone": "416-395-6014",
                "website": "https://www.toronto.ca/",
                "description": "FREE indoor playground for Toronto residents with climbing structures and play equipment",
                "age_range": "0-12 years",
                "price_info": "FREE for Toronto residents",
                "is_free": True,
                "schedule": {
                    "monday": [{"start": "10:00", "end": "18:00"}],
                    "tuesday": [{"start": "10:00", "end": "18:00"}],
                    "wednesday": [{"start": "10:00", "end": "18:00"}],
                    "thursday": [{"start": "10:00", "end": "20:30"}],
                    "friday": [{"start": "10:00", "end": "20:30"}],
                    "saturday": [{"start": "10:00", "end": "15:30"}],
                    "sunday": [{"start": "10:00", "end": "15:30"}]
                }
            },
            {
                "name": "Kids Fun City",
                "address": "2425 St. Clair Avenue West, Toronto, ON",
                "lat": 43.6684,
                "lng": -79.4947,
                "phone": "416-769-5437",
                "website": "https://kidsfuncity.ca/",
                "description": "Large indoor playground with multiple play zones, slides, and climbing structures",
                "age_range": "1-12 years",
                "price_info": "Drop-in rates available",
                "schedule": {
                    "monday": [{"start": "10:00", "end": "18:00"}],
                    "tuesday": [{"start": "10:00", "end": "18:00"}],
                    "wednesday": [{"start": "10:00", "end": "18:00"}],
                    "thursday": [{"start": "10:00", "end": "18:00"}],
                    "friday": [{"start": "10:00", "end": "18:00"}],
                    "saturday": [{"start": "10:00", "end": "18:00"}],
                    "sunday": [{"start": "10:00", "end": "18:00"}]
                }
            },
            {
                "name": "Liliput Playhouse",
                "address": "1315 Morningside Avenue, Toronto, ON",
                "lat": 43.7856,
                "lng": -79.2001,
                "phone": "416-282-7529",
                "website": "https://www.liliput.ca/",
                "description": "Indoor play center with themed play areas and activities for young children",
                "age_range": "0-7 years",
                "price_info": "Drop-in available",
                "schedule": {
                    "monday": [{"start": "10:00", "end": "17:00"}],
                    "tuesday": [{"start": "10:00", "end": "17:00"}],
                    "wednesday": [{"start": "10:00", "end": "17:00"}],
                    "thursday": [{"start": "10:00", "end": "17:00"}],
                    "friday": [{"start": "10:00", "end": "17:00"}],
                    "saturday": [{"start": "10:00", "end": "17:00"}],
                    "sunday": [{"start": "10:00", "end": "17:00"}]
                }
            }
        ]

    def fetch_events(self, days_ahead: int = 14) -> List[Dict]:
        """Generate recurring drop-in events for indoor play centers"""

        print("🏰 Generating indoor play center drop-in events...")

        events = []
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=days_ahead)

        for center in self.play_centers:
            # Generate events for each day in the range
            current_date = start_date
            while current_date <= end_date:
                day_name = current_date.strftime('%A').lower()
                schedule = center['schedule'].get(day_name, [])

                # Create an event for each time slot on this day
                for time_slot in schedule:
                    event = self._create_event(center, current_date, time_slot)
                    if event:
                        events.append(event)

                current_date += timedelta(days=1)

        print(f"   ✅ Generated {len(events)} drop-in events from {len(self.play_centers)} play centers")
        return events

    def _create_event(self, center: Dict, date: datetime.date, time_slot: Dict) -> Dict:
        """Create a single event for a play center"""

        is_free = center.get('is_free', False)

        # Determine age groups from age_range
        age_groups = self._parse_age_range(center['age_range'])

        event = {
            "title": f"Drop-in Play at {center['name']}",
            "description": f"{center['description']} {center['price_info']}",
            "category": "Sports",  # Active play
            "icon": "🏰",
            "date": date.strftime('%Y-%m-%d'),
            "start_time": time_slot['start'],
            "end_time": time_slot['end'],
            "venue": {
                "name": center['name'],
                "address": center['address'],
                "neighborhood": "Toronto",
                "lat": center['lat'],
                "lng": center['lng']
            },
            "age_groups": age_groups,
            "indoor_outdoor": "Indoor",
            "organized_by": center['name'],
            "website": center['website'],
            "source": "IndoorPlayCenters",
            "scraped_at": datetime.now().isoformat(),
            "is_free": is_free
        }

        if not is_free:
            event['price'] = center['price_info']

        return event

    def _parse_age_range(self, age_range: str) -> List[str]:
        """Parse age range string to standard age groups"""
        age_groups = []

        if '0-2' in age_range or '0-1' in age_range:
            age_groups.append("Babies (0-2)")

        if any(x in age_range for x in ['0-5', '0-6', '0-7', '0-8', '2-5', '3-5', '1-5']):
            age_groups.append("Toddlers (3-5)")

        if any(x in age_range for x in ['6-12', '1-12', '0-12', '5-12']):
            age_groups.append("Kids (6-12)")

        return age_groups if age_groups else ["Toddlers (3-5)", "Kids (6-12)"]


def main():
    scraper = IndoorPlayCentersScraper()
    events = scraper.fetch_events(days_ahead=14)

    print(f"\n📊 Summary:")
    print(f"   Total drop-in events: {len(events)}")

    free_count = len([e for e in events if e.get('is_free')])
    paid_count = len(events) - free_count
    print(f"   Free: {free_count}, Paid: {paid_count}")

    # Save to JSON
    with open('indoor_play_centers_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to indoor_play_centers_events.json")


if __name__ == "__main__":
    main()
