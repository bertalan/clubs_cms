# 97 - Sintesi delle Modifiche Effettuate

## Panoramica

Questo documento riassume tutte le modifiche apportate al progetto ClubCMS
a partire dal commit `b33815a` fino all'attuale sessione di lavoro.

---

## 1. Pagamenti: Stripe e PayPal

| Pacchetto | Stato | Versione | Note |
|-----------|-------|----------|------|
| `stripe`  | Installato in Docker | 9.12.0 | Presente in `requirements.txt` (`>=8.0,<10.0`) |
| PayPal    | Funzionante via `httpx` | 0.28.1 | Usa direttamente PayPal Orders API v2, nessun SDK separato necessario |

**File coinvolti:**
- `apps/events/payment.py` — `create_paypal_order()`, `capture_paypal_order()`, `get_paypal_access_token()`
- `apps/events/views.py` — `StripeWebhookView`, `PayPalCaptureView`
- `apps/events/tests/test_payment_views.py` — `@pytest.mark.skipif(not HAS_STRIPE)` per i test Stripe

---

## 2. Correzioni WCAG 2.2 e W3C

### 2.1 Bordi dei form (SC 1.4.11 — Non-text Contrast >= 3:1)

**Problema:** I bordi degli input erano `1px solid rgba(0,0,0,0.15)` (~1.6:1 contrasto) — invisibili su sfondi chiari.

**Soluzione:**
- `base.css` `:root` — aggiunto `--color-border: rgba(0, 0, 0, 0.35)` (>3:1 su bianco)
- Tutti i `.form-input`, `.form-select`, `.form-textarea` ora usano `2px solid var(--color-border)`
- Focus state: `box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.2)`

### 2.2 Input Django senza classi CSS (allauth)

**Problema:** Django allauth genera `<input>` senza classi CSS. Gli input nelle pagine login/signup erano completamente privi di stile.

**Soluzione:** Aggiunto selettore `.auth-card input[type="text/email/password/..."]` in `base.css` con lo stesso stile dei `.form-input`.

### 2.3 Dichiarazioni duplicate eliminate

**Problema:** `.form-input` era dichiarato 3 volte in `base.css` con valori diversi.

**Soluzione:** Mantenuta una sola dichiarazione canonica (sezione "Form Utilities") con commento WCAG. Le altre due sostituite con riferimenti.

### 2.4 Temi: `--color-border` aggiunto

| Tema | `--color-border` | Note |
|------|-------------------|------|
| Velocity | `rgba(0,0,0,0.35)` (default) | Sfondo chiaro di base |
| Heritage | `rgba(0,0,0,0.35)` (default) | Sfondo crema |
| Terra | `rgba(0,0,0,0.3)` | Sfondo caldo `#E8DFD0` |
| Zen | `rgba(0,0,0,0.35)` (default) | Minimalista |
| Clubs | `rgba(255,255,255,0.3)` | Tema scuro — bordi chiari |
| Tricolore | `rgba(0,0,0,0.3)` | Sfondo `#F4F5F0` |

### 2.5 Tema Clubs: styling completo dark mode per form e auth

Aggiunto in `clubs/main.css`:
- `.auth-card` con sfondo `--color-surface-alt`, bordi luminosi
- Input auth con sfondo `--color-surface`, bordi `rgba(255,255,255,0.3)`
- Focus ring rosso `rgba(196, 30, 58, 0.25)`
- Pricing card con bordi e badge coerenti col tema
- `.auth-switch a` color `--color-secondary` per visibilita'

### 2.6 Dark mode globale per form

In `base.css` aggiunto blocco `.dark-mode` per auth card inputs e form utilities:
- Sfondo `--color-surface-alt`
- Bordi `rgba(255, 255, 255, 0.3)`
- Focus ring `rgba(96, 165, 250, 0.25)`

### 2.7 `.btn-outline` aggiunto

**Problema:** La classe `.btn-outline` era usata nel template `membership_plans.html` ma non definita.

**Soluzione:** Aggiunto `.btn-outline` in `base.css` con bordo e colore `--color-primary`, hover inverso.

---

## 3. Navbar: semplificazione e accessibilita'

### 3.1 Menu utente ridotto da 9 a 6 voci

**Prima (9 voci):**
1. Il mio profilo
2. Tessera socio
3. Le mie iscrizioni
4. I miei eventi
5. Elenco soci (condizionale)
6. Impostazioni privacy
7. Preferenze notifiche
8. Impostazioni mutuo soccorso (condizionale)
9. Esci

