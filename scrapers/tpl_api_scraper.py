#!/usr/bin/env python3
"""
Toronto Public Library API Scraper
Fetches real events from TPL's Open Data API
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
import re
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class TPLAPIScraper:
    def __init__(self):
        self.api_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca/datastore/dump/c73bbe54-3a48-4ada-8eef-a1a2864021e4"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.geocode_cache = {}  # In-memory cache for geocoding

        # TPL branch locations with coordinates (comprehensive list)
        self.branch_coords = {
            "Agincourt": {"lat": 43.7856, "lng": -79.2787},
            "Albion": {"lat": 43.7372, "lng": -79.5496},
            "Albert Campbell": {"lat": 43.7748, "lng": -79.2305},
            "Alderwood": {"lat": 43.6032, "lng": -79.5479},
            "Annette Street": {"lat": 43.6644, "lng": -79.4815},
            "Barbara Frum": {"lat": 43.7284, "lng": -79.4127},
            "Beaches": {"lat": 43.6687, "lng": -79.2981},
            "Bendale": {"lat": 43.7632, "lng": -79.2518},
            "Black Creek": {"lat": 43.7566, "lng": -79.5234},
            "Bloor/Gladstone": {"lat": 43.6563, "lng": -79.4507},
            "Brentwood": {"lat": 43.6829, "lng": -79.5734},
            "Bridlewood": {"lat": 43.7729, "lng": -79.2824},
            "Broadway": {"lat": 43.7094, "lng": -79.3928},
            "Cedarbrae": {"lat": 43.7631, "lng": -79.2259},
            "Centennial": {"lat": 43.6431, "lng": -79.5360},
            "City Hall": {"lat": 43.6534, "lng": -79.3839},
            "Cliffcrest": {"lat": 43.7129, "lng": -79.2379},
            "College/Shaw": {"lat": 43.6541, "lng": -79.4196},
            "Danforth/Coxwell": {"lat": 43.6868, "lng": -79.3218},
            "Davenport": {"lat": 43.6744, "lng": -79.4174},
            "Dawes Road": {"lat": 43.6888, "lng": -79.2854},
            "Deer Park": {"lat": 43.6880, "lng": -79.3955},
            "Dufferin/St. Clair": {"lat": 43.6783, "lng": -79.4524},
            "Eatonville": {"lat": 43.6522, "lng": -79.5611},
            "Eglinton Square": {"lat": 43.7263, "lng": -79.2761},
            "Evelyn Gregory": {"lat": 43.7722, "lng": -79.2982},
            "Fairview": {"lat": 43.7363, "lng": -79.3471},
            "Flemingdon Park": {"lat": 43.7147, "lng": -79.3369},
            "Fort York": {"lat": 43.6391, "lng": -79.4030},
            "Gerrard/Ashdale": {"lat": 43.6700, "lng": -79.3279},
            "Goldhawk Park": {"lat": 43.7093, "lng": -79.5643},
            "Guildwood": {"lat": 43.7555, "lng": -79.1972},
            "High Park": {"lat": 43.6544, "lng": -79.4657},
            "Highland Creek": {"lat": 43.7820, "lng": -79.1767},
            "Humber Bay": {"lat": 43.6249, "lng": -79.4815},
            "Humber Summit": {"lat": 43.7551, "lng": -79.5781},
            "Jane/Dundas": {"lat": 43.6637, "lng": -79.4949},
            "Jane/Sheppard": {"lat": 43.7430, "lng": -79.4983},
            "Jones": {"lat": 43.6643, "lng": -79.3443},
            "Kennedy/Eglinton": {"lat": 43.7291, "lng": -79.2682},
            "Leaside": {"lat": 43.7067, "lng": -79.3638},
            "Lillian H. Smith": {"lat": 43.6577, "lng": -79.4000},
            "Long Branch": {"lat": 43.5943, "lng": -79.5478},
            "Main Street": {"lat": 43.6886, "lng": -79.3005},
            "Malvern": {"lat": 43.8078, "lng": -79.2288},
            "Maria A. Shchuka": {"lat": 43.7714, "lng": -79.2318},
            "Maryvale": {"lat": 43.7617, "lng": -79.2761},
            "McGregor Park": {"lat": 43.7151, "lng": -79.2998},
            "Merril Collection": {"lat": 43.6577, "lng": -79.4000},
            "Mount Dennis": {"lat": 43.6913, "lng": -79.4889},
            "Mount Pleasant": {"lat": 43.7071, "lng": -79.3889},
            "New Toronto": {"lat": 43.6055, "lng": -79.5182},
            "North York Central Library": {"lat": 43.7675, "lng": -79.4129},
            "Oakwood Village Library and Arts Centre": {"lat": 43.6822, "lng": -79.4350},
            "Palmerston": {"lat": 43.6651, "lng": -79.4144},
            "Parkdale": {"lat": 43.6396, "lng": -79.4390},
            "Pleasant View": {"lat": 43.7524, "lng": -79.4588},
            "Port Union": {"lat": 43.7857, "lng": -79.1363},
            "Queen/Saulter": {"lat": 43.6632, "lng": -79.3269},
            "Rexdale": {"lat": 43.7108, "lng": -79.5707},
            "Richview": {"lat": 43.6908, "lng": -79.5574},
            "Runnymede": {"lat": 43.6526, "lng": -79.4787},
            "Sanderson": {"lat": 43.7799, "lng": -79.2450},
            "Scarborough Civic Centre": {"lat": 43.7739, "lng": -79.2576},
            "S. Walter Stewart": {"lat": 43.6930, "lng": -79.3546},
            "St. Clair/Silverthorn": {"lat": 43.6857, "lng": -79.4682},
            "St. James Town": {"lat": 43.6675, "lng": -79.3776},
            "St. Lawrence": {"lat": 43.6497, "lng": -79.3689},
            "Steeles": {"lat": 43.7916, "lng": -79.4677},
            "Swansea Memorial": {"lat": 43.6487, "lng": -79.4779},
            "Taylor Memorial": {"lat": 43.7777, "lng": -79.2269},
            "Thorncliffe": {"lat": 43.7062, "lng": -79.3452},
            "Todmorden Room": {"lat": 43.6910, "lng": -79.3515},
            "Toronto Reference Library": {"lat": 43.6719, "lng": -79.3864},
            "Victoria Village": {"lat": 43.7284, "lng": -79.3103},
            "Weston": {"lat": 43.7009, "lng": -79.5176},
            "Woodside Square": {"lat": 43.7905, "lng": -79.2946},
            "Woodview Park": {"lat": 43.7521, "lng": -79.3037},
            "Yorkville": {"lat": 43.6710, "lng": -79.3906}
        }

    def fetch_events(self, days_ahead: int = 60) -> List[Dict]:
        """Fetch kids/family events from TPL Open Data API"""

        print("📚 Fetching from Toronto Public Library API...")

        try:
            # Fetch data from API - increased limit
            response = requests.get(
                self.api_url,
                headers=self.headers,
                params={'format': 'json', 'limit': 30000},
                timeout=60
            )

            if response.status_code != 200:
                print(f"   ❌ API error: {response.status_code}")
                return []

            data = response.json()
            records = data.get('records', [])

            events = self._parse_tpl_events(records, days_ahead)
            print(f"   ✅ Found {len(events)} TPL events")
            return events

        except Exception as e:
            print(f"   ❌ Error fetching TPL events: {e}")
            return []

    def _parse_tpl_events(self, records: List, days_ahead: int) -> List[Dict]:
        """Parse TPL API records into our event format"""
        events = []

        # Calculate date range
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        # Keywords for kids events - very broad to capture all possible events
        kids_keywords = ['baby', 'babies', 'child', 'children', 'family', 'families',
                        'kid', 'kids', 'toddler', 'preschool', 'storytime', 'story time',
                        'craft', 'teen', 'youth', 'earlyon', 'junior', 'young', 'parent',
                        'lego', 'play', 'game', 'art', 'music', 'dance', 'sing', 'read',
                        'book', 'learning', 'stem', 'science', 'coding', 'robot', 'maker',
                        'animate', 'puppet', 'costume', 'workshop', 'program', 'club',
                        'ages', 'grade', 'school', 'explore', 'discover', 'fun', 'creative',
                        'build', 'create', 'imagine', 'adventure', 'interactive', 'hands-on',
                        'beginner', 'intro', 'all ages', 'movie', 'film', 'gaming']

        for record in records:
            try:
                # Extract fields from record array
                # Based on API schema: [_id, title, startdate, enddate, starttime, endtime,
                #                       library, location, description, pagelink, id, rcid,
                #                       eventtype1, eventtype2, eventtype3, agegroup1, agegroup2, agegroup3, ...]

                title = str(record[1]) if len(record) > 1 else ''
                startdate_str = record[2] if len(record) > 2 else ''
                starttime_str = str(record[4]) if len(record) > 4 else None
                endtime_str = str(record[5]) if len(record) > 5 else None
                library = str(record[6]) if len(record) > 6 else ''
                description = str(record[8]) if len(record) > 8 else ''
                pagelink = str(record[9]) if len(record) > 9 else ''
                agegroup1 = str(record[15]) if len(record) > 15 else ''
                agegroup2 = str(record[16]) if len(record) > 16 else ''
                agegroup3 = str(record[17]) if len(record) > 17 else ''

                # Parse and filter date
                if not startdate_str:
                    continue

                event_date = datetime.strptime(startdate_str, '%Y-%m-%d').date()

                # Filter: Must be in date range
                if event_date < today or event_date > end_date:
                    continue

                # Filter: Must be kids/family relevant (very permissive)
                text_to_check = (title + ' ' + description + ' ' + agegroup1 + ' ' + agegroup2 + ' ' + agegroup3).lower()

                # First check: explicitly kids-related keywords
                has_kids_keyword = any(kw in text_to_check for kw in kids_keywords)

                # Second check: age group indicates kids/family
                has_kids_age = any(age_term in (agegroup1 + agegroup2 + agegroup3).lower()
                                  for age_term in ['baby', 'babies', 'infant', 'toddler', 'preschool',
                                                  'child', 'children', 'kids', 'kid', 'youth', 'teen',
                                                  'family', 'families', '0-', '1-', '2-', '3-', '4-', '5-',
                                                  '6-', '7-', '8-', '9-', '10-', '11-', '12-', '13-', '14-',
                                                  '15-', '16-', '17-', 'ages 0', 'ages 1', 'ages 2'])

                # Accept if either condition is met
                if not (has_kids_keyword or has_kids_age):
                    continue

                # Filter out job training/employment events (not fun!)
                job_keywords = ['resume', 'job', 'career', 'employment', 'interview', 'cv ', 'volunteer for resume']
                if any(kw in text_to_check for kw in job_keywords):
                    continue

                # Clean description (remove HTML)
                description = self._clean_description(description)

                # Parse times
                start_time = self._parse_time(starttime_str)
                end_time = self._parse_time(endtime_str)

                # Get branch coordinates
                coords = self._get_branch_coords(library)

                # Skip events without valid coordinates
                if coords is None:
                    continue

                # Determine age groups
                age_groups = self._determine_age_groups(title, description, agegroup1, agegroup2, agegroup3)

                # Determine category
                category, icon = self._determine_category(title, description)

                event = {
                    "title": title,
                    "description": description,
                    "category": category,
                    "icon": icon,
                    "date": startdate_str,
                    "start_time": start_time,
                    "end_time": end_time,
                    "venue": {
                        "name": f"Toronto Public Library - {library}",
                        "address": library,
                        "neighborhood": library,
                        "lat": coords["lat"],
                        "lng": coords["lng"],
                        "phone": "416-393-7131"
                    },
                    "age_groups": age_groups,
                    "indoor_outdoor": "Indoor",
                    "organized_by": "Toronto Public Library",
                    "website": pagelink if pagelink != 'None' else "https://www.torontopubliclibrary.ca",
                    "source": "TPL",
                    "scraped_at": datetime.now().isoformat()
                }

                events.append(event)

            except Exception as e:
                # Skip problematic records
                continue

        return events

    def _get_branch_coords(self, library: str) -> Dict:
        """Get coordinates for a library branch"""
        # Try exact match
        if library in self.branch_coords:
            return self.branch_coords[library]

        # Try partial match
        for branch, coords in self.branch_coords.items():
            if branch.lower() in library.lower() or library.lower() in branch.lower():
                return coords

        # Try geocoding the branch name
        coords = self._geocode_library(library)
        if coords:
            return coords

        # If all else fails, return None to skip this event
        return None

    def _geocode_library(self, library_name: str) -> dict:
        """Geocode a library branch using Google Geocoding API"""
        # Check cache
        if library_name in self.geocode_cache:
            return self.geocode_cache[library_name]

        # Get API key
        api_key = os.getenv('GOOGLE_MAPS_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            return None

        try:
            # Format address for geocoding
            address = f"Toronto Public Library {library_name}, Toronto, Ontario, Canada"

            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': address,
                'key': api_key
            }

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'OK' and data.get('results'):
                    location = data['results'][0]['geometry']['location']
                    coords = {"lat": float(location['lat']), "lng": float(location['lng'])}
                    self.geocode_cache[library_name] = coords
                    return coords
        except Exception as e:
            print(f"   ⚠️  Geocoding failed for {library_name}: {e}")

        return None

    def _parse_time(self, time_str) -> str:
        """Parse time string to HH:MM format"""
        if not time_str or time_str == 'None' or time_str.lower() == 'all day':
            return "10:00"  # Default to 10am

        try:
            # If already in HH:MM format
            if ':' in time_str and len(time_str) <= 5:
                return time_str

            # Parse from various formats (e.g., "2:00 PM", "14:00", etc.)
            time_str = time_str.strip().upper()

            # Handle AM/PM format
            if 'AM' in time_str or 'PM' in time_str:
                time_obj = datetime.strptime(time_str, '%I:%M %p')
                return time_obj.strftime('%H:%M')

            # Handle 24-hour format
            if ':' in time_str:
                parts = time_str.split(':')
                hour = int(parts[0])
                minute = int(parts[1][:2])
                return f"{hour:02d}:{minute:02d}"

        except:
            pass

        return "10:00"  # Default fallback

    def _determine_age_groups(self, title: str, description: str, age1: str, age2: str, age3: str) -> List[str]:
        """Determine age groups from event details"""
        text = (title + ' ' + description + ' ' + age1 + ' ' + age2 + ' ' + age3).lower()
        age_groups = []

        # Check age group fields first
        if any(word in (age1 + age2 + age3).lower() for word in ['baby', 'infant']):
            age_groups.append("Babies (0-2)")

        if any(word in (age1 + age2 + age3).lower() for word in ['toddler', 'preschool', 'child']):
            age_groups.append("Toddlers (3-5)")

        if any(word in (age1 + age2 + age3).lower() for word in ['child', 'children']):
            if "Toddlers (3-5)" not in age_groups:
                age_groups.append("Kids (6-12)")

        if any(word in (age1 + age2 + age3).lower() for word in ['teen', 'youth']):
            age_groups.append("Teens (13-17)")

        # Check title/description if no age groups found
        if not age_groups:
            if any(word in text for word in ['baby', 'babies', 'infant']):
                age_groups.append("Babies (0-2)")

            if any(word in text for word in ['toddler', 'preschool']):
                age_groups.append("Toddlers (3-5)")

            if any(word in text for word in ['kids', 'children', 'junior']):
                age_groups.append("Kids (6-12)")

            if any(word in text for word in ['teen', 'youth']):
                age_groups.append("Teens (13-17)")

        # Check for family/all ages
        if any(word in text for word in ['family', 'all ages', 'everyone']):
            age_groups.append("All Ages")

        return age_groups if age_groups else ["All Ages"]

    def _determine_category(self, title: str, description: str) -> tuple:
        """Determine category and icon"""
        text = (title + ' ' + description).lower()

        if any(word in text for word in ['story', 'read', 'book', 'literacy']):
            return "Learning", "📚"
        if any(word in text for word in ['craft', 'art', 'paint', 'draw', 'create']):
            return "Arts", "🎨"
        if any(word in text for word in ['stem', 'science', 'tech', 'coding', 'robot']):
            return "Learning", "🔬"
        if any(word in text for word in ['music', 'sing', 'dance', 'perform']):
            return "Entertainment", "🎵"
        if any(word in text for word in ['lego', 'build', 'construct']):
            return "Learning", "🧱"
        if any(word in text for word in ['play', 'game', 'toy', 'earlyon']):
            return "Play", "🎈"

        return "Learning", "📚"

    def _clean_description(self, description: str) -> str:
        """Clean HTML and truncate description"""
        # Remove HTML tags
        clean = re.sub('<[^<]+?>', '', description)

        # Remove HTML entities
        clean = clean.replace('&#10;', ' ')
        clean = clean.replace('&nbsp;', ' ')
        clean = re.sub('&#\d+;', '', clean)

        # Remove excessive whitespace
        clean = re.sub(r'\s+', ' ', clean)

        # Truncate
        if len(clean) > 250:
            clean = clean[:247] + "..."

        return clean.strip()


def main():
    scraper = TPLAPIScraper()
    events = scraper.fetch_events(days_ahead=60)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    # Save to JSON
    with open('tpl_api_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to tpl_api_events.json")


if __name__ == "__main__":
    main()
