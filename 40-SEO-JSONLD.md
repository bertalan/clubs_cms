# SEO and JSON-LD

## Overview

SEO configuration is managed entirely through the Wagtail admin panel. JSON-LD structured data is generated automatically based on page type and content.

## SEO Settings in Admin

### Site-Level SEO

Configure in **Settings → Site Settings → SEO**:

| Field | Description |
|-------|-------------|
| Site Name | Organization name for schema.org |
| Site Description | Default meta description |
| Site Keywords | Default keywords (comma-separated) |
| Logo | Organization logo for structured data |
| Social Image | Default Open Graph image |
| Phone | Contact phone for schema.org |
| Email | Contact email |
| Address | Physical address for LocalBusiness schema |

### Page-Level SEO

Each page has SEO fields in the "Promote" tab:

| Field | Purpose |
|-------|---------|
| Title Tag | Custom title for search results |
| Meta Description | Description for search results (160 chars) |
| Social Image | Open Graph/Twitter card image |
| Keywords | Page-specific keywords |
| Canonical URL | Prevent duplicate content |
| Robots | noindex, nofollow options |

## JSON-LD Structured Data

Structured data is generated automatically based on page type.

### Schema Types by Page

| Page Type | Schema.org Type | Key Properties |
|-----------|-----------------|----------------|
| HomePage | Organization | name, url, logo, telephone, address |
| ContentPage | WebPage | name, description, url |
| NewsPage | Article | headline, datePublished, author, image |
| EventPage | Event | name, startDate, endDate, location, offers |
| ContactPage | ContactPage | name, telephone, email, address |
| GalleryPage | ImageGallery | name, image (array) |

### Organization Schema (HomePage)

Generated from Site Settings:

| Property | Source |
|----------|--------|
| @type | "Organization" |
| name | Site Settings → Site Name |
| url | Site root URL |
| logo | Site Settings → Logo |
| telephone | Site Settings → Phone |
| email | Site Settings → Email |
| address | Site Settings → Address |
| sameAs | Site Settings → Social Links |

### Article Schema (NewsPage)

Generated from page content:

| Property | Source |
|----------|--------|
| @type | "Article" or "NewsArticle" |
| headline | Page title |
| description | Meta description or intro |
| datePublished | First published date |
| dateModified | Last updated date |
| author | Page author or site name |
| image | Cover image |
| publisher | Organization data |

### Event Schema (EventPage)

Generated from event fields:

| Property | Source |
|----------|--------|
| @type | "Event" |
| name | Event title |
| description | Event description |
| startDate | Event start date (ISO 8601) |
| endDate | Event end date (ISO 8601) |
| location | Venue name + address |
| image | Event image |
| offers | Ticket info (if applicable) |
| organizer | Organization data |

### Nested Schema for Index Pages

Index pages (news listing, events listing, search results) use **ItemList** schema with nested items:

| Page Type | Schema Structure |
|-----------|------------------|
| News Index | ItemList → ListItem → Article |
| Events Index | ItemList → ListItem → Event |
| Gallery Index | ItemList → ListItem → ImageObject |
| Partners Page | ItemList → ListItem → LocalBusiness |
| Search Results | SearchResultsPage → ItemList |

---

## Partners Schema (PartnersPage)

### ItemList for Partners Page

| Property | Source |
|----------|--------|
| @type | "ItemList" |
| name | "Our Partners" |
| numberOfItems | Total partners count |
| itemListElement | Array of LocalBusiness |

### LocalBusiness Schema (per partner)

| Property | Source |
|----------|--------|
| @type | "LocalBusiness" |
| name | Partner name |
| description | Partner description |
| url | Partner website |
| image | Partner logo |
| address | Partner address (if provided) |
| telephone | Partner phone (if provided) |
| makesOffer | Member discount offer |

### Offer Schema (member discount)

| Property | Source |
|----------|--------|
| @type | "Offer" |
| name | Discount description |
| eligibleCustomerType | "Member" |
| priceSpecification | Discount percentage or amount |

---

## Press Office Schema (PressPage)

| Property | Source |
|----------|--------|
| @type | "WebPage" |
| name | Page title |
| description | Meta description |
| mainEntity | Organization schema |
| hasPart | Array of MediaObject (press assets) |

### MediaObject (brand assets)

| Property | Source |
|----------|--------|
| @type | "MediaObject" |
| name | Asset name |
| contentUrl | Download URL |
| encodingFormat | File MIME type |
| description | Asset description |

---

## Mutual Aid Schema (MutualAidPage)

Minimal schema to protect helper privacy:

