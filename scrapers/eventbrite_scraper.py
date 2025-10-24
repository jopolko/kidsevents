#!/usr/bin/env python3
"""
EventBrite Scraper for Kids Events
Fetches free AND paid family/kids events from EventBrite API

NOTE: Requires EventBrite OAuth token
Get one at: https://www.eventbrite.com/platform/api#/introduction/authentication
Set environment variable: export EVENTBRITE_TOKEN="your_token_here"
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
import os
import re

class EventBriteScraper:
    def __init__(self):
        self.api_base = "https://www.eventbriteapi.com/v3"
        self.token = os.environ.get('EVENTBRITE_TOKEN')

        if not self.token:
            print("⚠️  No EventBrite API token found")
            print("   Set EVENTBRITE_TOKEN environment variable to use this scraper")

        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def fetch_events(self, days_ahead: int = 14) -> List[Dict]:
        """Fetch free AND paid kids/family events from EventBrite"""

        if not self.token:
            print("   ⚠️  Skipping EventBrite (no API token)")
            return []

        print("🎫 Fetching from EventBrite...")

        try:
            # Calculate date range
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days_ahead)

            # Search params (removed 'price': 'free' to get all events)
            params = {
                'location.address': 'Toronto, ON, Canada',
                'location.within': '25km',
                'start_date.range_start': start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'start_date.range_end': end_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'expand': 'venue,category,ticket_availability',
                'page_size': 50
            }

            events = []
            page = 1
            has_more = True

            while has_more and page <= 5:  # Limit to 5 pages (250 events max)
                params['page'] = page

                response = requests.get(
                    f"{self.api_base}/events/search/",
                    headers=self.headers,
                    params=params,
                    timeout=15
                )

                if response.status_code != 200:
                    print(f"   ❌ API error: {response.status_code}")
                    break

                data = response.json()
                event_list = data.get('events', [])

                for event in event_list:
                    parsed = self._parse_event(event)
                    if parsed:
                        events.append(parsed)

                # Check pagination
                pagination = data.get('pagination', {})
                has_more = pagination.get('has_more_items', False)
                page += 1

            free_count = len([e for e in events if e.get('is_free')])
            paid_count = len(events) - free_count
            print(f"   ✅ Found {len(events)} EventBrite events ({free_count} free, {paid_count} paid)")
            return events

        except Exception as e:
            print(f"   ❌ Error fetching EventBrite events: {e}")
            return []

    def _parse_event(self, event: Dict) -> Dict:
        """Parse EventBrite event into our format"""

        try:
            # Get basic info
            name = event.get('name', {}).get('text', '')
            description = event.get('description', {}).get('text', '')

            # Filter for kids/family events
            if not self._is_kids_relevant(name, description):
                return None

            # Parse date/time
            start_str = event.get('start', {}).get('local', '')
            end_str = event.get('end', {}).get('local', '')

            if not start_str:
                return None

            start_dt = datetime.fromisoformat(start_str)
            end_dt = datetime.fromisoformat(end_str) if end_str else start_dt + timedelta(hours=2)

            # Get venue
            venue = event.get('venue', {})
            venue_name = venue.get('name', 'TBD')
            address = venue.get('address', {})
            address_str = address.get('address_1', '')

            # Get coordinates
            lat = float(venue.get('latitude', 43.6532))
            lng = float(venue.get('longitude', -79.3832))

            # Clean description
            description = self._clean_description(description)

            # Determine category and age groups
            age_groups = self._determine_age_groups(name, description)
            category, icon = self._determine_category(name, description)

            # Determine if event is free
            is_free = event.get('is_free', False)

            # Build event dict
            event_dict = {
                "title": name,
                "description": description,
                "category": category,
                "icon": icon,
                "date": start_dt.strftime('%Y-%m-%d'),
                "start_time": start_dt.strftime('%H:%M'),
                "end_time": end_dt.strftime('%H:%M'),
                "venue": {
                    "name": venue_name,
                    "address": address_str,
                    "neighborhood": "Toronto",
                    "lat": lat,
                    "lng": lng
                },
                "age_groups": age_groups,
                "indoor_outdoor": "Indoor",
                "organized_by": event.get('organizer', {}).get('name', 'EventBrite Organizer'),
                "website": event.get('url', ''),
                "source": "EventBrite",
                "eventbrite_id": event.get('id'),
                "scraped_at": datetime.now().isoformat(),
                "is_free": is_free
            }

            # Add price info if not free
            if not is_free:
                # Try to get ticket info
                ticket_availability = event.get('ticket_availability', {})
                min_price = ticket_availability.get('minimum_ticket_price', {})
                if min_price:
                    price_value = min_price.get('major_value', 0)
                    currency = min_price.get('currency', 'CAD')
                    if price_value > 0:
                        event_dict['price'] = f"${price_value} {currency}"

            return event_dict

        except Exception as e:
            return None

    def _is_kids_relevant(self, title: str, description: str) -> bool:
        """Check if event is relevant to kids/families"""
        text = (title + ' ' + description).lower()

        # Keywords that indicate kids events
        kids_keywords = [
            'kid', 'kids', 'child', 'children', 'family', 'families',
            'baby', 'babies', 'infant', 'toddler', 'preschool',
            'youth', 'teen', 'junior', 'young', 'ages',
            'storytime', 'story time', 'playtime', 'play time',
            'craft', 'workshop', 'stem', 'science for kids',
            'all ages', 'everyone welcome',
            'parent', 'parents', 'mom', 'dad'
        ]

        return any(keyword in text for keyword in kids_keywords)

    def _determine_age_groups(self, title: str, description: str) -> List[str]:
        """Determine age groups from event details"""
        text = (title + ' ' + description).lower()
        age_groups = []

        if any(word in text for word in ['baby', 'babies', 'infant', '0-2']):
            age_groups.append("Babies (0-2)")

        if any(word in text for word in ['toddler', 'preschool', '2-5', '3-5']):
            age_groups.append("Toddlers (3-5)")

        if any(word in text for word in ['kids', 'children', '6-12', 'elementary']):
            age_groups.append("Kids (6-12)")

        if any(word in text for word in ['teen', 'youth', '13-17']):
            age_groups.append("Teens (13-17)")

        if any(word in text for word in ['family', 'all ages', 'everyone']):
            age_groups.append("All Ages")

        return age_groups if age_groups else ["All Ages"]

    def _determine_category(self, title: str, description: str) -> tuple:
        """Determine category and icon"""
        text = (title + ' ' + description).lower()

        if any(word in text for word in ['art', 'craft', 'paint', 'draw']):
            return "Arts", "🎨"
        if any(word in text for word in ['music', 'concert', 'sing', 'dance']):
            return "Entertainment", "🎵"
        if any(word in text for word in ['sport', 'play', 'active']):
            return "Sports", "⚽"
        if any(word in text for word in ['science', 'stem', 'tech', 'robot', 'coding']):
            return "Learning", "🔬"
        if any(word in text for word in ['story', 'book', 'read']):
            return "Learning", "📚"
        if any(word in text for word in ['nature', 'outdoor', 'park']):
            return "Nature", "🌳"

        return "Entertainment", "🎉"

    def _clean_description(self, description: str) -> str:
        """Clean and truncate description"""
        # Remove HTML tags
        clean = re.sub('<[^<]+?>', '', description)

        # Remove excessive whitespace
        clean = re.sub(r'\s+', ' ', clean)

        # Truncate
        if len(clean) > 250:
            clean = clean[:247] + "..."

        return clean.strip()


def main():
    scraper = EventBriteScraper()
    events = scraper.fetch_events(days_ahead=14)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    # Save to JSON
    with open('eventbrite_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to eventbrite_events.json")


if __name__ == "__main__":
    main()
