#!/usr/bin/env python3
"""
Help! We've Got Kids Scraper
Fetches free kids/family events from Help! We've Got Kids Toronto
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
import re
import time
from bs4 import BeautifulSoup

class HelpWeveGotKidsScraper:
    def __init__(self):
        self.base_url = "https://helpwevegotkids.com"
        self.events_url = f"{self.base_url}/toronto/events/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        }

    def fetch_events(self, days_ahead: int = 30) -> List[Dict]:
        """Fetch free kids/family events from Help! We've Got Kids"""

        print("🎈 Fetching from Help! We've Got Kids...")

        try:
            # Use a session for better cookie/header handling
            session = requests.Session()
            session.headers.update(self.headers)

            # Add a small delay to be polite
            time.sleep(1)

            response = session.get(
                self.events_url,
                timeout=20,
                allow_redirects=True
            )

            if response.status_code != 200:
                print(f"   ⚠️  HTTP {response.status_code} - trying alternate approach")
                # Try without some headers that might trigger protection
                simple_headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
                time.sleep(2)
                response = requests.get(self.events_url, headers=simple_headers, timeout=20)

                if response.status_code != 200:
                    print(f"   ⚠️  Still getting HTTP {response.status_code} - site may have bot protection")
                    return []

            soup = BeautifulSoup(response.content, 'html.parser')
            events = []

            # The site uses WordPress with Event Organiser plugin
            # Look for event posts
            event_items = soup.find_all('div', class_=lambda x: x and ('event' in str(x).lower() or 'eo-event' in str(x).lower()))

            if not event_items:
                # Try finding all article or post elements
                event_items = soup.find_all(['article', 'div'], class_=lambda x: x and 'post' in str(x).lower())

            for item in event_items[:30]:  # Limit to first 30 events
                parsed = self._parse_event_item(item, soup)
                if parsed:
                    events.append(parsed)

            if events:
                print(f"   ✅ Found {len(events)} events from Help! We've Got Kids")
            else:
                print(f"   ⚠️  No events found - site may use JavaScript rendering")

            return events

        except requests.exceptions.RequestException as e:
            print(f"   ❌ Network error: {e}")
            return []
        except Exception as e:
            print(f"   ❌ Error fetching Help! We've Got Kids events: {e}")
            return []

    def _parse_event_item(self, item, soup) -> Dict:
        """Parse an individual event item"""

        try:
            # Extract title
            title_elem = item.find(['h2', 'h3', 'h4', 'a'])
            if not title_elem:
                return None

            title = title_elem.get_text(strip=True)

            # Filter for kids relevance and free events
            if not self._is_kids_relevant(title):
                return None

            if not self._is_free(title, item.get_text()):
                return None

            # Get event detail URL
            link_elem = item.find('a', href=True)
            event_url = link_elem['href'] if link_elem else None
            if event_url and not event_url.startswith('http'):
                event_url = f"{self.base_url}{event_url}"

            # Try to extract date from text
            event_date = self._extract_date(item.get_text())
            if not event_date:
                # Default to upcoming weekend
                today = datetime.now().date()
                days_ahead = (5 - today.weekday()) % 7  # Next Saturday
                event_date = (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')

            # Extract location if possible
            venue_name = "Toronto Area"
            address = "Toronto, ON"

            # Determine category and age groups
            age_groups = self._determine_age_groups(title)
            category, icon = self._determine_category(title)

            # Get coordinates (default to Toronto center)
            lat, lng = 43.6532, -79.3832

            # Build event dict
            event_dict = {
                "title": title,
                "description": f"Free family event from Help! We've Got Kids",
                "category": category,
                "icon": icon,
                "date": event_date,
                "start_time": "10:00",
                "end_time": "12:00",
                "venue": {
                    "name": venue_name,
                    "address": address,
                    "neighborhood": "Toronto",
                    "lat": lat,
                    "lng": lng
                },
                "age_groups": age_groups,
                "indoor_outdoor": "Indoor",
                "organized_by": "Help! We've Got Kids",
                "website": event_url or self.events_url,
                "source": "HelpWeveGotKids",
                "scraped_at": datetime.now().isoformat(),
                "is_free": True
            }

            return event_dict

        except Exception as e:
            return None

    def _fetch_event_detail(self, url: str) -> Dict:
        """Fetch details for a specific event"""
        # Placeholder for detailed event scraping
        # This would fetch individual event pages
        return None

    def _extract_date(self, text: str) -> str:
        """Extract date from text"""
        # Look for date patterns
        date_patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
            r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',  # Month DD, YYYY
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    if '/' in pattern:
                        month, day, year = match.groups()
                        date_obj = datetime(int(year), int(month), int(day))
                    else:
                        month_str, day, year = match.groups()
                        date_obj = datetime.strptime(f"{month_str} {day} {year}", "%B %d %Y")

                    return date_obj.strftime('%Y-%m-%d')
                except:
                    continue

        return None

    def _is_free(self, title: str, text: str) -> bool:
        """Check if event is free"""
        combined = (title + ' ' + text).lower()

        # Look for free indicators
        if any(word in combined for word in ['free', 'no cost', 'complimentary', 'admission free']):
            return True

        # Exclude paid events
        if any(word in combined for word in ['$', 'ticket', 'admission:', 'cost:', 'price:']):
            return False

        # Default to considering it potentially free (will be filtered by aggregator if needed)
        return True

    def _is_kids_relevant(self, title: str) -> bool:
        """Check if event is relevant to kids/families"""
        text = title.lower()

        # Filter out adult-only events
        adult_keywords = ['wine', 'beer', 'cocktail', 'singles', '19+', '18+', 'adults only']
        if any(keyword in text for keyword in adult_keywords):
            return False

        # Most events on Help! We've Got Kids are kid-relevant
        return True

    def _determine_age_groups(self, title: str) -> List[str]:
        """Determine age groups from event title"""
        text = title.lower()
        age_groups = []

        if any(word in text for word in ['baby', 'babies', 'infant', '0-2']):
            age_groups.append("Babies (0-2)")

        if any(word in text for word in ['toddler', 'preschool', '2-5', '3-5']):
            age_groups.append("Toddlers (3-5)")

        if any(word in text for word in ['kids', 'children', '6-12', 'elementary']):
            age_groups.append("Kids (6-12)")

        if any(word in text for word in ['teen', 'youth', '13-17']):
            age_groups.append("Teens (13-17)")

        if any(word in text for word in ['family', 'all ages', 'everyone']):
            age_groups.append("All Ages")

        return age_groups if age_groups else ["All Ages"]

    def _determine_category(self, title: str) -> tuple:
        """Determine category and icon"""
        text = title.lower()

        if any(word in text for word in ['art', 'craft', 'paint', 'draw', 'create']):
            return "Arts", "🎨"
        if any(word in text for word in ['music', 'concert', 'sing', 'dance', 'performance']):
            return "Entertainment", "🎵"
        if any(word in text for word in ['sport', 'play', 'active', 'swim', 'skate']):
            return "Sports", "⚽"
        if any(word in text for word in ['science', 'stem', 'tech', 'robot', 'coding', 'learn']):
            return "Learning", "🔬"
        if any(word in text for word in ['story', 'book', 'read', 'library']):
            return "Learning", "📚"
        if any(word in text for word in ['nature', 'outdoor', 'park', 'hike', 'trail']):
            return "Nature", "🌳"
        if any(word in text for word in ['halloween', 'trick', 'treat', 'spooky']):
            return "Entertainment", "🎃"

        return "Entertainment", "🎉"


def main():
    scraper = HelpWeveGotKidsScraper()
    events = scraper.fetch_events(days_ahead=30)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    # Save to JSON
    with open('helpwevegotkids_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to helpwevegotkids_events.json")


if __name__ == "__main__":
    main()
