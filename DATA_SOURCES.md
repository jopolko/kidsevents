# Data Sources for Toronto Kids Events

This document lists all data sources integrated into the platform, including whether events are free or paid.

## Data Sources Overview

| Source | Free/Paid | Update Frequency | Event Types |
|--------|-----------|------------------|-------------|
| Toronto Public Library | 100% Free | Daily | Storytimes, workshops, programs |
| Museums & Cultural Centers | 100% Free | Monthly | Free admission days, special events |
| EarlyON Centres | 100% Free | Daily | Drop-in programs (ages 0-6) |
| Parks & Recreation | 100% Free | Daily | Drop-in sports, activities |
| Community Centres | 100% Free | Daily | Recreation programs |
| Adventure Playgrounds | 100% Free | Daily | Outdoor playground hours |
| Community Events | 100% Free | Daily | Parks, festivals, city events |
| **TRCA Conservation Areas** | **100% Free** | Daily | Nature programs, outdoor education |
| **Farmers' Markets** | **100% Free** | Weekly | Markets with kids activities |
| **Harbourfront Centre** | **Mixed** | Daily | Concerts, festivals, KidSpark ($15) |
| **EventBrite** | **Mixed** | Daily | Various kids/family events |
| **Indoor Play Centres** | **Paid** | Daily | Trampoline parks, play centres |
| ChatterBlock | Mixed | Weekly | Community-submitted events |
| To Do Canada | Mixed | Weekly | Curated family activities |
| Family Fun Canada | Mixed | Weekly | Weekend family events |

---

## Source Details

### 100% FREE Sources

