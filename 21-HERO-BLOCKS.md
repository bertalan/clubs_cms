# Hero Blocks

## Overview

Hero blocks create impactful full-width headers at the top of pages.

---

## HeroSliderBlock

Rotating carousel of slides with images and text.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Slides | Repeater | Yes | 1-10 slides |
| Autoplay | Boolean | No | Auto-advance slides |
| Interval | Number | No | Seconds between slides (default: 5) |
| Height | Dropdown | No | 50%, 75%, 100% viewport |
| Show Arrows | Boolean | No | Navigation arrows |
| Show Dots | Boolean | No | Slide indicators |

### Slide Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Image | Image Chooser | Yes | Background image |
| Title | Text | Yes | Main heading |
| Subtitle | Text | No | Supporting text |
| Link | URL/Page | No | Click destination |
| Link Text | Text | No | Button text |

### Display Features

| Feature | Description |
|---------|-------------|
| Lazy Loading | Images load on demand |
| Responsive | Optimized crops per breakpoint |
| Touch Swipe | Mobile gesture support |
| Keyboard | Arrow key navigation |
| Pause on Hover | Stops autoplay on mouse over |

### Image Specifications

| Viewport | Recommended Size |
|----------|------------------|
| Desktop | 1920×1080 px |
| Tablet | 1024×768 px |
| Mobile | 768×1024 px |

---

## HeroBannerBlock

Single hero image with text overlay.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Image | Image Chooser | Yes | Background image |
| Title | Text | Yes | Main heading |
| Subtitle | Text | No | Supporting text |
| CTA Text | Text | No | Button label |
| CTA Link | URL/Page | No | Button destination |
| Overlay | Dropdown | No | None, Light, Medium, Dark |
| Text Position | Dropdown | No | Left, Center, Right |
| Height | Dropdown | No | 50%, 75%, 100% viewport |

### Text Overlay Options

| Overlay | Effect |
|---------|--------|
| None | No darkening |
| Light | 30% opacity |
| Medium | 50% opacity |
| Dark | 70% opacity |

### Alignment

| Position | Description |
|----------|-------------|
| Left | Text aligned left with padding |
| Center | Centered text (default) |
| Right | Text aligned right with padding |

---

## HeroCountdownBlock

Countdown timer to an event.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Event | Page Chooser (Event) | Yes | Target event page |
| Background Image | Image Chooser | No | Optional background |
| Title Override | Text | No | Custom title (else event name) |
| Subtitle | Text | No | Supporting text |
| Show Registration | Boolean | No | Display register button |

### Countdown Display

| Element | Source |
|---------|--------|
| Days | Calculated from event start date |
| Hours | Calculated |
| Minutes | Calculated |
| Seconds | Optional (live update) |

### Behavior

| State | Display |
|-------|---------|
| Future Event | Countdown active |
| Event Started | "Happening Now" |
| Event Ended | "Event Completed" or hide block |

---

## HeroVideoBlock

Video background hero section.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Video URL | Embed | Yes | YouTube/Vimeo URL |
| Fallback Image | Image Chooser | Yes | Shown before video loads |
| Title | Text | No | Overlay text |
| Subtitle | Text | No | Supporting text |
| Muted | Boolean | Yes | Always muted (default: true) |
| Loop | Boolean | No | Loop video |

### Video Behavior

| Feature | Description |
|---------|-------------|
| Autoplay | Starts automatically (muted) |
| No Controls | Video controls hidden |
| Fallback | Image shown on mobile/slow connection |
| Lazy Load | Video loads when visible |

---

## Settings (All Hero Blocks)

| Field | Options |
|-------|---------|
| Custom ID | Text (for anchor links) |
| Full Width | Boolean (edge-to-edge) |
| Text Color | Light, Dark |

---

## Best Practices

| Guideline | Reason |
|-----------|--------|
| Use high-quality images | Heroes are prominent |
| Keep text short | Readability on all devices |
| Test on mobile | Different crop may be needed |
| Set focal point | Ensure key content visible |
| Limit slider to 5 slides | User engagement drops |

---

## Accessibility

| Feature | Implementation |
|---------|----------------|
| Alt text | From image title in Wagtail |
| Keyboard nav | Arrow keys for slider |
| Reduced motion | Respects user preference |
| Screen reader | Announces slide changes |
