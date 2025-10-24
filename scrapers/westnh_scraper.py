#!/usr/bin/env python3
"""
West Neighbourhood House (formerly St Christopher House) Scraper
Generates recurring drop-in parenting programs
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict


class WestNHScraper:
    def __init__(self):
        self.name = "West Neighbourhood House"
        self.address = "248 Ossington Avenue, Toronto"
        self.phone = "416-532-4828 x161"
        # Coordinates for 248 Ossington Avenue
        self.lat = 43.6463
        self.lng = -79.4204

    def fetch_events(self, days_ahead: int = 7) -> List[Dict]:
        """Generate recurring drop-in events"""

        print(f"🏘️  Generating West Neighbourhood House drop-in sessions...")

        events = []
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        # Drop-in program runs Tuesday, Wednesday, Thursday, Friday
        # 9:30 AM - 1:00 PM
        drop_in_days = [1, 2, 3, 4]  # Tuesday=1, Wednesday=2, Thursday=3, Friday=4

        current_date = today
        while current_date <= end_date:
            if current_date.weekday() in drop_in_days:
                event = {
                    "title": "Free Drop-In Parenting Program",
                    "description": "Drop-in program for parents/caregivers and children 0-6 years. Indoor playground, arts & crafts, music & movement, and parent relief available. No fees, no registration required.",
                    "category": "Play",
                    "icon": "🎨",
                    "date": current_date.strftime('%Y-%m-%d'),
                    "start_time": "09:30",
                    "end_time": "13:00",
                    "venue": {
                        "name": "West Neighbourhood House",
                        "address": self.address,
                        "neighborhood": "Little Portugal",
                        "lat": self.lat,
                        "lng": self.lng,
                        "phone": self.phone
                    },
                    "age_groups": ["Babies (0-2)", "Toddlers (3-5)"],
                    "indoor_outdoor": "Indoor",
                    "organized_by": "West Neighbourhood House (formerly St Christopher House)",
                    "website": "https://www.westnh.org/",
                    "source": "WestNH",
                    "scraped_at": datetime.now().isoformat(),
                    "is_free": True
                }
                events.append(event)

            current_date += timedelta(days=1)

        print(f"   ✅ Generated {len(events)} West Neighbourhood House events")
        return events


def main():
    scraper = WestNHScraper()
    events = scraper.fetch_events(days_ahead=7)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    # Save to JSON
    with open('westnh_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to westnh_events.json")


if __name__ == "__main__":
    main()
