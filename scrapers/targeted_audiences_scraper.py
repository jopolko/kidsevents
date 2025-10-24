#!/usr/bin/env python3
"""
Targeted Audiences Event Scraper
Creates events targeting specific visitor segments:
- Active Sports Families
- Tech/STEM Enthusiasts
- Performing Arts Lovers
- Special Needs/Inclusive Events
- Teen/Youth Programs
- Outdoor Adventure Seekers
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict


class TargetedAudiencesScraper:
    def __init__(self):
        self.venues = {
            'sports': [],
            'stem': [],
            'performing_arts': [],
            'special_needs': [],
            'teen': [],
            'outdoor': []
        }

    def fetch_all_venues(self):
        """Fetch all venue categories"""
        self.fetch_sports_venues()
        self.fetch_stem_venues()
        self.fetch_performing_arts_venues()
        self.fetch_special_needs_venues()
        self.fetch_teen_venues()
        self.fetch_outdoor_venues()

    def fetch_sports_venues(self):
        """Sports leagues and drop-in activities"""

        print("⚽ Curating sports venues...")

        self.venues['sports'] = [
            {
                "name": "City of Toronto Drop-In Sports",
                "type": "Free Drop-In Sports",
                "description": "FREE drop-in basketball, ball hockey, soccer, volleyball at community centers city-wide!",
                "address": "Multiple Locations",
                "neighborhood": "City-Wide",
                "lat": 43.6532,
                "lng": -79.3832,
                "website": "https://www.toronto.ca/explore-enjoy/recreation/sports-programs/",
                "specialties": ["Basketball", "Soccer", "Ball Hockey", "Volleyball"],
                "age_groups": ["Kids (6-12)", "Teens (13-17)"],
                "target_audience": "Active Sports Families",
                "icon": "🏀"
            },
            {
                "name": "TOP Sports Toronto",
                "type": "Multi-Sport Programs",
                "description": "Multi-sport development! Hockey, soccer, lacrosse for competitive & recreational athletes.",
                "address": "Midtown Toronto",
                "neighborhood": "Midtown",
                "lat": 43.6962,
                "lng": -79.4163,
                "website": "https://www.toronto.topsports.ca",
                "specialties": ["Hockey", "Soccer", "Lacrosse"],
                "age_groups": ["Kids (6-12)", "Teens (13-17)"],
                "target_audience": "Active Sports Families",
                "icon": "🏒"
            },
            {
                "name": "SC Toronto Soccer Club",
                "type": "Community Soccer",
                "description": "Community soccer club! House league for boys & girls 4-16. All skill levels welcome!",
                "address": "Toronto",
                "neighborhood": "City-Wide",
                "lat": 43.6532,
                "lng": -79.3832,
                "website": "https://www.sctoronto.ca/",
                "specialties": ["Soccer", "House League"],
                "age_groups": ["Toddlers (3-5)", "Kids (6-12)", "Teens (13-17)"],
                "target_audience": "Active Sports Families",
                "icon": "⚽"
            }
        ]
        print(f"   ✅ Found {len(self.venues['sports'])} sports venues")

    def fetch_stem_venues(self):
        """STEM, robotics, coding programs"""

        print("🤖 Curating STEM & tech venues...")

        self.venues['stem'] = [
            {
                "name": "Toronto Public Library - FREE STEM Workshops",
                "type": "Free STEM Programs",
                "description": "FREE coding, robotics, circuits! VEX Go, Ozobots, hands-on tech projects. Select Saturdays.",
                "address": "Various TPL Branches",
                "neighborhood": "City-Wide",
                "lat": 43.6532,
                "lng": -79.3832,
                "website": "https://www.torontopubliclibrary.ca/",
                "specialties": ["Coding", "Robotics", "Circuits", "Ozobots"],
                "age_groups": ["Kids (6-12)", "Teens (13-17)"],
                "target_audience": "Tech/STEM Enthusiasts",
                "icon": "💻"
            },
            {
                "name": "MakerKids - Trial Classes",
                "type": "Tech Makerspace",
                "description": "$10 trial classes! Coding, robotics, Minecraft. World's biggest makerspace for kids!",
                "address": "Multiple Toronto Locations",
                "neighborhood": "City-Wide",
                "lat": 43.6532,
                "lng": -79.3832,
                "website": "https://makerkids.com/",
                "specialties": ["Coding", "Robotics", "Minecraft", "Electronics"],
                "age_groups": ["Kids (6-12)", "Teens (13-17)"],
                "target_audience": "Tech/STEM Enthusiasts",
                "icon": "🤖"
            },
            {
                "name": "Exceed Robotics - Free Trial Workshop",
                "type": "Robotics Programs",
                "description": "FREE trial workshops! Hands-on robotics, coding, AI projects. Thornhill, Mississauga, Richmond Hill.",
                "address": "Multiple GTA Locations",
                "neighborhood": "GTA",
                "lat": 43.6532,
                "lng": -79.3832,
                "website": "https://exceedrobotics.com/",
                "specialties": ["Robotics", "Coding", "AI", "Engineering"],
                "age_groups": ["Kids (6-12)", "Teens (13-17)"],
                "target_audience": "Tech/STEM Enthusiasts",
                "icon": "🔬"
            },
            {
                "name": "Ontario Science Centre - Sensory Saturdays",
                "type": "Science Museum",
                "description": "Early openings, adapted programming! Reduced sound, dimmed lights. STEM fun for all!",
                "address": "770 Don Mills Rd",
                "neighborhood": "Don Mills",
                "lat": 43.7167,
                "lng": -79.3389,
                "website": "https://www.ontariosciencecentre.ca/",
                "specialties": ["Science", "Interactive Exhibits", "Planetarium"],
                "age_groups": ["All Ages"],
                "target_audience": "Tech/STEM Enthusiasts",
                "icon": "🔭"
            }
        ]
        print(f"   ✅ Found {len(self.venues['stem'])} STEM venues")

    def fetch_performing_arts_venues(self):
        """Theater, dance, music programs"""

        print("🎭 Curating performing arts venues...")

        self.venues['performing_arts'] = [
            {
                "name": "ARTSies Musical Theatre",
                "type": "Youth Musical Theatre",
                "description": "Musical theatre for kids 5-teens! Classes, camps, Broadway performances. No experience needed!",
                "address": "Scarborough",
                "neighborhood": "Scarborough",
                "lat": 43.7764,
                "lng": -79.2318,
                "website": "https://www.artsiesinc.com/",
                "specialties": ["Musical Theatre", "Singing", "Dancing", "Acting"],
                "age_groups": ["Kids (6-12)", "Teens (13-17)"],
                "target_audience": "Performing Arts Lovers",
                "icon": "🎭"
            },
            {
                "name": "Generations Performing Arts",
                "type": "Non-Competitive Dance & Theatre",
                "description": "Ballet, jazz, tap, hip hop, musical theatre! Non-competitive, inclusive for all ages.",
                "address": "Toronto",
                "neighborhood": "Central Toronto",
                "lat": 43.6532,
                "lng": -79.3832,
                "website": "https://www.generationsperformingarts.com/",
                "specialties": ["Ballet", "Jazz", "Hip Hop", "Musical Theatre", "Acro"],
                "age_groups": ["Toddlers (3-5)", "Kids (6-12)", "Teens (13-17)"],
                "target_audience": "Performing Arts Lovers",
                "icon": "💃"
            },
            {
                "name": "Randolph Kids",
                "type": "Drama & Arts School",
                "description": "Drama, dance, musical theatre downtown! Summer camps, intensives, year-round classes.",
                "address": "Downtown Toronto",
                "neighborhood": "Downtown",
                "lat": 43.6532,
                "lng": -79.3832,
                "website": "https://randolphkids.com/",
                "specialties": ["Drama", "Dance", "Musical Theatre", "Acting"],
                "age_groups": ["Kids (6-12)", "Teens (13-17)"],
                "target_audience": "Performing Arts Lovers",
                "icon": "🎬"
            }
        ]
        print(f"   ✅ Found {len(self.venues['performing_arts'])} performing arts venues")

    def fetch_special_needs_venues(self):
        """Sensory-friendly and inclusive programs"""

        print("♿ Curating inclusive & sensory-friendly venues...")

        self.venues['special_needs'] = [
            {
                "name": "Ripley's Aquarium - Sensory Sundays",
                "type": "Sensory-Friendly Attraction",
                "description": "1st Sunday monthly! Increased lighting, no background music. Certified Autism Center!",
                "address": "288 Bremner Blvd",
                "neighborhood": "Harbourfront",
                "lat": 43.6424,
                "lng": -79.3860,
                "website": "https://www.ripleyaquariums.com/canada/",
                "specialties": ["Marine Life", "Sensory-Friendly", "Quiet Hours"],
                "age_groups": ["All Ages"],
                "target_audience": "Special Needs/Inclusive",
                "icon": "🐠"
            },
            {
                "name": "CN Tower - Low Sensory Mornings",
                "type": "Sensory-Friendly Experience",
                "description": "Reduced capacity, lighting adjustments, music-free, quiet room available!",
                "address": "290 Bremner Blvd",
                "neighborhood": "Downtown",
                "lat": 43.6426,
                "lng": -79.3871,
                "website": "https://www.cntower.ca/",
                "specialties": ["Observatory", "Sensory-Friendly", "Quiet Space"],
                "age_groups": ["All Ages"],
                "target_audience": "Special Needs/Inclusive",
                "icon": "🗼"
            },
            {
                "name": "Ontario Science Centre - Sensory Saturdays",
                "type": "Sensory-Friendly Science",
                "description": "Early entry, reduced sound, dimmed lights, adapted programming for sensory sensitivities!",
                "address": "770 Don Mills Rd",
                "neighborhood": "Don Mills",
                "lat": 43.7167,
                "lng": -79.3389,
                "website": "https://www.ontariosciencecentre.ca/",
                "specialties": ["Science", "Sensory-Friendly", "Adapted Programs"],
                "age_groups": ["All Ages"],
                "target_audience": "Special Needs/Inclusive",
                "icon": "🔬"
            },
            {
                "name": "Toronto Zoo - Sensory Mornings",
                "type": "Sensory-Friendly Zoo",
                "description": "Early entry, limited crowds, sensory-friendly programming. Quiet, calm zoo experience!",
                "address": "2000 Meadowvale Rd",
                "neighborhood": "Scarborough",
                "lat": 43.8178,
                "lng": -79.1860,
                "website": "https://www.torontozoo.com/",
                "specialties": ["Animals", "Sensory-Friendly", "Early Access"],
                "age_groups": ["All Ages"],
                "target_audience": "Special Needs/Inclusive",
                "icon": "🦁"
            },
            {
                "name": "Variety Village",
                "type": "Inclusive Sports & Recreation",
                "description": "Inclusive sports! Swimming, hockey, track & field for kids with various abilities. Financial aid available!",
                "address": "3701 Danforth Ave",
                "neighborhood": "Scarborough",
                "lat": 43.6881,
                "lng": -79.2698,
                "website": "https://varietyvillage.ca/",
                "specialties": ["Adapted Sports", "Swimming", "Hockey", "Inclusive Programs"],
                "age_groups": ["All Ages"],
                "target_audience": "Special Needs/Inclusive",
                "icon": "♿"
            },
            {
                "name": "Cineplex - Sensory Friendly Screenings",
                "type": "Sensory-Friendly Movies",
                "description": "Lights up, sound down! Sensory-friendly movies for kids with autism & sensory sensitivities.",
                "address": "Select Cineplex Theatres",
                "neighborhood": "City-Wide",
                "lat": 43.6532,
                "lng": -79.3832,
                "website": "https://www.cineplex.com/",
                "specialties": ["Movies", "Sensory-Friendly", "Adapted Screenings"],
                "age_groups": ["All Ages"],
                "target_audience": "Special Needs/Inclusive",
                "icon": "🎬"
            }
        ]
        print(f"   ✅ Found {len(self.venues['special_needs'])} inclusive venues")

    def fetch_teen_venues(self):
        """Teen-specific programs and spaces"""

        print("😎 Curating teen programs...")

        self.venues['teen'] = [
            {
                "name": "Toronto Youth Drop-In Programs",
                "type": "Teen Drop-In Centers",
                "description": "FREE teen drop-ins! Gaming, sports, arts, leadership programs. After-school safe spaces.",
                "address": "Community Centers City-Wide",
                "neighborhood": "City-Wide",
                "lat": 43.6532,
                "lng": -79.3832,
                "website": "https://www.toronto.ca/",
                "specialties": ["Gaming", "Sports", "Arts", "Leadership"],
                "age_groups": ["Teens (13-17)"],
                "target_audience": "Teen Programs",
                "icon": "🎮"
            }
        ]
        print(f"   ✅ Found {len(self.venues['teen'])} teen programs")

    def fetch_outdoor_venues(self):
        """Outdoor adventure and nature programs"""

        print("🏕️ Curating outdoor adventure venues...")

        self.venues['outdoor'] = [
            {
                "name": "Toronto Parks - Free Outdoor Play",
                "type": "Nature Exploration",
                "description": "FREE outdoor adventure playgrounds! Nature trails, splash pads, climbing structures city-wide.",
                "address": "Parks City-Wide",
                "neighborhood": "City-Wide",
                "lat": 43.6532,
                "lng": -79.3832,
                "website": "https://www.toronto.ca/explore-enjoy/parks-gardens-beaches/",
                "specialties": ["Playgrounds", "Nature Trails", "Splash Pads"],
                "age_groups": ["All Ages"],
                "target_audience": "Outdoor Adventure Seekers",
                "icon": "🌲"
            },
            {
                "name": "Toronto Island Park",
                "type": "Island Adventure",
                "description": "Ferry ride to paradise! Beaches, bike rentals, Centreville amusement park, nature trails!",
                "address": "Toronto Islands",
                "neighborhood": "Toronto Islands",
                "lat": 43.6193,
                "lng": -79.3783,
                "website": "https://www.toronto.ca/explore-enjoy/parks-gardens-beaches/toronto-island-park/",
                "specialties": ["Beaches", "Biking", "Amusement Park", "Nature"],
                "age_groups": ["All Ages"],
                "target_audience": "Outdoor Adventure Seekers",
                "icon": "🏖️"
            }
        ]
        print(f"   ✅ Found {len(self.venues['outdoor'])} outdoor venues")

    def generate_targeted_events(self, days_ahead: int = 30) -> List[Dict]:
        """Generate events for all target audiences"""

        print("\n🎯 Generating targeted audience events...")

        # Fetch all venues first
        self.fetch_all_venues()

        events = []
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        # Generate events for each category
        for category, venues in self.venues.items():
            for venue in venues:
                # Generate recurring events based on type
                venue_events = self._generate_venue_events(venue, category, today, end_date)
                events.extend(venue_events)

        print(f"   ✅ Generated {len(events)} targeted events across all audiences")
        return events

    def _generate_venue_events(self, venue, category, today, end_date):
        """Generate recurring events for a venue"""
        events = []

        # Different schedules for different categories
        if category == 'special_needs':
            # First Sunday of month for sensory events
            current_date = today
            while current_date <= end_date:
                # Find first Sunday of month
                first_day = datetime(current_date.year, current_date.month, 1).date()
                days_to_sunday = (6 - first_day.weekday()) % 7
                first_sunday = first_day + timedelta(days=days_to_sunday)

                if first_sunday >= today and first_sunday <= end_date:
                    events.append(self._create_event(venue, first_sunday, category))

                # Move to next month
                if current_date.month == 12:
                    current_date = datetime(current_date.year + 1, 1, 1).date()
                else:
                    current_date = datetime(current_date.year, current_date.month + 1, 1).date()

        else:
            # Weekly events for other categories (Saturdays)
            days_until_saturday = (5 - today.weekday()) % 7
            if days_until_saturday == 0:
                days_until_saturday = 7
            next_saturday = today + timedelta(days=days_until_saturday)

            # Generate 2 Saturday events
            for week in range(2):
                event_date = next_saturday + timedelta(days=week * 7)
                if event_date <= end_date:
                    events.append(self._create_event(venue, event_date, category))

        return events

    def _create_event(self, venue, event_date, category):
        """Create a single event from venue data"""

        # Custom titles based on category
        title_prefix = {
            'sports': "⚽ Sports Drop-In",
            'stem': "🤖 STEM Workshop",
            'performing_arts': "🎭 Performing Arts",
            'special_needs': "♿ Sensory-Friendly",
            'teen': "😎 Teen Program",
            'outdoor': "🏕️ Outdoor Adventure"
        }.get(category, "")

        return {
            "title": f"{title_prefix}: {venue['name']}",
            "description": venue['description'],
            "category": {
                'sports': 'Sports',
                'stem': 'Learning',
                'performing_arts': 'Arts',
                'special_needs': 'Play',
                'teen': 'Entertainment',
                'outdoor': 'Nature'
            }.get(category, 'Entertainment'),
            "icon": venue['icon'],
            "date": event_date.strftime('%Y-%m-%d'),
            "start_time": "10:00",
            "end_time": "16:00",
            "venue": {
                "name": venue['name'],
                "address": venue['address'],
                "neighborhood": venue['neighborhood'],
                "lat": venue['lat'],
                "lng": venue['lng']
            },
            "age_groups": venue['age_groups'],
            "indoor_outdoor": "Indoor",
            "organized_by": venue['name'],
            "website": venue['website'],
            "source": "TargetedAudiences",
            "target_audience": venue['target_audience'],
            "venue_type": venue['type']
        }


def main():
    scraper = TargetedAudiencesScraper()
    events = scraper.generate_targeted_events(days_ahead=30)

    print(f"\n📊 Summary:")
    print(f"   Total targeted events: {len(events)}")

    # Count by target audience
    audiences = {}
    for event in events:
        aud = event['target_audience']
        audiences[aud] = audiences.get(aud, 0) + 1

    print(f"\n👥 Events by Target Audience:")
    for audience, count in sorted(audiences.items(), key=lambda x: x[1], reverse=True):
        print(f"   {audience}: {count}")

    # Save to JSON
    with open('targeted_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved to targeted_events.json")


if __name__ == "__main__":
    main()
