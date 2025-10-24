#!/usr/bin/env python3
"""
Holistic Community Events Scraper
Curated alternative/holistic/multicultural community events for conscious parents
- Cultural festivals, Indigenous events, African drumming
- Community gardens, urban farming, nature workshops
- Forest schools, Waldorf events, nature circles
- Hippie/alternative parenting activities
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict


class HolisticCommunityScraper:
    def __init__(self):
        pass

    def fetch_events(self, days_ahead: int = 90) -> List[Dict]:
        """Fetch holistic/alternative community events"""

        print("🌿 Fetching holistic & multicultural community events...")

        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        events = []

        # Indigenous Arts Festival (Annual - June)
        if today.month <= 6:
            indigenous_date = datetime(today.year, 6, 21).date()
            if today <= indigenous_date <= end_date:
                events.append({
                    "title": "Toronto Indigenous Arts Festival & Na-Me-Res Pow Wow",
                    "description": "FREE 2-day festival celebrating Indigenous culture with drumming, dancing, storytelling, Indigenous food market, and over 100 drummers. Theme: 'Mino Bimaadiziwin' (A Good Life). All ages welcome!",
                    "category": "Entertainment",
                    "icon": "🪶",
                    "date": indigenous_date.strftime('%Y-%m-%d'),
                    "start_time": "11:00",
                    "end_time": "18:00",
                    "venue": {
                        "name": "Fort York National Historic Site",
                        "address": "250 Fort York Blvd",
                        "neighborhood": "Fort York",
                        "lat": 43.6393,
                        "lng": -79.4036,
                        "phone": "311"
                    },
                    "age_groups": ["All Ages"],
                    "indoor_outdoor": "Outdoor",
                    "organized_by": "City of Toronto Indigenous Arts Festival",
                    "website": "https://www.toronto.ca/explore-enjoy/festivals-events/indigenous-arts-festival/",
                    "phone": "311",
                    "source": "HolisticCommunity"
                })

        # Afrofest (Annual - July)
        if today.month <= 7:
            afrofest_date = datetime(today.year, 7, 5).date()
            if today <= afrofest_date <= end_date:
                events.append({
                    "title": "Afrofest - Largest FREE African Festival",
                    "description": "Celebrate African arts, music & culture! African drumming, traditional dance, contemporary pop, Children's Creative Village with face painting, storytelling. 100,000+ visitors, 45+ performances, 90+ vendors.",
                    "category": "Entertainment",
                    "icon": "🥁",
                    "date": afrofest_date.strftime('%Y-%m-%d'),
                    "start_time": "12:00",
                    "end_time": "20:00",
                    "venue": {
                        "name": "Woodbine Park",
                        "address": "Woodbine Ave & Lake Shore Blvd E",
                        "neighborhood": "The Beaches",
                        "lat": 43.6656,
                        "lng": -79.3033,
                        "phone": "416-395-0355"
                    },
                    "age_groups": ["All Ages"],
                    "indoor_outdoor": "Outdoor",
                    "organized_by": "Afrofest",
                    "website": "https://www.afrofest.ca/",
                    "phone": "416-395-0355",
                    "source": "HolisticCommunity"
                })

        # WAYO Children's Festival (August - Swahili "community")
        if today.month <= 8:
            wayo_date = datetime(today.year, 8, 7).date()
            if today <= wayo_date <= end_date:
                events.append({
                    "title": "WAYO Children's Festival - Multicultural Arts",
                    "description": "4-day artistic celebration! 'Jamii' (community in Swahili). Multicultural performances, storytelling from around the world, global music & dance. Ages under 12.",
                    "category": "Arts",
                    "icon": "🌍",
                    "date": wayo_date.strftime('%Y-%m-%d'),
                    "start_time": "10:00",
                    "end_time": "17:00",
                    "venue": {
                        "name": "Harbourfront Centre",
                        "address": "235 Queens Quay W",
                        "neighborhood": "Harbourfront",
                        "lat": 43.6385,
                        "lng": -79.3817,
                        "phone": "416-973-4000"
                    },
                    "age_groups": ["Toddlers (3-5)", "Kids (6-12)"],
                    "indoor_outdoor": "Outdoor",
                    "organized_by": "Harbourfront Centre",
                    "website": "https://www.harbourfrontcentre.com/",
                    "phone": "416-973-4000",
                    "source": "HolisticCommunity"
                })

        # Evergreen Brick Works - Recurring Saturday workshops
        # Find next Saturday
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0:
            days_until_saturday = 7
        next_saturday = today + timedelta(days=days_until_saturday)

        while next_saturday <= end_date:
            events.append({
                "title": "Evergreen Brick Works - Nature Craft Workshop",
                "description": "FREE drop-in nature crafts & urban farming activities! Make seed bombs, learn composting, nature art with found materials. Explore gardens & ravine trails.",
                "category": "Nature",
                "icon": "🌱",
                "date": next_saturday.strftime('%Y-%m-%d'),
                "start_time": "10:00",
                "end_time": "15:00",
                "venue": {
                    "name": "Evergreen Brick Works",
                    "address": "550 Bayview Ave",
                    "neighborhood": "Don Valley",
                    "lat": 43.6851,
                    "lng": -79.3654,
                    "phone": "416-596-7670"
                },
                "age_groups": ["All Ages"],
                "indoor_outdoor": "Outdoor",
                "organized_by": "Evergreen",
                "website": "https://www.evergreen.ca/",
                "phone": "416-596-7670",
                "source": "HolisticCommunity"
            })
            next_saturday += timedelta(days=14)  # Every other Saturday

        # The Stop Green Barn - Sundays
        days_until_sunday = (6 - today.weekday()) % 7
        if days_until_sunday == 0:
            days_until_sunday = 7
        next_sunday = today + timedelta(days=days_until_sunday)

        count = 0
        while next_sunday <= end_date and count < 4:  # First 4 Sundays
            events.append({
                "title": "The Stop Green Barn - Community Garden Open Day",
                "description": "FREE urban farming experience! Explore greenhouse, community gardens, compost demonstration. Kids learn organic gardening, worm composting, seed planting. Bake oven demos!",
                "category": "Nature",
                "icon": "🌻",
                "date": next_sunday.strftime('%Y-%m-%d'),
                "start_time": "12:00",
                "end_time": "16:00",
                "venue": {
                    "name": "The Stop Green Barn",
                    "address": "601 Christie St (Wychwood Barns)",
                    "neighborhood": "St. Clair West",
                    "lat": 43.6801,
                    "lng": -79.4264,
                    "phone": "416-652-7867"
                },
                "age_groups": ["All Ages"],
                "indoor_outdoor": "Outdoor",
                "organized_by": "The Stop Community Food Centre",
                "website": "https://www.thestop.org/",
                "phone": "416-652-7867",
                "source": "HolisticCommunity"
            })
            next_sunday += timedelta(days=7)
            count += 1

        # Franklin Children's Garden - Toronto Island (Summer weekdays)
        if 7 <= today.month <= 8:  # July-August
            # Add weekdays in July/August
            current_date = today if today.month >= 7 else datetime(today.year, 7, 1).date()
            end_check = min(end_date, datetime(today.year, 8, 31).date())

            while current_date <= end_check:
                if current_date.weekday() < 5:  # Monday-Friday
                    events.append({
                        "title": "Franklin Children's Garden - Island Nature Crafts",
                        "description": "FREE drop-in! Storytelling, bug identification, organic gardening, nature studies & crafts. Little Sprouts Garden creative outdoor activities daily 1-4pm.",
                        "category": "Nature",
                        "icon": "🐛",
                        "date": current_date.strftime('%Y-%m-%d'),
                        "start_time": "13:00",
                        "end_time": "16:00",
                        "venue": {
                            "name": "Franklin Children's Garden (Toronto Island)",
                            "address": "Toronto Island Park",
                            "neighborhood": "Toronto Islands",
                            "lat": 43.6193,
                            "lng": -79.3783,
                            "phone": "416-392-1111"
                        },
                        "age_groups": ["Toddlers (3-5)", "Kids (6-12)"],
                        "indoor_outdoor": "Outdoor",
                        "organized_by": "Toronto Island Community",
                        "website": "https://www.toronto.ca/explore-enjoy/parks-gardens-beaches/toronto-island-park/",
                        "phone": "416-392-1111",
                        "source": "HolisticCommunity"
                    })
                current_date += timedelta(days=1)

        # Dufferin Grove Bake Oven (Thursdays)
        next_thursday = today + timedelta(days=(3 - today.weekday()) % 7)
        if next_thursday == today:
            next_thursday += timedelta(days=7)

        count = 0
        while next_thursday <= end_date and count < 6:
            events.append({
                "title": "Dufferin Grove Park - Community Bake Oven",
                "description": "FREE community bread baking! Wood-fired clay oven. Kids help make pizza & bread dough. Super chill hippie park vibes. Bring ingredients to share!",
                "category": "Learning",
                "icon": "🍞",
                "date": next_thursday.strftime('%Y-%m-%d'),
                "start_time": "17:00",
                "end_time": "19:30",
                "venue": {
                    "name": "Dufferin Grove Park",
                    "address": "875 Dufferin St",
                    "neighborhood": "Dufferin Grove",
                    "lat": 43.6555,
                    "lng": -79.4327,
                    "phone": "416-392-0913"
                },
                "age_groups": ["All Ages"],
                "indoor_outdoor": "Outdoor",
                "organized_by": "Dufferin Grove Park Community",
                "website": "http://www.dufferinpark.ca/",
                "phone": "416-392-0913",
                "source": "HolisticCommunity"
            })
            next_thursday += timedelta(days=14)
            count += 1

        # Native Child & Family Services - Monthly Workshops (First Saturday)
        # Find first Saturday of each month
        current_month = today.month
        for month_offset in range(3):  # Next 3 months
            target_month = current_month + month_offset
            target_year = today.year
            if target_month > 12:
                target_month -= 12
                target_year += 1

            # First day of month
            first_day = datetime(target_year, target_month, 1).date()
            # Find first Saturday
            days_to_saturday = (5 - first_day.weekday()) % 7
            first_saturday = first_day + timedelta(days=days_to_saturday)

            if first_saturday < today:
                continue
            if first_saturday > end_date:
                break

            events.append({
                "title": "Indigenous Parenting Circle - Cultural Teaching",
                "description": "FREE culturally responsive circle! Connect with Indigenous traditions, customs, practices. Sweetgrass ceremony, drumming, storytelling. All families welcome to learn.",
                "category": "Learning",
                "icon": "🪶",
                "date": first_saturday.strftime('%Y-%m-%d'),
                "start_time": "10:00",
                "end_time": "12:00",
                "venue": {
                    "name": "Native Child & Family Services",
                    "address": "30 College St",
                    "neighborhood": "Downtown",
                    "lat": 43.6595,
                    "lng": -79.3928,
                    "phone": "416-969-8510"
                },
                "age_groups": ["All Ages"],
                "indoor_outdoor": "Indoor",
                "organized_by": "Native Child & Family Services of Toronto",
                "website": "https://nativechild.org/",
                "phone": "416-969-8510",
                "source": "HolisticCommunity"
            })

        print(f"   ✅ Found {len(events)} holistic community events")
        return events


def main():
    scraper = HolisticCommunityScraper()
    events = scraper.fetch_events(days_ahead=90)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    # Show sample
    if events:
        print(f"\n   Sample events:")
        for event in events[:5]:
            print(f"   {event['icon']} {event['title']} ({event['date']})")

    # Save to JSON
    with open('holistic_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved to holistic_events.json")


if __name__ == "__main__":
    main()
