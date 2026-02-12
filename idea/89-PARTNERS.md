# Partners & Affiliates System

## Overview

Dedicated section for partners, sponsors, affiliated clubs, and collaborators. Each partner has a representative page managed by an assigned owner.

### Multilingual

| Element | Translatable |
|---------|-------------|
| PartnerIndexPage | Yes (title, intro, body) |
| PartnerPage | Yes (all text fields, body) |
| PartnerCategory snippet | Yes (name, description) |
| Contact info | No (universal data) |

See [41-MULTILANG.md](41-MULTILANG.md) for translation workflow.

---

## Page Structure

```
PartnerIndexPage (listing)
└── PartnerPage (individual partner)
```

### URLs

| Page | URL |
|------|-----|
| Partner listing | `/partners/` |
| Category filter | `/partners/?category=sponsor` |
| Individual partner | `/partners/{slug}/` |

---

## PartnerCategory Snippet

### Purpose

Categorize partners by type and relationship level.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| name | Text | Category name |
| slug | Slug | URL identifier |
| description | Text | Category description |
| icon | Image | Optional category icon |
| order | Integer | Display order |

### Example Categories

| Category | Description |
|----------|-------------|
| Main Sponsor | Primary financial supporters |
| Technical Sponsor | Products/services sponsors |
| Partner | Commercial partners |
| Affiliated Club | Motorcycle clubs network |
| Institutional | Government, associations |
| Media Partner | Press, magazines, websites |

### Admin Path

```
Snippets → Partner Categories
```

---

## PartnerIndexPage

### Purpose

Lists all partners organized by category with filtering.

### Content Tab Fields

| Field | Type | Description |
|-------|------|-------------|
| Title | Text | e.g., "Our Partners" |
| Intro | RichText | Section introduction |
| Body | StreamField | Optional content above listing |

### Listing Configuration

| Option | Description |
|--------|-------------|
| Group by Category | Show partners grouped |
| Show Logos | Grid of logos |
| Show Cards | Full info cards |
| Filter by Category | Category tabs/dropdown |

### Display Options

| Style | Description |
|-------|-------------|
| Logo Grid | Logos only, click for detail |
| Card Grid | Logo + name + short description |
| List | Full width cards with more info |

### Featured Partners

| Option | Description |
|--------|-------------|
| Featured Section | Show featured partners at top |
| Carousel | Rotating featured logos |
| Hero | Main sponsor in hero position |

### Settings

| Setting | Value |
|---------|-------|
| Max Count | 1 |
| Subpage Types | PartnerPage only |
| Schema Type | CollectionPage |

---

## PartnerPage

### Purpose

Individual partner/sponsor showcase page.

### Content Tab Fields

| Field | Type | Description |
|-------|------|-------------|
| Name | Text | Partner/company name |
| Slug | Slug | URL identifier |
| Logo | Image | Partner logo |
| Category | PartnerCategory | Type of partner |
| Intro | Text | Short description |
| Body | StreamField | Full partner content |

### Body StreamField Blocks

| Block | Purpose |
|-------|---------|
| RichTextBlock | Company description, history |
| ImageBlock | Photos, products |
| GalleryBlock | Image gallery |
| VideoEmbedBlock | Promo videos |
| QuoteBlock | Testimonial from partner |
| DocumentBlock | Brochures, catalogs |
| MapBlock | Location map |

### Contact Tab

| Field | Type | Description |
|-------|------|-------------|
| Website | URL | Partner website |
| Email | Email | Contact email |
| Phone | Text | Phone number |
| Address | Text | Physical address |
| City | Text | City |
| Country | Choice | Country |

### Social Tab

| Field | Type | Description |
|-------|------|-------------|
| Facebook | URL | Facebook page |
| Instagram | URL | Instagram profile |
| LinkedIn | URL | LinkedIn page |
| YouTube | URL | YouTube channel |
| Twitter/X | URL | Twitter profile |

### Ownership Tab

| Field | Type | Description |
|-------|------|-------------|
| Owner | User Chooser | User who can edit |
| Owner Email | Email | Notification email |
| Last Updated By | User | Auto-filled |
| Last Updated At | DateTime | Auto-filled |

### Display Tab

