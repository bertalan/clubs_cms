---
name: theme-css
description: Use when changing CSS, colors, spacing or component styling in ClubCMS. Enforces the 3-level theme architecture (base.css, 6 theme main.css files, ColorScheme variables) and dark mode for every theme.
---

# Theme CSS changes (ClubCMS)

Files (under `clubcms/static/css/`):
- `base.css` — structure: reset, grid, typography, buttons, forms, base component styles.
- `themes/{velocity,heritage,terra,zen,clubs,tricolore}/main.css` — aesthetics per theme.
- `:root` variables injected from the ColorScheme snippet.

## Decide the level first

- Layout, structure or a new component → `base.css`, using only CSS variables.
- Look and feel → all 6 `main.css` files, in the same change.
- Never hard-code colors in templates or in `base.css`. Use `--color-*`, `--font-body`, `--font-heading`.

Required variables: `--color-primary`, `--color-secondary`, `--color-accent`, `--color-surface`, `--color-surface-alt`, `--color-text-primary`, `--color-text-muted`.

## Checklist for each of the 6 themes

1. Light mode style present.
2. `.dark-mode` override present (class on `<html>`).
3. Contrast: text ≥ 7:1 (AAA, project target), large text ≥ 4.5:1, on surface, surface-alt and primary backgrounds.
4. Visible focus state (`:focus-visible`).
5. No horizontal overflow at 360px width.

Find all six files for a selector in one call:

```bash
grep -n "<selector>" clubcms/static/css/base.css clubcms/static/css/themes/*/main.css
```

## Verify

```bash
docker compose exec web pytest apps/website/tests/test_themes.py -q
```

For visual checks, use the `frontend-uiux-a11y` skill and the `design:accessibility-review` skill.
