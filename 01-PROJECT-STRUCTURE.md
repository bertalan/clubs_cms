# Project Structure

## Directory Layout

```
clubcms/
├── clubcms/                 # Django project config
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py          # Common settings
│   │   ├── dev.py           # Development
│   │   └── prod.py          # Production
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   ├── core/                # Shared utilities
│   │   ├── seo.py           # JSON-LD mixin
│   │   ├── context_processors.py
│   │   └── wagtail_hooks.py
│   │
│   ├── website/             # Main app
│       ├── models/
│       │   ├── __init__.py
│       │   ├── pages.py     # All Page models
│       │   ├── snippets.py  # Navbar, Footer, ColorScheme
│       │   └── settings.py  # SiteSettings
│       ├── blocks/
│       │   ├── __init__.py
│       │   ├── hero.py      # Hero blocks
│       │   ├── content.py   # Cards, CTA, Stats
│       │   └── media.py     # Gallery, Video
│       └── templatetags/
│           └── website_tags.py
│   │
│   └── federation/          # Event Federation (see 92-EVENT-FEDERATION.md)
│       ├── __init__.py
│       ├── apps.py
│       ├── models.py        # FederatedClub, ExternalEvent, Interest, Comment
│       ├── admin.py
│       ├── wagtail_hooks.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── views.py     # API endpoints
│       │   └── security.py  # Signing/verification
│       ├── sync/
│       │   └── tasks.py     # Sync logic
│       ├── management/
│       │   └── commands/
│       │       └── sync_federation.py
│       ├── urls_api.py
│       ├── urls_frontend.py
│       └── views.py         # Frontend views
│
├── templates/
│   ├── base.html            # Base template
│   ├── website/
│   │   ├── pages/           # Page templates
│   │   └── blocks/          # Block templates
│   └── includes/
│       ├── navbar.html
│       ├── footer.html
│       └── lightbox.html
│
├── templates/federation/        # Federation templates
│   ├── external_events_list.jinja2
│   ├── external_event_detail.jinja2
│   ├── includes/
│   │   ├── event_card.jinja2
│   │   ├── interest_buttons.jinja2
│   │   └── comments_section.jinja2
│   └── emails/
│       ├── new_partner_events.html
│       ├── interest_milestone.html
│       └── new_comment.html
│
├── static/
│   ├── css/
│   │   ├── themes/
│   │   │   ├── modern.css
│   │   │   └── classic.css
│   │   └── components/
│   └── js/
│
└── locale/                  # Translations
```

## Organizational Principles

### Models in Separate Modules
- `pages.py`: HomePage, AboutPage, NewsPage, etc.
- `snippets.py`: reusable elements
- `settings.py`: SiteSettings wagtail

### Blocks in Thematic Modules
- `hero.py`: HeroSliderBlock, HeroCountdownBlock
- `content.py`: CardBlock, CTABlock, StatsBlock
- `media.py`: GalleryBlock, VideoBlock

### Templates Mirror Structure
- Page template: `templates/website/pages/{model_name}.html`
- Block template: `templates/website/blocks/{block_name}.html`

## Key Files

| File | Purpose |
|------|---------|
| `apps/website/models/pages.py` | All page models |
| `apps/website/blocks/__init__.py` | Blocks export |
| `apps/core/seo.py` | JsonLdMixin for schema.org |
| `apps/federation/models.py` | Federation models |
| `apps/federation/api/views.py` | Federation API |
| `templates/base.html` | Master template |

## Naming Conventions

- **Page models**: `{Name}Page` (e.g. `HomePage`, `NewsIndexPage`)
- **Blocks**: `{Name}Block` (e.g. `HeroSliderBlock`)
- **Templates**: snake_case (e.g. `home_page.html`)
- **CSS classes**: kebab-case (e.g. `hero-slider`)
