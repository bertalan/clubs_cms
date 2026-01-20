# Notification & Newsletter System

## Overview

Unified notification system for delivering site updates to users via email and PWA push notifications. Designed for Wagtail integration with privacy-first unsubscribe flow.

---

## Core Concepts

### Notification Types

| Type | Trigger | Recipients |
|------|---------|------------|
| News Published | NewsPage goes live | Subscribed users |
| Event Published | EventDetailPage goes live | Subscribed users |
| Event Reminder | X days before event | Registered attendees + favorites |
| Weekend Favorites | Thursday before weekend | Users with favorited weekend events |
| Registration Opens | Event registration enabled | Users who favorited |
| Photo Approved | Member upload approved | Uploader |
| Membership Expiring | 30/7 days before expiry | Member |
| Partner News | Partner updates discount | Members who used that partner |
| Aid Request | Mutual aid request in area | Helpers in radius |

### Delivery Channels

| Channel | Description |
|---------|-------------|
| Email | HTML email with plain text fallback |
| PWA Push | Web Push notification to installed app |
| In-App | Notification bell in navbar (optional) |

---

## User Preferences Model

### Subscription Settings

Each user has notification preferences stored in their profile:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| email_notifications | Boolean | True | Master switch for email |
| push_notifications | Boolean | False | Master switch for PWA push |
| news_updates | Boolean | True | Receive news publications |
| event_updates | Boolean | True | Receive event publications |
| event_reminders | Boolean | True | Reminders before registered events |
| membership_alerts | Boolean | True | Expiry and renewal notices |
| partner_updates | Boolean | False | Partner discount changes |
| aid_requests | Boolean | True | Mutual aid requests (if helper) |

### Digest Frequency

| Option | Description |
|--------|-------------|
| Immediate | Send as soon as content is published |
| Daily | One email per day at configured time |
| Weekly | One email per week on configured day |

Default: **Daily** (reduces email fatigue)

---

## Delivery Schedule

### User-Configurable Timing

Users can choose when to receive notifications:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| digest_day | Choice | Thursday | Day of week for weekly digest |
| digest_time | Time | 09:00 | Preferred delivery time |
| weekend_reminder_day | Choice | Thursday | Day for weekend events reminder |
| weekend_reminder_time | Time | 09:00 | Time for weekend reminder |
| timezone | Choice | Europe/Rome | User's local timezone |

### Day Options

| Value | Label |
|-------|-------|
| monday | Monday |
| tuesday | Tuesday |
| wednesday | Wednesday |
| thursday | Thursday |
| friday | Friday |
| saturday | Saturday |
| sunday | Sunday |

### Time Slots

Predefined time slots (simpler than free-form time picker):

| Slot | Time |
|------|------|
| Early morning | 06:00 |
| Morning | 09:00 |
| Lunch | 12:00 |
| Afternoon | 15:00 |
| Evening | 18:00 |
| Night | 21:00 |

---

## Weekend Favorites Reminder

### Purpose

Automatically notify users about their favorited events happening this weekend.

### How It Works

1. **Scheduled Task** runs on configured day (default: Thursday)
2. **Find Weekend Events**: Events starting Friday 00:00 to Sunday 23:59
3. **Match Favorites**: Find users who favorited these events
4. **Send Reminder**: One email per user listing all their weekend favorites

### Email Content

| Section | Content |
|---------|----------|
| Subject | "This weekend: X events you saved ❤️" |
| Heading | "Your weekend events" |
| List | Each favorited event with date, time, location |
| CTA | "View all my events" → My Events page |
| Footer | Why received + unsubscribe link |

### User Controls

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| weekend_reminder_enabled | Boolean | True | Receive weekend reminders |
| weekend_reminder_day | Choice | Thursday | Which day to receive |
| weekend_reminder_time | Time | 09:00 | What time to receive |

### No Favorites = No Email

If user has no favorited events for the coming weekend, no email is sent.

---

## Email Structure

### Required Elements

Every notification email must include:

1. **Header**
   - Club logo
   - Clear subject line

2. **Content Summary**
   - Title of new content
   - Brief excerpt (max 150 characters)
   - "Read more" link to full content

3. **Why You Received This**
   - Clear explanation in footer
   - Example: "You receive this because you subscribed to News updates"

