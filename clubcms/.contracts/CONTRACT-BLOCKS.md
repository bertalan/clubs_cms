# CONTRACT: Blocks
# Version: 1.0
# Agent: AG-3 (BLOCKS)
# Date: 2026-02-11

## Source Directory
`clubcms/apps/website/blocks/`

## Module Structure
| File | Classes |
|------|---------|
| `hero.py` | HeroSlideBlock, HeroSliderBlock, HeroBannerBlock, HeroCountdownBlock, HeroVideoBlock |
| `content.py` | CardBlock, CardsGridBlock, CTABlock, StatItemBlock, StatsBlock, QuoteBlock, TimelineItemBlock, TimelineBlock, TeamMemberBlock, TeamGridBlock, NewsletterSignupBlock, AlertBlock |
| `media.py` | GalleryImageBlock, GalleryBlock, VideoEmbedBlock, ImageBlock, DocumentBlock, DocumentListBlock, MapBlock |
| `layout.py` | AccordionItemBlock, AccordionBlock, TabItemBlock, TabsBlock, TwoColumnBlock, SectionBlock, DividerBlock, SpacerBlock |
| `route.py` | WaypointBlock, RouteBlock |
| `__init__.py` | All imports + block list definitions |

---

## Block Lists (exported from `__init__.py`)

### HERO_BLOCKS
| Name | Block Class |
|------|-------------|
| `hero_slider` | HeroSliderBlock |
| `hero_banner` | HeroBannerBlock |
| `hero_countdown` | HeroCountdownBlock |
| `hero_video` | HeroVideoBlock |

### CONTENT_BLOCKS
| Name | Block Class |
|------|-------------|
| `rich_text` | RichTextBlock (from wagtail.blocks) |
| `cards_grid` | CardsGridBlock |
| `cta` | CTABlock |
| `stats` | StatsBlock |
| `quote` | QuoteBlock |
| `timeline` | TimelineBlock |
| `team_grid` | TeamGridBlock |
| `newsletter_signup` | NewsletterSignupBlock |
| `alert` | AlertBlock |

### MEDIA_BLOCKS
| Name | Block Class |
|------|-------------|
| `image` | ImageBlock |
| `gallery` | GalleryBlock |
| `video_embed` | VideoEmbedBlock |
| `document` | DocumentBlock |
| `document_list` | DocumentListBlock |
| `map` | MapBlock |

### LAYOUT_BLOCKS
| Name | Block Class |
|------|-------------|
| `accordion` | AccordionBlock |
| `tabs` | TabsBlock |
| `two_columns` | TwoColumnBlock |
| `section` | SectionBlock |
| `divider` | DividerBlock |
| `spacer` | SpacerBlock |

### ROUTE_BLOCKS
| Name | Block Class |
|------|-------------|
| `route` | RouteBlock |

### Combined Lists
| List | Composition | Used By |
|------|------------|---------|
| `BODY_BLOCKS` | CONTENT_BLOCKS + MEDIA_BLOCKS + LAYOUT_BLOCKS | AboutPage, BoardPage, NewsIndexPage, EventsPage, GalleryPage, ContactPage, PrivacyPage, TransparencyPage, PressPage |
| `HOME_BLOCKS` | HERO_BLOCKS + BODY_BLOCKS | HomePage |
| `NEWS_BLOCKS` | BODY_BLOCKS + news_gallery (GalleryBlock) | NewsPage |
| `EVENT_BLOCKS` | BODY_BLOCKS + ROUTE_BLOCKS + event_gallery (GalleryBlock) + event_map (MapBlock) | EventDetailPage |

---

## Hero Blocks

### HeroSliderBlock
| Field | Type | Default | Required |
|-------|------|---------|----------|
| slides | ListBlock(HeroSlideBlock) | — | Yes (min 1) |
| autoplay | BooleanBlock | True | No |
| interval | IntegerBlock | 5000 | Yes |
| height | ChoiceBlock | 75vh | Yes |
| show_arrows | BooleanBlock | True | No |
| show_dots | BooleanBlock | True | No |

**Template:** `website/blocks/hero_slider_block.html`
**Icon:** image

#### HeroSlideBlock (inner)
| Field | Type | Required |
|-------|------|----------|
| image | ImageChooserBlock | Yes |
| title | CharBlock(255) | No |
| subtitle | CharBlock(255) | No |
| cta_text | CharBlock(120) | No |
| cta_link | PageChooserBlock | No |
| cta_url | URLBlock | No |

