#!/bin/bash
# Daily scraper runner for Toronto Kids Events
# Runs all scrapers and updates events.json

# Set working directory
cd /var/www/html/kidsevents/scrapers

# Log file
LOG_FILE="/var/www/html/kidsevents/scrapers/scraper.log"

# Add timestamp
echo "========================================" >> "$LOG_FILE"
echo "Scraper run started: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Run the data aggregator
python3 data_aggregator.py >> "$LOG_FILE" 2>&1

# Check if successful
if [ $? -eq 0 ]; then
    echo "✅ Scraper completed successfully at $(date)" >> "$LOG_FILE"

    # Ensure www-data can read (john runs cron; john is in www-data group)
    chgrp www-data /var/www/html/kidsevents/*.json
    chgrp www-data /var/www/html/kidsevents/scrapers/*.json
    chmod g+rw /var/www/html/kidsevents/*.json
    chmod g+rw /var/www/html/kidsevents/scrapers/*.json

    # Refresh GEO / AI-citation content: re-bake the FULL event list + Event
    # schema into index.html so AI crawlers (which do not run JS) see today's
    # complete inventory, not a stale snapshot. Must run AFTER aggregation,
    # which just rewrote events_week1.json + metadata.json that geo_inject reads.
    if python3 /var/www/html/kidsevents/geo_inject.py >> "$LOG_FILE" 2>&1; then
        echo "✅ geo_inject refreshed index.html at $(date)" >> "$LOG_FILE"
    else
        echo "⚠️ geo_inject failed at $(date)" >> "$LOG_FILE"
    fi
else
    echo "❌ Scraper failed at $(date)" >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"
