# Content Moderation

## Overview

User-generated content (photos, comments, contributions) goes through a moderation queue before publication.

---

## Moderable Content Types

| Content | Moderation |
|---------|------------|
| Member photos | Always |
| Comments | Configurable |
| Member stories | Always |
| Event proposals | Always |

---

## Moderation Status

### Fields

| Field | Type | Description |
|-------|------|-------------|
| is_approved | Boolean | Approved for publication |
| approved_by | FK to User | Who approved |
| approved_at | DateTime | When approved |
| rejection_reason | Text | If rejected, why |

### Status Values

| Status | Description |
|--------|-------------|
| Pending | Awaiting review |
| Approved | Published |
| Rejected | Not published |

---

## Admin Panel

### Moderation Queue

```
Wagtail Admin → Moderation
```

### Queue Display

| Column | Content |
|--------|---------|
| Type | Photo / Comment / Story |
| Preview | Thumbnail or text excerpt |
| Author | User who submitted |
| Submitted | Date/time |
| Actions | Approve / Reject / View |

### Filters

| Filter | Options |
|--------|---------|
| Content Type | All / Photos / Comments / Stories |
| Date Range | From - To |
| Author | User search |

---

## Quick Actions

### Approve

| Step | Action |
|------|--------|
| Click Approve | Sets `is_approved = True` |
| Auto-fill | `approved_by` = current user |
| Auto-fill | `approved_at` = now |
| Result | Content visible on site |

### Reject

| Step | Action |
|------|--------|
| Click Reject | Opens reason modal |
| Enter reason | Optional message |
| Confirm | Content deleted or flagged |
| Result | Author notified (optional) |

### Bulk Actions

| Action | Description |
|--------|-------------|
| Approve selected | Approve multiple items |
| Reject selected | Reject multiple items |
| Delete selected | Permanently remove |

---

## Dashboard Widget

### Pending Count

Shows in Wagtail admin dashboard:

| Element | Content |
|---------|---------|
| Badge | Number of pending items |
| Link | Direct to moderation queue |
| Alert | "X items need review" |

---

## Notifications

### To Moderators

| Event | Notification |
|-------|--------------|
| New submission | Email (configurable) |
| Daily digest | Summary of pending |
| High volume | Alert if queue > threshold |

### To Authors

| Event | Notification |
|-------|--------------|
| Submitted | "Your content is under review" |
| Approved | "Your content is now live" |
| Rejected | "Your content was not approved" + reason |

---

## Auto-Moderation (Optional)

### Trusted Users

| Setting | Description |
|---------|-------------|
| Auto-approve | Skip queue for trusted members |
| Trust criteria | X approved items, Y months member |

### Content Filters

| Filter | Action |
|--------|--------|
| Profanity check | Flag for review |
| Spam detection | Auto-reject |
| Duplicate check | Flag duplicates |

---

## Permissions

| Action | Who |
|--------|-----|
| Submit content | Members with appropriate product |
| View queue | Staff, Moderators |
| Approve/Reject | Staff, Moderators |
| Configure settings | Admin only |

### Moderator Role

| Permission | Description |
|------------|-------------|
| View moderation queue | Yes |
| Approve content | Yes |
| Reject content | Yes |
| Edit content | No (view only) |
| Delete content | Configurable |

---

## Settings

### Site Settings → Moderation

| Setting | Type | Description |
|---------|------|-------------|
| Photo moderation | Boolean | Require approval for photos |
| Comment moderation | Choice | None / Pre / Post |
| Story moderation | Boolean | Require approval for stories |
| Notify moderators | Boolean | Email on new submission |
| Notify authors | Boolean | Email on status change |
| Auto-approve trusted | Boolean | Skip queue for trusted users |
| Trusted threshold | Integer | Items needed for trust |

---

## References

- [81-GALLERY-UPLOAD.md](81-GALLERY-UPLOAD.md) - Photo uploads
- [83-TRANSACTIONAL-MODELS.md](83-TRANSACTIONAL-MODELS.md) - Comments
- [85-CONTRIBUTION-BASE.md](85-CONTRIBUTION-BASE.md) - Member contributions
