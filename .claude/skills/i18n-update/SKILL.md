---
name: i18n-update
description: Use after adding or changing user-visible strings in ClubCMS templates or Python code. Extracts, translates, compiles and verifies the .po catalogs for it, en, de, fr, es inside Docker, without ad-hoc scripts in /tmp.
---

# i18n update (ClubCMS)

IT is the source language. Catalogs: `clubcms/locale/{it,en,de,fr,es}/LC_MESSAGES/django.po`.
Run everything from `clubcms/` through Docker.

## 1. Extract

```bash
docker compose exec web python manage.py makemessages -l it -l en -l de -l fr -l es --no-wrap
```

## 2. Find what is missing (do not read whole .po files)

```bash
docker compose exec web sh -c 'for l in it en de fr es; do printf "%s: " $l; msgfmt --statistics -o /dev/null locale/$l/LC_MESSAGES/django.po; done'
docker compose exec web msgattrib --untranslated --no-obsolete locale/de/LC_MESSAGES/django.po
docker compose exec web msgattrib --only-fuzzy --no-obsolete locale/de/LC_MESSAGES/django.po
```

## 3. Translate

- Edit only the reported entries with Edit (exact msgid match). Keep placeholders (`%(name)s`, `{0}`) and HTML identical.
- Remove the `#, fuzzy` flag only after checking the translation is correct.
- Do not create new `scripts/translate_*.py` files; they are historical one-offs.

## 4. Compile and verify

```bash
docker compose exec web sh -c 'for l in it en de fr es; do msgfmt --check -o /dev/null locale/$l/LC_MESSAGES/django.po || exit 1; done'
docker compose exec web python manage.py compilemessages
docker compose exec web pytest apps/core/tests/test_i18n_coverage.py apps/core/tests/test_i18n_e2e.py -q
```

Done when: 0 untranslated and 0 fuzzy in all 5 locales, `msgfmt --check` clean, i18n tests green.
