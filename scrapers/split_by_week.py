#!/usr/bin/env python3
"""
Split events.json into weekly chunks for faster initial page load
Generates: events_week1.json, events_week2.json, events_week3.json, events_week4.json
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

def split_events_by_week():
    """Split events into weekly JSON files"""

    # Read the main events file
    events_path = Path(__file__).parent / 'events.json'

    if not events_path.exists():
        print("❌ events.json not found")
        return

    with open(events_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    events = data.get('events', [])

    if not events:
        print("❌ No events found in events.json")
        return

    # Get current date
    today = datetime.now().date()

    # Define week boundaries
    week_1_end = today + timedelta(days=7)
    week_2_end = today + timedelta(days=14)
    week_3_end = today + timedelta(days=21)
    week_4_end = today + timedelta(days=28)

    # Split events into weeks
    week_1 = []
    week_2 = []
    week_3 = []
    week_4 = []

    for event in events:
        try:
            event_date = datetime.strptime(event['date'], '%Y-%m-%d').date()

            # Week 1: today through +7 days
            if today <= event_date < week_1_end:
                week_1.append(event)
            # Week 2: +7 through +14 days
            elif week_1_end <= event_date < week_2_end:
                week_2.append(event)
            # Week 3: +14 through +21 days
            elif week_2_end <= event_date < week_3_end:
                week_3.append(event)
            # Week 4: +21 through +28 days
            elif week_3_end <= event_date < week_4_end:
                week_4.append(event)
        except:
            continue

    # Save weekly files
    parent_dir = Path(__file__).parent.parent

    weeks = [
        ('events_week1.json', week_1, "Week 1"),
        ('events_week2.json', week_2, "Week 2"),
        ('events_week3.json', week_3, "Week 3"),
        ('events_week4.json', week_4, "Week 4")
    ]

    for filename, week_events, week_name in weeks:
        output = {
            'generated_at': datetime.now().isoformat(),
            'total_events': len(week_events),
            'week': week_name,
            'events': week_events
        }

        # Save to scrapers directory (compact JSON for faster loading)
        with open(Path(__file__).parent / filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, separators=(',', ':'))

        # Also save to parent directory for web access (compact JSON for faster loading)
        with open(parent_dir / filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, separators=(',', ':'))

        print(f"✅ {week_name}: {len(week_events)} events -> {filename}")

    print(f"\n📊 Total: {len(week_1) + len(week_2) + len(week_3) + len(week_4)} events split into 4 weeks")


if __name__ == "__main__":
    split_events_by_week()