4. **Unsubscribe Section**
   - One-click unsubscribe link (no login required)
   - Link to manage all preferences (requires login)
   - Example: "Unsubscribe from News updates | Manage preferences"

### Email Templates (Snippets)

| Template | Purpose |
|----------|---------|
| DigestEmail | Daily/weekly summary of multiple items |
| SingleNotification | Immediate notification for one item |
| ReminderEmail | Event reminder |
| ExpiryNotice | Membership expiry warning |
| WelcomeEmail | New subscriber confirmation |

---

## One-Click Unsubscribe Flow

### Security Token

Each unsubscribe link contains a secure token:
- Unique per user + notification type combination
- Long expiry (1 year, regenerated on use)
- Cannot be guessed or enumerated

### Unsubscribe Page Flow

**Step 1: Click Link**
- User clicks unsubscribe link in email
- Link format: `/notifications/unsubscribe/{token}/`

**Step 2: Confirmation Page**
- Shows what they're unsubscribing from
- Shows their email (partially masked: j***@example.com)
- Optional: Text field for feedback ("Why are you leaving?")
- Two buttons: "Confirm Unsubscribe" | "Cancel"

**Step 3: Success Page**
- Confirms unsubscription
- Shows remaining subscriptions
- Link to re-subscribe if it was a mistake
- Link to manage all preferences (requires login)

### No Login Required

The entire unsubscribe flow works without authentication:
- Token validates the user
- Only allows unsubscribe action (not subscribe)
- Feedback is optional and anonymous

---

## PWA Push Notifications

### Registration Flow

1. User enables push in their preferences
2. Browser prompts for permission
3. Push subscription saved to user profile
4. Confirmation push sent: "Notifications enabled!"

### Push Subscription Model

| Field | Description |
|-------|-------------|
| user | Link to user |
| endpoint | Push service URL |
| p256dh_key | Encryption key |
| auth_key | Auth secret |
| created_at | Registration date |
| last_used | Last successful push |
| user_agent | Browser/device info |

### Push Content

Limited by browser constraints:
- Title: max 50 characters
- Body: max 100 characters
- Icon: club logo
- Action: "View" → opens content URL

### Multiple Devices

Users can have multiple push subscriptions (phone, tablet, desktop). Each device is registered separately.

---

## Notification Queue

### How It Works

1. **Trigger**: Content published or event occurs
2. **Queue**: Notification added to queue with recipients
3. **Process**: Background task processes queue
4. **Deliver**: Send via configured channel
5. **Log**: Record delivery status

### Queue Model

| Field | Description |
|-------|-------------|
| notification_type | Type of notification |
| content_object | Link to triggering content |
| recipient | Target user |
| channel | email / push / in_app |
| status | pending / sent / failed / skipped |
| scheduled_for | When to send (for digests) |
| sent_at | Actual send time |
| error_message | If failed, why |

### Digest Processing

For users with daily/weekly digest:
1. Notifications queued but not sent immediately
2. Scheduled task runs at configured time
3. Groups notifications by type
4. Sends single digest email with all items
5. Marks individual notifications as sent

---

## Wagtail Integration

### Page Published Hook

When a page is published:
1. Check if page type is news or event
2. Find users subscribed to that type
3. Create notification queue entries
4. Respect digest preferences

### Admin Panel

**Notifications Dashboard** (in Wagtail admin sidebar):

| View | Content |
|------|---------|
| Queue | Pending notifications with status |
| Sent | Recently sent with open/click rates |
| Failed | Failed deliveries for retry |
| Subscribers | User count by subscription type |

### Bulk Actions

From admin, editors can:
- Retry failed notifications
- Cancel pending notifications
- Send test notification to self
- Preview digest email

---

## API Endpoints

### Public Endpoints (No Auth)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/notifications/unsubscribe/{token}/` | GET | Get unsubscribe info |
| `/api/notifications/unsubscribe/{token}/` | POST | Confirm unsubscribe |

### Authenticated Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/notifications/preferences/` | GET | Get user preferences |
| `/api/notifications/preferences/` | PATCH | Update preferences |
| `/api/notifications/push/register/` | POST | Register push subscription |
| `/api/notifications/push/unregister/` | POST | Remove push subscription |
| `/api/notifications/history/` | GET | User's notification history |

### Internal Endpoints (Admin Only)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/notifications/queue/` | GET | View notification queue |
| `/api/notifications/queue/{id}/retry/` | POST | Retry failed notification |
| `/api/notifications/send-test/` | POST | Send test notification |
| `/api/notifications/stats/` | GET | Delivery statistics |

