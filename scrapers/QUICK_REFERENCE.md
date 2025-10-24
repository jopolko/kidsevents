# FreeTO Scrapers - Quick Reference

## 🚀 Common Commands

### Setup
```bash
cd scrapers
pip3 install -r requirements.txt
./setup.sh
```

### Run Scrapers
```bash
# All sources (recommended)
python3 data_aggregator.py

# Individual sources
python3 tpl_scraper.py
python3 eventbrite_fetcher.py
```

### View Output
```bash
# Simple view
cat events.json | jq '.[0]'

# Count events
cat events.json | jq '. | length'

# Statistics
cat events_full.json | jq '.statistics'
```

---

## 📁 File Structure

```
pq/
├── index.html              # Main app
├── load_events.js          # Loads scraped data
├── GETTING_STARTED.md      # Full guide
└── scrapers/
    ├── setup.sh            # Automated setup
    ├── requirements.txt    # Python deps
    ├── tpl_scraper.py      # TPL scraper
    ├── eventbrite_fetcher.py  # EventBrite API
    ├── data_aggregator.py  # Combines all
    ├── events.json         # Output (production)
    └── events_full.json    # Output (with metadata)
```

---

## 🔑 Environment Variables

```bash
# EventBrite API (optional)
export EVENTBRITE_TOKEN="your_token_here"

# Slack notifications (optional)
export SLACK_WEBHOOK="https://hooks.slack.com/..."
```

---

## ⏰ Automation Options

### Cron (Local)
```bash
# Edit crontab
crontab -e

# Daily at 6 AM
0 6 * * * cd /path/to/pq/scrapers && python3 data_aggregator.py
```

### GitHub Actions (Cloud)
```yaml
# .github/workflows/scrape-events.yml
on:
  schedule:
    - cron: '0 6 * * *'
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Module not found | `pip3 install -r requirements.txt` |
| EventBrite 401 | Check `$EVENTBRITE_TOKEN` |
| No events | Run scrapers individually to test |
| CORS error | Use local server: `python3 -m http.server` |

---

## 📊 Data Quality Checks

```bash
# Missing required fields
cat events.json | jq '.[] | select(.title == null)'

# Future dates only
cat events.json | jq '.[] | select(.date < now)'

# Valid coordinates
cat events.json | jq '.[] | select(.venue.lat > 44 or .venue.lat < 43)'
```

---

## 🎯 Quick Tests

```bash
# Test 1: Run aggregator
python3 data_aggregator.py

# Test 2: Validate JSON
cat events.json | jq '.'

# Test 3: Count events
ls -lh events*.json
cat events.json | jq '. | length'

# Test 4: View in browser
cd .. && python3 -m http.server 8000
# Open http://localhost:8000
```

---

## 📈 Adding New Sources

1. Create `newsource_scraper.py`
2. Follow template in `scrapers/README.md`
3. Add to `data_aggregator.py`
4. Test: `python3 newsource_scraper.py`
5. Run: `python3 data_aggregator.py`

---

## 🔗 Useful Links

- **EventBrite API:** https://www.eventbrite.com/platform/api
- **TPL Events:** https://www.torontopubliclibrary.ca/programs-and-classes/
- **Cron Helper:** https://crontab.guru/
- **jq Playground:** https://jqplay.org/

---

## 📞 Quick Help

```bash
# View full documentation
cat GETTING_STARTED.md

# View scraper docs
cat README.md

# Check Python version
python3 --version

# Check dependencies
pip3 list | grep -E "requests|beautifulsoup4|lxml"

# Test network
curl -I https://www.eventbriteapi.com
```

---

**Pro Tip:** Bookmark this file for quick reference! 🔖
