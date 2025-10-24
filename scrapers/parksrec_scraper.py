#!/usr/bin/env python3
"""
Toronto Parks & Recreation Drop-In Programs Scraper
Fetches free drop-in programs for kids from Toronto Open Data
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
import time
import os
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class ParksRecScraper:
    def __init__(self):
        self.dropin_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/1a5be46a-4039-48cd-a2d2-8e702abf9516/resource/067b41e7-ac8a-4d3f-ad08-089f8cd70316/download/drop-in.json"
        self.locations_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/1a5be46a-4039-48cd-a2d2-8e702abf9516/resource/87f95a5a-184f-4df5-ad37-84bcc1ea99a9/download/locations.json"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        # Geocoding cache - load from file if exists
        self.geocode_cache_file = 'geocode_cache.json'
        self.geocode_cache = self._load_geocode_cache()

        # Direct phone numbers for major community centres
        self.facility_phones = {
            'Glen Long Community Centre': '416-395-7921',
            'Scadding Court Community Centre': '416-392-0335',
            'Regent Park Community Centre': '416-392-0335',
            'Eastview Neighbourhood Community Centre': '416-396-7946',
            'Harbourfront Community Centre': '416-392-1509',
            'North Toronto Memorial Community Centre': '416-395-7954',
            'Scarborough Civic Centre': '416-396-4040',
            'Etobicoke Olympium': '416-394-8954',
            'Malvern Recreation Centre': '416-396-4054',
            'Leaside Memorial Community Gardens': '416-396-4037',
            'St Lawrence Community Centre': '416-392-1228',
            'High Park Community Centre': '416-392-6916',
            'Swansea Town Hall': '416-392-0335',
            'Frankland Community Centre': '416-392-0335',
            'Beaches Recreation Centre': '416-392-0753',
            'Moss Park Community Centre': '416-392-0335',
            'Wallace Emerson Community Centre': '416-392-0039',
            'Dufferin Grove Community Centre': '416-392-0335',
            'Dovercourt Recreation Centre': '416-392-0744',
            'Birchmount Community Centre': '416-396-4311',
            'Agincourt Community Recreation Centre': '416-396-4037',
            'Earl Bales Community Centre': '416-395-7873',
            'Scarborough Village Recreation Centre': '416-396-4048',
            'Flemingdon Park': '416-395-0300',
            'Flemingdon Community Centre & Playground Paradise': '416-395-0300',
            'Centennial Recreation Centre - Scarborough': '416-396-4057',
            'Hillcrest Community Centre': '416-392-0746',
            'Jimmie Simpson Recreation Centre': '416-392-0751',
            'Parkdale Community Recreation Centre': '416-392-6696',
            'East York Community Recreation Centre': '416-396-2880',
            'St Lawrence Community Recreation Centre': '416-392-1228',
            # Newly added phone numbers
            'Albion Arena': '416-394-8690',
            'Annette Community Recreation Centre': '416-392-0736',
            'Barbara Frum Recreation Centre': '416-395-6123',
            'Canoe Landing Community Recreation Centre': '416-397-4200',
            'Driftwood Community Recreation Centre': '416-395-7944',
            'Edithvale Community Centre': '416-395-6164',
            'Fairbank Memorial Community Centre': '416-394-2473',
            'Heron Park Community Recreation Centre': '416-396-4035',
            "L'Amoreaux Community Recreation Centre": '416-396-4510',
            'Mary McCormick Recreation Centre': '416-392-0742',
            'Oriole Community Recreation Centre': '416-395-6005',
            'Roding Community Centre': '416-395-7964',
            'Swansea Community Recreation Centre': '416-392-6796',
            'Victoria Village Recreation Centre and Arena': '416-395-0143',
            'Wellesley Community Centre': '416-392-0227',
            'Goulding Community Recreation Centre': '416-395-0123',
            'John Innes Community Recreation Centre': '416-392-6779',
            'Matty Eckler Recreation Centre': '416-392-0750',
            'Northwood Community Centre': '416-395-6182',
            'Oakridge Community Recreation Centre': '416-338-1966',
            'McGregor Park Community Centre': '416-396-4023',
            'Trinity Community Recreation Centre': '416-392-0743',
            'Dennis R. Timbrell Resource Centre': '416-395-7972',
            'Cummer Park Community Centre': '416-395-7803',
            'Ellesmere Community Recreation Centre': '416-396-5536'
        }

    def _load_geocode_cache(self) -> dict:
        """Load geocode cache from file"""
        if os.path.exists(self.geocode_cache_file):
            try:
                with open(self.geocode_cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_geocode_cache(self):
        """Save geocode cache to file"""
        try:
            with open(self.geocode_cache_file, 'w') as f:
                json.dump(self.geocode_cache, f)
        except:
            pass

    def fetch_events(self, days_ahead: int = 14) -> List[Dict]:
        """Fetch Parks & Rec drop-in programs for kids"""

        print("🏃 Fetching from Toronto Parks & Recreation...")

        try:
            # Fetch locations data
            locations_response = requests.get(
                self.locations_url,
                headers=self.headers,
                timeout=30
            )

            if locations_response.status_code != 200:
                print(f"   ❌ Locations API error: {locations_response.status_code}")
                return []

            locations_data = locations_response.json()
            locations_dict = {loc['Location ID']: loc for loc in locations_data}

            # Fetch drop-in programs data
            dropin_response = requests.get(
                self.dropin_url,
                headers=self.headers,
                timeout=30
            )

            if dropin_response.status_code != 200:
                print(f"   ❌ Drop-in API error: {dropin_response.status_code}")
                return []

            dropin_data = dropin_response.json()
            events = self._parse_dropin_programs(dropin_data, locations_dict, days_ahead)

            # Save geocode cache for next run
            self._save_geocode_cache()

            print(f"   ✅ Found {len(events)} Parks & Rec drop-in programs")
            return events

        except Exception as e:
            print(f"   ❌ Error fetching Parks & Rec events: {e}")
            return []

    def _geocode_address(self, address: str, district: str) -> tuple:
        """Geocode an address using Google Geocoding API with caching"""
        # Check cache first
        cache_key = f"{address}, {district}, Ontario, Canada"
        if cache_key in self.geocode_cache:
            return self.geocode_cache[cache_key]

        # Get Google Maps API key from environment
        api_key = os.getenv('GOOGLE_MAPS_API_KEY') or os.getenv('GOOGLE_API_KEY')

        if not api_key:
            print(f"   ⚠️  No Google API key found, skipping geocoding for {address}")
            # Don't cache failed attempts - return None to indicate failure
            return None

        # Use Google Geocoding API
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': cache_key,
                'key': api_key
            }

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'OK' and data.get('results'):
                    location = data['results'][0]['geometry']['location']
                    lat = float(location['lat'])
                    lng = float(location['lng'])
                    self.geocode_cache[cache_key] = (lat, lng)
                    return (lat, lng)
                elif data.get('status') == 'ZERO_RESULTS':
                    print(f"   ⚠️  No geocoding results for {address}")
                else:
                    print(f"   ⚠️  Geocoding error for {address}: {data.get('status')}")
            else:
                print(f"   ⚠️  Geocoding API error {response.status_code} for {address}")
        except Exception as e:
            print(f"   ⚠️  Geocoding failed for {address}: {e}")

        # Don't cache failed attempts - return None to indicate failure
        return None

    def _parse_dropin_programs(self, programs: List[Dict], locations_dict: Dict, days_ahead: int) -> List[Dict]:
        """Parse drop-in programs into event format"""
        events = []

        # Calculate date range
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        for program in programs:
            try:
                # Filter for kids programs only (age max <= 17)
                age_max = program.get('Age Max')
                if not age_max or age_max == 'None':
                    continue

                age_max_int = int(age_max)
                if age_max_int > 17:
                    continue

                # Parse program date
                first_date_str = program.get('First Date')
                if not first_date_str:
                    continue

                program_date = datetime.strptime(first_date_str, '%Y-%m-%d').date()

                # Only include programs within our date range
                if program_date < today or program_date > end_date:
                    continue

                # Get location info
                location_id = program.get('Location ID')
                location = locations_dict.get(location_id, {})

                location_name = location.get('Location Name', 'Parks & Rec Center')

                # Build address
                street_no = location.get('Street No', '')
                street_name = location.get('Street Name', '')
                street_type = location.get('Street Type', '')
                street_dir = location.get('Street Direction', '')

                address_parts = [p for p in [street_no, street_name, street_type, street_dir] if p and p != 'None']
                address = ' '.join(address_parts) if address_parts else 'TBD'

                district = location.get('District', 'Toronto')

                # Format times
                start_hour = int(program.get('Start Hour', 0))
                start_minute = int(program.get('Start Minute', 0))
                end_hour = int(program.get('End Hour', 0))
                end_minute = int(program.get('End Min', 0))

                start_time = f"{start_hour:02d}:{start_minute:02d}"
                end_time = f"{end_hour:02d}:{end_minute:02d}"

                # Determine age groups
                age_min = program.get('Age Min', '0')
                age_min_int = int(age_min) if age_min and age_min != 'None' else 0

                age_groups = self._get_age_groups(age_min_int, age_max_int)

                # Determine category and icon
                course_title = program.get('Course Title', '')
                section = program.get('Section', '')
                category, icon = self._categorize_program(course_title, section)

                # Get direct phone number if available
                phone = self.facility_phones.get(location_name)

                # Geocode address for accurate distance sorting
                coords = self._geocode_address(address, district)

                # Skip events without valid coordinates
                if coords is None:
                    continue

                lat, lng = coords

                # Create event
                event = {
                    "title": course_title,
                    "description": f"Free drop-in program at {location_name}. {section}. Ages {age_min}-{age_max}.",
                    "category": category,
                    "icon": icon,
                    "date": program_date.strftime('%Y-%m-%d'),
                    "start_time": start_time,
                    "end_time": end_time,
                    "venue": {
                        "name": location_name,
                        "address": address,
                        "neighborhood": district,
                        "lat": lat,
                        "lng": lng
                    },
                    "age_groups": age_groups,
                    "indoor_outdoor": self._get_indoor_outdoor(location.get('Location Type', '')),
                    "organized_by": "City of Toronto Parks & Recreation",
                    "website": "https://www.toronto.ca/data/parks/prd/index.html",
                    "source": "ParksRec",
                    "scraped_at": datetime.now().isoformat()
                }

                # Only add phone number if we have a direct number (not 311)
                if phone:
                    event["venue"]["phone"] = phone
                    event["phone"] = phone

                events.append(event)

            except Exception as e:
                # Skip programs with parsing errors
                continue

        return events

    def _get_age_groups(self, age_min: int, age_max: int) -> List[str]:
        """Convert age range to age group tags"""
        age_groups = []

        if age_min <= 2 and age_max >= 0:
            age_groups.append("Babies (0-2)")
        if age_min <= 5 and age_max >= 3:
            age_groups.append("Toddlers (3-5)")
        if age_min <= 12 and age_max >= 6:
            age_groups.append("Kids (6-12)")
        if age_min <= 17 and age_max >= 13:
            age_groups.append("Teens (13-17)")

        return age_groups if age_groups else ["All Ages"]

    def _categorize_program(self, title: str, section: str) -> tuple:
        """Categorize program and assign icon"""
        title_lower = title.lower()
        section_lower = section.lower()

        # Sports
        if any(word in title_lower for word in ['sport', 'basketball', 'soccer', 'hockey', 'swim', 'skating', 'tennis', 'badminton']):
            return ('Sports', '⚽')

        # Arts
        if any(word in title_lower for word in ['art', 'craft', 'paint', 'draw', 'music', 'dance', 'drama', 'theatre']):
            return ('Arts', '🎨')

        # Learning (includes early years)
        if any(word in title_lower or word in section_lower for word in ['learn', 'early years', 'homework', 'stem', 'science', 'reading']):
            return ('Learning', '📚')

        # Play
        if any(word in title_lower for word in ['play', 'fun', 'recreation', 'games']):
            return ('Play', '🎮')

        # Nature
        if any(word in title_lower for word in ['nature', 'outdoor', 'park', 'garden', 'hiking']):
            return ('Nature', '🌳')

        # Default
        return ('Entertainment', '🎉')

    def _get_indoor_outdoor(self, location_type: str) -> str:
        """Determine if indoor or outdoor based on location type"""
        location_type_lower = location_type.lower()

        if any(word in location_type_lower for word in ['park', 'field', 'outdoor', 'trail']):
            return 'Outdoor'

        return 'Indoor'


def main():
    scraper = ParksRecScraper()
    events = scraper.fetch_events(days_ahead=14)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    # Save to JSON
    with open('parksrec_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to parksrec_events.json")


if __name__ == "__main__":
    main()
