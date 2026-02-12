# PWA - Progressive Web App

## Overview

The site works as a Progressive Web App, allowing users to install it on mobile devices and access it offline.

---

## Web App Manifest

### Configuration

Manifest generated dynamically from Site Settings.

| Field | Source |
|-------|--------|
| name | Site name |
| short_name | Site name (max 12 chars) |
| start_url | "/" |
| display | standalone |
| theme_color | From ColorScheme primary |
| background_color | White (#ffffff) |
| icons | Uploaded in Site Settings |

### Icon Requirements

| Size | Usage |
|------|-------|
| 192x192 | Android home screen |
| 512x512 | Android splash screen |
| 180x180 | iOS (apple-touch-icon) |

### Admin Path

```
Settings → Site Settings → PWA
```

| Setting | Type | Description |
|---------|------|-------------|
| PWA Name | Text | App name (override site name) |
| Short Name | Text | Max 12 characters |
| App Icon 192 | Image | 192x192 PNG |
| App Icon 512 | Image | 512x512 PNG |
| Theme Color | Color | Override primary color |

---

## Service Worker

### Features

| Feature | Description |
|---------|-------------|
| Offline page | Shows when network unavailable |
| Cache static assets | CSS, JS, fonts |
| Cache images | Recently viewed |
| Network first | HTML pages |
| Cache first | Static assets |

### Cached Resources

| Resource | Strategy |
|----------|----------|
| Homepage | Network first, cache fallback |
| CSS/JS | Cache first |
| Fonts | Cache first |
| Images | Cache with limit |
| API calls | Network only |

### Offline Page

| Element | Content |
|---------|---------|
| Logo | Site logo |
| Message | "You're offline" |
| Retry | "Try again" button |
| Cached content | Links to cached pages |

---

## Installation Prompt

### Display Conditions

| Condition | Required |
|-----------|----------|
| HTTPS | Yes |
| Valid manifest | Yes |
| Service worker | Yes |
| User engagement | Some interaction |

### Custom Prompt

| Element | Content |
|---------|---------|
| Banner | "Install our app" |
| Icon | App icon |
| Buttons | Install / Not now |
| Dismissible | Yes, remembers choice |

---

## Mobile Optimization

### Breakpoints

| Size | Device |
|------|--------|
| < 640px | Mobile |
| 640-1024px | Tablet |
| > 1024px | Desktop |

### Touch Targets

| Element | Minimum Size |
|---------|--------------|
| Buttons | 44x44 px |
| Links | 44px height |
| Form inputs | 44px height |

### Performance

| Optimization | Description |
|--------------|-------------|
| Lazy loading | Images below fold |
| Critical CSS | Inline above-fold styles |
| Font display | swap (prevent FOIT) |
| Image formats | WebP with fallback |

---

## Template Integration

### Head Section

| Tag | Purpose |
|-----|---------|
| `<link rel="manifest">` | Point to manifest |
| `<meta name="theme-color">` | Browser chrome color |
| `<meta name="apple-mobile-web-app-capable">` | iOS fullscreen |
| `<link rel="apple-touch-icon">` | iOS icon |

### Body End

| Element | Purpose |
|---------|---------|
| Service worker registration | Install SW |
| Install prompt handler | Custom install UI |

---

## Testing

### Lighthouse Audit

| Category | Target |
|----------|--------|
| PWA | 100 |
| Performance | > 90 |
| Accessibility | > 90 |

### Manual Tests

| Test | Method |
|------|--------|
| Install | Add to home screen |
| Offline | Airplane mode |
| Splash screen | Launch from icon |

---

## References

- [84-PWA-PUSH.md](84-PWA-PUSH.md) - Push notifications