---

## Service Integration

### Other Systems Can Trigger Notifications

The API allows any system to create notifications:

**Event Registration System**:
- Registration confirmed → notify user
- Waitlist promoted → notify user
- Event cancelled → notify all attendees

**Gallery Upload**:
- Photo approved → notify uploader
- Photo rejected → notify with reason

**Mutual Aid**:
- Help request in area → notify nearby helpers
- Request fulfilled → notify requester

**Partners**:
- New partner added → notify all members (optional)
- Discount changed → notify members who used partner

### Notification Creation API

```
POST /api/notifications/create/
{
  "type": "custom",
  "title": "Your photo was approved",
  "body": "Your photo from Raduno 2026 is now visible",
  "url": "/galleria/raduno-2026/",
  "recipients": [user_id],
  "channels": ["email", "push"]
}
```

---

## Privacy & Compliance

### GDPR Compliance

| Requirement | Implementation |
|-------------|----------------|
| Consent | Explicit opt-in at registration |
| Right to withdraw | One-click unsubscribe |
| Data access | Preferences visible in profile |
| Data deletion | Notifications deleted with account |

### Email Best Practices

| Practice | Implementation |
|----------|----------------|
| List-Unsubscribe header | Included in all emails |
| Physical address | Club address in footer |
| Clear sender | "Motoclub <noreply@domain>" |
| No deceptive subjects | Clear, honest subject lines |

### Rate Limiting

| Limit | Value |
|-------|-------|
| Max emails per user per day | 5 (digests count as 1) |
| Max push per user per hour | 3 |
| Cooldown after unsubscribe | 24 hours before re-enable |

---

## Snippets

### NotificationTemplate

Stores email templates for different notification types:

| Field | Description |
|-------|-------------|
| name | Internal identifier |
| subject | Email subject line |
| heading | Email heading |
| body_template | Body with placeholders |
| cta_text | Call-to-action button text |

### Translation Support

All templates are translatable via Wagtail Localize:
- Subject line
- Heading
- Body template
- CTA text
- Footer text

---

## Background Tasks

### Required Tasks

| Task | Schedule | Purpose |
|------|----------|---------|
| process_notification_queue | Every 5 minutes | Send pending immediate notifications |
| send_daily_digest | Daily at 08:00 | Compile and send daily digests |
| send_weekly_digest | Weekly on Monday 08:00 | Compile and send weekly digests |
| cleanup_old_notifications | Daily at 03:00 | Delete notifications older than 90 days |
| check_expiring_memberships | Daily at 09:00 | Queue expiry reminders |

### Task Runner Options

| Option | Description |
|--------|-------------|
| Django-Q | Lightweight, database-backed |
| Celery | Full-featured, Redis/RabbitMQ |
| Wagtail-specific hooks | For simple cases |

Recommendation: **Django-Q** for simplicity with Wagtail.

---

## User Interface

### Preference Page

In user profile, a "Notifications" tab:

| Section | Controls |
|---------|----------|
| Email Notifications | Master toggle + frequency dropdown |
| Push Notifications | Master toggle + device list |
| Topics | Checkboxes for each notification type |
| Test | "Send me a test notification" button |

### Notification Bell (Optional)

In navbar, a bell icon showing:
- Unread count badge
- Dropdown with recent notifications
- "Mark all as read" link
- "View all" link to full history

---

## Implementation Notes

### Email Service

Use Django's email backend. For production, configure:
- SMTP server (Mailgun, SendGrid, Amazon SES)
- From address
- Reply-to address

### Push Service

Web Push requires:
- VAPID keys (public/private pair)
- Service worker in PWA
- HTTPS (required for push)

### Testing

Admin can:
- Send test email to any address
- Send test push to own devices
- Preview digest with sample content
- Simulate unsubscribe flow

---

## References

- [80-MEMBERSHIP-SYSTEM.md](80-MEMBERSHIP-SYSTEM.md) - Member profile with preferences
- [84-PWA.md](84-PWA.md) - PWA and service worker setup
- [41-MULTILANG.md](41-MULTILANG.md) - Template translation
- [82-EVENT-REGISTRATIONS.md](82-EVENT-REGISTRATIONS.md) - Event registration triggers
