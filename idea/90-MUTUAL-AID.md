# Mutual Aid Network

## Overview

A volunteer network of members offering roadside assistance and mutual help to fellow motorcyclists. Members can signal their availability and skills on an interactive map.

**Federation-enabled:** This network is shared with partner clubs. Visitors from federated clubs can view helpers and request contact (with limits). See [Federation Access](#federation-access) section.

### Key Features

| Feature | Description |
|---------|-------------|
| Interactive map | OpenStreetMap with clustered markers |
| Skill filtering | Find helpers by specific skill |
| Privacy-first | Helpers control what data is visible |
| Federation | Shared with trusted partner clubs |
| Anti-abuse | External users have contact limits |

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

**URL:** `/mutual-aid/`

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

**Admin Path:** Snippets → Aid Skills

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

| Data | On Map (list) | On Helper Card | After Contact Unlock |
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

### Privacy Presets

Quick presets for common configurations:

| Preset | Description | Settings |
|--------|-------------|----------|
| **Minimal** | Just the basics | All off (default) |
| **Standard** | Show contact options | Phone + WhatsApp on |
| **Open** | Full visibility | All on except exact location |
| **Anonymous** | Skills only | All off, contact via form only |

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
| City | e.g., "Turin" |
| Skills | Icons + names |
| Radius | "Available within 25 km" |
| Status | 🟢 Available / 🔴 Not available |

### Conditionally Visible

| Element | When Shown |
|---------|------------|
| Photo | If enabled by helper |
| Bio | If enabled by helper |
| WhatsApp | If enabled by helper |
| Available Hours | If enabled by helper |

### For External Visitors

External visitors from partner clubs see an additional badge:

| Element | Description |
|---------|-------------|
| Visitor badge | "👤 You are visiting from Partner Club" |
| Contact counter | "2 of 3 contacts used" |
| Unlock button | "Show contact details" (counts toward limit) |

---

## Contact Options

| Method | Visibility | How |
|--------|------------|-----|
| Contact Form | Always | Built-in form (no data exposed) |
| WhatsApp | If enabled | Direct link |
| Phone | If enabled | Click to call |
| Email | If enabled | Mailto link |

**Note:** For external visitors, viewing phone/email/WhatsApp counts toward their contact limit. The contact form is always free and unlimited.

---

## Contact Form (Privacy-First)

### Purpose

Allows contact without exposing any personal data. Always available, even for external visitors.

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

| User Type | See Map | See Helpers | View Contacts | Limit |
|-----------|---------|-------------|---------------|-------|
| Public (anonymous) | ❌ | ❌ | ❌ | - |
| Registered (not member) | ✅ View | ✅ Basic | ❌ | - |
| Active member | ✅ Full | ✅ Full | ✅ Unlimited | None |
| External (federated) | ✅ Full | ✅ Full | ✅ Limited | 3 contacts |
| External (approved) | ✅ Full | ✅ Full | ✅ Unlimited | None |

### Becoming a Helper

| Requirement | Description |
|-------------|-------------|
| Active membership | Card must be valid |
| At least 1 skill | Must select skills |
| City set | For map placement |
| Accept terms | Mutual aid agreement |

---

## Federation Access

### Overview

When clubs federate (see [92-EVENT-FEDERATION.md](92-EVENT-FEDERATION.md)), their members can access each other's Mutual Aid networks. To prevent abuse while allowing genuine help requests, external visitors have a contact limit.

### How It Works

| Step | Description |
|------|-------------|
| 1 | User from Partner Club visits our Mutual Aid page |
| 2 | System recognizes them via federation API |
| 3 | They see the full map and all helpers |
| 4 | They can use the contact form freely (unlimited) |
| 5 | To see direct contact info, they click "Unlock contact" |
| 6 | Each unlock counts toward their 3-contact limit |
| 7 | After 3 unlocks, they can request full access |
| 8 | Admin reviews and approves/rejects |

### Contact Limits

| User Status | Contact Unlocks | Duration |
|-------------|-----------------|----------|
| External (new) | 3 | Per club, rolling 30 days |
| External (approved) | Unlimited | Until approval expires (1 year) |
| External (blocked) | 0 | Permanent until admin unblocks |

### What Counts as an Unlock

| Action | Counts? |
|--------|---------|
| Viewing helper on map | ❌ No |
| Viewing helper card (name, skills, city) | ❌ No |
| Using the contact form | ❌ No |
| Clicking "Show phone number" | ✅ Yes |
| Clicking "Show email" | ✅ Yes |
| Clicking "Open WhatsApp" | ✅ Yes |

**Important:** If a helper has not enabled any contact info, visitors cannot unlock anything for that helper (only the form is available).

---

## FederatedAidAccess Model

Tracks external users accessing our Mutual Aid.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| source_club | FK(FederatedClub) | Which partner club |
| external_user_id | String | User ID on their site |
| external_display_name | String | Their display name |
| contacts_unlocked | Integer | Count of unlocked contacts |
| access_level | Choice | limited / full / blocked |
| first_access | DateTime | First visit |
| last_access | DateTime | Most recent activity |
| approved_by | FK(User) | Admin who approved (if full) |
| approved_at | DateTime | When approved |
| approval_expires | DateTime | When approval ends |
| notes | Text | Admin notes |

**Access Levels:**

| Level | Description |
|-------|-------------|
| limited | Default, 3-contact limit applies |
| full | Admin approved, unlimited contacts |
| blocked | Admin blocked, no contact access |

---

## Full Access Request

### When Limit Is Reached

When an external user exhausts their 3 contacts, they see:

| Element | Content |
|---------|---------|
| Message | "You have used all 3 contact unlocks" |
| Explanation | "To continue using our Mutual Aid network, you can request full access" |
| Option 1 | "Request Full Access" button |
| Option 2 | "Use contact form instead" (always works) |

### Request Process

| Step | Actor | Action |
|------|-------|--------|
| 1 | External user | Clicks "Request Full Access" |
| 2 | External user | Optionally adds message explaining why |
| 3 | System | Creates FederatedAidAccessRequest |
| 4 | System | Notifies admins (email + in-app) |
| 5 | Admin | Reviews request in admin panel |
| 6 | Admin | Sees: user name, club, membership valid, contacts used |
| 7 | Admin | Approves, rejects, or blocks |
| 8 | System | Notifies external user of decision |

### FederatedAidAccessRequest Model

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| federated_access | FK | Link to FederatedAidAccess |
| message | Text | User's message (optional) |
| status | Choice | pending / approved / rejected |
| created_at | DateTime | When requested |
| reviewed_by | FK(User) | Admin who handled |
| reviewed_at | DateTime | When handled |
| rejection_reason | Text | Why rejected (optional) |

---

## Admin Panel for Federation

### External Access Dashboard

**Location:** Wagtail Admin → Mutual Aid → External Access

### List View

| Column | Description |
|--------|-------------|
| User | Display name + source club |
| Status | 🟡 Limited / 🟢 Full / 🔴 Blocked |
| Contacts Used | e.g., "3 of 3" or "12 (unlimited)" |
| Last Access | Relative time |
| Actions | View / Approve / Block |

### Pending Requests

| Column | Description |
|--------|-------------|
| User | Display name |
| Club | Source club name |
| Requested | When |
| Message | User's message (truncated) |
| Actions | ✅ Approve / ❌ Reject / 🚫 Block |

### Bulk Actions

| Action | Description |
|--------|-------------|
| Approve selected | Grant full access |
| Reset limits | Reset contact count to 0 |
| Block selected | Revoke all access |

### Admin Notifications

| Event | Notification |
|-------|--------------|
| New access request | Email + Push to admins |
| Request pending > 3 days | Reminder email |
| Request auto-expired (7 days) | Log only |

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
| **From partner clubs** | Requests from external visitors |

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
| New request (local member) | Email + Push |
| New request (external visitor) | Email + Push (marked as external) |
| Request cancelled | Email |
| Thank you received | Email |

### To External Visitor

| Event | Notification |
|-------|--------------|
| Full access approved | Email via federation API |
| Full access rejected | Email via federation API |
| Contact unlocked | Confirmation on screen |
| Limit reached | Alert with options |

### To Admin

| Event | Notification |
|-------|--------------|
| New full access request | Email + Push |
| Request pending > 3 days | Email reminder |

---

## Configuration

### Settings

| Setting | Default | Description |
|---------|---------|-------------|
| FEDERATION_AID_ENABLED | True | Enable federated access |
| GUEST_CONTACT_LIMIT | 3 | Unlocks before limit |
| APPROVED_CONTACT_LIMIT | 0 | Unlocks after approval (0 = unlimited) |
| APPROVAL_DURATION_DAYS | 365 | How long approval lasts |
| REQUEST_EXPIRY_DAYS | 7 | Auto-reject pending requests |
| LIMIT_RESET_DAYS | 30 | Rolling window for limit count |
| NOTIFY_ADMINS_ON_REQUEST | True | Email admins for requests |

### Environment Variables

| Variable | Description |
|----------|-------------|
| FEDERATION_AID_ENABLED | Master switch for federated aid |

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
| **Ambassador** | Helped member from partner club |

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

**Location:** Wagtail Admin → Mutual Aid → Helpers

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

### With Federation

| Feature | Integration |
|---------|-------------|
| Partner recognition | Via [92-EVENT-FEDERATION.md](92-EVENT-FEDERATION.md) |
| External user tracking | FederatedAidAccess model |
| Admin approval | FederatedAidAccessRequest model |
| Cross-club notifications | Via federation API |

---

## Implementation Checklist

### Phase 1: Core

- [ ] MutualAidPage model
- [ ] AidSkill snippet
- [ ] User model extensions
- [ ] Privacy controls (per-field)
- [ ] Interactive map (Leaflet)
- [ ] Helper card component
- [ ] Contact form
- [ ] Helper dashboard

### Phase 2: Federation

- [ ] FederatedAidAccess model
- [ ] FederatedAidAccessRequest model
- [ ] External user detection
- [ ] Contact unlock counter
- [ ] Limit reached UI
- [ ] Full access request flow
- [ ] Admin approval panel
- [ ] Admin notifications
- [ ] External user notifications

### Phase 3: Polish

- [ ] Rating system
- [ ] Gamification badges
- [ ] Emergency mode
- [ ] Translations

---

## Files to Create/Modify

| File | Purpose |
|------|---------|
| apps/mutual_aid/models.py | Add FederatedAidAccess, FederatedAidAccessRequest |
| apps/mutual_aid/views.py | Add external user handling |
| apps/mutual_aid/wagtail_hooks.py | Admin panels for external access |
| templates/mutual_aid/helper_card.html | Add external visitor badge |
| templates/mutual_aid/limit_reached.html | Limit reached modal |
| templates/mutual_aid/access_request_form.html | Request full access |

---

## References

- [80-MEMBERSHIP-SYSTEM.md](80-MEMBERSHIP-SYSTEM.md) - User model, display_name
- [41-MULTILANG.md](41-MULTILANG.md) - Translation workflow
- [42-SNIPPETS.md](42-SNIPPETS.md) - AidSkill snippet
- [84-PWA-PUSH.md](84-PWA-PUSH.md) - Push notifications
- [87-ROUTE-MAPS.md](87-ROUTE-MAPS.md) - Map integration
- [91-NOTIFICATIONS.md](91-NOTIFICATIONS.md) - Notification system
- [92-EVENT-FEDERATION.md](92-EVENT-FEDERATION.md) - Federation system
