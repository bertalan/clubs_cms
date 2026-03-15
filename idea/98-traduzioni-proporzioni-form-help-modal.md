# Piano: Traduzioni, Proporzioni Form, Help Modal per Account Pages

## Panoramica

Portare le pagine account (profilo, privacy, notifiche, mutuo soccorso) allo
stesso livello qualitativo della pagina di registrazione eventi: help modal
sui campi, classi CSS WCAG, help_text tradotto, proporzioni corrette.

---

## Step 1: Estrarre `_apply_wcag_attrs` in modulo condiviso

**File:** `apps/core/forms_helpers.py` (nuovo)

Spostare da `apps/events/forms.py` le funzioni `_apply_wcag_attrs`,
`_CSS_CLASS_MAP`, `_AUTOCOMPLETE_MAP` in un modulo condiviso. Aggiornare
l'import in `events/forms.py`. Estendere `_AUTOCOMPLETE_MAP` con i campi
members (phone, mobile, birth_date, address, city, postal_code, country).

## Step 2: Aggiungere `help_text` tradotto ai campi ClubUser

**File:** `apps/members/models.py`

Aggiungere `help_text=_("...")` a tutti i campi usati nei form:

- **Profile fields:** phone, mobile, birth_date, birth_place, bio, display_name (gia' presente ma non tradotto), address, city, province, postal_code, country
- **Privacy fields:** show_in_directory, public_profile, show_real_name_to_members, newsletter
- **Notification fields:** email_notifications, push_notifications, news_updates, event_updates, event_reminders, membership_alerts, partner_updates, aid_requests, partner_events, partner_event_comments, digest_frequency
- **Aid fields:** aid_available, aid_radius_km, aid_location_city, aid_coordinates (gia' presente ma non tradotto), aid_notes

Questo genera una migrazione (dati solo, nessuna colonna nuova — `help_text` e' solo metadata).

## Step 3: Chiamare `_apply_wcag_attrs` nei form members

**File:** `apps/members/forms.py`

- Importare `_apply_wcag_attrs` dal nuovo modulo
- Aggiungere `__init__` a `ProfileForm` che chiama `_apply_wcag_attrs(self)`
- Aggiungere `_apply_wcag_attrs(self)` negli `__init__` esistenti di `PrivacySettingsForm`, `NotificationPreferencesForm`, `AidAvailabilityForm`

Questo applica automaticamente `form-input`, `form-select`, `form-textarea`,
`form-check-input` e attributi `aria-*` a tutti i widget.

## Step 4: Creare partial template condiviso `_form_field.html`

**File:** `templates/includes/_form_field.html` (nuovo)

Basato su `events/_form_field.html`, gestisce sia input normali che checkbox:

```html
{% load i18n %}
<div class="form-group{% if field.errors %} form-group--error{% endif %}{% if field.field.widget.input_type == 'checkbox' %} form-check{% endif %}">
    {% if field.field.widget.input_type == "checkbox" %}
        {{ field }}
        <label for="{{ field.id_for_label }}">{{ field.label }}</label>
        {% if field.help_text %}
        <button type="button" class="field-help-btn" aria-label="{% trans 'Help' %}: {{ field.label }}" data-help="{{ field.help_text }}">?</button>
        {% endif %}
    {% else %}
        <div class="form-label-row">
            <label class="form-label" for="{{ field.id_for_label }}">
                {{ field.label }}{% if field.field.required %} <span class="form-required" aria-hidden="true">*</span>{% endif %}
            </label>
            {% if field.help_text %}
            <button type="button" class="field-help-btn" aria-label="{% trans 'Help' %}: {{ field.label }}" data-help="{{ field.help_text }}">?</button>
            {% endif %}
        </div>
        {{ field }}
    {% endif %}
    {% if field.help_text %}
    <p class="form-help-text" id="help_{{ field.html_name }}">{{ field.help_text }}</p>
    {% endif %}
    {% if field.errors %}
    <ul class="form-errors" role="alert">
        {% for error in field.errors %}
        <li>{{ error }}</li>
        {% endfor %}
    </ul>
    {% endif %}
</div>
```

## Step 5: Creare include condiviso `_field_help_modal.html`

**File:** `templates/includes/_field_help_modal.html` (nuovo)

Estrarre modal HTML + JavaScript da `events/register.html` in un include
riusabile (modal `#field-help-modal` + script JS per open/close/escape).

## Step 6: Aggiornare i 4 template account

### `templates/account/profile.html`
- Usare `container--narrow` per larghezza max 720px
- Sostituire il rendering manuale dei campi con `{% include "includes/_form_field.html" with field=field %}`
- Mantenere i due `<fieldset>` (Personal Information + Address)
- Aggiungere `{% include "includes/_field_help_modal.html" %}` in fondo

### `templates/account/privacy.html`
- Usare `container--narrow`
- Sostituire rendering con include partial
- Aggiungere modal include

### `templates/account/notifications.html`
- Usare `container--narrow`
- Sostituire rendering con include partial (3 fieldset mantenuti)
- Aggiungere modal include

### `templates/account/aid.html`
- Usare `container--narrow`
- Sostituire rendering con include partial
- Aggiungere modal include

## Step 7: Compilare traduzioni i18n

```bash
docker exec clubcms-web-1 python manage.py makemessages -l it -l en -l de -l fr -l es --no-location
```

Poi aggiungere le traduzioni italiane per:
- Tutti i nuovi help_text dei campi
- Stringhe "Help", "Close", "Field help" usate nel modal
- Eventuali stringhe mancanti dai template
- Compilare: `docker exec clubcms-web-1 python manage.py compilemessages`

## Step 8: Aggiornare `events/forms.py` per usare il modulo condiviso

**File:** `apps/events/forms.py`

Sostituire le definizioni locali di `_CSS_CLASS_MAP`, `_AUTOCOMPLETE_MAP`,
`_apply_wcag_attrs` con import da `apps/core/forms_helpers.py`.

## Step 9: Test e verifica

- Eseguire test suite: `docker exec clubcms-web-1 python -m pytest -q`
- Verificare end-to-end autenticato (tutte le 7 pagine account)
- Verificare che `makemigrations` non generi migrazioni inattese (help_text non cambia lo schema DB)

---

## File da modificare/creare

| File | Azione |
|------|--------|
| `apps/core/forms_helpers.py` | **Nuovo** — WCAG helpers condivisi |
| `apps/members/models.py` | Aggiungere help_text tradotto a ~30 campi |
| `apps/members/forms.py` | Importare e chiamare _apply_wcag_attrs |
| `apps/events/forms.py` | Importare da core invece di definire localmente |
| `templates/includes/_form_field.html` | **Nuovo** — partial form field |
| `templates/includes/_field_help_modal.html` | **Nuovo** — modal + JS |
| `templates/account/profile.html` | Refactor con include + container--narrow |
| `templates/account/privacy.html` | Refactor con include + container--narrow |
| `templates/account/notifications.html` | Refactor con include + container--narrow |
| `templates/account/aid.html` | Refactor con include + container--narrow |
| `locale/it/LC_MESSAGES/django.po` | Aggiornare traduzioni |

## Verifica

```bash
# Test suite
docker exec clubcms-web-1 python -m pytest -q

# E2E autenticato
docker exec clubcms-web-1 python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clubcms.settings')
django.setup()
from django.test import Client
from apps.members.models import ClubUser
client = Client()
user = ClubUser.objects.get(username='testuser')
client.force_login(user)
for url in ['/it/account/profile/', '/it/account/privacy/', '/it/account/notifications/', '/it/account/aid/']:
    resp = client.get(url)
    assert resp.status_code == 200, f'{url} failed: {resp.status_code}'
    assert 'field-help-btn' in resp.content.decode() or 'form-input' in resp.content.decode()
print('All OK')
"

# Verificare assenza migrazioni pendenti
docker exec clubcms-web-1 python manage.py makemigrations --check --dry-run
```
