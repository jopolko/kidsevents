# Toronto Kids Events Data Scrapers

Automated data collection scripts for aggregating free kids events in Toronto.

## 📁 Files

- **`tpl_scraper.py`** - Toronto Public Library event scraper
- **`eventbrite_fetcher.py`** - EventBrite API integration
- **`data_aggregator.py`** - Combines all sources into unified JSON
- **`requirements.txt`** - Python dependencies

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd scrapers
pip install -r requirements.txt
```

### 2. Set Up EventBrite (Optional)

To get live EventBrite data:

```bash
# Get your token at: https://www.eventbrite.com/platform/api
export EVENTBRITE_TOKEN="your_token_here"
```

Without a token, sample data will be used.

### 3. Run Aggregator

```bash
python data_aggregator.py
```

This will:
- ✅ Fetch events from TPL
- ✅ Fetch events from EventBrite
- ✅ Remove duplicates
- ✅ Filter past events
- ✅ Validate data
- ✅ Generate `events.json` and `events_full.json`

## 📊 Output Files

### `events.json`
Clean event list for production use:
```json
[
  {
    "id": "abc123",
    "title": "Storytime for Preschoolers",
    "description": "Interactive stories and songs",
    "category": "Learning",
    "icon": "📚",
    "date": "2025-10-25",
    "start_time": "10:30",
    "end_time": "11:15",
    "venue": {
      "name": "Toronto Public Library - Beaches",
      "address": "2161 Queen Street East",
      "neighborhood": "The Beaches",
      "lat": 43.6687,
      "lng": -79.2981
    },
    "age_groups": ["Toddlers (3-5)"],
    "indoor_outdoor": "Indoor",
    "organized_by": "Toronto Public Library",
    "website": "https://www.torontopubliclibrary.ca/",
    "source": "TPL"
  }
]
```

### `events_full.json`
Includes metadata and statistics:
```json
{
  "generated_at": "2025-10-16T10:00:00",
  "total_events": 42,
  "statistics": {
    "sources": {"TPL": 30, "EventBrite": 12},
    "categories": {"Learning": 25, "Arts": 10, "Sports": 7}
  },
  "events": [...]
}
```

## 🔧 Individual Scrapers

Run scrapers separately for testing:

### TPL Scraper
```bash
python tpl_scraper.py
# Output: tpl_events.json
```

### EventBrite Fetcher
```bash
python eventbrite_fetcher.py
# Output: eventbrite_events.json
```

## 🤖 Automation with GitHub Actions

### Schedule Daily Updates

Create `.github/workflows/scrape-events.yml`:

```yaml
name: Scrape Events

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          cd scrapers
          pip install -r requirements.txt

      - name: Run aggregator
        env:
          EVENTBRITE_TOKEN: ${{ secrets.EVENTBRITE_TOKEN }}
        run: |
          cd scrapers
          python data_aggregator.py

      - name: Commit and push
        run: |
          git config user.name "GitHub Actions Bot"
          git config user.email "actions@github.com"
          git add scrapers/events.json scrapers/events_full.json
          git commit -m "Update events data" || exit 0
          git push
```

## 📝 Adding New Sources

### Template for New Scraper

```python
#!/usr/bin/env python3
"""
New Source Scraper
"""

import json
from datetime import datetime
from typing import List, Dict

class NewSourceScraper:
    def __init__(self):
        self.base_url = "https://example.com"

    def scrape_events(self) -> List[Dict]:
        """Scrape events from source"""
        events = []

        # Your scraping logic here

        return events

    def save_to_json(self, events: List[Dict], filename: str):
        """Save events to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)

def main():
    scraper = NewSourceScraper()
    events = scraper.scrape_events()
    scraper.save_to_json(events, "newsource_events.json")

if __name__ == "__main__":
    main()
```

Then add to `data_aggregator.py`:

```python
from newsource_scraper import NewSourceScraper

# In main():
newsource_scraper = NewSourceScraper()
newsource_events = newsource_scraper.scrape_events()
aggregator.add_events(newsource_events, 'NewSource')
```

## 🗓️ Recommended Schedule

- **Daily (6 AM):** Full aggregation
- **Weekly (Sunday):** Deep scrape with validation
- **Monthly:** Manual review and cleanup

## 🛠️ Troubleshooting

### "No EventBrite API token found"
- Get token at https://www.eventbrite.com/platform/api
- Set as environment variable: `export EVENTBRITE_TOKEN="..."`
- Or use sample data for testing

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Permission denied"
```bash
chmod +x *.py
```

## 📈 Future Enhancements

Potential additions:
- **Parks & Recreation scraper** - Toronto Parks programs
- **Museums scraper** - ROM, AGO, Science Centre
- **Community centres** - 148+ locations
- **Geocoding** - Convert addresses to coordinates
- **Image scraping** - Event photos
- **Selenium** - For dynamic websites
- **Proxy rotation** - Avoid rate limiting
- **Error notifications** - Email/Slack alerts

## 🤝 Contributing

To add a new event source:

1. Create `source_scraper.py` following the template
2. Add to `data_aggregator.py`
3. Update this README
4. Test with `python data_aggregator.py`
5. Submit PR

## 📄 License

MIT - Use freely for Toronto Kids Events project
