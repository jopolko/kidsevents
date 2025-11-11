#!/usr/bin/env python3
"""
Google Place ID Lookup Module
Resolves venue addresses to Google Place IDs with caching and rate limiting
"""

import os
import json
import time
import hashlib
import requests
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from secure location
env_path = Path('/var/secrets/kidsevents.env')
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    # Fallback to local .env for development
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)


class PlaceIDLookup:
    """
    Looks up Google Place IDs for venues with caching to minimize API calls
    """

    def __init__(self, cache_file: str = "place_id_cache.json"):
        """
        Initialize the Place ID lookup service

        Args:
            cache_file: Path to JSON file for caching results
        """
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY') or os.getenv('GOOGLE_API_KEY')
        self.cache_file = Path(__file__).parent / cache_file
        self.cache = self._load_cache()
        self.api_calls = 0
        self.cache_hits = 0
        self.last_api_call = 0
        self.min_delay_seconds = 0.1  # 100ms between API calls (10 requests/second max)

    def _load_cache(self) -> Dict:
        """Load cached Place IDs from file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                print("   ⚠️  Could not load cache, starting fresh")
                return {}
        return {}

    def _save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"   ⚠️  Could not save cache: {e}")

    def _generate_cache_key(self, venue_name: str, address: str) -> str:
        """Generate unique cache key for a venue"""
        key = f"{venue_name.lower().strip()}|{address.lower().strip()}"
        return hashlib.md5(key.encode()).hexdigest()

    def _rate_limit(self):
        """Enforce rate limiting between API calls"""
        now = time.time()
        time_since_last_call = now - self.last_api_call

        if time_since_last_call < self.min_delay_seconds:
            sleep_time = self.min_delay_seconds - time_since_last_call
            time.sleep(sleep_time)

        self.last_api_call = time.time()

    def lookup_place_id(self, venue_name: str, address: str,
                       lat: Optional[float] = None,
                       lng: Optional[float] = None) -> Optional[str]:
        """
        Look up Google Place ID for a venue

        Args:
            venue_name: Name of the venue
            address: Street address of the venue
            lat: Optional latitude for better matching
            lng: Optional longitude for better matching

        Returns:
            Google Place ID string, or None if not found
        """
        # Check cache first
        cache_key = self._generate_cache_key(venue_name, address)

        if cache_key in self.cache:
            self.cache_hits += 1
            cached_data = self.cache[cache_key]

            # Return None if we previously failed to find this venue
            if cached_data.get('place_id') is None:
                return None

            return cached_data.get('place_id')

        # No cache hit - make API call
        if not self.api_key:
            print("   ⚠️  No Google API key found, skipping Place ID lookup")
            return None

        self._rate_limit()

        api_result = self._call_places_api(venue_name, address, lat, lng)

        # Cache the result (even if None)
        cache_entry = {
            'place_id': None,
            'venue_name': venue_name,
            'address': address,
            'looked_up_at': datetime.now().isoformat()
        }

        # Add API metadata if available
        if api_result:
            cache_entry.update(api_result)

        self.cache[cache_key] = cache_entry
        self._save_cache()
        self.api_calls += 1

        return cache_entry.get('place_id')

    def _call_places_api(self, venue_name: str, address: str,
                        lat: Optional[float] = None,
                        lng: Optional[float] = None) -> Optional[Dict]:
        """
        Call Google Places API (New) to find Place ID

        Uses the new Places API Text Search endpoint (15x faster than legacy API)
        Returns a dict with place_id and metadata, or None if not found
        """
        # NEW API endpoint (faster!)
        base_url = "https://places.googleapis.com/v1/places:searchText"

        # Build search query - combine venue name and address for best results
        search_query = f"{venue_name}, {address}"

        # Build request body (new API uses POST with JSON)
        request_body = {
            'textQuery': search_query
        }

        # Add location bias if coordinates provided
        if lat is not None and lng is not None:
            request_body['locationBias'] = {
                'circle': {
                    'center': {
                        'latitude': lat,
                        'longitude': lng
                    },
                    'radius': 500.0
                }
            }

        # Set language for better results
        request_body['languageCode'] = 'en'

        # New API uses headers for authentication and field selection
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress,places.location'
        }

        try:
            response = requests.post(base_url, json=request_body, headers=headers, timeout=5)
            response.raise_for_status()

            data = response.json()

            # New API returns 'places' array instead of 'candidates'
            if data.get('places') and len(data['places']) > 0:
                # Return the first (most relevant) result
                place = data['places'][0]

                # Extract place ID (new API uses 'id' instead of 'place_id')
                place_id = place.get('id')

                # Return all metadata for caching
                if place_id:
                    location = place.get('location', {})
                    display_name = place.get('displayName', {})

                    return {
                        'place_id': place_id,
                        'google_name': display_name.get('text') if isinstance(display_name, dict) else str(display_name),
                        'google_address': place.get('formattedAddress'),
                        'google_lat': location.get('latitude'),
                        'google_lng': location.get('longitude')
                    }

                return {'place_id': place_id}

            # New API returns empty array instead of ZERO_RESULTS status
            elif not data.get('places'):
                return None

            else:
                print(f"   ⚠️  Places API (New) unexpected response format")
                return None

        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors (403, 404, etc.)
            if e.response.status_code == 403:
                print(f"   ⚠️  Places API (New) REQUEST_DENIED: {e.response.text}")
                print(f"   💡 Enable Places API (New) at: https://console.cloud.google.com/google/maps-apis/api-list")
            elif e.response.status_code == 400:
                print(f"   ⚠️  Places API (New) BAD_REQUEST: Check request format")
                print(f"      Response: {e.response.text[:200]}")
            else:
                print(f"   ⚠️  Places API (New) HTTP {e.response.status_code}: {e.response.text[:200]}")
            return None

        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  API request failed: {e}")
            return None

    def enrich_venue(self, venue: Dict) -> Dict:
        """
        Enrich a venue dictionary with Place ID

        Args:
            venue: Venue dictionary with name, address, lat, lng

        Returns:
            Updated venue dictionary with place_id field
        """
        venue_name = venue.get('name', '')
        address = venue.get('address', '')
        lat = venue.get('lat')
        lng = venue.get('lng')

        if not venue_name or not address:
            return venue

        place_id = self.lookup_place_id(venue_name, address, lat, lng)

        if place_id:
            venue['place_id'] = place_id

            # Optionally update coordinates if we got better ones from Google
            cache_key = self._generate_cache_key(venue_name, address)
            cached_data = self.cache.get(cache_key, {})

            google_lat = cached_data.get('google_lat')
            google_lng = cached_data.get('google_lng')

            # Only update if we don't have coordinates or Google's are more precise
            if google_lat and google_lng:
                if not lat or not lng:
                    venue['lat'] = google_lat
                    venue['lng'] = google_lng

        return venue

    def get_stats(self) -> Dict:
        """Get statistics about API usage"""
        return {
            'api_calls': self.api_calls,
            'cache_hits': self.cache_hits,
            'cache_size': len(self.cache),
            'api_calls_saved': self.cache_hits
        }

    def print_stats(self):
        """Print statistics about API usage"""
        stats = self.get_stats()
        total_lookups = stats['api_calls'] + stats['cache_hits']

        if total_lookups == 0:
            print("   📍 No Place ID lookups performed")
            return

        cache_rate = (stats['cache_hits'] / total_lookups) * 100 if total_lookups > 0 else 0

        print(f"   📍 Place ID Lookup Stats:")
        print(f"      • Total lookups: {total_lookups}")
        print(f"      • API calls: {stats['api_calls']}")
        print(f"      • Cache hits: {stats['cache_hits']} ({cache_rate:.1f}%)")
        print(f"      • Cache size: {stats['cache_size']} venues")


# Example usage
if __name__ == "__main__":
    # Test the lookup service
    lookup = PlaceIDLookup()

    # Test venue
    test_venue = {
        'name': 'Toronto Public Library - Bloor/Gladstone Branch',
        'address': '1101 Bloor St W',
        'lat': 43.6584,
        'lng': -79.4307
    }

    print("Testing Place ID lookup...")
    print(f"Venue: {test_venue['name']}")
    print(f"Address: {test_venue['address']}")
    print()

    enriched_venue = lookup.enrich_venue(test_venue)

    if enriched_venue.get('place_id'):
        print(f"✅ Found Place ID: {enriched_venue['place_id']}")
    else:
        print("❌ No Place ID found")

    print()
    lookup.print_stats()
