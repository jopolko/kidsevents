#!/usr/bin/env python3
"""
MOCA (Museum of Contemporary Art Toronto) Event Scraper
Website: https://moca.ca
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import re
import time

class MOCAScraper:
    """
    Scraper for MOCA Toronto events
    Website: https://moca.ca/families/ and https://moca.ca/events/
    Note: Free admission for visitors 18 and under
    """

    def __init__(self):
        self.business_name = "MOCA Toronto"
        self.base_url = "https://moca.ca"
        self.events_url = f"{self.base_url}/events/"
        self.families_url = f"{self.base_url}/families/"

        # MOCA location
        self.venue_name = "Museum of Contemporary Art Toronto"
        self.address = "158 Sterling Rd, Toronto, ON M6R 2B2"
        self.neighborhood = "Junction Triangle"
        self.lat = 43.6464
        self.lng = -79.4476

        # Event defaults
        self.default_category = "Arts"
        self.default_icon = "🎨"
        self.default_age_groups = ["Kids (6-12)", "Teens (13-17)", "Toddlers (3-5)"]
        self.indoor_outdoor = "Indoor"

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def fetch_events(self, days_ahead: int = 90) -> List[Dict]:
        """Fetch events from MOCA website"""

        print(f"🎨 Fetching from {self.business_name}...")

        events = []

        # Try events page first
        events.extend(self._fetch_from_url(self.events_url))

        # Add recurring family programs
        events.extend(self._generate_family_programs(days_ahead))

        if events:
            print(f"   ✅ Found {len(events)} MOCA events")
        else:
            print(f"   ⚠️  No MOCA events found")

        return events

    def _fetch_from_url(self, url: str) -> List[Dict]:
        """Fetch events from a specific URL"""

        try:
            time.sleep(1)  # Be polite
            response = requests.get(url, headers=self.headers, timeout=15)

            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.content, 'html.parser')
            events = []

            # Look for event elements (Elementor-based site)
            # Try multiple selectors
            event_items = soup.find_all('article', class_=lambda x: x and 'event' in str(x).lower())

            if not event_items:
                # Try finding by heading + date pattern
                event_items = soup.find_all(['div', 'section'],
                                           class_=lambda x: x and ('elementor' in str(x).lower() or 'event' in str(x).lower()))

            for item in event_items[:15]:  # Limit to first 15 events
                parsed = self._parse_event(item)
                if parsed:
                    events.append(parsed)

            return events

        except Exception as e:
            return []

    def _parse_event(self, item) -> Dict:
        """Parse an individual event item"""

        try:
            # Extract title
            title_elem = item.find(['h1', 'h2', 'h3', 'h4', 'h5'])
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)

            # Skip if not kid-friendly
            if not self._is_family_friendly(title):
                return None

            # Extract link
            link_elem = item.find('a', href=True)
            url = self.base_url
            if link_elem:
                url = link_elem['href']
                if not url.startswith('http'):
                    url = self.base_url + ('/' if not url.startswith('/') else '') + url

            # Extract description
            desc_elem = item.find('p')
            description = desc_elem.get_text(strip=True)[:200] if desc_elem else title

            # Extract date - look for date patterns
            date_text = item.get_text()
            event_date = self._parse_date(date_text)

            # Extract time
            start_time, end_time = self._parse_time(date_text)

            # Determine if free (admission is free for under 18)
            is_free = "free" in title.lower() or "free with admission" in description.lower()

            event = {
                'title': f"{title} (Free for kids 18 & under)",
                'description': description,
                'category': self.default_category,
                'icon': self.default_icon,
                'date': event_date,
                'start_time': start_time,
                'end_time': end_time,
                'venue': {
                    'name': self.venue_name,
                    'address': self.address,
                    'neighborhood': self.neighborhood,
                    'lat': self.lat,
                    'lng': self.lng
                },
                'age_groups': self.default_age_groups,
                'indoor_outdoor': self.indoor_outdoor,
                'organized_by': self.business_name,
                'website': url,
                'source': 'MOCA'
            }

            return event

        except Exception as e:
            return None

    def _generate_family_programs(self, days_ahead: int) -> List[Dict]:
        """Generate recurring family programs"""

        events = []
        today = datetime.now()
        end_date = today + timedelta(days=days_ahead)

        # TD Community Sundays (first full weekend of every month)
        current = today
        while current <= end_date:
            # Find first Sunday of the month
            first_of_month = current.replace(day=1)
            # Find first Sunday
            days_to_sunday = (6 - first_of_month.weekday()) % 7
            if days_to_sunday == 0:
                days_to_sunday = 7
            first_sunday = first_of_month + timedelta(days=days_to_sunday)

            if first_sunday >= today and first_sunday <= end_date:
                events.append({
                    'title': "TD Community Sunday - Free Admission for All",
                    'description': "Free admission for everyone! Explore contemporary art with family-friendly activities.",
                    'category': "Arts",
                    'icon': "🎨",
                    'date': first_sunday.strftime('%Y-%m-%d'),
                    'start_time': "11:00",
                    'end_time': "18:00",
                    'venue': {
                        'name': self.venue_name,
                        'address': self.address,
                        'neighborhood': self.neighborhood,
                        'lat': self.lat,
                        'lng': self.lng
                    },
                    'age_groups': ["Babies (0-2)", "Toddlers (3-5)", "Kids (6-12)", "Teens (13-17)"],
                    'indoor_outdoor': "Indoor",
                    'organized_by': self.business_name,
                    'website': f"{self.base_url}/families/",
                    'source': 'MOCA'
                })

            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        # Saturday Drop-in Tours (every Saturday)
        current = today
        while current <= end_date:
            if current.weekday() == 5:  # Saturday
                if current >= today:
                    # 12 PM tour
                    events.append({
                        'title': "Saturday Drop-in Tour (12 PM)",
                        'description': "Free guided tour exploring MOCA's current exhibitions. Free admission for kids 18 & under.",
                        'category': "Arts",
                        'icon': "🎨",
                        'date': current.strftime('%Y-%m-%d'),
                        'start_time': "12:00",
                        'end_time': "13:00",
                        'venue': {
                            'name': self.venue_name,
                            'address': self.address,
                            'neighborhood': self.neighborhood,
                            'lat': self.lat,
                            'lng': self.lng
                        },
                        'age_groups': ["Kids (6-12)", "Teens (13-17)"],
                        'indoor_outdoor': "Indoor",
                        'organized_by': self.business_name,
                        'website': f"{self.base_url}/families/",
                        'source': 'MOCA'
                    })

                    # 2 PM tour
                    events.append({
                        'title': "Saturday Drop-in Tour (2 PM)",
                        'description': "Free guided tour exploring MOCA's current exhibitions. Free admission for kids 18 & under.",
                        'category': "Arts",
                        'icon': "🎨",
                        'date': current.strftime('%Y-%m-%d'),
                        'start_time': "14:00",
                        'end_time': "15:00",
                        'venue': {
                            'name': self.venue_name,
                            'address': self.address,
                            'neighborhood': self.neighborhood,
                            'lat': self.lat,
                            'lng': self.lng
                        },
                        'age_groups': ["Kids (6-12)", "Teens (13-17)"],
                        'indoor_outdoor': "Indoor",
                        'organized_by': self.business_name,
                        'website': f"{self.base_url}/families/",
                        'source': 'MOCA'
                    })

            current += timedelta(days=1)

        return events

    def _is_family_friendly(self, title: str) -> bool:
        """Check if event is family-friendly"""

        family_keywords = [
            'workshop', 'drop-in', 'family', 'kids', 'children', 'art hive',
            'community sunday', 'tour', 'drawing', 'creative', 'making'
        ]

        title_lower = title.lower()

        # Check for family keywords
        if any(keyword in title_lower for keyword in family_keywords):
            return True

        # Exclude adult-only events
        adult_keywords = ['wine', 'cocktail', 'adults only', 'after hours', '19+', '18+']
        if any(keyword in title_lower for keyword in adult_keywords):
            return False

        return True

    def _parse_date(self, date_text: str) -> str:
        """Parse date from text"""

        if not date_text:
            # Default to next Saturday
            today = datetime.now()
            days_to_sat = (5 - today.weekday()) % 7
            if days_to_sat == 0:
                days_to_sat = 7
            return (today + timedelta(days=days_to_sat)).strftime('%Y-%m-%d')

        today = datetime.now()

        # Try parsing common date formats
        date_formats = [
            '%B %d, %Y',      # January 15, 2025
            '%b %d, %Y',      # Jan 15, 2025
            '%Y-%m-%d',       # 2025-01-15
        ]

        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_text.strip(), fmt)
                return date_obj.strftime('%Y-%m-%d')
            except:
                pass

        # Try month + day pattern (e.g., "October 25, 2025")
        match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})', date_text, re.IGNORECASE)
        if match:
            month_name = match.group(1).capitalize()
            day = int(match.group(2))
            year = int(match.group(3))

            months = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }

            if month_name in months:
                try:
                    return datetime(year, months[month_name], day).strftime('%Y-%m-%d')
                except:
                    pass

        # Default to next week
        return (today + timedelta(days=7)).strftime('%Y-%m-%d')

    def _parse_time(self, time_text: str) -> tuple:
        """Parse start and end time from text"""

        if not time_text:
            return ('10:00', '17:00')  # Museum hours

        # Try to find time patterns
        time_pattern = r'(\d{1,2}):(\d{2})\s*(am|pm)?(?:\s*[-–]\s*(\d{1,2}):(\d{2})\s*(am|pm)?)?'
        match = re.search(time_pattern, time_text, re.IGNORECASE)

        if match:
            start_hour = int(match.group(1))
            start_min = match.group(2)
            start_period = match.group(3) or ''

            end_hour = int(match.group(4)) if match.group(4) else start_hour + 1
            end_min = match.group(5) or '00'
            end_period = match.group(6) or start_period

            # Convert to 24-hour format
            if start_period.lower() == 'pm' and start_hour != 12:
                start_hour += 12
            if start_period.lower() == 'am' and start_hour == 12:
                start_hour = 0

            if end_period.lower() == 'pm' and end_hour != 12:
                end_hour += 12
            if end_period.lower() == 'am' and end_hour == 12:
                end_hour = 0

            start_time = f"{start_hour:02d}:{start_min}"
            end_time = f"{end_hour:02d}:{end_min}"

            return (start_time, end_time)

        return ('10:00', '17:00')  # Default museum hours


if __name__ == "__main__":
    scraper = MOCAScraper()
    events = scraper.fetch_events()

    print(f"\n{'='*60}")
    print(f"Total events found: {len(events)}")
    print(f"{'='*60}")

    if events:
        print("\nFirst few events:")
        import json
        for event in events[:3]:
            print(json.dumps(event, indent=2))
            print()