**Dopo (6 voci):**
1. Il mio profilo
2. Tessera socio
3. I miei eventi (unifica iscrizioni + eventi)
4. Elenco soci (condizionale)
5. Impostazioni (link unico a `/account/privacy/`)
6. Esci

### 3.2 URL difensivi per allauth

Usa pattern `{% url 'account_logout' as logout_url %}` con `{% if logout_url %}` per graceful degradation se allauth non e' installato.

### 3.3 Internazionalizzazione

Corretto `aria-label` del logo: `"{{ site_name }} - Home"` => `"{{ site_name }} - {% trans 'Home' %}"`.
Tutti i testi visibili usano `{% trans %}`.

---

## 4. Coordinamento dei 6 temi

Ogni tema ora include:

### Componenti CSS coordinati:
- `.site-nav__dropdown-*` — stile dropdown coerente col tema
- `.auth-card` — bordi/raggi coerenti (Heritage: 2px, no radius; Clubs: no radius; Zen: 2px radius; Tricolore: tricolore border-top)
- `.pricing-card` — stile card membership coerente
- `.form-input` focus — colore primario del tema
- Dark mode — variabili colore coerenti

### Tabella di coordinamento:

| Componente | Velocity | Heritage | Terra | Zen | Clubs | Tricolore |
|-----------|----------|----------|-------|-----|-------|-----------|
| Nav | fixed, blur | sticky, navy | sticky, green | sticky, light | fixed, blur | sticky, light |
| Auth card | rounded | square, gold border | square | minimal | square, dark bg | tricolore top |
| Pricing | rounded | square, gold | square | minimal | square, dark | tricolore top |
| Focus ring | purple | gold | green | blue | red | green |
| Form border | 2px dark | 2px dark | 2px dark | 2px dark | 2px light | 2px dark |

---

## 5. Sicurezza

### 5.1 Modifiche precedenti (gia' implementate)

- **SEC-1:** `SECURE_PROXY_SSL_HEADER` in settings
- **SEC-2:** Rate limiting cache-based per favorites (`apps/events/views.py`)
- **SEC-3:** Controllo `is_active_member` per mutual aid (`apps/mutual_aid/views.py`)

### 5.2 URL difensivi

- allauth URLs inclusi condizionalmente in `urls.py` con `try: import allauth`
- Template navbar usa `{% url ... as var %}` per evitare crash se allauth non presente
- `@login_required` e decoratori appropriati su tutte le view protette

---

## 6. Multilingua

- Tutti i template usano `{% load i18n %}` e `{% trans %}`
- URL patterns sotto `i18n_patterns()` con `prefix_default_language=True`
- allauth templates con stringhe tradotte
- aria-label navbar tradotto
- Supporto: `it`, `en`, `de`, `fr`, `es` (configurati in `LANGUAGES`)

---

## 7. Risultato test

```
177 passed, 4 skipped in 17.63s
```

I 4 test skippati sono relativi a Stripe webhook (`TestStripeWebhookView`) —
necessitano del pacchetto `stripe` che e' installato in Docker ma non nell'ambiente `.venv` locale.

---

## 8. File modificati in questa sessione

### CSS
- `static/css/base.css` — `:root` vars, WCAG form borders, auth input styling, dark mode forms, `.btn-outline`, dedup
- `static/css/themes/tricolore/main.css` — `--color-border`
- `static/css/themes/clubs/main.css` — form dark overrides, auth card dark styling, pricing card dark

### Template
- `templates/includes/navbar.html` — user menu semplificato, aria-label i18n fix

### Nessun file Python modificato in questa sessione
(Le modifiche Python erano nella sessione precedente: urls.py, views.py, tests)

---

## 9. Comandi Docker eseguiti

```bash
# Migrazione applicata
docker exec clubcms-web-1 python manage.py migrate website 0005

# Verifica
docker exec clubcms-web-1 python manage.py showmigrations website
# website.0005_navbaritem_parent... OK

# Sito verificato
curl -s -o /dev/null -w "%{http_code}" http://localhost:8888/it/
# 200
```

---

## 10. Prossimi passi consigliati

1. **Compilare stringhe i18n:** `django-admin makemessages -l it -l en -l de -l fr -l es`
2. **Verificare i 6 temi visivamente** nel browser con il selettore tema attivo
3. **Configurare dropdown nel Wagtail admin** — creare NavbarItem con `parent` per testare i sottomenu
4. **Installare stripe localmente** per eseguire anche i 4 test skippati: `pip install stripe>=8.0`
5. **Test end-to-end** del flusso registrazione: signup -> login -> profilo -> membership -> pagamento