### HeroBannerBlock
| Field | Type | Default | Required |
|-------|------|---------|----------|
| image | ImageChooserBlock | — | Yes |
| title | CharBlock(255) | — | No |
| subtitle | TextBlock | — | No |
| cta_text | CharBlock(120) | — | No |
| cta_link | PageChooserBlock | — | No |
| cta_url | URLBlock | — | No |
| overlay | ChoiceBlock | dark | Yes |
| text_position | ChoiceBlock | center | Yes |
| height | ChoiceBlock | 75vh | Yes |

**Template:** `website/blocks/hero_banner_block.html`
**Icon:** image

### HeroCountdownBlock
| Field | Type | Default | Required |
|-------|------|---------|----------|
| event | PageChooserBlock(EventDetailPage) | — | Yes |
| background_image | ImageChooserBlock | — | No |
| title_override | CharBlock(255) | — | No |
| show_registration_button | BooleanBlock | True | No |

**Template:** `website/blocks/hero_countdown_block.html`
**Icon:** date

### HeroVideoBlock
| Field | Type | Default | Required |
|-------|------|---------|----------|
| video_url | URLBlock | — | Yes |
| fallback_image | ImageChooserBlock | — | Yes |
| title | CharBlock(255) | — | No |
| subtitle | TextBlock | — | No |
| cta_text | CharBlock(120) | — | No |
| cta_link | PageChooserBlock | — | No |
| cta_url | URLBlock | — | No |
| muted | BooleanBlock | True | No |
| loop | BooleanBlock | True | No |

**Template:** `website/blocks/hero_video_block.html`
**Icon:** media

---

## Content Blocks

### CardBlock
| Field | Type | Required |
|-------|------|----------|
| image | ImageChooserBlock | No |
| title | CharBlock(255) | Yes |
| text | TextBlock | No |
| link_page | PageChooserBlock | No |
| link_url | URLBlock | No |
| link_text | CharBlock(120) | No |

**Template:** `website/blocks/card_block.html`
**Icon:** doc-full

### CardsGridBlock
| Field | Type | Default | Required |
|-------|------|---------|----------|
| title | CharBlock(255) | — | No |
| cards | ListBlock(CardBlock) | — | Yes (min 1) |
| columns | ChoiceBlock | 3 | Yes |
| style | ChoiceBlock | default | Yes |

**Template:** `website/blocks/cards_grid_block.html`
**Icon:** grid

### CTABlock
| Field | Type | Default | Required |
|-------|------|---------|----------|
| title | CharBlock(255) | — | Yes |
| text | RichTextBlock | — | No |
| button_text | CharBlock(120) | — | Yes |
| button_link | PageChooserBlock | — | No |
| button_url | URLBlock | — | No |
| background_style | ChoiceBlock | primary | Yes |
| background_image | ImageChooserBlock | — | No |

**Template:** `website/blocks/cta_block.html`
**Icon:** pick

### StatsBlock
| Field | Type | Default | Required |
|-------|------|---------|----------|
| title | CharBlock(255) | — | No |
| stats | ListBlock(StatItemBlock) | — | Yes (min 1) |
| background_style | ChoiceBlock | default | Yes |

**Template:** `website/blocks/stats_block.html`
**Icon:** order

#### StatItemBlock (inner)
| Field | Type | Required |
|-------|------|----------|
| value | CharBlock(50) | Yes |
| label | CharBlock(100) | Yes |
| icon | CharBlock(50) | No |

### QuoteBlock
| Field | Type | Required |
|-------|------|----------|
| quote | TextBlock | Yes |
| author | CharBlock(255) | No |
| role | CharBlock(255) | No |
| image | ImageChooserBlock | No |

**Template:** `website/blocks/quote_block.html`
**Icon:** openquote

### TimelineBlock
| Field | Type | Required |
|-------|------|----------|
| title | CharBlock(255) | No |
| items | ListBlock(TimelineItemBlock) | Yes (min 1) |

**Template:** `website/blocks/timeline_block.html`
**Icon:** date

#### TimelineItemBlock (inner)
| Field | Type | Required |
|-------|------|----------|
| year | CharBlock(20) | Yes |
| title | CharBlock(255) | Yes |
| description | RichTextBlock | No |

