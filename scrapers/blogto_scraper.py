#!/usr/bin/env python3
"""
BlogTO Kids Events Scraper
Fetches kids/family events from BlogTO Toronto
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import re
import time

class BlogTOScraper:
    def __init__(self):
        self.base_url = "https://www.blogto.com"
        self.kids_section = f"{self.base_url}/kids/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def fetch_events(self, days_ahead: int = 30) -> List[Dict]:
        """Fetch kids/family events from BlogTO"""

        print("📰 Fetching from BlogTO Kids...")

        try:
            time.sleep(1)  # Be polite

            response = requests.get(self.kids_section, headers=self.headers, timeout=15)

            if response.status_code != 200:
                print(f"   ⚠️  HTTP {response.status_code}")
                return []

            soup = BeautifulSoup(response.content, 'html.parser')
            events = []

            # BlogTO uses article cards for events
            articles = soup.find_all('article', class_=lambda x: x and 'article' in str(x).lower())

            if not articles:
                # Fallback: find divs with event-like classes
                articles = soup.find_all(['div', 'article'], class_=lambda x: x and ('post' in str(x).lower() or 'card' in str(x).lower()))

            for article in articles[:20]:  # Limit to first 20
                parsed = self._parse_article(article)
                if parsed:
                    events.append(parsed)

            if events:
                print(f"   ✅ Found {len(events)} events from BlogTO")
            else:
                print(f"   ⚠️  No events found")

            return events

        except Exception as e:
            print(f"   ❌ Error fetching BlogTO events: {e}")
            return []

    def _parse_article(self, article) -> Dict:
        """Parse an individual article/event"""

        try:
            # Extract title
            title_elem = article.find(['h2', 'h3', 'a'], class_=lambda x: 'title' in str(x).lower() if x else False)
            if not title_elem:
                title_elem = article.find(['h2', 'h3'])
            if not title_elem:
                return None

            title = title_elem.get_text(strip=True)

            # Filter for kids-related content
            kids_keywords = ['kid', 'child', 'family', 'toddler', 'baby', 'teen', 'youth',
                           'playground', 'park', 'free', 'festival', 'event']
            if not any(keyword in title.lower() for keyword in kids_keywords):
                return None

            # Extract link
            link_elem = article.find('a', href=True)
            if not link_elem:
                return None

            url = link_elem['href']
            if not url.startswith('http'):
                url = self.base_url + url

            # Extract date from text if available
            date_text = article.get_text()
            event_date = self._extract_date(date_text)

            if not event_date:
                # Default to tomorrow if no date found
                event_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

            # Extract description/excerpt
            desc_elem = article.find(['p', 'div'], class_=lambda x: 'excerpt' in str(x).lower() if x else False)
            description = desc_elem.get_text(strip=True)[:200] if desc_elem else title

            # Create event
            event = {
                'title': title,
                'description': description,
                'category': self._categorize(title + ' ' + description),
                'icon': self._get_icon(title + ' ' + description),
                'date': event_date,
                'start_time': '10:00',  # Default time
                'end_time': '17:00',
                'venue': {
                    'name': 'Various Toronto Locations',
                    'address': 'Toronto, ON',
                    'neighborhood': 'Toronto',
                    'lat': 43.6532,
                    'lng': -79.3832
                },
                'age_groups': ['All Ages'],
                'indoor_outdoor': 'Both',
                'organized_by': 'BlogTO Featured',
                'website': url,
                'source': 'BlogTO'
            }

            return event

        except Exception as e:
            return None

    def _extract_date(self, text: str) -> str:
        """Extract date from text"""

        today = datetime.now()

        # Look for common date patterns
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
                # If month has passed, use next year
                if month < today.month:
                    year += 1
                try:
                    date_obj = datetime(year, month, day)
                    return date_obj.strftime('%Y-%m-%d')
                except:
                    pass

        # Look for "this weekend", "next week", etc.
        if 'this weekend' in text.lower() or 'saturday' in text.lower():
            # Find next Saturday
            days_ahead = (5 - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            date_obj = today + timedelta(days=days_ahead)
            return date_obj.strftime('%Y-%m-%d')

        return None

    def _categorize(self, text: str) -> str:
        """Categorize event based on content"""

        text_lower = text.lower()

        if any(word in text_lower for word in ['music', 'concert', 'dance', 'perform']):
            return 'Arts'
        elif any(word in text_lower for word in ['park', 'outdoor', 'nature', 'garden']):
            return 'Nature'
        elif any(word in text_lower for word in ['museum', 'gallery', 'exhibit']):
            return 'Learning'
        elif any(word in text_lower for word in ['sport', 'swim', 'skate', 'play']):
            return 'Sports'
        elif any(word in text_lower for word in ['festival', 'fair', 'market']):
            return 'Entertainment'
        else:
            return 'Entertainment'

    def _get_icon(self, text: str) -> str:
        """Get icon based on content"""

        text_lower = text.lower()

        if any(word in text_lower for word in ['music', 'concert']):
            return '🎵'
        elif any(word in text_lower for word in ['art', 'paint', 'craft']):
            return '🎨'
        elif any(word in text_lower for word in ['park', 'outdoor', 'nature']):
            return '🌳'
        elif any(word in text_lower for word in ['museum', 'gallery']):
            return '🏛️'
        elif any(word in text_lower for word in ['sport', 'swim', 'skate']):
            return '⚽'
        elif any(word in text_lower for word in ['festival', 'fair']):
            return '🎪'
        elif any(word in text_lower for word in ['food', 'market']):
            return '🍕'
        else:
            return '🎉'


if __name__ == "__main__":
    scraper = BlogTOScraper()
    events = scraper.fetch_events()
    print(f"\nTotal events: {len(events)}")
    if events:
        print("\nSample event:")
        import json
        print(json.dumps(events[0], indent=2))
