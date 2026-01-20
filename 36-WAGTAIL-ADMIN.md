# Wagtail Admin Configuration

## Theme Management Section

Create a dedicated **Theme Configuration** section in Wagtail admin under Settings:

### Site Settings Panel

| Tab | Contents |
|-----|----------|
| General | Site name, tagline, contact email |
| Theme | Theme selection, color configuration |
| Branding | Logo, favicon, social images |
| Social | Social media links |
| Forms | Captcha configuration |

### Theme Settings Fields

| Field | Type | Description |
|-------|------|-------------|
| Theme | Dropdown | velocity, heritage, terra, zen, clubs, tricolore |
| Color Scheme | Snippet Chooser | Select predefined or custom scheme |
| Dark Mode | Checkbox | Enable dark mode toggle (if theme supports) |
| Custom CSS | Text Area | Additional CSS overrides (optional) |

### Color Configuration Fields

| Field | Type | Default |
|-------|------|---------|
| Primary Color | Color Picker | Theme default |
| Secondary Color | Color Picker | Theme default |
| Accent Color | Color Picker | Theme default |
| Surface Color | Color Picker | #FFFFFF |
| Surface Alt Color | Color Picker | #F5F5F5 |
| Text Primary | Color Picker | #111111 |
| Text Muted | Color Picker | #666666 |

## Color Scheme Snippets

Predefined color schemes are managed as Snippets:

### Admin Location
**Snippets → Color Schemes**

### Fields
| Field | Description |
|-------|-------------|
| Name | Scheme identifier (e.g., "Velocity Dark") |
| Primary | Main brand color |
| Secondary | Accent/highlight color |
| Accent | Links and interactive elements |
| Surface | Background color |
| Surface Alt | Card/section backgrounds |
| Text Primary | Main text color |
| Text Muted | Secondary text color |

### Predefined Schemes

Create via admin or fixtures:
- Velocity Default
- Velocity Dark
- Heritage Gold
- Heritage Navy
- Terra Earth
- Terra Dark
- Zen Light
- Clubs Black
- Tricolore Classic

## Form Settings & Captcha

### Captcha Options

Every form on the site should use one of the following captcha options:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **Honeypot + Time** | Hidden field + submission time check | No external service, GDPR-friendly | Less effective against sophisticated bots |
| **hCaptcha** | Privacy-focused challenges | GDPR compliant, earns credits | May require user interaction |
| **Cloudflare Turnstile** | Privacy-focused alternative | GDPR-friendly, good UX | Requires Cloudflare account |

### Form Settings Fields

| Field | Type | Description |
|-------|------|-------------|
| Captcha Method | Dropdown | honeypot, turnstile, hcaptcha |
| Honeypot Field Name | Text | Random name for honeypot (default: "website") |
| Min Submit Time | Number | Minimum seconds before valid submit (default: 3) |
| hCaptcha Site Key | Text | hCaptcha site key |
| hCaptcha Secret Key | Text | hCaptcha secret key |
| Turnstile Site Key | Text | Cloudflare Turnstile site key |
| Turnstile Secret Key | Text | Cloudflare Turnstile secret key |

### Recommended Configuration

For each form type, configure in admin:

| Form Type | Recommended Captcha |
|-----------|---------------------|
| Contact Form | Honeypot + Time OR Turnstile |
| Newsletter Signup | Honeypot + Time |
| Event Registration | Turnstile OR hCaptcha |
| Member Registration | Turnstile OR hCaptcha |
| Comments | Honeypot + Time |

## Admin Branding

Customize admin appearance in **Settings → Admin Branding**:

| Setting | Description |
|---------|-------------|
| Admin Logo | Logo for login page |
| Admin Color | Primary admin interface color |
| Help URL | Link to user documentation |
| Support Email | Contact for site editors |

## Menu Configuration

### Main Menu
Managed via **Settings → Main Menu**:
- Add/remove menu items
- Drag to reorder
- Set link to page or external URL
- Configure dropdown submenus

### Footer Menu
Managed via **Settings → Footer Menu**:
- Column-based organization
- Links to pages or external URLs
- Social media icons

## Dashboard Customization

### Welcome Panel
- Site name and quick stats
- Recent content updates
- Quick action buttons

### Content Statistics
- Total pages by type
- Recent edits
- Pending moderation

### Custom Dashboard Widgets

Add project-specific widgets to the Wagtail dashboard:

| Widget | Content | Priority |
|--------|---------|----------|
| Recent Registrations | Last 10 event registrations with trend | High |
| Photos Pending | Count of photos awaiting moderation | High |
| Expiring Memberships | Members expiring in next 30 days | Medium |
| Failed Notifications | Notifications that need retry | Medium |
| Aid Requests | Open mutual aid requests | Low |
| Partner Activity | Recent partner verifications | Low |

### Widget Display

