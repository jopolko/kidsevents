# Getting Started with FreeTO Data Collection

Complete guide to setting up automated event scraping for FreeTO.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Detailed Setup](#detailed-setup)
3. [Usage Examples](#usage-examples)
4. [Automation](#automation)
5. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start (5 minutes)

### Step 1: Install Dependencies

```bash
cd scrapers
pip3 install -r requirements.txt
```

### Step 2: Run Aggregator

```bash
python3 data_aggregator.py
```

### Step 3: Check Output

Open `events.json` - you should see aggregated events from all sources!

### Step 4: View in Browser

Open `index.html` in your browser - events will automatically load from `events.json`.

---

## 🔧 Detailed Setup

### Prerequisites

- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **pip** - Usually comes with Python
- **Internet connection** - For API calls

### Installation

#### Option 1: Automated Setup

```bash
cd scrapers
./setup.sh
```

This will:
- ✅ Check Python installation
- ✅ Install all dependencies
- ✅ Test the aggregator
- ✅ Generate initial events data

#### Option 2: Manual Setup

```bash
# 1. Navigate to scrapers directory
cd scrapers

# 2. Install dependencies
pip3 install requests beautifulsoup4 lxml python-dateutil

# 3. Test individual scrapers
python3 tpl_scraper.py
python3 eventbrite_fetcher.py

# 4. Run aggregator
python3 data_aggregator.py
```

### EventBrite API Setup (Optional but Recommended)

EventBrite provides rich, structured event data. To enable:

#### 1. Get API Token

- Visit https://www.eventbrite.com/platform/api
- Sign in or create account
- Create a new app
- Copy your **Private Token**

#### 2. Set Environment Variable

**macOS/Linux:**
```bash
export EVENTBRITE_TOKEN="your_token_here"
```

**Windows:**
```cmd
set EVENTBRITE_TOKEN=your_token_here
```

**Permanent (add to `~/.bashrc` or `~/.zshrc`):**
```bash
echo 'export EVENTBRITE_TOKEN="your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

#### 3. Test

```bash
python3 eventbrite_fetcher.py
```

You should see real EventBrite events!

---

## 📖 Usage Examples

### Example 1: Update Events Daily

```bash
cd /var/www/html/pq/scrapers
python3 data_aggregator.py
```

This generates fresh `events.json` and `events_full.json`.

### Example 2: Test Individual Source

```bash
# Test TPL scraper
python3 tpl_scraper.py
cat tpl_events.json

# Test EventBrite
python3 eventbrite_fetcher.py
cat eventbrite_events.json
```

### Example 3: Custom Date Range

Edit `eventbrite_fetcher.py`:

```python
# Fetch events for next 60 days instead of 30
events = fetcher.fetch_events(days_ahead=60)
```

### Example 4: Filter by Category

After running aggregator, filter events:

```bash
# Get only arts events
cat events.json | jq '.[] | select(.category == "Arts")'

# Get only toddler events
cat events.json | jq '.[] | select(.age_groups[] | contains("Toddlers"))'
```

---

## 🤖 Automation

### Option 1: Cron Job (macOS/Linux)

Update events every day at 6 AM:

```bash
# Edit crontab
crontab -e

# Add this line:
0 6 * * * cd /var/www/html/pq/scrapers && /usr/bin/python3 data_aggregator.py >> /tmp/freeto-scraper.log 2>&1
```

**Test cron job:**
```bash
# Run manually to verify path
cd /var/www/html/pq/scrapers && python3 data_aggregator.py
```

**View logs:**
```bash
tail -f /tmp/freeto-scraper.log
```

### Option 2: GitHub Actions (Recommended)

Create `.github/workflows/scrape-events.yml`:

```yaml
name: Update Events Data

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
  workflow_dispatch:  # Manual trigger button

jobs:
  scrape:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

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

      - name: Commit updated data
        run: |
          git config user.name "FreeTO Bot"
          git config user.email "bot@freeto.ca"
          git add scrapers/events.json scrapers/events_full.json
          git diff --quiet && git diff --staged --quiet || \
            (git commit -m "Update events data [automated]" && git push)
```

**Add EventBrite token to GitHub Secrets:**

1. Go to your repo → Settings → Secrets → Actions
2. Click "New repository secret"
3. Name: `EVENTBRITE_TOKEN`
4. Value: Your EventBrite API token
5. Click "Add secret"

**Test GitHub Action:**

1. Go to Actions tab in your repo
2. Click "Update Events Data"
3. Click "Run workflow"
4. Watch it run!

### Option 3: Netlify/Vercel Build Hook

If hosting on Netlify/Vercel, trigger rebuild after updating data:

```bash
# In data_aggregator.py, add at the end:
import os
import requests

webhook_url = os.getenv('NETLIFY_BUILD_HOOK')
if webhook_url:
    requests.post(webhook_url)
    print("✅ Triggered site rebuild")
```

---

## 🧪 Testing

### Test Complete Pipeline

```bash
cd scrapers

# 1. Clear old data
rm -f *.json

# 2. Run aggregator
python3 data_aggregator.py

# 3. Verify output
ls -lh events*.json

# 4. Check event count
cat events.json | jq '. | length'

# 5. View first event
cat events.json | jq '.[0]'

# 6. Test in browser
cd ..
python3 -m http.server 8000
# Open http://localhost:8000
```

### Validate Data Quality

```bash
# Check for required fields
cat events.json | jq '.[] | select(.title == null or .date == null)'

# Check date range
cat events.json | jq '[.[].date] | min, max'

# Check sources
cat events.json | jq '[.[].source] | group_by(.) | map({source: .[0], count: length})'
```

---

## 🐛 Troubleshooting

### Problem: "Module not found"

**Solution:**
```bash
pip3 install -r requirements.txt
```

### Problem: "EventBrite API returns 401"

**Solution:**
- Check token: `echo $EVENTBRITE_TOKEN`
- Regenerate token at https://www.eventbrite.com/platform/api
- Make sure no extra spaces: `export EVENTBRITE_TOKEN="abc123"`

### Problem: "No events generated"

**Solution:**
```bash
# Check if scrapers run individually
python3 tpl_scraper.py  # Should create tpl_events.json
python3 eventbrite_fetcher.py  # Should create eventbrite_events.json

# Check aggregator logs
python3 data_aggregator.py 2>&1 | tee debug.log
cat debug.log
```

### Problem: "Events not showing in browser"

**Solutions:**

1. **Check JSON file exists:**
   ```bash
   ls -l scrapers/events.json
   ```

2. **Check JSON is valid:**
   ```bash
   cat scrapers/events.json | jq '.'
   ```

3. **Check browser console:**
   - Open DevTools (F12)
   - Look for errors in Console tab
   - Check Network tab for failed requests

4. **CORS issues (local development):**
   ```bash
   # Use a local server instead of file://
   python3 -m http.server 8000
   # Open http://localhost:8000
   ```

### Problem: "Cron job not running"

**Solutions:**

1. **Check cron syntax:**
   ```bash
   # View crontab
   crontab -l

   # Verify it's scheduled
   0 6 * * * means daily at 6:00 AM
   */30 * * * * means every 30 minutes
   ```

2. **Check paths are absolute:**
   ```bash
   # Bad (relative path):
   0 6 * * * cd scrapers && python3 data_aggregator.py

   # Good (absolute path):
   0 6 * * * cd /var/www/html/pq/scrapers && /usr/bin/python3 data_aggregator.py
   ```

3. **Check logs:**
   ```bash
   tail -f /tmp/freeto-scraper.log
   ```

4. **Test manually:**
   ```bash
   /usr/bin/python3 /var/www/html/pq/scrapers/data_aggregator.py
   ```

---

## 📊 Monitoring

### Check Last Update

```bash
# When was data last updated?
ls -lh scrapers/events.json

# What's in the metadata?
cat scrapers/events_full.json | jq '.generated_at'
```

### Event Statistics

```bash
# Total events
cat scrapers/events.json | jq '. | length'

# Events by source
cat scrapers/events_full.json | jq '.statistics.sources'

# Events by category
cat scrapers/events_full.json | jq '.statistics.categories'

# Date range
cat scrapers/events_full.json | jq '.statistics.date_range'
```

### Set Up Alerts

**Email on failure (cron):**

```bash
# In crontab:
MAILTO=your@email.com
0 6 * * * cd /var/www/html/pq/scrapers && python3 data_aggregator.py || echo "FreeTO scraper failed"
```

**Slack notification:**

```python
# In data_aggregator.py, add:
import requests
import os

def notify_slack(message):
    webhook = os.getenv('SLACK_WEBHOOK')
    if webhook:
        requests.post(webhook, json={"text": message})

# After aggregation:
notify_slack(f"✅ FreeTO: Updated {len(events)} events")
```

---

## 🎯 Next Steps

1. ✅ **Set up automation** (GitHub Actions or cron)
2. ✅ **Add EventBrite token** for live data
3. ✅ **Monitor first few runs** to catch issues
4. ✅ **Expand sources** (see scrapers/README.md)
5. ✅ **Share with community!**

---

## 📚 Additional Resources

- **Scrapers Documentation:** `scrapers/README.md`
- **EventBrite API Docs:** https://www.eventbrite.com/platform/docs
- **Cron Guide:** https://crontab.guru/
- **GitHub Actions Docs:** https://docs.github.com/en/actions

---

## 🤝 Need Help?

- Check `scrapers/README.md` for detailed docs
- Review error logs
- Test scrapers individually
- Verify dependencies are installed

---

**Happy scraping! 🎉**
