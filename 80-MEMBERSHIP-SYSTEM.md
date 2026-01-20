# Member System

## Overview

Complete member management system for the motorcycle club with:
- Full personal data (anagrafica)
- Composable products (package manager)
- QR code and barcode for member cards
- Public profile with published content
- Favorite events

### Multilingual

| Element | Translatable |
|---------|-------------|
| Product snippet | Yes (name, description) |
| Profile page labels | Via template i18n |
| Member card | Universal logo, i18n text |
| User data | No (personal data) |

See [41-MULTILANG.md](41-MULTILANG.md) for translation workflow.

---

## User Model

### Personal Data

| Field | Type | Description |
|-------|------|-------------|
| username | Text | Login username |
| email | Email | Email (unique) |
| first_name | Text | First name |
| last_name | Text | Last name |
| display_name | Text | Public display name (nickname) |
| phone | Text | Phone number |
| mobile | Text | Mobile number |
| birth_date | Date | Date of birth |
| birth_place | Text | Place of birth |
| photo | Image | Profile photo |

### Display Name System

| Field | Type | Description |
|-------|------|-------------|
| display_name | Text | Shown to public instead of real name |
| show_real_name_to_members | Boolean | Members can see first_name + last_name |
| show_real_name_to_admins | Boolean | Admins can always see real name |

### Name Visibility Rules

| Viewer | Sees |
|--------|------|
| Public (not logged in) | display_name only |
| Registered user (not member) | display_name only |
| Active member | display_name OR real name (if allowed) |
| Admin/Staff | Always real name + display_name |

### Display Logic

```
get_visible_name(viewer):
  if viewer.is_admin:
    return f"{first_name} {last_name} ({display_name})"
  elif viewer.is_active_member and show_real_name_to_members:
    return f"{first_name} {last_name}"
  else:
    return display_name or f"{first_name} {last_name[0]}."
```

### Default Display Name

If `display_name` is empty, system generates: `first_name + last_name initial` (e.g., "Mario R.")

### Identity Document

| Field | Type | Description |
|-------|------|-------------|
| fiscal_code | Text (16) | Tax identification number |
| document_type | Choice | ID Card / License / Passport |
| document_number | Text | Document number |
| document_expiry | Date | Document expiration |

### Address

| Field | Type | Description |
|-------|------|-------------|
| address | Text | Street and number |
| city | Text | City |
| province | Text (2) | Province/State |
| postal_code | Text (5) | Postal code |
| country | Choice | Country (default: Italy) |

### Membership Card

| Field | Type | Description |
|-------|------|-------------|
| card_number | Text | Card number (auto-generated) |
| membership_date | Date | First membership date |
| membership_expiry | Date | Card expiration |
| products | M2M Relation | Assigned products |

### Preferences

| Field | Type | Description |
|-------|------|-------------|
| newsletter | Boolean | Receives newsletter |
| show_in_directory | Boolean | Visible in member directory |
| public_profile | Boolean | Public profile enabled |
| bio | Long Text | Biography for public profile |

---

## Products (Snippet)

Modular system to compose member profiles. Each product is an assignable "tag".

### Product Fields

| Field | Type | Description |
|-------|------|-------------|
| name | Text | Product name |
| slug | Slug | Unique identifier |
| description | Text | Description |
| price | Decimal | Cost (€) |
| is_active | Boolean | Product active |
| order | Integer | Display order |

### Product Permissions

| Field | Type | Description |
|-------|------|-------------|
| grants_vote | Boolean | Voting rights |
| grants_upload | Boolean | Can upload photos |
| grants_events | Boolean | Can register for events |
| grants_discount | Integer | Event discount % |

### Product Examples

| Product | Price | Vote | Upload | Events |
|---------|-------|------|--------|--------|
| Basic Card | €20 | ❌ | ❌ | ✅ |
| Voting Rights | €0 | ✅ | ❌ | ❌ |
| Gallery Access | €0 | ❌ | ✅ | ❌ |
| ASI Insurance | €15 | ❌ | ❌ | ❌ |
| Premium Newsletter | €5 | ❌ | ❌ | ❌ |

### Profile Composition

| Profile | Products | Total |
|---------|----------|-------|
| **Regular** | Basic Card + Vote | €20 |
| **Supporter** | Basic Card + Vote + Newsletter | €25 |
| **Junior** | Basic Card | €20 |
| **Honorary** | All (free) | €0 |
| **Premium** | Card + Vote + Gallery + Newsletter | €25 |

### Admin Path

```
Snippets → Products
```

---

## QR Code and Barcode

### Automatic Generation

Generated automatically when saving a member:

| Type | Format | Content |
|------|--------|---------|
| QR Code | PNG 300x300 | vCard with member data |
| Barcode | PNG Code128 | Card number |

### QR Code Content (vCard)

| Field | Value |
|-------|-------|
| FN | First Last Name |
| TEL | Phone |
| EMAIL | Email |
| ORG | Club Name |
| NOTE | Card: XXX - Expires: DD/MM/YYYY |

