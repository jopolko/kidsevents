#!/usr/bin/env python3
"""
TEMPLATE: Business Event Scraper
Copy this file and customize for any small/medium business

INSTRUCTIONS:
1. Copy this file: cp TEMPLATE_business_scraper.py mybusiness_scraper.py
2. Replace "BUSINESS_NAME" with the actual business name
3. Update the URL and location details
4. Adjust the parsing logic for the specific website structure
5. Import in data_aggregator.py and add to the main() function
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import re
import time

class BUSINESS_NAMEScraper:
    """
    Scraper for BUSINESS_NAME events
    Website: [ADD WEBSITE URL HERE]
    """

    def __init__(self):
        # ============================================
        # CUSTOMIZE THESE VALUES
        # ============================================
        self.business_name = "BUSINESS_NAME"  # e.g., "Mad Science Toronto"
        self.base_url = "https://example.com"  # Business website
        self.events_url = f"{self.base_url}/events"  # Events page URL

        # Business location (for geocoding)
        self.venue_name = "BUSINESS_NAME Location"
        self.address = "123 Main St, Toronto, ON"
        self.neighborhood = "Downtown"
        self.lat = 43.6532  # Toronto City Hall coords as default
        self.lng = -79.3832

        # Event defaults
        self.default_category = "Learning"  # Learning, Arts, Sports, Nature, Entertainment
        self.default_icon = "🔬"  # Choose appropriate emoji
        self.default_age_groups = ["Kids (6-12)"]  # Adjust as needed
        self.indoor_outdoor = "Indoor"  # Indoor, Outdoor, or Both

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def fetch_events(self, days_ahead: int = 30) -> List[Dict]:
        """Fetch events from the business website"""

        print(f"🎯 Fetching from {self.business_name}...")

        try:
            time.sleep(1)  # Be polite - don't hammer small business sites

            response = requests.get(self.events_url, headers=self.headers, timeout=15)

            if response.status_code != 200:
                print(f"   ⚠️  HTTP {response.status_code}")
                return []

            soup = BeautifulSoup(response.content, 'html.parser')
            events = []

            # ============================================
            # CUSTOMIZE THIS PART - Find event elements
            # ============================================

            # Option 1: Find by class name (inspect the website to find the right class)
            event_items = soup.find_all('div', class_='event-item')

            # Option 2: Find by tag and class pattern
            # event_items = soup.find_all(class_=lambda x: x and 'event' in str(x).lower())

            # Option 3: Find articles or posts
            # event_items = soup.find_all(['article', 'div'], class_='post')

            # Option 4: Find by ID pattern
            # event_items = soup.find_all(id=re.compile(r'event-\d+'))

            for item in event_items[:20]:  # Limit to first 20 events
                parsed = self._parse_event(item)
                if parsed:
                    events.append(parsed)

            if events:
                print(f"   ✅ Found {len(events)} events from {self.business_name}")
            else:
                print(f"   ⚠️  No events found - check the CSS selectors")

            return events

        except Exception as e:
            print(f"   ❌ Error fetching {self.business_name} events: {e}")
            return []

    def _parse_event(self, item) -> Dict:
        """Parse an individual event item"""

        try:
            # ============================================
            # CUSTOMIZE THIS PART - Extract event details
            # ============================================

            # Extract title
            title_elem = item.find(['h1', 'h2', 'h3', 'h4'])
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)

            # Extract link
            link_elem = item.find('a', href=True)
            url = self.base_url  # Default to homepage
            if link_elem:
                url = link_elem['href']
                if not url.startswith('http'):
                    url = self.base_url + ('/' if not url.startswith('/') else '') + url

            # Extract description
            desc_elem = item.find('p', class_='description')  # Adjust class name
            description = desc_elem.get_text(strip=True)[:200] if desc_elem else title

            # Extract date
            date_elem = item.find(class_='event-date')  # Adjust class name
            event_date = self._parse_date(date_elem.get_text() if date_elem else '')

            # Extract time
            time_elem = item.find(class_='event-time')  # Adjust class name
            start_time, end_time = self._parse_time(time_elem.get_text() if time_elem else '')

            # Create event object
            event = {
                'title': title,
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
                'source': self.business_name.replace(' ', '')
            }

            return event

        except Exception as e:
            return None

    def _parse_date(self, date_text: str) -> str:
        """Parse date from text - customize as needed"""

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
            '%m/%d/%Y',       # 01/15/2025
            '%d/%m/%Y',       # 15/01/2025
        ]

        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_text.strip(), fmt)
                return date_obj.strftime('%Y-%m-%d')
            except:
                pass

        # Try month + day pattern
        match = re.search(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2})', date_text, re.IGNORECASE)
        if match:
            month_abbr = date_text[:3].capitalize()
            months = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                     'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
            if month_abbr in months:
                day = int(match.group(1))
                month = months[month_abbr]
                year = today.year
                if month < today.month:
                    year += 1
                try:
                    return datetime(year, month, day).strftime('%Y-%m-%d')
                except:
                    pass

        # Default to next week
        return (today + timedelta(days=7)).strftime('%Y-%m-%d')

    def _parse_time(self, time_text: str) -> tuple:
        """Parse start and end time from text"""

        if not time_text:
            return ('10:00', '16:00')  # Default time

        # Try to find time patterns like "2:00 PM - 4:00 PM" or "14:00-16:00"
        time_pattern = r'(\d{1,2}):?(\d{2})?\s*(am|pm)?.*?(\d{1,2}):?(\d{2})?\s*(am|pm)?'
        match = re.search(time_pattern, time_text, re.IGNORECASE)

        if match:
            start_hour = int(match.group(1))
            start_min = match.group(2) or '00'
            start_period = match.group(3) or ''

            end_hour = int(match.group(4)) if match.group(4) else start_hour + 2
            end_min = match.group(5) or '00'
            end_period = match.group(6) or start_period

            # Convert to 24-hour format if PM
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

        return ('10:00', '16:00')  # Default


# ============================================
# TEST THE SCRAPER
# ============================================
if __name__ == "__main__":
    scraper = BUSINESS_NAMEScraper()
    events = scraper.fetch_events()

    print(f"\n{'='*60}")
    print(f"Total events found: {len(events)}")
    print(f"{'='*60}")

    if events:
        print("\nFirst event:")
        import json
        print(json.dumps(events[0], indent=2))
    else:
        print("\nNo events found. Check:")
        print("1. Is the events_url correct?")
        print("2. Are the CSS selectors matching the website structure?")
        print("3. Does the website require JavaScript rendering?")
