#!/usr/bin/env python3
"""
Adventure Playgrounds Scraper
Top 10+ FREE adventure playgrounds in Toronto and GTA
These are outdoor playgrounds with unique, nature-inspired, or themed play features
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict

class AdventurePlaygroundsScraper:
    def __init__(self):
        # Top FREE adventure playgrounds in Toronto/GTA
        self.playgrounds = {
            'Jamie Bell Adventure Playground': {
                'address': '1873 Bloor St W, High Park',
                'lat': 43.6536, 'lng': -79.4641,
                'website': 'https://www.toronto.ca/explore-enjoy/parks-gardens-beaches/high-park/',
                'features': 'Castle-themed wooden structures, possibly largest outdoor playground in Ontario, medieval village design, rebuilt 2012',
                'category': 'Castle & Medieval',
                'neighborhood': 'High Park',
                'age_range': 'All Ages',
                'accessibility': 'Partially accessible',
                'note': 'Community-built by 3000+ volunteers. Located near Duck Pond in High Park.'
            },
            'Biidaasige Park': {
                'address': '51 Commissioners St, Port Lands',
                'lat': 43.6463, 'lng': -79.3497,
                'website': 'https://www.toronto.ca/explore-enjoy/parks-recreation/places-spaces/beaches-gardens-attractions/biidaasige-park/',
                'features': 'Woodland Scramble, Badlands with water play, Snowy Owl Theatre amphitheater, 33ft tall Raccoon slide, Indigenous-themed',
                'category': 'Nature & Indigenous',
                'neighborhood': 'Port Lands',
                'age_range': 'All Ages',
                'accessibility': 'Fully accessible',
                'note': 'Means "sunlight shining toward us" in Anishinaabemowin. Opened 2025. Multiple themed play zones.'
            },
            'Corktown Common': {
                'address': '155 Bayview Ave, West Don Lands',
                'lat': 43.6541, 'lng': -79.3524,
                'website': 'https://www.waterfrontoronto.ca/our-projects/corktown-common',
                'features': 'Natural play area, stumps to climb, sandbox with water tap, innovative splash pad, nature-inspired design',
                'category': 'Nature Play',
                'neighborhood': 'West Don Lands',
                'age_range': 'All Ages',
                'accessibility': 'Fully accessible',
                'note': 'Urban park with nature play elements. Water play, swings, slides. Well-spread playground.'
            },
            'Neshama Playground (Oriole Park)': {
                'address': '201 Oriole Pkwy',
                'lat': 43.7014, 'lng': -79.3980,
                'website': 'https://www.toronto.ca/explore-enjoy/parks-recreation/places-spaces/parks-and-recreation-facilities/location/?id=1394',
                'features': 'First fully accessible playground in Toronto! Rubber surfacing, ramped structures, Braille panels, sensory musical features, enclosed climbing merry-go-round',
                'category': 'Accessible & Sensory',
                'neighborhood': 'North Toronto',
                'age_range': 'All Ages',
                'accessibility': 'Fully accessible - first of its kind',
                'note': 'Canada\'s first fully accessible playground! Wheelchair-friendly, autism-friendly sensory toys, wide ramps.'
            },
            'Trinity Bellwoods Park': {
                'address': '790 Queen St W',
                'lat': 43.6475, 'lng': -79.4166,
                'website': 'https://www.toronto.ca/explore-enjoy/parks-recreation/places-spaces/parks-and-recreation-facilities/location/?id=241',
                'features': 'Roped spider web climbing section, rings, stepping stones, twisted monkey bars, varying adventure levels',
                'category': 'Climbing & Adventure',
                'neighborhood': 'Queen West',
                'age_range': '3-12',
                'accessibility': 'Partially accessible',
                'note': 'Trendy Queen West park. Wading pool in summer. Great for climbers!'
            },
            'Dufferin Grove Park': {
                'address': '1240 Bloor St W',
                'lat': 43.6563, 'lng': -79.4348,
                'website': 'https://www.toronto.ca/explore-enjoy/parks-recreation/places-spaces/parks-and-recreation-facilities/location/?id=87',
                'features': 'Wooden structures blend into natural habitat, massive sandpit with digging tools, water hose for dam-building',
                'category': 'Nature & Sand Play',
                'neighborhood': 'Dufferin Grove',
                'age_range': 'All Ages',
                'accessibility': 'Partially accessible',
                'note': 'Dream playground! Shady, natural wood structures. Kids love building dams and bridges in sandpit.'
            },
            'Withrow Park': {
                'address': '725 Logan Ave, Riverdale',
                'lat': 43.6789, 'lng': -79.3445,
                'website': 'https://www.toronto.ca/explore-enjoy/parks-recreation/places-spaces/parks-and-recreation-facilities/location/?id=306',
                'features': 'Two playgrounds, hexagonal climbing blocks, spinning rides, tons of swings, wading pool, 8 hectares',
                'category': 'Multi-playground Park',
                'neighborhood': 'Riverdale',
                'age_range': 'All Ages',
                'accessibility': 'Partially accessible',
                'note': 'Huge 8-hectare park. Multiple playgrounds for different ages. Sandboxes, wading pool.'
            },
            'Cherry Beach Sports Fields Playground': {
                'address': '115 Unwin Ave',
                'lat': 43.6357, 'lng': -79.3403,
                'website': 'https://www.toronto.ca/explore-enjoy/parks-gardens-beaches/beaches/',
                'features': 'Large wooden pirate ship with two steering wheels, smaller ship with sandbox, soft flooring',
                'category': 'Pirate & Nautical',
                'neighborhood': 'Port Lands',
                'age_range': '3-12',
                'accessibility': 'Partially accessible',
                'note': 'Famous pirate ship playground! Beside soccer fields. Easy to spot from parking.'
            },
            'Grange Park': {
                'address': 'Beverley St & Grange St (behind AGO)',
                'lat': 43.6531, 'lng': -79.3920,
                'website': 'https://grangeparktoronto.ca/',
                'features': 'Art-inspired playground: spilled paint can, crumpled paper, artist\'s palette, charcoal pencil tower, paint tube sculpture',
                'category': 'Art & Creative',
                'neighborhood': 'Downtown',
                'age_range': 'All Ages',
                'accessibility': 'Fully accessible',
                'note': 'Behind Art Gallery of Ontario! Artist studio themed. Reopened 2017. Unique climbing structures.'
            },
            'Kew Gardens': {
                'address': '2075 Queen St E',
                'lat': 43.6687, 'lng': -79.2988,
                'website': 'https://www.toronto.ca/explore-enjoy/parks-recreation/places-spaces/parks-and-recreation-facilities/location/?id=107',
                'features': 'Castle-themed wooden structure, tall tower with slides, four-person spring teeter-totter, wading pool',
                'category': 'Castle & Beach',
                'neighborhood': 'The Beaches',
                'age_range': 'All Ages',
                'accessibility': 'Partially accessible',
                'note': 'Stretches from Queen St to Lake Ontario. Fenced playground. Classic swings, slides, 3 climbing structures.'
            },
            'Marie Curtis Park': {
                'address': '2 Cheswick Dr, Etobicoke',
                'lat': 43.5884, 'lng': -79.5442,
                'website': 'https://www.toronto.ca/explore-enjoy/parks-gardens-beaches/beaches/',
                'features': 'Waterfront playground, wading pool, beach (supervised Jul-Aug), splash pad, large surrounding park',
                'category': 'Beach & Waterfront',
                'neighborhood': 'Long Branch',
                'age_range': 'All Ages',
                'accessibility': 'Partially accessible',
                'note': 'Along Etobicoke Creek. Near Long Branch GO. Beach access! Great for full day trips.'
            },
            'Chinguacousy Park': {
                'address': '9050 Bramalea Rd, Brampton',
                'lat': 43.7169, 'lng': -79.7580,
                'website': 'https://www.brampton.ca/EN/residents/Recreation/Community-Centres/Chinguacousy-Park',
                'features': 'Splash pad, petting zoo, mini golf, pond, multiple playgrounds, skiing in winter, year-round activities',
                'category': 'Multi-Activity Park',
                'neighborhood': 'Brampton',
                'age_range': 'Toddlers to Teens',
                'accessibility': 'Fully accessible',
                'note': 'One of most comprehensive park activity lists! Toddlers to teens. Some activities have fees.'
            },
            'PlayPark (Waterfront)': {
                'address': 'Queens Quay E & Lower Sherbourne (Under Development)',
                'lat': 43.6426, 'lng': -79.3635,
                'website': 'https://www.waterfrontoronto.ca/our-projects/PlayPark',
                'features': '3 acres accessible play, nature-themed zones with trees and stones, trails and scrambles, foster love of outdoors',
                'category': 'Nature Play',
                'neighborhood': 'Waterfront',
                'age_range': 'All Ages',
                'accessibility': 'Fully accessible when complete',
                'note': 'FREE forever! Major waterfront playground. Owned by City of Toronto in perpetuity. Opening soon!'
            },
        }

    def fetch_events(self, days_ahead: int = 7) -> List[Dict]:
        """Generate daily 'open' events for adventure playgrounds"""
        print("🏰 Generating adventure playground availability...")

        events = []
        today = datetime.now()

        for playground_name, pg_info in self.playgrounds.items():
            current = today
            end_date = today + timedelta(days=days_ahead)

            while current <= end_date:
                # Playgrounds open dawn to dusk (approximate)
                is_summer = current.month >= 5 and current.month <= 9
                hours = ('08:00', '20:00') if is_summer else ('08:00', '18:00')

                event = {
                    "title": f"{playground_name} - Open",
                    "description": f"FREE adventure playground! {pg_info['features']}. {pg_info.get('note', '')}",
                    "category": "Play",
                    "icon": "🏰",
                    "date": current.strftime('%Y-%m-%d'),
                    "start_time": hours[0],
                    "end_time": hours[1],
                    "venue": {
                        "name": playground_name,
                        "address": pg_info['address'],
                        "neighborhood": pg_info['neighborhood'],
                        "lat": pg_info['lat'],
                        "lng": pg_info['lng'],
                        "phone": "416-338-4386" if 'Brampton' not in pg_info['neighborhood'] else "311"
                    },
                    "age_groups": [pg_info.get('age_range', 'All Ages')],
                    "indoor_outdoor": "Outdoor",
                    "organized_by": "City of Toronto Parks" if 'Brampton' not in pg_info['neighborhood'] else "City of Brampton",
                    "website": pg_info['website'],
                    "source": "AdventurePlaygrounds",
                    "scraped_at": datetime.now().isoformat(),
                    "is_free": True,
                    "playground_category": pg_info['category'],
                    "accessibility": pg_info['accessibility']
                }
                events.append(event)

                current += timedelta(days=1)

        print(f"   ✅ Generated {len(events)} adventure playground availability events")
        return events


def main():
    scraper = AdventurePlaygroundsScraper()
    events = scraper.fetch_events(days_ahead=7)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")
    print(f"   Unique playgrounds: {len(scraper.playgrounds)}")

    with open('adventure_playgrounds_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to adventure_playgrounds_events.json")


if __name__ == "__main__":
    main()
