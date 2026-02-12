# Event Registration System

## Overview

Anyone can register for events. Members receive exclusive discounts. Administrators manage registrations, capacity, and attendance through the Wagtail admin.

### Open Registration Policy

| User Type | Can Register | Discount |
|-----------|--------------|----------|
| Guest (not logged in) | ✅ Yes | None |
| Registered user (not member) | ✅ Yes | None |
| Active member | ✅ Yes | Member discount |

### Member Discount Incentive

Non-members see the member price alongside their price with a CTA:

| Element | Description |
|---------|-------------|
| Standard price | Price for non-members |
| Member price | Discounted price (crossed out if not member) |
| CTA link | "Become a member and save €X" → /become-member/ |
| Savings badge | Shows potential savings |

---

## EventDetailPage - Additional Fields

### Registration Settings

| Field | Type | Description |
|-------|------|-------------|
| registration_open | Boolean | Accept registrations |
| max_participants | Integer | Capacity (0 = unlimited) |
| allow_guests | Boolean | Can bring guests |
| max_guests | Integer | Max guests per registration |
| require_login | Boolean | Require account (not membership) |

### Pricing

| Field | Type | Description |
|-------|------|-------------|
| participation_fee | Decimal | Base cost (€) |
| member_discount | Integer | % discount for members |

---

## Pricing Tiers (Unified System)

A single repeatable structure handles both early booking discounts AND registration deadline.

### Tier Fields

| Field | Type | Description |
|-------|------|-------------|
| days_before | Integer | Days before event start |
| hours_before | Integer | Hours before event start |
| minutes_before | Integer | Minutes before event start |
| discount_percent | Integer | % discount (0 = no discount) |
| label | Text | Display label |
| is_deadline | Boolean | If true, registration closes after this tier |

### How It Works

Tiers are evaluated from longest to shortest time before event. The first matching tier applies.

```
Example: Event starts March 20, 2026 at 10:00

Tier 1: 60 days, 0h, 0m → discount 20% → "Super Early Bird"
Tier 2: 30 days, 0h, 0m → discount 10% → "Early Bird"  
Tier 3: 7 days, 0h, 0m → discount 5% → "Advance"
Tier 4: 0 days, 12h, 0m → discount 0% → "Standard" → is_deadline = true

Timeline:
- Jan 19 → 20% off (Super Early Bird)
- Feb 18 → 10% off (Early Bird)
- Mar 13 → 5% off (Advance)
- Mar 19 22:00 → Full price, last chance
- Mar 19 22:01 → CLOSED
```

### Tier Examples

| Days | Hours | Min | Discount | Label | Deadline? |
|------|-------|-----|----------|-------|-----------|
| 60 | 0 | 0 | 20% | Super Early Bird | No |
| 30 | 0 | 0 | 10% | Early Bird | No |
| 7 | 0 | 0 | 5% | Advance | No |
| 2 | 0 | 0 | 0% | Standard | No |
| 0 | 2 | 0 | 0% | Last Minute | ✅ Yes |

### Simplified Configurations

**Only deadline, no discounts:**

| Days | Hours | Discount | Label | Deadline? |
|------|-------|----------|-------|-----------|
| 0 | 12 | 0% | - | ✅ Yes |

Closes 12 hours before event, no early booking discounts.

**Only early booking, closes at event start:**

| Days | Hours | Discount | Label | Deadline? |
|------|-------|----------|-------|-----------|
| 30 | 0 | 15% | Early Bird | No |
| 0 | 0 | 0% | Standard | ✅ Yes |

Discount until 30 days before, then full price until event starts.

### Price Display

| Element | Content |
|---------|---------|
| Current price | Calculated with active tier discount |
| Original price | Strikethrough if discounted |
| Savings | "Save €X" badge |
| Next tier | "Book by {date} to save {%}" |
| Deadline | "Registration closes {date/time}" |

### Deadline Display

| Time Remaining | Display |
|----------------|---------|
| More than 7 days | "Registration closes: {date}" |
| 1-7 days | "Only {X} days left to register!" |
| Less than 24 hours | "Only {X} hours left!" |
| Less than 1 hour | "Closing soon! {X} minutes left" |
| Closed | "Registration closed" |

### Computed Properties

| Property | Logic |
|----------|-------|
| `current_tier` | First tier where now < event_start - tier_time |
| `current_discount` | current_tier.discount_percent |
| `current_price` | participation_fee * (1 - current_discount/100) |
| `deadline_datetime` | Tier with is_deadline=true, calculated time |
| `registration_closed` | now > deadline_datetime |

### Price Display

| Element | Content |
|---------|--------|
| Current price | Calculated with applicable discount |
| Original price | Strikethrough if discounted |
| Savings | "Save €X" badge |
| Deadline | "Book by {date} to save {%}" |

### Logistics

| Field | Type | Description |
|-------|------|-------------|
| meeting_point | Text | Meeting location |
| meeting_time | Time | Departure time |
| difficulty | Choice | Easy / Medium / Challenging |
| requirements | RichText | What to bring |

### Computed Properties

| Property | Description |
|----------|-------------|
| available_spots | max_participants - confirmed registrations |
| is_full | available_spots = 0 |
| registration_closed | deadline passed or event started |

---

## Registration Model