| Field | Type | Description |
|-------|------|-------------|
| is_featured | Boolean | Show in featured section |
| display_order | Integer | Order within category |
| show_on_homepage | Boolean | Show in homepage partners |
| partnership_start | Date | When partnership began |
| partnership_end | Date | When it ends (optional) |

### Computed Properties

| Property | Logic |
|----------|-------|
| is_active | partnership_end is null OR >= today |
| years_partner | today - partnership_start |

---

## Owner Permissions

### How Ownership Works

Each PartnerPage can have an assigned owner (registered user). The owner can edit their own page without full admin access.

### Permission Matrix

| Action | Owner | Editor | Admin |
|--------|-------|--------|-------|
| View own page | ✅ | ✅ | ✅ |
| Edit own page | ✅ | ✅ | ✅ |
| Edit other pages | ❌ | ✅ | ✅ |
| Create new page | ❌ | ✅ | ✅ |
| Delete page | ❌ | ❌ | ✅ |
| Publish directly | ❌ | ✅ | ✅ |
| Submit for moderation | ✅ | ✅ | ✅ |

### Owner Workflow

| Step | Action |
|------|--------|
| 1 | Owner logs in |
| 2 | Sees "My Partner Page" in dashboard |
| 3 | Edits content |
| 4 | Submits for moderation (or auto-publish if enabled) |
| 5 | Admin approves changes |
| 6 | Page updated |

### Moderation Options

| Setting | Behavior |
|---------|----------|
| Owner requires approval | Changes go to moderation queue |
| Owner can publish | Changes go live immediately |
| Auto-approve after first | First edit moderated, then auto |

### Owner Dashboard Widget

| Element | Description |
|---------|-------------|
| Page Status | Published / Draft / Pending |
| Last Edit | Date of last modification |
| Quick Edit | Button to edit page |
| View Live | Button to view published page |

---

## Homepage Integration

### Partner Logos Block

Display partner logos on homepage.

| Option | Description |
|--------|-------------|
| Filter | By category, featured only |
| Max Items | Limit number shown |
| Style | Grid, carousel, marquee |
| Link | Click goes to partner page |

### Configuration in HomePage

| Field | Type | Description |
|-------|------|-------------|
| show_partners | Boolean | Display partner section |
| partner_title | Text | Section heading |
| partner_categories | M2M | Which categories to show |
| partner_style | Choice | Grid / Carousel / Marquee |

---

## Schema.org

### PartnerPage Schema

| Property | Source |
|----------|--------|
| @type | "Organization" |
| name | Name field |
| logo | Logo image URL |
| url | Website field |
| description | Intro field |
| address | Address fields |
| sameAs | Social URLs array |

### Example Output

```json
{
  "@type": "Organization",
  "name": "Acme Motors",
  "logo": "https://example.com/media/logos/acme.png",
  "url": "https://acme-motors.com",
  "description": "Leading motorcycle parts supplier",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Milan",
    "addressCountry": "IT"
  },
  "sameAs": [
    "https://facebook.com/acmemotors",
    "https://instagram.com/acmemotors"
  ]
}
```

---

## Admin Panel

### Partners Menu

```
Wagtail Admin → Partners
```

### List View Columns

| Column | Field |
|--------|-------|
| Logo | Thumbnail |
| Name | name |
| Category | category |
| Owner | owner.display_name |
| Status | Active/Inactive |
| Featured | is_featured |

### Filters

| Filter | Options |
|--------|---------|
| Category | Dropdown |
| Status | Active / Inactive / All |
| Featured | Yes / No |
| Has Owner | Yes / No |

### Bulk Actions

| Action | Description |
|--------|-------------|
| Set Featured | Mark as featured |
| Remove Featured | Unmark |
| Assign Owner | Assign user to pages |
| Change Category | Move to category |

---

## Notifications

### Owner Notifications

| Event | Notification |
|-------|--------------|
| Page assigned | "You are now the owner of {Partner}" |
| Edit approved | "Your changes to {Partner} are live" |
| Edit rejected | "Your changes need revision" |
| Reminder | "Please update your partner page" |

### Admin Notifications

| Event | Notification |
|-------|--------------|
| Owner submitted edit | "Review: {Partner} edited by {Owner}" |
| Partnership expiring | "{Partner} expires in 30 days" |

---

## Integration

