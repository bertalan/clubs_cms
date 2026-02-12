# CONTRACT: Pages
# Version: 1.0
# Agent: AG-1 (CORE-MODELS)
# Date: 2026-02-11

## Source File
`clubcms/apps/website/models/pages.py`

## Temporary Block Lists
The file defines `TEMP_BODY_BLOCKS`, `TEMP_HOME_BLOCKS`, `TEMP_NEWS_BLOCKS`, `TEMP_EVENT_BLOCKS`.
AG-3 must replace these with real block imports:
```python
from apps.website.blocks import BODY_BLOCKS, HOME_BLOCKS, NEWS_BLOCKS, EVENT_BLOCKS
```

## Tag Through Models
| Class | Through-for | Related Name |
|-------|-------------|--------------|
| `NewsPageTag` | `website.NewsPage` | `tagged_items` |
| `EventPageTag` | `website.EventDetailPage` | `tagged_items` |

---

## 1. HomePage
| Attribute | Value |
|-----------|-------|
| Class | `HomePage` |
| max_count | 1 |
| parent_page_types | `["wagtailcore.Page"]` |
| subpage_types | `[]` |
| template | `website/pages/home_page.html` |

### Key Fields
| Field | Type |
|-------|------|
| hero_title | CharField(255) |
| hero_subtitle | CharField(255) |
| hero_image | FK → wagtailimages.Image |
| primary_cta_text | CharField(120) |
| primary_cta_link | FK → wagtailcore.Page |
| primary_cta_url | URLField |
| secondary_cta_text | CharField(120) |
| secondary_cta_link | FK → wagtailcore.Page |
| secondary_cta_url | URLField |
| body | StreamField (HOME_BLOCKS) |
| featured_event | FK → wagtailcore.Page |

---

## 2. AboutPage
| Attribute | Value |
|-----------|-------|
| Class | `AboutPage` |
| max_count | 1 |
| parent_page_types | (any) |
| subpage_types | `["website.BoardPage"]` |
| template | `website/pages/about_page.html` |

### Key Fields
| Field | Type |
|-------|------|
| intro | RichTextField |
| cover_image | FK → wagtailimages.Image |
| body | StreamField (BODY_BLOCKS) |

---

## 3. BoardPage
| Attribute | Value |
|-----------|-------|
| Class | `BoardPage` |
| max_count | (unlimited) |
| parent_page_types | `["website.AboutPage"]` |
| subpage_types | `[]` |
| template | `website/pages/board_page.html` |

### Key Fields
| Field | Type |
|-------|------|
| intro | RichTextField |
| body | StreamField (BODY_BLOCKS) |

---

## 4. NewsIndexPage
| Attribute | Value |
|-----------|-------|
| Class | `NewsIndexPage` |
| max_count | 1 |
| parent_page_types | (any) |
| subpage_types | `["website.NewsPage"]` |
| template | `website/pages/news_index_page.html` |

### Key Fields
| Field | Type |
|-------|------|
| intro | RichTextField |
| body | StreamField (BODY_BLOCKS) |

### Methods
| Method | Description |
|--------|-------------|
| `get_context()` | Returns paginated (12/page) child NewsPages, filterable by `?category=`, `?tag=` |

---

## 5. NewsPage
| Attribute | Value |
|-----------|-------|
| Class | `NewsPage` |
| max_count | (unlimited) |
| parent_page_types | `["website.NewsIndexPage"]` |
| subpage_types | `[]` |
| template | `website/pages/news_page.html` |

### Key Fields
| Field | Type |
|-------|------|
| cover_image | FK → wagtailimages.Image |
| intro | TextField |
| body | StreamField (NEWS_BLOCKS) |
| display_date | DateField (default: now) |
| author | FK → AUTH_USER_MODEL |
| tags | ClusterTaggableManager (through NewsPageTag) |
| category | FK → website.NewsCategory |

### Properties
| Property | Returns |
|----------|---------|
| `reading_time` | int (minutes, cached) |

### Ordering
`["-display_date"]`

### External Dependencies
- `website.NewsCategory` snippet (defined by AG-2 snippets agent)

---

## 6. EventsPage
| Attribute | Value |
|-----------|-------|
| Class | `EventsPage` |
| max_count | 1 |
| parent_page_types | (any) |
| subpage_types | `["website.EventDetailPage"]` |
| template | `website/pages/events_page.html` |

### Key Fields
| Field | Type |
|-------|------|
| intro | RichTextField |
| body | StreamField (BODY_BLOCKS) |

### Methods
| Method | Description |
|--------|-------------|
| `get_context()` | Returns paginated (12/page) child EventDetailPages. `?show=upcoming` (default) or `?show=past`. Filterable by `?category=`, `?tag=` |

---

## 7. EventDetailPage
| Attribute | Value |
|-----------|-------|
| Class | `EventDetailPage` |
| max_count | (unlimited) |
| parent_page_types | `["website.EventsPage"]` |
| subpage_types | `[]` |
| template | `website/pages/event_detail_page.html` |

