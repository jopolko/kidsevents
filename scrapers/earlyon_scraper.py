#!/usr/bin/env python3
"""
EarlyON Child and Family Centers Scraper
Fetches free drop-in programs for children 0-6 years from Toronto Open Data
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
import re

class EarlyONScraper:
    def __init__(self):
        self.api_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/610e4814-7b85-4bbe-8cc2-e435dd4c539c/resource/b6956076-4456-4a3f-9303-d166c9dbb5d6/download/earlyonlocations_prod.json"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def fetch_events(self, days_ahead: int = 7) -> List[Dict]:
        """Fetch EarlyON drop-in programs for the next week"""

        print("👶 Fetching from EarlyON Child and Family Centers...")

        try:
            response = requests.get(
                self.api_url,
                headers=self.headers,
                timeout=15
            )

            if response.status_code != 200:
                print(f"   ❌ API error: {response.status_code}")
                return []

            data = response.json()
            events = self._parse_earlyon_centers(data, days_ahead)
            print(f"   ✅ Found {len(events)} EarlyON drop-in sessions")
            return events

        except Exception as e:
            print(f"   ❌ Error fetching EarlyON events: {e}")
            return []

    def _parse_earlyon_centers(self, centers: List[Dict], days_ahead: int) -> List[Dict]:
        """Parse EarlyON centers into recurring weekly events"""
        events = []

        # Calculate date range
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        for center in centers:
            # Only include centers with drop-in hours
            dropin_hours = center.get('dropinHours')
            if not dropin_hours or str(dropin_hours).strip().lower() in ['none', '']:
                continue

            dropin_hours = str(dropin_hours).strip()

            # Parse the drop-in schedule
            schedule = self._parse_schedule(dropin_hours)
            if not schedule:
                continue

            # Get location info
            program_name = center.get('program_name', 'EarlyON Center')
            address = center.get('full_address', center.get('address', 'TBD'))
            lat = float(center.get('lat', 43.6532)) if center.get('lat') else 43.6532
            lng = float(center.get('lng', -79.3832)) if center.get('lng') else -79.3832
            phone = center.get('phone', '')
            website = center.get('website', '')
            agency = center.get('agency', 'EarlyON Program')

            # Generate events for each day in the schedule
            for day_name, time_ranges in schedule.items():
                # Find all occurrences of this weekday in the date range
                day_dates = self._get_weekday_dates(day_name, today, end_date)

                for event_date in day_dates:
                    for start_time, end_time in time_ranges:
                        event = {
                            "title": f"EarlyON Drop-In at {program_name}",
                            "description": f"Free drop-in program for children 0-6 years and caregivers. Play, learn, and connect with other families. No registration required.",
                            "category": "Learning",
                            "icon": "👶",
                            "date": event_date.strftime('%Y-%m-%d'),
                            "start_time": start_time,
                            "end_time": end_time,
                            "venue": {
                                "name": program_name,
                                "address": address,
                                "neighborhood": center.get('ward_name', 'Toronto'),
                                "lat": lat,
                                "lng": lng,
                                "phone": phone
                            },
                            "age_groups": ["Babies (0-2)", "Toddlers (3-5)"],
                            "indoor_outdoor": "Indoor",
                            "organized_by": agency,
                            "website": website if website and website.lower() != 'none' else None,
                            "phone": phone,
                            "source": "EarlyON",
                            "scraped_at": datetime.now().isoformat()
                        }
                        events.append(event)

        return events

    def _parse_schedule(self, schedule_str: str) -> Dict:
        """Parse drop-in hours string into structured schedule"""
        # Example: "Wednesday: 9:00 a.m. - 11:30 a.m."
        # Example: "Monday, Wednesday: 9:00 a.m. - 12:00 p.m."
        # Example: "Monday: 9:00 a.m. - noon | Tuesday: 2:00 p.m. - 4:00 p.m."

        schedule = {}

        # Split by common delimiters (pipe, semicolon, newline)
        lines = re.split(r'[;\n|]', schedule_str)

        for line in lines:
            line = line.strip()
            if not line or ':' not in line:
                continue

            # Split day and time
            parts = line.split(':', 1)
            if len(parts) != 2:
                continue

            day_part = parts[0].strip()
            time_part = parts[1].strip()

            # Extract day(s)
            days = []
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                if day in day_part:
                    days.append(day)

            if not days:
                continue

            # Extract time range
            time_range = self._parse_time_range(time_part)
            if not time_range:
                continue

            # Add to schedule
            for day in days:
                if day not in schedule:
                    schedule[day] = []
                schedule[day].append(time_range)

        return schedule

    def _parse_time_range(self, time_str: str) -> tuple:
        """Parse time range string to (start_time, end_time) tuple"""
        # Example: "9:00 a.m. - 11:30 a.m."
        # Example: "9:00am - 12:00pm"

        try:
            # Remove extra spaces and normalize
            time_str = re.sub(r'\s+', ' ', time_str.strip())

            # Find dash or hyphen separator
            if ' - ' in time_str:
                parts = time_str.split(' - ')
            elif '-' in time_str:
                parts = time_str.split('-')
            elif ' to ' in time_str:
                parts = time_str.split(' to ')
            else:
                return None

            if len(parts) != 2:
                return None

            start_str = parts[0].strip()
            end_str = parts[1].strip()

            # Convert to 24-hour format
            start_time = self._convert_to_24h(start_str)
            end_time = self._convert_to_24h(end_str)

            if start_time and end_time:
                return (start_time, end_time)

        except Exception:
            pass

        return None

    def _convert_to_24h(self, time_str: str) -> str:
        """Convert time string to 24-hour HH:MM format"""
        try:
            # Normalize the string
            time_str = time_str.lower().replace('.', '').replace(' ', '')

            # Handle "noon" special case
            if 'noon' in time_str:
                return "12:00"

            # Extract AM/PM
            is_pm = 'pm' in time_str or 'p.m' in time_str
            is_am = 'am' in time_str or 'a.m' in time_str

            # Remove am/pm
            time_str = re.sub(r'[ap]\.?m\.?', '', time_str).strip()

            # Parse time
            if ':' in time_str:
                hour, minute = time_str.split(':', 1)
                hour = int(hour)
                minute = int(minute[:2])  # Take first 2 digits
            else:
                hour = int(time_str)
                minute = 0

            # Convert to 24-hour
            if is_pm and hour != 12:
                hour += 12
            elif is_am and hour == 12:
                hour = 0

            return f"{hour:02d}:{minute:02d}"

        except Exception:
            return None

    def _get_weekday_dates(self, day_name: str, start_date, end_date) -> List:
        """Get all dates for a specific weekday within date range"""
        weekday_map = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }

        target_weekday = weekday_map.get(day_name)
        if target_weekday is None:
            return []

        dates = []
        current_date = start_date

        # Find first occurrence of the weekday
        while current_date.weekday() != target_weekday:
            current_date += timedelta(days=1)
            if current_date > end_date:
                return dates

        # Add all occurrences within range
        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=7)

        return dates


def main():
    scraper = EarlyONScraper()
    events = scraper.fetch_events(days_ahead=7)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    # Save to JSON
    with open('earlyon_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to earlyon_events.json")


if __name__ == "__main__":
    main()
