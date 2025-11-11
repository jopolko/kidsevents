#!/usr/bin/env python3
"""
Toronto Open Data API Scraper
Fetches festivals and events from the City of Toronto Open Data Portal
API Documentation: https://open.toronto.ca/dataset/festivals-events/
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
import re

class TorontoOpenDataScraper:
    def __init__(self):
        self.api_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/9201059e-43ed-4369-885e-0b867652feac/resource/8900fdb2-7f6c-4f50-8581-b463311ff05d/download/file.json"

        # Toronto neighborhoods/areas to validate location
        self.toronto_areas = [
            'toronto', 'etobicoke', 'scarborough', 'north york', 'york',
            'downtown', 'midtown', 'uptown', 'east york', 'old toronto',
            # Toronto neighborhoods
            'beaches', 'leslieville', 'riverdale', 'cabbagetown', 'parkdale',
            'roncesvalles', 'high park', 'junction', 'liberty village',
            'king west', 'queen west', 'dundas west', 'ossington',
            'kensington', 'chinatown', 'little italy', 'little portugal',
            'bloorskirroronto', 'annex', 'forest hill', 'rosedale', 'davisville',
            'eglinton', 'lawrence park', 'leaside', 'don mills',
            'agincourt', 'malvern', 'rouge', 'guild', 'wexford',
            'danforth', 'greektown'
        ]

        # Areas to EXCLUDE (not Toronto)
        self.exclude_areas = [
            'burlington', 'oakville', 'milton', 'halton', 'hamilton',
            'mississauga', 'brampton', 'caledon', 'peel',
            'vaughan', 'richmond hill', 'markham', 'newmarket', 'aurora',
            'king city', 'pickering', 'ajax', 'whitby', 'oshawa', 'durham',
            'clarington', 'uxbridge', 'stouffville'
        ]

    def fetch_events(self, days_ahead: int = 60) -> List[Dict]:
        """Fetch kids/family events from Toronto Open Data"""

        print("🏛️  Fetching from Toronto Open Data API...")

        try:
            response = requests.get(self.api_url, timeout=30)

            if response.status_code != 200:
                print(f"   ❌ API error: {response.status_code}")
                return []

            data = response.json()
            all_events = data.get('value', [])

            # Filter and parse events
            events = []
            today = datetime.now().date()
            end_date = today + timedelta(days=days_ahead)

            for event in all_events:
                parsed = self._parse_event(event, today, end_date)
                if parsed:
                    events.append(parsed)

            print(f"   ✅ Found {len(events)} Toronto Open Data events")
            return events

        except Exception as e:
            print(f"   ❌ Error fetching Toronto Open Data events: {e}")
            return []

    def _parse_event(self, event: Dict, today, end_date) -> Dict:
        """Parse an individual event from the API"""

        try:
            # Get basic info
            event_name = event.get('event_name', '').strip()
            if not event_name:
                return None

            # Check if event is kid/family friendly
            if not self._is_kids_event(event):
                return None

            # Get dates
            start_date = event.get('event_startdate')
            if not start_date:
                return None

            # Parse start date
            event_date = datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()

            # Filter by date range
            if event_date < today or event_date > end_date:
                return None

            # Get location and validate it's in Toronto
            event_locations = event.get('event_locations', [])

            # Skip if location is explicitly in excluded areas (Burlington, etc)
            if event_locations and self._is_excluded_location(event_locations):
                return None

            # Parse location from dict structure
            venue_info = self._parse_location_dict(event_locations[0] if event_locations else {})

            # Get description
            description = event.get('short_description') or event.get('event_description', '')
            description = self._clean_text(description)[:250]

            # Get category
            event_categories = event.get('event_category', [])
            category, icon = self._categorize_event(event_categories, event_name, description)

            # Get pricing
            is_free = event.get('free_event', 'No') == 'Yes'
            child_price = event.get('event_price_child')

            # Get times
            calendar_date = event.get('calendar_date', '')
            start_time = self._extract_time(calendar_date) or '10:00'
            end_time = self._calculate_end_time(start_time)

            # Determine if free
            if not is_free and child_price:
                try:
                    # Check if child price is 0 or null
                    if float(child_price) == 0:
                        is_free = True
                except:
                    pass

            # Include all free events, and paid events if they have low/no child prices or are explicitly family events
            # This is already filtered to kids events by _is_kids_event, so we're good

            # Get website
            website = event.get('event_website') or event.get('ticket_website', '')

            # Build event
            return {
                'title': event_name,
                'description': description or event_name,
                'category': category,
                'icon': icon,
                'date': event_date.strftime('%Y-%m-%d'),
                'start_time': start_time,
                'end_time': end_time,
                'venue': venue_info,
                'age_groups': self._determine_age_groups(event_name, description),
                'indoor_outdoor': 'Both',
                'organized_by': 'City of Toronto',
                'website': website,
                'source': 'TorontoOpenData',
                'is_free': is_free,
                'scraped_at': datetime.now().isoformat()
            }

        except Exception as e:
            return None

    def _is_excluded_location(self, locations: List[Dict]) -> bool:
        """Check if event location is in excluded areas (not Toronto)"""

        if not locations:
            return False

        # Extract text from location dicts
        location_texts = []
        for loc in locations:
            if isinstance(loc, dict):
                location_texts.append(loc.get('location_name', ''))
                location_texts.append(loc.get('location_address', ''))
            elif isinstance(loc, str):
                location_texts.append(loc)

        location_text = ' '.join(location_texts).lower()

        # Check for excluded areas (Burlington, Mississauga, etc)
        for exclude in self.exclude_areas:
            if exclude in location_text:
                return True

        return False

    def _is_kids_event(self, event: Dict) -> bool:
        """Check if event is suitable for kids/families"""

        event_name = event.get('event_name', '').lower()
        description = event.get('short_description', '') or event.get('event_description', '')
        description = description.lower() if description else ''

        # Keywords that indicate kids events
        kids_keywords = [
            'kid', 'kids', 'child', 'children', 'family', 'families',
            'baby', 'babies', 'infant', 'toddler', 'preschool',
            'youth', 'teen', 'junior', 'ages 0', 'ages 1', 'ages 2',
            'ages 3', 'ages 4', 'ages 5', 'ages 6', 'all ages'
        ]

        text = event_name + ' ' + description
        return any(keyword in text for keyword in kids_keywords)

    def _parse_location_dict(self, location_dict: Dict) -> Dict:
        """Parse location dict from API into venue dict"""

        if not location_dict:
            return {
                'name': 'Toronto',
                'address': '',
                'neighborhood': 'Toronto',
                'lat': 43.6532,
                'lng': -79.3832
            }

        venue_name = location_dict.get('location_name', 'Toronto Venue')
        address = location_dict.get('location_address', '')

        # Try to get GPS coordinates
        lat = 43.6532
        lng = -79.3832
        location_gps = location_dict.get('location_gps', [])
        if location_gps and isinstance(location_gps, list) and len(location_gps) > 0:
            try:
                # location_gps is a string representation of JSON
                import json
                if isinstance(location_gps, str):
                    gps_data = json.loads(location_gps)
                else:
                    gps_data = location_gps

                if gps_data and len(gps_data) > 0:
                    lat = float(gps_data[0].get('gps_lat', lat))
                    lng = float(gps_data[0].get('gps_lng', lng))
            except:
                pass

        # Try to extract neighborhood from address
        neighborhood = 'Toronto'
        for area in ['Etobicoke', 'Scarborough', 'North York', 'East York']:
            if area in address:
                neighborhood = area
                break

        return {
            'name': venue_name,
            'address': address,
            'neighborhood': neighborhood,
            'lat': lat,
            'lng': lng
        }

    def _categorize_event(self, categories: List[str], name: str, description: str) -> tuple:
        """Categorize event and assign icon"""

        text = (name + ' ' + description).lower()

        # Check API categories first
        if categories:
            category_str = ' '.join(categories).lower()
            if 'art' in category_str or 'exhibit' in category_str:
                return 'Arts', '🎨'
            if 'music' in category_str or 'performance' in category_str:
                return 'Entertainment', '🎵'
            if 'sport' in category_str:
                return 'Sports', '⚽'
            if 'festival' in category_str or 'fair' in category_str:
                return 'Entertainment', '🎪'

        # Check event text
        if any(word in text for word in ['art', 'craft', 'paint', 'draw', 'exhibit']):
            return 'Arts', '🎨'
        if any(word in text for word in ['music', 'concert', 'dance', 'perform']):
            return 'Entertainment', '🎵'
        if any(word in text for word in ['sport', 'play', 'active']):
            return 'Sports', '⚽'
        if any(word in text for word in ['story', 'book', 'read', 'learn']):
            return 'Learning', '📚'
        if any(word in text for word in ['festival', 'fair', 'carnival']):
            return 'Entertainment', '🎪'

        return 'Entertainment', '🎉'

    def _determine_age_groups(self, name: str, description: str) -> List[str]:
        """Determine age groups from event details"""

        text = (name + ' ' + description).lower()
        age_groups = []

        if any(word in text for word in ['baby', 'babies', 'infant', '0-2']):
            age_groups.append('Babies (0-2)')
        if any(word in text for word in ['toddler', 'preschool', '3-5', '2-5']):
            age_groups.append('Toddlers (3-5)')
        if any(word in text for word in ['kid', 'children', '6-12', 'elementary']):
            age_groups.append('Kids (6-12)')
        if any(word in text for word in ['teen', 'youth', '13-17']):
            age_groups.append('Teens (13-17)')
        if any(word in text for word in ['family', 'all ages', 'everyone']):
            age_groups.append('All Ages')

        return age_groups if age_groups else ['All Ages']

    def _extract_time(self, datetime_str: str) -> str:
        """Extract time from datetime string"""

        if not datetime_str:
            return None

        try:
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return dt.strftime('%H:%M')
        except:
            return None

    def _calculate_end_time(self, start_time: str) -> str:
        """Calculate end time (assume 2 hours after start)"""

        try:
            hour, minute = map(int, start_time.split(':'))
            hour = (hour + 2) % 24
            return f"{hour:02d}:{minute:02d}"
        except:
            return '17:00'

    def _clean_text(self, text: str) -> str:
        """Clean HTML and extra whitespace from text"""

        if not text:
            return ''

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


def main():
    scraper = TorontoOpenDataScraper()
    events = scraper.fetch_events(days_ahead=14)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    if events:
        print(f"\n   Sample events:")
        for event in events[:5]:
            print(f"   {event['icon']} {event['title']} - {event['date']}")

    # Save to JSON
    with open('toronto_opendata_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved to toronto_opendata_events.json")


if __name__ == "__main__":
    main()