#### 1. Toronto Public Library (TPL)
- **Type:** 100% Free
- **Events:** Storytimes, STEM workshops, craft programs, author visits
- **API:** Official TPL Events API
- **Update Frequency:** Daily
- **Coverage:** 100+ library branches across Toronto
- **Website:** [torontopubliclibrary.ca](https://www.torontopubliclibrary.ca)

#### 2. Museums & Cultural Centers
- **Type:** 100% Free admission days
- **Venues:**
  - Art Gallery of Ontario (AGO) - Free Wednesday evenings
  - Aga Khan Museum - Free Wednesday evenings
  - Gardiner Museum - Free with TPL card
  - Toronto History Museums - Free admission
  - ROM Kids Free Days - Monthly
- **Update Frequency:** Monthly
- **Website:** Various museum websites

#### 3. EarlyON Child and Family Centres
- **Type:** 100% Free
- **Events:** Drop-in play, crafts, parent support
- **Ages:** 0-6 years
- **Coverage:** 80+ locations across Toronto
- **Update Frequency:** Daily
- **Website:** [toronto.ca/earlyon](https://www.toronto.ca/community-people/children-parenting/children-programs-activities/earlyon-child-family-centres/)

#### 4. Parks & Recreation
- **Type:** 100% Free drop-in programs
- **Events:** Sports, swimming, skating, crafts
- **Coverage:** Community centres citywide
- **Update Frequency:** Daily
- **Website:** [toronto.ca/parks-recreation](https://www.toronto.ca/explore-enjoy/recreation/)

#### 5. Adventure Playgrounds
- **Type:** 100% Free
- **Locations:** 13 top outdoor adventure playgrounds
- **Features:**
  - Jamie Bell Adventure Playground (High Park) - Castle theme
  - Biidaasige Park - Indigenous-themed
  - Neshama Playground - Fully accessible
  - Cherry Beach - Pirate ship
  - And 9 more locations
- **Hours:** Dawn to dusk daily
- **Update Frequency:** Daily

#### 6. Community Events
- **Type:** 100% Free
- **Events:**
  - City festivals and celebrations
  - Free outdoor concerts
  - Parks events
  - Splash pads (summer)
  - Outdoor skating rinks (winter)
- **Update Frequency:** Daily
- **Coverage:** Citywide

#### 7. Toronto & Region Conservation Authority (TRCA)
- **Type:** 100% Free programs
- **Conservation Areas:**
  - Kortright Centre for Conservation - Environmental education, Maple Syrup Festival
  - Boyd Conservation Area - Nature walks, bird watching
  - Heart Lake Conservation Area - Swimming, trails, nature programs
  - Tommy Thompson Park - Bird watching, cycling, wildlife viewing
  - Black Creek Pioneer Village - Historical programs, heritage crafts
  - And 3 more locations
- **Programs:** Nature walks, outdoor education, seasonal programs, wildlife viewing
- **Update Frequency:** Daily
- **Coverage:** GTA-wide conservation areas
- **Ages:** All ages welcome
- **Note:** Some areas may have parking fees
- **Website:** [trca.ca](https://trca.ca)

#### 8. Farmers' Markets
- **Type:** 100% Free admission
- **Markets:**
  - St. Lawrence Market (indoor, year-round)
  - Evergreen Brick Works (Saturdays, May-Oct) - Farm animals, kids activities
  - Wychwood Barns (Saturdays, year-round)
  - Dufferin Grove (Thursdays, Jun-Oct) - Playground on-site
  - Leslieville (Sundays, May-Oct)
  - Withrow Park (Saturdays, May-Oct) - Adjacent to major playground
  - Sorauren (Mondays, May-Oct) - Park setting
  - And 2 more markets
- **Activities:** Local vendors, kids activities, playgrounds nearby, community atmosphere
- **Update Frequency:** Weekly schedules
- **Coverage:** Toronto-wide
- **Ages:** All ages, family-friendly
- **Website:** Various market websites

---

### MIXED (Free + Paid) Sources

#### 9. Harbourfront Centre
- **Type:** Mixed (both free and paid events)
- **Free Events:**
  - Summer Music in the Garden (Jun-Aug, Thursdays)
  - Free Flicks outdoor movies (Jul-Aug, Tuesdays)
  - Canada Day celebration
  - Unity Fest hip hop festival
  - Art gallery exhibitions
- **Paid Events:**
  - KidSpark - $15/person (ages 10 and under, free for 2 and under)
  - JUNIOR Festival (some ticketed performances)
  - Workshops and camps
- **Update Frequency:** Daily
- **Website:** [harbourfrontcentre.com](https://harbourfrontcentre.com)

#### 10. EventBrite
- **Type:** Mixed (free and paid)
- **Coverage:** 25km radius around Toronto
- **Event Types:** Workshops, classes, festivals, performances
- **Filtering:** Kids/family-relevant events only
- **Update Frequency:** Daily
- **Note:** Requires API token
- **Website:** [eventbrite.ca](https://www.eventbrite.ca)

#### 11. ChatterBlock
- **Type:** Mixed
- **Events:** Community-submitted kids activities
- **Coverage:** GTA-wide
- **Update Frequency:** Weekly
- **Website:** [chatterblock.com](https://www.chatterblock.com)

#### 12. To Do Canada
- **Type:** Mixed
- **Events:** Curated family activities and attractions
- **Update Frequency:** Weekly
- **Website:** [todocanada.ca](https://www.todocanada.ca)

#### 13. Family Fun Canada
- **Type:** Mixed
- **Events:** Weekend family activities
- **Update Frequency:** Weekly
- **Website:** [familyfuncanada.com](https://www.familyfuncanada.com/toronto/)

---

### PAID Sources

#### 14. Indoor Play Centres & Trampoline Parks
- **Type:** Paid admission
- **Venues:** 20+ locations including:
  - Happy Kingdom
  - Bunch of Fun Playland
  - Air Riderz Vaughan
  - Sky Zone Toronto
  - The Jump City (Richmond Hill, Scarborough)
  - Kids Fun City
  - And 14 more venues
- **Typical Cost:** $13-20 per child
- **Update Frequency:** Daily (operating hours)
- **Ages:** Toddlers to age 12
- **Website:** Various venue websites

---

## Filtering by Price

All events include an `is_free` field:
- `true` = Free admission
- `false` = Paid admission (price info included when available)

Users can filter events by:
1. **Free Only** - Shows only free events
2. **All Events** - Shows both free and paid
3. **Price Range** - Filter by specific price ranges (coming soon)

---

## Data Quality & Updates

### Update Schedule
- **Automated scraping:** Runs daily at 2 AM EST
- **Manual updates:** As needed for special events
- **Data validation:** All events checked for required fields

### Event Deduplication
Events are deduplicated using:
- Title + Date + Time + Venue name (case-insensitive hash)

### Data Retention
- Past events are automatically filtered out
- Events are displayed up to 30 days in advance

---

## Contributing New Sources

Want to suggest a new data source? We prioritize:
1. ✅ Official city/library/museum sources
2. ✅ Free or low-cost events
3. ✅ Toronto and GTA coverage
4. ✅ Regularly updated event calendars
5. ✅ Family/kids focus (ages 0-12)

Contact: [Add contact method]

---

**Updated:** October 19, 2025 at 04:52 AM UTC
