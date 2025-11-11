# Place ID Lookup Setup Guide

## Overview

The Place ID lookup feature enriches event venues with Google Place IDs, which provide precise locations for map markers. This eliminates the ambiguity when multiple organizations share the same address.

## Benefits

- **Precise Locations**: Each Place ID uniquely identifies a specific venue
- **Consistent Mapping**: Stable identifiers that don't change
- **Better User Experience**: Map markers point to the exact venue, not just the street address
- **Automatic Caching**: Repeated venues are cached to minimize API calls

## Setup Instructions

### 1. Get a Google API Key

If you don't already have one:

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project or select an existing one
3. Enable the **Places API**
4. Create an API key

### 2. Configure Environment Variables

Create a `.env` file in the `/var/www/html/kidsevents/` directory:

```bash
cd /var/www/html/kidsevents
nano .env
```

Add your Google API key:

```env
GOOGLE_MAPS_API_KEY=your_api_key_here
```

Or alternatively:

```env
GOOGLE_API_KEY=your_api_key_here
```

### 3. Set Permissions

```bash
chmod 600 /var/www/html/kidsevents/.env
```

### 4. Configure API Key Restrictions (IMPORTANT!)

To prevent unauthorized use:

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Click on your API key
3. Under "Application restrictions":
   - Select "IP addresses"
   - Add your server's IP address: `143.110.236.86` (or run `curl ifconfig.me` to check)
4. Under "API restrictions":
   - Select "Restrict key"
   - Enable only: **Places API** and **Geocoding API**
5. Click "Save"

## How It Works

### Caching System

The lookup service maintains a cache in `place_id_cache.json` that stores:
- Place ID for each venue
- Google's canonical name and address
- Coordinates from Google
- Timestamp of lookup

This means:
- **First run**: Makes API calls for all unique venues
- **Subsequent runs**: Uses cached data, no API calls needed
- **New venues**: Only new venues trigger API calls

### Rate Limiting

The module enforces:
- Maximum 10 requests per second
- 100ms delay between API calls
- Automatic throttling to prevent quota exhaustion

### Cost Estimation

Google Places API pricing (as of 2025):
- **Find Place from Text**: $17 per 1,000 requests
- **Free tier**: $200 credit per month (~11,700 free lookups)

Example scenarios:
- 100 unique venues = $1.70 (first run only)
- 500 unique venues = $8.50 (first run only)
- 1,000 unique venues = $17 (first run only)
- Subsequent runs = $0 (uses cache)

## Usage

### Automatic Integration

The Place ID lookup is automatically integrated into the data aggregation pipeline:

```bash
cd /var/www/html/kidsevents/scrapers
python3 data_aggregator.py
```

Output will show:
```
📍 Enriching venues with Google Place IDs...
   ✅ Enriched 156 venues with Place IDs
   📍 Place ID Lookup Stats:
      • Total lookups: 200
      • API calls: 44
      • Cache hits: 156 (78.0%)
      • Cache size: 200 venues
```

### Manual Testing

Test the lookup for a specific venue:

```bash
cd /var/www/html/kidsevents/scrapers
python3 place_id_lookup.py
```

### Cache Management

View the cache:
```bash
cat /var/www/html/kidsevents/scrapers/place_id_cache.json | jq '.' | head -50
```

Check cache size:
```bash
cat /var/www/html/kidsevents/scrapers/place_id_cache.json | jq '. | length'
```

Clear cache (forces fresh lookups):
```bash
rm /var/www/html/kidsevents/scrapers/place_id_cache.json
```

## Output Format

Events will now include a `place_id` field in the venue object:

```json
{
  "title": "Storytime at Bloor/Gladstone",
  "venue": {
    "name": "Toronto Public Library - Bloor/Gladstone Branch",
    "address": "1101 Bloor St W",
    "neighborhood": "Dufferin Grove",
    "lat": 43.6584,
    "lng": -79.4307,
    "place_id": "ChIJX8aN9tU0K4gRbQnWnEj_kXE"
  }
}
```

## Frontend Integration

To use Place IDs in your maps:

### Google Maps

```javascript
// Use Place ID directly
const place = new google.maps.places.Place({
  id: venue.place_id
});

// Or create a marker with Place ID
const marker = new google.maps.Marker({
  position: { lat: venue.lat, lng: venue.lng },
  map: map,
  title: venue.name,
  // Can link to Place details
  placeId: venue.place_id
});
```

### Links to Google Maps

```javascript
// Direct link to the specific venue on Google Maps
const mapsUrl = `https://www.google.com/maps/place/?q=place_id:${venue.place_id}`;
```

## Troubleshooting

### API Key Not Found

**Error**: `⚠️ No Google API key found, skipping Place ID lookup`

**Solution**:
1. Create `.env` file with `GOOGLE_MAPS_API_KEY` or `GOOGLE_API_KEY`
2. Check file permissions: `chmod 600 .env`
3. Install python-dotenv: `pip3 install python-dotenv`

### Places API Not Enabled

**Error**: API returns error about Places API not enabled

**Solution**:
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/library/places-backend.googleapis.com)
2. Click "Enable"

### Quota Exceeded

**Error**: `OVER_QUERY_LIMIT` status from API

**Solution**:
1. Check your [API usage](https://console.cloud.google.com/apis/dashboard)
2. Increase quotas or enable billing
3. The cache will prevent repeated calls

### Wrong Venues Returned

If Google returns incorrect venues:

1. Check that venue names and addresses are accurate in scrapers
2. The lookup uses location bias (lat/lng) to prefer nearby results
3. Manually review `place_id_cache.json` and remove incorrect entries
4. Re-run aggregator to get fresh lookups

## Disabling Place ID Lookup

If you want to run the aggregator without Place ID lookups:

**Option 1**: Don't set the API key (it will skip automatically)

**Option 2**: Comment out the enrichment step in `data_aggregator.py`:

```python
# aggregator.enrich_with_place_ids()  # Commented out
```

## Monitoring

### Check API Usage

Monitor your Google API usage:
- https://console.cloud.google.com/apis/dashboard
- Set up billing alerts to avoid unexpected charges

### Cache Hit Rate

Aim for:
- **First run**: 0% cache hits (expected)
- **Daily runs**: 80-95% cache hits (most venues cached)
- **After new sources added**: Lower % until new venues cached

## Security Considerations

- ✅ API key stored in `.env` (not in source code)
- ✅ `.env` has restricted permissions (600)
- ✅ `.env` blocked from web access (.htaccess)
- ✅ API key restricted to server IP
- ✅ API key restricted to specific APIs
- ✅ Rate limiting prevents abuse
- ✅ Caching minimizes API calls

## Best Practices

1. **Run aggregator regularly**: Daily runs will use cached data
2. **Review cache periodically**: Check for incorrect lookups
3. **Monitor API usage**: Set up billing alerts
4. **Rotate API keys**: Every 90 days for security
5. **Backup cache**: Include `place_id_cache.json` in backups

## Support

For issues with:
- **This module**: Check the code in `place_id_lookup.py`
- **Google API**: https://cloud.google.com/support
- **API pricing**: https://developers.google.com/maps/billing-and-pricing/pricing
