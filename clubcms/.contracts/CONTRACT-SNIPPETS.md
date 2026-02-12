# CONTRACT: Snippets & SiteSettings
# Version: 1.0
# Agent: AG-2 (SNIPPETS)
# Date: 2026-02-11

## Source Files
- `clubcms/apps/website/models/snippets.py` -- all snippet models
- `clubcms/apps/website/models/settings.py` -- SiteSettings

---

## Snippet Models (all `@register_snippet`)

### 1. ColorScheme
| Field | Type | Default / Notes |
|-------|------|-----------------|
| `name` | CharField(100) | Required |
| `primary` | CharField(7) | `#0F172A` |
| `secondary` | CharField(7) | `#F59E0B` |
| `accent` | CharField(7) | `#8B5CF6` |
| `surface` | CharField(7) | `#F8FAFC` |
| `surface_alt` | CharField(7) | `#FFFFFF` |
| `text_primary` | CharField(7) | `#111111` |
| `text_muted` | CharField(7) | `#666666` |
| `is_dark_mode` | BooleanField | `False` |

**Methods:**
- `get_css_variables()` -> `dict[str, str]` mapping `--color-*` to hex values.

---

### 2. Navbar (ClusterableModel)
| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField(100) | Required |
| `logo` | FK -> Image | nullable, SET_NULL |
| `show_search` | BooleanField | `True` |

**Inline children:** `items` -> NavbarItem (Orderable)

### 3. NavbarItem (Orderable)
| Field | Type | Notes |
|-------|------|-------|
| `navbar` | ParentalKey -> Navbar | related_name="items" |
| `label` | CharField(100) | Required |
| `link_page` | FK -> Page | nullable, SET_NULL |
| `link_url` | URLField | blank |
| `open_new_tab` | BooleanField | `False` |
| `is_cta` | BooleanField | `False` |

---

### 4. Footer (ClusterableModel)
| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField(100) | Required |
| `description` | RichTextField | blank |
| `copyright_text` | CharField(255) | blank |
| `phone` | CharField(30) | blank |
| `email` | EmailField | blank |
| `address` | TextField | blank |

**Inline children:**
- `menu_items` -> FooterMenuItem (Orderable)
- `social_links` -> FooterSocialLink (Orderable)

### 5. FooterMenuItem (Orderable)
| Field | Type | Notes |
|-------|------|-------|
| `footer` | ParentalKey -> Footer | related_name="menu_items" |
| `label` | CharField(100) | Required |
| `link_page` | FK -> Page | nullable, SET_NULL |
| `link_url` | URLField | blank |

### 6. FooterSocialLink (Orderable)
| Field | Type | Notes |
|-------|------|-------|
| `footer` | ParentalKey -> Footer | related_name="social_links" |
| `platform` | CharField(20) | choices: facebook, instagram, twitter, youtube, linkedin, tiktok |
| `url` | URLField | Required |

---

### 7. FAQ
| Field | Type | Notes |
|-------|------|-------|
| `question` | CharField(255) | Required |
| `answer` | RichTextField | Required |
| `category` | CharField(100) | blank |
| `order` | IntegerField | `0` |

**Meta:** `ordering = ["order"]`

---

### 8. Testimonial
| Field | Type | Notes |
|-------|------|-------|
| `quote` | TextField | Required |
| `author_name` | CharField(100) | Required |
| `author_role` | CharField(100) | blank |
| `author_photo` | FK -> Image | nullable, SET_NULL |
| `date` | DateField | nullable |
| `featured` | BooleanField | `False` |

---

### 9. NewsCategory
| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField(100) | Required |
| `slug` | SlugField | unique |
| `description` | TextField | blank |
| `color` | CharField(7) | `#000000` |

**Meta:** `ordering = ["name"]`

**Used by:** `NewsPage.category` (FK)

---

### 10. EventCategory
| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField(100) | Required |
| `slug` | SlugField | unique |
| `icon` | CharField(20) | choices: motorcycle, rally, meeting, social, charity, race |

**Meta:** `ordering = ["name"]`

**Used by:** `EventDetailPage.category` (FK)

---

### 11. PhotoTag
| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField(100) | Required |
| `slug` | SlugField | unique |

**Meta:** `ordering = ["name"]`

---

### 12. PartnerCategory
| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField(100) | Required |
| `slug` | SlugField | unique |
| `description` | TextField | blank |
| `icon` | CharField(50) | blank |
| `order` | IntegerField | `0` |

**Meta:** `ordering = ["order", "name"]`

