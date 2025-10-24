#!/usr/bin/env python3
"""
Toronto City Events Scraper
Fetches free kids/family events from City of Toronto's official events API
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
import re

class TorontoEventsScraper:
    def __init__(self):
        self.api_url = "https://secure.toronto.ca/cc_sr_v1/data/edc_eventcal_APR"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def fetch_events(self, days_ahead: int = 90, limit: int = 500) -> List[Dict]:
        """Fetch free family/kids events from City of Toronto"""

        print("🏛️  Fetching events from City of Toronto...")

        try:
            response = requests.get(
                self.api_url,
                headers=self.headers,
                params={'limit': limit},
                timeout=15
            )

            if response.status_code != 200:
                print(f"   ❌ API error: {response.status_code}")
                return []

            data = response.json()
            events = self._parse_toronto_events(data, days_ahead)
            print(f"   ✅ Found {len(events)} City of Toronto events")
            return events

        except Exception as e:
            print(f"   ❌ Error fetching Toronto events: {e}")
            return []

    def _parse_toronto_events(self, data: List[Dict], days_ahead: int) -> List[Dict]:
        """Parse Toronto API response into our event format"""
        events = []

        # Calculate date range
        today = datetime.now()
        end_date = today + timedelta(days=days_ahead)

        for item in data:
            cal_event = item.get('calEvent', {})

            # Note: Not filtering by isCityEvent - community events are valuable too

            # Filter: Must be free
            fees = cal_event.get('fees', '')
            if fees and fees.lower() not in ['free', 'no fee', '$0', '']:
                continue

            # Parse dates
            try:
                start_str = cal_event.get('startDate', '')
                end_str = cal_event.get('endDate', '')

                if not start_str:
                    continue

                start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))

                # Filter: Must be in date range
                if start_dt < today or start_dt > end_date:
                    continue

                # End time
                if end_str:
                    end_dt = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                else:
                    end_dt = start_dt + timedelta(hours=2)

            except Exception:
                continue

            # Get basic info
            title = cal_event.get('eventName', '').strip()
            if not title:
                continue

            description = cal_event.get('description', '')
            description = self._clean_description(description)

            # Filter: Must be relevant to kids/families
            if not self._is_kids_relevant(title, description, cal_event):
                continue

            # Get location
            venue_name = cal_event.get('locationName', 'TBD')
            address = cal_event.get('locationAddress', '')
            city = cal_event.get('locationCity', 'Toronto')

            # Try to get coordinates
            lat, lng = self._get_coords(cal_event)

            # Determine age groups and category
            age_groups = self._determine_age_groups(title, description, cal_event)
            category, icon = self._determine_category(title, description, cal_event)

            # Determine indoor/outdoor
            indoor_outdoor = "Indoor"
            categories = cal_event.get('categoryString', '').lower()
            if any(word in categories for word in ['outdoor', 'park', 'nature']):
                indoor_outdoor = "Outdoor"

            # Get organizer
            organizer = cal_event.get('orgName', 'City of Toronto')

            # Get website
            website = cal_event.get('recUrl', '')
            if not website:
                website = f"https://www.toronto.ca/event-cal/{cal_event.get('_id', '')}"

            event = {
                "title": title,
                "description": description,
                "category": category,
                "icon": icon,
                "date": start_dt.strftime('%Y-%m-%d'),
                "start_time": start_dt.strftime('%H:%M'),
                "end_time": end_dt.strftime('%H:%M'),
                "venue": {
                    "name": venue_name,
                    "address": address,
                    "neighborhood": city,
                    "lat": lat,
                    "lng": lng
                },
                "age_groups": age_groups,
                "indoor_outdoor": indoor_outdoor,
                "organized_by": organizer,
                "website": website,
                "source": "CityOfToronto",
                "toronto_event_id": cal_event.get('_id'),
                "scraped_at": datetime.now().isoformat()
            }

            events.append(event)

        return events

    def _is_kids_relevant(self, title: str, description: str, cal_event: Dict) -> bool:
        """Check if event is relevant to kids/families"""
        text = (title + " " + description).lower()
        categories = cal_event.get('categoryString', '').lower()

        # Keywords that indicate kids events
        kids_keywords = [
            'kid', 'kids', 'child', 'children', 'family', 'families',
            'baby', 'babies', 'infant', 'toddler', 'preschool',
            'youth', 'teen', 'junior', 'young', 'ages',
            'storytime', 'story time', 'playtime', 'play time',
            'craft', 'activity', 'workshop', 'painting', 'art',
            'all ages', 'everyone welcome', 'welcome all',
            'park', 'playground', 'outdoor', 'nature',
            'learn', 'education', 'class', 'program'
        ]

        # Check title, description, and categories
        if any(keyword in text for keyword in kids_keywords):
            return True

        if any(keyword in categories for keyword in ['family', 'children', 'youth', 'arts', 'parks']):
            return True

        # If it's an outdoor/arts/workshop event and free, it's likely family-friendly
        if any(word in categories for word in ['arts', 'outdoors', 'parks', 'workshops']):
            return True

        return False

    def _get_coords(self, cal_event: Dict) -> tuple:
        """Extract coordinates from event"""
        # Try geolocation field
        geolocation = cal_event.get('geolocation', {})
        if geolocation:
            lat = geolocation.get('lat')
            lng = geolocation.get('lng')
            if lat and lng:
                return float(lat), float(lng)

        # Default to downtown Toronto
        return 43.6532, -79.3832

    def _determine_age_groups(self, title: str, description: str, cal_event: Dict) -> List[str]:
        """Determine age groups from event details"""
        text = (title + " " + description).lower()
        age_groups = []

        if any(word in text for word in ['baby', 'babies', 'infant', '0-2', '0-18 months']):
            age_groups.append("Babies (0-2)")

        if any(word in text for word in ['toddler', 'preschool', '2-5', '3-5']):
            age_groups.append("Toddlers (3-5)")

        if any(word in text for word in ['kids', 'children', '6-12', 'elementary', 'junior']):
            age_groups.append("Kids (6-12)")

        if any(word in text for word in ['teen', 'youth', '13-17', 'adolescent']):
            age_groups.append("Teens (13-17)")

        if any(word in text for word in ['family', 'all ages', 'everyone']):
            age_groups.append("All Ages")

        return age_groups if age_groups else ["All Ages"]

    def _determine_category(self, title: str, description: str, cal_event: Dict) -> tuple:
        """Determine category and icon"""
        text = (title + " " + description).lower()
        categories = cal_event.get('categoryString', '').lower()

        if any(word in text + categories for word in ['art', 'craft', 'paint', 'draw', 'creative']):
            return "Arts", "🎨"
        if any(word in text + categories for word in ['music', 'concert', 'sing', 'dance', 'performance']):
            return "Entertainment", "🎵"
        if any(word in text + categories for word in ['sport', 'soccer', 'basketball', 'play', 'active', 'fitness']):
            return "Sports", "⚽"
        if any(word in text + categories for word in ['science', 'stem', 'tech', 'learn', 'education', 'workshop']):
            return "Learning", "🔬"
        if any(word in text + categories for word in ['story', 'book', 'read', 'library', 'literary']):
            return "Learning", "📚"
        if any(word in text + categories for word in ['nature', 'outdoor', 'park', 'hike', 'environment']):
            return "Nature", "🌳"
        if any(word in text + categories for word in ['festival', 'celebration', 'community']):
            return "Entertainment", "🎉"

        return "Entertainment", "🎭"

    def _clean_description(self, description: str) -> str:
        """Clean and truncate description"""
        # Remove HTML entities
        clean = description.replace('&#10;', ' ')
        clean = clean.replace('&#8217;', "'")
        clean = clean.replace('&#8212;', "-")

        # Remove HTML tags
        clean = re.sub('<[^<]+?>', '', clean)

        # Remove excessive whitespace
        clean = re.sub(r'\s+', ' ', clean)

        # Truncate
        if len(clean) > 250:
            clean = clean[:247] + "..."

        return clean.strip()


def main():
    scraper = TorontoEventsScraper()
    events = scraper.fetch_events(days_ahead=30)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    # Save to JSON
    with open('toronto_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to toronto_events.json")


if __name__ == "__main__":
    main()
