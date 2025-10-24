#!/usr/bin/env python3
"""
Today's Parent Toronto Events Scraper
Fetches kids/family events from Today's Parent Toronto section
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import re
import time

class TodaysParentScraper:
    def __init__(self):
        self.base_url = "https://www.todaysparent.com"
        self.toronto_section = f"{self.base_url}/family/activities/toronto-kids-events"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def fetch_events(self, days_ahead: int = 30) -> List[Dict]:
        """Fetch kids/family events from Today's Parent"""

        print("👨‍👩‍👧‍👦 Fetching from Today's Parent Toronto...")

        try:
            time.sleep(1)  # Be polite

            response = requests.get(self.toronto_section, headers=self.headers, timeout=15)

            if response.status_code != 200:
                print(f"   ⚠️  HTTP {response.status_code}")
                return []

            soup = BeautifulSoup(response.content, 'html.parser')
            events = []

            # Find articles/event listings
            articles = soup.find_all(['article', 'div'], class_=lambda x: x and ('post' in str(x).lower() or 'event' in str(x).lower() or 'article' in str(x).lower()))

            for article in articles[:20]:  # Limit to first 20
                parsed = self._parse_article(article)
                if parsed:
                    events.append(parsed)

            if events:
                print(f"   ✅ Found {len(events)} events from Today's Parent")
            else:
                print(f"   ⚠️  No events found")

            return events

        except Exception as e:
            print(f"   ❌ Error fetching Today's Parent events: {e}")
            return []

    def _parse_article(self, article) -> Dict:
        """Parse an individual article/event"""

        try:
            # Extract title
            title_elem = article.find(['h1', 'h2', 'h3', 'h4'])
            if not title_elem:
                title_elem = article.find('a')
            if not title_elem:
                return None

            title = title_elem.get_text(strip=True)

            # Skip if title is too short or generic
            if len(title) < 10:
                return None

            # Extract link
            link_elem = article.find('a', href=True)
            if not link_elem:
                return None

            url = link_elem['href']
            if not url.startswith('http'):
                url = self.base_url + url

            # Extract description
            desc_elem = article.find(['p', 'div'], class_=lambda x: 'excerpt' in str(x).lower() or 'description' in str(x).lower() if x else False)
            if not desc_elem:
                desc_elem = article.find('p')

            description = desc_elem.get_text(strip=True)[:200] if desc_elem else title

            # Extract date
            date_text = article.get_text()
            event_date = self._extract_date(date_text)

            if not event_date:
                # Default to next week if no date found
                event_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

            # Determine age group from content
            age_groups = self._determine_age_groups(title + ' ' + description)

            # Create event
            event = {
                'title': title,
                'description': description,
                'category': self._categorize(title + ' ' + description),
                'icon': self._get_icon(title + ' ' + description),
                'date': event_date,
                'start_time': '10:00',
                'end_time': '16:00',
                'venue': {
                    'name': 'Various Toronto Locations',
                    'address': 'Toronto, ON',
                    'neighborhood': 'Toronto',
                    'lat': 43.6532,
                    'lng': -79.3832
                },
                'age_groups': age_groups,
                'indoor_outdoor': 'Both',
                'organized_by': "Today's Parent Featured",
                'website': url,
                'source': 'TodaysParent'
            }

            return event

        except Exception as e:
            return None

    def _extract_date(self, text: str) -> str:
        """Extract date from text"""

        today = datetime.now()

        # Look for month patterns
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

    def _determine_age_groups(self, text: str) -> List[str]:
        """Determine age groups from text"""

        text_lower = text.lower()
        age_groups = []

        if any(word in text_lower for word in ['baby', 'babies', 'infant', '0-2', 'newborn']):
            age_groups.append('Babies (0-2)')
        if any(word in text_lower for word in ['toddler', '3-5', 'preschool', 'pre-k']):
            age_groups.append('Toddlers (3-5)')
        if any(word in text_lower for word in ['kid', 'child', '6-12', 'elementary', 'school-age']):
            age_groups.append('Kids (6-12)')
        if any(word in text_lower for word in ['teen', 'youth', '13+']):
            age_groups.append('Teens (13+)')

        # Default to all ages if nothing specific found
        if not age_groups:
            age_groups = ['All Ages']

        return age_groups

    def _categorize(self, text: str) -> str:
        """Categorize event"""

        text_lower = text.lower()

        if any(word in text_lower for word in ['music', 'concert', 'dance']):
            return 'Arts'
        elif any(word in text_lower for word in ['park', 'outdoor', 'nature']):
            return 'Nature'
        elif any(word in text_lower for word in ['museum', 'science', 'learn', 'educational']):
            return 'Learning'
        elif any(word in text_lower for word in ['sport', 'swim', 'hockey', 'soccer']):
            return 'Sports'
        elif any(word in text_lower for word in ['festival', 'fair', 'celebration']):
            return 'Entertainment'
        else:
            return 'Entertainment'

    def _get_icon(self, text: str) -> str:
        """Get icon based on content"""

        text_lower = text.lower()

        if any(word in text_lower for word in ['music', 'concert']):
            return '🎵'
        elif any(word in text_lower for word in ['art', 'craft', 'paint']):
            return '🎨'
        elif any(word in text_lower for word in ['park', 'outdoor', 'nature']):
            return '🌳'
        elif any(word in text_lower for word in ['museum', 'science']):
            return '🔬'
        elif any(word in text_lower for word in ['sport', 'hockey', 'soccer']):
            return '⚽'
        elif any(word in text_lower for word in ['festival', 'celebration']):
            return '🎪'
        else:
            return '🎉'


if __name__ == "__main__":
    scraper = TodaysParentScraper()
    events = scraper.fetch_events()
    print(f"\nTotal events: {len(events)}")
    if events:
        print("\nSample event:")
        import json
        print(json.dumps(events[0], indent=2))
