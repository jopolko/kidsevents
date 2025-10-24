#!/usr/bin/env python3
"""
Toronto Farmers' Markets Scraper
Major farmers markets with family-friendly activities
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict

class FarmersMarketsScraper:
    def __init__(self):
        """Initialize Toronto farmers markets with kids activities"""
        # Major Toronto farmers markets with regular kids programming
        self.markets = {
            'St. Lawrence Market': {
                'address': '93 Front St E, Toronto',
                'lat': 43.6487, 'lng': -79.3716,
                'website': 'https://www.stlawrencemarket.com/',
                'schedule': {
                    # Tuesday to Saturday
                    2: [('08:00', '18:00')],  # Tuesday
                    3: [('08:00', '18:00')],  # Wednesday
                    4: [('08:00', '18:00')],  # Thursday
                    5: [('08:00', '18:00')],  # Friday
                    6: [('05:00', '17:00')],  # Saturday
                },
                'neighborhood': 'Old Toronto',
                'activities': 'Weekly market with fresh produce, bakery, crafts. Kid-friendly vendors.',
                'note': 'Indoor market, year-round.'
            },
            'Evergreen Brick Works Farmers Market': {
                'address': '550 Bayview Ave, Toronto',
                'lat': 43.6850, 'lng': -79.3661,
                'website': 'https://www.evergreen.ca/evergreen-brick-works/farmers-market/',
                'schedule': {
                    6: [('08:00', '13:00')],  # Saturday only
                },
                'neighborhood': 'Don Valley',
                'activities': 'Farm animals, kids activities, local food vendors, nature programs',
                'note': 'May to October. Family-friendly environment with nature activities.'
            },
            'Dufferin Grove Farmers Market': {
                'address': '875 Dufferin St, Toronto',
                'lat': 43.6554, 'lng': -79.4348,
                'website': 'https://dufferinpark.ca/farmers-market/',
                'schedule': {
                    4: [('15:00', '19:00')],  # Thursday
                },
                'neighborhood': 'Dufferin Grove',
                'activities': 'Playground on-site, local vendors, community atmosphere',
                'note': 'June to October. Family-friendly park setting.'
            },
            'Wychwood Barns Farmers Market': {
                'address': '601 Christie St, Toronto',
                'lat': 43.6761, 'lng': -79.4259,
                'website': 'https://www.artscapewychwood.ca/whats-on/farmers-market',
                'schedule': {
                    6: [('08:00', '12:30')],  # Saturday
                },
                'neighborhood': 'Wychwood',
                'activities': 'Kids activities, live music, local artisans, community hub',
                'note': 'Year-round indoor/outdoor market.'
            },
            'Leslieville Farmers Market': {
                'address': '1350 Queen St E, Toronto',
                'lat': 43.6658, 'lng': -79.3317,
                'website': 'https://www.leslievillefarmersmarket.com/',
                'schedule': {
                    0: [('09:00', '13:00')],  # Sunday
                },
                'neighborhood': 'Leslieville',
                'activities': 'Family-friendly, local vendors, kids activities',
                'note': 'May to October.'
            },
            'Sorauren Farmers Market': {
                'address': 'Sorauren Ave & Wabash Ave, Toronto',
                'lat': 43.6452, 'lng': -79.4414,
                'website': 'https://www.soraurenmarket.com/',
                'schedule': {
                    1: [('15:00', '19:00')],  # Monday
                },
                'neighborhood': 'Roncesvalles',
                'activities': 'Playground adjacent, kids activities, community gathering',
                'note': 'May to October. Park setting with playground.'
            },
            'Nathan Phillips Square Farmers Market': {
                'address': '100 Queen St W, Toronto',
                'lat': 43.6534, 'lng': -79.3839,
                'website': 'https://www.toronto.ca/explore-enjoy/recreation/skating-winter-activities/nathan-phillips-square/',
                'schedule': {
                    3: [('08:00', '14:00')],  # Wednesday
                },
                'neighborhood': 'Downtown',
                'activities': 'Central location, local vendors, public square activities',
                'note': 'May to October.'
            },
            'Withrow Park Farmers Market': {
                'address': '725 Logan Ave, Toronto',
                'lat': 43.6789, 'lng': -79.3445,
                'website': 'https://www.withrowmarket.com/',
                'schedule': {
                    6: [('09:00', '13:00')],  # Saturday
                },
                'neighborhood': 'Riverdale',
                'activities': 'Large playground on-site, kids activities, community atmosphere',
                'note': 'May to October. Adjacent to major playground.'
            },
            'Bloor-Borden Farmers Market': {
                'address': 'Bloor St W & Borden St, Toronto',
                'lat': 43.6665, 'lng': -79.4110,
                'website': 'https://bloorborden.com/',
                'schedule': {
                    6: [('09:00', '13:00')],  # Saturday
                },
                'neighborhood': 'Annex',
                'activities': 'Local vendors, community market, family-friendly',
                'note': 'May to October.'
            },
        }

    def fetch_events(self, days_ahead: int = 28) -> List[Dict]:
        """Generate farmers market events based on their schedules"""
        print("🥕 Fetching from Toronto Farmers' Markets...")

        events = []
        today = datetime.now()
        end_date = today + timedelta(days=days_ahead)

        # Determine market season (May-Oct for most outdoor markets)
        current_month = today.month

        for market_name, market_info in self.markets.items():
            # Check if market is seasonal
            is_seasonal = 'May to October' in market_info['note']
            is_year_round = 'year-round' in market_info['note'].lower() or 'Year-round' in market_info['note']

            # Skip seasonal markets if outside season (May=5, Oct=10)
            if is_seasonal and not is_year_round:
                if current_month < 5 or current_month > 10:
                    continue

            current = today
            while current <= end_date:
                weekday = current.weekday()

                # Check if market operates on this weekday
                if weekday in market_info['schedule']:
                    for time_slot in market_info['schedule'][weekday]:
                        start_time, end_time = time_slot

                        event = {
                            "title": f"{market_name}",
                            "description": f"FREE farmers market! {market_info['activities']} Support local farmers and makers. {market_info['note']}",
                            "category": "Learning",
                            "icon": "🥕",
                            "date": current.strftime('%Y-%m-%d'),
                            "start_time": start_time,
                            "end_time": end_time,
                            "venue": {
                                "name": market_name,
                                "address": market_info['address'],
                                "neighborhood": market_info['neighborhood'],
                                "lat": market_info['lat'],
                                "lng": market_info['lng']
                            },
                            "age_groups": ["All Ages"],
                            "indoor_outdoor": "Outdoor" if is_seasonal else "Indoor",
                            "organized_by": "Community Farmers Market",
                            "website": market_info['website'],
                            "source": "FarmersMarkets",
                            "scraped_at": datetime.now().isoformat(),
                            "is_free": True,
                        }
                        events.append(event)

                current += timedelta(days=1)

        print(f"   ✅ Generated {len(events)} farmers market events")
        return events


def main():
    scraper = FarmersMarketsScraper()
    events = scraper.fetch_events(days_ahead=28)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    with open('farmers_markets_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to farmers_markets_events.json")


if __name__ == "__main__":
    main()
