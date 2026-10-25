# ClubCMS — Development Guide

## Stack
Django 5.2 + Wagtail 7.x, 8 apps in `clubcms/apps/`: `core`, `website`, `members`, `events`, `federation`, `notifications`, `mutual_aid`, `places`.
Custom user model: `ClubUser`. Task queue: Django-Q2. Dev via Docker, TDD.

## Ripresa del lavoro (obbligatorio)
- Stato e prossimi passi: `idea/tasks/BACKLOG.md` (unica fonte di verità). Leggerlo a inizio sessione.
- Aggiornarlo a fine di ogni attività e prima di una compattazione del contesto (≈85% del limite).
- Report di analisi più recente: `idea/tasks/REPORT-2026-10-25.md`.

## Namespace operative
- `live`: server bare metal raggiunto via SSH (`deploy/clubs.betabi.it/deploy.sh`). Skill: `/deploy-live`.
- `dev` (default): sempre Docker (`docker compose`) dentro il repository.
- Vietato usare venv locale (`clubcms/.venv`) o Python di sistema, salvo richiesta esplicita.
- Ogni azione che può impattare `live`: conferma esplicita prima dell'esecuzione.

## Skill di progetto (`.claude/skills/`)
- `wagtail-project-workflow` — workflow feature/bug, migrazioni, checklist Wagtail.
- `frontend-uiux-a11y` — template, CSS, a11y (WCAG 2.2 AA minimo, AAA su contrasto).
- `theme-css` — modifiche ai 6 temi + dark mode.
- `i18n-update` — estrazione/compilazione/verifica `.po` nei 5 locale.
- `deploy-live` — deploy su `live` (solo su richiesta esplicita).

## i18n
- Lingue: IT (sorgente), EN, DE, FR, ES. Wagtail-localize abilitato.
- Ogni stringa visibile: `{% trans "..." %}` in template, `_("...")` in Python.
- URL pubbliche in `i18n_patterns()`, admin/API fuori.
- Dopo modifica stringhe: skill `i18n-update`.

## 6 Temi CSS — Architettura 3 livelli
1. `static/css/base.css` — shared (reset, grid, typography, buttons, forms)
2. `static/css/themes/{name}/main.css` — theme overrides (velocity, heritage, terra, zen, clubs, tricolore)
3. `:root` CSS variables — dynamic injection da ColorScheme snippet

Modifiche strutturali → `base.css`. Modifiche estetiche → **tutti 6 i temi** + dark mode. Dettagli: skill `theme-css`.

## Sicurezza
- Ogni view con dati personali: `LoginRequiredMixin` + ownership check (`user=request.user`).
- Mai `@csrf_exempt` senza auth alternativa (HMAC, webhook signature). Sempre `{% csrf_token %}` nei form POST.
- File serve: validare path dentro `MEDIA_ROOT`.
- Rate limiting: Django cache **condivisa** (DatabaseCache/Redis) o DB. Mai dict in-memory né `LocMemCache` (non condivisa tra worker gunicorn).
- Secrets solo in `.env`, mai hard-coded.

## Privacy & Visibilità dati
- **Mai esporre**: email, telefono, indirizzo, codice fiscale senza controllo ruolo.
- Nomi utenti: sempre `ClubUser.get_visible_name(viewer=request.user)`.
- Federazione: mai dati personali, solo conteggi aggregati.
- Verifica partner: solo `display_name` + `membership_expiry`.

## Comandi
```bash
docker compose -f clubcms/docker-compose.yml up -d
docker compose -f clubcms/docker-compose.yml exec web python manage.py migrate
docker compose -f clubcms/docker-compose.yml exec web pytest apps/ -q          # tutta la suite
docker compose -f clubcms/docker-compose.yml exec web pytest apps/<app>/ -q    # prima il test più stretto
docker compose -f clubcms/docker-compose.yml exec web ruff check apps/

# CI completa (stessi controlli del pre-push e di GitHub Actions)
bash clubcms/scripts/ci.sh            # oppure: cd clubcms && make ci
git config core.hooksPath .githooks   # una volta per clone: attiva il pre-push

# Demo content (EN primary + IT secondary)
docker compose -f clubcms/docker-compose.yml exec web python manage.py build_demo_db
docker compose -f clubcms/docker-compose.yml exec web python manage.py load_demo --lang en --primary --flush
docker compose -f clubcms/docker-compose.yml exec web python manage.py load_demo --lang it
```

## Uso dei token
- Non leggere: `clubcms/.venv/`, `clubcms.tgz`, `clubcms/scripts.zip`, `clubcms/db_export.json`, `clubcms/scripts/translate_*.py`, `*.po` interi (usare grep/polib mirati).
- `idea/` è la specifica storica: aprire solo il file pertinente partendo da `idea/00-INDEX.md`.
- Test: `-q` e `--tb=short`; `-v` solo sul singolo file che fallisce.

## Stile risposte (ispirato a caveman)
- Prima la risposta, poi il motivo, poi il prossimo passo. Niente preamboli, niente riepiloghi finali ripetuti.
- Frasi brevi e attive. Mai omettere negazioni (non, mai, solo, tranne) né numeri.
- Codice, comandi, path ed errori sempre esatti; mostrare solo le righe cambiate.
- Durante i tool: solo brevi righe di stato a inizio, cambio fase e fine.
- Prosa completa (non compressa) per: avvisi di sicurezza, azioni irreversibili o su `live`, passi in sequenza, domande all'utente, e tutto ciò che resta nel repo (codice, commit, doc).

## Pre-commit checklist
- Stringhe utente in `{% trans %}` / `_()`
- CSS: `base.css` (strutturali) o tutti 6 temi (estetiche)
- View protette + ownership check
- `{% csrf_token %}` nei form
- Nessun dato personale esposto senza controllo ruolo
- `bash clubcms/scripts/ci.sh` verde (lo esegue anche il pre-push)
- Nessun secret hard-coded
- `idea/tasks/BACKLOG.md` aggiornato
