---
name: wagtail-project-workflow
description: "Use when working on ClubCMS features, bugs, refactors, or releases in Django 5 + Wagtail 7. Covers project conventions, safe workflow, migrations, i18n, tests, Docker deploy, and acceptance checks for this repository."
---

# Wagtail Project Workflow (ClubCMS)

## Purpose

This skill defines how the agent should plan, implement, and validate changes in this Wagtail-based project.

## Tech Context

- Stack: Django 5.x, Wagtail 7.x, PostgreSQL, docker compose.
- App root: clubcms.
- Main app modules: apps/core, apps/website, apps/members, apps/events, apps/federation, apps/notifications, apps/mutual_aid.
- Settings modules: clubcms.settings.dev and clubcms.settings.prod.

## Execution Namespaces

- `live`: bare-metal Meta server is reached via host alias in `~/.ssh/config`.
- Default development target: Docker only (`docker compose` in this repository) whenever the user does not specify a target.
- Never assume local virtualenv or system-wide Python/pip execution unless explicitly requested by the user.
- For any command with potential production impact, request explicit confirmation before execution.

## Mandatory Workflow

1. Read context before editing:
- Scan relevant models, forms, views, urls, templates, tests, and settings.
- Prefer minimal, targeted edits.

2. Keep architecture consistent:
- Reuse existing app boundaries and naming patterns.
- Do not move logic across apps unless explicitly requested.

3. Data changes:
- If models change, create migrations and verify they apply cleanly.
- Never hand-edit old migrations unless requested for a repair.

4. Internationalization:
- Keep user-facing text translatable.
- Preserve multilingual routing and language-aware URLs.

5. Security defaults:
- Preserve secure-by-default behavior for production settings.
- Avoid introducing permissive auth, CSRF bypasses, or open redirects.

6. Testing and verification:
- Run the narrowest meaningful tests first, then broader tests when needed.
- Report what was tested and what was not tested.

## Project-Specific Commands

Run from the clubcms directory unless specified otherwise.

- Development stack:
  - docker compose up -d
  - docker compose exec web python manage.py migrate
- Tests:
  - docker compose exec web pytest apps/ -v
- i18n:
  - docker compose exec web python manage.py makemessages -l it -l en -l de -l fr -l es --no-wrap
  - docker compose exec web python manage.py compilemessages
- Production stack:
  - docker compose -f docker-compose.prod.yml up -d
  - docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

## Coding Standards For This Repo

- Preserve existing coding style and import ordering.
- Keep comments short and only where logic is not obvious.
- Do not reformat unrelated files.
- Favor explicit, readable code over compact one-liners in business logic.

## Wagtail/Django Change Checklist

Use this checklist when applicable:

- Models updated and migrations created.
- Admin editing UX checked (panels, snippets, chooser behavior).
- Page models and StreamField blocks remain backward compatible.
- URLs and reverse names still valid.
- Templates render in all supported languages where impacted.
- Permissions and member-only flows still enforced.
- Health endpoint behavior unchanged unless intentionally modified.

## Deployment Safety Checklist

For production-facing changes:

- Works with clubcms.settings.prod.
- Does not break gunicorn startup path.
- Static and media assumptions remain compatible with Docker volumes.
- Any new env vars are documented in .env example files.

## Definition Of Done

A task is complete when:

- Code is implemented with minimal surface area.
- Relevant tests pass or test gaps are explicitly declared.
- Migration, i18n, and deploy impacts are addressed.
- Final summary includes changed files and operational notes.
