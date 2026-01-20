# Transactional Models

## Overview

Guidelines for choosing between Django Models and Wagtail Snippets for data storage.

---

## Decision Rule

| Use Case | Model Type |
|----------|------------|
| High-volume, user-generated data | Django Model |
| Editorial content managed manually | Wagtail Snippet |
| Transactional records (logs, registrations) | Django Model |
| Reusable content (FAQ, partners) | Wagtail Snippet |

---

## Django Models (Transactional)

### Activity Log

Tracks user actions across the site.

| Field | Type | Description |
|-------|------|-------------|
| actor | FK to User | Who performed action |
| action_type | Choice | photo, event, membership |
| verb | Text | Action description (e.g., "registered for") |
| target_type | Text | Content type name |
| target_id | Integer | Content object ID |
| target_title | Text | Content title (denormalized) |
| target_url | Text | Content URL (denormalized) |
| created_at | DateTime | When action occurred |

### Reaction

User reactions to content (likes, loves).

| Field | Type | Description |
|-------|------|-------------|
| user | FK to User | Who reacted |
| content_type | Text | What type of content |
| object_id | Integer | Which content |
| reaction_type | Choice | like, love |
| created_at | DateTime | When reacted |

**Unique constraint:** One reaction per user per object.

### Comment

User comments on content.

| Field | Type | Description |
|-------|------|-------------|
| user | FK to User | Who commented |
| content_type | Text | What type of content |
| object_id | Integer | Which content |
| text | Text | Comment body |
| created_at | DateTime | When posted |
| is_approved | Boolean | Moderation status |
| parent | FK to self | For threaded replies |

---

## Admin Integration

### Activity Log Admin

| Feature | Description |
|---------|-------------|
| Menu | "Activity" in Wagtail admin |
| Display | Actor, verb, target, date |
| Filters | Action type, date range |
| Read-only | No editing, view only |

### Comments Admin

| Feature | Description |
|---------|-------------|
| Menu | "Comments" in Wagtail admin |
| Display | User, text preview, status |
| Filters | Approved / Pending / All |
| Actions | Approve, Reject, Delete |

---

## Activity Triggers

Activities are logged automatically when:

| Event | Activity Created |
|-------|-----------------|
| Event registration | "{user} registered for {event}" |
| Photo uploaded | "{user} uploaded photo to {collection}" |
| Photo approved | "{user}'s photo was approved" |
| Membership renewed | "{user} renewed membership" |
| Comment posted | "{user} commented on {content}" |

---

## Reactions Usage

### Where Reactions Appear

| Content Type | Reactions Enabled |
|--------------|-------------------|
| NewsPage | Yes (configurable) |
| EventDetailPage | Yes (configurable) |
| GalleryImage | Yes (configurable) |
| Comment | No |

### Display

| Element | Description |
|---------|-------------|
| Count | Total reactions by type |
| User State | User's own reaction highlighted |
| Toggle | Click to add/remove reaction |

---

## Comments Usage

### Where Comments Appear

| Content Type | Comments Enabled |
|--------------|------------------|
| NewsPage | Optional (per page setting) |
| EventDetailPage | Optional (per page setting) |
| GalleryImage | No |
| ExternalEvent | Yes (local organization only) |

**Note:** ExternalEvent comments use `ExternalEventComment` model and are visible only to local members. See [92-EVENT-FEDERATION.md](92-EVENT-FEDERATION.md).

### Moderation

| Setting | Options |
|---------|---------|
| Pre-moderation | All comments require approval |
| Post-moderation | Comments visible, can be removed |
| Trusted users | Auto-approve for verified members |

---

## Performance Considerations

### Denormalization

Target title and URL stored with activity to avoid joins.

### Cleanup

| Rule | Action |
|------|--------|
| Activities > 2 years | Archive or delete |
| Orphaned reactions | Clean up when content deleted |
| Spam comments | Auto-delete after rejection |

---

## Site Settings

### Activity Settings

```
Settings → Activity
```

| Setting | Type | Description |
|---------|------|-------------|
| Log activities | Boolean | Enable activity logging |
| Retention days | Integer | Days to keep activities |
| Public activity feed | Boolean | Show on homepage |

### Comment Settings

```
Settings → Comments
```

| Setting | Type | Description |
|---------|------|-------------|
| Enable comments | Boolean | Site-wide toggle |
| Moderation mode | Choice | Pre / Post / Trusted |
| Notify on comment | Boolean | Email moderators |

---

## References

- [85-MODERATION.md](85-MODERATION.md) - Content moderation
- [80-MEMBERSHIP-SYSTEM.md](80-MEMBERSHIP-SYSTEM.md) - Member system
- [92-EVENT-FEDERATION.md](92-EVENT-FEDERATION.md) - Federation models (FederatedClub, ExternalEvent, ExternalEventInterest, ExternalEventComment)
