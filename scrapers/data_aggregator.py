#!/usr/bin/env python3
"""
Data Aggregator for Toronto Kids Events
Combines events from multiple sources, deduplicates, and outputs unified JSON
"""

import json
import sys
from datetime import datetime, timezone
from typing import List, Dict
import hashlib
from pathlib import Path

# Zero-cost deterministic description enricher (lives at the repo root).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from editorialize import enrich as _editorialize

# Import our scrapers
# TPL scraper removed 2026-06-18 - mill source, excluded from product (library = common knowledge)
from toronto_opendata_scraper import TorontoOpenDataScraper
from meetup_api_scraper import MeetupAPIScraper
from rss_feed_scraper import RSSFeedScraper
from community_events_scraper import CommunityEventsScraper
# EventBrite scraper removed - API deprecated public event search in Feb 2020
from museums_free_days_scraper import MuseumFreeDaysScraper
# EarlyON scraper removed 2026-06-18 - mill source, excluded from product
# ParksRec scraper removed 2026-06-18 - mill source, excluded from product
# ChatterBlock scraper removed 2026-06-18 - ToS-risky aggregator scrape (C&D risk)
from holistic_community_scraper import HolisticCommunityScraper
# ToDoCanada scraper removed - site has Cloudflare protection that requires JavaScript
from familyfun_scraper import FamilyFunScraper
from toronto_artisans_scraper import TorontoArtisansScraper
from targeted_audiences_scraper import TargetedAudiencesScraper
from community_centres_scraper import CommunityCentresScraper
from indoor_play_scraper import IndoorPlayScraper
from adventure_playgrounds_scraper import AdventurePlaygroundsScraper
from harbourfront_scraper import HarbourfrontScraper
from trca_scraper import TRCAScraper
from farmers_markets_scraper import FarmersMarketsScraper
# KidsOutAndAbout scraper removed 2026-06-18 - ToS-risky aggregator scrape (C&D risk)
from indoor_play_centers_scraper import IndoorPlayCentersScraper
# HelpWeveGotKids scraper removed 2026-06-18 - ToS-risky aggregator scrape (C&D risk)
# BlogTO scraper removed 2026-06-18 - ToS-risky aggregator scrape (C&D risk)
# TodaysParent scraper removed - site has Cloudflare protection that requires JavaScript
from likeadad_scraper import LikeADadScraper
# BIA scraper removed - all 4 BIA websites have broken/changed URLs
from moca_scraper import MOCAScraper
from mississauga_scraper import MississaugaScraper
from tinytown_scraper import TinyTownScraper
from stonegate_scraper import StonegateScraper
from artsetobicoke_scraper import ArtsEtobicokeScraper
from westnh_scraper import WestNHScraper
from toronto_opendata_api_scraper import TorontoOpenDataScraper
from evergreen_brickworks_scraper import EvergreenBrickWorksScraper
from rom_scraper import ROMScraper
from ago_scraper import AGOScraper
from agakhan_scraper import AgaKhanMuseumScraper
from highpark_scraper import HighParkScraper
from fortyork_scraper import FortYorkScraper
from tribe_scraper import TribeScraper
from jsonld_scraper import JsonLdScraper
from activenet_scraper import ActiveNetScraper
from place_id_lookup import PlaceIDLookup


