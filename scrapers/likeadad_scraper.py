#!/usr/bin/env python3
"""
Like A Dad GTA Events Scraper
Fetches kids/family events from Like A Dad blog (GTA dad blogger)
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import re
import time

class LikeADadScraper:
    def __init__(self):
        self.base_url = "https://likeadad.net"
        # Changed from /category/toronto-life/ to /category/toronto/
        self.events_section = f"{self.base_url}/category/toronto/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://likeadad.net/'
        }

    def fetch_events(self, days_ahead: int = 30) -> List[Dict]:
        """Fetch kids/family events from Like A Dad blog"""

        print("👨‍👧 Fetching from Like A Dad GTA Events...")

        try:
            time.sleep(1)  # Be polite

            response = requests.get(self.events_section, headers=self.headers, timeout=15)

            if response.status_code != 200:
                print(f"   ⚠️  HTTP {response.status_code}")
                return []

            soup = BeautifulSoup(response.content, 'html.parser')
            events = []

            # Find blog posts about events
            articles = soup.find_all(['article', 'div'], class_=lambda x: x and ('post' in str(x).lower() or 'article' in str(x).lower()))

            for article in articles[:15]:  # Limit to first 15
                parsed = self._parse_article(article)
                if parsed:
                    events.append(parsed)

            if events:
                print(f"   ✅ Found {len(events)} events from Like A Dad")
            else:
                print(f"   ⚠️  No events found")

            return events

        except Exception as e:
            print(f"   ❌ Error fetching Like A Dad events: {e}")
            return []

    def _parse_article(self, article) -> Dict:
        """Parse an individual article/event"""

        try:
            # Extract title (LikeADad uses h4 for entry-title)
            title_elem = article.find(['h1', 'h2', 'h3', 'h4', 'h5'])
            if not title_elem:
                return None

            title = title_elem.get_text(strip=True)

            # Filter for event-related content (broadened to catch more relevant posts)
            event_keywords = ['event', 'festival', 'fair', 'free', 'family', 'kid', 'children',
                            'activities', 'things to do', 'weekend', 'camp', 'fun', 'toronto']
            if not any(keyword in title.lower() for keyword in event_keywords):
                return None

            # Extract link
            link_elem = article.find('a', href=True)
            if not link_elem:
                return None

            url = link_elem['href']
            if not url.startswith('http'):
                url = self.base_url + url

            # Extract description/excerpt
            desc_elem = article.find(['p', 'div'], class_=lambda x: 'excerpt' in str(x).lower() or 'summary' in str(x).lower() if x else False)
            if not desc_elem:
                desc_elem = article.find('p')

            description = desc_elem.get_text(strip=True)[:200] if desc_elem else title

            # Extract date from text
            date_text = article.get_text()
            event_date = self._extract_date(date_text, title)

            if not event_date:
                # Default to this weekend
                today = datetime.now()
                days_to_saturday = (5 - today.weekday()) % 7
                if days_to_saturday == 0:
                    days_to_saturday = 7
                event_date = (today + timedelta(days=days_to_saturday)).strftime('%Y-%m-%d')

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
                    'name': 'GTA Location',
                    'address': 'Greater Toronto Area',
                    'neighborhood': 'GTA',
                    'lat': 43.6532,
                    'lng': -79.3832
                },
                'age_groups': ['All Ages'],
                'indoor_outdoor': 'Both',
                'organized_by': 'Like A Dad Featured',
                'website': url,
                'source': 'LikeADad'
            }

            return event

        except Exception as e:
            return None

    def _extract_date(self, text: str, title: str) -> str:
        """Extract date from text"""

        combined_text = text + ' ' + title
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
            match = re.search(pattern, combined_text, re.IGNORECASE)
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

        # Look for "this weekend", "next weekend"
        if 'this weekend' in combined_text.lower():
            days_to_sat = (5 - today.weekday()) % 7
            if days_to_sat == 0:
                days_to_sat = 7
            return (today + timedelta(days=days_to_sat)).strftime('%Y-%m-%d')

        if 'next weekend' in combined_text.lower():
            days_to_sat = ((5 - today.weekday()) % 7) + 7
            return (today + timedelta(days=days_to_sat)).strftime('%Y-%m-%d')

        return None

    def _categorize(self, text: str) -> str:
        """Categorize event"""

        text_lower = text.lower()

        if any(word in text_lower for word in ['music', 'concert', 'show']):
            return 'Arts'
        elif any(word in text_lower for word in ['park', 'outdoor', 'nature', 'playground']):
            return 'Nature'
        elif any(word in text_lower for word in ['museum', 'science', 'learn']):
            return 'Learning'
        elif any(word in text_lower for word in ['sport', 'game', 'play']):
            return 'Sports'
        elif any(word in text_lower for word in ['festival', 'fair', 'carnival']):
            return 'Entertainment'
        else:
            return 'Entertainment'

    def _get_icon(self, text: str) -> str:
        """Get icon based on content"""

        text_lower = text.lower()

        if any(word in text_lower for word in ['music', 'concert']):
            return '🎵'
        elif any(word in text_lower for word in ['art', 'craft']):
            return '🎨'
        elif any(word in text_lower for word in ['park', 'outdoor', 'nature']):
            return '🌳'
        elif any(word in text_lower for word in ['museum', 'science']):
            return '🔬'
        elif any(word in text_lower for word in ['sport', 'game']):
            return '⚽'
        elif any(word in text_lower for word in ['festival', 'fair']):
            return '🎪'
        else:
            return '🎉'


if __name__ == "__main__":
    scraper = LikeADadScraper()
    events = scraper.fetch_events()
    print(f"\nTotal events: {len(events)}")
    if events:
        print("\nSample event:")
        import json
        print(json.dumps(events[0], indent=2))
