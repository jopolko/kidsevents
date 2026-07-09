#!/usr/bin/env python3
"""
Meetup.com Event Scraper
Fetches free kids/family events from Meetup
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
import os

class MeetupScraper:
    def __init__(self):
        # Meetup uses GraphQL API - no auth needed for public events
        self.api_url = "https://www.meetup.com/gql"
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch_events(self, days_ahead: int = 30) -> List[Dict]:
        """Fetch free family/kids events from Meetup in Toronto area"""

        print("🔍 Fetching events from Meetup...")

        # Calculate date range
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days_ahead)

        events = []

        # Query for kids and family related topics in Toronto
        topics = [
            'kids-activities',
            'family-fun',
            'children',
            'parents-and-kids',
            'toddlers',
            'preschool'
        ]

        for topic in topics:
            try:
                topic_events = self._fetch_by_topic(topic, start_date, end_date)
                events.extend(topic_events)
                print(f"   Found {len(topic_events)} events for '{topic}'")
            except Exception as e:
                print(f"   ⚠️  Error fetching '{topic}': {e}")
                continue

        # Remove duplicates
        seen_ids = set()
        unique_events = []
        for event in events:
            event_id = event.get('meetup_id')
            if event_id and event_id not in seen_ids:
                seen_ids.add(event_id)
                unique_events.append(event)

        print(f"✅ Found {len(unique_events)} unique Meetup events")
        return unique_events

    def _fetch_by_topic(self, topic: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Fetch events for a specific topic"""

        # GraphQL query to search events by topic
        query = """
        query($topicCategory: String!, $lat: Float!, $lon: Float!, $startDate: DateTime, $endDate: DateTime) {
          rankedEvents(input: {
            filter: {
              lat: $lat
              lon: $lon
              radius: 25
              topicCategory: $topicCategory
              startDateRange: $startDate
              endDateRange: $endDate
              isFree: true
            }
          }) {
            edges {
              node {
                id
                title
                description
                eventUrl
                dateTime
                endTime
                timezone
                venue {
                  name
                  address
                  city
                  lat
                  lng
                }
                group {
                  name
                }
              }
            }
          }
        }
        """

        variables = {
            "topicCategory": topic,
            "lat": 43.6532,  # Toronto downtown
            "lon": -79.3832,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat()
        }

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"query": query, "variables": variables},
                timeout=15
            )

            if response.status_code != 200:
                return []

            data = response.json()
            events = self._parse_meetup_response(data)
            return events

        except Exception as e:
            print(f"   Error querying Meetup API: {e}")
            return []

    def _parse_meetup_response(self, data: Dict) -> List[Dict]:
        """Parse Meetup API response into our event format"""
        events = []

        edges = data.get('data', {}).get('rankedEvents', {}).get('edges', [])

        for edge in edges:
            node = edge.get('node', {})

            if not node:
                continue

            # Parse datetime
            try:
                start = datetime.fromisoformat(node['dateTime'].replace('Z', '+00:00'))

                # End time may be null
                if node.get('endTime'):
                    end = datetime.fromisoformat(node['endTime'].replace('Z', '+00:00'))
                else:
                    end = start + timedelta(hours=2)  # Default 2 hour duration

            except Exception:
                continue

            # Get venue
            venue_data = node.get('venue', {})
            if not venue_data or venue_data.get('city', '').lower() != 'toronto':
                continue

            # Determine age groups and category
            title = node.get('title', '')
            description = node.get('description', '')

            age_groups = self._determine_age_groups(title, description)
            category, icon = self._determine_category(title, description)

            event = {
                "title": title,
                "description": self._clean_description(description),
                "category": category,
                "icon": icon,
                "date": start.strftime('%Y-%m-%d'),
                "start_time": start.strftime('%H:%M'),
                "end_time": end.strftime('%H:%M'),
                "venue": {
                    "name": venue_data.get('name', 'TBD'),
                    "address": venue_data.get('address', ''),
                    "neighborhood": venue_data.get('city', 'Toronto'),
                    "lat": float(venue_data.get('lat', 43.6532)),
                    "lng": float(venue_data.get('lng', -79.3832))
                },
                "age_groups": age_groups,
                "indoor_outdoor": "Indoor",  # Default
                "organized_by": node.get('group', {}).get('name', 'Community Event'),
                "website": node.get('eventUrl', ''),
                "source": "Meetup",
                "meetup_id": node.get('id'),
                "scraped_at": datetime.now().isoformat()
            }

            events.append(event)

        return events

    def _determine_age_groups(self, title: str, description: str) -> List[str]:
        """Determine age groups from event details"""
        text = (title + " " + description).lower()
        age_groups = []

        if any(word in text for word in ['baby', 'babies', 'infant', '0-2']):
            age_groups.append("Babies (0-2)")

        if any(word in text for word in ['toddler', 'preschool', '2-5', '3-5']):
            age_groups.append("Toddlers (3-5)")

        if any(word in text for word in ['kids', 'children', '6-12', 'elementary', 'school age']):
            age_groups.append("Kids (6-12)")

        if any(word in text for word in ['teen', 'youth', '13-17']):
            age_groups.append("Teens (13-17)")

        if any(word in text for word in ['family', 'all ages']):
            age_groups.append("All Ages")

        return age_groups if age_groups else ["All Ages"]

    def _determine_category(self, title: str, description: str) -> tuple:
        """Determine category and icon"""
        text = (title + " " + description).lower()

        if any(word in text for word in ['art', 'craft', 'paint', 'draw', 'creative']):
            return "Arts", "🎨"
        if any(word in text for word in ['music', 'concert', 'sing', 'dance']):
            return "Entertainment", "🎵"
        if any(word in text for word in ['sport', 'soccer', 'basketball', 'play', 'active']):
            return "Sports", "⚽"
        if any(word in text for word in ['science', 'stem', 'tech', 'learn', 'education']):
            return "Learning", "🔬"
        if any(word in text for word in ['story', 'book', 'read', 'library']):
            return "Learning", "📚"
        if any(word in text for word in ['nature', 'outdoor', 'park', 'hike']):
            return "Nature", "🌳"

        return "Entertainment", "🎭"

    def _clean_description(self, description: str) -> str:
        """Clean and truncate description"""
        import re
        # Remove HTML tags
        clean = re.sub('<[^<]+?>', '', description)
        # Remove excessive whitespace
        clean = re.sub(r'\s+', ' ', clean)
        # Truncate
        if len(clean) > 200:
            clean = clean[:197] + "..."
        return clean.strip()


def main():
    scraper = MeetupScraper()
    events = scraper.fetch_events(days_ahead=30)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    # Save to JSON
    with open('meetup_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to meetup_events.json")


if __name__ == "__main__":
    main()
