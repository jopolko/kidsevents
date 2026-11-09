#!/usr/bin/env python3
"""
Family Fun Canada Events Scraper
Scrapes family events from familyfuncanada.com
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
from bs4 import BeautifulSoup


class FamilyFunScraper:
    def __init__(self):
        self.base_url = "https://www.familyfuncanada.com/toronto/weekend-guide/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def fetch_events(self, days_ahead: int = 14) -> List[Dict]:
        """Fetch family events from Family Fun Canada"""

        print("👨‍👩‍👧‍👦 Fetching from Family Fun Canada...")

        try:
            response = requests.get(
                self.base_url,
                headers=self.headers,
                timeout=15
            )

            if response.status_code != 200:
                print(f"   ❌ Family Fun Canada error: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            events = []
            today = datetime.now().date()
            end_date = today + timedelta(days=days_ahead)

            # Find article content
            article = soup.find('article')
            if not article:
                print("   ❌ Could not find article content")
                return []

            # Look for event headings
            headings = article.find_all(['h2', 'h3', 'h4'])

            for heading in headings:
                try:
                    event = self._parse_event(heading, today, end_date)
                    if event:
                        events.append(event)
                except:
                    continue

            print(f"   ✅ Found {len(events)} Family Fun Canada events")
            return events

        except Exception as e:
            print(f"   ❌ Error fetching Family Fun Canada events: {e}")
            return []

    def _parse_event(self, heading, today, end_date) -> Dict:
        """Parse event from heading"""

        title = heading.get_text(strip=True)

        if not title or len(title) < 10:
            return None

        # Skip non-event headings (page elements, navigation, etc)
        skip_keywords = ['newsletter', 'sign-up', 'subscribe', 'event guide', 'weekend guide',
                        'about us', 'contact', 'related posts', 'share this', 'follow us']
        if any(keyword in title.lower() for keyword in skip_keywords):
            return None

        # Only real dated events: the guide also lists roundup articles, adult shows, campers-only
        # weekends and places outside the GTA. Roundups have no date in the heading.
        low = title.lower()
        if any(k in low for k in ('guide to', 'things to do', 'bucket list', 'freebies', "don't miss", 'don’t miss',
                                  'camper', 'bala ', 'miniature', 'fall for dance', 'dog-friendly')):
            return None
        import re as _re
        if not _re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d', low):
            return None

        # Get description from following paragraphs
        description = ""
        next_elem = heading.find_next_sibling()
        count = 0
        while next_elem and next_elem.name == 'p' and count < 3:
            description += next_elem.get_text(strip=True) + " "
            next_elem = next_elem.find_next_sibling()
            count += 1

        # Keep full description - no truncation

        # Default to this weekend
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0:
            days_until_saturday = 7
        event_date = today + timedelta(days=days_until_saturday)

        # Check if free
        is_free = 'free' in (title + description).lower()

        # Categorize
        category, icon = self._categorize(title + " " + description)

        return {
            "title": title,
            "description": description.strip() or "Family-friendly weekend activity",
            "category": category,
            "icon": icon,
            "date": event_date.strftime('%Y-%m-%d'),
            "start_time": "10:00",
            "end_time": "17:00",
            "venue": {
                "name": "Various Locations",
                "address": "Toronto, ON",
                "neighborhood": "Toronto",
                "lat": 43.6532,
                "lng": -79.3832
            },
            "age_groups": ["All Ages"],
            "indoor_outdoor": "Indoor",
            "organized_by": "Community Event",
            "website": self.base_url,
            "source": "FamilyFun",
            "is_free": is_free
        }

    def _categorize(self, text: str) -> tuple:
        """Categorize event"""

        text = text.lower()

        if any(word in text for word in ['art', 'craft', 'paint', 'maker']):
            return "Arts", "🎨"
        if any(word in text for word in ['music', 'concert', 'show', 'theatre']):
            return "Entertainment", "🎭"
        if any(word in text for word in ['sport', 'game', 'play']):
            return "Sports", "⚽"
        if any(word in text for word in ['nature', 'outdoor', 'hike', 'park']):
            return "Nature", "🌳"
        if any(word in text for word in ['festival', 'fair']):
            return "Entertainment", "🎪"

        return "Entertainment", "🎉"


def main():
    scraper = FamilyFunScraper()
    events = scraper.fetch_events(days_ahead=14)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    if events:
        print(f"\n   Sample events:")
        for event in events[:3]:
            print(f"   {event['icon']} {event['title']}")

    # Save to JSON
    with open('familyfun_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved to familyfun_events.json")


if __name__ == "__main__":
    main()
