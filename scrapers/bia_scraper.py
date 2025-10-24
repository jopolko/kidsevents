#!/usr/bin/env python3
"""
Toronto BIA (Business Improvement Area) Events Scraper
Fetches community events from Toronto neighborhood BIAs
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import re
import time

class BIAScraper:
    def __init__(self):
        # Toronto BIA websites
        self.bias = [
            {
                'name': 'Beaches',
                'url': 'https://thebeachesbia.com/events',
                'lat': 43.6672,
                'lng': -79.2970
            },
            {
                'name': 'Bloor West Village',
                'url': 'https://bloorwestvillagebia.com/events',
                'lat': 43.6509,
                'lng': -79.4856
            },
            {
                'name': 'Leslieville',
                'url': 'https://leslieville.com/events',
                'lat': 43.6616,
                'lng': -79.3302
            },
            {
                'name': 'Kensington Market',
                'url': 'https://kensingtonmarketbia.com/events',
                'lat': 43.6549,
                'lng': -79.4001
            },
        ]

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def fetch_events(self, days_ahead: int = 30) -> List[Dict]:
        """Fetch events from Toronto BIAs"""

        print("🏘️  Fetching from Toronto BIAs...")

        all_events = []

        for bia in self.bias:
            print(f"   📍 Checking {bia['name']}...")
            try:
                time.sleep(2)  # Be very polite to small business sites

                response = requests.get(bia['url'], headers=self.headers, timeout=15)

                if response.status_code != 200:
                    print(f"      ⚠️  HTTP {response.status_code}")
                    continue

                soup = BeautifulSoup(response.content, 'html.parser')

                # Generic event finding - look for common patterns
                events = self._find_events(soup, bia)

                if events:
                    all_events.extend(events)
                    print(f"      ✅ Found {len(events)} events")
                else:
                    print(f"      ⚠️  No events found")

            except Exception as e:
                print(f"      ❌ Error: {e}")
                continue

        if all_events:
            print(f"   ✅ Total BIA events: {len(all_events)}")
        else:
            print(f"   ⚠️  No BIA events found")

        return all_events

    def _find_events(self, soup, bia: Dict) -> List[Dict]:
        """Find events on a BIA page"""

        events = []

        # Look for event containers - common class names
        event_selectors = [
            'event',
            'tribe-event',
            'eo-event',
            'calendar-event',
            'vevent'
        ]

        event_items = []
        for selector in event_selectors:
            items = soup.find_all(class_=lambda x: x and selector in str(x).lower())
            if items:
                event_items.extend(items)
                break

        # If no specific event classes, look for articles or posts
        if not event_items:
            event_items = soup.find_all(['article', 'div'], class_=lambda x: x and ('post' in str(x).lower() or 'item' in str(x).lower()))

        for item in event_items[:10]:  # Limit per BIA
            parsed = self._parse_event(item, bia)
            if parsed:
                events.append(parsed)

        return events

    def _parse_event(self, item, bia: Dict) -> Dict:
        """Parse an individual event"""

        try:
            # Extract title
            title_elem = item.find(['h1', 'h2', 'h3', 'h4', 'a'], class_=lambda x: 'title' in str(x).lower() if x else False)
            if not title_elem:
                title_elem = item.find(['h1', 'h2', 'h3', 'h4'])
            if not title_elem:
                title_elem = item.find('a')
            if not title_elem:
                return None

            title = title_elem.get_text(strip=True)

            # Filter for family-friendly content
            family_keywords = ['family', 'kid', 'child', 'free', 'community', 'festival',
                             'fair', 'market', 'celebration', 'music', 'art', 'craft']
            text_content = item.get_text().lower()
            if not any(keyword in text_content for keyword in family_keywords):
                return None

            # Extract link
            link_elem = item.find('a', href=True)
            url = link_elem['href'] if link_elem else bia['url']
            if url and not url.startswith('http'):
                # Get base URL from BIA url
                base = '/'.join(bia['url'].split('/')[:3])
                url = base + ('/' if not url.startswith('/') else '') + url

            # Extract description
            desc_elem = item.find(['p', 'div'], class_=lambda x: 'description' in str(x).lower() or 'excerpt' in str(x).lower() if x else False)
            if not desc_elem:
                desc_elem = item.find('p')

            description = desc_elem.get_text(strip=True)[:200] if desc_elem else title

            # Extract date
            date_text = item.get_text()
            event_date = self._extract_date(date_text)

            if not event_date:
                # Default to next Saturday
                today = datetime.now()
                days_to_sat = (5 - today.weekday()) % 7
                if days_to_sat == 0:
                    days_to_sat = 7
                event_date = (today + timedelta(days=days_to_sat)).strftime('%Y-%m-%d')

            # Determine if free
            is_free = 'free' in text_content.lower()

            # Create event
            event = {
                'title': title,
                'description': description,
                'category': 'Entertainment',
                'icon': '🎪',
                'date': event_date,
                'start_time': '10:00',
                'end_time': '17:00',
                'venue': {
                    'name': f"{bia['name']} BIA",
                    'address': f"{bia['name']}, Toronto",
                    'neighborhood': bia['name'],
                    'lat': bia['lat'],
                    'lng': bia['lng']
                },
                'age_groups': ['All Ages'],
                'indoor_outdoor': 'Outdoor',
                'organized_by': f"{bia['name']} BIA",
                'website': url,
                'source': 'BIA',
                'free': is_free
            }

            return event

        except Exception as e:
            return None

    def _extract_date(self, text: str) -> str:
        """Extract date from text"""

        today = datetime.now()

        # Month patterns
        patterns = [
            (r'(?:Jan|January)\s+(\d{1,2})', 1),
            (r'(?:Feb|February)\s+(\d{1,2})', 2),
            (r'(?:Mar|March)\s+(\d{1,2})', 3),
            (r'(?:Apr|April)\s+(\d{1,2})', 4),
            (r'(?:May)\s+(\d{1,2})', 5),
            (r'(?:Jun|June)\s+(\d{1,2})', 6),
            (r'(?:Jul|July)\s+(\d{1,2})', 7),
            (r'(?:Aug|August)\s+(\d{1,2})', 8),
            (r'(?:Sep|Sept|September)\s+(\d{1,2})', 9),
            (r'(?:Oct|October)\s+(\d{1,2})', 10),
            (r'(?:Nov|November)\s+(\d{1,2})', 11),
            (r'(?:Dec|December)\s+(\d{1,2})', 12),
        ]

        for pattern, month in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                day = int(match.group(1))
                year = today.year
                if month < today.month:
                    year += 1
                try:
                    date_obj = datetime(year, month, day)
                    return date_obj.strftime('%Y-%m-%d')
                except:
                    pass

        return None


if __name__ == "__main__":
    scraper = BIAScraper()
    events = scraper.fetch_events()
    print(f"\nTotal events: {len(events)}")
    if events:
        print("\nSample event:")
        import json
        print(json.dumps(events[0], indent=2))
