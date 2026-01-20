# Member Contributions

## Overview

Members can submit content to the site. All submissions go through moderation before publication.

---

## Contribution Types

| Type | Description | Approval |
|------|-------------|----------|
| Event photos | Photos from club events | Moderated |
| Trip story | Ride report with text and photos | Moderated |
| Event proposal | Suggest a new event | Moderated |
| Announcement | Short notice for members | Moderated |

---

## Trip Story Submission

### Access

| URL | `/account/submit-story/` |
|-----|--------------------------|
| Requirement | Active member |
| Menu | Account → Submit Story |

### Form Fields

| Field | Type | Required |
|-------|------|----------|
| Title | Text | Yes |
| Date | Date picker | Yes |
| Introduction | Text (200 chars) | Yes |
| Content | Rich text | Yes |
| Cover Image | Image upload | Yes |
| Gallery | Multiple images | No |
| Related Event | Dropdown | No |

### Submission Flow

| Step | Action |
|------|--------|
| 1. Fill form | Member enters content |
| 2. Submit | Creates draft NewsPage |
| 3. Queue | Appears in moderation queue |
| 4. Review | Moderator approves/rejects |
| 5. Publish | Page goes live |

### Draft State

| Property | Value |
|----------|-------|
| live | False |
| owner | Submitting user |
| author | Submitting user |
| is_user_contributed | True |

---

## Event Proposal

### Access

| URL | `/account/propose-event/` |
|-----|---------------------------|
| Requirement | Active member |
| Menu | Account → Propose Event |

### Form Fields

| Field | Type | Required |
|-------|------|----------|
| Event Name | Text | Yes |
| Date | Date picker | Yes |
| Description | Text | Yes |
| Location | Text | Yes |
| Estimated Participants | Number | No |
| Notes | Text | No |

### Proposal Flow

| Step | Action |
|------|--------|
| 1. Submit | Creates proposal record |
| 2. Review | Admin reviews proposal |
| 3. Approve | Admin creates actual event |
| 4. Notify | Member notified of decision |

---

## Announcement Submission

### Access

| URL | `/account/submit-announcement/` |
|-----|----------------------------------|
| Requirement | Active member with permission |
| Menu | Account → Submit Announcement |

### Form Fields

| Field | Type | Required |
|-------|------|----------|
| Title | Text | Yes |
| Content | Text | Yes |
| Expiry Date | Date | No |

---

## Author Attribution

### NewsPage Extension

| Field | Type | Description |
|-------|------|-------------|
| author | FK to User | Content author |
| is_user_contributed | Boolean | Member-submitted |

### Display

| Element | Location |
|---------|----------|
| Author name | Article byline |
| Author avatar | Optional |
| Author profile link | If public profile enabled |

---

## My Contributions Page

### Access

```
/account/my-contributions/
```

### Sections

| Section | Content |
|---------|---------|
| Pending | Awaiting moderation |
| Published | Live content |
| Rejected | Rejected submissions |

### Display Columns

| Column | Content |
|--------|---------|
| Type | Story / Event / Announcement |
| Title | Submission title |
| Date | Submitted date |
| Status | Pending / Published / Rejected |
| Views | View count (if published) |

### Actions

| Action | Condition |
|--------|-----------|
| View | Always |
| Edit | While pending |
| Delete | While pending |

---

## Permissions

### Required Products

| Action | Product Permission |
|--------|-------------------|
| Submit story | `grants_upload` or specific |
| Propose event | Active member |
| Submit announcement | Staff or specific permission |

### Limits

| Limit | Value |
|-------|-------|
| Stories per month | 5 (configurable) |
| Proposals per month | 3 (configurable) |
| Pending limit | 3 (must approve before more) |

---

## Quality Guidelines

### Displayed to Members

| Guideline | Description |
|-----------|-------------|
| Image quality | Minimum 1200px wide |
| Text length | Minimum 200 words for stories |
| Relevance | Must be club-related |
| Originality | Own photos only |

---

## Site Settings

### Settings → Contributions

| Setting | Type | Description |
|---------|------|-------------|
| Enable stories | Boolean | Allow story submissions |
| Enable proposals | Boolean | Allow event proposals |
| Stories per month | Integer | Limit per user |
| Notify on submission | Boolean | Email moderators |
| Auto-approve trusted | Boolean | Skip queue for trusted |

---

## References

- [81-GALLERY-UPLOAD.md](81-GALLERY-UPLOAD.md) - Photo uploads
- [85-MODERATION.md](85-MODERATION.md) - Moderation system
- [80-MEMBERSHIP-SYSTEM.md](80-MEMBERSHIP-SYSTEM.md) - Member permissions