class DataAggregator:
    def __init__(self):
        self.events = []
        self.seen_hashes = set()
        self.place_id_lookup = PlaceIDLookup()

    def generate_event_hash(self, event: Dict) -> str:
        """Generate unique hash for event to detect duplicates"""
        # Use title, date, start_time, and venue to identify duplicates
        key = f"{event['title']}_{event['date']}_{event['start_time']}_{event['venue']['name']}"
        return hashlib.md5(key.lower().encode()).hexdigest()

    def is_duplicate(self, event: Dict) -> bool:
        """Check if event is a duplicate"""
        event_hash = self.generate_event_hash(event)
        if event_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(event_hash)
        return False

    def add_events(self, events: List[Dict], source: str):
        """Add events from a source, checking for duplicates"""
        added = 0
        duplicates = 0

        for event in events:
            # Ensure source is set
            event['source'] = source

            # Add unique ID if not present
            if 'id' not in event:
                event['id'] = self.generate_event_hash(event)

            if not self.is_duplicate(event):
                self.events.append(event)
                added += 1
            else:
                duplicates += 1

        print(f"   ✅ Added {added} events from {source}")
        if duplicates > 0:
            print(f"   ⚠️  Skipped {duplicates} duplicates")

        return added

    def filter_past_events(self):
        """Remove events that have already passed"""
        today = datetime.now().date()
        before_count = len(self.events)

        self.events = [
            event for event in self.events
            if datetime.strptime(event['date'], '%Y-%m-%d').date() >= today
        ]

        removed = before_count - len(self.events)
        if removed > 0:
            print(f"   🗑️  Removed {removed} past events")

    def sort_events(self):
        """Order by date, then interleave sources within each date (round-robin)
        so one high-volume source (EarlyON) can't form a long unbroken run."""
        from collections import defaultdict, deque
        by_date = defaultdict(list)
        for e in self.events:
            by_date[e.get('date','')].append(e)
        out = []
        for date in sorted(by_date):
            src = defaultdict(deque)
            for e in sorted(by_date[date], key=lambda x: x.get('start_time') or ''):
                src[e.get('source','?')].append(e)
            queues = list(src.values())
            while queues:
                for q in list(queues):
                    out.append(q.popleft())
                    if not q:
                        queues.remove(q)
        self.events = out

    def validate_events(self):
        """Validate event data and fix common issues"""
        validated = []

        for event in self.events:
            # Required fields
            if not all(key in event for key in ['title', 'date', 'start_time', 'venue']):
                print(f"   ⚠️  Skipping invalid event: {event.get('title', 'Unknown')}")
                continue

            # Ensure age_groups is a list
            if 'age_groups' not in event or not event['age_groups']:
                event['age_groups'] = ['All Ages']

            # Ensure category and icon exist
            if 'category' not in event:
                event['category'] = 'Entertainment'
            if 'icon' not in event:
                event['icon'] = '🎉'

            # Ensure indoor_outdoor is set
            if 'indoor_outdoor' not in event:
                event['indoor_outdoor'] = 'Indoor'

            # Ensure organized_by is set
            if 'organized_by' not in event:
                event['organized_by'] = 'Community Event'

            # Add default website if missing
            if 'website' not in event:
                event['website'] = None

            validated.append(event)

        skipped = len(self.events) - len(validated)
        if skipped > 0:
            print(f"   ⚠️  Skipped {skipped} invalid events")

        self.events = validated

    def enrich_with_place_ids(self):
        """Enrich venues with Google Place IDs for precise map locations"""
        print("📍 Enriching venues with Google Place IDs...")

        enriched_count = 0
        debug_count = 0
        for event in self.events:
            # Skip events without venues
            if 'venue' not in event or not event['venue']:
                continue

            venue = event['venue']

            # Only enrich if we don't already have a place_id
            if 'place_id' not in venue:
                # Enrich venue in place (modifies the dict directly)
                self.place_id_lookup.enrich_venue(venue)
                if venue.get('place_id'):
                    enriched_count += 1
                    # Debug: Show first 3 enrichments
                    if debug_count < 3:
                        print(f"   DEBUG: Enriched {venue.get('name')} with {venue.get('place_id')}")
                        debug_count += 1

        # Final check: How many events actually have place_ids?
        final_count = sum(1 for e in self.events if e.get('venue', {}).get('place_id'))
        print(f"   ✅ Enriched {enriched_count} venues with Place IDs")
        print(f"   🔍 Final verification: {final_count} events have place_id in venue")
        self.place_id_lookup.print_stats()

    def get_statistics(self) -> Dict:
        """Generate statistics about aggregated events"""
        stats = {
            'total_events': len(self.events),
            'sources': {},
            'categories': {},
            'age_groups': {},
            'date_range': {}
        }

        # Count by source
        for event in self.events:
            source = event.get('source', 'Unknown')
            stats['sources'][source] = stats['sources'].get(source, 0) + 1

        # Count by category
        for event in self.events:
            category = event.get('category', 'Unknown')
            stats['categories'][category] = stats['categories'].get(category, 0) + 1

        # Count by age group
        for event in self.events:
            for age in event.get('age_groups', []):
                stats['age_groups'][age] = stats['age_groups'].get(age, 0) + 1

        # Date range
        if self.events:
            dates = [event['date'] for event in self.events]
            stats['date_range'] = {
                'earliest': min(dates),
                'latest': max(dates)
            }

        return stats

    def editorialize_events(self):
        """Rewrite thin/boilerplate descriptions from each event's structured
        fields (venue, neighbourhood, ages, day/time, free). Zero-cost and
        deterministic; genuine scraper copy is preserved; idempotent."""
        n = 0
        for e in self.events:
            try:
                new = _editorialize(e)
                if new and new != e.get('description'):
                    e['description'] = new
                    n += 1
            except Exception:
                pass  # never let editorialization break a save
        print(f"✍️  Editorialized {n} thin descriptions")

    def save_to_json(self, filename: str = "events.json"):
        """Save aggregated events to JSON file"""
        self.editorialize_events()
        output = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'total_events': len(self.events),
            'events': self.events
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"💾 Saved {len(self.events)} events to {filename}")

    def save_separate_files(self):
        """Save events to multiple files for easier management"""
        self.editorialize_events()
        # DEBUG: Check place_ids before saving
        debug_count = sum(1 for e in self.events if e.get('venue', {}).get('place_id'))
        print(f"   DEBUG: Before saving - {debug_count} events have place_id")

        # Main events file (for production) - save with metadata in both locations
        output = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'total_events': len(self.events),
            'events': self.events
        }

        with open('events.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        # Also save to parent directory for web server access
        parent_dir = Path(__file__).parent.parent
        with open(parent_dir / 'events.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        # DEBUG: Verify after saving
        with open(parent_dir / 'events.json', 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            saved_count = sum(1 for e in saved_data['events'] if e.get('venue', {}).get('place_id'))
            print(f"   DEBUG: After saving - {saved_count} events have place_id in file")

        # Events with metadata (for debugging)
        output = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'total_events': len(self.events),
            'statistics': self.get_statistics(),
            'events': self.events
        }

        with open('events_full.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"💾 Saved to events.json, events_full.json, and ../events.json")

    def save_metadata(self):
        """Save lightweight metadata file for SEO and page meta tags"""
        from datetime import datetime, timedelta

        # Calculate unique venues
        unique_venues = set()
        for event in self.events:
            venue = event.get('venue', {})
            venue_name = venue.get('name', '')
            if venue_name:
                unique_venues.add(venue_name)

        # Get date range (next 7 days)
        today = datetime.now().date()
        next_week = today + timedelta(days=7)

        # Filter events for next 7 days
        week_events = [
            e for e in self.events
            if e.get('date') and today <= datetime.strptime(e['date'], '%Y-%m-%d').date() < next_week
        ]

        # Calculate unique venues for next 7 days
        week_venues = set()
        for event in week_events:
            venue = event.get('venue', {})
            venue_name = venue.get('name', '')
            if venue_name:
                week_venues.add(venue_name)

        metadata = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'total_events': len(week_events),
            'total_venues': len(week_venues),
            'date_range': {
                'start': today.strftime('%Y-%m-%d'),
                'end': next_week.strftime('%Y-%m-%d')
            },
            'human_readable': {
                'events': f"{len(week_events):,}",
                'venues': f"{len(week_venues):,}",
                'date_generated': datetime.now().strftime('%B %d, %Y')
            }
        }

        # Save to scrapers directory
        with open('metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, separators=(',', ':'))

        # Save to parent directory for web access
        parent_dir = Path(__file__).parent.parent
        with open(parent_dir / 'metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, separators=(',', ':'))

        print(f"📊 Saved metadata: {len(week_events):,} events at {len(week_venues):,} venues (next 7 days)")


def main():
    print("=" * 60)
    print("🎯 Toronto Kids Events Data Aggregator")
    print("=" * 60)
    print()

    aggregator = DataAggregator()

    # 1. Fetch from Holistic Community Events (Indigenous, multicultural, nature-based, hippie mom stuff)
    print("🌿 Fetching from Holistic Community Events...")
    try:
        holistic_scraper = HolisticCommunityScraper()
        holistic_events = holistic_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(holistic_events, 'HolisticCommunity')
    except Exception as e:
        print(f"   ❌ Error fetching Holistic Community Events: {e}")

    print()

    # 2. DISABLED - Generated/manually curated data, not real scraped events
    # print("🎪 Fetching from Community Events...")
    # try:
    #     community_scraper = CommunityEventsScraper()
    #     community_events = community_scraper.fetch_events()
    #     aggregator.add_events(community_events, 'Community')
    # except Exception as e:
    #     print(f"   ❌ Error fetching Community Events: {e}")

    print()

    # 2. Fetch from Toronto City Events (actual time-specific events!)
    print("🏛️  Fetching from Toronto City Events...")
    try:
        from toronto_events_scraper import TorontoEventsScraper
        toronto_scraper = TorontoEventsScraper()
        toronto_events = toronto_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(toronto_events, 'TorontoEvents')
    except Exception as e:
        print(f"   ❌ Error fetching Toronto Events: {e}")

    print()

    # 2. TPL removed 2026-06-18 - mill source, excluded from product (library = common knowledge)

    print()

    # 3. Fetch from Museums & Cultural Centers Free Days
    print("🏛️  Fetching from Museums & Cultural Centers...")
    try:
        museums_scraper = MuseumFreeDaysScraper()
        museums_events = museums_scraper.fetch_events(months_ahead=1)
        # Don't override source - use the source from each event
        for event in museums_events:
            aggregator.add_events([event], event.get('source', 'Museums'))
    except Exception as e:
        print(f"   ❌ Error fetching Museum events: {e}")

    print()

    # 4. EarlyON removed 2026-06-18 - mill source, excluded from product

    print()

    # 5. Parks & Rec removed 2026-06-18 - mill source, excluded from product

    print()

    # 6. ChatterBlock removed 2026-06-18 - ToS-risky aggregator scrape (C&D risk)

    print()

    # 7. REMOVED - EventBrite (API deprecated public event search in Feb 2020)
    # The /v3/events/search/ endpoint no longer exists - only private events accessible

    print()

    # 8. REMOVED - To Do Canada (Cloudflare protection requires JavaScript/headless browser)
    # Site returns 403 with challenge page that cannot be bypassed with simple HTTP requests

    print()

    # 9. Fetch from Family Fun Canada (weekend family activities)
    print("👨‍👩‍👧‍👦 Fetching from Family Fun Canada...")
    try:
        familyfun_scraper = FamilyFunScraper()
        familyfun_events = familyfun_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(familyfun_events, 'FamilyFun')
    except Exception as e:
        print(f"   ❌ Error fetching Family Fun Canada events: {e}")

    print()

    # 10. DISABLED - Generated fake artisan workshop data
    # print("🎨 Fetching from Toronto Artisans...")
    # try:
    #     artisans_scraper = TorontoArtisansScraper()
    #     artisan_events = artisans_scraper.generate_artisan_events(days_ahead=7)
    #     aggregator.add_events(artisan_events, 'Artisans')
    # except Exception as e:
    #     print(f"   ❌ Error fetching Artisan events: {e}")

    # print()

    # 11. DISABLED - Generated fake targeted audience data
    # print("🎯 Fetching from Targeted Audience Programs...")
    # try:
    #     targeted_scraper = TargetedAudiencesScraper()
    #     targeted_events = targeted_scraper.generate_targeted_events(days_ahead=7)
    #     aggregator.add_events(targeted_events, 'TargetedAudiences')
    # except Exception as e:
    #     print(f"   ❌ Error fetching Targeted Audience events: {e}")

    print()

    # 5. Fetch from Meetup API (disabled - returns 0 events)
    # print("👥 Fetching from Meetup API...")
    # try:
    #     meetup_scraper = MeetupAPIScraper()
    #     meetup_events = meetup_scraper.fetch_events()
    #     aggregator.add_events(meetup_events, 'Meetup')
    # except Exception as e:
    #     print(f"   ❌ Error fetching Meetup events: {e}")

    # print()

    # 6. Fetch from RSS Feeds (disabled - returns 0 events)
    # print("📰 Fetching from RSS feeds...")
    # try:
    #     rss_scraper = RSSFeedScraper()
    #     rss_events = rss_scraper.fetch_events()
    #     aggregator.add_events(rss_events, 'RSS')
    # except Exception as e:
    #     print(f"   ❌ Error fetching RSS events: {e}")

    print()

    # 13. DISABLED - Generated fake community centre programs
    # print("🏢 Fetching from Community Centres...")
    # try:
    #     cc_scraper = CommunityCentresScraper()
    #     cc_events = cc_scraper.fetch_events(days_ahead=7)
    #     aggregator.add_events(cc_events, 'CommunityCentres')
    # except Exception as e:
    #     print(f"   ❌ Error fetching Community Centre events: {e}")

    # print()

    # 14. DISABLED - Generated fake indoor play hours
    # print("🎪 Fetching from Indoor Play Centres & Trampoline Parks...")
    # try:
    #     indoor_play_scraper = IndoorPlayScraper()
    #     indoor_play_events = indoor_play_scraper.fetch_events(days_ahead=7)
    #     aggregator.add_events(indoor_play_events, 'IndoorPlay')
    # except Exception as e:
    #     print(f"   ❌ Error fetching Indoor Play events: {e}")

    # print()

    # 15. DISABLED - Generated fake playground availability
    # print("🏰 Fetching from Adventure Playgrounds...")
    # try:
    #     adventure_scraper = AdventurePlaygroundsScraper()
    #     adventure_events = adventure_scraper.fetch_events(days_ahead=7)
    #     aggregator.add_events(adventure_events, 'AdventurePlaygrounds')
    # except Exception as e:
    #     print(f"   ❌ Error fetching Adventure Playground events: {e}")

    print()

    # 16. Fetch from Harbourfront Centre (free AND paid events)
    print("🌊 Fetching from Harbourfront Centre...")
    try:
        harbourfront_scraper = HarbourfrontScraper()
        harbourfront_events = harbourfront_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(harbourfront_events, 'Harbourfront')
    except Exception as e:
        print(f"   ❌ Error fetching Harbourfront events: {e}")

    print()

    # 17. DISABLED - Generated fake conservation area events
    # print("🌲 Fetching from Toronto & Region Conservation Authority...")
    # try:
    #     trca_scraper = TRCAScraper()
    #     trca_events = trca_scraper.fetch_events(days_ahead=7)
    #     aggregator.add_events(trca_events, 'TRCA')
    # except Exception as e:
    #     print(f"   ❌ Error fetching TRCA events: {e}")

    # print()

    # 18. DISABLED - Generated fake farmers market hours
    # print("🥕 Fetching from Toronto Farmers' Markets...")
    # try:
    #     farmers_markets_scraper = FarmersMarketsScraper()
    #     farmers_markets_events = farmers_markets_scraper.fetch_events(days_ahead=7)
    #     aggregator.add_events(farmers_markets_events, 'FarmersMarkets')
    # except Exception as e:
    #     print(f"   ❌ Error fetching Farmers Markets events: {e}")

    print()

    # 19. KidsOutAndAbout removed 2026-06-18 - ToS-risky aggregator scrape (C&D risk)

    print()

    # 20. DISABLED - Generated fake indoor play drop-in hours
    # print("🏰 Fetching from Indoor Play Centers (drop-in hours)...")
    # try:
    #     indoor_play_centers_scraper = IndoorPlayCentersScraper()
    #     indoor_play_centers_events = indoor_play_centers_scraper.fetch_events(days_ahead=7)
    #     aggregator.add_events(indoor_play_centers_events, 'IndoorPlayCenters')
    # except Exception as e:
    #     print(f"   ❌ Error fetching Indoor Play Centers events: {e}")

    print()

    # 21. Help! We've Got Kids removed 2026-06-18 - ToS-risky aggregator scrape (C&D risk)

    print()

    # 22. BlogTO removed 2026-06-18 - ToS-risky aggregator scrape (C&D risk)

    print()

    # 23. REMOVED - Today's Parent (Cloudflare protection requires JavaScript/headless browser)
    # Site returns 403 with challenge page that cannot be bypassed with simple HTTP requests

    print()

    # 24. Fetch from Like A Dad
    print("👨‍👧 Fetching from Like A Dad GTA...")
    try:
        likeadad_scraper = LikeADadScraper()
        likeadad_events = likeadad_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(likeadad_events, 'LikeADad')
    except Exception as e:
        print(f"   ❌ Error fetching Like A Dad events: {e}")

    print()

    # 25. REMOVED - Toronto BIAs (all 4 BIA websites have broken/changed URLs)
    # Beaches BIA: DNS failure, Bloor West Village: 404, Leslieville: 404, Kensington Market: redirects to homepage

    print()

    # 26. Fetch from MOCA Toronto
    print("🎨 Fetching from MOCA Toronto...")
    try:
        moca_scraper = MOCAScraper()
        moca_events = moca_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(moca_events, 'MOCA')
    except Exception as e:
        print(f"   ❌ Error fetching MOCA events: {e}")

    print()

    # 27. Fetch from Mississauga Events
    print("🏛️  Fetching from Mississauga Events...")
    try:
        mississauga_scraper = MississaugaScraper()
        mississauga_events = mississauga_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(mississauga_events, 'Mississauga')
    except Exception as e:
        print(f"   ❌ Error fetching Mississauga events: {e}")

    print()

    # 28. Fetch from Tiny Town Vaughan
    print("🎪 Fetching from Tiny Town Vaughan...")
    try:
        tinytown_scraper = TinyTownScraper()
        tinytown_events = tinytown_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(tinytown_events, 'TinyTown')
    except Exception as e:
        print(f"   ❌ Error fetching Tiny Town events: {e}")

    print()

    # 29. Fetch from Stonegate Community Health Centre (Etobicoke)
    print("👶 Fetching from Stonegate CHC Etobicoke...")
    try:
        stonegate_scraper = StonegateScraper()
        stonegate_events = stonegate_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(stonegate_events, 'StonegateCHC')
    except Exception as e:
        print(f"   ❌ Error fetching Stonegate CHC events: {e}")

    print()

    # 30. Fetch from Arts Etobicoke
    print("🎨 Fetching from Arts Etobicoke...")
    try:
        artsetobicoke_scraper = ArtsEtobicokeScraper()
        artsetobicoke_events = artsetobicoke_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(artsetobicoke_events, 'ArtsEtobicoke')
    except Exception as e:
        print(f"   ❌ Error fetching Arts Etobicoke events: {e}")

    print()

    # 31. Fetch from West Neighbourhood House (Little Portugal drop-in)
    print("🏘️  Fetching from West Neighbourhood House...")
    try:
        westnh_scraper = WestNHScraper()
        westnh_events = westnh_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(westnh_events, 'WestNH')
    except Exception as e:
        print(f"   ❌ Error fetching West Neighbourhood House events: {e}")

    print()

    # 32. Fetch from Toronto Open Data API (City of Toronto festivals & events)
    print("🏛️  Fetching from Toronto Open Data API...")
    try:
        toronto_opendata_scraper = TorontoOpenDataScraper()
        toronto_opendata_events = toronto_opendata_scraper.fetch_events(days_ahead=60)
        aggregator.add_events(toronto_opendata_events, 'TorontoOpenData')
    except Exception as e:
        print(f"   ❌ Error fetching Toronto Open Data events: {e}")

    print()

    # 33. Fetch from Evergreen Brick Works (free weekly events)
    print("🌳 Fetching from Evergreen Brick Works...")
    try:
        evergreen_scraper = EvergreenBrickWorksScraper()
        evergreen_events = evergreen_scraper.fetch_events(days_ahead=30)
        aggregator.add_events(evergreen_events, 'EvergreenBrickWorks')
    except Exception as e:
        print(f"   ❌ Error fetching Evergreen Brick Works events: {e}")

    print()

    # 34. Fetch from ROM (Third Tuesday Nights Free)
    print("🏛️  Fetching from ROM...")
    try:
        rom_scraper = ROMScraper()
        rom_events = rom_scraper.fetch_events(days_ahead=90)
        aggregator.add_events(rom_events, 'ROM')
    except Exception as e:
        print(f"   ❌ Error fetching ROM events: {e}")

    print()

    # 35. Fetch from AGO (First Wednesday Night Free)
    print("🎨 Fetching from AGO...")
    try:
        ago_scraper = AGOScraper()
        ago_events = ago_scraper.fetch_events(days_ahead=90)
        aggregator.add_events(ago_events, 'AGO')
    except Exception as e:
        print(f"   ❌ Error fetching AGO events: {e}")

    print()

    # 36. Fetch from Aga Khan Museum (Free Wednesdays + Family Sundays)
    print("🕌 Fetching from Aga Khan Museum...")
    try:
        agakhan_scraper = AgaKhanMuseumScraper()
        agakhan_events = agakhan_scraper.fetch_events(days_ahead=90)
        aggregator.add_events(agakhan_events, 'AgaKhanMuseum')
    except Exception as e:
        print(f"   ❌ Error fetching Aga Khan Museum events: {e}")

    print()

    # 37. Fetch from High Park (Free Zoo + Nature Centre)
    print("🌳 Fetching from High Park...")
    try:
        highpark_scraper = HighParkScraper()
        highpark_events = highpark_scraper.fetch_events(days_ahead=90)
        aggregator.add_events(highpark_events, 'HighPark')
    except Exception as e:
        print(f"   ❌ Error fetching High Park events: {e}")

    print()

    # 38. Fetch from Toronto History Museums (FREE admission)
    print("🏰 Fetching from Toronto History Museums...")
    try:
        fortyork_scraper = FortYorkScraper()
        fortyork_events = fortyork_scraper.fetch_events(days_ahead=90)
        aggregator.add_events(fortyork_events, 'TorontoHistoryMuseums')
    except Exception as e:
        print(f"   ❌ Error fetching Toronto History Museums events: {e}")

    print()

    # 39. Platform sweep: every venue on The Events Calendar (Tribe), from tribe_venues.json
    print("📅 Fetching from Tribe-platform venues...")
    try:
        tribe_events = TribeScraper().fetch_events(days_ahead=90)
        aggregator.add_events(tribe_events, 'Tribe')
    except Exception as e:
        print(f"   ❌ Error fetching Tribe venue events: {e}")

    print()

    # 40. Platform sweep: venues publishing schema.org Event JSON-LD (jsonld_venues.json)
    print("🧬 Fetching from JSON-LD venues...")
    try:
        jsonld_events = JsonLdScraper().fetch_events(days_ahead=90)
        aggregator.add_events(jsonld_events, 'JSONLD')
    except Exception as e:
        print(f"   ❌ Error fetching JSON-LD venue events: {e}")

    print()

    # 41. Platform sweep: municipal recreation on ActiveNet (activenet_tenants.json) - event-like kid items only
    print("🏊 Fetching from ActiveNet municipal recreation...")
    try:
        activenet_events = ActiveNetScraper().fetch_events(days_ahead=45)
        aggregator.add_events(activenet_events, 'ActiveNet')
    except Exception as e:
        print(f"   ❌ Error fetching ActiveNet events: {e}")

    print()

    # 39. Process events
    print("🔧 Processing events...")
    aggregator.filter_past_events()
    aggregator.validate_events()
    aggregator.enrich_with_place_ids()
    aggregator.sort_events()

    print()

    # 6. Generate statistics
    print("📊 Statistics:")
    stats = aggregator.get_statistics()
    print(f"   Total events: {stats['total_events']}")
    print(f"   Sources: {stats['sources']}")
    print(f"   Categories: {stats['categories']}")
    print(f"   Date range: {stats['date_range'].get('earliest')} to {stats['date_range'].get('latest')}")

    print()

    # 7. Save to files
    print("💾 Saving data...")
    aggregator.save_separate_files()
    aggregator.save_metadata()

    print()

    # 8. Split into weekly chunks for faster loading
    print("📅 Splitting events by week for faster loading...")
    try:
        from split_by_week import split_events_by_week
        split_events_by_week()
    except Exception as e:
        print(f"   ⚠️  Could not split by week: {e}")

    print()
    print("=" * 60)
    print("✅ Aggregation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
