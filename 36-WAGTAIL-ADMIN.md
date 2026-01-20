# Wagtail Admin Configuration

## Theme Management Section

Create a dedicated **Theme Configuration** section in Wagtail admin under Settings:

### Site Settings Panel

| Tab | Contents |
|-----|----------|
| General | Site name, tagline, contact email |
| Theme | Theme selection, color configuration |
| Branding | Logo, favicon, social images |
| Social | Social media links |
| Forms | Captcha configuration |

### Theme Settings Fields

| Field | Type | Description |
|-------|------|-------------|
| Theme | Dropdown | velocity, heritage, terra, zen, clubs, tricolore |
| Color Scheme | Snippet Chooser | Select predefined or custom scheme |
| Dark Mode | Checkbox | Enable dark mode toggle (if theme supports) |
| Custom CSS | Text Area | Additional CSS overrides (optional) |

### Color Configuration Fields

| Field | Type | Default |
|-------|------|---------|
| Primary Color | Color Picker | Theme default |
| Secondary Color | Color Picker | Theme default |
| Accent Color | Color Picker | Theme default |
| Surface Color | Color Picker | #FFFFFF |
| Surface Alt Color | Color Picker | #F5F5F5 |
| Text Primary | Color Picker | #111111 |
| Text Muted | Color Picker | #666666 |

## Color Scheme Snippets

Predefined color schemes are managed as Snippets:

### Admin Location
**Snippets → Color Schemes**

### Fields
| Field | Description |
|-------|-------------|
| Name | Scheme identifier (e.g., "Velocity Dark") |
| Primary | Main brand color |
| Secondary | Accent/highlight color |
| Accent | Links and interactive elements |
| Surface | Background color |
| Surface Alt | Card/section backgrounds |
| Text Primary | Main text color |
| Text Muted | Secondary text color |

### Predefined Schemes

Create via admin or fixtures:
- Velocity Default
- Velocity Dark
- Heritage Gold
- Heritage Navy
- Terra Earth
- Terra Dark
- Zen Light
- Clubs Black
- Tricolore Classic

## Form Settings & Captcha

### Captcha Options

Every form on the site should use one of the following captcha options:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **Honeypot + Time** | Hidden field + submission time check | No external service, GDPR-friendly | Less effective against sophisticated bots |
| **hCaptcha** | Privacy-focused challenges | GDPR compliant, earns credits | May require user interaction |
| **Cloudflare Turnstile** | Privacy-focused alternative | GDPR-friendly, good UX | Requires Cloudflare account |

### Form Settings Fields

| Field | Type | Description |
|-------|------|-------------|
| Captcha Method | Dropdown | honeypot, turnstile, hcaptcha |
| Honeypot Field Name | Text | Random name for honeypot (default: "website") |
| Min Submit Time | Number | Minimum seconds before valid submit (default: 3) |
| hCaptcha Site Key | Text | hCaptcha site key |
| hCaptcha Secret Key | Text | hCaptcha secret key |
| Turnstile Site Key | Text | Cloudflare Turnstile site key |
| Turnstile Secret Key | Text | Cloudflare Turnstile secret key |

### Recommended Configuration

For each form type, configure in admin:

| Form Type | Recommended Captcha |
|-----------|---------------------|
| Contact Form | Honeypot + Time OR Turnstile |
| Newsletter Signup | Honeypot + Time |
| Event Registration | Turnstile OR hCaptcha |
| Member Registration | Turnstile OR hCaptcha |
| Comments | Honeypot + Time |

## Admin Branding

Customize admin appearance in **Settings → Admin Branding**:

| Setting | Description |
|---------|-------------|
| Admin Logo | Logo for login page |
| Admin Color | Primary admin interface color |
| Help URL | Link to user documentation |
| Support Email | Contact for site editors |

## Menu Configuration

### Main Menu
Managed via **Settings → Main Menu**:
- Add/remove menu items
- Drag to reorder
- Set link to page or external URL
- Configure dropdown submenus

### Footer Menu
Managed via **Settings → Footer Menu**:
- Column-based organization
- Links to pages or external URLs
- Social media icons

## Dashboard Customization

### Welcome Panel
- Site name and quick stats
- Recent content updates
- Quick action buttons

### Content Statistics
- Total pages by type
- Recent edits
- Pending moderation

## User Permissions

### Editor Groups
| Group | Permissions |
|-------|-------------|
| Editors | Create/edit pages, manage images |
| Moderators | Publish pages, manage comments |
| Designers | Edit theme settings, color schemes |
| Admins | Full access |

## Native Wagtail Features Used

All configuration uses native Wagtail components:

| Feature | Wagtail Component |
|---------|------------------|
| Site Settings | `BaseSiteSetting` |
| Color Schemes | `@register_snippet` |
| Menus | `wagtailmenus` or custom snippets |
| Forms | `wagtail.contrib.forms` |
| Branding | `WAGTAIL_SITE_NAME`, CSS overrides |
