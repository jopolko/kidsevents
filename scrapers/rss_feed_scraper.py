#!/usr/bin/env python3
"""
RSS Feed Scraper
Parses RSS feeds from various Toronto organizations for kids events
"""

import feedparser
import json
from datetime import datetime, timedelta
from typing import List, Dict
import re

class RSSFeedScraper:
    def __init__(self):
        # RSS feeds from Toronto organizations
        self.feeds = [
            {
                'url': 'https://www.rom.on.ca/en/whats-on/rss',
                'name': 'Royal Ontario Museum',
                'category': 'Learning',
                'address': '100 Queens Park',
                'lat': 43.6677,
                'lng': -79.3948
            },
            {
                'url': 'https://ontariosciencecentre.ca/feed/',
                'name': 'Ontario Science Centre',
                'category': 'Learning',
                'address': '770 Don Mills Rd',
                'lat': 43.7166,
                'lng': -79.3381
            },
            {
                'url': 'https://ago.ca/events/feed',
                'name': 'Art Gallery of Ontario',
                'category': 'Arts',
                'address': '317 Dundas St W',
                'lat': 43.6536,
                'lng': -79.3925
            },
            {
                'url': 'https://www.toronto.ca/feed/',
                'name': 'City of Toronto',
                'category': 'Entertainment',
                'address': 'Various Locations',
                'lat': 43.6532,
                'lng': -79.3832
            },
            {
                'url': 'https://harbourfrontcentre.com/events/feed/',
                'name': 'Harbourfront Centre',
                'category': 'Arts',
                'address': '235 Queens Quay W',
                'lat': 43.6385,
                'lng': -79.3817
            }
        ]

    def fetch_events(self, days_ahead: int = 30) -> List[Dict]:
        """Fetch events from RSS feeds"""

        print("📰 Fetching from RSS feeds...")

        all_events = []
        today = datetime.now()
        end_date = today + timedelta(days=days_ahead)

        for feed_info in self.feeds:
            try:
                events = self._parse_feed(feed_info, today, end_date)
                all_events.extend(events)
                print(f"   Found {len(events)} events from {feed_info['name']}")
            except Exception as e:
                print(f"   ⚠️  Error with {feed_info['name']}: {e}")

        print(f"   ✅ Found {len(all_events)} RSS feed events")
        return all_events

    def _parse_feed(self, feed_info: Dict, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Parse a single RSS feed"""
        events = []

        try:
            feed = feedparser.parse(feed_info['url'])

            for entry in feed.entries:
                try:
                    # Get title and description
                    title = entry.get('title', '').strip()
                    if not title:
                        continue

                    description = entry.get('summary', entry.get('description', ''))

                    # Check if kid-relevant
                    if not self._is_kids_relevant(title, description):
                        continue

                    # Try to parse date
                    event_date = None
                    if hasattr(entry, 'published_parsed'):
                        event_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed'):
                        event_date = datetime(*entry.updated_parsed[:6])

                    # Try to extract date from description
                    if not event_date:
                        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', description)
                        if date_match:
                            event_date = datetime(int(date_match.group(1)),
                                                 int(date_match.group(2)),
                                                 int(date_match.group(3)))

                    # Default to upcoming weekend if no date found
                    if not event_date:
                        event_date = start_date

                    # Filter by date range
                    if event_date < start_date or event_date > end_date:
                        continue

                    # Get URL
                    url = entry.get('link', '')

                    # Determine category and age groups
                    category = feed_info.get('category', 'Entertainment')
                    icon = self._get_icon(category)
                    age_groups = self._determine_age_groups(title, description)

                    # Check if free
                    if not self._is_free(title, description):
                        continue

                    event = {
                        "title": title,
                        "description": self._clean_description(description),
                        "category": category,
                        "icon": icon,
                        "date": event_date.strftime('%Y-%m-%d'),
                        "start_time": "10:00",
                        "end_time": "16:00",
                        "venue": {
                            "name": feed_info['name'],
                            "address": feed_info.get('address', 'Toronto, ON'),
                            "neighborhood": "Toronto",
                            "lat": feed_info.get('lat', 43.6532),
                            "lng": feed_info.get('lng', -79.3832)
                        },
                        "age_groups": age_groups,
                        "indoor_outdoor": "Indoor",
                        "organized_by": feed_info['name'],
                        "website": url,
                        "source": "RSS",
                        "scraped_at": datetime.now().isoformat()
                    }

                    events.append(event)

                except Exception:
                    continue

        except Exception:
            pass

        return events

    def _is_kids_relevant(self, title: str, description: str) -> bool:
        """Check if relevant to kids"""
        text = (title + " " + description).lower()

        keywords = [
            'kid', 'kids', 'child', 'children', 'family', 'families',
            'baby', 'babies', 'toddler', 'youth', 'junior',
            'all ages', 'everyone'
        ]

        return any(keyword in text for keyword in keywords)

    def _is_free(self, title: str, description: str) -> bool:
        """Check if free"""
        text = (title + " " + description).lower()

        # If mentions cost/price/admission without "free", skip it
        if any(word in text for word in ['$', 'cost', 'price', 'admission', 'ticket']):
            if 'free' not in text:
                return False

        return True

    def _determine_age_groups(self, title: str, description: str) -> List[str]:
        """Determine age groups"""
        text = (title + " " + description).lower()
        age_groups = []

        if any(word in text for word in ['baby', 'babies', 'infant']):
            age_groups.append("Babies (0-2)")
        if any(word in text for word in ['toddler', 'preschool']):
            age_groups.append("Toddlers (3-5)")
        if any(word in text for word in ['kids', 'children', 'elementary']):
            age_groups.append("Kids (6-12)")
        if any(word in text for word in ['teen', 'youth']):
            age_groups.append("Teens (13-17)")
        if any(word in text for word in ['family', 'all ages']):
            age_groups.append("All Ages")

        return age_groups if age_groups else ["All Ages"]

    def _get_icon(self, category: str) -> str:
        """Get icon for category"""
        icons = {
            'Learning': '🔬',
            'Arts': '🎨',
            'Entertainment': '🎭',
            'Sports': '⚽',
            'Nature': '🌳'
        }
        return icons.get(category, '🎉')

    def _get_address(self, org_name: str) -> str:
        """Get address for known organizations"""
        addresses = {
            'Royal Ontario Museum': '100 Queens Park',
            'Ontario Science Centre': '770 Don Mills Rd'
        }
        return addresses.get(org_name, 'Toronto, ON')

    def _get_coords(self, org_name: str) -> tuple:
        """Get coordinates for known organizations"""
        coords = {
            'Royal Ontario Museum': (43.6677, -79.3948),
            'Ontario Science Centre': (43.7166, -79.3381)
        }
        return coords.get(org_name, (43.6532, -79.3832))

    def _clean_description(self, description: str) -> str:
        """Clean description"""
        import re
        clean = re.sub('<[^<]+?>', '', description)
        clean = re.sub(r'\s+', ' ', clean)
        if len(clean) > 200:
            clean = clean[:197] + "..."
        return clean.strip()


def main():
    scraper = RSSFeedScraper()
    events = scraper.fetch_events(days_ahead=30)

    print(f"\n📊 Summary:")
    print(f"   Total events: {len(events)}")

    with open('rss_feed_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to rss_feed_events.json")


if __name__ == "__main__":
    main()
