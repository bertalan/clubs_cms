---
name: frontend-uiux-a11y
description: "Use when creating or reviewing templates, CSS, component behavior, navigation, and visual updates for ClubCMS. Focuses on UX quality, responsive behavior, accessibility (a11y), and Wagtail template integration."
---

# Frontend, UI/UX, and A11y Skill (ClubCMS)

## Purpose

This skill guides front-end work in ClubCMS to deliver usable, coherent, and accessible interfaces across devices and languages.

## Scope

- Django templates and partials.
- Theme CSS and shared styles.
- StreamField block rendering.
- Forms, navigation, and interactive UI patterns.

## UX Principles

- Prioritize clarity over decoration.
- Keep critical actions visible and predictable.
- Reduce cognitive load: consistent spacing, hierarchy, and wording.
- Preserve visual consistency with the selected project theme.

## Responsive Rules

- Mobile-first behavior for navigation, forms, and cards.
- No horizontal overflow at common breakpoints.
- Touch targets should remain comfortable on mobile.
- Verify key pages on small and large screens.

## Accessibility Baseline (Mandatory)

1. Semantic structure:
- Use proper landmarks (header, nav, main, footer).
- Keep heading order logical and non-skipping.

2. Keyboard accessibility:
- All interactive controls reachable by keyboard.
- Visible focus styles for links, buttons, and form fields.
- No keyboard trap in menus or dialogs.

3. Screen reader support:
- Inputs must have labels.
- Icon-only actions need accessible names.
- Informative alt text for content images.

4. Color and contrast:
- Ensure text contrast is sufficient in each theme.
- Do not rely on color alone to convey state.

5. Forms and errors:
- Clear validation messages near fields.
- Keep error summary discoverable and understandable.

## Wagtail Front-End Specific Guidance

- Reuse existing block templates before adding new variants.
- Keep block markup stable to avoid breaking historical content.
- Ensure translatable UI strings are wrapped for i18n.
- Avoid tightly coupling templates to one language path.

## Performance and Robustness

- Prefer lean CSS and avoid excessive DOM nesting.
- Use responsive images where possible.
- Avoid layout shifts for hero/media sections.

## Front-End Review Checklist

Use this checklist before closing a UI task:

- Visual hierarchy is clear and consistent.
- Works across mobile and desktop.
- Keyboard navigation works end-to-end.
- Focus state is visible on all interactive elements.
- Form labels and error states are accessible.
- No regressions in multilingual templates.
- No obvious contrast issues introduced.

## Definition Of Done

A front-end/UI task is complete when:

- UX goals are met without breaking existing theme behavior.
- A11y baseline checks are satisfied.
- Responsive behavior is verified on representative viewports.
- Any known limitations are explicitly documented.
