# Toronto Kids Events Architecture Overview

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📚 TPL API/Website    🎟️ EventBrite API    🏛️ Museums     │
│  🏞️ Parks & Rec       📱 Meetup.com        🌆 City Data    │
│                                                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    SCRAPERS LAYER                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────┐  ┌──────────────────┐  ┌────────────┐  │
│  │ tpl_scraper.py │  │ eventbrite_      │  │ Future     │  │
│  │                │  │ fetcher.py       │  │ scrapers   │  │
│  │ • Web scraping │  │ • API calls      │  │            │  │
│  │ • HTML parsing │  │ • JSON parsing   │  │            │  │
│  │ • Data mapping │  │ • Rate limiting  │  │            │  │
│  └────────────────┘  └──────────────────┘  └────────────┘  │
│                                                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               DATA AGGREGATOR                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  data_aggregator.py                                         │
│  ├─ Combine all sources                                     │
│  ├─ Deduplicate events                                      │
│  ├─ Validate data quality                                   │
│  ├─ Filter past events                                      │
│  ├─ Normalize format                                        │
│  └─ Generate statistics                                     │
│                                                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  DATA STORAGE                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📄 events.json          📄 events_full.json                │
│  ├─ Clean event list    ├─ Events + metadata               │
│  ├─ Production ready     ├─ Statistics                      │
│  └─ ~100KB               └─ Debugging info                  │
│                                                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  WEB APPLICATION                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  index.html (Single Page App)                               │
│  ├─ Event listing with cards                                │
│  ├─ Search & filters                                        │
│  ├─ Calendar view                                           │
│  ├─ Location-based "Near Me"                                │
│  └─ Event details modal                                     │
│                                                              │
│  load_events.js                                             │
│  └─ Fetches events.json and updates UI                      │
│                                                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      USERS                                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  👨‍👩‍👧 Parents    👶 Families    🎓 Newcomers    👵 Seniors   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### 1. Data Collection (Python)

```
Sources → Scrapers → Raw JSON files
```

**Files Created:**
- `tpl_events.json`
- `eventbrite_events.json`
- (future: `museums_events.json`, etc.)

### 2. Data Aggregation (Python)

```
Raw JSONs → Aggregator → Unified JSON
```

**Processing Steps:**
1. Load all source files
2. Deduplicate by (title + date + venue)
3. Validate required fields
4. Filter past events
5. Normalize format
6. Sort by date

**Files Created:**
- `events.json` - Production
- `events_full.json` - With metadata

### 3. Web Display (JavaScript)

```
events.json → load_events.js → App UI
```

**User Flow:**
1. Page loads with sample data
2. `load_events.js` fetches `events.json`
3. App updates with live data
4. User searches/filters events
5. User clicks "Near Me" for location-based sorting

---

## 📦 Component Breakdown

### Python Scrapers

**Purpose:** Collect event data from various sources

**Components:**

| File | Purpose | Output |
|------|---------|--------|
| `tpl_scraper.py` | Scrape Toronto Public Library | `tpl_events.json` |
| `eventbrite_fetcher.py` | Fetch from EventBrite API | `eventbrite_events.json` |
| `data_aggregator.py` | Combine & deduplicate all | `events.json` |

**Dependencies:**
- `requests` - HTTP calls
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser
- `python-dateutil` - Date handling

### Web Application

**Purpose:** Display events to users

**Components:**

| File | Purpose | Technology |
|------|---------|------------|
| `index.html` | Main UI | HTML5 + CSS3 + Vanilla JS |
| `load_events.js` | Dynamic data loading | Fetch API |

**Features:**
- 📋 List view with cards
- 📅 Calendar view
- 🔍 Real-time search
- 🎛️ Advanced filters
- 📍 Location-based sorting
- 📱 Mobile-first responsive

---

## 🔧 Event Data Schema

### Standard Event Object

```javascript
{
  "id": "unique_hash",
  "title": "Event Name",
  "description": "Short description",
  "category": "Learning",       // Learning, Arts, Sports, etc.
  "icon": "📚",                  // Emoji icon
  "date": "2025-10-25",          // YYYY-MM-DD
  "start_time": "10:30",         // HH:MM
  "end_time": "11:15",           // HH:MM
  "venue": {
    "name": "Toronto Public Library - Branch Name",
    "address": "123 Street Name",
    "neighborhood": "Area Name",
    "lat": 43.6532,              // For "Near Me" feature
    "lng": -79.3832
  },
  "age_groups": [                // Can have multiple
    "Babies (0-2)",
    "Toddlers (3-5)",
    "Kids (6-12)",
    "Teens (13-17)",
    "Adults",
    "Seniors (55+)",
    "All Ages"
  ],
  "indoor_outdoor": "Indoor",    // Indoor, Outdoor, or Both
  "organized_by": "Organization Name",
  "website": "https://...",      // Can be null
  "source": "TPL",               // Source identifier
  "scraped_at": "2025-10-16T10:00:00"  // ISO timestamp
}
```

