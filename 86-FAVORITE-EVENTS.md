# Event Favorites & Personal Calendar

## Overview

Members can save favorite events, view them on a map, export to calendar, and share their event list publicly.

## Features Summary

| Feature | Description |
|---------|-------------|
| ❤️ Favorite Button | Add/remove events to personal list |
| 📍 Map View | All favorites displayed on OpenStreetMap |
| 📅 ICS Export | Download calendar file |
| 🔗 Public Link | Shareable URL in member bio |
| 📁 Auto-Archive | Past events move to archive automatically |

---

## Favorite System

### Adding Favorites

| Element | Description |
|---------|-------------|
| Location | Heart icon on EventDetailPage |
| Action | Toggle favorite on/off |
| Feedback | Visual state change (filled/empty heart) |
| Requirement | Authenticated user (member or active account) |

### Favorite Storage

| Field | Type | Description |
|-------|------|-------------|
| User | FK to User | Who favorited |
| Event | FK to EventDetailPage | Which event |
| Added At | DateTime | When favorited |

---

## My Events Page

### Access

| Setting | Value |
|---------|-------|
| URL | `/account/my-events/` |
| Visibility | Authenticated users only |
| Menu | User dropdown menu |

### Tabs/Sections

| Tab | Content |
|-----|---------|
| Upcoming | Future favorited events (active list) |
| Archive | Past favorited events |

### Upcoming Events View

| Display | Description |
|---------|-------------|
| List View | Cards with event info |
| Map View | All events on OpenStreetMap (Leaflet) |
| Sort | By date (soonest first) |

### Event Card Info

| Element | Source |
|---------|--------|
| Event Title | Event name |
| Date/Time | Start date formatted |
| Location | Venue name + address |
| Status | Registered / Not registered |
| Actions | Remove favorite, Register, View |

### Map Features

| Feature | Description |
|---------|-------------|
| Provider | OpenStreetMap + Leaflet.js |
| Markers | One per event location |
| Popup | Event name, date, link |
| Clustering | Group nearby events |
| Geocoding | Nominatim (from event coordinates) |
| Route | OSRM link to directions |

---

## Archive Section

### Auto-Archive Logic

| Trigger | When event end_date (or start_date) < today |
|---------|---------------------------------------------|
| Action | Event appears in Archive tab instead of Upcoming |
| Data | Favorite record unchanged |

### Archive Filters

| Filter | Type |
|--------|------|
| Year | Dropdown (2024, 2025, 2026...) |
| Search | Text search in event names |

### Archive Display

| Element | Description |
|---------|-------------|
| Layout | List view (no map for past events) |
| Grouped By | Year |
| Actions | View event, Remove from favorites |

---

## Calendar Export (ICS)

### Export Options

| Option | Description |
|--------|-------------|
| All Upcoming | Export all future favorites |
| Single Event | Export one event |
| Date Range | Custom date selection |

### ICS Content

| Field | Source |
|-------|--------|
| SUMMARY | Event title |
| DTSTART | Start date/time |
| DTEND | End date/time |
| LOCATION | Venue name + address |
| DESCRIPTION | Event intro/description |
| URL | Event page URL |
| UID | Unique event identifier |

### Subscription URL

| Feature | Description |
|---------|-------------|
| URL | `/account/my-events/calendar.ics` |
| Format | Dynamic ICS feed |
| Auth | Token-based (no login required) |
| Updates | Always current favorites |

---

## Public Profile Link

### Enable Sharing

| Setting | Location |
|---------|----------|
| Toggle | Account Settings → Privacy |
| Option | "Show my events on public profile" |

### Public URL

| Format | `/members/{username}/events/` |
|--------|-------------------------------|
| Visibility | Anyone with link |
| Content | Upcoming favorites only (not archive) |

### Public Page Display

| Element | Description |
|---------|-------------|
| Header | Member name + avatar |
| Bio | Member bio text |
| Events | List of upcoming favorites |
| Map | Optional (toggle in settings) |
| ICS | Public calendar subscribe link |

### Privacy Options

| Option | Description |
|--------|-------------|
| Hide Events | Don't show on profile |
| Show List Only | No map |
| Show Map | Full display with locations |
| Hide Past | Only upcoming (default) |

---

## User Profile Integration

### Bio Section

| Field | Description |
|-------|-------------|
| Bio Text | Free text about member |
| Events Link | Auto-added if sharing enabled |
| Calendar Link | ICS subscription URL |

### Profile Fields (Site Settings)

| Field | Type |
|-------|------|
| Bio | RichText (limited) |
| Show Events Publicly | Boolean |
| Show Map on Profile | Boolean |
| Calendar Token | Auto-generated UUID |

---

## Admin Configuration

### Site Settings → Member Features

| Setting | Type | Default |
|---------|------|---------|
| Enable Favorites | Boolean | Yes |
| Enable Public Profiles | Boolean | Yes |
| Max Favorites | Number | 100 |
| Archive Retention | Years | 5 |

### Member Model Fields

| Field | Type | Description |
|-------|------|-------------|
| bio | TextField | Member bio text |
| show_events_publicly | Boolean | Enable public events page |
| show_map_publicly | Boolean | Show map on public profile |
| calendar_token | UUID | For ICS subscription auth |

---

## URL Structure

| URL | Purpose |
|-----|---------|
| `/account/my-events/` | Personal favorites (auth required) |
| `/account/my-events/archive/` | Past favorites |
| `/account/my-events/calendar.ics` | ICS feed (token auth) |
| `/members/{username}/` | Public profile |
| `/members/{username}/events/` | Public events list |
| `/members/{username}/calendar.ics` | Public ICS (if enabled) |

---

## API Endpoints (Optional)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/favorites/` | GET | List user favorites |
| `/api/favorites/{event_id}/` | POST | Add favorite |
| `/api/favorites/{event_id}/` | DELETE | Remove favorite |

---

## Template Includes

### Favorite Button

Include on EventDetailPage:
- Heart icon (empty/filled based on state)
- AJAX toggle (no page reload)
- Login prompt if not authenticated

### My Events Widget

Optional homepage widget for logged-in users:
- Next 3 upcoming favorites
- Link to full list

---

## Related Documentation

| Doc | Topic |
|-----|-------|
| [13-NEWS-EVENTS.md](13-NEWS-EVENTS.md) | Event page structure |
| [80-MEMBERSHIP-SYSTEM.md](80-MEMBERSHIP-SYSTEM.md) | Member model |
| [82-EVENT-REGISTRATIONS.md](82-EVENT-REGISTRATIONS.md) | Event registration |