---

### 13. PressRelease
| Field | Type | Notes |
|-------|------|-------|
| `title` | CharField(255) | Required |
| `date` | DateField | Required |
| `body` | RichTextField | Required |
| `attachment` | FK -> Document | nullable, SET_NULL |
| `is_archived` | BooleanField | `False` |

**Meta:** `ordering = ["-date"]`

---

### 14. BrandAsset
| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField(100) | Required |
| `category` | CharField(20) | choices: logo, font, photo, template |
| `file` | FK -> Document | nullable, SET_NULL |
| `preview` | FK -> Image | nullable, SET_NULL |
| `description` | TextField | blank |
| `order` | IntegerField | `0` |

**Meta:** `ordering = ["order", "name"]`

---

### 15. AidSkill
| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField(100) | Required |
| `slug` | SlugField | unique |
| `description` | TextField | blank |
| `icon` | CharField(50) | blank |
| `category` | CharField(20) | choices: mechanics, transport, logistics, emergency, other |
| `order` | IntegerField | `0` |

**Meta:** `ordering = ["order", "name"]`

---

### 16. Product
| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField(200) | Required |
| `slug` | SlugField | unique |
| `description` | TextField | blank |
| `price` | DecimalField(8,2) | Required |
| `is_active` | BooleanField | `True` |
| `order` | IntegerField | `0` |
| `grants_vote` | BooleanField | `False` |
| `grants_upload` | BooleanField | `False` |
| `grants_events` | BooleanField | `False` |
| `grants_discount` | BooleanField | `False` |
| `discount_percent` | IntegerField | `0` |

**Meta:** `ordering = ["order", "name"]`

---

## SiteSettings (`@register_setting`, `BaseSiteSetting`)

**Template access:** `{{ settings.website.SiteSettings.<field> }}`

### Tabs & Fields

| Tab | Fields |
|-----|--------|
| General | `site_name`, `tagline`, `description` |
| Theme | `theme` (choices: velocity, heritage, terra, zen, clubs, tricolore), `color_scheme` (FK -> ColorScheme) |
| Branding | `logo`, `logo_dark`, `favicon` (all FK -> Image) |
| Contact | `phone`, `email`, `address`, `hours` |
| Social | `facebook_url`, `instagram_url`, `twitter_url`, `youtube_url`, `linkedin_url`, `tiktok_url` |
| Navigation | `navbar` (FK -> Navbar), `footer` (FK -> Footer) |
| PWA | `pwa_name`, `pwa_short_name`, `pwa_description`, `pwa_icon_192`, `pwa_icon_512`, `pwa_theme_color`, `pwa_background_color` |
| Forms | `captcha_provider` (choices: honeypot, turnstile, hcaptcha), `captcha_site_key`, `captcha_secret_key` |
| Map | `map_routing_service` (choices: openstreetmap, google, mapbox), `map_api_key`, `map_default_center`, `map_default_zoom` |

### Methods
- `get_colors()` -> `dict[str, str]` -- delegates to `ColorScheme.get_css_variables()` or returns `{}`.

---

## Integration Notes

### For AG-3 (Blocks Agent)
- Blocks can reference snippets via `SnippetChooserBlock("website.FAQ")`, etc.
- `ColorScheme.get_css_variables()` provides the CSS var dict for style injection.

### For AG-4 (Templates Agent)
- Access site settings in templates: `{{ settings.website.SiteSettings.theme }}`
- Navbar items: `{% for item in settings.website.SiteSettings.navbar.items.all %}`
- Footer items: `{% for item in settings.website.SiteSettings.footer.menu_items.all %}`
- Footer social: `{% for link in settings.website.SiteSettings.footer.social_links.all %}`
- CSS vars: inject via `SiteSettings.get_colors()` in context processor.

### For AG-1 (Pages Agent)
- `NewsPage.category` -> FK to `website.NewsCategory`
- `EventDetailPage.category` -> FK to `website.EventCategory`
- Both already defined in pages.py with string references.

### For AG-6 (Members Agent)
- `Product` snippet defines purchasable tiers with `grants_*` privilege flags.
- Query active products: `Product.objects.filter(is_active=True)`

### For AG-7 (Mutual Aid Agent)
- `AidSkill` snippet provides the skill taxonomy.
- Query by category: `AidSkill.objects.filter(category="mechanics")`

### For AG-8 (Press Agent)
- `PressRelease` snippet holds press releases; `BrandAsset` holds downloadable assets.
- Active releases: `PressRelease.objects.filter(is_archived=False)`
