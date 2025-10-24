#!/usr/bin/env python3
"""
EventBrite API Fetcher
Fetches free kids/family events from EventBrite API
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
import os

class EventBriteFetcher:
    def __init__(self, api_token: str = None):
        self.api_token = api_token or os.getenv('EVENTBRITE_TOKEN')
        self.base_url = "https://www.eventbriteapi.com/v3"
        self.headers = {
            'Authorization': f'Bearer {self.api_token}' if self.api_token else ''
        }

    def fetch_events(self, days_ahead: int = 30) -> List[Dict]:
        """Fetch free events from EventBrite"""

        if not self.api_token:
            print("⚠️  No EventBrite API token found. Using sample data.")
            return self._get_sample_data()

        print("🔍 Fetching events from EventBrite...")

        # Calculate date range
        start_date = datetime.now().isoformat()
        end_date = (datetime.now() + timedelta(days=days_ahead)).isoformat()

        params = {
            'location.address': 'Toronto, ON, Canada',
            'location.within': '25km',
            'start_date.range_start': start_date,
            'start_date.range_end': end_date,
            'price': 'free',
            'categories': '103,105',  # Kids & Family categories
            'expand': 'venue,category',
            'page_size': 50
        }

        try:
            response = requests.get(
                f"{self.base_url}/events/search/",
                headers=self.headers,
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                events = self._parse_eventbrite_response(data)
                print(f"✅ Found {len(events)} EventBrite events")
                return events
            else:
                print(f"❌ EventBrite API error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching from EventBrite: {e}")
            return []

    def _parse_eventbrite_response(self, data: Dict) -> List[Dict]:
        """Parse EventBrite API response into our event format"""
        events = []

        for eb_event in data.get('events', []):
            # Skip if no venue or online-only
            if not eb_event.get('venue'):
                continue

            venue = eb_event['venue']

            # Skip if outside Toronto
            if not venue.get('address'):
                continue

            address = venue['address']
            if 'Toronto' not in address.get('city', ''):
                continue

            # Parse datetime
            start = datetime.fromisoformat(eb_event['start']['utc'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(eb_event['end']['utc'].replace('Z', '+00:00'))

            # Determine age groups and category
            name = eb_event['name']['text']
            description = eb_event.get('description', {}).get('text', '')

            age_groups = self._determine_age_groups(name, description)
            category, icon = self._determine_category(name, description)

            event = {
                "title": name,
                "description": self._clean_description(description),
                "category": category,
                "icon": icon,
                "date": start.strftime('%Y-%m-%d'),
                "start_time": start.strftime('%H:%M'),
                "end_time": end.strftime('%H:%M'),
                "venue": {
                    "name": venue.get('name', 'TBD'),
                    "address": address.get('address_1', ''),
                    "neighborhood": address.get('city', 'Toronto'),
                    "lat": float(venue.get('latitude', 43.6532)),
                    "lng": float(venue.get('longitude', -79.3832))
                },
                "age_groups": age_groups,
                "indoor_outdoor": "Indoor",  # Default, could be inferred
                "organized_by": "Community Event",
                "website": eb_event['url'],
                "source": "EventBrite",
                "eventbrite_id": eb_event['id'],
                "scraped_at": datetime.now().isoformat()
            }

            events.append(event)

        return events

    def _determine_age_groups(self, name: str, description: str) -> List[str]:
        """Determine age groups from event details"""
        text = (name + " " + description).lower()
        age_groups = []

        if any(word in text for word in ['baby', 'babies', 'infant']):
            age_groups.append("Babies (0-2)")

        if any(word in text for word in ['toddler', 'preschool', '2-5', '3-5']):
            age_groups.append("Toddlers (3-5)")

        if any(word in text for word in ['kids', 'children', '6-12', 'elementary']):
            age_groups.append("Kids (6-12)")

        if any(word in text for word in ['family', 'all ages']):
            age_groups.append("All Ages")

        return age_groups if age_groups else ["All Ages"]

    def _determine_category(self, name: str, description: str) -> tuple:
        """Determine category and icon"""
        text = (name + " " + description).lower()

        if any(word in text for word in ['art', 'craft', 'paint', 'draw']):
            return "Arts", "🎨"
        if any(word in text for word in ['music', 'concert', 'sing']):
            return "Entertainment", "🎵"
        if any(word in text for word in ['sport', 'soccer', 'basketball']):
            return "Sports", "⚽"
        if any(word in text for word in ['science', 'stem', 'tech']):
            return "Learning", "🔬"
        if any(word in text for word in ['story', 'book', 'read']):
            return "Learning", "📚"
        if any(word in text for word in ['nature', 'outdoor', 'park']):
            return "Nature", "🌳"

        return "Entertainment", "🎭"

    def _clean_description(self, description: str) -> str:
        """Clean and truncate description"""
        # Remove HTML tags
        import re
        clean = re.sub('<[^<]+?>', '', description)
        # Truncate to reasonable length
        if len(clean) > 200:
            clean = clean[:197] + "..."
        return clean.strip()

    def _get_sample_data(self) -> List[Dict]:
        """Return sample EventBrite events for testing"""
        return [
            {
                "title": "Kids Art Workshop",
                "description": "Creative art workshop for children ages 6-12.",
                "category": "Arts",
                "icon": "🎨",
                "date": "2025-10-25",
                "start_time": "14:00",
                "end_time": "16:00",
                "venue": {
                    "name": "Community Arts Centre",
                    "address": "123 Queen Street West",
                    "neighborhood": "Downtown",
                    "lat": 43.6532,
                    "lng": -79.3832
                },
                "age_groups": ["Kids (6-12)"],
                "indoor_outdoor": "Indoor",
                "organized_by": "Community Event",
                "website": "https://www.eventbrite.ca/",
                "source": "EventBrite",
                "scraped_at": datetime.now().isoformat()
            }
        ]

    def save_to_json(self, events: List[Dict], filename: str = "eventbrite_events.json"):
        """Save events to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved to {filename}")


def main():
    # Get token from environment or use None for sample data
    token = os.getenv('EVENTBRITE_TOKEN')

    if not token:
        print("ℹ️  To use live data, set EVENTBRITE_TOKEN environment variable")
        print("   Get your token at: https://www.eventbrite.com/platform/api")
        print()

    fetcher = EventBriteFetcher(token)
    events = fetcher.fetch_events(days_ahead=30)
    fetcher.save_to_json(events)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")


if __name__ == "__main__":
    main()
