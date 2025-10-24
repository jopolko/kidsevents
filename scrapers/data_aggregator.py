#!/usr/bin/env python3
"""
Data Aggregator for Toronto Kids Events
Combines events from multiple sources, deduplicates, and outputs unified JSON
"""

import json
from datetime import datetime, timezone
from typing import List, Dict
import hashlib
from pathlib import Path

# Import our scrapers
from tpl_api_scraper import TPLAPIScraper
from toronto_opendata_scraper import TorontoOpenDataScraper
from meetup_api_scraper import MeetupAPIScraper
from rss_feed_scraper import RSSFeedScraper
from community_events_scraper import CommunityEventsScraper
from eventbrite_scraper import EventBriteScraper
from museums_free_days_scraper import MuseumFreeDaysScraper
from earlyon_scraper import EarlyONScraper
from parksrec_scraper import ParksRecScraper
from chatterblock_scraper import ChatterBlockScraper
from holistic_community_scraper import HolisticCommunityScraper
from todocanada_scraper import ToDoCanadaScraper
from familyfun_scraper import FamilyFunScraper
from toronto_artisans_scraper import TorontoArtisansScraper
from targeted_audiences_scraper import TargetedAudiencesScraper
from community_centres_scraper import CommunityCentresScraper
from indoor_play_scraper import IndoorPlayScraper
from adventure_playgrounds_scraper import AdventurePlaygroundsScraper
from harbourfront_scraper import HarbourfrontScraper
from trca_scraper import TRCAScraper
from farmers_markets_scraper import FarmersMarketsScraper
from kidsoutandabout_scraper import KidsOutAndAboutScraper
from indoor_play_centers_scraper import IndoorPlayCentersScraper
from helpwevegotkids_scraper import HelpWeveGotKidsScraper
from blogto_scraper import BlogTOScraper
from todaysparent_scraper import TodaysParentScraper
from likeadad_scraper import LikeADadScraper
from bia_scraper import BIAScraper
from moca_scraper import MOCAScraper
from mississauga_scraper import MississaugaScraper
from tinytown_scraper import TinyTownScraper
from stonegate_scraper import StonegateScraper
from artsetobicoke_scraper import ArtsEtobicokeScraper
from westnh_scraper import WestNHScraper


class DataAggregator:
    def __init__(self):
        self.events = []
        self.seen_hashes = set()

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
        """Sort events by date and time"""
        self.events.sort(key=lambda e: (e['date'], e['start_time']))

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

    def save_to_json(self, filename: str = "events.json"):
        """Save aggregated events to JSON file"""
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

    # 2. Fetch from Toronto Public Library (using real API)
    print("📚 Fetching from Toronto Public Library...")
    try:
        tpl_scraper = TPLAPIScraper()
        tpl_events = tpl_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(tpl_events, 'TPL')
    except Exception as e:
        print(f"   ❌ Error fetching TPL events: {e}")

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

    # 4. Fetch from EarlyON Centers (free drop-in programs for kids 0-6)
    print("👶 Fetching from EarlyON Centers...")
    try:
        earlyon_scraper = EarlyONScraper()
        earlyon_events = earlyon_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(earlyon_events, 'EarlyON')
    except Exception as e:
        print(f"   ❌ Error fetching EarlyON events: {e}")

    print()

    # 5. Fetch from Parks & Recreation (drop-in programs for all ages)
    print("🏃 Fetching from Parks & Recreation...")
    try:
        parksrec_scraper = ParksRecScraper()
        parksrec_events = parksrec_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(parksrec_events, 'ParksRec')
    except Exception as e:
        print(f"   ❌ Error fetching Parks & Rec events: {e}")

    print()

    # 6. Fetch from ChatterBlock (actual changing events - festivals, workshops, performances)
    print("🎪 Fetching from ChatterBlock...")
    try:
        chatterblock_scraper = ChatterBlockScraper()
        chatterblock_events = chatterblock_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(chatterblock_events, 'ChatterBlock')
    except Exception as e:
        print(f"   ❌ Error fetching ChatterBlock events: {e}")

    print()

    # 7. Fetch from EventBrite (requires API token)
    print("🎫 Fetching from EventBrite...")
    try:
        eventbrite_scraper = EventBriteScraper()
        eventbrite_events = eventbrite_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(eventbrite_events, 'EventBrite')
    except Exception as e:
        print(f"   ❌ Error fetching EventBrite events: {e}")

    print()

    # 8. Fetch from To Do Canada (curated family activities)
    print("🎪 Fetching from To Do Canada...")
    try:
        todocanada_scraper = ToDoCanadaScraper()
        todocanada_events = todocanada_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(todocanada_events, 'ToDoCanada')
    except Exception as e:
        print(f"   ❌ Error fetching To Do Canada events: {e}")

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

    # 19. Fetch from Kids Out and About Toronto
    print("🎪 Fetching from Kids Out and About Toronto...")
    try:
        kidsoutandabout_scraper = KidsOutAndAboutScraper()
        kidsoutandabout_events = kidsoutandabout_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(kidsoutandabout_events, 'KidsOutAndAbout')
    except Exception as e:
        print(f"   ❌ Error fetching Kids Out and About events: {e}")

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

    # 21. Fetch from Help! We've Got Kids (family events aggregator)
    print("🎈 Fetching from Help! We've Got Kids...")
    try:
        helpwevegotkids_scraper = HelpWeveGotKidsScraper()
        helpwevegotkids_events = helpwevegotkids_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(helpwevegotkids_events, 'HelpWeveGotKids')
    except Exception as e:
        print(f"   ❌ Error fetching Help! We've Got Kids events: {e}")

    print()

    # 22. Fetch from BlogTO Kids
    print("📰 Fetching from BlogTO Kids...")
    try:
        blogto_scraper = BlogTOScraper()
        blogto_events = blogto_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(blogto_events, 'BlogTO')
    except Exception as e:
        print(f"   ❌ Error fetching BlogTO events: {e}")

    print()

    # 23. Fetch from Today's Parent Toronto
    print("👨‍👩‍👧‍👦 Fetching from Today's Parent Toronto...")
    try:
        todaysparent_scraper = TodaysParentScraper()
        todaysparent_events = todaysparent_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(todaysparent_events, 'TodaysParent')
    except Exception as e:
        print(f"   ❌ Error fetching Today's Parent events: {e}")

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

    # 25. Fetch from Toronto BIAs
    print("🏘️  Fetching from Toronto BIAs...")
    try:
        bia_scraper = BIAScraper()
        bia_events = bia_scraper.fetch_events(days_ahead=7)
        aggregator.add_events(bia_events, 'BIA')
    except Exception as e:
        print(f"   ❌ Error fetching BIA events: {e}")

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

    # 32. Process events
    print("🔧 Processing events...")
    aggregator.filter_past_events()
    aggregator.validate_events()
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
