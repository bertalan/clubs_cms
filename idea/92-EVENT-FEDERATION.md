# Event Federation System

## Overview

Federated event sharing between sites built on this project. Clubs can exchange public API keys to share their events, creating a network where members can discover events from partner clubs and express interest.

### Key Principles

| Principle | Description |
|-----------|-------------|
| **Separate table** | External events never mix with local Wagtail pages |
| **Anonymous engagement** | Only counts shown ("3 from Partner Club interested"), no names |
| **Manual approval** | Admin pre-approves trusted partner sites |
| **Optional reciprocity** | Can receive without sharing back |
| **Member comments** | Members can organize together ("Who drives from Milan?") |
| **Email notifications** | Alerts for new partner events and interest updates |

---

## Architecture

### System Overview

```
┌─────────────────────┐         ┌─────────────────────┐
│      Our Club       │◄───────►│    Partner Club     │
│       (Site A)      │   API   │       (Site B)      │
└──────────┬──────────┘ secure  └──────────┬──────────┘
           │                               │
           ▼                               ▼
┌─────────────────────┐         ┌─────────────────────┐
│   Local Events      │         │   Local Events      │
│   (Wagtail Pages)   │         │   (Wagtail Pages)   │
└─────────────────────┘         └─────────────────────┘
           │                               │
           ▼                               ▼
┌─────────────────────┐         ┌─────────────────────┐
│  External Events    │◄───────►│  External Events    │
│   (Django Model)    │  sync   │   (Django Model)    │
└─────────────────────┘         └─────────────────────┘
```

### Data Flow

```
1. Admin adds partner club with their public API key
2. Cron job fetches events from partner API
3. Events stored in ExternalEvent table
4. Members browse external events on frontend
5. Members can express interest (going/maybe/interested)
6. Interest counts shared back to origin club (anonymous)
7. Members can comment to organize (visible only locally)
```

---

## Models

### FederatedClub

Partner club configuration. Only admin can create/edit.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| name | CharField(255) | Display name ("Partner Club") |
| short_code | CharField(20) | URL-safe code ("partnerclub") |
| base_url | URLField | Partner site URL ("https://partnerclub.example.com") |
| logo_url | URLField | Optional logo URL for display |
| api_key | CharField(64) | Their public API key (given to us) |
| our_key_for_them | CharField(64) | Our key we gave them |
| is_active | Boolean | Enable sync |
| is_approved | Boolean | Admin approved this partner |
| share_our_events | Boolean | Share our events with them |
| auto_import | Boolean | Auto-show their events (vs manual review) |
| last_sync | DateTimeField | Last successful sync |
| last_error | TextField | Last sync error message |
| created_at | DateTimeField | When added |
| created_by | ForeignKey(User) | Admin who added |

**Notes:**
- `is_approved` must be True for sync to work
- `share_our_events` controls if we expose our API to them
- `auto_import` if False, external events need manual approval

### ExternalEvent

Events fetched from partner clubs. **Never editable by admin** (read-only).

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Local unique identifier |
| source_club | ForeignKey(FederatedClub) | Origin club |
| external_id | CharField(100) | ID on source site |
| event_name | CharField(255) | Event title |
| start_date | DateTimeField | Start date/time |
| end_date | DateTimeField | End date/time (nullable) |
| location_name | CharField(255) | Venue name |
| location_address | CharField(500) | Full address |
| location_lat | FloatField | Latitude (nullable) |
| location_lon | FloatField | Longitude (nullable) |
| description | TextField | Event description (sanitized HTML) |
| event_status | CharField(20) | EventScheduled/Cancelled/etc |
| image_url | URLField | Remote image URL |
| detail_url | URLField | Link to original event page |
| is_approved | Boolean | Admin approved for display |
| is_hidden | Boolean | Admin hidden from display |
| fetched_at | DateTimeField | When first fetched |
| updated_at | DateTimeField | Last update from source |

**Unique constraint:** `(source_club, external_id)`

**Notes:**
- Image served from original URL (no local copy)
- Description sanitized to remove scripts
- `is_approved` required if club has `auto_import=False`

### ExternalEventInterest

Member interest in an external event.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| user | ForeignKey(User) | Member expressing interest |
| external_event | ForeignKey(ExternalEvent) | Target event |
| interest_level | CharField(20) | going/maybe/interested |
| created_at | DateTimeField | When expressed |
| updated_at | DateTimeField | Last change |

