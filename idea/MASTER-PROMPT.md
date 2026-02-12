# ClubCMS — Master Development Prompt

> Prompt operativo da seguire per ogni sessione di sviluppo.
> Generato dopo audit completo del codice, delle 47 specifiche, e dei 6 temi.

---

## 1. MULTILINGUA (i18n / l10n)

### Stato attuale
- **Lingue**: IT (sorgente), EN, DE, FR, ES
- **Infrastruttura OK**: `wagtail-localize>=1.9`, `LocaleMiddleware`, `WAGTAIL_I18N_ENABLED=True`, 5 file `.po` popolati (IT: 67 msg, EN/DE/FR/ES: 53 msg ciascuno)
- **ColorScheme, Navbar, Footer**: snippet Wagtail translatable-ready

### Gap critici

| ID | Gap | Gravita | File |
|----|-----|---------|------|
| I18N-1 | URL non wrappate in `i18n_patterns()` — nessun prefisso `/it/`, `/en/`, etc. | **CRITICO** | `clubcms/urls.py` |
| I18N-2 | Nessun Language Switcher nella navbar o nel footer | **CRITICO** | `templates/includes/navbar.html`, `footer.html` |
| I18N-3 | File `.mo` non compilati per EN, DE, FR, ES (solo IT ha `.mo`) | **ALTO** | `locale/*/LC_MESSAGES/` |
| I18N-4 | `base.html` non carica `{% load i18n %}` e non usa tag wagtail_localize | **MEDIO** | `templates/base.html` |
| I18N-5 | Alcuni template (events, mutual_aid) non usano `{% trans %}` per stringhe statiche | **MEDIO** | Template vari |

### Regole da seguire

1. **Ogni stringa visibile all'utente** deve usare `{% trans "..." %}` o `_("...")` in Python
2. **URL pubbliche** devono essere wrappate in `i18n_patterns()` — le URL admin/API restano fuori
3. **Language switcher** deve apparire nella navbar (desktop) e nel menu mobile
4. **Dopo aggiunta/modifica di stringhe traducibili**: eseguire `makemessages -l it -l en -l de -l fr -l es` e poi `compilemessages`
5. **Wagtail pages**: usare `TranslatableMixin` dove necessario (gia previsto da wagtail-localize)
6. **hreflang tags**: gia implementati in `includes/seo_head.html` — verificare che funzionino con i18n_patterns

---

## 2. SISTEMA TEMI (6 Temi)

### Temi disponibili

| Tema | Linee CSS | Font | Filosofia |
|------|-----------|------|-----------|
| **Velocity** (default) | 1.877 | Inter + Open Sans | Moderno, dinamico, pill buttons |
| **Heritage** | 1.781 | Playfair Display + Lato | Classico, serif, bordi dorati |
| **Terra** | 1.723 | System fonts (zero download) | Eco, bordi definiti, no trasformazioni |
| **Zen** | 1.677 | Inter (2 pesi) | Minimale, max 720px, linee sottili |
| **Clubs** | 2.692 | System fonts (bold) | Premium, dark default, moto-inspired |
| **Tricolore** | 1.963 | Montserrat | Tricolore italiano, gradients |

**Totale**: 12.713 linee CSS

### Architettura 3 livelli

```
1. base.css           (shared reset, grid, typography, buttons, forms, events/news)
2. themes/{name}/main.css  (theme-specific overrides)
3. :root CSS variables     (dynamic color injection from ColorScheme snippet)
```

### Regole da seguire

1. **Mai modificare un solo tema**: ogni modifica CSS strutturale va in `base.css`; ogni modifica estetica va applicata a **tutti e 6** i temi
2. **Variabili CSS obbligatorie** in ogni tema:
   - `--color-primary`, `--color-secondary`, `--color-accent`
   - `--color-surface`, `--color-surface-alt`
   - `--color-text-primary`, `--color-text-muted`
3. **Token tema-specifici** (da non cambiare cross-tema):
   - `--{tema}-radius`, `--{tema}-shadow`, `--{tema}-transition`, `--{tema}-border`