| Widget | Shows |
|--------|-------|
| Registration Trend | Sparkline chart (7 days) |
| Pending Count | Badge with number |
| Expiring List | Name, expiry date, days left |
| Failed List | Type, recipient, error, retry button |

---

## Site Settings Extended

### Settings Tabs

Organize Site Settings into logical tabs:

| Tab | Contents |
|-----|----------|
| General | Site name, tagline, contact email |
| Theme | Theme selection, color scheme |
| Branding | Logo, favicon, social images |
| Social | Social media links |
| SEO | Default meta, Organization schema data |
| Forms | Captcha configuration |
| Notifications | Email settings, VAPID keys |
| PWA | App name, icons, manifest settings |

### SEO Tab Fields

| Field | Type | Description |
|-------|------|-------------|
| Organization Name | Text | For schema.org |
| Organization Type | Dropdown | SportsClub, Organization, etc. |
| Phone | Text | Contact phone |
| Email | Email | Contact email |
| Address | Text | Physical address |
| Latitude | Decimal | For maps and schema |
| Longitude | Decimal | For maps and schema |

### Notifications Tab Fields

| Field | Type | Description |
|-------|------|-------------|
| From Email | Email | Sender address |
| Reply-To Email | Email | Reply address |
| SMTP configured | Boolean | Read-only status |
| VAPID Public Key | Text | For push notifications |
| VAPID Private Key | Text | Hidden, for push |
| Default Digest Time | Time | When to send daily digest |
| Weekend Reminder Day | Dropdown | Day for weekend events email |

### PWA Tab Fields

| Field | Type | Description |
|-------|------|-------------|
| App Name | Text | PWA display name |
| Short Name | Text | Max 12 chars |
| App Icon 192 | Image | Android icon |
| App Icon 512 | Image | Splash screen |
| Theme Color | Color | Browser chrome color |
| Enable Offline | Boolean | Cache for offline use |

---

## Admin ViewSets

Register custom admin panels for transactional data using Wagtail's ModelViewSet.

### Members ViewSet

**Admin Path:** Members (in sidebar)

| View | Features |
|------|----------|
| List | Name, email, card number, expiry, status badge |
| Filters | Status (active/expired/pending), expiry range |
| Search | Name, email, card number |
| Actions | Renew, Export CSV, Send reminder |
| Detail | Full profile, products, registrations, uploads |

### Partners ViewSet

**Admin Path:** Partners (in sidebar)

| View | Features |
|------|----------|
| List | Name, category, owner, discount, status |
| Filters | Category, status (active/inactive) |
| Search | Name, description |
| Actions | Assign owner, Toggle status |
| Detail | Full info, verification log, discount history |

### Event Registrations ViewSet

**Admin Path:** Events → Registrations

| View | Features |
|------|----------|
| List | Event, attendee, date, status, payment |
| Filters | Event, status, date range, member/non-member |
| Search | Attendee name, email |
| Actions | Confirm, Cancel, Move to waitlist, Export CSV |
| Detail | Full registration, passenger info, payment |

### Photo Moderation ViewSet

**Admin Path:** Images → Moderation Queue

| View | Features |
|------|----------|
| List | Thumbnail, uploader, date, status |
| Filters | Status (pending/approved/rejected), date |
| Bulk Actions | Approve selected, Reject selected |
| Detail | Full image, metadata, uploader info |

### Aid Requests ViewSet

**Admin Path:** Mutual Aid → Requests

| View | Features |
|------|----------|
| List | Date, requester, location, status |
| Filters | Status (open/resolved), date range |
| Search | Location, requester |
| Actions | Mark resolved, Contact helper |
| Detail | Request details, helper responses |

### Notification Queue ViewSet

**Admin Path:** Notifications → Queue

| View | Features |
|------|----------|
| List | Type, recipient, channel, status, scheduled |
| Filters | Status (pending/sent/failed), type, channel |
| Actions | Retry failed, Cancel pending, Send test |
| Stats | Sent today, failed rate, pending count |

---

## Wagtail Reports

Built-in reports accessible from Reports menu.

### Event Registration Report

| Column | Data |
|--------|------|
| Event | Event name with link |
| Total Registrations | Count |
| Members | Count (%) |
| Non-Members | Count (%) |
| Revenue | Sum of payments |
| Waitlist | Count |

**Filters:** Date range, event category
**Export:** CSV, PDF

### Membership Status Report

| Column | Data |
|--------|------|
| Status | Active / Expiring / Expired |
| Count | Number of members |
| Percentage | Of total |
| Trend | vs. previous period |

**Filters:** Date range, product type
**Export:** CSV

### Notification Delivery Report

| Column | Data |
|--------|------|
| Period | Day/Week/Month |
| Sent | Total sent |
| Delivered | Successfully delivered |
| Failed | Failed attempts |
| Open Rate | Email opens (%) |
| Click Rate | Link clicks (%) |

