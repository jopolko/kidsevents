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

    # Fix ownership to www-data
    chown www-data:www-data /var/www/html/kidsevents/*.json
    chown www-data:www-data /var/www/html/kidsevents/scrapers/*.json
else
    echo "❌ Scraper failed at $(date)" >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"
