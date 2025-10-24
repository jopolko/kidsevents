/**
 * Load Events from JSON (Optimized with lazy loading)
 * Loads Week 1 first for fast initial render, then loads remaining weeks in background
 */

let allLoadedEvents = [];
let isLoadingMore = false;

async function loadWeekEvents(weekNumber) {
    try {
        console.log(`📥 Loading week ${weekNumber} events...`);

        const response = await fetch(`events_week${weekNumber}.json`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        let events = Array.isArray(data) ? data : data.events || [];

        // Filter to only next 7 days
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const nextWeek = new Date(today);
        nextWeek.setDate(today.getDate() + 7);

        const todayStr = today.toISOString().split('T')[0];
        const nextWeekStr = nextWeek.toISOString().split('T')[0];

        events = events.filter(event => {
            return event.date >= todayStr && event.date < nextWeekStr;
        });

        console.log(`✅ Loaded ${events.length} events from week ${weekNumber} (filtered to next 7 days)`);
        return events;

    } catch (error) {
        console.warn(`⚠️  Could not load week ${weekNumber}:`, error);
        return [];
    }
}

async function loadAllWeeks() {
    try {
        console.log('📥 Loading all weeks fallback...');

        const response = await fetch('events.json');

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        let events = Array.isArray(data) ? data : data.events || [];

        // Filter to only next 7 days
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const nextWeek = new Date(today);
        nextWeek.setDate(today.getDate() + 7);

        const todayStr = today.toISOString().split('T')[0];
        const nextWeekStr = nextWeek.toISOString().split('T')[0];

        events = events.filter(event => {
            return event.date >= todayStr && event.date < nextWeekStr;
        });

        console.log(`✅ Loaded ${events.length} events from full file (filtered to next 7 days)`);
        return events;

    } catch (error) {
        console.warn('⚠️  Could not load events.json:', error);
        return [];
    }
}

async function loadInitialEvents() {
    // Try to load week 1 first for fast initial render
    let week1Events = await loadWeekEvents(1);

    if (week1Events.length === 0) {
        // Fallback to full events.json if weekly files don't exist
        console.log('📥 Weekly files not found, loading full events.json...');
        week1Events = await loadAllWeeks();
        allLoadedEvents = week1Events;
        return week1Events;
    }

    allLoadedEvents = week1Events;

    // Load remaining weeks in background after initial render
    setTimeout(async () => {
        if (isLoadingMore) return;
        isLoadingMore = true;

        console.log('📥 Loading weeks 2-4 in background...');

        const [week2, week3, week4] = await Promise.all([
            loadWeekEvents(2),
            loadWeekEvents(3),
            loadWeekEvents(4)
        ]);

        const additionalEvents = [...week2, ...week3, ...week4];

        if (additionalEvents.length > 0) {
            allLoadedEvents = [...allLoadedEvents, ...additionalEvents];
            console.log(`✅ Loaded ${additionalEvents.length} more events in background`);

            // Filter for ages 0-12 + All Ages, and exclude cancelled events
            const filteredAllEvents = allLoadedEvents.filter(event => {
                // Skip cancelled events (e.g., "***CANCELLED***City Hall Social Club")
                if (event.title && event.title.toUpperCase().includes('CANCELLED')) {
                    return false;
                }

                return event.age_groups.some(age =>
                    age.includes('Babies') ||
                    age.includes('Toddlers') ||
                    age.includes('Kids (6-12)') ||
                    age === 'All Ages'
                );
            });

            // Update global variables with ALL weeks
            window.events = filteredAllEvents;
            window.currentEvents = filteredAllEvents;  // Update currentEvents too!
            window.allFilteredEvents = filteredAllEvents;

            console.log('✅ App updated with all weeks');

            // Trigger re-render
            setTimeout(() => {
                if (typeof filterEventsByAge === 'function') {
                    console.log('🎨 Re-rendering with all weeks...');
                    filterEventsByAge('all'); // Re-render with all weeks
                }
            }, 50);
        }

        isLoadingMore = false;
    }, 100); // Load after 100ms to not block initial render

    return week1Events;
}

/**
 * Load and display event count for the coming week
 * The actual count is calculated in index.html's updateDateRangeHeader function
 */
async function loadMetadata() {
    console.log('🔵 loadMetadata() function called');
    // Just a placeholder - the week-range element will be updated
    // by updateDateRangeHeader() in index.html after events are loaded
}

/**
 * Initialize app with loaded events
 */
async function initializeAppWithData() {
    // Load metadata first (don't await - let it load in parallel)
    loadMetadata().catch(err => console.error('Metadata load failed:', err));

    // Load initial events (week 1 only)
    const loadedEvents = await loadInitialEvents();

    if (loadedEvents && loadedEvents.length > 0) {
        // Assign IDs if missing
        const eventsWithIds = loadedEvents.map((event, index) => {
            if (!event.id) {
                event.id = index + 1;
            }
            return event;
        });

        // Replace sample events with loaded data
        window.sampleEvents = eventsWithIds;

        // Replace the events loaded from events.json
        console.log('🔄 Replacing initial events with week 1 data...');

        // Filter for ages 0-12 + All Ages, and exclude cancelled events
        const cancelledCount = eventsWithIds.filter(e => e.title && e.title.toUpperCase().includes('CANCELLED')).length;
        const filteredEvents = eventsWithIds.filter(event => {
            // Skip cancelled events (e.g., "***CANCELLED***City Hall Social Club")
            if (event.title && event.title.toUpperCase().includes('CANCELLED')) {
                return false;
            }

            return event.age_groups.some(age =>
                age.includes('Babies') ||
                age.includes('Toddlers') ||
                age.includes('Kids (6-12)') ||
                age === 'All Ages'
            );
        });

        if (cancelledCount > 0) {
            console.log(`🚫 Filtered out ${cancelledCount} cancelled events`);
        }

        // Update global variables that the HTML expects
        window.events = filteredEvents;
        window.currentEvents = filteredEvents;  // This is what filterEventsByAge checks!
        window.allFilteredEvents = filteredEvents;

        // Hide loading screen and show content
        const loadingEl = document.getElementById('loading');
        const contentEl = document.getElementById('content');
        if (loadingEl) loadingEl.style.display = 'none';
        if (contentEl) contentEl.style.display = 'block';

        console.log('✅ App initialized with week 1 data (more loading in background...)');

        // Wait a moment for DOM to be ready, then trigger render
        setTimeout(() => {
            if (typeof filterEventsByAge === 'function') {
                console.log('🎨 Rendering events...');
                filterEventsByAge('all');
            } else {
                console.error('❌ filterEventsByAge function not found!');
            }
        }, 100);
    } else {
        console.log('ℹ️  Using sample data from HTML');
    }
}

// Auto-load on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAppWithData);
} else {
    initializeAppWithData();
}