4. **Nuovo componente HTML**: aggiungere stile base in `base.css`, poi personalizzare in ogni `main.css`
5. **Dark mode**: supportata via classe `.dark-mode` su `<html>` — ogni tema deve avere override dark mode
6. **Test visivo**: prima di fare commit, verificare il rendering almeno su Velocity + Clubs (chiaro e scuro)
7. **Selezione tema**: via `SiteSettings.theme` in Wagtail admin → iniettato da `theme_context()` context processor
8. **ColorScheme snippet**: permette ai admin di personalizzare i colori senza toccare CSS — i colori vengono iniettati come `:root` variables

### File chiave

- Context processor: `clubcms/apps/core/context_processors.py`
- Base template (caricamento): `clubcms/templates/base.html:17-39`
- SiteSettings (modello): `clubcms/apps/website/models/settings.py`
- ColorScheme (snippet): `clubcms/apps/website/models/snippets.py`

---

## 3. SICUREZZA — Criteri per accessi web

### Autenticazione per view (36 views auditate)

| Categoria | Conteggio | Stato |
|-----------|-----------|-------|
| Views con autenticazione | 33/36 | OK |
| Views pubbliche intenzionali | 3/36 | OK (EventICSView, PublicProfileView, RobotsTxtView) |
| CSRF protetto | 36/36 | OK |
| CSRF exempt giustificato | 2 | StripeWebhookView (firma HMAC), FederationAPI (firma HMAC) |
| Ownership check | 28/36 | OK (8 non ne necessitano) |
| Rate limiting | 4 implementazioni | Verification, Favorites, ContactUnlock, FederationAPI |

### Problemi da risolvere

| ID | Problema | Severita | File:Riga |
|----|----------|----------|-----------|
| SEC-1 | Path traversal in QRCodeView/BarcodeView — path non validato contro MEDIA_ROOT | **ALTO** | `apps/members/views.py:212,241` |
| SEC-2 | Rate limiting favorites usa dict in-memory (cresce senza limiti, non persiste) | **MEDIO** | `apps/events/views.py:325` |
| SEC-3 | HelperDetailView manca check `is_active_member` | **MEDIO** | `apps/mutual_aid/views.py:74` |
| SEC-4 | File handle leak in QR/Barcode views (`open()` senza context manager) | **BASSO** | `apps/members/views.py:212,241` |

### Fix richiesti

**SEC-1** — Aggiungere prima di `FileResponse`:
```python
if not os.path.abspath(path).startswith(os.path.abspath(settings.MEDIA_ROOT)):
    raise Http404()
```

**SEC-2** — Sostituire `_toggle_timestamps = {}` con Django cache:
```python
from django.core.cache import cache
cache_key = f"toggle_fav_{user_id}"
if cache.get(cache_key):
    return JsonResponse({"error": "..."}, status=429)
cache.set(cache_key, True, 1)
```

**SEC-3** — Aggiungere decorator `active_member_required` a `HelperDetailView`

### Regole da seguire

1. **Ogni nuova view con dati personali** deve avere `LoginRequiredMixin` o `@login_required`
2. **Ogni view che modifica dati** deve verificare ownership (`user=request.user`)
3. **Mai usare `@csrf_exempt`** senza autenticazione alternativa (HMAC, API key, webhook signature)
4. **Form POST**: sempre includere `{% csrf_token %}`
5. **File serve**: sempre validare che il path sia dentro `MEDIA_ROOT`
6. **Rate limiting**: usare Django cache o database, mai dict in-memory
7. **Secret keys**: solo in environment variables (`.env`), mai hard-coded
8. **Produzione** (`settings/prod.py`): HSTS, SSL redirect, CSRF_COOKIE_HTTPONLY, SESSION_COOKIE_SECURE gia attivi

---

## 4. FLUSSO DATI — Visibilita per ruolo visitatore

### Definizioni ruoli

| Ruolo | Definizione | Codice |
|-------|-------------|--------|
| **Anonimo** | Non loggato | `request.user.is_authenticated == False` |
| **Loggato non-socio** | Account senza membership attiva | `is_active_member == False` |
| **Socio attivo** | Membership valida | `is_active_member == True` (scadenza >= oggi) |
| **Staff/Admin** | `is_staff == True` | Accesso admin Wagtail |
| **Partner federato** | API con HMAC-SHA256 | `FederatedClub.is_active AND is_approved` |

### Matrice visibilita

