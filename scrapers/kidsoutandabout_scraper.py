#!/usr/bin/env python3
"""
Kids Out and About Toronto Scraper
Fetches free kids/family events from Kids Out and About Toronto website
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
import re
from bs4 import BeautifulSoup

class KidsOutAndAboutScraper:
    def __init__(self):
        self.base_url = "https://toronto.kidsoutandabout.com"
        self.event_list_url = f"{self.base_url}/event-list"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def fetch_events(self, days_ahead: int = 30) -> List[Dict]:
        """Fetch free kids/family events from Kids Out and About Toronto"""

        print("🎪 Fetching from Kids Out and About Toronto...")

        try:
            response = requests.get(
                self.event_list_url,
                headers=self.headers,
                timeout=15
            )

            if response.status_code != 200:
                print(f"   ❌ Error: HTTP {response.status_code}")
                return []

            soup = BeautifulSoup(response.content, 'html.parser')
            events = []

            # Find all event items using the specific class pattern
            event_items = soup.find_all('div', class_='node-activity')

            for item in event_items:
                parsed = self._parse_event_item(item, soup)
                if parsed:
                    events.append(parsed)

            print(f"   ✅ Found {len(events)} events from Kids Out and About")
            return events

        except Exception as e:
            print(f"   ❌ Error fetching Kids Out and About events: {e}")
            return []

    def _parse_event_item(self, item, soup) -> Dict:
        """Parse an individual event item"""

        try:
            # Extract title from h2 tag within group-activity-details
            details_div = item.find('div', class_='group-activity-details')
            if not details_div:
                return None

            title_elem = details_div.find('h2')
            if not title_elem:
                return None

            title_link = title_elem.find('a')
            if not title_link:
                return None

            title = title_link.get_text(strip=True)
            if not title:
                return None

            event_url = title_link.get('href', '')
            if event_url and not event_url.startswith('http'):
                event_url = f"{self.base_url}{event_url}"

            # Extract location
            venue_name = "Toronto Area"
            address = "Toronto, ON"
            lat, lng = 43.6532, -79.3832

            contact_info = item.find('div', class_='field-name-field-contact-info')
            if contact_info:
                venue_link = contact_info.find('span', class_='fn')
                if venue_link:
                    venue_name = venue_link.get_text(strip=True)

                street = contact_info.find('div', class_='street-address')
                locality = contact_info.find('span', class_='locality')
                if street and locality:
                    address = f"{street.get_text(strip=True)}, {locality.get_text(strip=True)}, ON"

            # Extract dates
            dates_field = item.find('div', class_='field-field-activity-dates')
            if not dates_field:
                return None

            date_items = dates_field.find_all('span', class_='date-display-single')
            if not date_items:
                return None

            # Get first date
            first_date_text = date_items[0].get_text(strip=True)
            event_date = self._parse_date_string(first_date_text)
            if not event_date:
                return None

            # Extract time
            time_field = item.find('div', class_='field-name-field-time')
            start_time = "10:00"
            end_time = "12:00"

            if time_field:
                time_text = time_field.get_text(strip=True)
                start_time, end_time = self._parse_time(time_text)

            # Filter for kids relevance
            if not self._is_kids_relevant(title):
                return None

            # Check if free (look for pricing info)
            is_free = self._check_if_free(item)

            # Determine category and age groups
            age_groups = self._determine_age_groups(title)
            category, icon = self._determine_category(title)

            # Build event dict
            event_dict = {
                "title": title,
                "description": f"Event from Kids Out and About Toronto",
                "category": category,
                "icon": icon,
                "date": event_date,
                "start_time": start_time,
                "end_time": end_time,
                "venue": {
                    "name": venue_name,
                    "address": address,
                    "neighborhood": "Toronto",
                    "lat": lat,
                    "lng": lng
                },
                "age_groups": age_groups,
                "indoor_outdoor": "Indoor",
                "organized_by": "Kids Out and About Toronto",
                "website": event_url,
                "source": "KidsOutAndAbout",
                "scraped_at": datetime.now().isoformat(),
                "is_free": is_free
            }

            return event_dict

        except Exception as e:
            return None

    def _parse_date_string(self, date_str: str) -> str:
        """Parse MM/DD/YYYY format to YYYY-MM-DD"""
        try:
            # Format is MM/DD/YYYY
            parts = date_str.split('/')
            if len(parts) == 3:
                month, day, year = parts
                date_obj = datetime(int(year), int(month), int(day))
                return date_obj.strftime('%Y-%m-%d')
        except:
            pass
        return None

    def _check_if_free(self, item) -> bool:
        """Check if event is free by looking for price indicators"""
        text = item.get_text().lower()

        # Look for free indicators
        if any(word in text for word in ['free', 'no cost', 'no charge', 'complimentary']):
            return True

        # Look for price indicators
        if any(word in text for word in ['$', 'cost:', 'price:', 'ticket', 'admission:']):
            return False

        # Default to potentially free (will be shown to user)
        return True


    def _parse_time(self, time_text: str) -> tuple:
        """Parse time text to extract start and end times"""
        # Remove "Time:" prefix
        time_text = re.sub(r'^Time:\s*', '', time_text, flags=re.I)

        # Default times
        start_time = "10:00"
        end_time = "12:00"

        # Look for time patterns like "10 am - 6 pm" or "10:30 - 11:15"
        time_pattern = r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*-\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?'
        match = re.search(time_pattern, time_text, re.I)

        if match:
            start_hour = int(match.group(1))
            start_min = match.group(2) or "00"
            start_ampm = (match.group(3) or "am").lower()
            end_hour = int(match.group(4))
            end_min = match.group(5) or "00"
            end_ampm = (match.group(6) or start_ampm).lower()

            # Convert to 24-hour format
            if start_ampm == "pm" and start_hour != 12:
                start_hour += 12
            elif start_ampm == "am" and start_hour == 12:
                start_hour = 0

            if end_ampm == "pm" and end_hour != 12:
                end_hour += 12
            elif end_ampm == "am" and end_hour == 12:
                end_hour = 0

            start_time = f"{start_hour:02d}:{start_min}"
            end_time = f"{end_hour:02d}:{end_min}"

        return start_time, end_time

    def _is_kids_relevant(self, title: str) -> bool:
        """Check if event is relevant to kids/families"""
        text = title.lower()

        # Filter out adult-only events
        adult_keywords = ['wine', 'beer', 'cocktail', 'singles', '19+', '18+', 'adults only']
        if any(keyword in text for keyword in adult_keywords):
            return False

        # Most events on Kids Out and About are kid-relevant, but double-check
        kids_keywords = [
            'kid', 'kids', 'child', 'children', 'family', 'families',
            'baby', 'babies', 'infant', 'toddler', 'preschool',
            'youth', 'teen', 'junior', 'young', 'ages',
            'storytime', 'story', 'playtime', 'play',
            'craft', 'workshop', 'halloween', 'holiday'
        ]

        # If it's on Kids Out and About, default to True unless explicitly adult
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
    scraper = KidsOutAndAboutScraper()
    events = scraper.fetch_events(days_ahead=30)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    # Save to JSON
    with open('kidsoutandabout_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to kidsoutandabout_events.json")


if __name__ == "__main__":
    main()