**Unique constraint:** `(user, external_event)`

**Interest levels:**

| Value | Display | Emoji |
|-------|---------|-------|
| interested | Interested | 👀 |
| maybe | Maybe | 🤔 |
| going | Going! | ✅ |

### ExternalEventComment

Comments on external events for member organization.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| user | ForeignKey(User) | Author |
| external_event | ForeignKey(ExternalEvent) | Target event |
| content | TextField | Comment text |
| created_at | DateTimeField | When posted |
| updated_at | DateTimeField | Last edit |
| is_deleted | Boolean | Soft delete |

**Notes:**
- Comments visible only to local members
- Not shared with partner club
- Supports soft delete for moderation

---

## API Endpoints

### Public API (for partners to consume)

**Base URL:** `/api/federation/`

#### GET /api/federation/events/

Returns our public events. Requires valid API key.

**Request Headers:**

| Header | Required | Description |
|--------|----------|-------------|
| X-Federation-Key | Yes | Partner's API key for us |
| X-Timestamp | Yes | ISO 8601 timestamp |
| X-Signature | Yes | HMAC-SHA256 signature |

**Request:**
```http
GET /api/federation/events/
X-Federation-Key: pk_abc123...
X-Timestamp: 2026-01-20T10:30:00Z
X-Signature: sha256=abcdef123...
```

**Response:**
```json
{
  "club": {
    "name": "Our Motoclub",
    "code": "ourclub",
    "url": "https://example.com"
  },
  "events": [
    {
      "id": "evt_12345",
      "event_name": "Spring Rally 2026",
      "start_date": "2026-04-15T09:00:00+02:00",
      "end_date": "2026-04-15T18:00:00+02:00",
      "location_name": "Main Square",
      "location_address": "Main Square 1, City",
      "location_lat": 45.0715,
      "location_lon": 7.6858,
      "description": "Annual rally...",
      "event_status": "EventScheduled",
      "image_url": "https://example.com/media/events/rally.jpg",
      "detail_url": "https://example.com/events/spring-rally-2026/",
      "interest_count": {
        "going": 12,
        "maybe": 5,
        "interested": 23
      }
    }
  ],
  "total": 1,
  "last_updated": "2026-01-20T10:00:00Z"
}
```

**Filters (query params):**

| Param | Type | Description |
|-------|------|-------------|
| from_date | ISO date | Events starting from |
| to_date | ISO date | Events starting until |
| status | string | Filter by status |

#### POST /api/federation/interest/

Receive interest notification from partner (anonymous count only).

**Request:**
```json
{
  "event_id": "evt_12345",
  "counts": {
    "going": 3,
    "maybe": 2,
    "interested": 5
  },
  "club_code": "partnerclub"
}
```

**Response:**
```json
{
  "status": "ok",
  "received": true
}
```

**Note:** Only counts received, never user identities.

---

## Security

### API Key Exchange

1. Admin A generates a key pair in their admin
2. Admin A sends PUBLIC key to Admin B (email, phone, etc.)
3. Admin B adds the key to their FederatedClub record
4. Admin B sends their PUBLIC key to Admin A
5. Both admins verify via a test sync

### Key Format

```
Public key:  pk_[32 random chars]
Secret key:  sk_[64 random chars]
```

### Request Signing

Every API request must be signed:

```python
# Signing
import hmac
import hashlib
from datetime import datetime

def sign_request(secret_key: str, timestamp: str, body: str = "") -> str:
    message = f"{timestamp}:{body}"
    signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"
```

### Verification

```python
def verify_request(request, partner: FederatedClub) -> bool:
    # Check timestamp not older than 5 minutes
    timestamp = request.headers.get('X-Timestamp')
    if is_too_old(timestamp, max_age=300):
        return False
    
    # Verify signature
    provided_sig = request.headers.get('X-Signature')
    expected_sig = sign_request(
        partner.our_key_for_them,
        timestamp,
        request.body.decode()
    )
    return hmac.compare_digest(provided_sig, expected_sig)
```

### Rate Limiting

| Resource | Limit |
|----------|-------|
| Events fetch | 60 requests/hour per partner |
| Interest post | 120 requests/hour per partner |
| Failed auth | Block after 10 failures/hour |