**Filters:** Date range, notification type, channel
**Export:** CSV

### Photo Upload Report

| Column | Data |
|--------|------|
| Period | Week/Month |
| Uploaded | Total submitted |
| Approved | Published |
| Rejected | Rejected |
| Pending | Awaiting review |

---

## Bulk Actions

### Photo Moderation

| Action | Description |
|--------|-------------|
| Approve Selected | Publish all selected photos |
| Reject Selected | Reject with optional reason |
| Assign Collection | Move to specific collection |
| Add Tags | Apply tags to selected |

### Notification Queue

| Action | Description |
|--------|-------------|
| Retry Failed | Requeue failed notifications |
| Cancel Pending | Remove from queue |
| Send Now | Override schedule, send immediately |

### Event Registrations

| Action | Description |
|--------|-------------|
| Export Selected | Download as CSV |
| Send Reminder | Email selected attendees |
| Confirm All | Confirm pending registrations |
| Cancel All | Cancel with notification |

### Member Management

| Action | Description |
|--------|-------------|
| Export Selected | Download as CSV |
| Send Renewal | Email renewal reminder |
| Extend Membership | Add days to expiry |
| Generate Cards | Batch PDF generation |

---

## User Permissions

### Editor Groups

| Group | Permissions |
|-------|-------------|
| Editors | Create/edit pages, manage images |
| Moderators | Publish pages, manage comments, moderate photos |
| Designers | Edit theme settings, color schemes |
| Admins | Full access |

### Extended Groups

| Group | Permissions |
|-------|-------------|
| Partner Owners | Edit own partner only, view verifications |
| Press Editors | Manage press releases, brand assets |
| Aid Coordinators | Manage aid network, view helpers |
| Notification Managers | Manage notification queue, templates |
| Member Managers | View/edit members, registrations, renewals |

### Permission Matrix

| Feature | Editor | Moderator | Partner Owner | Press | Aid Coord | Notif Mgr | Member Mgr | Admin |
|---------|--------|-----------|---------------|-------|-----------|-----------|------------|-------|
| Pages | Edit | Publish | - | Press only | - | - | - | All |
| Images | Upload | Moderate | Own | Press | - | - | - | All |
| Members | - | View | - | - | View | - | Edit | All |
| Partners | - | - | Own | - | - | - | - | All |
| Registrations | - | View | - | - | - | - | Edit | All |
| Aid Network | - | - | - | - | Edit | - | - | All |
| Notifications | - | - | - | - | - | Edit | - | All |

---

## Admin API Endpoints

Internal API for admin functionality.

### Image Metadata

**Endpoint:** `/admin/api/image-metadata/{id}/`

| Method | Returns |
|--------|---------|
| GET | Title, description, tags, focal point |

Used by gallery upload to display existing metadata.

### Partner Verification

**Endpoint:** `/admin/api/partner/verify/`

| Method | Body | Returns |
|--------|------|---------|
| POST | card_number, secondary_check | is_valid, display_name, expiry |

Used by partner verification page.

### Notification Test

**Endpoint:** `/admin/api/notifications/test/`

| Method | Body | Returns |
|--------|------|---------|
| POST | type, channel, recipient | success, message |

Used to test notification delivery.

### Member Lookup

**Endpoint:** `/admin/api/members/lookup/`

| Method | Query | Returns |
|--------|-------|---------|
| GET | ?q=searchterm | List of matching members (id, name) |

Used by registration form for passenger lookup.

---

## Native Wagtail Features Used

All configuration uses native Wagtail components:

| Feature | Wagtail Component |
|---------|------------------|
| Site Settings | `BaseSiteSetting` |
| Color Schemes | `@register_snippet` |
| Menus | `wagtailmenus` or custom snippets |
| Forms | `wagtail.contrib.forms` |
| Branding | `WAGTAIL_SITE_NAME`, CSS overrides |
| ViewSets | `ModelViewSet` (Wagtail 5.0+) |
| Reports | `wagtail.contrib.reports` |
| Dashboard | `wagtail.admin.panels` hooks |
| Bulk Actions | `@hooks.register('register_bulk_action')` |

---

## References

- [80-SISTEMA-SOCI.md](80-SISTEMA-SOCI.md) - Member system
- [81-GALLERY-UPLOAD.md](81-GALLERY-UPLOAD.md) - Photo moderation
- [82-EVENTI-ISCRIZIONI.md](82-EVENTI-ISCRIZIONI.md) - Event registrations
- [89-PARTNERS.md](89-PARTNERS.md) - Partner system
- [90-MUTUAL-AID.md](90-MUTUAL-AID.md) - Mutual aid network
- [91-NOTIFICATIONS.md](91-NOTIFICATIONS.md) - Notification system
