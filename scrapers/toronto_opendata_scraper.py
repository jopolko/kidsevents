#!/usr/bin/env python3
"""
Toronto Open Data Scraper
Fetches festivals and events from City of Toronto Open Data Portal
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict

class TorontoOpenDataScraper:
    def __init__(self):
        # Toronto Open Data - Festivals & Events dataset
        self.api_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/datastore_search"
        self.resource_id = "7f01bd44-b9c2-4c0b-8c8c-d9f39fcee6e0"  # Festivals & Events

    def fetch_events(self, days_ahead: int = 30) -> List[Dict]:
        """Fetch events from Toronto Open Data"""

        print("🏛️  Fetching from Toronto Open Data...")

        try:
            # Calculate date range
            today = datetime.now()
            end_date = today + timedelta(days=days_ahead)

            params = {
                'resource_id': self.resource_id,
                'limit': 500
            }

            response = requests.get(self.api_url, params=params, timeout=15)

            if response.status_code != 200:
                print(f"   ❌ API error: {response.status_code}")
                return []

            data = response.json()
            events = self._parse_events(data, today, end_date)
            print(f"   ✅ Found {len(events)} Toronto Open Data events")
            return events

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []

    def _parse_events(self, data: Dict, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Parse Open Data response into our event format"""
        events = []

        records = data.get('result', {}).get('records', [])

        for record in records:
            try:
                # Parse event dates
                event_start_str = record.get('startDate', '')
                event_end_str = record.get('endDate', '')

                if not event_start_str:
                    continue

                # Parse date (format: YYYY-MM-DD or datetime string)
                event_start = self._parse_date(event_start_str)
                if not event_start:
                    continue

                # Filter by date range
                if event_start.date() < start_date.date() or event_start.date() > end_date.date():
                    continue

                # Get event details
                title = record.get('eventName', '').strip()
                if not title:
                    continue

                # Check if kid-friendly
                description = record.get('description', '')
                category_str = record.get('category', '').lower()

                if not self._is_kids_relevant(title, description, category_str):
                    continue

                # Parse location
                venue_name = record.get('locationName', 'TBD')
                address = record.get('locationAddress', '')

                # Get coordinates if available
                lat = 43.6532
                lng = -79.3832
                if record.get('latitude') and record.get('longitude'):
                    try:
                        lat = float(record.get('latitude'))
                        lng = float(record.get('longitude'))
                    except:
                        pass

                # Determine category and age groups
                category, icon = self._determine_category(title, description, category_str)
                age_groups = self._determine_age_groups(title, description)

                # Parse time
                start_time = "10:00"
                end_time = "17:00"

                # Try to extract time from description or use event dates
                if 'time' in description.lower():
                    # Simple time extraction
                    import re
                    time_match = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)?', description.lower())
                    if time_match:
                        hour = int(time_match.group(1))
                        minute = time_match.group(2)
                        ampm = time_match.group(3)
                        if ampm == 'pm' and hour < 12:
                            hour += 12
                        start_time = f"{hour:02d}:{minute}"
                        end_time = f"{hour+2:02d}:{minute}"

                # Check if free
                cost = record.get('cost', '').lower()
                if cost and cost not in ['free', 'no cost', '$0', '0', 'no charge']:
                    continue

                event = {
                    "title": title,
                    "description": description[:200] + "..." if len(description) > 200 else description,
                    "category": category,
                    "icon": icon,
                    "date": event_start.strftime('%Y-%m-%d'),
                    "start_time": start_time,
                    "end_time": end_time,
                    "venue": {
                        "name": venue_name,
                        "address": address,
                        "neighborhood": record.get('locationCity', 'Toronto'),
                        "lat": lat,
                        "lng": lng
                    },
                    "age_groups": age_groups,
                    "indoor_outdoor": "Outdoor" if 'outdoor' in description.lower() or 'park' in venue_name.lower() else "Indoor",
                    "organized_by": record.get('orgName', 'City of Toronto'),
                    "website": record.get('websiteUrl', ''),
                    "source": "TorontoOpenData",
                    "scraped_at": datetime.now().isoformat()
                }

                events.append(event)

            except Exception as e:
                continue

        return events

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string into datetime"""
        try:
            # Try YYYY-MM-DD format
            if 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            return None

    def _is_kids_relevant(self, title: str, description: str, category: str) -> bool:
        """Check if event is relevant to kids/families"""
        text = (title + " " + description + " " + category).lower()

        kids_keywords = [
            'kid', 'kids', 'child', 'children', 'family', 'families',
            'baby', 'babies', 'infant', 'toddler', 'youth', 'teen',
            'playground', 'carnival', 'fair', 'festival',
            'all ages', 'everyone', 'community'
        ]

        return any(keyword in text for keyword in kids_keywords)

    def _determine_age_groups(self, title: str, description: str) -> List[str]:
        """Determine age groups from event details"""
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
        if any(word in text for word in ['family', 'all ages', 'everyone']):
            age_groups.append("All Ages")

        return age_groups if age_groups else ["All Ages"]

    def _determine_category(self, title: str, description: str, category: str) -> tuple:
        """Determine category and icon"""
        text = (title + " " + description + " " + category).lower()

        if any(word in text for word in ['art', 'craft', 'paint', 'exhibit']):
            return "Arts", "🎨"
        if any(word in text for word in ['music', 'concert', 'dance', 'performance']):
            return "Entertainment", "🎵"
        if any(word in text for word in ['sport', 'game', 'active', 'play']):
            return "Sports", "⚽"
        if any(word in text for word in ['festival', 'fair', 'carnival', 'celebration']):
            return "Entertainment", "🎉"
        if any(word in text for word in ['nature', 'park', 'outdoor', 'garden']):
            return "Nature", "🌳"
        if any(word in text for word in ['learn', 'education', 'workshop']):
            return "Learning", "📚"

        return "Entertainment", "🎭"


def main():
    scraper = TorontoOpenDataScraper()
    events = scraper.fetch_events(days_ahead=30)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    with open('toronto_opendata_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to toronto_opendata_events.json")


if __name__ == "__main__":
    main()
