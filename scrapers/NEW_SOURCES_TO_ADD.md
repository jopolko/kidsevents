# New Sources to Add - Action List

## Verified Sources from Search (October 2025)

### Priority 1: Event Aggregators (Easy Wins)

1. **Child's Life**
   - URL: https://childslife.ca/events/category/toronto/
   - Type: Event calendar aggregator
   - Status: Ready to scrape
   - Copy: `cp TEMPLATE_business_scraper.py childslife_scraper.py`

2. **MOCA Toronto (Museum of Contemporary Art)**
   - URL: https://moca.ca/families/
   - Type: Museum family programs
   - Free admission for kids
   - Copy: `cp TEMPLATE_business_scraper.py moca_scraper.py`

### Priority 2: STEM Programs

3. **MakerKids**
   - URL: https://makerkids.com/
   - Type: STEM workshops, free trials
   - Location: Multiple Toronto locations
   - Copy: `cp TEMPLATE_business_scraper.py makerkids_scraper.py`

4. **Mad Science Toronto**
   - URL: https://toronto.madscience.org/
   - Type: Science workshops
   - Look for: Open houses, free events
   - Copy: `cp TEMPLATE_business_scraper.py madscience_scraper.py`

5. **UHN STEM Pathways**
   - URL: https://uhnstempathways.ca/
   - Type: Free community STEM programs
   - Copy: `cp TEMPLATE_business_scraper.py uhnstempathways_scraper.py`

6. **The STEAM Project**
   - URL: https://www.thesteamproject.ca
   - Location: Richmond Hill/GTA
   - Copy: `cp TEMPLATE_business_scraper.py steamproject_scraper.py`

### Priority 3: Dance Studios

7. **Run The Flex Dance Studio**
   - URL: https://runtheflex.com/
   - Type: Hip hop classes, $10 trial week
   - Copy: `cp TEMPLATE_business_scraper.py runtheflex_scraper.py`

8. **Pegasus Dance Studios**
   - URL: https://www.pegasusdancestudios.com/
   - Type: Multiple dance styles, free trial
   - Location: East Toronto (Danforth, Beaches)
   - Copy: `cp TEMPLATE_business_scraper.py pegasusdance_scraper.py`

9. **Joy of Dance Centre**
   - URL: https://www.joyofdance.ca/
   - Type: Kids dance classes 3+
   - Copy: `cp TEMPLATE_business_scraper.py joyofdance_scraper.py`

10. **St Clair Dance Collective**
    - URL: https://www.stclairdancecollective.com/toronto-toddler-dance-classes/
    - Type: Toddler dance 2-4 years
    - Copy: `cp TEMPLATE_business_scraper.py stclairdance_scraper.py`

### Priority 4: Already Scraping But Can Improve

11. **Kids Out and About Toronto**
    - URL: https://toronto.kidsoutandabout.com/
    - Status: Already in system but returning 0 events
    - Action: Fix the scraper URL/selectors

12. **ToDoCanada**
    - URL: https://www.todocanada.ca/
    - Status: Already in system but getting 403
    - Action: Fix headers or scraping method

13. **ChatterBlock**
    - URL: https://www.chatterblock.com/events/toronto-on-ca-c3981/
    - Status: Only getting 3 events
    - Action: Improve scraping to get more events

## Next Discovery Steps

### Google My Business Categories to Search

1. **Recreation Centers** - "Toronto recreation center kids programs"
2. **Art Schools** - "Toronto kids art classes trial"
3. **Music Schools** - "Toronto kids music lessons free trial"
4. **Gymnastics** - "Toronto kids gymnastics open house"
5. **Swimming** - "Toronto kids swim lessons trial"
6. **Martial Arts** - "Toronto kids karate taekwondo free class"
7. **Cooking Schools** - "Toronto kids cooking classes"

### Chains with Multiple Locations

1. **Indigo/Chapters** - All locations have storytime
   - Find all GTA locations
   - Scrape event calendars

2. **Lululemon** - Community fitness events
   - Toronto locations
   - Family yoga/fitness events

3. **Canadian Tire** - Kids workshops
   - All GTA locations
   - Weekend workshop schedule

4. **Home Depot** - Kids workshop
   - First Saturday monthly
   - All locations

5. **Michael's** - Kids craft classes
   - All GTA locations
   - Weekend events

### Cultural Centers

1. **Japanese Canadian Cultural Centre**
   - URL: https://www.jccc.on.ca/
   - Family programs, festivals

2. **Italian Cultural Centre**
   - URL: Find and add
   - Cultural events

3. **Chinese Cultural Centre**
   - URL: Find and add
   - Celebrations, programs

4. **Korean Cultural Centre**
   - URL: Find and add
   - Language, culture programs

### Libraries Beyond TPL

1. **Markham Public Library**
   - URL: https://www.markham.ca/library
   - Similar programs to TPL

2. **Mississauga Library**
   - URL: https://www.mississauga.ca/library/
   - Storytimes, programs

3. **Vaughan Public Libraries**
   - URL: https://www.vaughanpl.info/
   - Kids programs

4. **Richmond Hill Public Library**
   - URL: https://www.rhpl.ca/
   - Family events

5. **Brampton Library**
   - URL: https://www.bramptonlibrary.ca/
   - Kids events

## Research Tools

### Use These Google Searches

```bash
site:eventbrite.ca Toronto kids free
"Toronto" kids events site:*.ca
"GTA" children programs inurl:calendar
"Toronto" drop-in kids schedule
```

### Monitor These Hashtags (Manual Check)

- #TorontoKids
- #TorontoFamily
- #GTAKids
- #TorontoMom
- #TorontoParents
- #TorontoKidsEvents

## Implementation Checklist

For each new source:

- [ ] Visit website
- [ ] Find events/calendar page
- [ ] Check robots.txt
- [ ] Copy template scraper
- [ ] Customize URLs and selectors
- [ ] Test scraper: `python3 newsource_scraper.py`
- [ ] If successful, add to data_aggregator.py
- [ ] Run full aggregation
- [ ] Verify events appear on site

## Success Metrics

Track what works:
- Events found per source
- Update frequency
- Scraping reliability
- Event quality (unique vs duplicates)

**Goal:** Add 5-10 high-quality sources per month
**Target:** Reach 5,000+ total events

---

**Last Updated:** October 22, 2025
**Sources Identified:** 25+
**Sources Active:** 20
**Sources To Add:** 13 (Priority 1-3)
