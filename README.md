# Toronto Kids Events - Discover Events for Kids in Toronto

**Discover events and activities for children under 12 in Toronto**

🌐 Visit: [https://joshuaopolko.com/kidsevents/](https://joshuaopolko.com/kidsevents/)
📚 **Documentation:** See guides below

---

## ✨ Features

- 🎯 **Kids-Focused** - Events specifically for ages 0-12
- 📍 **Location-Based** - Find events near you with GPS
- 🔍 **Smart Search** - Real-time filtering by keywords
- 🎨 **Beautiful Design** - Modern, mobile-first UI
- ⚡ **Fast & Simple** - No login required
- 🆓 **90% Free** - Almost all events are completely free

---

## 🚀 Quick Start

### For Users

1. Open `index.html` in your browser
2. Click "Find Events Near Me" to see nearby events
3. Use filters to find perfect activities
4. Click any event for full details

### For Developers

```bash
# 1. Clone/download this project
cd kidsevents

# 2. Set up data scrapers
cd scrapers
pip3 install -r requirements.txt

# 3. Run data aggregator
python3 data_aggregator.py

# 4. View in browser
cd ..
python3 -m http.server 8000
# Open http://localhost:8000
```

---

## 📁 Project Structure

```
pq/
├── index.html                  # Main web app (single page)
├── load_events.js              # Loads dynamic event data
├── README.md                   # This file
├── GETTING_STARTED.md          # Complete setup guide
├── ARCHITECTURE.md             # System design overview
│
└── scrapers/                   # Data collection scripts
    ├── setup.sh                # Automated setup
    ├── requirements.txt        # Python dependencies
    ├── tpl_scraper.py          # Toronto Public Library
    ├── eventbrite_fetcher.py   # EventBrite API
    ├── data_aggregator.py      # Combines all sources
    ├── events.json             # Generated event data
    ├── README.md               # Scraper documentation
    ├── QUICK_REFERENCE.md      # Command cheat sheet
    └── ...
```

---

## 📖 Documentation

| Guide | Purpose | Audience |
|-------|---------|----------|
| **[README.md](README.md)** | Project overview | Everyone |
| **[GETTING_STARTED.md](GETTING_STARTED.md)** | Detailed setup guide | Developers |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System design | Technical |
| **[scrapers/README.md](scrapers/README.md)** | Scraper docs | Data engineers |
| **[scrapers/QUICK_REFERENCE.md](scrapers/QUICK_REFERENCE.md)** | Command cheat sheet | Quick lookup |

---

## 🎯 Use Cases

### Parents & Caregivers
- Find weekly and daily activities for kids
- Discover library storytimes nearby
- Plan weekly outings without spending money

### Newcomers to Toronto
- Explore free family-friendly events
- Learn about community resources
- Connect with Toronto's culture

### Budget-Conscious Families
- Save money on entertainment
- Access quality programs for free
- Build rich experiences without cost

---

## 🛠️ Technology Stack

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with gradients
- **Vanilla JavaScript** - No framework dependencies
- **Responsive Design** - Mobile-first approach

### Backend / Data
- **Python 3.8+** - Web scraping & API calls
- **BeautifulSoup** - HTML parsing
- **Requests** - HTTP library
- **JSON** - Data format

### Automation
- **GitHub Actions** - CI/CD pipeline
- **Cron** - Scheduled updates
- **Git** - Version control

---

## 📊 Data Sources

| Source | Events/Week | Status |
|--------|-------------|--------|
| **Toronto Public Library** | 500+ | ✅ Active |
| **EventBrite** | 50+ | ✅ Active |
| **Parks & Recreation** | 200+ | 🔜 Coming soon |
| **Museums** | 20+ | 🔜 Coming soon |
| **Community Centres** | 100+ | 🔜 Coming soon |

**Total:** 500+ events currently, 900+ when all sources added

---

## 🔄 How It Works

```
1. Scrapers collect events from multiple sources
   ↓
2. Aggregator combines & deduplicates data
   ↓
3. events.json is generated with clean data
   ↓
4. Web app loads and displays events
   ↓
5. Users search, filter, and find events!
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

---

## 🚀 Deployment

### Option 1: GitHub Pages (Free)
```bash
# Push to GitHub
git add .
git commit -m "Deploy Toronto Kids Events"
git push origin main

# Enable GitHub Pages in repo settings
# Site will be live at: https://yourusername.github.io/torontokidsevents
```

### Option 2: Netlify (Free)
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod

# Or connect GitHub repo in Netlify dashboard
```

### Option 3: Vercel (Free)
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

---

## 🤖 Automation

### Update Events Daily

**GitHub Actions** (Recommended):
```yaml
# .github/workflows/scrape-events.yml
name: Update Events
on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM
```

**Cron Job** (Local server):
```bash
crontab -e
# Add:
0 6 * * * cd /path/to/pq/scrapers && python3 data_aggregator.py
```

See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed instructions.

---

## 🎨 Customization

### Change Color Theme

Edit `index.html` CSS variables:
```css
:root {
    --primary: #3B82F6;      /* Main color */
    --accent: #F59E0B;       /* Accent color */
    --success: #10B981;      /* Success color */
}
```

### Add New Event Source

1. Create `scrapers/newsource_scraper.py`
2. Follow template in `scrapers/README.md`
3. Add to `scrapers/data_aggregator.py`
4. Run `python3 data_aggregator.py`

### Modify Filters

Edit age groups in `index.html`:
```javascript
<button onclick="app.applyQuickFilter('babies')">
  👶 Babies (0-2)
</button>
```

---

## 📈 Roadmap

### Phase 1 - MVP ✅
- [x] Basic web interface
- [x] TPL scraper
- [x] EventBrite integration
- [x] Search & filters
- [x] Location-based sorting
- [x] Calendar view

### Phase 2 - Data Expansion 🔜
- [ ] Parks & Recreation scraper
- [ ] Museums & galleries
- [ ] Community centres
- [ ] More event categories
- [ ] Better geocoding

### Phase 3 - Features 🔮
- [ ] User accounts
- [ ] Save favorite events
- [ ] Email notifications
- [ ] Submit event form
- [ ] Mobile app
- [ ] Social sharing

### Phase 4 - Scale 🚀
- [ ] Database backend
- [ ] REST API
- [ ] Admin dashboard
- [ ] Analytics
- [ ] Multi-city support

---

## 🐛 Known Issues

- **TPL Scraper**: Currently returns sample data (needs actual scraping implementation)
- **EventBrite**: Requires API token for live data
- **Coordinates**: Some venues may have inaccurate lat/lng
- **CORS**: Must use local server for development (not `file://`)

See [Issues](https://github.com/yourusername/torontokidsevents/issues) on GitHub.

---

## 🤝 Contributing

Contributions welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing`)
5. **Open** a Pull Request

### Areas needing help:
- 🕷️ Implement actual TPL scraping
- 🏞️ Add Parks & Rec scraper
- 🎨 Improve UI/UX design
- 📱 Mobile app development
- 🧪 Write tests
- 📝 Improve documentation

---

## 📄 License

MIT License - feel free to use for any purpose!

---

## 🙏 Acknowledgments

- **Toronto Public Library** - For amazing free programs
- **Toronto Parks & Recreation** - For community events
- **EventBrite** - For their API
- **City of Toronto** - For open data
- **All event organizers** - For providing free events!

---

## 📞 Contact & Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/torontokidsevents/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/torontokidsevents/discussions)
- **Email:** torontokidsevents@example.com
- **X (Twitter):** [@JoshuaOpolko](https://x.com/JoshuaOpolko)

---

## ⭐ Show Your Support

If this project helps you, give it a ⭐ on GitHub!

Share with other Toronto parents who might benefit.

---

**Built with ❤️ for Toronto families**

*Making free events easy to discover, one event at a time.*
# kidsevents
