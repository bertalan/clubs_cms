# Multilingual System

## Overview

The site supports multiple languages using native Wagtail Localize. All content is translatable through the admin interface.

## Supported Languages

| Code | Language | Flag |
|------|----------|------|
| en | English | 🇬🇧 |
| it | Italiano | 🇮🇹 |
| de | Deutsch | 🇩🇪 |
| fr | Français | 🇫🇷 |
| es | Español | 🇪🇸 |

**Site default language:** English (en)

---

## User Authoring Language

### Overview

Each content creator can choose their preferred authoring language. Content is written in the user's chosen language and then translated to all other languages.

### User Preference Setting

| Setting | Location |
|---------|----------|
| Field | User Profile → Preferred Language |
| Options | Any active site language |
| Default | English (site default) |

### How It Works

| Step | Action |
|------|--------|
| 1 | User sets preferred language (e.g., Italian) |
| 2 | User creates content in Italian |
| 3 | Content is submitted for translation |
| 4 | System translates to EN, DE, FR, ES |
| 5 | English version becomes the "canonical" public version |

### Content Creation Flow

| User Language | Creates In | Translates To |
|---------------|------------|---------------|
| Italian | IT | EN, DE, FR, ES |
| English | EN | IT, DE, FR, ES |
| German | DE | EN, IT, FR, ES |
| French | FR | EN, IT, DE, ES |
| Spanish | ES | EN, IT, DE, FR |

### Source Language Indicator

| Element | Description |
|---------|-------------|
| Badge | Shows original language (e.g., "Source: IT") |
| Location | Page editor, content listings |
| Purpose | Identify which version is the source |

---

## Admin Configuration

### Settings → Locales

| Locale | Status |
|--------|--------|
| English | Active (site default) |
| Italian | Active |
| German | Active |
| French | Active |
| Spanish | Active |

### Creating Locales

1. Go to **Settings → Locales**
2. Click "Add a locale"
3. Select language from dropdown
4. Choose sync options
5. Save

---

## Content Translation

### Translation Workflow

| Step | Action | Location |
|------|--------|----------|
| 1 | Create page in user's preferred language | Pages editor |
| 2 | Publish source version | Save & Publish |
| 3 | Click "Translate" or wait for auto-queue | Page actions menu |
| 4 | System translates to all other languages | Translation queue |
| 5 | Review translated content (optional) | Translation editor |
| 6 | Publish translations | Auto or manual |

### Translatable Content Types

| Content Type | Translatable | How |
|--------------|--------------|-----|
| Pages | Yes | Translate action |
| Snippets | Yes | If using TranslatableMixin |
| Images | Metadata only | Title, alt text |
| Documents | Metadata only | Title |
| StreamField | Yes | Per-block translation |

### Translation Status

| Status | Meaning |
|--------|---------|
| ✅ Published | Translation live |
| 📝 Draft | Translation in progress |
| 🔄 Needs update | Source changed |
| ❌ Missing | Not yet translated |

---

## Translation Queue System

### Overview

Content creators can request immediate translation or let the system handle it automatically via a scheduled queue.

### Manual Translation Request

Users with content creation permissions can request immediate translation:

| Limit | Value |
|-------|-------|
| Requests per day | 3 |
| Target languages | All active (EN, DE, FR, ES) |
| Processing | Immediate |
| Reset | Midnight (server time) |

### Action Button

| Element | Description |
|---------|-------------|
| Location | Page/snippet action menu |
| Label | "Translate Now" |
| Counter | Shows remaining requests (e.g., "2/3") |
| Disabled | When limit reached |

### Automatic Queue

Content not manually submitted is translated automatically:

| Setting | Value |
|---------|-------|
| Schedule | Every hour |
| Batch size | Variable (load balancing) |
| Priority | FIFO (first in, first out) |
| Languages | All active locales |

### Queue Priority Rules

| Priority | Content Type |
|----------|--------------|
| High | Pages with `urgent` flag |
| Normal | Standard pages, snippets |
| Low | Archived content |

### Hourly Batch Processing

| Hour | Behavior |
|------|----------|
| 00:00-06:00 | Larger batches (low traffic) |
| 06:00-22:00 | Smaller batches (balanced load) |
| 22:00-00:00 | Medium batches |

### Translation Status Display

| Status | Icon | Meaning |
|--------|------|---------|
| Queued | ⏳ | Waiting for auto-translation |
| Processing | 🔄 | Currently being translated |
| Completed | ✅ | All languages translated |
| Failed | ❌ | Translation error (retry queued) |

### User Notifications