### Security Checklist

| Check | Description |
|-------|-------------|
| ✅ HTTPS only | Reject non-SSL requests |
| ✅ Timestamp check | Max 5 minutes clock drift |
| ✅ HMAC signature | Verify every request |
| ✅ Rate limiting | Prevent abuse |
| ✅ Input sanitization | Strip scripts from descriptions |
| ✅ Admin approval | Partners must be pre-approved |

---

## Admin Interface

### Partner Management (Wagtail Snippets)

**Location:** Wagtail Admin → Settings → Federated Clubs

**List View Columns:**

| Column | Description |
|--------|-------------|
| Club name | With logo if available |
| Status | Active/Inactive badge |
| Approved | ✅ or ⏳ |
| Last sync | Relative time ("2 hours ago") |
| Events | Count of imported events |
| Actions | Sync now / Edit / Deactivate |

**Add/Edit Form Sections:**

| Section | Fields |
|---------|--------|
| Basic Info | name, short_code, base_url, logo_url |
| API Keys | api_key (theirs), our_key_for_them (readonly, generated) |
| Permissions | is_active, is_approved, share_our_events, auto_import |
| Status | last_sync, last_error (readonly) |

**Generate Key Button:**
- Creates new `our_key_for_them`
- Shows it once with "Copy to clipboard"
- Admin must send this to partner

### External Events (Read-Only Panel)

**Location:** Wagtail Admin → Federation → External Events

**List View:**

| Column | Description |
|--------|-------------|
| Event | Name with date |
| Partner | Source club name |
| Date | Start date |
| Status | EventScheduled/Cancelled |
| Approved | ✅ / ⏳ / ❌ |
| Interests | Count from our members |
| Actions | View / Approve / Hide |

**Bulk Actions:**

| Action | Description |
|--------|-------------|
| Approve selected | Mark as approved |
| Hide selected | Hide from frontend |
| Refresh selected | Re-fetch from source |

**Filters:**

| Filter | Options |
|--------|---------|
| Source club | Dropdown of active partners |
| Status | Scheduled / Cancelled / Postponed |
| Approval | Pending / Approved / Hidden |
| Date | Upcoming / Past / This month |

---

## Frontend Display

### Events from Partners Page

**URL:** `/eventi/partner/` or integrated into main events page

**Page Structure:**

```
┌─────────────────────────────────────────────────────┐
│  EVENTI DAI CLUB PARTNER                            │
│  "Scopri gli eventi organizzati dai nostri amici"   │
├─────────────────────────────────────────────────────┤
│  [Filters: Club ▼] [Date ▼] [Location ▼]            │
├─────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐             │
│  │ Event 1 │  │ Event 2 │  │ Event 3 │             │
│  │ MC Tori │  │ MC Roma │  │ MC Mila │             │
│  │ 15 Apr  │  │ 22 Apr  │  │ 1 May   │             │
│  │ 12 👥   │  │ 5 👥    │  │ 23 👥   │             │
│  └─────────┘  └─────────┘  └─────────┘             │
└─────────────────────────────────────────────────────┘
```

### Event Card

| Element | Content |
|---------|---------|
| Image | Event image (from source) or club logo |
| Club badge | Partner club name + logo |
| Title | Event name |
| Date/Time | Start date, formatted |
| Location | Venue name |
| Interest count | "12 del nostro club interessati" |
| Interest button | Only for logged-in members |

### Event Detail View

**URL:** `/eventi/partner/{club_code}/{event_id}/`

**Sections:**

1. **Header**
   - Event image or placeholder
   - Partner club badge
   - Event title
   - Date and location

2. **Description**
   - Full event description (sanitized)
   - Link to original event page

3. **Interest Panel** (members only)
   ```
   ┌──────────────────────────────────────┐
   │  Sei interessato?                    │
   │  [👀 Interessato] [🤔 Forse] [✅ Ci vado!] │
   │                                      │
   │  12 soci interessati                 │
   │  (nomi non visibili per privacy)     │
   └──────────────────────────────────────┘
   ```

