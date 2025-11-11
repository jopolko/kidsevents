#!/usr/bin/env python3
"""
ChatterBlock Events Scraper
Scrapes family/kids events from ChatterBlock Toronto
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
from bs4 import BeautifulSoup
import re
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class ChatterBlockScraper:
    def __init__(self):
        self.base_url = "https://www.chatterblock.com/events/toronto-on-ca-c3981/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.geocode_cache = {}  # In-memory cache for this session

    def fetch_events(self, days_ahead: int = 14) -> List[Dict]:
        """Fetch kids/family events from ChatterBlock"""

        print("🎪 Fetching from ChatterBlock Toronto...")

        try:
            response = requests.get(
                self.base_url,
                headers=self.headers,
                timeout=15
            )

            if response.status_code != 200:
                print(f"   ❌ ChatterBlock error: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract JSON-LD structured data
            json_ld_scripts = soup.find_all('script', type='application/ld+json')

            events = []
            today = datetime.now().date()
            end_date = today + timedelta(days=days_ahead)

            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)

                    # Handle both single events and lists
                    event_list = data if isinstance(data, list) else [data]

                    for event_data in event_list:
                        if event_data.get('@type') == 'Event':
                            parsed = self._parse_event(event_data, today, end_date)
                            if parsed:
                                events.append(parsed)
                except:
                    continue

            print(f"   ✅ Found {len(events)} ChatterBlock events")
            return events

        except Exception as e:
            print(f"   ❌ Error fetching ChatterBlock events: {e}")
            return []

    def _parse_event(self, event_data: Dict, today, end_date) -> Dict:
        """Parse JSON-LD event into our format"""

        try:
            # Get basic info
            name = event_data.get('name', '')
            description = event_data.get('description', '')

            # Filter for kids/family events
            if not self._is_kids_relevant(name, description):
                return None

            # Parse date
            start_str = event_data.get('startDate', '')
            if not start_str:
                return None

            start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            event_date = start_dt.date()

            # Only include events in date range
            if event_date < today or event_date > end_date:
                return None

            # Get venue info
            location = event_data.get('location', {})
            venue_name = location.get('name', 'TBD')

            address_dict = location.get('address', {})
            if isinstance(address_dict, dict):
                street = address_dict.get('streetAddress', '')
                city = address_dict.get('addressLocality', 'Toronto')
                address = f"{street}, {city}" if street else city
            else:
                address = str(address_dict) if address_dict else 'Toronto'

            # Get coordinates from JSON-LD or geocode address
            geo = location.get('geo', {})
            if geo and 'latitude' in geo and 'longitude' in geo:
                lat = float(geo['latitude'])
                lng = float(geo['longitude'])
            else:
                # Geocode the address if no coordinates provided
                coords = self._geocode_address(address)
                if coords:
                    lat, lng = coords
                else:
                    # Skip events without valid coordinates
                    return None

            # Parse times
            end_str = event_data.get('endDate', '')
            end_dt = datetime.fromisoformat(end_str.replace('Z', '+00:00')) if end_str else start_dt + timedelta(hours=2)

            start_time = start_dt.strftime('%H:%M')
            end_time = end_dt.strftime('%H:%M')

            # Determine category, icon, age groups
            age_groups = self._determine_age_groups(name, description)
            category, icon = self._determine_category(name, description)

            # Get URL
            url = event_data.get('url', 'https://www.chatterblock.com')

            # Check if free
            is_free = self._is_free_event(event_data, name, description)

            return {
                "title": name,
                "description": description,
                "category": category,
                "icon": icon,
                "date": event_date.strftime('%Y-%m-%d'),
                "start_time": start_time,
                "end_time": end_time,
                "venue": {
                    "name": venue_name,
                    "address": address,
                    "neighborhood": "Toronto",
                    "lat": lat,
                    "lng": lng
                },
                "age_groups": age_groups,
                "indoor_outdoor": "Indoor",
                "organized_by": event_data.get('organizer', {}).get('name', 'Community Organizer'),
                "website": url,
                "source": "ChatterBlock",
                "scraped_at": datetime.now().isoformat(),
                "is_free": is_free
            }

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
            'parent', 'parents', 'mom', 'dad', 'caregiver'
        ]

        return any(keyword in text for keyword in kids_keywords)

    def _is_free_event(self, event_data: Dict, title: str, description: str) -> bool:
        """Determine if event is free"""
        text = (title + ' ' + description).lower()

        # Check for free indicators
        if any(word in text for word in ['free', 'no cost', 'complimentary', 'no admission']):
            return True

        # Check offers
        offers = event_data.get('offers', {})
        if isinstance(offers, dict):
            price = offers.get('price', '')
            if price == '0' or price == 0 or price == 'Free':
                return True

        return False

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

    def _geocode_address(self, address: str) -> tuple:
        """Geocode an address using Google Geocoding API"""
        # Check cache first
        if address in self.geocode_cache:
            return self.geocode_cache[address]

        # Get Google Maps API key
        api_key = os.getenv('GOOGLE_MAPS_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            return None

        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': f"{address}, Ontario, Canada",
                'key': api_key
            }

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'OK' and data.get('results'):
                    location = data['results'][0]['geometry']['location']
                    coords = (float(location['lat']), float(location['lng']))
                    self.geocode_cache[address] = coords
                    return coords
        except Exception as e:
            print(f"   ⚠️  Geocoding failed for {address}: {e}")

        return None

    def _determine_category(self, title: str, description: str) -> tuple:
        """Determine category and icon"""
        text = (title + ' ' + description).lower()

        if any(word in text for word in ['art', 'craft', 'paint', 'draw', 'pottery', 'maker']):
            return "Arts", "🎨"
        if any(word in text for word in ['music', 'concert', 'sing', 'dance', 'performance']):
            return "Entertainment", "🎵"
        if any(word in text for word in ['sport', 'play', 'active', 'swim', 'skate', 'hockey']):
            return "Sports", "⚽"
        if any(word in text for word in ['science', 'stem', 'tech', 'robot', 'coding', 'workshop']):
            return "Learning", "🔬"
        if any(word in text for word in ['story', 'book', 'read', 'library']):
            return "Learning", "📚"
        if any(word in text for word in ['nature', 'outdoor', 'park', 'farm', 'garden']):
            return "Nature", "🌳"
        if any(word in text for word in ['festival', 'fair', 'market', 'carnival']):
            return "Entertainment", "🎪"

        return "Entertainment", "🎉"


def main():
    scraper = ChatterBlockScraper()
    events = scraper.fetch_events(days_ahead=14)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    # Show sample
    if events:
        print(f"\n   Sample events:")
        for event in events[:3]:
            print(f"   - {event['title']} ({event['date']})")

    # Save to JSON
    with open('chatterblock_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved to chatterblock_events.json")


if __name__ == "__main__":
    main()