| Event | Notification |
|-------|--------------|
| Manual request sent | Toast confirmation |
| Translation completed | Dashboard notification |
| Daily limit reached | Warning message |
| Auto-translation done | Optional email digest |

---

## Sync Options

### Field Sync Modes

| Mode | Behavior |
|------|----------|
| Synced | Changes in source auto-update translation |
| Overridden | Translation is independent |

### When to Override

| Content | Recommendation |
|---------|----------------|
| Text content | Override (translate) |
| Dates/times | Usually synced |
| Images | Override if text in image |
| Page references | Synced (auto-links to translation) |
| External URLs | Override if locale-specific |

---

## URL Structure

### URL Pattern

| Language | URL Example |
|----------|-------------|
| Italian | `/it/chi-siamo/` |
| English | `/en/about-us/` |
| German | `/de/ueber-uns/` |

### Slug Translation

Each language version can have its own slug:

| Language | Slug |
|----------|------|
| Italian | chi-siamo |
| English | about-us |
| German | ueber-uns |

---

## Language Switcher

### Display Options

| Style | Description |
|-------|-------------|
| Flags | Flag icons only |
| Codes | IT, EN, DE, FR, ES |
| Names | Italiano, English, Deutsch... |
| Flags + Codes | 🇮🇹 IT |

### Switcher Location

| Position | Implementation |
|----------|----------------|
| Navbar | Right side, dropdown or inline |
| Footer | Language list |
| Floating | Fixed position button |

### Behavior

| Scenario | Behavior |
|----------|----------|
| Translation exists | Link to translated page |
| No translation | Link to homepage in that language |
| Same page | Current language highlighted |

---

## Hreflang Tags

Automatically generated in page head:

| Tag | Purpose |
|-----|---------|
| `hreflang="it"` | Italian version |
| `hreflang="en"` | English version |
| `hreflang="x-default"` | Default (Italian) |

### Example Output

```
<link rel="alternate" hreflang="it" href="https://example.com/it/chi-siamo/">
<link rel="alternate" hreflang="en" href="https://example.com/en/about-us/">
<link rel="alternate" hreflang="x-default" href="https://example.com/it/chi-siamo/">
```

---

## Snippets Translation

### Translatable Snippets

| Snippet | Translatable Fields |
|---------|---------------------|
| Navbar | Menu item titles |
| Footer | Description, labels |
| FAQ | Questions, answers |
| Partners | Description (name usually same) |

### Non-Translatable Snippets

| Snippet | Reason |
|---------|--------|
| ColorScheme | Colors are universal |
| SocialLinks | URLs are universal |

---

## Template Strings

### What Gets Translated

| Type | Example |
|------|---------|
| Button labels | "Read More", "Submit" |
| Form labels | "Name", "Email", "Message" |
| Error messages | "This field is required" |
| Navigation labels | "Home", "Contact" |
| Date formats | Locale-specific |

### Translation Files

| Path | Purpose |
|------|---------|
| `locale/it/LC_MESSAGES/django.po` | Italian |
| `locale/en/LC_MESSAGES/django.po` | English |
| `locale/de/LC_MESSAGES/django.po` | German |
| `locale/fr/LC_MESSAGES/django.po` | French |
| `locale/es/LC_MESSAGES/django.po` | Spanish |

---

## Fallback Behavior

| Scenario | Fallback |
|----------|----------|
| Translation missing | Show Italian (default) |
| Partial translation | Show translated + Italian for missing |
| Image not translated | Use Italian image |

### Fallback Configuration

| Setting | Value |
|---------|-------|
| Fallback to default | Yes |
| Show untranslated | Yes (for editors) |

---

## Search

### Per-Language Search

| Feature | Behavior |
|---------|----------|
| Search scope | Current language only |
| Results | Only pages in active locale |
| Index | Separate index per language |

---

## SEO Considerations

| Aspect | Implementation |
|--------|----------------|
| hreflang | Auto-generated |
| Sitemap | Includes all languages |
| Meta tags | Per-language |
| Schema.org | Language-specific |

---

## Admin Interface Language

The admin interface can be in a different language than content:

| Setting | Purpose |
|---------|---------|
| User preference | Each editor chooses |
| Browser detection | Auto-detect |
| Default | Site default language |

---

## Native Wagtail Features Used

| Feature | Purpose |
|---------|---------|
| `wagtail_localize` | Translation management |
| `Locale` model | Language definitions |
| `TranslatableMixin` | Make snippets translatable |
| `get_translations()` | Get page translations |
| `locale` attribute | Current page language |
