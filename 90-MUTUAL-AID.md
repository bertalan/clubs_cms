# Mutual Aid Network

## Overview

A volunteer network of members offering roadside assistance and mutual help to fellow motorcyclists. Members can signal their availability and skills on an interactive map.

### Multilingual

| Element | Translatable |
|---------|-------------|
| MutualAidPage | Yes (title, intro, body) |
| AidSkill snippet | Yes (name, description) |
| UI labels | Via template i18n |
| Map controls | Via Leaflet i18n |

See [41-MULTILANG.md](41-MULTILANG.md) for translation workflow.

---

## Page Structure

### URL

```
/mutual-aid/
```

### MutualAidPage

| Field | Type | Description |
|-------|------|-------------|
| Title | Text | e.g., "Mutual Aid Network" |
| Intro | RichText | Explanation of the service |
| Body | StreamField | Additional content |
| Emergency Contacts | Repeater | Official emergency numbers |

---

## AidSkill Snippet

### Purpose

Predefined skills/services that helpers can offer.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| name | Text | Skill name |
| slug | Slug | Identifier |
| description | Text | What this skill covers |
| icon | Image/Icon | Visual identifier |
| category | Choice | Skill category |
| order | Integer | Display order |

### Skill Categories

| Category | Skills |
|----------|--------|
| **Mechanics** | Flat tire, Chain repair, Spark plugs, Battery jump, Basic diagnosis |
| **Transport** | Motorcycle trailer, Van transport, Ride accompaniment |
| **Logistics** | Overnight hosting, Motorcycle storage, Tool lending |
| **Emergency** | First aid certified, Accident recovery |
| **Other** | Local tour guide, Language translator |

### Admin Path

```
Snippets → Aid Skills
```

---

## User Model Extensions

### New Fields in User Profile

| Field | Type | Description |
|-------|------|-------------|
| aid_available | Boolean | Currently available to help |
| aid_skills | M2M to AidSkill | Skills offered |
| aid_radius_km | Integer | Availability radius (km) |
| aid_location_city | Text | City for map placement |
| aid_coordinates | Text | Lat/Long (optional, more precise) |
| aid_notes | Text | Additional info (schedule, vehicle type) |

---

## Privacy Controls (Per-Field)

### Overview

Each helper decides exactly what information is visible to others. All privacy settings are OFF by default (opt-in).

### Privacy Settings Panel

| Field | Setting | Default | Description |
|-------|---------|---------|-------------|
| Display Name | Always shown | - | Required for identification |
| City | Always shown | - | Required for map placement |
| Skills | Always shown | - | Required for search |
| **Phone** | show_phone_on_aid | ❌ Off | Show phone number |
| **Mobile** | show_mobile_on_aid | ❌ Off | Show mobile number |
| **WhatsApp** | show_whatsapp_on_aid | ❌ Off | Show WhatsApp button |
| **Email** | show_email_on_aid | ❌ Off | Show email address |
| **Exact Location** | show_exact_location | ❌ Off | Show precise map pin |
| **Photo** | show_photo_on_aid | ❌ Off | Show profile photo |
| **Bio** | show_bio_on_aid | ❌ Off | Show biography |
| **Available Hours** | show_hours_on_aid | ❌ Off | Show availability schedule |

### Visibility Matrix

| Data | On Map (list) | On Helper Card | After Contact Request |
|------|---------------|----------------|----------------------|
| Display name | ✅ Always | ✅ Always | ✅ Always |
| City (general) | ✅ Always | ✅ Always | ✅ Always |
| Skills | ✅ Always | ✅ Always | ✅ Always |
| Radius | ✅ Always | ✅ Always | ✅ Always |
| Photo | ❌ | If enabled | If enabled |
| Bio | ❌ | If enabled | If enabled |
| Phone | ❌ | ❌ | If enabled |
| Mobile | ❌ | ❌ | If enabled |
| WhatsApp | ❌ | If enabled | If enabled |
| Email | ❌ | ❌ | If enabled |
| Exact location | ❌ | ❌ | If enabled |
| Available hours | ❌ | If enabled | If enabled |

### Privacy Levels Presets

Quick presets for common configurations:

| Preset | Description | Settings |
|--------|-------------|----------|
| **Minimal** | Just the basics | All off (default) |
| **Standard** | Show contact options | Phone + WhatsApp on |
| **Open** | Full visibility | All on except exact location |
| **Anonymous** | Skills only | All off, contact via form only |

### User Interface

| Element | Description |
|---------|-------------|
| Toggle switches | Each field has on/off toggle |
| Preview | "This is how others see you" |
| Preset buttons | Quick apply presets |
| Save | Confirm changes |

---

## Interactive Map

### Map Features

| Feature | Description |
|---------|-------------|
| Provider | OpenStreetMap + Leaflet |
| Clustering | Groups nearby helpers |
| Zoom levels | Region → City → Neighborhood |
| Geolocation | "Find helpers near me" button |
| Filters | By skill, by radius |

### Map Display

| Element | Description |
|---------|-------------|
| Markers | Skill-based icons or generic |
| Popup (click) | Display name, city, skills |
| Card (click more) | Full helper card with enabled info |

### Location Privacy

| Setting | Map Behavior |
|---------|--------------|
| City only | Marker at city center (approximate) |
| Exact location | Marker at precise coordinates |
| Random offset | ±500m from real position |

---

## Helper Card

### Always Visible

