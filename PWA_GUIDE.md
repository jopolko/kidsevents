# Progressive Web App (PWA) Setup

Toronto Kids Events is now a fully functional Progressive Web App! Users can install it on their devices for a native app-like experience.

## ✅ What's Been Set Up

### 1. Web App Manifest (`manifest.json`)
- Defines app name, icons, colors, and behavior
- Tells browsers how to install the app
- Located at: `/kidsevents/manifest.json`

### 2. Service Worker (`sw.js`)
- Enables offline functionality
- Caches events data for offline viewing
- Automatic updates when new versions are available
- Located at: `/kidsevents/sw.js`

### 3. App Icons
- Generated 8 icon sizes (72px to 512px)
- Includes support for Android and iOS
- Located at: `/kidsevents/icons/`

### 4. HTML Integration
- Manifest linked in `<head>`
- Service worker registered in `<body>`
- Apple iOS meta tags for iOS installation
- Install promotion banner (optional)

## 📱 How Users Can Install

### Android (Chrome/Edge)
1. Visit the website
2. See "Install" prompt banner (or tap menu → "Install app")
3. Confirm installation
4. App appears on home screen

### iOS (Safari)
1. Visit the website in Safari
2. Tap Share button
3. Select "Add to Home Screen"
4. Confirm
5. App appears on home screen

### Desktop (Chrome/Edge)
1. Visit the website
2. Look for install icon in address bar (⊕ or ⬇️)
3. Click and confirm
4. App opens in standalone window

## 🎯 Features

### Offline Support
- Events data is cached automatically
- App works without internet connection
- Last synced data is always available

### Automatic Updates
- Service worker checks for updates every minute
- Prompts user to reload when new version is available
- No manual update needed

### Native App Feel
- Runs in standalone window (no browser UI)
- Splash screen on launch
- Theme colors match app design
- Proper app icon on home screen

### Install Promotion
- Green banner appears at bottom of screen
- "Install" and "Later" buttons
- Only shows on first visit
- Respects user choice

## 🛠️ Testing Your PWA

### 1. Test Locally
```bash
# Serve via HTTP (required for service workers)
cd /var/www/html/kidsevents
python3 -m http.server 8000
# Visit http://localhost:8000
```

### 2. Chrome DevTools
1. Open DevTools (F12)
2. Go to "Application" tab
3. Check "Manifest" section - should show all icons and metadata
4. Check "Service Workers" - should show registered worker
5. Check "Cache Storage" - should show cached files

### 3. Lighthouse Audit
1. Open DevTools
2. Go to "Lighthouse" tab
3. Select "Progressive Web App"
4. Click "Generate report"
5. Aim for 90+ score

### 4. Test Installation
1. Open in Chrome/Edge
2. Look for install prompt
3. Install and test offline:
   - Install app
   - Open app
   - Turn off internet
   - App should still work with cached data

## 🚀 Production Deployment

### Requirements
- ✅ HTTPS (already configured)
- ✅ Valid manifest.json
- ✅ Service worker
- ✅ Icons (all sizes)
- ✅ Responsive design

### Verification Checklist
- [ ] Visit site on mobile device
- [ ] Verify install prompt appears
- [ ] Install app to home screen
- [ ] Test offline functionality
- [ ] Check icons appear correctly
- [ ] Verify theme colors
- [ ] Test on both Android and iOS

## 📊 Analytics

The PWA tracks installations via Google Analytics:
- Event: `pwa_installed`
- Category: `PWA`
- Label: `App Installed`

Check GA4 to see how many users are installing the app.

## 🔧 Customization

### Change Theme Color
Edit `manifest.json`:
```json
"theme_color": "#4CAF50"  // Change to your brand color
```

### Change App Name
Edit `manifest.json`:
```json
"name": "Toronto Kids Events",
"short_name": "KidsEvents"
```

### Update Icons
Replace files in `/kidsevents/icons/` with new icons.
Generate from source image:
```bash
convert source.png -resize 192x192 icons/icon-192x192.png
# Repeat for all sizes: 72, 96, 128, 144, 152, 192, 384, 512
```

### Modify Cache Strategy
Edit `sw.js` to change:
- Cache name (for versioning)
- Cached URLs
- Cache strategy (cache-first vs network-first)

### Disable Install Banner
Remove or comment out `showInstallPromotion()` function call in `index.html`.

## 🐛 Troubleshooting

### Service Worker Not Registering
- Check browser console for errors
- Ensure HTTPS is working
- Clear browser cache and reload
- Check `/kidsevents/sw.js` is accessible

### Install Prompt Not Showing
- Some browsers only show after 2+ visits
- Clear site data and try again
- Check Chrome flags: `chrome://flags/#enable-app-install-prompts`

### Offline Not Working
- Check service worker is active in DevTools
- Verify events.json is cached
- Check cache storage in DevTools → Application → Cache Storage

### Icons Not Appearing
- Verify all icon files exist in `/kidsevents/icons/`
- Check manifest.json paths are correct
- Clear cache and reinstall

### Updates Not Working
- Service worker checks every minute
- Force update: Unregister service worker in DevTools and reload
- Increment cache name in `sw.js` to force refresh

## 📚 Resources

- [MDN: Progressive Web Apps](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [web.dev: PWA Checklist](https://web.dev/pwa-checklist/)
- [Google: Install Criteria](https://web.dev/install-criteria/)
- [Maskable Icons Generator](https://maskable.app/)

## 🎉 Success!

Your webapp is now a PWA! Users can install it and use it like a native app with offline support.
