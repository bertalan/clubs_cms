# Snippets

## Overview

Snippets are reusable content pieces managed by editors in the Wagtail admin. They are **NOT** pages but can be used across multiple pages.

## When to Use Snippets

| Use Snippets For | Don't Use Snippets For |
|------------------|------------------------|
| Navigation menus | User registrations |
| Footer content | Event attendances |
| Color schemes | Comments/reviews |
| Categories/tags | Transactional data |
| FAQ items | User uploads |
| Partner logos | Session data |
| Testimonials | Logs/analytics |

**Rule**: Snippets = editorial content. Django Models = application data.

See [83-TRANSACTIONAL-MODELS.md](83-TRANSACTIONAL-MODELS.md) for transactional models.

---

## Available Snippets

### Navigation Snippets

| Snippet | Purpose |
|---------|---------|
| Navbar | Main navigation menu |
| FooterMenu | Footer navigation links |

### Content Snippets

| Snippet | Purpose |
|---------|---------|
| Footer | Footer content (text, social links) |
| FAQ | Frequently asked questions |
| Testimonial | Member/customer quotes |
| Partner | Partner/sponsor logos |

### Configuration Snippets

| Snippet | Purpose |
|---------|---------|
| ColorScheme | Theme colors |
| SocialLinks | Social media URLs |
| ContactInfo | Contact details |

### Taxonomy Snippets

| Snippet | Purpose |
|---------|---------|
| NewsCategory | Article categories |
| EventCategory | Event categories |
| Tag | Content tags || PhotoTag | Gallery photo tags |

---

## PhotoTag Snippet

### Purpose
Reusable tags for organizing member-uploaded photos.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| name | Text | Tag name |
| slug | Slug | URL-safe identifier |

### Example Tags

| Tag | Usage |
|-----|-------|
| raduno | Club gatherings |
| gita | Day trips |
| moto-storiche | Vintage bikes |
| premiazioni | Awards |
| sociale | Social events |

### Usage
Used in batch photo uploads to tag multiple photos at once.

See [81-GALLERY-UPLOAD.md](81-GALLERY-UPLOAD.md) for batch upload details.
---

## Navbar Snippet

### Purpose
Main site navigation with menu items.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| Name | Text | Internal identifier |
| Items | Inline | Menu items (orderable) |

### Navbar Item Fields

| Field | Type | Description |
|-------|------|-------------|
| Title | Text | Display text |
| Link Page | Page Chooser | Internal page link |
| Link URL | URL | External URL (if no page) |
| Open New Tab | Boolean | Open in new window |
| Icon | Text | Optional icon class |
| Children | Inline | Submenu items |

### Features

| Feature | Description |
|---------|-------------|
| Drag & Drop | Reorder menu items |
| Nested Menus | Support for dropdowns |
| Translatable | Menu titles per language |
| Multiple Navbars | Different navs for sections |

---

## Footer Snippet

### Purpose
Site footer with contact info and social links.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| Name | Text | Internal identifier |
| Description | RichText | About text |
| Copyright Text | Text | Copyright notice |

### Contact Section

| Field | Type |
|-------|------|
| Phone | Text |
| Email | Email |
| Address | Text |
| Hours | Text |

### Social Links Section

| Field | Type |
|-------|------|
| Facebook | URL |
| Instagram | URL |
| Twitter/X | URL |
| YouTube | URL |
| LinkedIn | URL |

### Footer Menu Section

| Field | Type |
|-------|------|
| Menu Items | Inline (like Navbar) |

---

## ColorScheme Snippet

See [37-COLOR-SCHEME.md](37-COLOR-SCHEME.md) for complete documentation.

### Quick Reference

| Field | Purpose |
|-------|---------|
| Name | Scheme identifier |
| Primary Color | Main brand color |
| Secondary Color | Accent color |
| Background | Page background |
| Surface | Card backgrounds |
| Text Color | Body text |

---

## FAQ Snippet

### Purpose
Reusable FAQ items for accordion display.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| Question | Text | FAQ question |
| Answer | RichText | FAQ answer |
| Category | Dropdown | Optional grouping |
| Order | Number | Display order |