4. **Organization Comments** (members only)
   ```
   ┌──────────────────────────────────────┐
   │  💬 Let's organize!                  │
   ├──────────────────────────────────────┤
   │  User1: "Who's leaving at 8am?"      │
   │  └─ 2h ago                           │
   │                                      │
   │  User2: "Me! I have room for 2"      │
   │  └─ 1h ago                           │
   │                                      │
   │  [Write a comment...        ] [Send] │
   └──────────────────────────────────────┘
   ```

5. **Map**
   - OpenStreetMap with event location
   - Directions link

6. **External Link**
   - Prominent button: "Vai all'evento originale →"

### Interest Counts Display

| Count | Display |
|-------|---------|
| 0 | "Sii il primo a mostrare interesse!" |
| 1-5 | "X soci interessati" |
| 6-20 | "X soci interessati 🔥" |
| 21+ | "X soci interessati 🔥🔥" |

**Anonymous display:** Never show names or avatars to preserve privacy.

---

## Email Notifications

### Notification Types

| Type | Trigger | Recipients |
|------|---------|------------|
| New partner events | Sync finds new events | All members (digest) |
| Interest milestone | 5/10/20 interests reached | Members who showed interest |
| New comment | Someone comments on event | Members interested in event |
| Event update | Event details changed | Members interested in event |
| Event cancelled | Event cancelled at source | Members interested in event |

### User Preferences

Add to notification preferences (see 91-NOTIFICATIONS.md):

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| partner_events | Boolean | True | Receive partner event alerts |
| partner_event_comments | Boolean | True | Comments on interested events |

### Email Templates

#### New Partner Events (Digest)

**Subject:** "Nuovi eventi dai club partner 🏍️"

```
Ciao {name},

I nostri club partner hanno aggiunto nuovi eventi:

📅 Spring Rally - Partner Club A
   15 April 2026 • Main Square
   [Show interest →]

📅 Lakes Tour - Partner Club B  
   22 April 2026 • Lake Como
   [Mostra interesse →]

[Vedi tutti gli eventi partner →]
```

#### Interest Milestone

**Subject:** "🔥 10 members interested in Spring Rally!"

```
The event you're interested in is getting attention!

📅 Spring Rally - Partner Club
   15 April 2026

✅ 10 soci del nostro club interessati

[Vedi chi organizza il viaggio →]
```

---

## Sync Process

### Scheduled Task

**Frequency:** Every 2 hours (configurable)

**Command:** `python manage.py sync_federation`

### Sync Steps

1. **For each active, approved partner:**
   ```
   a. Build signed request
   b. Fetch /api/federation/events/
   c. Validate response schema
   d. For each event:
      - If new: Create ExternalEvent
      - If exists: Update fields
      - If removed from source: Mark as cancelled
   e. Update partner.last_sync
   f. If auto_import=False: Leave is_approved=False
   ```

2. **Error handling:**
   ```
   - Network error: Log, retry next cycle
   - Auth error: Log, mark partner.last_error
   - Parse error: Log, skip invalid events
   - After 3 consecutive failures: Notify admin
   ```

### Interest Sync (Outgoing)

When member expresses interest, optionally notify source club:

1. Aggregate counts for event
2. POST to partner's `/api/federation/interest/`
3. Only send counts, never user data

**Frequency:** Batch every 15 minutes (not real-time)

---

## Privacy Considerations

### What We Share

| Data | Shared? | Notes |
|------|---------|-------|
| Event details | ✅ Yes | Public events only |
| Interest counts | ✅ Yes | Aggregated only |
| Member names | ❌ No | Never shared |
| Member emails | ❌ No | Never shared |
| Comments | ❌ No | Local only |

### What We Receive

| Data | Usage |
|------|-------|
| Event details | Display to members |
| Interest counts | Show "X from Partner Club interested" |
| No personal data | Partners cannot send user info |

### GDPR Compliance

- No personal data crosses site boundaries
- Users can delete their interest (removes from counts)
- Partners only see anonymous aggregates
- Local comments can be deleted by user

---

## Database Migrations

### New Tables

| Table | Description |
|-------|-------------|
| federation_federatedclub | Partner club configuration |
| federation_externalevent | Imported events |
| federation_externaleventinterest | Member interest records |
| federation_externaleventcomment | Organization comments |

### Indexes

