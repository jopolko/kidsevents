#!/usr/bin/env python3
"""
To Do Canada Events Scraper
Scrapes family events from todocanada.ca
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
from bs4 import BeautifulSoup
import re


class ToDoCanadaScraper:
    def __init__(self):
        self.base_url = "https://www.todocanada.ca/things-to-do-in-toronto-kids-this-weekend/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def fetch_events(self, days_ahead: int = 14) -> List[Dict]:
        """Fetch family events from To Do Canada"""

        print("🎪 Fetching from To Do Canada...")

        try:
            response = requests.get(
                self.base_url,
                headers=self.headers,
                timeout=15
            )

            if response.status_code != 200:
                print(f"   ❌ To Do Canada error: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            events = []
            today = datetime.now().date()
            end_date = today + timedelta(days=days_ahead)

            # Find article content
            article_content = soup.find('div', class_='entry-content')
            if not article_content:
                print("   ❌ Could not find article content")
                return []

            # Look for event headings and details
            headings = article_content.find_all(['h2', 'h3'])

            for heading in headings:
                try:
                    event = self._parse_event_section(heading, today, end_date)
                    if event:
                        events.append(event)
                except Exception as e:
                    continue

            print(f"   ✅ Found {len(events)} To Do Canada events")
            return events

        except Exception as e:
            print(f"   ❌ Error fetching To Do Canada events: {e}")
            return []

    def _parse_event_section(self, heading, today, end_date) -> Dict:
        """Parse an event section"""

        title = heading.get_text(strip=True)

        # Skip non-event headings
        if not title or len(title) < 10:
            return None

        # Get following paragraphs for description
        description = ""
        next_elem = heading.find_next_sibling()
        while next_elem and next_elem.name in ['p', 'ul']:
            description += next_elem.get_text(strip=True) + " "
            next_elem = next_elem.find_next_sibling()
            if len(description) > 500:
                break

        description = description[:300]

        # Try to extract dates from title or description
        event_date = self._extract_date(title + " " + description, today, end_date)
        if not event_date:
            # Default to this weekend
            days_until_saturday = (5 - today.weekday()) % 7
            event_date = today + timedelta(days=days_until_saturday)

        # Extract location
        location = self._extract_location(title + " " + description)

        # Determine if free
        is_free = 'free' in (title + description).lower()

        # Categorize
        category, icon = self._categorize_event(title + " " + description)

        return {
            "title": title,
            "description": description.strip(),
            "category": category,
            "icon": icon,
            "date": event_date.strftime('%Y-%m-%d'),
            "start_time": "10:00",
            "end_time": "17:00",
            "venue": {
                "name": location,
                "address": "",
                "neighborhood": "Toronto",
                "lat": 43.6532,
                "lng": -79.3832
            },
            "age_groups": ["All Ages"],
            "indoor_outdoor": "Indoor",
            "organized_by": "Community Event",
            "website": self.base_url,
            "source": "ToDoCanada",
            "is_free": is_free
        }

    def _extract_date(self, text: str, today, end_date):
        """Try to extract date from text"""

        # Look for date patterns
        date_patterns = [
            r'(?:October|November|December|January|February)\s+\d{1,2}',
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'(?:this|next)\s+(?:weekend|Saturday|Sunday)'
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group()

                # Parse "this weekend" or "next weekend"
                if 'weekend' in date_str.lower():
                    days_until_saturday = (5 - today.weekday()) % 7
                    if days_until_saturday == 0:
                        days_until_saturday = 7
                    if 'next' in date_str.lower():
                        days_until_saturday += 7
                    return today + timedelta(days=days_until_saturday)

        return None

    def _extract_location(self, text: str) -> str:
        """Extract location from text"""

        # Common Toronto venues
        venues = [
            "Harbourfront Centre", "Ontario Science Centre", "ROM",
            "Royal Ontario Museum", "AGO", "Art Gallery of Ontario",
            "Toronto Zoo", "Ripley's Aquarium", "Casa Loma",
            "Evergreen Brick Works", "High Park", "Toronto Island"
        ]

        for venue in venues:
            if venue.lower() in text.lower():
                return venue

        return "Toronto"

    def _categorize_event(self, text: str) -> tuple:
        """Categorize event and assign icon"""

        text = text.lower()

        if any(word in text for word in ['craft', 'art', 'paint', 'draw', 'create']):
            return "Arts", "🎨"
        if any(word in text for word in ['music', 'concert', 'sing', 'dance', 'performance']):
            return "Entertainment", "🎵"
        if any(word in text for word in ['sport', 'skate', 'swim', 'play']):
            return "Sports", "⚽"
        if any(word in text for word in ['workshop', 'learn', 'science', 'story']):
            return "Learning", "📚"
        if any(word in text for word in ['festival', 'fair', 'carnival']):
            return "Entertainment", "🎪"

        return "Entertainment", "🎉"


def main():
    scraper = ToDoCanadaScraper()
    events = scraper.fetch_events(days_ahead=14)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    if events:
        print(f"\n   Sample events:")
        for event in events[:3]:
            print(f"   {event['icon']} {event['title']}")

    # Save to JSON
    with open('todocanada_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved to todocanada_events.json")


if __name__ == "__main__":
    main()