### Key Fields
| Field | Type |
|-------|------|
| cover_image | FK → wagtailimages.Image |
| intro | TextField |
| body | StreamField (EVENT_BLOCKS) |
| start_date | DateTimeField |
| end_date | DateTimeField (nullable) |
| location_name | CharField(255) |
| location_address | CharField(500) |
| location_coordinates | CharField(100) |
| registration_open | BooleanField (default False) |
| registration_deadline | DateTimeField (nullable) |
| max_attendees | PositiveIntegerField (default 0 = unlimited) |
| base_fee | DecimalField(8,2) (default 0) |
| early_bird_discount | PositiveIntegerField (default 0, %) |
| early_bird_deadline | DateTimeField (nullable) |
| member_discount_percent | PositiveIntegerField (default 0, %) |
| tags | ClusterTaggableManager (through EventPageTag) |
| category | FK → website.EventCategory |

### TabbedInterface Tabs
1. Content (content_panels)
2. Location (map_panels: location_name, location_address, location_coordinates)
3. Registration (registration_panels: registration settings + pricing)
4. Promote
5. Settings

### Properties
| Property | Returns |
|----------|---------|
| `is_past` | bool |
| `is_registration_open` | bool |
| `confirmed_count` | int (cached) |
| `spots_remaining` | int or None |
| `current_price` | Decimal |

### Methods
| Method | Returns |
|--------|---------|
| `member_price()` | Decimal (price with member discount) |

### Ordering
`["-start_date"]`

### External Dependencies
- `website.EventCategory` snippet (defined by AG-2 snippets agent)
- `self.registrations` reverse FK (defined by events app, gracefully handled)

---

## 8. GalleryPage
| Attribute | Value |
|-----------|-------|
| Class | `GalleryPage` |
| max_count | 1 |
| parent_page_types | (any) |
| subpage_types | `[]` |
| template | `website/pages/gallery_page.html` |

### Key Fields
| Field | Type |
|-------|------|
| intro | RichTextField |
| root_collection | FK → wagtail Collection |
| body | StreamField (BODY_BLOCKS) |

### Methods
| Method | Description |
|--------|-------------|
| `get_context()` | Lists child collections as albums (cover image, count). Supports `?album=<id>` for album detail with pagination (24/page). |

---

## 9. ContactPage
| Attribute | Value |
|-----------|-------|
| Class | `ContactPage` |
| max_count | 1 |
| parent_page_types | (any) |
| subpage_types | `[]` |
| template | `website/pages/contact_page.html` |

### Key Fields
| Field | Type |
|-------|------|
| intro | RichTextField |
| form_title | CharField(255) |
| success_message | RichTextField |
| body | StreamField (BODY_BLOCKS) |
| captcha_enabled | BooleanField (default True) |
| captcha_provider | CharField choices: honeypot, turnstile, hcaptcha |
| captcha_site_key | CharField(255) |
| captcha_secret_key | CharField(255) |

### TabbedInterface Tabs
1. Content
2. Anti-spam (captcha settings)
3. Promote
4. Settings

---

## 10. PrivacyPage
| Attribute | Value |
|-----------|-------|
| Class | `PrivacyPage` |
| max_count | 1 |
| parent_page_types | (any) |
| subpage_types | `[]` |
| template | `website/pages/privacy_page.html` |

### Key Fields
| Field | Type |
|-------|------|
| body | StreamField (BODY_BLOCKS) |
| last_updated | DateField (nullable) |

---

## 11. TransparencyPage
| Attribute | Value |
|-----------|-------|
| Class | `TransparencyPage` |
| max_count | 1 |
| parent_page_types | (any) |
| subpage_types | `[]` |
| template | `website/pages/transparency_page.html` |

### Key Fields
| Field | Type |
|-------|------|
| intro | RichTextField |
| body | StreamField (BODY_BLOCKS) |

---

## 12. PressPage
| Attribute | Value |
|-----------|-------|
| Class | `PressPage` |
| max_count | 1 |
| parent_page_types | (any) |
| subpage_types | `[]` |
| template | `website/pages/press_page.html` |

### Key Fields
| Field | Type |
|-------|------|
| intro | RichTextField |
| press_email | EmailField |
| press_phone | CharField(30) |
| press_contact | CharField(255) |
| body | StreamField (BODY_BLOCKS) |

---

## Integration Notes for Other Agents

### AG-2 (Snippets)
Must create these snippet models referenced by FK:
- `website.NewsCategory` with at least: `name`, `slug`, `description`, `color`
- `website.EventCategory` with at least: `name`, `slug`, `description`

### AG-3 (Blocks)
Must export from `apps.website.blocks`:
- `BODY_BLOCKS` — list of (name, block) tuples
- `HOME_BLOCKS` — extends BODY_BLOCKS with home-specific blocks
- `NEWS_BLOCKS` — extends BODY_BLOCKS with news-specific blocks (gallery)
- `EVENT_BLOCKS` — extends BODY_BLOCKS with event-specific blocks (gallery, map, route)

### Events App
The `EventDetailPage.confirmed_count` property expects a reverse relation `registrations` with a `status` field. This is handled gracefully (returns 0) if that model doesn't exist yet.

### Template Convention
All templates follow: `website/pages/{model_name_snake_case}.html`