| Table | Index |
|-------|-------|
| ExternalEvent | (source_club, external_id) unique |
| ExternalEvent | (start_date) for date filtering |
| ExternalEvent | (is_approved, is_hidden) for display |
| ExternalEventInterest | (user, external_event) unique |
| ExternalEventInterest | (external_event) for counts |
| ExternalEventComment | (external_event, created_at) |

---

## Configuration

### Settings

```python
# settings/base.py

FEDERATION_SETTINGS = {
    # Sync frequency in seconds (default 2 hours)
    "SYNC_INTERVAL": 60 * 60 * 2,
    
    # How long before request expires (seconds)
    "REQUEST_MAX_AGE": 300,
    
    # Max events to fetch per partner
    "MAX_EVENTS_PER_SYNC": 100,
    
    # Enable interest sync back to partners
    "SHARE_INTEREST_COUNTS": True,
    
    # Batch interest updates interval (seconds)
    "INTEREST_SYNC_INTERVAL": 60 * 15,
    
    # Days of future events to fetch
    "FETCH_FUTURE_DAYS": 365,
    
    # Rate limit per partner per hour
    "RATE_LIMIT_REQUESTS": 60,
}
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| FEDERATION_ENABLED | Master switch (true/false) |
| FEDERATION_OUR_CLUB_CODE | Our club identifier |
| FEDERATION_OUR_CLUB_NAME | Our display name |

---

## Implementation Checklist

### Phase 1: Core Models & Admin

- [ ] Create `apps/federation/` app
- [ ] Define FederatedClub model
- [ ] Define ExternalEvent model
- [ ] Define ExternalEventInterest model
- [ ] Define ExternalEventComment model
- [ ] Create migrations
- [ ] Register Wagtail snippets/viewsets
- [ ] Add admin list views
- [ ] Add key generation utility

### Phase 2: API Layer

- [ ] Create API endpoints
- [ ] Implement request signing
- [ ] Implement signature verification
- [ ] Add rate limiting
- [ ] Add input sanitization
- [ ] Write API tests

### Phase 3: Sync System

- [ ] Create sync management command
- [ ] Implement event fetching
- [ ] Implement event updating
- [ ] Add error handling
- [ ] Set up cron/celery task
- [ ] Add sync status monitoring

### Phase 4: Frontend

- [ ] Create partner events list template
- [ ] Create partner event detail template
- [ ] Add interest buttons (HTMX)
- [ ] Add comments section
- [ ] Add map integration
- [ ] Style with current theme

### Phase 5: Notifications

- [ ] Add notification preferences
- [ ] Create email templates
- [ ] Integrate with digest system
- [ ] Add milestone notifications
- [ ] Add comment notifications

### Phase 6: Polish

- [ ] Add translations (IT, EN, FR, ES, DE)
- [ ] Performance optimization (caching)
- [ ] Admin documentation
- [ ] User guide

---

## Files to Create

```
apps/federation/
├── __init__.py
├── apps.py
├── models.py              # All models
├── admin.py               # Django admin (minimal)
├── wagtail_hooks.py       # Wagtail admin panels
├── api/
│   ├── __init__.py
│   ├── views.py           # API endpoints
│   ├── serializers.py     # DRF serializers (optional)
│   └── security.py        # Signing/verification
├── sync/
│   ├── __init__.py
│   └── tasks.py           # Sync logic
├── management/
│   └── commands/
│       └── sync_federation.py
├── migrations/
├── urls_api.py            # API URL patterns
├── urls_frontend.py       # Frontend URL patterns
└── views.py               # Frontend views

templates/federation/
├── external_events_list.jinja2
├── external_event_detail.jinja2
├── includes/
│   ├── event_card.jinja2
│   ├── interest_buttons.jinja2
│   └── comments_section.jinja2
└── emails/
    ├── new_partner_events.html
    ├── interest_milestone.html
    └── new_comment.html
```

---

## Related Documents

- [82-EVENT-REGISTRATIONS.md](82-EVENT-REGISTRATIONS.md) - Local event registration
- [83-TRANSACTIONAL-MODELS.md](83-TRANSACTIONAL-MODELS.md) - Django models pattern
- [90-MUTUAL-AID.md](90-MUTUAL-AID.md) - Federated Mutual Aid Network
- [91-NOTIFICATIONS.md](91-NOTIFICATIONS.md) - Notification system
- [13-NEWS-EVENTS.md](13-NEWS-EVENTS.md) - EventDetailPage model
