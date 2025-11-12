#!/bin/bash
# KidsEvents daily scraper
# Runs data_aggregator.py and logs output

cd /var/www/html/kidsevents/scrapers

# Set environment variables if needed
export EVENTBRITE_TOKEN="${EVENTBRITE_TOKEN:-}"

# Run the aggregator
echo "======================================"
echo "Starting scraper at $(date)"
echo "======================================"

python3 data_aggregator.py 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Scraper completed successfully at $(date)"
else
    echo "❌ Scraper failed with exit code $EXIT_CODE at $(date)"
fi

echo ""