### Barcode Content

Card number in Code128 format, readable by scanners.

### Python Libraries

| Library | Function |
|---------|----------|
| `qrcode` | Generate QR code |
| `python-barcode` | Generate Code128 barcode |

### Storage

Generated images are automatically saved as:
- `media/members/qr/{card_number}.png`
- `media/members/barcode/{card_number}.png`

---

## Public Profile

### URL

```
/members/{username}/
```

### Visibility

| Condition | Profile Visible |
|-----------|-----------------|
| `public_profile = True` | ✅ |
| `public_profile = False` | ❌ (404) |

### Displayed Content

| Section | Description |
|---------|-------------|
| Info | Name, photo, bio |
| News | Articles published by member |
| Events | Events created/organized |
| Gallery | Uploaded albums/photos |
| Favorites | Saved events (if public) |

### Counts

| Data | Description |
|------|-------------|
| Articles | Number of published news |
| Events | Number of organized events |
| Photos | Number of uploaded photos |
| Favorites | Number of saved events |

### Privacy

| Field | Show in Profile |
|-------|-----------------|
| First and last name | ✅ Always |
| Email | ❌ Never (privacy) |
| Phone | ❌ Never (privacy) |
| City | ✅ If `show_in_directory` |
| Bio | ✅ If filled |

---

## Favorite Events

See [86-FAVORITE-EVENTS.md](86-FAVORITE-EVENTS.md) for complete details.

### Summary

| Feature | Description |
|---------|-------------|
| Heart button | Save event |
| My Events | Favorites list page |
| Map | OpenStreetMap view |
| ICS Export | Export to calendar |
| Profile Link | Share public favorites |
| Auto-Archive | Archive past events by year |
| Rotation | Keep last 10 favorites |

---

## Admin Panel

### Members Menu

```
Wagtail Admin → Members
```

### List View

| Column | Field |
|--------|-------|
| Username | username |
| Name | first_name + last_name |
| Card | card_number |
| Expiry | membership_expiry |
| Products | products (count) |
| Status | is_active_member |

### Filters

| Filter | Options |
|--------|---------|
| Status | Active / Expired / All |
| Products | Multiple selection |
| Expiry | Next 30/60/90 days |
| Newsletter | Yes / No |

### Search

| Searchable Fields |
|-------------------|
| username |
| first_name |
| last_name |
| email |
| fiscal_code |
| card_number |

### Bulk Actions

| Action | Description |
|--------|-------------|
| Renew | Extend expiry by 1 year |
| Add Product | Assign product to selection |
| Remove Product | Remove product from selection |
| Export CSV | Download member list |

---

## Derived Permissions

Member permissions derive from the sum of assigned products:

| Check | Logic |
|-------|-------|
| `can_vote` | At least one product with `grants_vote = True` |
| `can_upload` | At least one product with `grants_upload = True` |
| `can_register_events` | At least one product with `grants_events = True` |
| `discount_percent` | Maximum among assigned products |

### Member Status

| Property | Condition |
|----------|-----------|
| `is_active_member` | `membership_expiry >= today` |
| `is_expired` | `membership_expiry < today` |
| `days_to_expiry` | Days until expiry |

---

## Digital Card

### Card Page

```
/account/card/
```

### Content

| Section | Description |
|---------|-------------|
| Header | Club logo + year |
| Photo | Member profile photo |
| Data | Name, card number, expiry |
| QR Code | For quick verification |
| Barcode | Scannable card number |

### Print

"Print Card" button generates credit card format PDF:
- Front: Logo, photo, name, number
- Back: QR code, barcode, expiry

---

## Notifications

### Automatic Emails

| Event | Email |
|-------|-------|
| Welcome | New registration |
| Card Active | Products assigned |
| Expiry 30 days | Renewal reminder |
| Expiry 7 days | Urgent renewal |
| Expired | Card expired |
| Renewed | Renewal confirmation |

### Email Templates

```
templates/account/emails/
├── welcome.html
├── card_active.html
├── expiry_reminder.html
├── expiry_urgent.html
├── expired.html
└── renewed.html
```

---

## Integration

### With Events

| Feature | Requirement |
|---------|-------------|
| Event registration | `can_register_events` |
| Registration discount | `discount_percent` |
| Favorite events | `is_active_member` |

### With Gallery

| Feature | Requirement |
|---------|-------------|
| Photo upload | `can_upload` |
| Photos in profile | `public_profile` |

### With News

| Feature | Requirement |
|---------|-------------|
| Author articles | `is_staff` or specific permission |
| Articles in profile | `public_profile` |

---

## References

- [81-GALLERY-UPLOAD.md](81-GALLERY-UPLOAD.md) - Member photo uploads
- [82-EVENT-REGISTRATIONS.md](82-EVENT-REGISTRATIONS.md) - Event registration
- [86-FAVORITE-EVENTS.md](86-FAVORITE-EVENTS.md) - Favorite events