---

## 🚀 Deployment Options

### Option 1: Static Hosting (Simplest)

```
GitHub Pages / Netlify / Vercel
├─ Host index.html
├─ Host events.json
└─ Update via GitHub Actions
```

**Pros:** Free, simple, fast
**Cons:** Need to update events.json regularly

### Option 2: With Backend

```
Frontend (Netlify) + Backend (Heroku/Railway)
├─ Frontend: Static HTML/JS
├─ Backend: Python API
└─ Database: PostgreSQL
```

**Pros:** Real-time updates, more control
**Cons:** More complex, costs money

### Option 3: Serverless

```
Frontend (Vercel) + Functions (Vercel/AWS Lambda)
├─ Frontend: Static site
├─ API: Serverless functions
└─ Storage: S3 or CDN
```

**Pros:** Scalable, pay-per-use
**Cons:** Requires serverless knowledge

---

## 🔐 Security Considerations

### API Keys

- ✅ Store in environment variables
- ✅ Never commit to git
- ✅ Use GitHub Secrets for CI/CD
- ❌ Don't embed in client-side code

### Rate Limiting

- ✅ Respect API rate limits
- ✅ Add delays between requests
- ✅ Cache responses
- ✅ Use exponential backoff

### Data Privacy

- ✅ Only scrape public data
- ✅ Respect robots.txt
- ✅ No personal user data
- ✅ Link to original sources

---

## 📈 Performance Optimization

### Data Collection

- **Parallel scraping** - Run scrapers concurrently
- **Caching** - Store responses to reduce API calls
- **Incremental updates** - Only fetch new events
- **Error recovery** - Retry failed requests

### Web App

- **Lazy loading** - Load events as needed
- **Code splitting** - Split JS by route
- **Image optimization** - Compress event images
- **CDN** - Serve static files from CDN
- **Service worker** - Offline support

---

## 🧪 Testing Strategy

### Unit Tests

```python
# test_tpl_scraper.py
def test_age_group_detection():
    assert "Babies (0-2)" in get_age_groups("Baby time")

# test_aggregator.py
def test_deduplication():
    events = [event1, event1, event2]
    assert len(deduplicate(events)) == 2
```

### Integration Tests

```python
# test_full_pipeline.py
def test_complete_flow():
    # Run all scrapers
    # Aggregate data
    # Validate output
    assert len(events) > 0
    assert all(event['date'] >= today)
```

### End-to-End Tests

```javascript
// test_ui.js (with Playwright/Cypress)
test('Load events and search', async () => {
  await page.goto('http://localhost:8000')
  await page.fill('#searchInput', 'story')
  await expect(page.locator('.event-card')).toHaveCountGreaterThan(0)
})
```

---

## 🔮 Future Enhancements

### Data Collection

- [ ] Parks & Recreation scraper
- [ ] Museums/galleries scraper
- [ ] Community centres (148 locations)
- [ ] School events (TDSB, TCDSB)
- [ ] University events
- [ ] Meetup.com integration

### Features

- [ ] User accounts & saved events
- [ ] Email notifications
- [ ] Submit event form
- [ ] Event reviews/ratings
- [ ] Share to social media
- [ ] Mobile app (React Native)

### Infrastructure

- [ ] PostgreSQL database
- [ ] REST API
- [ ] GraphQL endpoint
- [ ] Real-time updates (WebSocket)
- [ ] Admin dashboard
- [ ] Analytics & monitoring

---

## 📊 Metrics to Track

### Data Quality

- Total events scraped
- Duplicate rate
- Invalid events filtered
- Source coverage
- Data freshness (age of events)

### User Engagement

- Page views
- Search queries
- Filter usage
- "Near Me" clicks
- Event detail views
- Calendar interactions

### System Health

- Scraper success rate
- API response times
- Error rates
- Data update frequency
- Storage usage

---

## 🛠️ Development Workflow

```
1. Local Development
   └─ Edit code
   └─ Run scrapers locally
   └─ Test in browser

2. Commit & Push
   └─ Git commit
   └─ Git push to GitHub

3. CI/CD (GitHub Actions)
   └─ Run tests
   └─ Run scrapers
   └─ Update events.json
   └─ Deploy to production

4. Production
   └─ Users see updated events
   └─ Monitor metrics
   └─ Iterate
```

---

## 📚 Learning Resources

- **Web Scraping:** BeautifulSoup docs
- **APIs:** EventBrite API guide
- **Frontend:** MDN Web Docs
- **Automation:** GitHub Actions docs
- **Deployment:** Netlify/Vercel guides

---

**This architecture is designed to be:**
- ✅ Simple to understand
- ✅ Easy to maintain
- ✅ Scalable for growth
- ✅ Cost-effective (mostly free)
- ✅ Developer-friendly
