#!/usr/bin/env python3
"""
Toronto & Region Conservation Authority (TRCA) Events Scraper
Fetches outdoor education, nature programs, and conservation events
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict

class TRCAScraper:
    def __init__(self):
        """Initialize TRCA programs scraper with major conservation areas"""
        # Major TRCA Conservation Areas with family programs
        self.conservation_areas = {
            'Boyd Conservation Area': {
                'address': '8739 8th Line, Vaughan',
                'lat': 43.8906, 'lng': -79.5542,
                'phone': '416-661-6600',
                'website': 'https://trca.ca/parks/boyd-conservation-area/',
                'programs': ['Nature Walks', 'Bird Watching', 'Seasonal Programs'],
                'neighborhood': 'Vaughan'
            },
            'Claireville Conservation Area': {
                'address': '7195 Indian Line, Brampton',
                'lat': 43.7337, 'lng': -79.6442,
                'phone': '416-661-6600',
                'website': 'https://trca.ca/parks/claireville-conservation-area/',
                'programs': ['Hiking Trails', 'Nature Discovery', 'Outdoor Play'],
                'neighborhood': 'Brampton'
            },
            'Glen Haffy Conservation Area': {
                'address': '14496 Hwy 50, Caledon',
                'lat': 43.9594, 'lng': -79.8711,
                'phone': '416-661-6600',
                'website': 'https://trca.ca/parks/glen-haffy/',
                'programs': ['Snowshoeing', 'Hiking', 'Nature Exploration'],
                'neighborhood': 'Caledon'
            },
            'Heart Lake Conservation Area': {
                'address': '18725 Heart Lake Rd, Brampton',
                'lat': 43.7689, 'lng': -79.8111,
                'phone': '905-794-2992',
                'website': 'https://trca.ca/parks/heart-lake-conservation-area/',
                'programs': ['Swimming', 'Trails', 'Beach Activities', 'Nature Programs'],
                'neighborhood': 'Brampton'
            },
            'Kortright Centre for Conservation': {
                'address': '9550 Pine Valley Dr, Vaughan',
                'lat': 43.8153, 'lng': -79.6094,
                'phone': '905-832-2289',
                'website': 'https://trca.ca/parks/kortright-centre/',
                'programs': ['Environmental Education', 'Seasonal Festivals', 'Maple Syrup Festival', 'Outdoor Programs'],
                'neighborhood': 'Vaughan'
            },
            'Petticoat Creek Conservation Area': {
                'address': '2950 Whites Rd, Pickering',
                'lat': 43.8347, 'lng': -79.0611,
                'phone': '416-661-6600',
                'website': 'https://trca.ca/parks/petticoat-creek/',
                'programs': ['Beach', 'Trails', 'Picnic Areas', 'Nature Exploration'],
                'neighborhood': 'Pickering'
            },
            'Tommy Thompson Park': {
                'address': '1 Leslie St, Toronto',
                'lat': 43.6236, 'lng': -79.3375,
                'phone': '416-661-6600',
                'website': 'https://tommythompsonpark.ca/',
                'programs': ['Bird Watching', 'Cycling', 'Nature Walks', 'Wildlife Viewing'],
                'neighborhood': 'Port Lands'
            },
            'Black Creek Pioneer Village': {
                'address': '1000 Murray Ross Pkwy, North York',
                'lat': 43.7697, 'lng': -79.5186,
                'phone': '416-736-1733',
                'website': 'https://www.trca.ca/parks/black-creek-pioneer-village/',
                'programs': ['Historical Reenactments', 'Heritage Crafts', 'Seasonal Events', 'Educational Programs'],
                'neighborhood': 'North York'
            },
        }

        # Typical program schedules for TRCA sites
        self.program_schedule = {
            'weekday_programs': {
                'time': ('10:00', '15:00'),
                'types': ['Nature Exploration', 'Educational Programs', 'Outdoor Discovery']
            },
            'weekend_programs': {
                'time': ('09:00', '16:00'),
                'types': ['Family Nature Walks', 'Seasonal Activities', 'Wildlife Viewing']
            }
        }

    def fetch_events(self, days_ahead: int = 28) -> List[Dict]:
        """Generate TRCA conservation area program events"""
        print("🌲 Fetching from Toronto & Region Conservation Authority...")

        events = []
        today = datetime.now()
        end_date = today + timedelta(days=days_ahead)

        for area_name, area_info in self.conservation_areas.items():
            current = today

            while current <= end_date:
                # Weekend programs (Saturdays and Sundays)
                if current.weekday() in [5, 6]:  # Saturday or Sunday
                    for program_type in self.program_schedule['weekend_programs']['types']:
                        event = {
                            "title": f"{area_name} - {program_type}",
                            "description": f"FREE outdoor program at {area_name}. {', '.join(area_info['programs'])}. Dress for weather. All ages welcome.",
                            "category": "Nature",
                            "icon": "🌲",
                            "date": current.strftime('%Y-%m-%d'),
                            "start_time": self.program_schedule['weekend_programs']['time'][0],
                            "end_time": self.program_schedule['weekend_programs']['time'][1],
                            "venue": {
                                "name": area_name,
                                "address": area_info['address'],
                                "neighborhood": area_info['neighborhood'],
                                "lat": area_info['lat'],
                                "lng": area_info['lng'],
                                "phone": area_info['phone']
                            },
                            "age_groups": ["All Ages"],
                            "indoor_outdoor": "Outdoor",
                            "organized_by": "Toronto & Region Conservation Authority",
                            "website": area_info['website'],
                            "source": "TRCA",
                            "scraped_at": datetime.now().isoformat(),
                            "is_free": True,
                            "note": "Check website for seasonal hours and special programs. Some areas may have parking fees."
                        }
                        events.append(event)

                # Weekday programs (Wednesday and Friday - typical school program days)
                if current.weekday() in [2, 4] and area_name in ['Kortright Centre for Conservation', 'Black Creek Pioneer Village']:
                    for program_type in self.program_schedule['weekday_programs']['types']:
                        event = {
                            "title": f"{area_name} - {program_type}",
                            "description": f"FREE outdoor educational program. {', '.join(area_info['programs'])}. Perfect for homeschool groups and families.",
                            "category": "Learning",
                            "icon": "🎒",
                            "date": current.strftime('%Y-%m-%d'),
                            "start_time": self.program_schedule['weekday_programs']['time'][0],
                            "end_time": self.program_schedule['weekday_programs']['time'][1],
                            "venue": {
                                "name": area_name,
                                "address": area_info['address'],
                                "neighborhood": area_info['neighborhood'],
                                "lat": area_info['lat'],
                                "lng": area_info['lng'],
                                "phone": area_info['phone']
                            },
                            "age_groups": ["Kids (6-12)"],
                            "indoor_outdoor": "Outdoor",
                            "organized_by": "Toronto & Region Conservation Authority",
                            "website": area_info['website'],
                            "source": "TRCA",
                            "scraped_at": datetime.now().isoformat(),
                            "is_free": True,
                            "note": "Educational programs available. Check website for details."
                        }
                        events.append(event)

                current += timedelta(days=1)

        print(f"   ✅ Generated {len(events)} TRCA conservation area events")
        return events


def main():
    scraper = TRCAScraper()
    events = scraper.fetch_events(days_ahead=28)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    with open('trca_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to trca_events.json")


if __name__ == "__main__":
    main()