| Funzionalita | Anonimo | Loggato non-socio | Socio attivo | Staff | Partner API |
|--------------|---------|-------------------|--------------|-------|-------------|
| **Directory soci** | NO | SI (nomi limitati) | SI (nomi reali se opt-in) | SI (completo) | NO |
| **Profili pubblici** | SI (se opt-in) | SI (se opt-in) | SI (se opt-in) | SI | NO |
| **Iscrizione eventi** | SI (guest form) | SI (con login) | SI (con sconto) | SI | NO |
| **Prezzi eventi** | SI (prezzo pieno) | SI (prezzo pieno) | SI (scontato) | SI | NO |
| **Mappa mutuo soccorso** | NO | NO | SI (privacy-filtered) | SI | Limitato (3 unlock/30gg) |
| **Contatto helper** | NO | NO | SI (form diretto) | SI | Limitato |
| **Eventi partner** | NO | SI (solo visualizzazione) | SI (commenti + interesse) | SI | NO |
| **Upload foto** | NO | NO | SI (se prodotto `grants_upload`) | SI (moderazione) | NO |
| **Moderazione foto** | NO | NO | NO | SI | NO |
| **Storico notifiche** | NO | SI (solo proprie) | SI (solo proprie) | SI (solo proprie) | NO |
| **Verifica socio (partner)** | NO | NO | NO | SI + partner owner | NO |
| **API Federazione** | NO | NO | NO | NO | SI (HMAC) |

### Dati personali MAI esposti

| Dato | Dove nascosto | Meccanismo |
|------|--------------|------------|
| **Email** | Ovunque (directory, profilo, map, verifica) | Mai nel context template |
| **Telefono** | Directory, profilo pubblico | Solo in mutual aid contact form (per soci) |
| **Indirizzo** | Ovunque | Solo in mutual aid (se `show_address_on_aid=True`) |
| **Codice fiscale** | Ovunque | Mai esposto in nessuna view |
| **Nome reale** | Directory per non-soci | `get_visible_name(viewer)` mascheramento |

### Sistema mascheramento nomi

```
Visitatore non-socio:  → vede display_name (nickname)
Socio attivo:          → vede nome reale SE l'altro utente ha show_real_name_to_members=True
                       → altrimenti display_name
Staff:                 → vede nome completo + display_name tra parentesi
```

**Implementazione**: `ClubUser.get_visible_name(viewer=user)` in `apps/members/models.py:122-141`

### Regole da seguire

1. **Mai esporre email in template** — usare `mask_email()` per visualizzazioni parziali
2. **Nuove view con dati personali**: seguire la matrice sopra
3. **`get_visible_name(viewer=request.user)`**: usare SEMPRE per mostrare nomi utenti
4. **Privacy mutual aid**: rispettare `AidPrivacySettings` — ogni campo ha il suo toggle
5. **Federazione**: mai condividere dati personali — solo conteggi aggregati ("X interessati")
6. **Unsubscribe**: token-based (no login richiesto), HMAC non enumerabile
7. **Verifica partner**: restituire SOLO `display_name` + `membership_expiry`, mai nome reale

---

## 5. TASK INCOMPLETI — Gap tra specifiche e implementazione

### Priorita CRITICA (bloccanti per produzione)

| ID | Task | Spec | File da modificare |
|----|------|------|--------------------|
| GAP-1 | Wrappare URL in `i18n_patterns()` | 41-MULTILANG | `clubcms/urls.py` |
| GAP-2 | Aggiungere language switcher in navbar | 41-MULTILANG | `templates/includes/navbar.html` |
| GAP-3 | Compilare file `.mo` per EN/DE/FR/ES | 41-MULTILANG | `locale/*/LC_MESSAGES/` |
| GAP-4 | Fix path traversal QR/Barcode views | Sicurezza | `apps/members/views.py` |

### Priorita ALTA (funzionalita mancanti)

| ID | Task | Spec | File da modificare |
|----|------|------|--------------------|
| GAP-5 | Campi mancanti EventDetailPage: `allow_guests`, `meeting_point`, `difficulty`, `passenger_fee/discount/included` | 82-EVENT-REG, 95-GAPS | `apps/website/models/pages.py` |
| GAP-6 | `computed_deadline` da PricingTier.is_deadline | 82-EVENT-REG | `apps/website/models/pages.py` |
| GAP-7 | Calcolo prezzo passeggero in `calculate_price()` | 82-EVENT-REG | `apps/events/utils.py` |
| GAP-8 | PricingTier InlinePanel in admin | 82-EVENT-REG | `apps/website/models/pages.py` |
| GAP-9 | Fix rate limiting favorites (dict → cache) | Sicurezza | `apps/events/views.py` |
| GAP-10 | Fix HelperDetailView access check | Sicurezza | `apps/mutual_aid/views.py` |

