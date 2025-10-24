#!/usr/bin/env python3
"""
Update events.json to mark which events are free vs paid
Based on known sources and event types
"""

import json
from datetime import datetime

def mark_free_status(events):
    """Mark events as free or paid based on source and content"""

    for event in events:
        source = event.get('source', '')
        title = event.get('title', '').lower()
        description = event.get('description', '').lower()
        organized_by = event.get('organized_by', '').lower()

        # Already has is_free flag
        if 'is_free' in event:
            continue

        # TPL events are FREE
        if source == 'TPL':
            event['is_free'] = True
            event['price_note'] = 'FREE - Toronto Public Library'

        # EarlyON Centers are FREE
        elif source == 'EarlyON':
            event['is_free'] = True
            event['price_note'] = 'FREE - EarlyON Drop-In'

        # Parks & Recreation - mostly FREE drop-ins
        elif source == 'ParksRec':
            event['is_free'] = True
            event['price_note'] = 'FREE - City of Toronto Parks & Rec'

        # Museums - check if it's a free day
        elif source == 'Museums':
            if 'free' in title or 'free' in description:
                event['is_free'] = True
                event['price_note'] = 'FREE Admission Day'
            else:
                event['is_free'] = False
                event['price_note'] = 'Regular admission applies'

        # Community events - mostly free
        elif source == 'Community':
            if any(word in title for word in ['market', 'festival', 'park', 'playground']):
                event['is_free'] = True
                event['price_note'] = 'FREE - Community Event'
            else:
                event['is_free'] = None  # Unknown
                event['price_note'] = 'Check website for pricing'

        # Holistic Community - mostly free
        elif source == 'HolisticCommunity':
            if 'free' in title or 'free' in description or 'drop-in' in title:
                event['is_free'] = True
                event['price_note'] = 'FREE - Drop-In Welcome'
            else:
                event['is_free'] = None
                event['price_note'] = 'Check website for pricing'

        # Artisan workshops - some free, some paid
        elif source == 'Artisans':
            event['is_free'] = None  # Mixed - check individual venue
            event['price_note'] = 'Varies by workshop - check website'

        # Targeted Audiences - mixed
        elif source == 'TargetedAudiences':
            if 'free' in title or 'free' in description or 'drop-in' in title:
                event['is_free'] = True
                event['price_note'] = 'FREE'
            elif 'trial' in title or '$10' in description:
                event['is_free'] = False
                event['price_note'] = 'Trial class - small fee'
            else:
                event['is_free'] = None
                event['price_note'] = 'Check website for pricing'

        # Default - unknown
        else:
            if 'is_free' not in event:
                event['is_free'] = None
                event['price_note'] = 'Check website for details'

    return events


def main():
    print("📊 Updating free/paid status for all events...")

    # Load events
    with open('events.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Handle new format with metadata
    if isinstance(data, dict) and 'events' in data:
        events = data['events']
        generated_at = data.get('generated_at')
        total_events = data.get('total_events')
    else:
        events = data
        generated_at = None
        total_events = len(events)

    print(f"   Loaded {len(events)} events")

    # Update free status
    events = mark_free_status(events)

    # Count stats
    free_count = sum(1 for e in events if e.get('is_free') == True)
    paid_count = sum(1 for e in events if e.get('is_free') == False)
    unknown_count = sum(1 for e in events if e.get('is_free') == None)

    print(f"\n   ✅ FREE Events: {free_count}")
    print(f"   💰 Paid Events: {paid_count}")
    print(f"   ❓ Unknown: {unknown_count}")

    # Save updated events with metadata
    output = {
        'generated_at': generated_at if generated_at else datetime.now().isoformat(),
        'total_events': len(events),
        'events': events
    }

    with open('events.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Saved updated events.json")

    # Show breakdown by source
    sources = {}
    for event in events:
        source = event.get('source', 'Unknown')
        is_free = event.get('is_free')

        if source not in sources:
            sources[source] = {'free': 0, 'paid': 0, 'unknown': 0}

        if is_free == True:
            sources[source]['free'] += 1
        elif is_free == False:
            sources[source]['paid'] += 1
        else:
            sources[source]['unknown'] += 1

    print(f"\n📋 Breakdown by Source:")
    for source in sorted(sources.keys()):
        info = sources[source]
        total = info['free'] + info['paid'] + info['unknown']
        print(f"   {source}: {info['free']} free, {info['paid']} paid, {info['unknown']} unknown (total: {total})")


if __name__ == "__main__":
    main()
