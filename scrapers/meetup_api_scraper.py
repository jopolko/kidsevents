#!/usr/bin/env python3
"""
Meetup API Scraper
Fetches kids/family events from Meetup using their public GraphQL API
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
import os

class MeetupAPIScraper:
    def __init__(self):
        self.api_url = "https://www.meetup.com/gql"
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Origin': 'https://www.meetup.com',
            'Referer': 'https://www.meetup.com/find/'
        }

    def fetch_events(self, days_ahead: int = 30) -> List[Dict]:
        """Fetch free family/kids events from Meetup in Toronto"""

        print("👥 Fetching from Meetup API...")

        # Search terms for kids events
        search_terms = [
            'kids Toronto',
            'family Toronto',
            'children Toronto',
            'toddlers Toronto',
            'parents Toronto'
        ]

        all_events = []

        for term in search_terms:
            try:
                events = self._search_events(term, days_ahead)
                all_events.extend(events)
                print(f"   Found {len(events)} events for '{term}'")
            except Exception as e:
                print(f"   ⚠️  Error searching '{term}': {e}")

        # Deduplicate by event URL
        seen = set()
        unique_events = []
        for event in all_events:
            url = event.get('website', '')
            if url and url not in seen:
                seen.add(url)
                unique_events.append(event)

        print(f"   ✅ Found {len(unique_events)} unique Meetup events")
        return unique_events

    def _search_events(self, search_term: str, days_ahead: int) -> List[Dict]:
        """Search for events using Meetup's search API"""

        # Use the simpler events endpoint
        url = f"https://www.meetup.com/find/events/?keywords={search_term.replace(' ', '+')}"

        try:
            # Try to get the page and parse events
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code != 200:
                return []

            # Meetup embeds event data in the page as JSON
            # Look for window.__INITIAL_STATE__
            import re
            match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', response.text)

            if not match:
                return []

            data = json.loads(match.group(1))

            # Parse the structure to find events
            events = self._parse_meetup_data(data, days_ahead)
            return events

        except Exception as e:
            return []

    def _parse_meetup_data(self, data: Dict, days_ahead: int) -> List[Dict]:
        """Parse Meetup page data to extract events"""
        events = []

        try:
            # Meetup's data structure varies, try common paths
            search_results = data.get('search', {}).get('results', [])

            today = datetime.now()
            end_date = today + timedelta(days=days_ahead)

            for result in search_results:
                try:
                    # Extract event data
                    event_data = result.get('event', {})
                    if not event_data:
                        continue

                    title = event_data.get('title', '')
                    if not title:
                        continue

                    # Parse date
                    date_time_str = event_data.get('dateTime', '')
                    if not date_time_str:
                        continue

                    event_dt = datetime.fromisoformat(date_time_str.replace('Z', '+00:00'))

                    # Filter by date
                    if event_dt < today or event_dt > end_date:
                        continue

                    # Get venue
                    venue = event_data.get('venue', {})
                    venue_name = venue.get('name', 'TBD')
                    address = venue.get('address', '')
                    lat = venue.get('lat', 43.6532)
                    lng = venue.get('lng', -79.3832)

                    # Only Toronto area
                    city = venue.get('city', '')
                    if 'toronto' not in city.lower():
                        continue

                    # Get description
                    description = event_data.get('description', '')

                    # Determine category and age groups
                    category, icon = self._determine_category(title, description)
                    age_groups = self._determine_age_groups(title, description)

                    # Get URL
                    event_url = event_data.get('eventUrl', '')

                    # Check if free
                    is_free = event_data.get('isFree', True)
                    if not is_free:
                        continue

                    event = {
                        "title": title,
                        "description": self._clean_description(description),
                        "category": category,
                        "icon": icon,
                        "date": event_dt.strftime('%Y-%m-%d'),
                        "start_time": event_dt.strftime('%H:%M'),
                        "end_time": (event_dt + timedelta(hours=2)).strftime('%H:%M'),
                        "venue": {
                            "name": venue_name,
                            "address": address,
                            "neighborhood": city,
                            "lat": lat,
                            "lng": lng
                        },
                        "age_groups": age_groups,
                        "indoor_outdoor": "Indoor",
                        "organized_by": event_data.get('group', {}).get('name', 'Meetup Group'),
                        "website": event_url,
                        "source": "Meetup",
                        "scraped_at": datetime.now().isoformat()
                    }

                    events.append(event)

                except Exception:
                    continue

        except Exception:
            pass

        return events

    def _determine_age_groups(self, title: str, description: str) -> List[str]:
        """Determine age groups"""
        text = (title + " " + description).lower()
        age_groups = []

        if any(word in text for word in ['baby', 'babies', 'infant']):
            age_groups.append("Babies (0-2)")
        if any(word in text for word in ['toddler', 'preschool']):
            age_groups.append("Toddlers (3-5)")
        if any(word in text for word in ['kids', 'children', 'elementary']):
            age_groups.append("Kids (6-12)")
        if any(word in text for word in ['teen', 'youth']):
            age_groups.append("Teens (13-17)")
        if any(word in text for word in ['family', 'all ages']):
            age_groups.append("All Ages")

        return age_groups if age_groups else ["All Ages"]

    def _determine_category(self, title: str, description: str) -> tuple:
        """Determine category and icon"""
        text = (title + " " + description).lower()

        if any(word in text for word in ['art', 'craft', 'creative']):
            return "Arts", "🎨"
        if any(word in text for word in ['music', 'sing', 'dance']):
            return "Entertainment", "🎵"
        if any(word in text for word in ['sport', 'play', 'active']):
            return "Sports", "⚽"
        if any(word in text for word in ['learn', 'education', 'stem']):
            return "Learning", "🔬"
        if any(word in text for word in ['nature', 'outdoor', 'park']):
            return "Nature", "🌳"

        return "Entertainment", "🎭"

    def _clean_description(self, description: str) -> str:
        """Clean description"""
        import re
        clean = re.sub('<[^<]+?>', '', description)
        clean = re.sub(r'\s+', ' ', clean)
        if len(clean) > 200:
            clean = clean[:197] + "..."
        return clean.strip()


def main():
    scraper = MeetupAPIScraper()
    events = scraper.fetch_events(days_ahead=30)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    with open('meetup_api_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to meetup_api_events.json")


if __name__ == "__main__":
    main()
