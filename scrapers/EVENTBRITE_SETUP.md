# EventBrite API Setup Guide

## Why You Need This

Currently, **TPL events make up 88.2% of all events** in the aggregator. We need EventBrite to diversify the event sources and get TPL below 30%.

**Current breakdown:**
- TPL: 1,002 events (88.2%)
- Museums: 87 events (7.7%)
- Community: 47 events (4.1%)

## How to Get an EventBrite API Token

### Step 1: Create an EventBrite Account
1. Go to https://www.eventbrite.com
2. Sign up for a free account (or log in if you have one)

### Step 2: Create an App
1. Go to https://www.eventbrite.com/platform/
2. Click "Create App" or go to https://www.eventbrite.com/account-settings/apps
3. Fill out the app details:
   - **App Name**: "FreeTO Events Scraper" (or any name)
   - **App Description**: "Aggregating free kids and family events in Toronto"
   - **App URL**: Your website or `https://joshuaopolko.com/pq/`

### Step 3: Get Your OAuth Token
1. Once the app is created, you'll see your **Private Token** (OAuth token)
2. Copy this token - it looks like: `ABCDEFGH123456789WXYZ`

### Step 4: Set the Environment Variable

On your server, set the environment variable:

```bash
# Temporary (for current session)
export EVENTBRITE_TOKEN="your_token_here"

# Permanent (add to ~/.bashrc or ~/.bash_profile)
echo 'export EVENTBRITE_TOKEN="your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

### Step 5: Test the Scraper

Test that it works:

```bash
cd /var/www/html/pq/scrapers
python3 eventbrite_scraper.py
```

You should see:
```
🎫 Fetching from EventBrite...
   ✅ Found X EventBrite events
```

### Step 6: Run the Full Aggregator

```bash
cd /var/www/html/pq/scrapers
python3 data_aggregator.py
```

## Expected Results

With EventBrite working, we should see:

- **EventBrite**: 100-300 free kids events (estimated)
- **TPL**: 1,002 events
- **Museums**: 87 events
- **Community**: 47 events

**Total**: ~1,200-1,400 events

**New breakdown** (estimated):
- TPL: ~70-75% (getting closer to 30% goal)
- EventBrite: ~10-20%
- Museums: ~6%
- Community: ~3%

## Troubleshooting

### "No EventBrite API token found"
- Make sure you've set the `EVENTBRITE_TOKEN` environment variable
- Verify with: `echo $EVENTBRITE_TOKEN`

### "API error: 401"
- Your token is invalid or expired
- Generate a new token from the EventBrite platform

### "API error: 429"
- You've hit the rate limit (5,000 requests/hour for free tier)
- Wait an hour or upgrade your EventBrite plan

## API Limits

**Free Tier:**
- 5,000 requests per hour
- Our scraper makes ~5-10 requests per run (with pagination)
- Running hourly via cron is well within limits

## Alternative: Scrape Without API

If you can't get an API token, we could try:
1. Scraping EventBrite's public pages (more brittle)
2. Finding more Toronto event sources (community centers, BIAs, etc.)
3. Reducing TPL event frequency (only show next 7 days instead of 14)

Let me know if you need help with any of these steps!
