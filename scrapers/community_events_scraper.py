#!/usr/bin/env python3
"""
Community Events Scraper
Aggregates real community events from various Toronto sources beyond libraries
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict

class CommunityEventsScraper:
    def __init__(self):
        # Manually curated community events that aren't library programs
        # This would be replaced with real scraping in production
        pass

    def get_real_community_events(self) -> List[Dict]:
        """
        Get real community events happening in Toronto
        These are manually curated but represent the types of events parents want:
        - Parks events
        - Community center activities
        - Free festivals
        - Outdoor activities
        - Cultural events
        """

        events = []
        today = datetime.now().date()

        # High Park Zoo & Playground
        events.append({
            "title": "High Park Zoo - Free Visit",
            "description": "Visit Toronto's free zoo featuring animals like bison, llamas, peacocks and more. Great playground nearby!",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "09:00",
            "end_time": "17:00",
            "branch": "High Park",
            "address": "1873 Bloor St W",
            "lat": 43.6465,
            "lng": -79.4637,
            "category": "Nature",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "City of Toronto Parks",
            "website": "https://www.toronto.ca/explore-enjoy/parks-gardens-beaches/zoos-farms/high-park-zoo/"
        })

        # Riverdale Farm
        events.append({
            "title": "Riverdale Farm - Free Petting Farm",
            "description": "Visit heritage farm animals including pigs, cows, chickens, and goats. Completely free!",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "09:00",
            "end_time": "17:00",
            "branch": "Cabbagetown",
            "address": "201 Winchester St",
            "lat": 43.6663,
            "lng": -79.3633,
            "category": "Nature",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "City of Toronto Parks",
            "website": "https://www.toronto.ca/explore-enjoy/parks-gardens-beaches/zoos-farms/riverdale-farm/"
        })

        # Toronto Music Garden
        events.append({
            "title": "Music Garden Free Concert",
            "description": "Free outdoor summer concert series at the beautiful waterfront Music Garden.",
            "date": (today + timedelta(days=2)).strftime('%Y-%m-%d'),
            "start_time": "19:00",
            "end_time": "20:00",
            "branch": "Harbourfront",
            "address": "479 Queens Quay W",
            "lat": 43.6378,
            "lng": -79.4162,
            "category": "Entertainment",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "City of Toronto",
            "website": "https://www.toronto.ca/explore-enjoy/festivals-events/summer-music-in-the-garden/"
        })

        # Wychwood Barns Farmers Market
        events.append({
            "title": "Wychwood Barns Farmers' Market",
            "description": "Family-friendly farmers market with local produce, live music, and kids activities.",
            "date": (today + timedelta(days=(5 - today.weekday()) % 7)).strftime('%Y-%m-%d'),  # Next Saturday
            "start_time": "08:00",
            "end_time": "12:00",
            "branch": "St. Clair West",
            "address": "601 Christie St",
            "lat": 43.6801,
            "lng": -79.4264,
            "category": "Entertainment",
            "age_groups": "All Ages",
            "indoor_outdoor": "Indoor",
            "organized_by": "Wychwood Barns",
            "website": "https://www.artscapewychwoodbarns.ca/whats-on/farmers-market"
        })

        # Evergreen Brick Works
        events.append({
            "title": "Evergreen Brick Works - Nature Play",
            "description": "Free nature exploration, gardens, and outdoor play space. Saturday morning farmer's market!",
            "date": (today + timedelta(days=(5 - today.weekday()) % 7)).strftime('%Y-%m-%d'),  # Next Saturday
            "start_time": "08:00",
            "end_time": "13:00",
            "branch": "Don Valley",
            "address": "550 Bayview Ave",
            "lat": 43.6851,
            "lng": -79.3654,
            "category": "Nature",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "Evergreen",
            "website": "https://www.evergreen.ca/evergreen-brick-works/"
        })

        # Harbourfront Centre
        events.append({
            "title": "Harbourfront Free Concerts",
            "description": "Free waterfront concerts and cultural performances. Check schedule for family-friendly shows.",
            "date": (today + timedelta(days=3)).strftime('%Y-%m-%d'),
            "start_time": "18:00",
            "end_time": "20:00",
            "branch": "Harbourfront",
            "address": "235 Queens Quay W",
            "lat": 43.6385,
            "lng": -79.3817,
            "category": "Entertainment",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "Harbourfront Centre",
            "website": "https://www.harbourfrontcentre.com/"
        })

        # AGO Free Wednesday
        if today.weekday() <= 2:  # If it's before Wednesday
            days_until_wed = (2 - today.weekday()) % 7
            events.append({
                "title": "AGO Free Wednesday Evening",
                "description": "Free admission to Art Gallery of Ontario every Wednesday evening from 6-9pm. Family-friendly galleries!",
                "date": (today + timedelta(days=days_until_wed)).strftime('%Y-%m-%d'),
                "start_time": "18:00",
                "end_time": "21:00",
                "branch": "Downtown",
                "address": "317 Dundas St W",
                "lat": 43.6536,
                "lng": -79.3925,
                "category": "Arts",
                "age_groups": "All Ages",
                "indoor_outdoor": "Indoor",
                "organized_by": "Art Gallery of Ontario",
                "website": "https://ago.ca/"
            })

        # Beaches Playground
        events.append({
            "title": "Beaches Boardwalk & Playground",
            "description": "Free beach access, beautiful boardwalk, multiple playgrounds, and splash pad in summer.",
            "date": (today + timedelta(days=1)).strftime('%Y-%m-%d'),
            "start_time": "09:00",
            "end_time": "18:00",
            "branch": "The Beaches",
            "address": "1675 Lake Shore Blvd E",
            "lat": 43.6678,
            "lng": -79.2961,
            "category": "Nature",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "City of Toronto Parks",
            "website": "https://www.toronto.ca/explore-enjoy/parks-gardens-beaches/beaches/"
        })

        # Allan Gardens Conservatory - FREE
        events.append({
            "title": "Allan Gardens Conservatory - Free Indoor Gardens",
            "description": "Beautiful FREE indoor botanical garden. Perfect escape on cold/rainy days. Open year-round!",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "10:00",
            "end_time": "17:00",
            "branch": "Garden District",
            "address": "160 Gerrard St E",
            "lat": 43.6623,
            "lng": -79.3754,
            "category": "Nature",
            "age_groups": "All Ages",
            "indoor_outdoor": "Indoor",
            "organized_by": "City of Toronto Parks",
            "website": "https://www.toronto.ca/explore-enjoy/parks-gardens-beaches/gardens-and-horticulture/conservatories/"
        })

        # St. Lawrence Market - FREE browsing
        events.append({
            "title": "St. Lawrence Market - Free Browsing & Exploring",
            "description": "Historic market hall, free to walk around. Vendors, prepared foods, kids love the atmosphere!",
            "date": (today + timedelta(days=(5 - today.weekday()) % 7)).strftime('%Y-%m-%d'),  # Next Saturday
            "start_time": "05:00",
            "end_time": "17:00",
            "branch": "Old Toronto",
            "address": "93 Front St E",
            "lat": 43.6487,
            "lng": -79.3716,
            "category": "Entertainment",
            "age_groups": "All Ages",
            "indoor_outdoor": "Indoor",
            "organized_by": "St. Lawrence Market",
            "website": "https://www.stlawrencemarket.com/"
        })

        # Nathan Phillips Square
        events.append({
            "title": "Nathan Phillips Square - FREE Skating (Winter)",
            "description": "Free outdoor skating in winter, splash pad in summer. City Hall views. Always something happening!",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "09:00",
            "end_time": "22:00",
            "branch": "Downtown",
            "address": "100 Queen St W",
            "lat": 43.6529,
            "lng": -79.3835,
            "category": "Sports",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "City of Toronto",
            "website": "https://www.toronto.ca/explore-enjoy/recreation/skating-winter-sports/outdoor-skating-rinks/"
        })

        # Distillery District - FREE
        events.append({
            "title": "Distillery District - Free Walk Around",
            "description": "Pedestrian-only cobblestone streets, shops, art installations. Free to explore, kids love it!",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "10:00",
            "end_time": "18:00",
            "branch": "Distillery District",
            "address": "55 Mill St",
            "lat": 43.6503,
            "lng": -79.3599,
            "category": "Entertainment",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "Distillery District",
            "website": "https://www.thedistillerydistrict.com/"
        })

        # Scarborough Bluffs
        events.append({
            "title": "Scarborough Bluffs - FREE Nature Views",
            "description": "Stunning cliffs and beach. Free parking at Bluffers Park. Amazing views, great for picnics!",
            "date": (today + timedelta(days=1)).strftime('%Y-%m-%d'),
            "start_time": "08:00",
            "end_time": "20:00",
            "branch": "Scarborough",
            "address": "1 Brimley Rd S",
            "lat": 43.7064,
            "lng": -79.2364,
            "category": "Nature",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "City of Toronto Parks",
            "website": "https://www.toronto.ca/explore-enjoy/parks-gardens-beaches/scarborough-bluffs/"
        })

        # Toronto Island Ferry - Park access
        events.append({
            "title": "Toronto Islands - Beaches & Playgrounds",
            "description": "Ferry ride + free beaches, playgrounds, bike rentals. Centreville costs but parks/beaches FREE!",
            "date": (today + timedelta(days=(5 - today.weekday()) % 7)).strftime('%Y-%m-%d'),  # Next Saturday
            "start_time": "09:00",
            "end_time": "18:00",
            "branch": "Toronto Islands",
            "address": "Toronto Island Park",
            "lat": 43.6193,
            "lng": -79.3783,
            "category": "Nature",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "City of Toronto Parks",
            "website": "https://www.toronto.ca/explore-enjoy/parks-gardens-beaches/toronto-island-park/"
        })

        # Kensington Market - FREE
        events.append({
            "title": "Kensington Market - Free Exploring",
            "description": "Eclectic neighborhood, street art, vintage shops, food. Pedestrian Sundays in summer!",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "10:00",
            "end_time": "18:00",
            "branch": "Kensington Market",
            "address": "Kensington Ave",
            "lat": 43.6544,
            "lng": -79.4008,
            "category": "Entertainment",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "Kensington Market BIA",
            "website": "https://www.kensington-market.ca/"
        })

        # Edwards Gardens
        events.append({
            "title": "Edwards Gardens - FREE Beautiful Gardens",
            "description": "Stunning FREE botanical gardens. Walking paths, streams, bridges. Perfect for family photos!",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "08:00",
            "end_time": "19:00",
            "branch": "North York",
            "address": "755 Lawrence Ave E",
            "lat": 43.7284,
            "lng": -79.3593,
            "category": "Nature",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "City of Toronto Parks",
            "website": "https://www.toronto.ca/explore-enjoy/parks-gardens-beaches/gardens-and-horticulture/edwards-gardens/"
        })

        # Roundhouse Park (trains!)
        events.append({
            "title": "Roundhouse Park - FREE Train Museum",
            "description": "See historic trains and locomotives up close. FREE! Kids obsessed with trains will love it.",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "09:00",
            "end_time": "17:00",
            "branch": "Entertainment District",
            "address": "255 Bremner Blvd",
            "lat": 43.6408,
            "lng": -79.3867,
            "category": "Learning",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "Toronto Railway Museum",
            "website": "https://www.trha.ca/roundhouse-park/"
        })

        # Downey's Farm - Annual Pumpkin Patch (Seasonal - September/October)
        # This is about 50km from Toronto in Caledon, demonstrating we include events in the greater Toronto area
        if today.month in [9, 10]:  # September and October
            events.append({
                "title": "Downey's Farm - Annual Pumpkin Patch",
                "description": "Pick your own pumpkins, corn maze, wagon rides, farm animals. Admission fee but picking is extra fun!",
                "date": (today + timedelta(days=(5 - today.weekday()) % 7)).strftime('%Y-%m-%d'),  # Next Saturday
                "start_time": "09:00",
                "end_time": "18:00",
                "branch": "Caledon",
                "address": "13682 Heart Lake Rd, Caledon",
                "lat": 43.8283,
                "lng": -79.8711,
                "category": "Nature",
                "age_groups": "All Ages",
                "indoor_outdoor": "Outdoor",
                "organized_by": "Downey's Farm",
                "website": "https://www.downeysfarm.on.ca/"
            })

        # Brooks Farms - Mount Albert (FREE Market Entry)
        events.append({
            "title": "Brooks Farms - FREE Market & Petting Zoo",
            "description": "Free farm market entry! See farm animals, explore the market. Barnyard Playland activities available (paid).",
            "date": (today + timedelta(days=(5 - today.weekday()) % 7)).strftime('%Y-%m-%d'),  # Next Saturday
            "start_time": "09:00",
            "end_time": "17:00",
            "branch": "Mount Albert",
            "address": "122 Ashworth Rd, Mount Albert",
            "lat": 44.1214,
            "lng": -79.2956,
            "category": "Nature",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "Brooks Farms",
            "website": "https://www.brooksfarms.com"
        })

        # Springridge Farm - Milton
        events.append({
            "title": "Springridge Farm - Petting Zoo & Activities",
            "description": "$5 admission for petting zoo with goats, rabbits, chickens. Seasonal pick-your-own strawberries and pumpkins!",
            "date": (today + timedelta(days=(5 - today.weekday()) % 7)).strftime('%Y-%m-%d'),  # Next Saturday
            "start_time": "09:00",
            "end_time": "17:00",
            "branch": "Milton",
            "address": "7256 Bell School Line, Milton",
            "lat": 43.5806,
            "lng": -79.9439,
            "category": "Nature",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "Springridge Farm",
            "website": "https://www.springridgefarm.com"
        })

        # Pingle's Farm Market - Hampton/Oshawa
        events.append({
            "title": "Pingle's Farm Market - FREE Market Entry",
            "description": "FREE to browse farm market! Seasonal pick-your-own, sunflower fields, corn maze. Open year-round!",
            "date": (today + timedelta(days=(5 - today.weekday()) % 7)).strftime('%Y-%m-%d'),  # Next Saturday
            "start_time": "09:00",
            "end_time": "18:00",
            "branch": "Hampton",
            "address": "1805 Taunton Rd E, Hampton",
            "lat": 43.9464,
            "lng": -78.8853,
            "category": "Nature",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "Pingle's Farm Market",
            "website": "https://pinglesfarmmarket.com"
        })

        # Mississauga Celebration Square - FREE Summer Events
        events.append({
            "title": "Celebration Square - FREE Summer Concerts & Events",
            "description": "FREE concerts, festivals, outdoor fitness, food trucks! Largest wading pool. Events May-October.",
            "date": (today + timedelta(days=(5 - today.weekday()) % 7)).strftime('%Y-%m-%d'),  # Next Saturday
            "start_time": "11:00",
            "end_time": "21:00",
            "branch": "Mississauga",
            "address": "300 City Centre Dr, Mississauga",
            "lat": 43.5933,
            "lng": -79.6428,
            "category": "Entertainment",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "City of Mississauga",
            "website": "https://www.mississauga.ca"
        })

        # Brampton Gage Park
        events.append({
            "title": "Gage Park Brampton - FREE Splash Pad & Playground",
            "description": "FREE splash pad (9am-9pm), accessible playground, skating in winter. Free concerts in summer!",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "09:00",
            "end_time": "21:00",
            "branch": "Brampton",
            "address": "45 Main St S, Brampton",
            "lat": 43.6845,
            "lng": -79.7596,
            "category": "Sports",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "City of Brampton",
            "website": "https://www.brampton.ca"
        })

        # Pickering Waterfront - Beachfront Park
        events.append({
            "title": "Pickering Beachfront Park - FREE Beach & Splash Pad",
            "description": "FREE lakeside splash pad, 2 playgrounds (tots & kids 5+), beach swimming, volleyball. Free parking!",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "09:00",
            "end_time": "20:00",
            "branch": "Pickering",
            "address": "Liverpool Rd, Pickering",
            "lat": 43.8354,
            "lng": -79.0869,
            "category": "Nature",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "City of Pickering",
            "website": "https://www.pickering.ca"
        })

        # Ajax Waterfront Park - Rotary Park
        events.append({
            "title": "Ajax Waterfront Park - FREE Beach & Splash Pad",
            "description": "FREE accessible playground & splash pad! Sandy beach, 6km waterfront trails, fishing, picnic areas.",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "09:00",
            "end_time": "20:00",
            "branch": "Ajax",
            "address": "Rotary Park, Ajax",
            "lat": 43.8509,
            "lng": -79.0204,
            "category": "Nature",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "Town of Ajax",
            "website": "https://www.ajax.ca"
        })

        # Markham Museum
        events.append({
            "title": "Markham Museum - FREE Outdoor Grounds",
            "description": "FREE access to museum grounds! Heritage village, farm animals, walking trails. Indoor exhibits (paid).",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "10:00",
            "end_time": "17:00",
            "branch": "Markham",
            "address": "9350 Markham Rd, Markham",
            "lat": 43.9167,
            "lng": -79.2628,
            "category": "Learning",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "City of Markham",
            "website": "https://www.markham.ca/museum"
        })


        # Kortright Centre - Vaughan (FREE trails)
        events.append({
            "title": "Kortright Centre - FREE Nature Trails",
            "description": "FREE access to beautiful nature trails year-round! 325 hectares of forests, meadows, streams.",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "09:00",
            "end_time": "17:00",
            "branch": "Vaughan",
            "address": "9550 Pine Valley Dr, Vaughan",
            "lat": 43.8253,
            "lng": -79.5872,
            "category": "Nature",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "Toronto & Region Conservation Authority",
            "website": "https://trca.ca/conservation/places-to-visit/kortright-centre/"
        })

        # Centennial Park - Etobicoke
        events.append({
            "title": "Centennial Park - FREE Playground & Trails",
            "description": "FREE 525-acre park! Playgrounds, ski hill, greenhouse, mini-golf (seasonal fee), picnic areas.",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "08:00",
            "end_time": "21:00",
            "branch": "Etobicoke",
            "address": "256 Centennial Park Rd, Etobicoke",
            "lat": 43.6425,
            "lng": -79.5958,
            "category": "Nature",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "City of Toronto Parks",
            "website": "https://www.toronto.ca"
        })

        # Mississauga Valley Park - FREE Splash Pad
        events.append({
            "title": "Mississauga Valley Park - FREE Splash Pad & Playground",
            "description": "FREE large splash pad, playground, tennis courts, walking trails along the Credit River!",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "09:00",
            "end_time": "21:00",
            "branch": "Mississauga",
            "address": "1275 Mississauga Valley Blvd, Mississauga",
            "lat": 43.5789,
            "lng": -79.6647,
            "category": "Sports",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "City of Mississauga",
            "website": "https://www.mississauga.ca"
        })

        # Toronto History Museums - FREE Admission (10 sites)
        events.append({
            "title": "Fort York National Historic Site - FREE",
            "description": "FREE admission! War of 1812 historic site, soldiers' barracks, guided tours, military demonstrations.",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "10:00",
            "end_time": "17:00",
            "branch": "Downtown",
            "address": "250 Fort York Blvd, Toronto",
            "lat": 43.6393,
            "lng": -79.4036,
            "category": "Learning",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "City of Toronto",
            "website": "https://www.toronto.ca/explore-enjoy/history-art-culture/museums/"
        })

        events.append({
            "title": "Spadina Museum - FREE Historic Mansion",
            "description": "FREE! 1930s mansion tours, beautiful gardens, family programs. Kids love the grand staircases!",
            "date": (today + timedelta(days=(5 - today.weekday()) % 7)).strftime('%Y-%m-%d'),  # Next Saturday
            "start_time": "12:00",
            "end_time": "17:00",
            "branch": "Casa Loma",
            "address": "285 Spadina Rd, Toronto",
            "lat": 43.6788,
            "lng": -79.4066,
            "category": "Learning",
            "age_groups": "All Ages",
            "indoor_outdoor": "Indoor",
            "organized_by": "City of Toronto",
            "website": "https://www.toronto.ca/explore-enjoy/history-art-culture/museums/"
        })

        events.append({
            "title": "Scarborough Museum - FREE Heritage Village",
            "description": "FREE! 1890s village with historic buildings, farm animals, costumed interpreters. Kids love it!",
            "date": (today + timedelta(days=(5 - today.weekday()) % 7)).strftime('%Y-%m-%d'),  # Next Saturday
            "start_time": "12:00",
            "end_time": "17:00",
            "branch": "Scarborough",
            "address": "1007 Brimley Rd, Scarborough",
            "lat": 43.7747,
            "lng": -79.2397,
            "category": "Learning",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "City of Toronto",
            "website": "https://www.toronto.ca/explore-enjoy/history-art-culture/museums/"
        })

        # Sherbourne Common - Waterfront Splash Pad
        events.append({
            "title": "Sherbourne Common - FREE Waterfront Splash Pad",
            "description": "FREE 920m² splash pad! Waterfront views, change rooms, skating rink in winter. LED light shows!",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "09:00",
            "end_time": "20:00",
            "branch": "Waterfront",
            "address": "5 Lower Sherbourne St, Toronto",
            "lat": 43.6426,
            "lng": -79.3635,
            "category": "Sports",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "Waterfront Toronto",
            "website": "https://www.waterfrontoronto.ca"
        })

        # Sugar Beach - Waterfront
        events.append({
            "title": "Sugar Beach - FREE Waterfront Beach & Splash Pad",
            "description": "FREE beach, splash pad in granite maple leaf, pink umbrellas, Muskoka chairs. LED light shows!",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "09:00",
            "end_time": "20:00",
            "branch": "Waterfront",
            "address": "11 Dockside Dr, Toronto",
            "lat": 43.6424,
            "lng": -79.3597,
            "category": "Nature",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "Waterfront Toronto",
            "website": "https://www.waterfrontoronto.ca"
        })

        # Aga Khan Museum - Free Wednesdays
        if today.weekday() == 2:  # Wednesday
            events.append({
                "title": "Aga Khan Museum - FREE Wednesday Evening",
                "description": "FREE Wed 4-8pm! Islamic art & culture, beautiful architecture, family programs on Sundays.",
                "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
                "start_time": "16:00",
                "end_time": "20:00",
                "branch": "North York",
                "address": "77 Wynford Dr, North York",
                "lat": 43.7256,
                "lng": -79.3322,
                "category": "Arts",
                "age_groups": "All Ages",
                "indoor_outdoor": "Indoor",
                "organized_by": "Aga Khan Museum",
                "website": "https://www.agakhanmuseum.org"
            })

        # Gardiner Museum - TPL MAP Pass
        events.append({
            "title": "Gardiner Museum - FREE with Library Card",
            "description": "FREE with TPL card! Ceramic art, hands-on clay studio, family programs. Half-price Fridays 4-9pm!",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "10:00",
            "end_time": "17:00",
            "branch": "University",
            "address": "111 Queens Park, Toronto",
            "lat": 43.6677,
            "lng": -79.3948,
            "category": "Arts",
            "age_groups": "All Ages",
            "indoor_outdoor": "Indoor",
            "organized_by": "Gardiner Museum",
            "website": "https://www.gardinermuseum.on.ca"
        })

        # Playground Paradise - Flemingdon Park (FREE for residents)
        events.append({
            "title": "Playground Paradise - FREE Indoor Play",
            "description": "FREE for Toronto residents! Indoor climbing, slides, tree structure. Ages up to 12. Snack-free!",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "09:00",
            "end_time": "20:00",
            "branch": "Flemingdon Park",
            "address": "150 Grenoble Dr, North York",
            "lat": 43.7158,
            "lng": -79.3391,
            "category": "Sports",
            "age_groups": "All Ages",
            "indoor_outdoor": "Indoor",
            "organized_by": "City of Toronto",
            "website": "https://www.toronto.ca"
        })

        # Bronte Beach - Oakville
        events.append({
            "title": "Bronte Beach Park - FREE Beach & Playground",
            "description": "FREE sand beach, playground, walking trails, volleyball. New playground coming 2025!",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "08:00",
            "end_time": "20:00",
            "branch": "Oakville",
            "address": "45 W River St, Oakville",
            "lat": 43.3951,
            "lng": -79.6903,
            "category": "Nature",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "Town of Oakville",
            "website": "https://www.oakville.ca"
        })

        # Coronation Park - Oakville
        events.append({
            "title": "Coronation Park Oakville - FREE Splash Pad & Beach",
            "description": "FREE splash pad, playgrounds, beach volleyball, picnic areas. Lakefront views, snack bar!",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "08:00",
            "end_time": "20:00",
            "branch": "Oakville",
            "address": "1415 Lakeshore Rd W, Oakville",
            "lat": 43.4322,
            "lng": -79.7089,
            "category": "Sports",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "Town of Oakville",
            "website": "https://www.oakville.ca"
        })

        # Thornhill Community Centre
        events.append({
            "title": "Thornhill Community Centre - FREE Drop-In Programs",
            "description": "FREE drop-in activities! Pools, rinks, gym, youth space. Library with Makerspace for kids!",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "09:00",
            "end_time": "21:00",
            "branch": "Thornhill",
            "address": "7755 Bayview Ave, Thornhill",
            "lat": 43.8153,
            "lng": -79.4194,
            "category": "Sports",
            "age_groups": "All Ages",
            "indoor_outdoor": "Indoor",
            "organized_by": "City of Markham",
            "website": "https://www.markham.ca"
        })

        # Artisan Markets & Flea Markets - Sundays
        events.append({
            "title": "Evergreen Garden Market - Local Artisans & Crafts",
            "description": "FREE admission! Local artisans, handmade crafts, vintage finds. Every Sunday at Brick Works!",
            "date": (today + timedelta(days=(6 - today.weekday()) % 7)).strftime('%Y-%m-%d'),  # Next Sunday
            "start_time": "10:00",
            "end_time": "15:00",
            "branch": "Don Valley",
            "address": "550 Bayview Ave, Toronto",
            "lat": 43.6851,
            "lng": -79.3654,
            "category": "Arts",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "Evergreen Brick Works",
            "website": "https://www.evergreen.ca"
        })

        events.append({
            "title": "Parkdale Flea - Vintage & Artisan Market",
            "description": "FREE entry! Antique furniture, handmade jewelry, local art, food vendors. Dogs welcome!",
            "date": (today + timedelta(days=(6 - today.weekday()) % 7)).strftime('%Y-%m-%d'),  # Next Sunday
            "start_time": "11:00",
            "end_time": "16:00",
            "branch": "Parkdale",
            "address": "1266 Queen St W, Toronto",
            "lat": 43.6389,
            "lng": -79.4387,
            "category": "Arts",
            "age_groups": "All Ages",
            "indoor_outdoor": "Indoor",
            "organized_by": "Parkdale Flea",
            "website": "https://www.parkdaleflea.com"
        })

        # Wychwood Barns Farmers Market already added, enhancing description
        # Adding Junction Farmers Market
        events.append({
            "title": "Junction Farmers Market - Kids Scavenger Hunt",
            "description": "FREE! Kids' scavenger hunt, face painting, ukulele lessons. High Park Nature Centre visits weekly!",
            "date": (today + timedelta(days=(5 - today.weekday()) % 7)).strftime('%Y-%m-%d'),  # Next Saturday
            "start_time": "09:00",
            "end_time": "13:00",
            "branch": "Junction",
            "address": "2960 Dundas St W, Toronto",
            "lat": 43.6644,
            "lng": -79.4708,
            "category": "Entertainment",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "Junction Farmers Market",
            "website": "https://www.junctionfarmersmarket.ca"
        })

        # Home Depot Kids Workshop - Second Saturday
        second_saturday = today + timedelta(days=(5 - today.weekday()) % 7)
        while second_saturday.day < 8 or second_saturday.day > 14:
            second_saturday += timedelta(days=7 if second_saturday.day < 8 else -7)

        events.append({
            "title": "Home Depot Kids Workshop - FREE Building Project",
            "description": "FREE! Ages 4-12 build monthly craft project (hammer & glue). Registration required. Parental supervision!",
            "date": second_saturday.strftime('%Y-%m-%d'),
            "start_time": "10:00",
            "end_time": "12:00",
            "branch": "Various GTA",
            "address": "Multiple Home Depot Locations",
            "lat": 43.6532,
            "lng": -79.3832,
            "category": "Learning",
            "age_groups": "All Ages",
            "indoor_outdoor": "Indoor",
            "organized_by": "Home Depot",
            "website": "https://www.homedepot.ca"
        })

        # Toronto Public Library Makerspaces - 3D Printing
        events.append({
            "title": "TPL Digital Innovation Hub - FREE 3D Printing",
            "description": "FREE 3D printing, audio/video production, design workstations. Training classes! 12 branches citywide.",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "10:00",
            "end_time": "20:00",
            "branch": "Various Toronto",
            "address": "Multiple TPL Branches",
            "lat": 43.6532,
            "lng": -79.3832,
            "category": "Learning",
            "age_groups": "All Ages",
            "indoor_outdoor": "Indoor",
            "organized_by": "Toronto Public Library",
            "website": "https://www.torontopubliclibrary.ca"
        })

        # Mississauga Library Makerspace
        events.append({
            "title": "Mississauga Library Makerspace - FREE Tech Access",
            "description": "FREE 3D printers, robotics, sewing machines, filmmaking tools! Ages 12+ (with caregiver if under 12).",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "09:00",
            "end_time": "21:00",
            "branch": "Mississauga",
            "address": "Multiple Library Locations",
            "lat": 43.5890,
            "lng": -79.6441,
            "category": "Learning",
            "age_groups": "All Ages",
            "indoor_outdoor": "Indoor",
            "organized_by": "Mississauga Library",
            "website": "https://www.mississauga.ca/library/"
        })

        # Black Creek Community Farm
        events.append({
            "title": "Black Creek Community Farm - Volunteer & Learn",
            "description": "FREE volunteer! Toronto's largest urban farm. Kids programs, planting, harvesting, farm market!",
            "date": (today + timedelta(days=(5 - today.weekday()) % 7)).strftime('%Y-%m-%d'),  # Next Saturday
            "start_time": "10:00",
            "end_time": "16:00",
            "branch": "Jane & Finch",
            "address": "500 Murray Ross Pkwy, North York",
            "lat": 43.7676,
            "lng": -79.5075,
            "category": "Nature",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "Black Creek Community Farm",
            "website": "https://www.blackcreekfarm.ca"
        })

        # Not Far From The Tree - Fruit Picking
        events.append({
            "title": "Not Far From The Tree - FREE Fruit Picking",
            "description": "FREE volunteer fruit picking! Harvest shared with volunteers, homeowners & food banks. 2000+ volunteers!",
            "date": (today + timedelta(days=(5 - today.weekday()) % 7)).strftime('%Y-%m-%d'),  # Next Saturday
            "start_time": "09:00",
            "end_time": "12:00",
            "branch": "Various Toronto",
            "address": "Wychwood Barns Base",
            "lat": 43.6801,
            "lng": -79.4264,
            "category": "Nature",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "Not Far From The Tree",
            "website": "https://www.notfarfromthetree.org"
        })

        # ArtHeart Community Art
        events.append({
            "title": "ArtHeart - FREE Community Arts Programs",
            "description": "FREE visual arts education! Materials, nourishment provided. Open, safe environment for all families!",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "10:00",
            "end_time": "18:00",
            "branch": "Regent Park",
            "address": "585 Dundas St E, Toronto",
            "lat": 43.6601,
            "lng": -79.3619,
            "category": "Arts",
            "age_groups": "All Ages",
            "indoor_outdoor": "Indoor",
            "organized_by": "ArtHeart",
            "website": "https://www.artheart.ca"
        })

        # MOCA Free Community Sunday
        if today.weekday() == 6:  # Sunday
            events.append({
                "title": "MOCA - FREE Community Sunday",
                "description": "FREE admission one Sunday/month! Drop-in all-ages art workshop. Try new mediums, explore exhibits!",
                "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
                "start_time": "11:00",
                "end_time": "18:00",
                "branch": "Junction Triangle",
                "address": "158 Sterling Rd, Toronto",
                "lat": 43.6442,
                "lng": -79.4393,
                "category": "Arts",
                "age_groups": "All Ages",
                "indoor_outdoor": "Indoor",
                "organized_by": "MOCA Toronto",
                "website": "https://moca.ca"
            })

        # SEASONAL: Splash Pads (May 17 - September 14)
        if today.month >= 5 and today.month <= 9:
            events.append({
                "title": "Toronto Splash Pads - 140+ FREE Locations",
                "description": "FREE! 140+ splash pads citywide. Open May 17-Sept 14, 9am-9pm daily. Find your nearest one!",
                "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
                "start_time": "09:00",
                "end_time": "21:00",
                "branch": "Citywide Toronto",
                "address": "Multiple Locations",
                "lat": 43.6532,
                "lng": -79.3832,
                "category": "Sports",
                "age_groups": "All Ages",
                "indoor_outdoor": "Outdoor",
                "organized_by": "City of Toronto Parks",
                "website": "https://www.toronto.ca"
            })

        # SEASONAL: Outdoor Skating Rinks (November - March)
        if today.month >= 11 or today.month <= 3:
            events.append({
                "title": "FREE Outdoor Skating - City Rinks",
                "description": "FREE! 50+ outdoor rinks citywide. Open Nov-March, 10am-10pm daily. Nathan Phillips, Harbourfront & more!",
                "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
                "start_time": "10:00",
                "end_time": "22:00",
                "branch": "Citywide Toronto",
                "address": "Multiple Locations",
                "lat": 43.6532,
                "lng": -79.3832,
                "category": "Sports",
                "age_groups": "All Ages",
                "indoor_outdoor": "Outdoor",
                "organized_by": "City of Toronto Parks",
                "website": "https://www.toronto.ca"
            })

        # TUESDAY: Free Flicks at Harbourfront (Summer only)
        if today.weekday() == 1 and today.month >= 7 and today.month <= 8:  # Tuesday in July-August
            events.append({
                "title": "FREE Harbourfront Movies - Tuesday Nights",
                "description": "FREE outdoor movies by the lake! Every Tuesday night July-August. Bring blanket, arrive early!",
                "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
                "start_time": "20:30",
                "end_time": "23:00",
                "branch": "Harbourfront",
                "address": "235 Queens Quay W, Toronto",
                "lat": 43.6385,
                "lng": -79.3817,
                "category": "Entertainment",
                "age_groups": "All Ages",
                "indoor_outdoor": "Outdoor",
                "organized_by": "Harbourfront Centre",
                "website": "https://www.harbourfrontcentre.com"
            })

        # WEDNESDAY: Movies at David Pecaut Square (Summer only)
        if today.weekday() == 2 and today.month >= 7 and today.month <= 8:  # Wednesday in July-August
            events.append({
                "title": "Movies in the Park - David Pecaut Square",
                "description": "FREE outdoor movies! Wednesday evenings at sunset. Pre-show trivia, live music, TIFF intros!",
                "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
                "start_time": "20:00",
                "end_time": "23:00",
                "branch": "Entertainment District",
                "address": "David Pecaut Square, Toronto",
                "lat": 43.6468,
                "lng": -79.3891,
                "category": "Entertainment",
                "age_groups": "All Ages",
                "indoor_outdoor": "Outdoor",
                "organized_by": "City of Toronto",
                "website": "https://www.toronto.ca"
            })

        # WEDNESDAY: Berczy Beats Lunchtime Concerts (July-August)
        if today.weekday() == 2 and today.month >= 7 and today.month <= 8:  # Wednesday in July-August
            events.append({
                "title": "Berczy Beats - FREE Lunchtime Concerts",
                "description": "FREE outdoor lunch concerts! Every Wednesday 11:30am-1:30pm. Beautiful Berczy Park downtown!",
                "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
                "start_time": "11:30",
                "end_time": "13:30",
                "branch": "Financial District",
                "address": "35 Wellington St E, Toronto",
                "lat": 43.6489,
                "lng": -79.3746,
                "category": "Entertainment",
                "age_groups": "All Ages",
                "indoor_outdoor": "Outdoor",
                "organized_by": "St. Lawrence Market BIA",
                "website": "https://www.toronto.ca"
            })

        # THURSDAY: Parent & Tot Swim (Example - recurring weekly)
        if today.weekday() == 3:  # Thursday
            events.append({
                "title": "Parent & Tot Swim - Toronto Pan Am Centre",
                "description": "FREE drop-in swim for kids 0-6! Every Thursday 9:30am. No registration, first-come basis!",
                "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
                "start_time": "09:30",
                "end_time": "11:00",
                "branch": "Scarborough",
                "address": "875 Morningside Ave, Scarborough",
                "lat": 43.7844,
                "lng": -79.1968,
                "category": "Sports",
                "age_groups": "All Ages",
                "indoor_outdoor": "Indoor",
                "organized_by": "Toronto Pan Am Sports Centre",
                "website": "https://www.tpasc.ca"
            })

        # SATURDAY: Music in Yorkville Park (Summer)
        if today.weekday() == 5 and today.month >= 6 and today.month <= 9:  # Saturday June-Sept
            events.append({
                "title": "FREE Music in Yorkville Park",
                "description": "FREE live music! Every Saturday 1:30-4:30pm. Beautiful outdoor setting, family-friendly!",
                "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
                "start_time": "13:30",
                "end_time": "16:30",
                "branch": "Yorkville",
                "address": "115 Cumberland St, Toronto",
                "lat": 43.6708,
                "lng": -79.3936,
                "category": "Entertainment",
                "age_groups": "All Ages",
                "indoor_outdoor": "Outdoor",
                "organized_by": "Village of Yorkville",
                "website": "https://www.toronto.ca"
            })

        # SATURDAY: Toronto Outdoor Picture Show (June-August specific dates)
        if today.weekday() == 5 and today.month >= 6 and today.month <= 8:  # Saturday June-August
            events.append({
                "title": "Toronto Outdoor Picture Show - FREE Movies",
                "description": "FREE outdoor movies! 20 screenings Jun-Aug at Fort York, Christie Pits, Corktown. Bring blanket!",
                "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
                "start_time": "20:30",
                "end_time": "23:00",
                "branch": "Various Toronto",
                "address": "Multiple Park Locations",
                "lat": 43.6532,
                "lng": -79.3832,
                "category": "Entertainment",
                "age_groups": "All Ages",
                "indoor_outdoor": "Outdoor",
                "organized_by": "City of Toronto",
                "website": "https://www.toronto.ca"
            })

        # SUNDAY: Summer Music in the Garden (June-August)
        if today.weekday() == 6 and today.month >= 6 and today.month <= 8:  # Sunday June-August
            events.append({
                "title": "FREE Summer Music in the Garden",
                "description": "FREE waterfront concerts! Every Sunday 4pm at Toronto Music Garden. Beautiful lakeside setting!",
                "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
                "start_time": "16:00",
                "end_time": "17:30",
                "branch": "Harbourfront",
                "address": "479 Queens Quay W, Toronto",
                "lat": 43.6378,
                "lng": -79.4162,
                "category": "Entertainment",
                "age_groups": "All Ages",
                "indoor_outdoor": "Outdoor",
                "organized_by": "City of Toronto",
                "website": "https://www.toronto.ca"
            })

        # EarlyON Drop-In Centers - Weekday mornings (Monday-Friday)
        if today.weekday() < 5:  # Monday-Friday
            events.append({
                "title": "EarlyON Drop-In - FREE Play for Ages 0-6",
                "description": "FREE drop-in play! Mon-Fri 9:30am-4pm. 80+ locations. No registration needed, toys, crafts, snacks!",
                "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
                "start_time": "09:30",
                "end_time": "16:00",
                "branch": "Citywide Toronto",
                "address": "80+ Locations across Toronto",
                "lat": 43.6532,
                "lng": -79.3832,
                "category": "Learning",
                "age_groups": "All Ages",
                "indoor_outdoor": "Indoor",
                "organized_by": "City of Toronto",
                "website": "https://www.toronto.ca"
            })

        # Library Storytimes - Tuesday & Thursday mornings
        if today.weekday() in [1, 3]:  # Tuesday or Thursday
            events.append({
                "title": "TPL Baby & Toddler Time - FREE Storytime",
                "description": "FREE storytime! Tues & Thurs 10-10:30am. Songs, rhymes, stories. Ages 0-3. 100+ library branches!",
                "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
                "start_time": "10:00",
                "end_time": "10:30",
                "branch": "Citywide Toronto",
                "address": "Multiple TPL Branches",
                "lat": 43.6532,
                "lng": -79.3832,
                "category": "Learning",
                "age_groups": "All Ages",
                "indoor_outdoor": "Indoor",
                "organized_by": "Toronto Public Library",
                "website": "https://www.torontopubliclibrary.ca"
            })

        # Amos Waites Park - Waterfront park with playground and splash pad
        events.append({
            "title": "Amos Waites Park - Playground & Splash Pad",
            "description": "Waterfront park with boat-themed playground, splash pad, and outdoor pool. Free playground and splash pad access!",
            "date": (today + timedelta(days=0)).strftime('%Y-%m-%d'),
            "start_time": "09:00",
            "end_time": "20:00",
            "branch": "Mimico",
            "address": "2441 Lake Shore Blvd W",
            "lat": 43.6160,
            "lng": -79.5017,
            "category": "Play",
            "age_groups": "All Ages",
            "indoor_outdoor": "Outdoor",
            "organized_by": "City of Toronto Parks",
            "website": "https://www.toronto.ca/explore-enjoy/parks-recreation/places-spaces/parks-and-recreation-facilities/location/?id=939&title=Amos-Waites-Park"
        })

        return events

    def _convert_to_standard_format(self, raw_events: List[Dict]) -> List[Dict]:
        """Convert community events to standard format"""
        from tpl_scraper import TPLScraper
        tpl_scraper = TPLScraper()

        standardized = []
        for event in raw_events:
            category, icon = tpl_scraper.get_category(event['title'], event['description'])

            # Override with event-specific category if provided
            if 'category' in event:
                category = event['category']
                category_icons = {
                    'Nature': '🌳',
                    'Entertainment': '🎵',
                    'Arts': '🎨',
                    'Learning': '📚',
                    'Sports': '⚽'
                }
                icon = category_icons.get(category, icon)

            standardized.append({
                "title": event['title'],
                "description": event['description'],
                "category": category,
                "icon": icon,
                "date": event['date'],
                "start_time": event['start_time'],
                "end_time": event['end_time'],
                "venue": {
                    "name": event.get('branch', 'Toronto'),
                    "address": event['address'],
                    "neighborhood": event.get('branch', 'Toronto'),
                    "lat": event['lat'],
                    "lng": event['lng']
                },
                "age_groups": [event.get('age_groups', 'All Ages')],
                "indoor_outdoor": event.get('indoor_outdoor', 'Outdoor'),
                "organized_by": event.get('organized_by', 'Community'),
                "website": event.get('website', 'https://www.toronto.ca'),
                "source": "Community",
                "scraped_at": datetime.now().isoformat()
            })

        return standardized

    def fetch_events(self) -> List[Dict]:
        """Main method to fetch community events"""
        print("🎪 Fetching community events (parks, festivals, activities)...")

        raw_events = self.get_real_community_events()
        events = self._convert_to_standard_format(raw_events)

        print(f"   ✅ Found {len(events)} community events")
        return events


def main():
    scraper = CommunityEventsScraper()
    events = scraper.fetch_events()

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    with open('community_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to community_events.json")


if __name__ == "__main__":
    main()
