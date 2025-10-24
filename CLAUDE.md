# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FreeTO is a web application for discovering free kids events (ages 0-12) in Toronto. The project consists of:
- A single-page frontend application (vanilla JavaScript, no frameworks)
- Python scrapers that collect event data from multiple sources
- A data aggregator that combines, deduplicates, and validates events

## Development Commands

### Initial Setup
```bash
cd scrapers
pip3 install -r requirements.txt
# Or run automated setup:
./setup.sh
```

### Data Collection
```bash
# Run all scrapers and aggregate data (main command)
cd scrapers
python3 data_aggregator.py

# Run individual scrapers for testing
python3 tpl_api_scraper.py
python3 eventbrite_scraper.py
python3 earlyon_scraper.py
# ... etc for other scrapers
```

### Testing the Web Application
```bash
# Serve the application locally (required - file:// protocol won't work due to CORS)
python3 -m http.server 8000
# Then open http://localhost:8000
```

### Data Validation
```bash
# Count events
cat scrapers/events.json | jq '. | length'

# View statistics
cat scrapers/events_full.json | jq '.statistics'

# Check for invalid events
cat scrapers/events.json | jq '.[] | select(.title == null or .date == null)'

# View first event
cat scrapers/events.json | jq '.[0]'
```

## Architecture

### Data Flow
1. **Scrapers** (`scrapers/*_scraper.py`) collect events from various sources and output individual JSON files
2. **Aggregator** (`scrapers/data_aggregator.py`) combines all sources, deduplicates, validates, and filters past events
3. **Output** is written to `scrapers/events.json` (production) and `scrapers/events_full.json` (with metadata)
4. **Frontend** (`index.html`) loads events via `load_events.js` which fetches the JSON data

### Key Components

#### Frontend (index.html)
- Single HTML file containing all UI code
- Vanilla JavaScript (no build step, no framework)
- Features: search, filters, calendar view, location-based sorting
- All JavaScript and CSS are inline for simplicity
- Mobile-first responsive design

#### Scrapers (scrapers/*.py)
Each scraper follows this pattern:
- Has a class named after the source (e.g., `TPLAPIScraper`)
- Implements `scrape()` or similar method returning list of event dictionaries
- Outputs to `scrapers/{source}_events.json`
- Handles its own error cases gracefully

Active scrapers:
- `tpl_api_scraper.py` - Toronto Public Library API
- `eventbrite_scraper.py` - EventBrite API
- `earlyon_scraper.py` - EarlyON Centres
- `parksrec_scraper.py` - Toronto Parks & Recreation
- `chatterblock_scraper.py` - ChatterBlock events
- `holistic_community_scraper.py` - Holistic community events
- `todocanada_scraper.py` - ToDoCanada events
- `familyfun_scraper.py` - Family fun events
- `toronto_artisans_scraper.py` - Toronto artisan events
- `targeted_audiences_scraper.py` - Events for specific audiences
- And more (see `scrapers/data_aggregator.py` imports)

#### Data Aggregator (scrapers/data_aggregator.py)
- Imports all scraper classes
- Runs each scraper and collects events
- Deduplicates using hash of (title + date + start_time + venue)
- Filters out past events
- Validates required fields
- Sorts by date and time
- Outputs `events.json` and `events_full.json`

### Event Data Schema

Each event must have these fields:
```javascript
{
  "id": "unique_hash",           // Auto-generated if missing
  "title": "Event Name",
  "description": "Short description",
  "category": "Learning",        // Learning, Arts, Sports, etc.
  "icon": "📚",                  // Emoji icon
  "date": "2025-10-25",          // YYYY-MM-DD format
  "start_time": "10:30",         // HH:MM format
  "end_time": "11:15",           // HH:MM format
  "venue": {
    "name": "Venue Name",
    "address": "123 Street Name",
    "neighborhood": "Area Name",
    "lat": 43.6532,              // Required for "Near Me" feature
    "lng": -79.3832
  },
  "age_groups": ["Toddlers (3-5)"],  // Can be multiple
  "indoor_outdoor": "Indoor",    // Indoor, Outdoor, or Both
  "organized_by": "Organization Name",
  "website": "https://...",      // Can be null
  "source": "TPL",               // Source identifier
  "scraped_at": "2025-10-16T10:00:00"  // ISO timestamp
}
```

## Adding New Event Sources

1. Create a new scraper file in `scrapers/` (e.g., `newsource_scraper.py`)
2. Implement a scraper class with a method that returns events in the schema above
3. Add import to `scrapers/data_aggregator.py`
4. Instantiate the scraper and call `aggregator.add_events()` in the main function
5. Test by running `python3 data_aggregator.py`

## Environment Variables

- `EVENTBRITE_TOKEN` - EventBrite API token (optional, uses sample data if not set)
- Other scrapers may require additional API keys or tokens

## Important Notes

### When Modifying Scrapers
- Always return events in the standard schema format
- Handle errors gracefully (don't crash the entire aggregation if one source fails)
- Print clear status messages (use ✅, ⚠️, 🗑️ emojis for consistency)
- Filter for kids events (ages 0-12) and free events only
- Include lat/lng coordinates for the "Near Me" feature to work

### When Modifying the Frontend
- All code is in `index.html` - there's no separate JS or CSS file
- The `app` object is the main application state
- Events are loaded via `load_events.js` which fetches from `scrapers/events.json`
- Must serve via HTTP server for CORS (not file://)
- Test on mobile viewport sizes

### Data Aggregation
- The aggregator runs all scrapers sequentially (not parallel)
- Deduplication is based on title, date, time, and venue name (case-insensitive)
- Past events are filtered out automatically
- Events without required fields are skipped with a warning

## File Locations

- Main app: `/var/www/html/kidsevents/index.html`
- Event loader: `/var/www/html/kidsevents/load_events.js`
- Scrapers: `/var/www/html/kidsevents/scrapers/`
- Output data: `/var/www/html/kidsevents/scrapers/events.json`
- Working directory: `/var/www/html/kidsevents`

## Dependencies

Python packages (see `scrapers/requirements.txt`):
- `requests` - HTTP library for API calls and scraping
- `beautifulsoup4` - HTML parsing
- `lxml` - Fast XML/HTML parser
- `python-dateutil` - Date parsing and manipulation

Frontend has zero dependencies (vanilla JavaScript).
