# PWA - Push Notifications

## Overview

Send push notifications to members who opt-in. Uses Web Push protocol with VAPID authentication.

---

## Requirements

### Library

| Package | Purpose |
|---------|---------|
| django-webpush | Python Web Push library |
| pywebpush | Low-level push sending |

### VAPID Keys

Generate once per site, store in settings.

| Key | Description |
|-----|-------------|
| Public Key | Shared with browser |
| Private Key | Server-side only |
| Email | Contact for push service |

---

## Subscription Storage

### Fields

| Field | Type | Description |
|-------|------|-------------|
| user | FK to User | Subscriber |
| endpoint | Text | Push service URL |
| p256dh | Text | Encryption key |
| auth | Text | Auth secret |
| is_active | Boolean | Subscription valid |
| created_at | DateTime | When subscribed |
| user_agent | Text | Browser info |

### Unique Constraint

One subscription per user per endpoint (user can have multiple devices).

---

## User Opt-In Flow

### Step 1: Permission Request

| Element | Location |
|---------|----------|
| Prompt | Account settings or notification bell |
| Text | "Enable notifications for event reminders" |
| Buttons | Allow / Not now |

### Step 2: Browser Permission

Browser shows native permission dialog.

### Step 3: Subscription

On "Allow", browser returns subscription object sent to server.

### Step 4: Confirmation

| Feedback | Description |
|----------|-------------|
| Success | "Notifications enabled" |
| Denied | "You can enable later in settings" |

---

## Notification Types

### Event Notifications

| Trigger | Message |
|---------|---------|
| New event published | "New event: {title}" |
| Event reminder (1 day) | "Tomorrow: {event} at {time}" |
| Event reminder (1 hour) | "Starting soon: {event}" |
| Registration confirmed | "You're registered for {event}" |

### Member Notifications

| Trigger | Message |
|---------|---------|
| Membership expiring (7 days) | "Membership expires in 7 days" |
| Membership expired | "Your membership has expired" |
| Photo approved | "Your photo has been published" |

### Admin Notifications

| Trigger | Message |
|---------|---------|
| New registration | "{user} registered for {event}" |
| Content pending | "{n} items awaiting moderation" |

---

## Admin Configuration

### Site Settings → Notifications

| Setting | Type | Description |
|---------|------|-------------|
| Push enabled | Boolean | Master toggle |
| VAPID public key | Text | Public key |
| Event notifications | Boolean | Send for new events |
| Reminder hours | List | When to send reminders |

### Per-User Settings

| Setting | Type | Default |
|---------|------|---------|
| Event reminders | Boolean | True |
| New events | Boolean | True |
| Membership alerts | Boolean | True |

---

## Sending Notifications

### Manual Send

Admin can send notification to:
- All subscribers
- Specific user
- Event registrants
- Membership type

### Automated Send

| Trigger | Timing |
|---------|--------|
| New event | On publish |
| Event reminder | Cron job (daily check) |
| Membership expiry | Cron job (daily check) |

---

## Notification Content

### Structure

| Field | Description |
|-------|-------------|
| title | Notification title |
| body | Message text |
| icon | Site icon |
| badge | Small badge icon |
| url | Click destination |

### Click Behavior

User clicks notification → opens URL in browser.

---

## Error Handling

### Invalid Subscription

| Error | Action |
|-------|--------|
| 404/410 | Mark subscription inactive |
| Expired | Delete subscription |
| Rate limit | Retry with backoff |

### Cleanup

| Task | Frequency |
|------|-----------|
| Remove inactive | Weekly |
| Retry failed | Daily |

---

## Privacy

### Data Stored

| Data | Purpose |
|------|---------|
| Endpoint | Send notifications |
| Keys | Encryption |
| Device info | Debugging |

### User Control

| Action | Method |
|--------|--------|
| Opt-out | Account settings toggle |
| Delete subscription | Unsubscribe button |
| Browser revoke | Browser settings |

---

## References

- [84-PWA-BASE.md](84-PWA-BASE.md) - PWA base setup
- [80-SISTEMA-SOCI.md](80-SISTEMA-SOCI.md) - Member system
- [91-NOTIFICATIONS.md](91-NOTIFICATIONS.md) - Full notification system (email + push + queue)

---

## Note

This document covers the PWA-specific push subscription mechanics. For the complete notification system including:
- Email notifications
- Notification queue and scheduling
- User preferences (day/time)
- Weekend favorites reminder
- One-click unsubscribe
- API endpoints

See **[91-NOTIFICATIONS.md](91-NOTIFICATIONS.md)**.