| Property | Source |
|----------|--------|
| @type | "WebPage" |
| name | Page title |
| description | General description of the network |
| potentialAction | SearchAction for finding helpers |

No individual helper data is exposed in schema.

---

#### ItemList Properties

| Property | Source |
|----------|--------|
| @type | "ItemList" |
| name | Page title (e.g., "Latest News") |
| description | Page meta description |
| numberOfItems | Total items count |
| itemListElement | Array of ListItem |

#### ListItem Properties (per item)

| Property | Source |
|----------|--------|
| @type | "ListItem" |
| position | Item position (1, 2, 3...) |
| url | Link to item page |
| item | Nested schema (Article, Event, etc.) |

### Search Results Schema

Search results pages use **SearchResultsPage** schema:

| Property | Source |
|----------|--------|
| @type | "SearchResultsPage" |
| name | "Search results for: [query]" |
| mainEntity | ItemList with results |
| potentialAction | SearchAction schema |

#### SearchAction Properties

| Property | Value |
|----------|-------|
| @type | "SearchAction" |
| target | Site URL + "?q={search_term}" |
| query-input | "required name=search_term" |

## Open Graph Tags

Generated automatically in page head:

| Tag | Source |
|-----|--------|
| og:title | Title tag or page title |
| og:description | Meta description |
| og:image | Social image or cover image |
| og:url | Canonical URL |
| og:type | article, website, event |
| og:site_name | Site Settings → Site Name |

## Twitter Cards

| Tag | Source |
|-----|--------|
| twitter:card | summary_large_image |
| twitter:title | Title tag |
| twitter:description | Meta description |
| twitter:image | Social image |

## Sitemap

Wagtail generates sitemap automatically at `/sitemap.xml`:

- All published pages included
- Last modified dates
- Change frequency (configurable)
- Priority (configurable per page)

### Sitemap Configuration

In page "Promote" tab:

| Field | Options |
|-------|---------|
| Include in sitemap | Yes/No |
| Change frequency | Always, Hourly, Daily, Weekly, Monthly, Yearly, Never |
| Priority | 0.0 to 1.0 |

## Robots.txt

Configure via **Settings → Site Settings → SEO**:

| Option | Effect |
|--------|--------|
| Allow all | Standard crawling |
| Disallow admin | Block /admin/ paths |
| Disallow media | Block /media/ paths |
| Custom rules | Add custom directives |

### Feed Discovery

Include feed URLs in robots.txt:

| Feed Type | Path | Purpose |
|-----------|------|--------|
| Sitemap | /sitemap.xml | Page index for crawlers |
| Atom | /feed/atom/ | Content syndication |
| RSS | /feed/rss/ | Content syndication |

Feeds are auto-discovered via `<link>` tags in page head:
- `<link rel="alternate" type="application/atom+xml" href="/feed/atom/">`
- `<link rel="alternate" type="application/rss+xml" href="/feed/rss/">`

## Canonical URLs

Automatically generated for:
- Paginated pages
- Filtered/sorted views
- Multilingual pages (hreflang)

Override per page in "Promote" tab if needed.

## Multilingual SEO

For multilingual sites (with wagtail-localize):

| Tag | Purpose |
|-----|---------|
| hreflang | Language alternatives |
| x-default | Default language |
| lang attribute | HTML lang attribute |

## Validation Tools

Test structured data:

| Tool | URL |
|------|-----|
| Schema Validator | https://validator.schema.org/ |
| Schema.org Validator | https://validator.schema.org |
| Facebook Debugger | https://developers.facebook.com/tools/debug |
| Twitter Card Validator | https://cards-dev.twitter.com/validator |

## SEO Checklist

### Per Page
- [ ] Unique title tag (50-60 chars)
- [ ] Meta description (150-160 chars)
- [ ] Social image (1200x630px)
- [ ] Proper heading hierarchy (H1 → H2 → H3)
- [ ] Alt text on all images
- [ ] Internal links

### Site-Wide
- [ ] Organization schema on homepage
- [ ] Sitemap submitted to search engines (via robots.txt)
- [ ] Robots.txt configured
- [ ] SSL certificate active
- [ ] Mobile-friendly design
- [ ] Fast page load (<3s)

## Native Wagtail Features Used

| Feature | Purpose |
|---------|---------|
| `search_description` | Meta description field |
| `seo_title` | Custom title tag |
| `BaseSiteSetting` | Site-level SEO settings |
| `wagtail.contrib.sitemaps` | Automatic sitemap |
| Page `promote_panels` | SEO fields in admin |
