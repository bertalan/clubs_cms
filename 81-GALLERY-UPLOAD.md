# Gallery - Member Uploads

## Overview

Members with upload permission can submit photos to the gallery. Photos go through a moderation queue before being published.

---

## Custom Image Model

Extends Wagtail's native Image with member upload fields.

### Additional Fields

| Field | Type | Description |
|-------|------|-------------|
| uploaded_by | FK to User | Member who uploaded |
| is_approved | Boolean | Moderation status |
| uploaded_at | DateTime | Upload timestamp |
| event | FK to EventDetailPage | Optional linked event |

### Admin Path

```
Images → All Images
```

Filter by:
- `is_approved`: Yes / No
- `uploaded_by`: Member selection

---

## Upload Flow

### Requirements

| Requirement | Condition |
|-------------|-----------|
| Authenticated | User must be logged in |
| Active Member | `is_active_member = True` |
| Upload Permission | Product with `grants_upload = True` |

### Upload Form

| Field | Type | Required |
|-------|------|----------|
| Photo | Image file | Yes |
| Title | Text | No (auto-generated from filename) |
| Event | Dropdown | No |

### Form Location

| Page | Element |
|------|---------|
| Gallery Page | Upload button (if permitted) |
| Event Page | "Add photos" section |
| Account | "My uploads" page |

---

## Upload URL

```
/account/upload-photo/
```

### Form Settings

| Setting | Value |
|---------|-------|
| Max file size | 10 MB |
| Allowed formats | JPG, PNG, WebP |
| Multiple files | Yes (up to 20) |

---

## Batch Upload

Upload multiple photos at once with shared metadata.

### Batch Form Fields

| Field | Type | Applied To |
|-------|------|------------|
| Photos | Multiple files | Individual |
| Title Prefix | Text | All (+ sequential number) |
| Description | Text | All photos |
| Tags | Tag selector | All photos |
| Event | Dropdown | All photos |
| Collection | Dropdown | All photos |

### Title Generation

| Setting | Example |
|---------|--------|
| Prefix: "Raduno 2026" | "Raduno 2026 - 01", "Raduno 2026 - 02"... |
| No prefix | Filename used as title |

### Tags (Snippet)

Reusable tags for photo organization.

| Field | Type | Description |
|-------|------|-------------|
| name | Text | Tag name |
| slug | Slug | URL-safe identifier |

### Admin Path

```
Snippets → Photo Tags
```

### Tag Examples

| Tag | Usage |
|-----|-------|
| raduno | Club gatherings |
| gita | Day trips |
| moto-storiche | Vintage bikes |
| premiazioni | Awards |
| sociale | Social events |

### Batch Upload Flow

| Step | Action |
|------|--------|
| 1. Select files | Drag & drop or file picker |
| 2. Set shared metadata | Title prefix, description, tags |
| 3. Preview | Thumbnails with auto-titles |
| 4. Upload | Progress bar per file |
| 5. Complete | Summary with success/errors |

---

## Moderation Queue

### Admin Panel

```
Wagtail Admin → Pending Photos
```

### Queue Display

| Column | Field |
|--------|-------|
| Thumbnail | Image preview |
| Title | Photo title |
| Uploaded By | Member name |
| Event | Linked event (if any) |
| Date | Upload date |
| Actions | Approve / Reject |

### Bulk Actions

| Action | Description |
|--------|-------------|
| Approve Selected | Approve multiple photos |
| Reject Selected | Delete multiple photos |
| Assign to Event | Link to specific event |
| Assign to Collection | Move to collection |

---

## Approval Process

### On Approval

| Action | Description |
|---------|-------------|
| Set `is_approved = True` | Photo visible in gallery |
| Assign Collection | Based on event or default |
| Notify User | Optional email notification |
| Add to Activity | Log in member activity |

### On Rejection

| Action | Description |
|--------|-------------|
| Delete Image | Remove from media |
| Notify User | Optional email with reason |

---

## Collections Assignment

### Automatic

| Condition | Collection |
|-----------|------------|
| Event linked | Event's collection |
| No event | "Member Uploads" default collection |

### Manual

Moderator can reassign to any collection during approval.

---

## Member Dashboard

### My Uploads Page

```
/account/my-uploads/
```

### Display

| Section | Content |
|---------|---------|
| Pending | Photos awaiting approval |
| Approved | Published photos |
| Rejected | Rejected (last 30 days) |

### Stats

| Metric | Description |
|--------|-------------|
| Total Uploads | All-time count |
| Approved | Approved count |
| Pending | Awaiting moderation |

---

## Notifications

### Email Templates

| Event | Email |
|-------|-------|
| Upload received | Confirmation |
| Photo approved | Published notification |
| Photo rejected | Rejection with reason |

---

## Permissions

| Action | Who |
|--------|-----|
| Upload photos | Members with `grants_upload` |
| View pending | Staff / Moderators |
| Approve/Reject | Staff / Moderators |
| Delete own | Uploader (pending only) |

---

## References

- [14-GALLERY.md](14-GALLERY.md) - Gallery page and collections
- [80-MEMBERSHIP-SYSTEM.md](80-MEMBERSHIP-SYSTEM.md) - Member products and permissions
- [85-MODERATION.md](85-MODERATION.md) - Moderation system
