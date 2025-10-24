#!/usr/bin/env python3
"""
Toronto Artisans & Artists Scraper
Curated list of local artisans, artists, makers, and craft workshops by neighborhood
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict


class TorontoArtisansScraper:
    def __init__(self):
        self.artisans = []

    def fetch_artisans(self) -> List[Dict]:
        """Fetch curated artisans and artists by neighborhood"""

        print("🎨 Curating Toronto artisans and artists...")

        # Kensington Market
        self.artisans.extend([
            {
                "name": "Kensington Studios",
                "type": "Community Art Space",
                "neighborhood": "Kensington Market",
                "description": "Artist studios and outdoor market featuring local painters, sculptors, and makers. Summer market runs daily April-September.",
                "address": "19 Kensington Ave",
                "lat": 43.6544,
                "lng": -79.4004,
                "website": "https://www.kensingtonstudios.com/",
                "phone": "416-603-5925",
                "specialties": ["Painting", "Sculpture", "Mixed Media", "Jewelry"],
                "family_friendly": True,
                "icon": "🎨"
            },
            {
                "name": "Kensington Market Pedestrian Sundays",
                "type": "Community Market",
                "neighborhood": "Kensington Market",
                "description": "Car-free Sundays! Local artisans, street performers, vintage vendors. Runs last Sunday of month May-October.",
                "address": "Kensington Ave & Augusta Ave",
                "lat": 43.6544,
                "lng": -79.4004,
                "website": "https://kensingtonmarket.to/",
                "phone": "416-392-0675",
                "specialties": ["Street Market", "Artisan Goods", "Vintage", "Food"],
                "family_friendly": True,
                "icon": "🚶"
            }
        ])

        # Leslieville/Riverdale
        self.artisans.extend([
            {
                "name": "Arts Market Toronto",
                "type": "Artisan Collective",
                "neighborhood": "Leslieville",
                "description": "270+ local artists with storefronts. Pottery, jewelry, textiles, woodwork. Support local makers!",
                "address": "790 Queen St E",
                "lat": 43.6575,
                "lng": -79.3458,
                "website": "https://artsmarket.ca/",
                "phone": "416-364-3227",
                "specialties": ["Pottery", "Jewelry", "Textiles", "Woodwork", "Illustration"],
                "family_friendly": True,
                "icon": "🖼️"
            },
            {
                "name": "Leslieville Flea Market",
                "type": "Weekly Flea Market",
                "neighborhood": "Leslieville",
                "description": "Sundays May-October at Ashbridge Estate! 11am-5pm. 50+ vendors, artisans, vintage goods, local makers.",
                "address": "1444 Queen St E",
                "lat": 43.6667,
                "lng": -79.3057,
                "website": "https://torontoflea.com/",
                "phone": "416-596-0322",
                "specialties": ["Vintage", "Artisan Goods", "Food", "Handmade Crafts"],
                "family_friendly": True,
                "icon": "🏪"
            },
            {
                "name": "Riverdale Hub - Sunday Artisan Market",
                "type": "Monthly Craft Market",
                "neighborhood": "Riverdale",
                "description": "Second Sunday of every month! Local artisans selling handmade goods, art, crafts. Family-friendly atmosphere.",
                "address": "1083 Queen St E",
                "lat": 43.6607,
                "lng": -79.3312,
                "website": "https://riverdalehub.ca/",
                "phone": "416-469-4167",
                "specialties": ["Handmade Crafts", "Art", "Ceramics", "Textiles"],
                "family_friendly": True,
                "icon": "🎪"
            },
            {
                "name": "The Danforth Arts Studio",
                "type": "Art Studio & Workshops",
                "neighborhood": "Danforth",
                "description": "Kids & family art classes! Painting, drawing, sculpture workshops. Drop-in sessions available.",
                "address": "270 Danforth Ave",
                "lat": 43.6776,
                "lng": -79.3575,
                "website": "https://thedanforthartstudio.com/",
                "phone": "416-778-6985",
                "specialties": ["Kids Classes", "Painting", "Drawing", "Sculpture"],
                "family_friendly": True,
                "icon": "🖌️"
            },
            {
                "name": "Clay With Me Pottery Studio",
                "type": "Pottery Studio",
                "neighborhood": "Leslieville",
                "description": "Toronto's friendliest pottery studio! Kids programs, paint-your-own pottery, mosaic workshops. Drop-in welcome!",
                "address": "1076 Queen St E",
                "lat": 43.6605,
                "lng": -79.3320,
                "website": "https://claywithme.ca/",
                "phone": "647-748-2529",
                "specialties": ["Pottery", "Kids Classes", "Paint Your Own", "Mosaics"],
                "family_friendly": True,
                "icon": "🏺"
            },
            {
                "name": "Pottery Studio 1",
                "type": "Pottery & Ceramics Studio",
                "neighborhood": "Downtown",
                "description": "Pottery lessons for kids 3+! Group & individual classes daily 11am-9pm. Wheel throwing, hand building.",
                "address": "Downtown Toronto",
                "lat": 43.6532,
                "lng": -79.3832,
                "website": "https://pottery-studio.ca/",
                "phone": "647-776-2529",
                "specialties": ["Pottery", "Kids Classes", "Wheel Throwing", "Hand Building"],
                "family_friendly": True,
                "icon": "🏺"
            }
        ])

        # Downtown/Central
        self.artisans.extend([
            {
                "name": "Studio Mooi",
                "type": "Creative Workshop Space",
                "neighborhood": "Downtown",
                "description": "Kids programs, PA Day camps, birthday parties. Inspiring creativity for all ages!",
                "address": "Multiple Toronto Locations",
                "lat": 43.6532,
                "lng": -79.3832,
                "website": "https://www.studiomooi.ca/",
                "phone": "647-348-6664",
                "specialties": ["Kids Workshops", "Art Classes", "Camps", "Private Events"],
                "family_friendly": True,
                "icon": "✨"
            },
            {
                "name": "The Make Station",
                "type": "Youth Art Studio",
                "neighborhood": "West End",
                "description": "Art camps & classes for kids! Painting, drawing, photography, sculpture, mixed media exploration.",
                "address": "West Toronto",
                "lat": 43.6465,
                "lng": -79.4656,
                "website": "https://themakestation.ca/",
                "phone": "647-350-6253",
                "specialties": ["Kids Art", "Photography", "Sculpture", "Mixed Media"],
                "family_friendly": True,
                "icon": "🎨"
            },
            {
                "name": "The Maker Bean Cafe",
                "type": "Makerspace & Cafe",
                "neighborhood": "Downtown",
                "description": "Canada's FIRST makerspace cafe! Laser cutting, 3D printing, kids tech camps. Locally sourced coffee!",
                "address": "Multiple Toronto Locations",
                "lat": 43.6532,
                "lng": -79.3832,
                "website": "https://themakerbean.com/",
                "phone": "416-546-2326",
                "specialties": ["Tech Workshops", "Laser Cutting", "3D Printing", "Kids Camps"],
                "family_friendly": True,
                "icon": "⚡"
            },
            {
                "name": "The Artful Child",
                "type": "Process Art Studio",
                "neighborhood": "Roncesvalles",
                "description": "Creative process art school for kids & families! Drop-in sessions. Paint, squish, pour, create!",
                "address": "Roncesvalles area",
                "lat": 43.6435,
                "lng": -79.4486,
                "website": "https://www.theartfulchild.ca/",
                "phone": "647-350-2787",
                "specialties": ["Process Art", "Kids Classes", "Drop-In", "Family Workshops"],
                "family_friendly": True,
                "icon": "🎨"
            },
            {
                "name": "4Cats Arts Studio",
                "type": "Kids Art Studio",
                "neighborhood": "Multiple Locations",
                "description": "Art classes for kids! Creative self-expression through painting, drawing, sculpture. Ages 18mo-12yrs.",
                "address": "Multiple Toronto Locations",
                "lat": 43.6532,
                "lng": -79.3832,
                "website": "https://www.4cats.com/",
                "phone": "416-636-2287",
                "specialties": ["Kids Art", "Painting", "Drawing", "Sculpture"],
                "family_friendly": True,
                "icon": "🎨"
            }
        ])

        # Harbourfront
        self.artisans.extend([
            {
                "name": "Harbourfront Centre - Craft & Design",
                "type": "Professional Craft Studios",
                "neighborhood": "Harbourfront",
                "description": "Glass blowing, ceramics, jewelry making, textiles! Watch artisans work, take classes.",
                "address": "235 Queens Quay W",
                "lat": 43.6385,
                "lng": -79.3817,
                "website": "https://harbourfrontcentre.com/",
                "phone": "416-973-4000",
                "specialties": ["Glass Blowing", "Ceramics", "Jewelry", "Textiles", "Screen Printing"],
                "family_friendly": True,
                "icon": "🔥"
            }
        ])

        # Distillery District
        self.artisans.extend([
            {
                "name": "Toronto Artisan Market - Distillery",
                "type": "Artisan Market",
                "neighborhood": "Distillery District",
                "description": "Monthly market in historic Distillery District. Local makers, food artisans, unique crafts.",
                "address": "Distillery District",
                "lat": 43.6503,
                "lng": -79.3599,
                "website": "https://www.torontoartisanmarket.com/",
                "phone": "416-364-1177",
                "specialties": ["Handmade Goods", "Food Artisans", "Jewelry", "Art"],
                "family_friendly": True,
                "icon": "🏭"
            }
        ])

        # Bloor West/Ossington
        self.artisans.extend([
            {
                "name": "Site 3 coLaboratory",
                "type": "Art & Technology Makerspace",
                "neighborhood": "Bloor-Ossington",
                "description": "Woodworking, glassworking, 3D printing, electronics. Classes for adults and families.",
                "address": "Near Bloor & Ossington",
                "lat": 43.6569,
                "lng": -79.4234,
                "website": "https://www.site3.ca/",
                "phone": "647-479-7483",
                "specialties": ["Woodworking", "Glassworking", "3D Printing", "Electronics"],
                "family_friendly": True,
                "icon": "🔧"
            },
            {
                "name": "Paperhouse Studio",
                "type": "Paper Arts Studio",
                "neighborhood": "Dundas West",
                "description": "Paper & print arts! Origami, bookbinding, monoprinting, papermaking classes.",
                "address": "Dundas West",
                "lat": 43.6520,
                "lng": -79.4478,
                "website": "https://www.paperhousestudio.com/",
                "phone": "416-516-7273",
                "specialties": ["Origami", "Bookbinding", "Printing", "Papermaking"],
                "family_friendly": True,
                "icon": "📄"
            }
        ])

        # The Beaches
        self.artisans.extend([
            {
                "name": "The Beaches Arts & Crafts Show",
                "type": "Annual Craft Fair",
                "neighborhood": "The Beaches",
                "description": "Springtime tradition since 1984! 150+ independent artists, makers, designers. Outdoor show.",
                "address": "Kew Gardens, The Beaches",
                "lat": 43.6679,
                "lng": -79.2975,
                "website": "https://www.beachesartandcraftshow.com/",
                "phone": "416-699-2677",
                "specialties": ["Fine Art", "Crafts", "Jewelry", "Pottery", "Textiles"],
                "family_friendly": True,
                "icon": "🏖️"
            }
        ])

        # Scarborough/East
        self.artisans.extend([
            {
                "name": "MakerKids",
                "type": "Tech Makerspace for Kids",
                "neighborhood": "Multiple Locations",
                "description": "World's biggest makerspace for kids! Minecraft, robotics, coding camps and workshops.",
                "address": "Bloor West & Jane (+ other locations)",
                "lat": 43.6465,
                "lng": -79.4878,
                "website": "https://www.makerkids.com/",
                "phone": "647-348-5437",
                "specialties": ["Robotics", "Coding", "Minecraft", "Tech Camps"],
                "family_friendly": True,
                "icon": "🤖"
            }
        ])

        # Alternative/Specialty
        self.artisans.extend([
            {
                "name": "Toronto Dark Arts Market",
                "type": "Alternative Arts Market",
                "neighborhood": "Various Locations",
                "description": "Bi-monthly alternative marketplace! Gothic, witchy, alternative artists, musicians, makers.",
                "address": "Rotating Venues",
                "lat": 43.6532,
                "lng": -79.3832,
                "website": "https://www.torontodarkartsmarket.com/",
                "specialties": ["Alternative Art", "Gothic Crafts", "Music", "Unique Goods"],
                "family_friendly": False,
                "icon": "🌙"
            },
            {
                "name": "Sharpen Skills",
                "type": "Hands-On Workshop Studio",
                "neighborhood": "Downtown",
                "description": "Self-sufficiency workshops! Woodworking, leatherwork, knife skills. Expert artisans, small groups.",
                "address": "Downtown Toronto",
                "lat": 43.6532,
                "lng": -79.3832,
                "website": "https://sharpenskills.ca/",
                "specialties": ["Woodworking", "Leatherwork", "Knife Making", "Practical Skills"],
                "family_friendly": False,
                "icon": "🪵"
            }
        ])

        print(f"   ✅ Curated {len(self.artisans)} artisans and makers")
        return self.artisans

    def generate_artisan_events(self, days_ahead: int = 30) -> List[Dict]:
        """Generate events from artisan spaces"""

        print("🎪 Generating artisan workshop events...")

        # First, fetch artisans if not already loaded
        if not self.artisans:
            self.fetch_artisans()

        events = []
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        # Generate recurring weekend events for family-friendly artisans
        for artisan in self.artisans:
            if not artisan['family_friendly']:
                continue

            # Find this coming weekend (Saturday or Sunday if today is before Sunday)
            current_weekday = today.weekday()

            # If today is Sunday (6), start from next Saturday
            if current_weekday == 6:
                days_until_saturday = 6
            else:
                # Otherwise find next Saturday
                days_until_saturday = (5 - current_weekday) % 7
                if days_until_saturday == 0:
                    days_until_saturday = 7

            next_saturday = today + timedelta(days=days_until_saturday)

            # Generate weekend events (Sat & Sun) for next 2 weekends
            for week in range(2):
                saturday = next_saturday + timedelta(days=week * 7)
                sunday = saturday + timedelta(days=1)

                # Saturday event
                if saturday <= end_date:
                    event_data = {
                        "title": f"{artisan['name']} - Weekend Workshop",
                        "description": f"{artisan['description']} Specialties: {', '.join(artisan['specialties'][:3])}. Drop-in welcome!",
                        "category": "Arts",
                        "icon": artisan['icon'],
                        "date": saturday.strftime('%Y-%m-%d'),
                        "start_time": "10:00",
                        "end_time": "16:00",
                        "venue": {
                            "name": artisan['name'],
                            "address": artisan['address'],
                            "neighborhood": artisan['neighborhood'],
                            "lat": artisan['lat'],
                            "lng": artisan['lng']
                        },
                        "age_groups": ["All Ages"],
                        "indoor_outdoor": "Indoor",
                        "organized_by": artisan['name'],
                        "website": artisan['website'],
                        "source": "Artisans",
                        "artisan_type": artisan['type']
                    }
                    if 'phone' in artisan:
                        event_data['phone'] = artisan['phone']
                    events.append(event_data)

                # Sunday event
                if sunday <= end_date:
                    event_data = {
                        "title": f"{artisan['name']} - Sunday Sessions",
                        "description": f"{artisan['description']} Specialties: {', '.join(artisan['specialties'][:3])}. Family-friendly!",
                        "category": "Arts",
                        "icon": artisan['icon'],
                        "date": sunday.strftime('%Y-%m-%d'),
                        "start_time": "11:00",
                        "end_time": "15:00",
                        "venue": {
                            "name": artisan['name'],
                            "address": artisan['address'],
                            "neighborhood": artisan['neighborhood'],
                            "lat": artisan['lat'],
                            "lng": artisan['lng']
                        },
                        "age_groups": ["All Ages"],
                        "indoor_outdoor": "Indoor",
                        "organized_by": artisan['name'],
                        "website": artisan['website'],
                        "source": "Artisans",
                        "artisan_type": artisan['type']
                    }
                    if 'phone' in artisan:
                        event_data['phone'] = artisan['phone']
                    events.append(event_data)

        print(f"   ✅ Generated {len(events)} artisan workshop events")
        return events


def main():
    scraper = TorontoArtisansScraper()

    # Get artisans list
    artisans = scraper.fetch_artisans()

    # Generate events
    events = scraper.generate_artisan_events(days_ahead=30)

    print(f"\n📊 Summary:")
    print(f"   Total artisans: {len(artisans)}")
    print(f"   Total events generated: {len(events)}")

    # Save artisans directory
    with open('toronto_artisans.json', 'w', encoding='utf-8') as f:
        json.dump(artisans, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved artisans to toronto_artisans.json")

    # Save events
    with open('artisan_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved events to artisan_events.json")

    # Show neighborhood distribution
    neighborhoods = {}
    for artisan in artisans:
        hood = artisan['neighborhood']
        neighborhoods[hood] = neighborhoods.get(hood, 0) + 1

    print(f"\n🏘️  Artisans by Neighborhood:")
    for hood, count in sorted(neighborhoods.items(), key=lambda x: x[1], reverse=True):
        print(f"   {hood}: {count}")


if __name__ == "__main__":
    main()
