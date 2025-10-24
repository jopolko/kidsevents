#!/usr/bin/env python3
"""
Identify venues with incorrect/default geocoding coordinates.
Default coordinates (43.6532, -79.3832) indicate geocoding failure.
"""

import json
from collections import defaultdict

# Default coordinates used when geocoding fails
DEFAULT_LAT = 43.6532
DEFAULT_LNG = -79.3832
TOLERANCE = 0.0001  # Small tolerance for floating point comparison

def main():
    # Read events
    with open('events.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    events = data.get('events', [])

    # Track unique venues and their coordinates
    venues = {}  # key: (name, address), value: (lat, lng, event_count)
    bad_venues = defaultdict(int)  # venues with default coords

    for event in events:
        venue = event.get('venue', {})
        name = venue.get('name', 'Unknown')
        address = venue.get('address', 'Unknown')
        lat = venue.get('lat')
        lng = venue.get('lng')

        if lat is None or lng is None:
            continue

        venue_key = (name, address)

        # Count events per venue
        if venue_key not in venues:
            venues[venue_key] = {'lat': lat, 'lng': lng, 'count': 0, 'neighborhood': venue.get('neighborhood', 'Unknown')}
        venues[venue_key]['count'] += 1

        # Check if using default coordinates
        if abs(lat - DEFAULT_LAT) < TOLERANCE and abs(lng - DEFAULT_LNG) < TOLERANCE:
            bad_venues[venue_key] += 1

    # Report findings
    print("=" * 80)
    print("GEOCODING ANALYSIS REPORT")
    print("=" * 80)
    print(f"\nTotal unique venues: {len(venues)}")
    print(f"Venues with default/bad coordinates: {len(bad_venues)}")
    print(f"Total events affected: {sum(bad_venues.values())}")
    print(f"\nDefault coordinates: ({DEFAULT_LAT}, {DEFAULT_LNG})")

    # List venues with bad geocoding, sorted by event count
    if bad_venues:
        print("\n" + "=" * 80)
        print("VENUES NEEDING RE-GEOCODING (sorted by event count)")
        print("=" * 80)

        sorted_bad_venues = sorted(bad_venues.items(), key=lambda x: venues[x[0]]['count'], reverse=True)

        for i, (venue_key, event_count) in enumerate(sorted_bad_venues, 1):
            name, address = venue_key
            venue_info = venues[venue_key]
            neighborhood = venue_info['neighborhood']

            print(f"\n{i}. {name}")
            print(f"   Address: {address}")
            print(f"   Neighborhood: {neighborhood}")
            print(f"   Events affected: {event_count}")
            print(f"   Current coords: ({venue_info['lat']}, {venue_info['lng']})")

    # Also check for venues at exactly the same coordinates (potential duplicates)
    print("\n" + "=" * 80)
    print("COORDINATE CLUSTERING ANALYSIS")
    print("=" * 80)

    coord_clusters = defaultdict(list)
    for venue_key, info in venues.items():
        coord_key = (round(info['lat'], 4), round(info['lng'], 4))
        coord_clusters[coord_key].append((venue_key, info['count']))

    # Find clusters with many venues
    large_clusters = [(coords, venue_list) for coords, venue_list in coord_clusters.items()
                     if len(venue_list) >= 5]
    large_clusters.sort(key=lambda x: len(x[1]), reverse=True)

    print(f"\nFound {len(large_clusters)} coordinate clusters with 5+ venues")
    print("(May indicate geocoding issues or legitimate shared locations)\n")

    for i, (coords, venue_list) in enumerate(large_clusters[:10], 1):
        total_events = sum(count for _, count in venue_list)
        print(f"{i}. Coordinates: {coords} - {len(venue_list)} venues, {total_events} events")
        for (name, address), count in sorted(venue_list, key=lambda x: x[1], reverse=True)[:5]:
            print(f"   • {name} ({count} events)")
            if address not in name:
                print(f"     {address}")

    # Save detailed report to file
    output_file = 'geocoding_issues.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("VENUES REQUIRING RE-GEOCODING\n")
        f.write("=" * 80 + "\n\n")

        for i, (venue_key, event_count) in enumerate(sorted_bad_venues, 1):
            name, address = venue_key
            venue_info = venues[venue_key]
            neighborhood = venue_info['neighborhood']

            f.write(f"{i}. {name}\n")
            f.write(f"   Address: {address}\n")
            f.write(f"   Neighborhood: {neighborhood}\n")
            f.write(f"   Events: {event_count}\n")
            f.write(f"   Coords: ({venue_info['lat']}, {venue_info['lng']})\n\n")

    print(f"\n{'=' * 80}")
    print(f"Full report saved to: {output_file}")
    print(f"{'=' * 80}\n")

if __name__ == '__main__':
    main()