### Usage
Add FAQ block to any page, select FAQ items to display.

---

## Testimonial Snippet

### Purpose
Member quotes and testimonials.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| Quote | Text | Testimonial text |
| Author Name | Text | Person quoted |
| Author Role | Text | Title/role |
| Author Photo | Image | Optional photo |
| Date | Date | When given |
| Featured | Boolean | Show prominently |

---

## Partner Snippet

**Note:** For the complete Partner system with pages and ownership, see [89-PARTNERS.md](89-PARTNERS.md).

### PartnerCategory Snippet

Categorize partners by type.

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
| Technical Sponsor | Products/services |
| Partner | Commercial partners |
| Affiliated Club | Motorcycle clubs network |
| Institutional | Government, associations |
| Media Partner | Press, magazines |

---

## Category Snippets

### NewsCategory

| Field | Type |
|-------|------|
| Name | Text |
| Slug | Auto-generated |
| Description | Text |
| Color | Color picker |

### EventCategory

| Field | Type |
|-------|------|
| Name | Text |
| Slug | Auto-generated |
| Icon | Icon chooser |

---

## Admin Access

### Snippets Menu Location

**Snippets** appears in main admin sidebar with sub-items:
- Navbar
- Footer
- ColorScheme
- FAQ
- etc.

### Permissions

| Permission | Who Can |
|------------|---------|
| View | Editors, Moderators, Admins |
| Add | Moderators, Admins |
| Edit | Moderators, Admins |
| Delete | Admins only |

---

## Snippet in Site Settings

Some snippets are selected in Site Settings:

| Setting | Snippet Type |
|---------|--------------|
| Active Navbar | Navbar |
| Active Footer | Footer |
| Color Scheme | ColorScheme |
| Theme | Theme selection |

Configure in **Settings → Site Settings**.

---

## Using Snippets in Templates

### Via Site Settings

Access snippets assigned in Site Settings:

| Template Access | Purpose |
|-----------------|---------|
| `settings.website.SiteSettings.navbar` | Active navbar |
| `settings.website.SiteSettings.footer` | Active footer |
| `settings.website.SiteSettings.color_scheme` | Active colors |

### Navbar Items Loop

Display menu items:

| Access | Content |
|--------|---------|
| `.items.all` | All menu items |
| `item.title` | Menu item title |
| `item.url` | Link URL |
| `item.children.all` | Submenu items |

### Footer Content

| Access | Content |
|--------|---------|
| `.description` | Footer text |
| `.phone` | Phone number |
| `.email` | Email address |
| `.facebook` | Facebook URL |

---

## Snippet Translation

### Translatable Snippets

| Snippet | Translatable | Fields |
|---------|--------------|--------|
| Navbar | Yes | Item titles |
| Footer | Yes | Description, labels |
| FAQ | Yes | Questions, answers |
| Testimonial | Yes | Quote text |
| Partner | Partial | Description only |
| ColorScheme | No | Colors are universal |
| PhotoTag | Partial | Name only |
| Product | Yes | Name, description |
| PressRelease | Yes | Title, body |
| PartnerCategory | Yes | Name, description |
| AidSkill | Yes | Name, description |
| NotificationTemplate | Yes | Subject, heading, body, CTA text |

See [41-MULTILANG.md](41-MULTILANG.md) for full translation documentation.

### Translation Workflow

Same as pages:
1. Create in default language
2. Use "Translate" action
3. Edit translations
4. Publish

---

## Snippet ViewSet Customization

Admin can customize snippet listing:

| Customization | Options |
|---------------|---------|
| List columns | Choose displayed fields |
| Filters | Filter by status, category |
| Search | Search by name, content |
| Icons | Custom menu icons |
| Ordering | Default sort order |

---

## Native Wagtail Features Used

| Feature | Purpose |
|---------|---------|
| `@register_snippet` | Register as snippet |
| `TranslatableMixin` | Enable translation |
| `ClusterableModel` | Allow inline children |
| `Orderable` | Drag-drop ordering |
| `InlinePanel` | Nested items in admin |
| `SnippetChooserPanel` | Select in page editor |