| Element | Description |
|---------|-------------|
| Display Name | e.g., "Paolo M." |
| City | e.g., "Alessandria" |
| Skills | Icons + names |
| Radius | "Available within 25 km" |
| Status | 🟢 Available / 🔴 Not available |

### Conditionally Visible

| Element | If Enabled |
|---------|------------|
| Photo | Profile picture |
| Bio | Short biography |
| WhatsApp | Click to chat button |
| Available Hours | e.g., "Weekdays 18-22, Weekends all day" |

### Contact Options

| Method | Visibility | How |
|--------|------------|-----|
| Contact Form | Always | Built-in form (no data exposed) |
| WhatsApp | If enabled | Direct link |
| Phone | If enabled | Click to call |
| Email | If enabled | Mailto link |

---

## Contact Form (Privacy-First)

### Purpose

Allows contact without exposing any personal data.

### Form Fields

| Field | Type | Description |
|-------|------|-------------|
| Your Name | Text | Requester's name |
| Your Phone | Text | Requester's phone |
| Location | Text | Where help is needed |
| Issue | Choice | Type of problem |
| Message | Text | Additional details |
| Urgency | Choice | Low / Medium / High |

### Notification to Helper

| Channel | Content |
|---------|---------|
| Email | Full request details |
| Push (if PWA) | "New help request from {Name}" |
| SMS (optional) | Short alert with link |

### Response

Helper can:
- Accept (reveals contact to requester)
- Decline (no data shared)
- Suggest alternative (forward to another helper)

---

## Access Control

### Who Can See What

| User Type | See Map | See Helpers | Contact |
|-----------|---------|-------------|---------|
| Public | ❌ | ❌ | ❌ |
| Registered (not member) | ✅ View only | ✅ Basic info | ❌ |
| Active member | ✅ Full | ✅ Full enabled | ✅ |
| Helper (member) | ✅ Full | ✅ Full enabled | ✅ + receives |

### Becoming a Helper

| Requirement | Description |
|-------------|-------------|
| Active membership | Card must be valid |
| At least 1 skill | Must select skills |
| City set | For map placement |
| Accept terms | Mutual aid agreement |

---

## Helper Dashboard

### My Helper Profile

| Section | Content |
|---------|---------|
| Status toggle | Available / Not available |
| My Skills | Add/remove skills |
| My Radius | Adjust km range |
| Privacy Settings | Per-field toggles |
| Preview | How others see me |

### My Activity

| Element | Description |
|---------|-------------|
| Requests received | List of help requests |
| Requests sent | My requests to others |
| Stats | Helps given, rating (optional) |

### Quick Actions

| Action | Description |
|--------|-------------|
| Go Offline | Temporarily unavailable |
| Update Location | Refresh coordinates |
| Edit Skills | Modify skill set |

---

## Notifications

### To Helper

| Event | Notification |
|-------|--------------|
| New request | Email + Push |
| Request cancelled | Email |
| Thank you received | Email |

### To Requester

| Event | Notification |
|-------|--------------|
| Helper accepted | Email + SMS (if urgent) |
| Helper declined | Email |
| No response (24h) | Reminder to try others |

---

## Optional Features

### Rating System

| Feature | Description |
|---------|-------------|
| After help | Requester can rate helper |
| Anonymous | Rating doesn't show who gave it |
| Display | Average rating on helper card |
| Minimum | Show only after 3+ ratings |

### Gamification

| Badge | Requirement |
|-------|-------------|
| First Aid | First successful help |
| Road Angel | 5 helps given |
| Guardian | 10 helps given |
| Legend | 25 helps given |

### Emergency Mode

| Feature | Description |
|---------|-------------|
| SOS Button | Quick help request |
| Auto-location | GPS coordinates sent |
| Broadcast | Notify all helpers in range |
| Priority | Marked as urgent |

---

## Admin Panel

### Helpers Management

```
Wagtail Admin → Mutual Aid → Helpers
```

### List View

| Column | Field |
|--------|-------|
| Display Name | display_name |
| City | aid_location_city |
| Skills | aid_skills count |
| Status | aid_available |
| Helps Given | stats |

### Moderation

| Action | Description |
|--------|-------------|
| Verify helper | Confirm identity |
| Suspend helper | Temporarily disable |
| Remove helper | Remove from network |
| View logs | See activity history |

---

## Integration

### With Member System

| Feature | Integration |
|---------|-------------|
| Profile fields | Extended User Model |
| Membership check | Only active members |
| Display name | From [80-MEMBERSHIP-SYSTEM.md](80-MEMBERSHIP-SYSTEM.md) |

### With Events

| Feature | Integration |
|---------|-------------|
| Event helpers | Show helpers at event location |
| Rally support | Dedicated helpers for event |

### With PWA

| Feature | Integration |
|---------|-------------|
| Push notifications | New requests |
| Offline map | Cached helper data |
| Geolocation | Find helpers nearby |

---

## References

- [80-MEMBERSHIP-SYSTEM.md](80-MEMBERSHIP-SYSTEM.md) - User model, display_name
- [41-MULTILANG.md](41-MULTILANG.md) - Translation workflow
- [42-SNIPPETS.md](42-SNIPPETS.md) - AidSkill snippet
- [84-PWA-PUSH.md](84-PWA-PUSH.md) - Push notifications
- [87-ROUTE-MAPS.md](87-ROUTE-MAPS.md) - Map integration