Django model (not Snippet) for high-volume transactional data.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| event | FK to EventDetailPage | Which event |
| user | FK to User | Who registered |
| status | Choice | registered, confirmed, cancelled |
| registered_at | DateTime | When registered |
| guests | Integer | Number of guests (0+) |
| guest_names | Text | Guest names (optional) |
| notes | Text | Special requirements |
| payment_status | Choice | pending, paid, refunded |

### Status Values

| Status | Description |
|--------|-------------|
| registered | Initial registration |
| confirmed | Confirmed by admin or payment |
| cancelled | Cancelled by user or admin |
| waitlist | Event full, on waiting list |

---

## Passenger/Companion Management

Riders can register a passenger (pillion). Passenger may or may not be a member.

### Passenger Fields

| Field | Type | Required |
|-------|------|----------|
| has_passenger | Boolean | No |
| passenger_is_member | Boolean | No |
| passenger_member | FK to User | If member |
| passenger_first_name | Text | No* |
| passenger_last_name | Text | No* |
| passenger_email | Email | No |
| passenger_phone | Text | No |
| passenger_fiscal_code | Text | No |
| passenger_birth_date | Date | No |
| passenger_emergency_contact | Text | No |

*Required if `has_passenger = True` and `passenger_is_member = False`

### Passenger Selection Flow

| Step | Action |
|------|--------|
| 1. Toggle | "I'm bringing a passenger" |
| 2. Member check | "Is passenger a club member?" |
| 3a. If member | Select from member dropdown |
| 3b. If not member | Enter passenger details |
| 4. Optional fields | Emergency contact, dietary needs |

### Member Passenger Lookup

| Method | Description |
|--------|-------------|
| Autocomplete | Search by name |
| Card number | Enter membership card |
| Recent | Show previously registered passengers |

### Passenger Pricing

| Setting | Type | Description |
|---------|------|-------------|
| passenger_fee | Decimal | Additional cost for passenger |
| passenger_discount | Integer | % discount if passenger is member |
| passenger_included | Boolean | Passenger included in base fee |

### Admin Display

| Column | Content |
|--------|--------|
| Rider | Primary registrant |
| Passenger | Name (+ "Member" badge if applicable) |
| Total Fee | Combined price |

### Passenger Count

Capacity can count:
- Riders only
- Riders + Passengers
- Configurable per event

---

## Registration Flow

### Public Event Page

| Element | Display |
|---------|---------|
| Spots available | "X spots left" or "Unlimited" |
| Register button | If open and not full |
| Deadline | "Register by {date}" |
| Fee | Price with member discount |

### Registration Form

| Field | Type | Required |
|-------|------|----------|
| Guests | Number | If `allow_guests` |
| Guest Names | Text | If guests > 0 |
| Notes | Textarea | No |
| Accept Terms | Checkbox | Yes |

### After Registration

| Action | Result |
|--------|--------|
| Confirmation email | Sent immediately |
| Added to My Events | Visible in account |
| Status | "Registered" (pending confirmation) |

---

## User Dashboard

### My Registrations

```
/account/my-registrations/
```

### Display

| Column | Content |
|--------|---------|
| Event | Title + date |
| Status | Badge (registered/confirmed/cancelled) |
| Guests | Number |
| Actions | Cancel, View |

### Actions

| Action | Condition |
|--------|-----------|
| Cancel | Before deadline |
| View Event | Always |
| Download Ticket | If confirmed |

---

## Admin Panel

### Menu

```
Wagtail Admin → Registrations
```

### List View

| Column | Field |
|--------|-------|
| Event | Event title |
| Participant | User name |
| Status | Status badge |
| Guests | Guest count |
| Date | Registration date |
| Payment | Payment status |

### Filters

| Filter | Options |
|--------|---------|
| Event | Dropdown |
| Status | All / Registered / Confirmed / Cancelled |
| Date Range | From - To |
| Payment | Pending / Paid / Refunded |

### Bulk Actions

| Action | Description |
|--------|-------------|
| Confirm | Change status to confirmed |
| Cancel | Cancel selected |
| Send Reminder | Email reminder |
| Export CSV | Download list |

---

## Capacity Management

### When Full

| Option | Description |
|--------|-------------|
| Close registrations | No more registrations |
| Enable waitlist | New registrations go to waitlist |

### Waitlist

| Feature | Description |
|---------|-------------|
| Auto-promote | When spot opens, first waitlist moves to registered |
| Notification | Email sent when promoted |
| Position | Show position in queue |

---

## Notifications

### Email Templates

| Event | Email |
|-------|-------|
| Registration received | Confirmation with details |
| Status confirmed | Ticket/confirmation |
| Reminder | Day before event |
| Cancelled | Cancellation confirmation |
| Waitlist promoted | Spot available |

---

## Permissions

| Action | Who |
|--------|-----|
| Register | Members with `grants_events` |
| Cancel own | Registered user (before deadline) |
| View all registrations | Staff |
| Confirm/Cancel others | Staff |
| Export | Staff |

---

## Captcha Protection

Registration form protected by hCaptcha to prevent spam registrations.

| Setting | Value |
|---------|-------|
| Provider | hCaptcha |
| When | Anonymous or high-traffic events |
| Bypass | Logged-in members (optional) |

---

## References

- [13-NEWS-EVENTS.md](13-NEWS-EVENTS.md) - EventDetailPage base
- [80-MEMBERSHIP-SYSTEM.md](80-MEMBERSHIP-SYSTEM.md) - Member permissions
- [86-FAVORITE-EVENTS.md](86-FAVORITE-EVENTS.md) - Favorite events
