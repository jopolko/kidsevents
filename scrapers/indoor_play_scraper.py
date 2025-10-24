#!/usr/bin/env python3
"""
Indoor Play Centres & Trampoline Parks Scraper
Generates operating hours and special events for Toronto/GTA indoor play facilities
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict

class IndoorPlayScraper:
    def __init__(self):
        # Indoor play centres, trampoline parks, and similar venues
        self.venues = {
            # Original venues from user
            'Happy Kingdom': {
                'address': '1980 St Clair Ave W',
                'lat': 43.6745, 'lng': -79.4511,
                'website': 'https://www.happykingdom.ca/',
                'type': 'Indoor Playground',
                'hours': {'weekday': ('11:00', '19:00'), 'weekend': ('11:00', '19:00')},
                'note': 'Weekday $13.99, Weekend $16.99 (first child)'
            },
            'Air Riderz Vaughan': {
                'address': '570 Applewood Cres Unit 3, Vaughan',
                'lat': 43.7909, 'lng': -79.5294,
                'website': 'https://www.airriderz.com/vaughan/',
                'type': 'Trampoline Park',
                'hours': {'weekday': ('10:00', '20:00'), 'weekend': ('10:00', '21:00')},
                'note': '15,000 sq ft trampoline park, ninja warrior course'
            },
            'Tiny Town Vaughan': {
                'address': '5875 Hwy 7 Unit 12, Woodbridge',
                'lat': 43.7691, 'lng': -79.5806,
                'website': 'https://tinytownvaughan.ca/',
                'type': 'Indoor Playground',
                'hours': {'weekday': ('10:00', '18:00'), 'weekend': ('10:00', '19:00')},
                'note': '9 themed play rooms - doctor, salon, fire station, pizzeria'
            },
            'Neshama Playground': {
                'address': '4600 Bathurst St, North York',
                'lat': 43.7611, 'lng': -79.4380,
                'website': 'http://pmalarch.ca/projects/play/neshama-playground/',
                'type': 'Indoor Playground',
                'hours': {'weekday': ('09:00', '17:00'), 'weekend': ('09:00', '17:00')},
                'note': 'Jewish Community Centre playground, all welcome'
            },

            # Similar venues found through research
            'Funday Indoor Playground': {
                'address': '6085 Creditview Rd, Mississauga',
                'lat': 43.6158, 'lng': -79.7403,
                'website': 'https://www.thefunday.ca/',
                'type': 'Indoor Playground',
                'hours': {'weekday': ('10:00', '20:00'), 'weekend': ('10:00', '20:00')},
                'note': 'Drop-in play sessions, toddlers to age 10'
            },
            'Kids Fun City': {
                'address': '7601 Jane St, Vaughan',
                'lat': 43.8227, 'lng': -79.5218,
                'website': 'https://kidsfuncity.ca/',
                'type': 'Indoor Playground',
                'hours': {'weekday': ('10:00', '18:00'), 'weekend': ('10:00', '19:00')},
                'note': 'Laser tag, mini-golf, go-karts'
            },
            'Extreme Fun': {
                'address': '186 Bartley Dr, North York',
                'lat': 43.7802, 'lng': -79.3477,
                'website': 'https://www.extremefun.ca/',
                'type': 'Indoor Playground',
                'hours': {'weekday': ('09:30', '14:30'), 'weekend': ('10:00', '18:00')},
                'note': '5500 sq ft facility with 15 ft play structure'
            },
            'Sky Zone Scarborough': {
                'address': '45 Esandar Dr Unit 1A, Scarborough',
                'lat': 43.7175, 'lng': -79.3279,
                'website': 'https://www.skyzone.com/ca-toronto/',
                'type': 'Trampoline Park',
                'hours': {'weekday': ('09:00', '21:00'), 'weekend': ('09:00', '23:00')},
                'note': 'Toddler Time program available, Little Leapers for toddlers'
            },
            'The Jump City Richmond Hill': {
                'address': '1070 Major Mackenzie Dr E, Richmond Hill',
                'lat': 43.8724, 'lng': -79.4273,
                'website': 'https://thejumpcity.ca/',
                'type': 'Trampoline Park',
                'hours': {'weekday': ('10:00', '20:00'), 'weekend': ('09:00', '21:00')},
                'note': 'Multi-level play structures, trampoline park, climbing walls'
            },
            'The Jump City Scarborough': {
                'address': '1900 Eglinton Ave E, Scarborough',
                'lat': 43.7290, 'lng': -79.2624,
                'website': 'https://thejumpcity.ca/',
                'type': 'Trampoline Park',
                'hours': {'weekday': ('10:00', '20:00'), 'weekend': ('09:00', '21:00')},
                'note': 'Multi-level play structures, trampoline park, climbing walls'
            },
            'Liliput Playhouse': {
                'address': '1912 Avenue Rd Unit 200, North York',
                'lat': 43.7233, 'lng': -79.4112,
                'website': 'https://www.liliput.ca/',
                'type': 'Indoor Playground',
                'hours': {'weekday': ('09:00', '17:00'), 'weekend': ('10:00', '18:00')},
                'note': 'Music, art, pirate ship sandbox, pillow pit'
            },
            'Kidsports Indoor Playground': {
                'address': '2550 Matheson Blvd E, Mississauga',
                'lat': 43.6345, 'lng': -79.6133,
                'website': 'https://www.kidsportsindoorplayground.com/',
                'type': 'Indoor Playground',
                'hours': {'weekday': ('10:00', '19:00'), 'weekend': ('10:00', '20:00')},
                'note': '18,000 sq ft, largest in Mississauga'
            },
            'Kidsapia': {
                'address': '5100 Erin Mills Pkwy, Mississauga',
                'lat': 43.5281, 'lng': -79.7360,
                'website': 'https://kidsapia.ca/',
                'type': 'Indoor Playground',
                'hours': {'weekday': ('10:00', '19:00'), 'weekend': ('10:00', '20:00')},
                'note': 'Space-themed playground at Erin Mills Town Centre'
            },
            'Funland Indoor Playground': {
                'address': '5051 Highway 7 E Unit 1A, Markham',
                'lat': 43.8540, 'lng': -79.3214,
                'website': 'https://funlandplayground.ca/',
                'type': 'Indoor Playground',
                'hours': {'weekday': ('10:00', '19:00'), 'weekend': ('10:00', '20:00')},
                'note': 'Ages 1-13, arcade games, toddler area'
            },
            'Mighty Jungle': {
                'address': '3100 Ridgeway Dr Unit 19, Mississauga',
                'lat': 43.5697, 'lng': -79.6435,
                'website': 'https://www.themightyjungle.ca/',
                'type': 'Indoor Playground',
                'hours': {'weekday': ('10:00', '18:00'), 'weekend': ('10:00', '19:00')},
                'note': 'Three-storey jungle-themed playground'
            },
            'Playtown': {
                'address': '2170 Dunwin Dr Unit 6, Mississauga',
                'lat': 43.5928, 'lng': -79.6484,
                'website': 'http://www.kidsplaytown.ca/',
                'type': 'Indoor Playground',
                'hours': {'weekday': ('10:00', '18:00'), 'weekend': ('10:00', '19:00')},
                'note': 'Themed playhouses: restaurant, construction, raceway, salon'
            },
            'Kidnasium Lawrence Park': {
                'address': '1660 Avenue Rd, North York',
                'lat': 43.7233, 'lng': -79.4112,
                'website': 'https://kidnasium.ca/',
                'type': 'Indoor Playground',
                'hours': {'weekday': ('09:00', '18:00'), 'weekend': ('09:00', '18:00')},
                'note': 'Drop-in play, gymnastics programs'
            },
            'Kidnasium Upper Beaches': {
                'address': '1330 Gerrard St E, Toronto',
                'lat': 43.6692, 'lng': -79.3164,
                'website': 'https://kidnasium.ca/',
                'type': 'Indoor Playground',
                'hours': {'weekday': ('09:00', '18:00'), 'weekend': ('09:00', '18:00')},
                'note': 'Drop-in play, gymnastics programs'
            },
            'Bunch of Fun Playland': {
                'address': '11 Kodiak Cres Unit B, North York',
                'lat': 43.7672, 'lng': -79.4894,
                'website': 'https://bunchoffunplayland.com/',
                'type': 'Indoor Playground',
                'hours': {'weekday': ('10:00', '19:00'), 'weekend': ('10:00', '19:00')},
                'note': 'Two playgrounds (toddler & older kids), pottery painting, games'
            },
            'KartTown': {
                'address': '85 Ellesmere Rd Unit 102, Scarborough (Parkway Mall)',
                'lat': 43.7672, 'lng': -79.2692,
                'website': 'https://karttown.ca/',
                'type': 'Go-Kart & Indoor Playground',
                'hours': {'weekday': ('14:00', '20:00'), 'weekend': ('10:00', '20:00')},
                'note': 'Kids go-karting, arcade, play area. Ages 2+ (with parent), 6+ solo. 20% OFF weekdays. VIP Package $35 (20 laps + 15 games)'
            },
            'Jump for Joy Danforth': {
                'address': '1472 Danforth Ave, Toronto',
                'lat': 43.6850, 'lng': -79.3285,
                'website': 'https://jumpforjoyplaycentre.ca/',
                'type': 'Indoor Playground',
                'hours': {'weekday': ('09:00', '14:00'), 'weekend': ('09:00', '14:00')},
                'note': 'Ages 0-6, jumping castle, ball pit, infant area. Mon-Fri only'
            },
            'Playcious Oakville': {
                'address': '3280 S Service Rd W Unit C4, Oakville',
                'lat': 43.4659, 'lng': -79.7421,
                'website': 'https://playcious.com/',
                'type': 'Indoor Playground',
                'hours': {'weekday': ('10:30', '20:00'), 'weekend': ('10:30', '20:00')},
                'note': '18,000 sq ft with trampolines, wall climbing, bumper cars, arcade'
            },
            'Playcious Mississauga': {
                'address': '75 Courtney Park Dr W Unit 2B, Mississauga',
                'lat': 43.6589, 'lng': -79.7123,
                'website': 'https://playcious.com/',
                'type': 'Indoor Playground',
                'hours': {'weekday': ('10:30', '20:00'), 'weekend': ('10:30', '20:00')},
                'note': '18,000 sq ft with trampolines, wall climbing, bumper cars, arcade'
            },
            'The Bubble North York': {
                'address': '65 Orfus Rd Unit A, North York',
                'lat': 43.7183, 'lng': -79.4623,
                'website': 'https://the-bubble.com/',
                'type': 'Indoor Playground',
                'hours': {'weekday': ('15:00', '20:00'), 'weekend': ('10:00', '21:00')},
                'note': '10,000 sq ft inflatable park, laser tag, arcade'
            },
            'The Bubble Vaughan': {
                'address': '7979 Weston Rd, Vaughan',
                'lat': 43.8006, 'lng': -79.5534,
                'website': 'https://the-bubble.com/',
                'type': 'Indoor Playground',
                'hours': {'weekday': ('15:00', '20:00'), 'weekend': ('10:00', '21:00')},
                'note': '10,000 sq ft inflatable park, laser tag, arcade'
            },
            'Kids Cuckoos Nest Aurora': {
                'address': '155 Industrial Pkwy S, Aurora',
                'lat': 44.0006, 'lng': -79.4712,
                'website': 'https://kidscuckoosnest.com/',
                'type': 'Indoor Playground',
                'hours': {'weekday': ('10:00', '18:00'), 'weekend': ('09:00', '19:00')},
                'note': '10,000 sq ft, separate play structures for different ages'
            },
        }

    def fetch_events(self, days_ahead: int = 7) -> List[Dict]:
        """Generate operating hours for indoor play centres"""
        print("🎪 Generating indoor play centre hours...")

        events = []
        today = datetime.now()

        for venue_name, venue_info in self.venues.items():
            current = today
            end_date = today + timedelta(days=days_ahead)

            while current <= end_date:
                # Determine if weekend
                is_weekend = current.weekday() >= 5  # Sat=5, Sun=6
                hours = venue_info['hours']['weekend' if is_weekend else 'weekday']

                event = {
                    "title": f"{venue_name} - Open Play",
                    "description": f"{venue_info['type']} open for drop-in play. {venue_info.get('note', '')}",
                    "category": "Play",
                    "icon": "🎪" if venue_info['type'] == 'Indoor Playground' else "🤸",
                    "date": current.strftime('%Y-%m-%d'),
                    "start_time": hours[0],
                    "end_time": hours[1],
                    "venue": {
                        "name": venue_name,
                        "address": venue_info['address'],
                        "neighborhood": venue_name.split()[-1],  # Last word often indicates area
                        "lat": venue_info['lat'],
                        "lng": venue_info['lng']
                    },
                    "age_groups": ["Toddlers (3-5)", "Kids (6-12)"],
                    "indoor_outdoor": "Indoor",
                    "organized_by": venue_name,
                    "website": venue_info['website'],
                    "source": "IndoorPlay",
                    "scraped_at": datetime.now().isoformat(),
                    "is_free": False  # Most charge admission
                }
                events.append(event)

                current += timedelta(days=1)

        print(f"   ✅ Generated {len(events)} indoor play centre hours")
        return events


def main():
    scraper = IndoorPlayScraper()
    events = scraper.fetch_events(days_ahead=7)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    with open('indoor_play_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to indoor_play_events.json")


if __name__ == "__main__":
    main()
