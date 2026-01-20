# HomePage

## Overview

The HomePage is the main landing page of the site. Only one instance is allowed.

## Admin Configuration

### Content Tab

| Section | Fields |
|---------|--------|
| Hero | Title, subtitle, background image, CTA buttons |
| Body | StreamField with flexible content blocks |

### Hero Section Fields

| Field | Type | Description |
|-------|------|-------------|
| Hero Title | Text | Main headline (required) |
| Hero Subtitle | Text | Supporting text |
| Hero Image | Image Chooser | Background image |
| Primary CTA Text | Text | Main button label |
| Primary CTA Link | Page/URL Chooser | Main button destination |
| Secondary CTA Text | Text | Secondary button label |
| Secondary CTA Link | Page/URL Chooser | Secondary button destination |

### StreamField Blocks (Body)

The body section supports these blocks:

| Block | Usage |
|-------|-------|
| Hero Slider | Additional hero carousels |
| Stats Section | Key numbers/statistics |
| Featured News | Latest news preview |
| Featured Events | Upcoming events preview |
| Cards Grid | Service/feature cards |
| CTA Section | Call-to-action banners |
| Gallery Preview | Photo gallery snippet |
| Sponsors/Partners | Logo grid |
| Testimonials | Member quotes |

## Featured Content

### Featured Event

| Field | Type | Description |
|-------|------|-------------|
| Featured Event | Page Chooser | Select highlighted event |

The featured event appears prominently on the homepage with:
- Event title and date
- Location
- Registration button (if open)
- Countdown timer (optional)

### Featured News

Configure in StreamField block:
- Number of articles to show (default: 3)
- Category filter (optional)
- Display style (cards, list, featured)

## Display Sections

Typical homepage layout:

| Section | Content Source |
|---------|----------------|
| Hero | Hero fields |
| Stats | Stats block in body |
| About Preview | Rich text block |
| Upcoming Events | Featured Events block |
| Latest News | Featured News block |
| Gallery Preview | Gallery Preview block |
| CTA/Membership | CTA block |
| Partners | Sponsors block |

## Schema.org

HomePage generates **Organization** schema:

| Property | Source |
|----------|--------|
| @type | "Organization" |
| name | Site Settings → Site Name |
| url | Site root URL |
| logo | Site Settings → Logo |
| description | Site Settings → Description |
| telephone | Site Settings → Phone |
| email | Site Settings → Email |
| address | Site Settings → Address |
| sameAs | Site Settings → Social Links |

## Settings

| Setting | Value |
|---------|-------|
| Max Count | 1 |
| Show in Menus | Yes (default) |
| Subpage Types | None |
| Parent Page Types | Root only |

## Template Sections

The template includes these sections:

| Include | Purpose |
|---------|---------|
| Hero section | Main hero with image/slider |
| Stats section | Key numbers |
| Content blocks | StreamField rendering |
| Featured event | Highlighted event card |
| Newsletter signup | Email subscription form |
