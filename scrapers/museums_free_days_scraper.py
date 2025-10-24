#!/usr/bin/env python3
"""
Museums & Cultural Centers Free Days Scraper
Generates recurring free admission events for ROM, AGO, and special cultural events
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict
from dateutil.relativedelta import relativedelta

class MuseumFreeDaysScraper:
    def __init__(self):
        self.venues = {
            'ROM': {
                'name': 'Royal Ontario Museum',
                'address': '100 Queens Park',
                'lat': 43.6677,
                'lng': -79.3948,
                'website': 'https://www.rom.on.ca'
            },
            'AGO': {
                'name': 'Art Gallery of Ontario',
                'address': '317 Dundas St W',
                'lat': 43.6536,
                'lng': -79.3925,
                'website': 'https://ago.ca'
            },
            'Harbourfront': {
                'name': 'Harbourfront Centre',
                'address': '235 Queens Quay W',
                'lat': 43.6387,
                'lng': -79.3816,
                'website': 'https://harbourfrontcentre.com'
            },
            'OSC_Harbourfront': {
                'name': 'Ontario Science Centre KidSpark at Harbourfront',
                'address': '235 Queens Quay W',
                'lat': 43.6387,
                'lng': -79.3816,
                'website': 'https://www.ontariosciencecentre.ca'
            },
            'OSC_Sherway': {
                'name': 'Ontario Science Centre at CF Sherway Gardens',
                'address': '25 The West Mall',
                'lat': 43.6104,
                'lng': -79.5576,
                'website': 'https://www.ontariosciencecentre.ca'
            }
        }

    def fetch_events(self, months_ahead: int = 3) -> List[Dict]:
        """Generate free museum and cultural events for the next few months"""

        print("🏛️  Generating museum & cultural free days...")

        events = []

        # ROM Third Tuesday Nights Free
        events.extend(self._generate_rom_third_tuesdays(months_ahead))

        # AGO First Wednesday Nights Free
        events.extend(self._generate_ago_first_wednesdays(months_ahead))

        # AGO Free Main Floor (Oct 1 - Nov 30, 2025)
        events.extend(self._generate_ago_free_main_floor())

        # ROM Free Main Floor (Oct 1 - Nov 30, 2025)
        events.extend(self._generate_rom_free_main_floor())

        # Harbourfront Centre ongoing free programs
        events.extend(self._generate_harbourfront_ongoing())

        # Ontario Science Centre pop-up locations
        events.extend(self._generate_osc_popup())

        print(f"   ✅ Generated {len(events)} museum/cultural events")
        return events

    def _generate_rom_third_tuesdays(self, months_ahead: int) -> List[Dict]:
        """Generate ROM Third Tuesday Night Free events"""
        events = []
        today = datetime.now()

        for month_offset in range(months_ahead + 1):
            target_month = today + relativedelta(months=month_offset)

            # Find third Tuesday of the month
            first_day = target_month.replace(day=1)

            # Find first Tuesday
            days_until_tuesday = (1 - first_day.weekday()) % 7
            first_tuesday = first_day + timedelta(days=days_until_tuesday)

            # Third Tuesday is 2 weeks later
            third_tuesday = first_tuesday + timedelta(weeks=2)

            # Skip if in the past
            if third_tuesday.date() < today.date():
                continue

            venue = self.venues['ROM']

            event = {
                "title": "ROM Third Tuesday Night FREE Admission",
                "description": "Free admission for everyone on the third Tuesday evening of each month! Explore world cultures, natural history, and special exhibitions. Advance tickets required (released 2 weeks prior).",
                "category": "Learning",
                "icon": "🏛️",
                "date": third_tuesday.strftime('%Y-%m-%d'),
                "start_time": "16:30",
                "end_time": "20:30",
                "venue": {
                    "name": venue['name'],
                    "address": venue['address'],
                    "neighborhood": "Downtown",
                    "lat": venue['lat'],
                    "lng": venue['lng']
                },
                "age_groups": ["All Ages"],
                "indoor_outdoor": "Indoor",
                "organized_by": "Royal Ontario Museum",
                "website": venue['website'] + "/whats-on/special-programs/third-tuesday-nights-free",
                "source": "Museums"
            }
            events.append(event)

        return events

    def _generate_ago_first_wednesdays(self, months_ahead: int) -> List[Dict]:
        """Generate AGO First Wednesday Night Free events"""
        events = []
        today = datetime.now()

        for month_offset in range(months_ahead + 1):
            target_month = today + relativedelta(months=month_offset)

            # Find first Wednesday of the month
            first_day = target_month.replace(day=1)
            days_until_wednesday = (2 - first_day.weekday()) % 7
            first_wednesday = first_day + timedelta(days=days_until_wednesday)

            # Skip if in the past
            if first_wednesday.date() < today.date():
                continue

            venue = self.venues['AGO']

            event = {
                "title": "AGO First Wednesday Night FREE Admission",
                "description": "Free admission on the first Wednesday evening of each month! See world-class art collections including Canadian, European, and contemporary works. Tickets released Monday before.",
                "category": "Arts",
                "icon": "🎨",
                "date": first_wednesday.strftime('%Y-%m-%d'),
                "start_time": "18:00",
                "end_time": "21:00",
                "venue": {
                    "name": venue['name'],
                    "address": venue['address'],
                    "neighborhood": "Downtown",
                    "lat": venue['lat'],
                    "lng": venue['lng']
                },
                "age_groups": ["All Ages"],
                "indoor_outdoor": "Indoor",
                "organized_by": "Art Gallery of Ontario",
                "website": venue['website'] + "/visit/free-wednesday-nights",
                "source": "ArtGallery"
            }
            events.append(event)

        return events

    def _generate_ago_free_main_floor(self) -> List[Dict]:
        """Generate AGO Free Main Floor events (Oct 1 - Nov 30, 2025)"""
        events = []
        start_date = datetime(2025, 10, 1)
        end_date = datetime(2025, 11, 30)
        today = datetime.now()

        # Generate events for Saturdays and Sundays
        current = start_date
        venue = self.venues['AGO']

        while current <= end_date:
            if current.weekday() in [5, 6] and current.date() >= today.date():  # Saturday or Sunday
                event = {
                    "title": "AGO Free Main Floor + Weekend Activities",
                    "description": "Free access to first-floor galleries! Enjoy pop-up performances showcasing local artists and educational activities for all ages. Every weekend has a fresh theme!",
                    "category": "Arts",
                    "icon": "🎨",
                    "date": current.strftime('%Y-%m-%d'),
                    "start_time": "10:00",
                    "end_time": "17:00",
                    "venue": {
                        "name": venue['name'],
                        "address": venue['address'],
                        "neighborhood": "Downtown",
                        "lat": venue['lat'],
                        "lng": venue['lng']
                    },
                    "age_groups": ["All Ages"],
                    "indoor_outdoor": "Indoor",
                    "organized_by": "Art Gallery of Ontario",
                    "website": venue['website'],
                    "source": "ArtGallery"
                }
                events.append(event)

            current += timedelta(days=1)

        return events

    def _generate_rom_free_main_floor(self) -> List[Dict]:
        """Generate ROM Free Main Floor events (Oct 1 - Nov 30, 2025)"""
        events = []
        start_date = datetime(2025, 10, 1)
        end_date = datetime(2025, 11, 30)
        today = datetime.now()

        # Generate events for Saturdays and Sundays
        current = start_date
        venue = self.venues['ROM']

        while current <= end_date:
            if current.weekday() in [5, 6] and current.date() >= today.date():  # Saturday or Sunday
                event = {
                    "title": "ROM Free Main Floor + Weekend Activities",
                    "description": "Free access to expansive first-floor galleries! Every weekend brings fresh themes with pop-up performances, local artists, and exciting educational activities for all ages.",
                    "category": "Learning",
                    "icon": "🏛️",
                    "date": current.strftime('%Y-%m-%d'),
                    "start_time": "10:00",
                    "end_time": "17:30",
                    "venue": {
                        "name": venue['name'],
                        "address": venue['address'],
                        "neighborhood": "Downtown",
                        "lat": venue['lat'],
                        "lng": venue['lng']
                    },
                    "age_groups": ["All Ages"],
                    "indoor_outdoor": "Indoor",
                    "organized_by": "Royal Ontario Museum",
                    "website": venue['website'],
                    "source": "Museums"
                }
                events.append(event)

            current += timedelta(days=1)

        return events

    def _generate_harbourfront_ongoing(self) -> List[Dict]:
        """Generate Harbourfront Centre ongoing free activities"""
        events = []
        today = datetime.now()
        venue = self.venues['Harbourfront']

        # Generate for next 30 days, every day
        for day_offset in range(30):
            current = today + timedelta(days=day_offset)

            event = {
                "title": "Harbourfront Centre - Free Waterfront Activities",
                "description": "Explore Toronto's waterfront! Free art exhibitions, outdoor spaces, and family-friendly activities daily. Check website for current events and performances.",
                "category": "Entertainment",
                "icon": "🎭",
                "date": current.strftime('%Y-%m-%d'),
                "start_time": "10:00",
                "end_time": "20:00",
                "venue": {
                    "name": venue['name'],
                    "address": venue['address'],
                    "neighborhood": "Waterfront",
                    "lat": venue['lat'],
                    "lng": venue['lng']
                },
                "age_groups": ["All Ages"],
                "indoor_outdoor": "Both",
                "organized_by": "Harbourfront Centre",
                "website": venue['website'],
                "source": "Entertainment"
            }
            events.append(event)

        return events

    def _generate_osc_popup(self) -> List[Dict]:
        """Generate Ontario Science Centre pop-up location events"""
        events = []
        today = datetime.now()
        end_date = datetime(2025, 12, 31)  # Extended through 2025

        venues = ['OSC_Harbourfront', 'OSC_Sherway']

        for venue_key in venues:
            venue = self.venues[venue_key]
            current = today

            while current <= end_date:
                # Only generate for days when OSC is typically open (Tue-Sun)
                if current.weekday() < 6:  # Not Monday
                    event = {
                        "title": f"Ontario Science Centre Pop-Up - Hands-On STEM Play",
                        "description": "Interactive STEM exhibits for kids 10 and under! Explore Innovation Station, Imagination Playground, and Rigamajig. Note: $15 admission (free for ages 2 and under, free for Indigenous peoples).",
                        "category": "Learning",
                        "icon": "🔬",
                        "date": current.strftime('%Y-%m-%d'),
                        "start_time": "10:00",
                        "end_time": "17:00",
                        "venue": {
                            "name": venue['name'],
                            "address": venue['address'],
                            "neighborhood": "Toronto",
                            "lat": venue['lat'],
                            "lng": venue['lng']
                        },
                        "age_groups": ["Babies (0-2)", "Toddlers (3-5)", "Kids (6-12)"],
                        "indoor_outdoor": "Indoor",
                        "organized_by": "Ontario Science Centre",
                        "website": venue['website'],
                        "source": "ScienceCentre"
                    }
                    events.append(event)

                current += timedelta(days=7)  # Weekly to avoid overwhelming with daily entries

        return events


def main():
    scraper = MuseumFreeDaysScraper()
    events = scraper.fetch_events(months_ahead=3)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    # Save to JSON
    with open('museum_free_days.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to museum_free_days.json")


if __name__ == "__main__":
    main()