### Priorita MEDIA (WCAG / UX)

| ID | Task | Spec | File da modificare |
|----|------|------|--------------------|
| GAP-11 | `aria-describedby` su campi form registrazione | 95-GAPS (W2) | `apps/events/forms.py` |
| GAP-12 | `aria-required="true"` su campi required | 95-GAPS (W3) | `apps/events/forms.py` |
| GAP-13 | Classi CSS (`form-input`, `form-select`) sui widget Django | 95-GAPS (W4) | `apps/events/forms.py` |
| GAP-14 | Attributi `autocomplete` sui campi personali | 95-GAPS (W5) | `apps/events/forms.py` |
| GAP-15 | Link ai termini nel checkbox `accept_terms` | 95-GAPS (W6) | `apps/events/forms.py` |
| GAP-16 | Riepilogo pre-submit nella registrazione | 95-GAPS (U3) | `templates/events/register.html` |

### Priorita BASSA (nice to have)

| ID | Task | Spec |
|----|------|------|
| GAP-17 | PWA service worker (referenziato ma non trovato) | 84-PWA-BASE |
| GAP-18 | Sistema contributi/storie utente | 85-CONTRIBUTION-BASE |
| GAP-19 | Press office completo | 88-PRESS-OFFICE |
| GAP-20 | Background task scheduling (django-q2 configurato ma task non schedulati) | 91-NOTIFICATIONS |

---

## 6. ARCHITETTURA — Riferimenti rapidi

### App Django (7)

| App | Funzione | Modelli principali |
|-----|----------|-------------------|
| `core` | Feed RSS, robots.txt, context processors, SEO tags | - |
| `website` | Pages, blocks, settings, snippets, uploads, verifica | HomePage, NewsPage, EventDetailPage, SiteSettings, ColorScheme, Product |
| `members` | Utenti, profili, card, directory, privacy | ClubUser (custom User), Product (M2M) |
| `events` | Registrazioni, pagamenti, preferiti, ICS | EventRegistration, PricingTier, EventFavorite |
| `federation` | Multi-club partnership, API HMAC | FederatedClub, ExternalEvent, ExternalEventInterest |
| `notifications` | Email, push, in-app, unsubscribe | NotificationQueue, PushSubscription, UnsubscribeToken |
| `mutual_aid` | Rete volontari, mappa, privacy | MutualAidPage, AidPrivacySettings, AidRequest, AccessRequest |

### URL root

```
/django-admin/     → Django admin
/admin/            → Wagtail admin
/account/          → Members (profilo, card, privacy, notifiche, directory)
/members/<user>/   → Profilo pubblico
/events/           → Registrazione, pagamenti, preferiti, ICS
/mutual-aid/       → Mappa helper, contatti, richieste accesso
/notifications/    → Unsubscribe, push, storico
/api/federation/   → API federazione (se abilitata)
/eventi/partner/   → Frontend eventi federati (se abilitata)
/                  → Core (feed, robots) + Wagtail catch-all
```

### Docker

```bash
docker compose -f clubcms/docker-compose.yml up -d
docker compose -f clubcms/docker-compose.yml exec web python manage.py makemigrations
docker compose -f clubcms/docker-compose.yml exec web python manage.py migrate
docker compose -f clubcms/docker-compose.yml exec web pytest apps/ -v
```

---

## 7. CHECKLIST PRE-COMMIT

Per ogni sessione di sviluppo, prima di fare commit verificare:

- [ ] Stringhe utente wrappate in `{% trans %}` o `_()`
- [ ] CSS modifiche applicate a `base.css` (strutturali) o **tutti 6 temi** (estetiche)
- [ ] View con dati personali ha `LoginRequiredMixin` + ownership check
- [ ] Form POST ha `{% csrf_token %}`
- [ ] Nessun dato personale esposto senza controllo ruolo
- [ ] Test passano: `pytest apps/ -v`
- [ ] Nessun secret hard-coded
- [ ] File path validati contro `MEDIA_ROOT`
