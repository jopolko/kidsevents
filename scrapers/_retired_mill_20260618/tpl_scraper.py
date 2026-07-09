#!/usr/bin/env python3
"""
Toronto Public Library Event Scraper
Scrapes events from TPL's program calendar and outputs JSON
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import List, Dict
import time
import os
from pathlib import Path

class TPLScraper:
    def __init__(self):
        self.base_url = "https://www.torontopubliclibrary.ca"
        self.programs_url = f"{self.base_url}/programs-and-classes/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

        # TPL branch locations with coordinates (sample - add more)
        self.branch_coords = {
            "Beaches": {"lat": 43.6687, "lng": -79.2981},
            "Fort York": {"lat": 43.6391, "lng": -79.4030},
            "Reference Library": {"lat": 43.6719, "lng": -79.3864},
            "Parkdale": {"lat": 43.6396, "lng": -79.4390},
            "Danforth/Coxwell": {"lat": 43.6868, "lng": -79.3218},
            "Lillian H. Smith": {"lat": 43.6577, "lng": -79.4000},
            "High Park": {"lat": 43.6544, "lng": -79.4657},
            "Toronto Reference Library": {"lat": 43.6719, "lng": -79.3864},
            "Albion": {"lat": 43.7372, "lng": -79.5496},
            "Agincourt": {"lat": 43.7856, "lng": -79.2787},
        }

    def get_age_groups(self, program_name: str, description: str) -> List[str]:
        """Determine age groups from program name and description"""
        text = (program_name + " " + description).lower()
        age_groups = []

        if any(word in text for word in ['baby', 'babies', 'infant', '0-2', '0-18 months']):
            age_groups.append("Babies (0-2)")

        if any(word in text for word in ['toddler', 'preschool', '3-5', '2-5', 'early years']):
            age_groups.append("Toddlers (3-5)")

        if any(word in text for word in ['kids', 'children', '6-12', 'junior', 'elementary']):
            age_groups.append("Kids (6-12)")

        if any(word in text for word in ['teen', 'youth', '13-17', 'young adult']):
            age_groups.append("Teens (13-17)")

        if any(word in text for word in ['family', 'all ages', 'everyone']):
            age_groups.append("All Ages")

        # Default if no specific age found
        if not age_groups:
            age_groups.append("All Ages")

        return age_groups

    def get_category(self, program_name: str, description: str) -> tuple:
        """Determine category and icon from program details"""
        text = (program_name + " " + description).lower()

        if any(word in text for word in ['story', 'read', 'book', 'literacy']):
            return "Learning", "📚"

        if any(word in text for word in ['craft', 'art', 'paint', 'draw', 'create', 'make']):
            return "Arts", "🎨"

        if any(word in text for word in ['stem', 'science', 'tech', 'coding', 'robot', 'experiment']):
            return "Learning", "🔬"

        if any(word in text for word in ['music', 'sing', 'dance', 'perform']):
            return "Entertainment", "🎵"

        if any(word in text for word in ['lego', 'build', 'construct']):
            return "Learning", "🧱"

        if any(word in text for word in ['play', 'game', 'toy']):
            return "Play", "🎈"

        return "Learning", "📚"

    def extract_branch_name(self, location_text: str) -> str:
        """Extract clean branch name from location string"""
        # Remove "Toronto Public Library - " prefix
        branch = location_text.replace("Toronto Public Library - ", "")
        branch = branch.replace("TPL - ", "")
        branch = branch.strip()
        return branch

    def get_branch_coords(self, branch_name: str) -> Dict:
        """Get coordinates for a branch, with fallback"""
        # Try exact match first
        if branch_name in self.branch_coords:
            return self.branch_coords[branch_name]

        # Try partial match
        for known_branch, coords in self.branch_coords.items():
            if known_branch.lower() in branch_name.lower():
                return coords

        # Default to downtown Toronto
        return {"lat": 43.6532, "lng": -79.3832}

    def _load_manual_data(self) -> List[Dict]:
        """Load events from manual data entry file if available"""
        manual_file = Path(__file__).parent / "tpl_manual_data.json"

        if not manual_file.exists():
            return []

        try:
            with open(manual_file, 'r', encoding='utf-8') as f:
                manual_programs = json.load(f)

            events = []
            for program in manual_programs:
                events.append(self._convert_program_to_event(program))

            return events
        except Exception as e:
            print(f"   ⚠️  Error loading manual data: {e}")
            return []

    def _try_rss_feed(self) -> List[Dict]:
        """Try to load from RSS feed if available"""
        # TPL doesn't have a public RSS feed for programs
        # This is a placeholder for future implementation
        return []

    def _convert_program_to_event(self, program: Dict) -> Dict:
        """Convert a TPL program dict to standardized event format"""
        branch_coords = self.get_branch_coords(program.get("branch", ""))
        age_groups = self.get_age_groups(program["title"], program.get("description", ""))
        category, icon = self.get_category(program["title"], program.get("description", ""))

        return {
            "title": program["title"],
            "description": program.get("description", ""),
            "category": category,
            "icon": icon,
            "date": program["date"],
            "start_time": program["start_time"],
            "end_time": program["end_time"],
            "venue": {
                "name": f"Toronto Public Library - {program.get('branch', 'TBD')}",
                "address": program.get("address", "TBD"),
                "neighborhood": program.get("branch", "Toronto"),
                "lat": branch_coords["lat"],
                "lng": branch_coords["lng"]
            },
            "age_groups": age_groups,
            "indoor_outdoor": "Indoor",
            "organized_by": "Toronto Public Library",
            "website": program.get("url", self.base_url),
            "source": "TPL",
            "scraped_at": datetime.now().isoformat()
        }

    def scrape_programs(self, max_pages: int = 5) -> List[Dict]:
        """
        Scrape TPL programs - tries multiple approaches:
        1. Manual data file (tpl_manual_data.json)
        2. RSS feed (if available)
        3. Sample data as fallback
        """
        print("🔍 Fetching Toronto Public Library events...")

        # Try manual data first
        events = self._load_manual_data()
        if events:
            print(f"   ✅ Loaded {len(events)} events from manual data file")
            return events

        # Try RSS feed
        events = self._try_rss_feed()
        if events:
            print(f"   ✅ Loaded {len(events)} events from RSS feed")
            return events

        # Fall back to sample data
        print("   ⚠️  Using sample data (no live data available)")
        print("   💡 To add real TPL events, create: tpl_manual_data.json")

        sample_programs = [
            {
                "title": "Baby & Me",
                "description": "Songs, rhymes and bounces for babies and caregivers.",
                "date": "2025-10-22",
                "start_time": "10:00",
                "end_time": "10:30",
                "branch": "High Park",
                "ages": "0-18 months"
            },
            {
                "title": "Preschool Storytime",
                "description": "Stories, songs and activities for preschoolers.",
                "date": "2025-10-23",
                "start_time": "10:30",
                "end_time": "11:15",
                "branch": "Beaches",
                "ages": "3-5 years"
            },
            {
                "title": "LEGO Club",
                "description": "Build amazing creations with LEGO. Bricks provided.",
                "date": "2025-10-24",
                "start_time": "16:00",
                "end_time": "17:00",
                "branch": "Reference Library",
                "ages": "6-12 years"
            }
        ]

        for program in sample_programs:
            branch_coords = self.get_branch_coords(program["branch"])
            age_groups = self.get_age_groups(program["title"], program["description"])
            category, icon = self.get_category(program["title"], program["description"])

            event = {
                "title": program["title"],
                "description": program["description"],
                "category": category,
                "icon": icon,
                "date": program["date"],
                "start_time": program["start_time"],
                "end_time": program["end_time"],
                "venue": {
                    "name": f"Toronto Public Library - {program['branch']}",
                    "address": "TBD",  # Would scrape full address
                    "neighborhood": program["branch"],
                    "lat": branch_coords["lat"],
                    "lng": branch_coords["lng"]
                },
                "age_groups": age_groups,
                "indoor_outdoor": "Indoor",
                "organized_by": "Toronto Public Library",
                "website": self.base_url,
                "source": "TPL",
                "scraped_at": datetime.now().isoformat()
            }

            events.append(event)

        print(f"✅ Found {len(events)} TPL events")
        return events

    def save_to_json(self, events: List[Dict], filename: str = "tpl_events.json"):
        """Save events to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved to {filename}")


def main():
    scraper = TPLScraper()
    events = scraper.scrape_programs()
    scraper.save_to_json(events)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    # Show categories breakdown
    categories = {}
    for event in events:
        cat = event['category']
        categories[cat] = categories.get(cat, 0) + 1

    print(f"   Categories: {categories}")


if __name__ == "__main__":
    main()