### With Events

| Feature | Description |
|---------|-------------|
| Event Sponsor | Link partner as event sponsor |
| Sponsor Block | Show sponsors on event page |

### With News

| Feature | Description |
|---------|-------------|
| Related Partner | Link news to partner |
| Partner News | Filter news by partner |

### With Members

| Feature | Description |
|---------|-------------|
| Partner Discount | Products from partner sponsors |
| Partner Link | Member works for partner |

---

## Member Verification System

### Purpose

Partners can verify if a customer is an active club member eligible for discounts/benefits, without accessing personal data.

### Access Control

| User Type | Can Verify |
|-----------|------------|
| Public | ❌ No access |
| Registered user | ❌ No access |
| Partner Owner | ✅ Own verification page |
| Admin | ✅ Full access |

### Verification URL

```
/partners/verify-member/
```

Accessible only when logged in as Partner Owner or Admin.

### Two-Factor Verification

To prevent abuse, verification requires TWO matching pieces of information:

| Factor | Description |
|--------|-------------|
| **Primary** | Card number (e.g., "2026-0142") |
| **Secondary** | One of: Display name, City, or Phone (partial) |

### Verification Form

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Card Number | Text | Yes | Full card number |
| Verification Type | Choice | Yes | Display Name / City / Phone |
| Verification Value | Text | Yes | Value to match |

### Verification Type Options

| Type | User Provides | System Matches |
|------|---------------|----------------|
| Display Name | Full display name | Exact match |
| City | City name | Exact match |
| Phone | Last 4 digits | Partial match |

### Response (Success)

| Field | Shown | Example |
|-------|-------|---------|
| Status | ✅ | "Valid member" |
| Display Name | Yes | "Mario R." |
| Valid Until | Yes | "31/12/2026" |
| Member Since | Yes | "2019" |

### Response (Failure)

| Scenario | Message |
|----------|---------|
| Card not found | "Card number not found" |
| Wrong verification | "Verification data does not match" |
| Card expired | "Card expired on {date}" |
| Card suspended | "Card temporarily suspended" |

### Privacy Protection

| Data | Shown to Partner |
|------|------------------|
| Display name | ✅ Yes |
| First/Last name | ❌ Never |
| Email | ❌ Never |
| Phone (full) | ❌ Never |
| Address | ❌ Never |
| Photo | ❌ Never |

### Rate Limiting

| Protection | Value |
|------------|-------|
| Max attempts per hour | 20 |
| Lockout after failures | 5 consecutive |
| Lockout duration | 15 minutes |
| Alert admin | After 10 failed attempts |

### Verification Log

Each verification attempt is logged:

| Field | Description |
|-------|-------------|
| timestamp | When verification occurred |
| partner | Which partner verified |
| card_number | Card checked |
| result | Success / Not found / Wrong data / Expired |
| ip_address | For security audit |

### Partner Dashboard Widget

| Element | Description |
|---------|-------------|
| Verify Member | Quick access button |
| Recent Verifications | Last 10 checks |
| Stats | Success rate, total checks |

### Member Notification (Optional)

| Setting | Behavior |
|---------|----------|
| notify_on_verification | Email member when card verified |
| show_verification_history | Member sees who checked |

### Workflow Example

```
1. Customer shows card: "2026-0142"
2. Partner asks: "What city do you live in?"
3. Customer: "Alessandria"
4. Partner enters: Card=2026-0142, Type=City, Value=Alessandria
5. System: ✅ "Mario R. - Valid until 31/12/2026"
6. Partner applies discount
```

### Alternative: QR Code Scan

| Feature | Description |
|---------|-------------|
| Scan QR | Partner scans member's QR code |
| Auto-fill | Card number auto-populated |
| Still requires | Secondary verification factor |

---

## References

- [42-SNIPPETS.md](42-SNIPPETS.md) - PartnerCategory snippet
- [41-MULTILANG.md](41-MULTILANG.md) - Translation workflow
- [85-MODERATION.md](85-MODERATION.md) - Moderation queue
- [12-CONTENT-PAGES.md](12-CONTENT-PAGES.md) - Page structure patterns
- [80-MEMBERSHIP-SYSTEM.md](80-MEMBERSHIP-SYSTEM.md) - Member system with display_name