### TeamMemberBlock
| Field | Type | Required |
|-------|------|----------|
| name | CharBlock(255) | Yes |
| role | CharBlock(255) | No |
| photo | ImageChooserBlock | No |
| bio | RichTextBlock | No |
| email | EmailBlock | No |
| phone | CharBlock(30) | No |

**Template:** `website/blocks/team_member_block.html`
**Icon:** user

### TeamGridBlock
| Field | Type | Default | Required |
|-------|------|---------|----------|
| title | CharBlock(255) | — | No |
| members | ListBlock(TeamMemberBlock) | — | Yes (min 1) |
| columns | ChoiceBlock | 3 | Yes |

**Template:** `website/blocks/team_grid_block.html`
**Icon:** group

### NewsletterSignupBlock
| Field | Type | Default | Required |
|-------|------|---------|----------|
| heading | CharBlock(255) | "Stay updated" | Yes |
| description | TextBlock | — | No |
| button_text | CharBlock(120) | "Subscribe" | Yes |
| background | ChoiceBlock | primary | Yes |

**Template:** `website/blocks/newsletter_signup_block.html`
**Icon:** mail

### AlertBlock
| Field | Type | Default | Required |
|-------|------|---------|----------|
| message | RichTextBlock | — | Yes |
| alert_type | ChoiceBlock | info | Yes |
| dismissible | BooleanBlock | True | No |

**Template:** `website/blocks/alert_block.html`
**Icon:** warning

---

## Media Blocks

### GalleryImageBlock (inner block)
| Field | Type | Required |
|-------|------|----------|
| image | ImageChooserBlock | Yes |
| caption | CharBlock(255) | No |

### GalleryBlock
| Field | Type | Default | Required |
|-------|------|---------|----------|
| title | CharBlock(255) | — | No |
| images | ListBlock(GalleryImageBlock) | — | Yes (min 1) |
| columns | ChoiceBlock | 3 | Yes |
| lightbox | BooleanBlock | True | No |
| aspect_ratio | ChoiceBlock | auto | Yes |

**Template:** `website/blocks/gallery_block.html`
**Icon:** image

### VideoEmbedBlock
| Field | Type | Default | Required |
|-------|------|---------|----------|
| video | EmbedBlock | — | Yes |
| caption | CharBlock(255) | — | No |
| autoplay | BooleanBlock | False | No |

**Template:** `website/blocks/video_embed_block.html`
**Icon:** media

### ImageBlock
| Field | Type | Default | Required |
|-------|------|---------|----------|
| image | ImageChooserBlock | — | Yes |
| caption | CharBlock(255) | — | No |
| alignment | ChoiceBlock | full | Yes |

**Template:** `website/blocks/image_block.html`
**Icon:** image

### DocumentBlock
| Field | Type | Required |
|-------|------|----------|
| document | DocumentChooserBlock | Yes |
| description | TextBlock | No |

**Template:** `website/blocks/document_block.html`
**Icon:** doc-full

### DocumentListBlock
| Field | Type | Required |
|-------|------|----------|
| title | CharBlock(255) | No |
| documents | ListBlock(DocumentBlock) | Yes (min 1) |

**Template:** `website/blocks/document_list_block.html`
**Icon:** doc-full

### MapBlock
| Field | Type | Default | Required |
|-------|------|---------|----------|
| address | CharBlock(500) | — | No |
| coordinates | CharBlock(100) | — | Yes |
| zoom | IntegerBlock | 14 | Yes |
| height | IntegerBlock | 400 | Yes |
| title | CharBlock(255) | — | No |

**Template:** `website/blocks/map_block.html`
**Icon:** site

---

## Layout Blocks

### AccordionBlock
| Field | Type | Required |
|-------|------|----------|
| title | CharBlock(255) | No |
| items | ListBlock(AccordionItemBlock) | Yes (min 1) |

**Template:** `website/blocks/accordion_block.html`
**Icon:** list-ul

#### AccordionItemBlock (inner)
| Field | Type | Required |
|-------|------|----------|
| title | CharBlock(255) | Yes |
| content | RichTextBlock | Yes |

### TabsBlock
| Field | Type | Required |
|-------|------|----------|
| tabs | ListBlock(TabItemBlock) | Yes (min 2) |

**Template:** `website/blocks/tabs_block.html`
**Icon:** form

#### TabItemBlock (inner)
| Field | Type | Required |
|-------|------|----------|
| title | CharBlock(255) | Yes |
| content | RichTextBlock | Yes |

