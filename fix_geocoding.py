#!/usr/bin/env python3
"""
Fix geocoding for venues with incorrect/default coordinates.
Uses Google Geocoding API to get accurate coordinates.
"""

import json
import os
import time
import requests
from collections import defaultdict

# Default coordinates that indicate geocoding failure
DEFAULT_LAT = 43.6532
DEFAULT_LNG = -79.3832
TOLERANCE = 0.0001

# Read Google API key from environment
def get_api_key():
    """Read Google API key from .env file"""
    api_key = None
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.strip().startswith('GOOGLE_API_KEY'):
                    api_key = line.split('=', 1)[1].strip()
                    break

    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file")

    return api_key

def geocode_address(address, api_key=None):
    """
    Geocode an address using Nominatim (OpenStreetMap) API
    Returns (lat, lng) tuple or None if failed
    """
    # Build the full address
    if 'Toronto' not in address and 'ON' not in address:
        full_address = f"{address}, Toronto, ON, Canada"
    else:
        full_address = address

    # Use Nominatim (OpenStreetMap) - free and no API key required
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': full_address,
        'format': 'json',
        'limit': 1,
        'countrycodes': 'ca',
        'bounded': 1,
        'viewbox': '-79.788,43.465,-79.115,43.855'  # Toronto bounding box
    }

    headers = {
        'User-Agent': 'KidsEvents-Toronto/1.0 (Geocoding Fix Script)'
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if len(data) > 0:
            lat = float(data[0]['lat'])
            lng = float(data[0]['lon'])
            return (lat, lng)
        else:
            print(f"  ⚠️  Geocoding failed: No results - {full_address}")
            return None

    except Exception as e:
        print(f"  ❌ Error geocoding {full_address}: {e}")
        return None

def main():
    print("=" * 80)
    print("FIXING GEOCODING ISSUES")
    print("=" * 80)
    print("\n📡 Using Nominatim (OpenStreetMap) API for geocoding")
    print("⚠️  Rate limited to 1 request per second per OSM usage policy")

    # Read events
    print("\n📖 Loading events.json...")
    with open('events.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    events = data.get('events', [])
    print(f"✓ Loaded {len(events)} events")

    # Find unique venues with bad coordinates
    venues_to_fix = {}  # key: (name, address), value: list of event indices

    for i, event in enumerate(events):
        venue = event.get('venue', {})
        lat = venue.get('lat')
        lng = venue.get('lng')

        if lat is None or lng is None:
            continue

        # Check if using default coordinates
        if abs(lat - DEFAULT_LAT) < TOLERANCE and abs(lng - DEFAULT_LNG) < TOLERANCE:
            name = venue.get('name', 'Unknown')
            address = venue.get('address', 'Unknown')
            venue_key = (name, address)

            if venue_key not in venues_to_fix:
                venues_to_fix[venue_key] = []
            venues_to_fix[venue_key].append(i)

    print(f"\n🔍 Found {len(venues_to_fix)} unique venues to re-geocode")
    print(f"📍 Total events affected: {sum(len(v) for v in venues_to_fix.values())}")

    # Ask for confirmation
    response = input(f"\n⚠️  This will make {len(venues_to_fix)} API calls to Google. Continue? [y/N]: ")
    if response.lower() != 'y':
        print("❌ Cancelled")
        return

    # Geocode each unique venue
    fixed_count = 0
    failed_count = 0
    skipped_count = 0

    print(f"\n{'=' * 80}")
    print("GEOCODING VENUES")
    print(f"{'=' * 80}\n")

    for i, (venue_key, event_indices) in enumerate(venues_to_fix.items(), 1):
        name, address = venue_key
        event_count = len(event_indices)

        print(f"{i}/{len(venues_to_fix)}: {name}")
        print(f"  Address: {address}")
        print(f"  Events: {event_count}")

        # Skip venues with vague addresses
        vague_indicators = ['Multiple', 'Various', 'All Branches', 'City-Wide', 'Citywide',
                           'Downtown Toronto', 'Toronto', 'Select', 'Community Centers']
        if any(indicator in address or indicator in name for indicator in vague_indicators):
            print(f"  ⏭️  Skipping (vague location)")
            skipped_count += 1
            continue

        # Try to geocode
        result = geocode_address(address)

        if result:
            lat, lng = result
            print(f"  ✅ Success: ({lat:.6f}, {lng:.6f})")

            # Update all events for this venue
            for event_idx in event_indices:
                events[event_idx]['venue']['lat'] = lat
                events[event_idx]['venue']['lng'] = lng

            fixed_count += 1
        else:
            failed_count += 1

        # Rate limiting: 1 request per second for Nominatim
        if i < len(venues_to_fix):
            time.sleep(1.0)

    # Save updated events
    print(f"\n{'=' * 80}")
    print("SAVING RESULTS")
    print(f"{'=' * 80}\n")

    output_file = 'events_fixed.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Updated events saved to: {output_file}")

    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}\n")
    print(f"Venues processed: {len(venues_to_fix)}")
    print(f"  ✅ Successfully geocoded: {fixed_count}")
    print(f"  ❌ Failed to geocode: {failed_count}")
    print(f"  ⏭️  Skipped (vague locations): {skipped_count}")
    print(f"\nEvents updated: {sum(len(venues_to_fix[v]) for v in list(venues_to_fix.keys())[:fixed_count])}")

    if fixed_count > 0:
        print(f"\n💡 Next steps:")
        print(f"  1. Review events_fixed.json")
        print(f"  2. Backup current events.json: cp events.json events_backup.json")
        print(f"  3. Replace with fixed version: mv events_fixed.json events.json")
        print(f"  4. Test the website to verify distances are correct")

if __name__ == '__main__':
    main()