### TwoColumnBlock
| Field | Type | Default | Required |
|-------|------|---------|----------|
| left_column | RichTextBlock | — | Yes |
| right_column | RichTextBlock | — | Yes |
| split | ChoiceBlock | 50-50 | Yes |

**Template:** `website/blocks/two_column_block.html`
**Icon:** placeholder

### SectionBlock
| Field | Type | Default | Required |
|-------|------|---------|----------|
| title | CharBlock(255) | — | No |
| content | RichTextBlock | — | Yes |
| background | ChoiceBlock | default | Yes |
| background_image | ImageChooserBlock | — | No |
| padding | ChoiceBlock | md | Yes |

**Template:** `website/blocks/section_block.html`
**Icon:** placeholder

### DividerBlock
| Field | Type | Default | Required |
|-------|------|---------|----------|
| style | ChoiceBlock | line | Yes |

**Template:** `website/blocks/divider_block.html`
**Icon:** horizontalrule

### SpacerBlock
| Field | Type | Default | Required |
|-------|------|---------|----------|
| size | ChoiceBlock | md | Yes |

**Template:** `website/blocks/spacer_block.html`
**Icon:** arrows-up-down

---

## Route Blocks

### WaypointBlock (inner block)
| Field | Type | Default | Required |
|-------|------|---------|----------|
| name | CharBlock(255) | — | Yes |
| address | CharBlock(500) | — | No |
| coordinates | CharBlock(100) | — | Yes |
| icon_type | ChoiceBlock | waypoint | Yes |
| notes | TextBlock | — | No |

### RouteBlock
| Field | Type | Default | Required |
|-------|------|---------|----------|
| title | CharBlock(255) | — | Yes |
| description | TextBlock | — | No |
| waypoints | ListBlock(WaypointBlock) | — | Yes (min 2) |
| route_type | ChoiceBlock | touring | Yes |
| distance | CharBlock(50) | — | No |
| elevation | CharBlock(50) | — | No |
| estimated_duration | CharBlock(50) | — | No |
| difficulty | ChoiceBlock | moderate | Yes |
| map_height | IntegerBlock | 500 | Yes |

**Template:** `website/blocks/route_block.html`
**Icon:** site

---

## Integration Notes for Other Agents

### AG-1 (Pages)
Replace temporary block imports in `apps/website/models/pages.py`:
```python
# Remove TEMP_*_BLOCKS and their imports
# Replace with:
from apps.website.blocks import BODY_BLOCKS, HOME_BLOCKS, NEWS_BLOCKS, EVENT_BLOCKS
```

### AG-4 (Templates)
Must create these block templates:
- `website/blocks/hero_slider_block.html`
- `website/blocks/hero_banner_block.html`
- `website/blocks/hero_countdown_block.html`
- `website/blocks/hero_video_block.html`
- `website/blocks/card_block.html`
- `website/blocks/cards_grid_block.html`
- `website/blocks/cta_block.html`
- `website/blocks/stats_block.html`
- `website/blocks/quote_block.html`
- `website/blocks/timeline_block.html`
- `website/blocks/team_member_block.html`
- `website/blocks/team_grid_block.html`
- `website/blocks/newsletter_signup_block.html`
- `website/blocks/alert_block.html`
- `website/blocks/gallery_block.html`
- `website/blocks/video_embed_block.html`
- `website/blocks/image_block.html`
- `website/blocks/document_block.html`
- `website/blocks/document_list_block.html`
- `website/blocks/map_block.html`
- `website/blocks/accordion_block.html`
- `website/blocks/tabs_block.html`
- `website/blocks/two_column_block.html`
- `website/blocks/section_block.html`
- `website/blocks/divider_block.html`
- `website/blocks/spacer_block.html`
- `website/blocks/route_block.html`

### CSS Class Convention
Apply `block-{block-name}` (kebab-case) as the root CSS class:
- `block-hero-slider`, `block-hero-banner`, `block-hero-countdown`, `block-hero-video`
- `block-card`, `block-cards-grid`, `block-cta`, `block-stats`, `block-quote`
- `block-timeline`, `block-team-member`, `block-team-grid`
- `block-newsletter-signup`, `block-alert`
- `block-gallery`, `block-video-embed`, `block-image`, `block-document`
- `block-document-list`, `block-map`
- `block-accordion`, `block-tabs`, `block-two-columns`, `block-section`
- `block-divider`, `block-spacer`
- `block-route`
