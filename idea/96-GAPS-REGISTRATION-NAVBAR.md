# Gap Analysis: Registration, Navigation & Hidden Pages

> **Scope:** Analisi completa delle mancanze su registrazione utente, navigazione e pagine non visibili.
> **Metodo:** TDD — per ogni elemento: test prima, implementazione poi, verifica integrazione.

---

## Executive Summary

### Problemi critici identificati

| ID | Problema | Severita |
|----|----------|----------|
| **REG-1** | Nessun template custom per signup/login/logout (allauth usa default senza tema) | **CRITICO** |
| **REG-2** | Nessun link "Registrati" / "Accedi" nella navbar | **CRITICO** |
| **REG-3** | Nessun menu utente dopo login (profilo, tessera, privacy, ecc.) | **CRITICO** |
| **NAV-1** | Navbar completamente piatta — zero supporto dropdown/submenu | **ALTO** |
| **NAV-2** | 9+ pagine account non raggiungibili dalla navigazione | **ALTO** |
| **NAV-3** | Nessun indicatore visivo utente loggato vs anonimo | **ALTO** |
| **NAV-4** | Menu mobile non supporta sottomenu srotolabili | **MEDIO** |
| **REG-4** | Nessuna pagina "Diventa Socio" con prodotti/piani membership | **ALTO** |
| **REG-5** | Flusso post-registrazione incompleto (nessun onboarding) | **MEDIO** |

---

## Parte 1: REGISTRAZIONE — Stato attuale e gap

### Cosa esiste

- `RegistrationForm` in `apps/members/forms.py:25-62` estende `allauth.account.forms.SignupForm`
- Configurazione allauth in `clubcms/settings/base.py:161-199`:
  - `ACCOUNT_FORMS = {"signup": "apps.members.forms.RegistrationForm"}`
  - `ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]`
  - `ACCOUNT_EMAIL_VERIFICATION = "optional"`
- Custom user model `ClubUser` in `apps/members/models.py`
- 7 template account in `templates/account/` (profile, card, privacy, notifications, aid, directory, public_profile)

### Cosa MANCA

| File mancante | Scopo |
|---------------|-------|
| `templates/account/signup.html` | Pagina di registrazione con tema del sito |
| `templates/account/login.html` | Pagina di login con tema del sito |
| `templates/account/logout.html` | Conferma logout |
| `templates/account/password_reset.html` | Reset password |
| `templates/account/password_reset_done.html` | Conferma invio reset |
| `templates/account/password_change.html` | Cambio password |
| `templates/account/email_confirm.html` | Conferma email |
| `templates/account/email.html` | Gestione email |
| NO pagina "Diventa Socio" | Vetrina prodotti/piani membership |
| NO flusso onboarding | Guida post-registrazione |

### Come funziona OGGI il flusso registrazione

```
1. Utente naviga a /account/signup/ (nessun link visibile)
2. Allauth serve il template DEFAULT (non tematizzato, non integrato con base.html)
3. Form mostra: username, email, password1, password2, first_name, last_name, display_name, newsletter
4. Dopo submit → allauth crea ClubUser
5. Redirect a LOGIN_REDIRECT_URL = "/my-profile/" (404 — l'URL corretto e' /account/profile/)
6. Nessuna email di benvenuto
7. Nessun onboarding
8. Card_number, membership_date, membership_expiry = NULL
9. products = vuoto → nessun permesso
```

### Problemi specifici

1. **LOGIN_REDIRECT_URL errato**: punta a `/my-profile/` ma la view e' a `/account/profile/`
2. **Nessun template allauth**: i template vanno in `templates/account/` con naming allauth v0.60+
3. **Nessun link visibile**: impossibile trovare signup/login senza conoscere l'URL
4. **Nessuna pagina "Diventa Socio"**: i prodotti (tessera base, voto, gallery, ecc.) non sono presentati all'utente

---

## Parte 2: NAVIGAZIONE — Stato attuale e gap

### Struttura attuale navbar

```
[Logo] [Link1] [Link2] ... [LinkN] [Search] [Lang]
```

- Tutti i link sono piatti (flat), nessun dropdown
- `NavbarItem` model (`snippets.py:162-198`): label, link_page, link_url, is_cta — nessun `parent`/`children`
- Template `navbar.html`: loop semplice `{% for item in navbar.items.all %}` senza nesting

### Pagine NON raggiungibili dalla navigazione

| Pagina | URL | Richiede auth |
|--------|-----|---------------|
| Registrazione | `/account/signup/` | No |
| Login | `/account/login/` | No |
| Profilo | `/account/profile/` | Si |
| Tessera digitale | `/account/card/` | Si |
| Privacy | `/account/privacy/` | Si |
| Notifiche | `/account/notifications/` | Si |
| Mutuo soccorso | `/account/aid/` | Si |
| Directory soci | `/account/directory/` | Si |
| Le mie iscrizioni | `/events/my-registrations/` | Si |
| I miei eventi | `/events/my-events/` | Si |
| I miei upload | `/my-uploads/` | Si |
| Storico notifiche | `/notifications/history/` | Si |
| Mappa mutuo soccorso | `/mutual-aid/` | Si |

---

## Parte 3: PIANO DI IMPLEMENTAZIONE TDD

> Per ogni feature: **1) Test** → **2) Implementazione** → **3) Verifica integrazione**

---

### FASE 1: Modello Navbar con supporto dropdown

#### 1.1 Test: NavbarItem con figli (dropdown)

**File:** `apps/website/tests/test_navbar.py`

```python
"""
Test per la navigazione con supporto dropdown/submenu.
Verifica: modello, rendering template, integrazione temi, i18n, sicurezza.
"""

# --- TEST MODELLO ---

class TestNavbarItemParentChild:
    """NavbarItem puo' avere figli per creare dropdown."""

    def test_navbar_item_has_parent_field(self):
        """NavbarItem ha campo parent nullable."""

    def test_top_level_items_have_no_parent(self):
        """Items di primo livello hanno parent=None."""

    def test_child_items_have_parent(self):
        """Sub-items hanno parent che punta a un NavbarItem."""

    def test_max_depth_is_one(self):
        """Solo 1 livello di nesting (no sub-sub-menu)."""

    def test_parent_is_not_cta(self):
        """Un item con figli non puo' essere CTA."""

    def test_deleting_parent_cascades_children(self):
        """Eliminare parent elimina i figli."""


# --- TEST TEMPLATE ---

class TestNavbarDropdownRendering:
    """Il template navbar renderizza dropdown con ARIA corretti."""

    def test_top_level_without_children_renders_link(self):
        """Item senza figli = link diretto <a>."""

    def test_top_level_with_children_renders_dropdown(self):
        """Item con figli = <button> toggle + <ul> submenu."""

    def test_dropdown_has_aria_expanded(self):
        """Button dropdown ha aria-expanded='false' iniziale."""

    def test_dropdown_has_aria_haspopup(self):
        """Button dropdown ha aria-haspopup='true'."""

    def test_submenu_has_role_menu(self):
        """Submenu <ul> ha role='menu'."""

    def test_submenu_items_have_role_menuitem(self):
        """Link nel submenu hanno role='menuitem'."""

    def test_active_page_in_dropdown_marks_parent(self):
        """Se pagina attiva e' in dropdown, anche parent ha classe 'active'."""


# --- TEST MOBILE ---

class TestMobileDropdown:
    """Dropdown su mobile e' srotolabile (accordion style)."""

    def test_mobile_dropdown_is_collapsible(self):
        """Su mobile, dropdown usa pattern accordion."""

    def test_mobile_dropdown_toggle_class(self):
        """Click su parent mobiletoggle la classe 'open'."""


# --- TEST INTEGRAZIONE TEMI ---

class TestNavbarThemeIntegration:
    """Dropdown funziona con tutti e 6 i temi."""

    def test_velocity_dropdown_styles_exist(self):
        """velocity/main.css contiene stili per .site-nav__dropdown."""

    def test_heritage_dropdown_styles_exist(self):
        """heritage/main.css contiene stili per .site-nav__dropdown."""

    def test_terra_dropdown_styles_exist(self):
        """terra/main.css contiene stili per .site-nav__dropdown."""

    def test_zen_dropdown_styles_exist(self):
        """zen/main.css contiene stili per .site-nav__dropdown."""

    def test_clubs_dropdown_styles_exist(self):
        """clubs/main.css contiene stili per .site-nav__dropdown."""

    def test_tricolore_dropdown_styles_exist(self):
        """tricolore/main.css contiene stili per .site-nav__dropdown."""


# --- TEST I18N ---

class TestNavbarMultilingual:
    """Dropdown labels sono traducibili."""

    def test_navbar_item_label_uses_gettext(self):
        """Label navbar sono wrappati in trans tag nel template."""

    def test_dropdown_in_all_languages(self):
        """Dropdown funziona con prefisso /it/, /en/, ecc."""
```

#### 1.2 Implementazione: Modello NavbarItem con parent

**File da modificare:** `apps/website/models/snippets.py`

Aggiungere a `NavbarItem`:
```python
parent = models.ForeignKey(
    "self",
    null=True,
    blank=True,
    on_delete=models.CASCADE,
    related_name="children",
    verbose_name=_("Parent item"),
    help_text=_("Leave empty for top-level items. Select a parent for dropdown sub-items."),
)
```

Aggiungere metodo a `Navbar`:
```python
def top_level_items(self):
    """Restituisce solo gli items di primo livello (senza parent)."""
    return self.items.filter(parent__isnull=True)
```

#### 1.3 Implementazione: Template navbar con dropdown

**File da modificare:** `templates/includes/navbar.html`

```html
{% for item in navbar.top_level_items %}
    {% with children=item.children.all %}
    {% if children %}
        {# DROPDOWN #}
        <div class="site-nav__dropdown">
            <button class="site-nav__dropdown-toggle"
                    type="button"
                    aria-expanded="false"
                    aria-haspopup="true">
                {{ item.label }}
                <span class="site-nav__dropdown-arrow" aria-hidden="true">&#9662;</span>
            </button>
            <ul class="site-nav__dropdown-menu" role="menu">
                {% for child in children %}
                <li role="none">
                    <a href="{% if child.link_page %}{% pageurl child.link_page %}{% else %}{{ child.link_url }}{% endif %}"
                       role="menuitem"
                       {% if child.open_new_tab %}target="_blank" rel="noopener noreferrer"{% endif %}>
                        {{ child.label }}
                    </a>
                </li>
                {% endfor %}
            </ul>
        </div>
    {% else %}
        {# LINK DIRETTO #}
        <a href="...">{{ item.label }}</a>
    {% endif %}
    {% endwith %}
{% endfor %}
```

#### 1.4 Implementazione: CSS dropdown in base.css + 6 temi

**File:** `static/css/base.css` — stili strutturali:
```css
.site-nav__dropdown { position: relative; }
.site-nav__dropdown-menu {
    display: none; position: absolute; top: 100%; left: 0;
    list-style: none; padding: 0.5rem 0; min-width: 200px; z-index: 1000;
}
.site-nav__dropdown.open .site-nav__dropdown-menu,
.site-nav__dropdown:focus-within .site-nav__dropdown-menu { display: block; }

/* Mobile: accordion style */
@media (max-width: 768px) {
    .site-nav__dropdown-menu { position: static; display: none; }
    .site-nav__dropdown.open .site-nav__dropdown-menu { display: block; }
}
```

**Ogni tema** (`themes/{name}/main.css`): aggiungere colori, bordi, ombre specifiche.

#### 1.5 Implementazione: JavaScript dropdown

**Aggiungere in `navbar.html` o in `static/js/navbar.js`:**
```javascript
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.site-nav__dropdown-toggle').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            var dropdown = this.closest('.site-nav__dropdown');
            var isOpen = dropdown.classList.contains('open');
            // Chiudi tutti gli altri
            document.querySelectorAll('.site-nav__dropdown.open').forEach(function(d) {
                d.classList.remove('open');
                d.querySelector('.site-nav__dropdown-toggle').setAttribute('aria-expanded', 'false');
            });
            if (!isOpen) {
                dropdown.classList.add('open');
                this.setAttribute('aria-expanded', 'true');
            }
        });
    });
    // Chiudi dropdown al click fuori
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.site-nav__dropdown')) {
            document.querySelectorAll('.site-nav__dropdown.open').forEach(function(d) {
                d.classList.remove('open');
                d.querySelector('.site-nav__dropdown-toggle').setAttribute('aria-expanded', 'false');
            });
        }
    });
    // Keyboard: Escape chiude dropdown
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.site-nav__dropdown.open').forEach(function(d) {
                d.classList.remove('open');
                var toggle = d.querySelector('.site-nav__dropdown-toggle');
                toggle.setAttribute('aria-expanded', 'false');
                toggle.focus();
            });
        }
    });
});
```

#### 1.6 Verifica integrazione

- [ ] **Wagtail admin**: InlinePanel NavbarItem mostra campo "Parent item" con autocomplete
- [ ] **Multilingual**: dropdown funziona con URL prefissate `/it/`, `/en/`, ecc.
- [ ] **6 Temi**: stili dropdown presenti in ogni `main.css`
- [ ] **Sicurezza**: nessun XSS nei label (gia' escaped da Django template engine)
- [ ] **WCAG**: aria-expanded, aria-haspopup, role=menu, role=menuitem, keyboard nav
- [ ] **Mobile**: dropdown srotolabile (accordion) nel menu hamburger

---

### FASE 2: Menu utente autenticato nella navbar

#### 2.1 Test: Visibilita' condizionale navbar

**File:** `apps/website/tests/test_navbar_auth.py`

```python
"""
Test per la sezione utente nella navbar.
Verifica: visibilita' condizionale, link corretti, sicurezza, i18n.
"""

class TestAnonymousUserNavbar:
    """Utente anonimo vede link Accedi/Registrati."""

    def test_anonymous_sees_login_link(self):
        """Anonimo vede 'Accedi' che punta a /account/login/."""

    def test_anonymous_sees_signup_link(self):
        """Anonimo vede 'Registrati' che punta a /account/signup/."""

    def test_anonymous_does_not_see_user_menu(self):
        """Anonimo NON vede il dropdown utente."""

    def test_anonymous_does_not_see_account_links(self):
        """Anonimo NON vede link profilo/tessera/privacy."""


class TestAuthenticatedUserNavbar:
    """Utente loggato vede dropdown con le proprie pagine."""

    def test_logged_in_sees_user_dropdown(self):
        """Utente loggato vede dropdown con display_name."""

    def test_logged_in_sees_profile_link(self):
        """Dropdown contiene link a /account/profile/."""

    def test_logged_in_sees_card_link(self):
        """Dropdown contiene link a /account/card/."""

    def test_logged_in_sees_privacy_link(self):
        """Dropdown contiene link a /account/privacy/."""

    def test_logged_in_sees_notifications_link(self):
        """Dropdown contiene link a /account/notifications/."""

    def test_logged_in_sees_my_events_link(self):
        """Dropdown contiene link a /events/my-events/."""

    def test_logged_in_sees_my_registrations_link(self):
        """Dropdown contiene link a /events/my-registrations/."""

    def test_logged_in_sees_logout_link(self):
        """Dropdown contiene link Logout."""

    def test_logged_in_does_not_see_login_signup(self):
        """Utente loggato NON vede Accedi/Registrati."""


class TestActiveMemberNavbar:
    """Socio attivo vede link addizionali."""

    def test_member_sees_directory_link(self):
        """Socio attivo vede link Directory Soci."""

    def test_member_sees_aid_link(self):
        """Socio attivo vede link Mutuo Soccorso (settings)."""

    def test_member_sees_mutual_aid_map(self):
        """Socio attivo vede link Mappa Soccorso."""

    def test_non_member_does_not_see_directory(self):
        """Loggato senza membership NON vede Directory."""


class TestNavbarUserMenuI18n:
    """Link utente sono tradotti."""

    def test_profile_label_is_translated(self):
        """'Il mio profilo' tradotto in EN come 'My profile'."""

    def test_logout_label_is_translated(self):
        """'Esci' tradotto in EN come 'Log out'."""
```

#### 2.2 Implementazione: Sezione utente in navbar.html

Aggiungere DOPO il loop dei menu items, PRIMA del search:

```html
{# User menu #}
<div class="site-nav__user">
    {% if request.user.is_authenticated %}
        <div class="site-nav__dropdown">
            <button class="site-nav__dropdown-toggle site-nav__user-toggle"
                    type="button" aria-expanded="false" aria-haspopup="true">
                {% if request.user.photo %}
                    <img src="{{ request.user.photo.url }}" alt="" class="site-nav__avatar">
                {% endif %}
                <span>{{ request.user.get_display_name }}</span>
                <span class="site-nav__dropdown-arrow" aria-hidden="true">&#9662;</span>
            </button>
            <ul class="site-nav__dropdown-menu" role="menu">
                <li role="none">
                    <a href="{% url 'account:profile' %}" role="menuitem">
                        {% trans "My profile" %}
                    </a>
                </li>
                <li role="none">
                    <a href="{% url 'account:card' %}" role="menuitem">
                        {% trans "Membership card" %}
                    </a>
                </li>
                <li role="none">
                    <a href="{% url 'events:my_registrations' %}" role="menuitem">
                        {% trans "My registrations" %}
                    </a>
                </li>
                <li role="none">
                    <a href="{% url 'events:my_events' %}" role="menuitem">
                        {% trans "My events" %}
                    </a>
                </li>
                {% if request.user.is_active_member %}
                <li role="none">
                    <a href="{% url 'account:directory' %}" role="menuitem">
                        {% trans "Member directory" %}
                    </a>
                </li>
                {% endif %}
                <li class="site-nav__dropdown-divider" role="separator"></li>
                <li role="none">
                    <a href="{% url 'account:privacy' %}" role="menuitem">
                        {% trans "Privacy settings" %}
                    </a>
                </li>
                <li role="none">
                    <a href="{% url 'account:notifications' %}" role="menuitem">
                        {% trans "Notification preferences" %}
                    </a>
                </li>
                {% if request.user.is_active_member %}
                <li role="none">
                    <a href="{% url 'account:aid' %}" role="menuitem">
                        {% trans "Mutual aid settings" %}
                    </a>
                </li>
                {% endif %}
                <li class="site-nav__dropdown-divider" role="separator"></li>
                <li role="none">
                    <a href="{% url 'account_logout' %}" role="menuitem">
                        {% trans "Log out" %}
                    </a>
                </li>
            </ul>
        </div>
    {% else %}
        <a href="{% url 'account_login' %}" class="site-nav__login">
            {% trans "Log in" %}
        </a>
        <a href="{% url 'account_signup' %}" class="site-nav__cta">
            {% trans "Sign up" %}
        </a>
    {% endif %}
</div>
```

#### 2.3 Verifica integrazione

- [ ] **Wagtail**: nessuna modifica al modello — puro template
- [ ] **Multilingual**: tutti i `{% trans %}` presenti, URL con `{% url %}` rispettano i18n_patterns
- [ ] **6 Temi**: stili `.site-nav__user`, `.site-nav__avatar`, `.site-nav__login` in ogni tema
- [ ] **Sicurezza**: link account non visibili ad anonimo, link member-only non visibili a non-soci
- [ ] **Flusso dati**: `request.user.is_active_member` usato per condizionare link
- [ ] **WCAG**: dropdown utente con stessi pattern ARIA del dropdown navigazione

---

### FASE 3: Template allauth tematizzati

#### 3.1 Test: Template registrazione e login

**File:** `apps/members/tests/test_auth_templates.py`

```python
"""
Test per i template allauth customizzati.
Verifica: rendering, integrazione tema, i18n, WCAG, sicurezza.
"""

class TestSignupTemplate:
    """Template signup estende base.html e mostra campi corretti."""

    def test_signup_page_returns_200(self):
        """GET /account/signup/ restituisce 200."""

    def test_signup_extends_base_template(self):
        """Template signup estende base.html (include navbar/footer)."""

    def test_signup_form_has_csrf_token(self):
        """Form contiene {% csrf_token %}."""

    def test_signup_shows_custom_fields(self):
        """Form mostra first_name, last_name, display_name, newsletter."""

    def test_signup_form_has_aria_required(self):
        """Campi required hanno aria-required='true'."""

    def test_signup_form_has_css_classes(self):
        """Input hanno classe 'form-input'."""

    def test_signup_has_login_link(self):
        """Pagina contiene link 'Hai gia' un account? Accedi'."""

    def test_signup_responds_in_all_languages(self):
        """GET /it/account/signup/ e /en/account/signup/ restituiscono 200."""


class TestLoginTemplate:
    """Template login estende base.html."""

    def test_login_page_returns_200(self):
        """GET /account/login/ restituisce 200."""

    def test_login_extends_base_template(self):
        """Template login estende base.html."""

    def test_login_has_csrf_token(self):
        """Form contiene {% csrf_token %}."""

    def test_login_has_signup_link(self):
        """Pagina contiene link 'Non hai un account? Registrati'."""

    def test_login_has_password_reset_link(self):
        """Pagina contiene link 'Password dimenticata?'."""

    def test_login_responds_in_all_languages(self):
        """GET /it/account/login/ e /en/account/login/ restituiscono 200."""


class TestLogoutTemplate:
    """Template logout con conferma."""

    def test_logout_requires_post(self):
        """Logout richiede POST (non GET) per sicurezza."""

    def test_logout_page_shows_confirmation(self):
        """GET /account/logout/ mostra conferma 'Sei sicuro?'."""

    def test_logout_redirects_to_home(self):
        """POST logout redirige a /."""


class TestPasswordResetTemplate:
    """Template reset password."""

    def test_password_reset_returns_200(self):
        """GET /account/password/reset/ restituisce 200."""

    def test_password_reset_extends_base(self):
        """Template estende base.html."""


class TestSignupIntegration:
    """Test integrazione completa flusso registrazione."""

    def test_signup_creates_club_user(self):
        """POST signup crea un ClubUser con first_name e last_name."""

    def test_signup_sets_display_name(self):
        """Se display_name fornito, viene salvato."""

    def test_signup_sets_newsletter(self):
        """Se newsletter=True, viene salvato."""

    def test_signup_redirects_to_profile(self):
        """Dopo signup, redirect a /account/profile/."""

    def test_signup_user_has_no_membership(self):
        """Nuovo utente ha card_number=None, membership_expiry=None."""
```

#### 3.2 Implementazione: Template allauth

**Nota:** Allauth v0.60+ usa path `templates/account/` per i template override.

**File:** `templates/account/signup.html`
```html
{% extends "base.html" %}
{% load i18n %}

{% block title %}{% trans "Sign up" %}{% endblock %}

{% block content %}
<div class="container auth-container">
    <div class="auth-card">
        <h1>{% trans "Create your account" %}</h1>
        <p class="auth-subtitle">
            {% trans "Join the club and access events, member directory, and more." %}
        </p>

        <form method="post" action="{% url 'account_signup' %}">
            {% csrf_token %}
            {% for field in form %}
            <div class="form-group {% if field.errors %}has-error{% endif %}">
                <label for="{{ field.id_for_label }}">
                    {{ field.label }}
                    {% if field.field.required %}<span class="required" aria-hidden="true">*</span>{% endif %}
                </label>
                {{ field }}
                {% if field.help_text %}
                <small id="{{ field.id_for_label }}_help" class="form-help">{{ field.help_text }}</small>
                {% endif %}
                {% for error in field.errors %}
                <span class="form-error" role="alert">{{ error }}</span>
                {% endfor %}
            </div>
            {% endfor %}
            <button type="submit" class="btn btn-primary btn-block">
                {% trans "Sign up" %}
            </button>
        </form>

        <p class="auth-switch">
            {% trans "Already have an account?" %}
            <a href="{% url 'account_login' %}">{% trans "Log in" %}</a>
        </p>
    </div>
</div>
{% endblock %}
```

**File:** `templates/account/login.html` — stesso pattern con form login.

**File:** `templates/account/logout.html` — conferma POST.

**File:** `templates/account/password_reset.html` — form email.

#### 3.3 Fix LOGIN_REDIRECT_URL

**File:** `clubcms/settings/base.py`
```python
# PRIMA (errato):
LOGIN_REDIRECT_URL = "/my-profile/"
# DOPO (corretto):
LOGIN_REDIRECT_URL = "/account/profile/"
```

#### 3.4 Verifica integrazione

- [ ] **Wagtail**: template estendono `base.html` che include navbar/footer/theme
- [ ] **Multilingual**: tutti i testi in `{% trans %}`, URL con `{% url %}` i18n-compatibili
- [ ] **6 Temi**: classi `.auth-container`, `.auth-card`, `.auth-switch` in `base.css` + 6 temi
- [ ] **Sicurezza**: CSRF token presente, password validation attiva, no password in URL
- [ ] **Flusso dati**: dopo signup, ClubUser creato con campi custom, redirect corretto
- [ ] **WCAG**: aria-required, label collegati, error con role=alert

---

### FASE 4: Pagina "Diventa Socio" (Membership Plans)

#### 4.1 Test: Pagina prodotti membership

**File:** `apps/members/tests/test_membership_page.py`

```python
"""
Test per la pagina pubblica dei piani membership.
Verifica: visibilita' prodotti, pricing, CTA, link da registrazione.
"""

class TestMembershipPlansPage:
    """Pagina /become-member/ mostra i prodotti attivi."""

    def test_page_returns_200(self):
        """GET /become-member/ restituisce 200."""

    def test_page_shows_active_products(self):
        """Solo prodotti con is_active=True sono visibili."""

    def test_page_hides_inactive_products(self):
        """Prodotti con is_active=False non sono visibili."""

    def test_page_shows_prices(self):
        """Ogni prodotto mostra il prezzo."""

    def test_page_shows_product_features(self):
        """Ogni prodotto mostra le feature (voto, upload, eventi, sconto)."""

    def test_page_has_signup_cta(self):
        """Se anonimo, CTA 'Registrati' che punta a signup."""

    def test_page_has_contact_cta_for_logged_in(self):
        """Se loggato non-socio, CTA 'Contatta il club'."""

    def test_page_shows_current_plan_for_members(self):
        """Se socio, mostra piano attuale con badge 'Piano attivo'."""

    def test_page_is_multilingual(self):
        """Pagina disponibile in /it/ e /en/."""
```

#### 4.2 Implementazione

**Opzione A (consigliata):** View Django semplice con template

**File:** `apps/members/views.py` — aggiungere:
```python
class MembershipPlansView(TemplateView):
    template_name = "account/membership_plans.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.website.models.snippets import Product
        context["products"] = Product.objects.filter(is_active=True).order_by("order")
        if self.request.user.is_authenticated:
            context["user_products"] = self.request.user.products.all()
        return context
```

**File:** `apps/members/urls.py` — aggiungere:
```python
path("become-member/", views.MembershipPlansView.as_view(), name="membership_plans"),
```

**File:** `templates/account/membership_plans.html` — layout con card pricing per ogni prodotto.

#### 4.3 Verifica integrazione

- [ ] **Wagtail**: Product snippet gia' gestito via admin Wagtail
- [ ] **Multilingual**: Product.name e .description traducibili, template con `{% trans %}`
- [ ] **6 Temi**: stili `.pricing-card`, `.pricing-badge` in base.css + 6 temi
- [ ] **Sicurezza**: pagina pubblica, nessun dato sensibile esposto
- [ ] **Flusso dati**: mostra prodotti attivi, evidenzia piano corrente per soci

---

### FASE 5: Fix sicurezza dalla MASTER-PROMPT

#### 5.1 Test: Fix sicurezza

**File:** `apps/members/tests/test_security.py`

```python
"""
Test sicurezza: path traversal, rate limiting, access control.
"""

class TestQRCodePathTraversal:
    """SEC-1: QR/Barcode views non permettono path traversal."""

    def test_qr_path_inside_media_root(self):
        """Path QR valido dentro MEDIA_ROOT restituisce 200."""

    def test_qr_path_outside_media_root_returns_404(self):
        """Path con ../ restituisce 404."""

    def test_barcode_path_outside_media_root_returns_404(self):
        """Path barcode con traversal restituisce 404."""


class TestFavoritesRateLimiting:
    """SEC-2: Rate limiting favorites usa Django cache."""

    def test_toggle_favorite_once_succeeds(self):
        """Prima toggle funziona."""

    def test_toggle_favorite_rapid_returns_429(self):
        """Toggle rapido (< 1s) restituisce 429."""

    def test_rate_limit_uses_cache_not_dict(self):
        """Verifica che si usa django.core.cache, non dict."""


class TestHelperDetailAccess:
    """SEC-3: HelperDetailView richiede membro attivo."""

    def test_anonymous_redirected_to_login(self):
        """Anonimo rediretto a login."""

    def test_non_member_gets_403(self):
        """Loggato senza membership ottiene 403."""

    def test_active_member_gets_200(self):
        """Socio attivo ottiene 200."""
```

#### 5.2 Implementazione fix

**SEC-1** — `apps/members/views.py:212,241`:
```python
import os
from django.conf import settings as django_settings

def get(self, request, *args, **kwargs):
    path = ...  # existing path logic
    if not os.path.abspath(path).startswith(os.path.abspath(django_settings.MEDIA_ROOT)):
        raise Http404()
    # ... rest of view
```

**SEC-2** — `apps/events/views.py:325`:
```python
from django.core.cache import cache

# Replace _toggle_timestamps dict with:
cache_key = f"toggle_fav_{request.user.pk}"
if cache.get(cache_key):
    return JsonResponse({"error": _("Too many requests")}, status=429)
cache.set(cache_key, True, 1)
```

**SEC-3** — `apps/mutual_aid/views.py:74`:
```python
# Add to HelperDetailView
from apps.members.decorators import active_member_required
# or use mixin that checks is_active_member
```

#### 5.3 Verifica integrazione

- [ ] **Sicurezza**: tutti e 3 i fix verificati con test specifici
- [ ] **Flusso dati**: rate limiting non impatta utenti normali

---

### FASE 6: Struttura sottomenu consigliata per il Wagtail admin

Configurazione suggerita per la Navbar nel Wagtail Snippets admin:

```
Navbar Items:
├── Home                        (top-level, link_page=HomePage)
├── Chi Siamo                   (top-level, link_page=AboutPage)
├── Eventi                      (top-level, dropdown)
│   ├── Calendario              (child, link_page=EventsIndexPage)
│   ├── I miei eventi           (child, link_url=/events/my-events/)
│   └── Le mie iscrizioni       (child, link_url=/events/my-registrations/)
├── Galleria                    (top-level, link_page=GalleryPage)
├── Il Club                     (top-level, dropdown)
│   ├── Diventa socio           (child, link_url=/account/become-member/)
│   ├── Directory soci          (child, link_url=/account/directory/)
│   ├── Partner e sponsor       (child, link_page=PartnersPage)
│   └── Mutuo soccorso          (child, link_url=/mutual-aid/)
├── News                        (top-level, link_page=NewsIndexPage)
├── Contatti                    (top-level, link_page=ContactPage)
└── [User Menu]                 (automatico dal template, non da snippet)
    ├── Il mio profilo
    ├── Tessera digitale
    ├── Le mie iscrizioni
    ├── I miei eventi
    ├── [divider] ----
    ├── Privacy
    ├── Notifiche
    ├── Mutuo soccorso (settings)
    ├── [divider] ----
    └── Esci
```

---

## Parte 4: ORDINE DI ESECUZIONE

### Step 1 — Test foundation (`conftest.py`)

Creare `apps/conftest.py` con factory comuni:
- `UserFactory` (ClubUser con/senza membership)
- `NavbarFactory` (con items)
- `ProductFactory`
- `SiteSettingsFactory`

### Step 2 — Navbar dropdown (FASE 1)

1. Scrivere test `test_navbar.py`
2. Migration: aggiungere `parent` a NavbarItem
3. Implementare `top_level_items()` in Navbar
4. Aggiornare template `navbar.html`
5. Aggiungere CSS dropdown in `base.css` + 6 temi
6. Aggiungere JavaScript dropdown
7. Eseguire test
8. Verificare integrazione

### Step 3 — User menu (FASE 2)

1. Scrivere test `test_navbar_auth.py`
2. Aggiungere sezione utente in `navbar.html`
3. Aggiungere stili `.site-nav__user` in CSS
4. Eseguire test
5. Verificare integrazione

### Step 4 — Template allauth (FASE 3)

1. Scrivere test `test_auth_templates.py`
2. Creare 4+ template allauth
3. Fix `LOGIN_REDIRECT_URL`
4. Aggiungere stili `.auth-container`, `.auth-card` in CSS
5. Eseguire test
6. Verificare integrazione

### Step 5 — Pagina membership (FASE 4)

1. Scrivere test `test_membership_page.py`
2. Creare view + URL + template
3. Aggiungere stili `.pricing-card` in CSS
4. Eseguire test
5. Verificare integrazione

### Step 6 — Fix sicurezza (FASE 5)

1. Scrivere test sicurezza
2. Applicare fix SEC-1, SEC-2, SEC-3
3. Eseguire test
4. Verificare integrazione

### Step 7 — i18n strings

1. Aggiungere tutte le nuove stringhe con `{% trans %}` / `_()`
2. `makemessages -l it -l en -l de -l fr -l es`
3. `compilemessages`
4. Verificare in tutte le lingue

---

## Parte 5: FILE MAP — Tutti i file da creare/modificare

### File NUOVI da creare

| File | Scopo |
|------|-------|
| `apps/conftest.py` | Factory comuni per test |
| `apps/website/tests/__init__.py` | Package test website |
| `apps/website/tests/test_navbar.py` | Test dropdown navbar |
| `apps/website/tests/test_navbar_auth.py` | Test user menu navbar |
| `apps/members/tests/test_auth_templates.py` | Test template allauth |
| `apps/members/tests/test_membership_page.py` | Test pagina membership |
| `apps/members/tests/test_security.py` | Test fix sicurezza |
| `templates/account/signup.html` | Registrazione tematizzata |
| `templates/account/login.html` | Login tematizzato |
| `templates/account/logout.html` | Conferma logout |
| `templates/account/password_reset.html` | Reset password |
| `templates/account/password_change.html` | Cambio password |
| `templates/account/email_confirm.html` | Conferma email |
| `templates/account/membership_plans.html` | Pagina "Diventa Socio" |

### File ESISTENTI da modificare

| File | Modifica |
|------|----------|
| `apps/website/models/snippets.py` | `NavbarItem.parent` field |
| `templates/includes/navbar.html` | Dropdown + user menu + login/signup |
| `static/css/base.css` | Stili dropdown, auth, pricing |
| `static/css/themes/velocity/main.css` | Stili dropdown tema |
| `static/css/themes/heritage/main.css` | Stili dropdown tema |
| `static/css/themes/terra/main.css` | Stili dropdown tema |
| `static/css/themes/zen/main.css` | Stili dropdown tema |
| `static/css/themes/clubs/main.css` | Stili dropdown tema |
| `static/css/themes/tricolore/main.css` | Stili dropdown tema |
| `clubcms/settings/base.py` | Fix LOGIN_REDIRECT_URL |
| `apps/members/urls.py` | URL membership_plans |
| `apps/members/views.py` | MembershipPlansView + fix SEC-1 |
| `apps/events/views.py` | Fix SEC-2 (rate limiting) |
| `apps/mutual_aid/views.py` | Fix SEC-3 (access check) |

---

## Parte 6: CHECKLIST VERIFICA INTEGRAZIONE (per ogni fase)

Dopo ogni fase, eseguire questa checklist:

### Wagtail
- [ ] Snippet admin funziona (navbar con dropdown, prodotti)
- [ ] Page admin funziona (nessun regression)
- [ ] SiteSettings seleziona navbar correttamente

### Multilingual
- [ ] Tutte le stringhe in `{% trans %}` o `_()`
- [ ] URL con `{% url %}` rispettano i18n_patterns
- [ ] `makemessages` genera stringhe per tutte le lingue
- [ ] `compilemessages` compila senza errori
- [ ] Pagine accessibili con prefisso /it/, /en/, /de/, /fr/, /es/

### Temi (6)
- [ ] CSS strutturali in `base.css`
- [ ] CSS estetici in tutti e 6 `themes/{name}/main.css`
- [ ] Verificare rendering almeno su Velocity + Clubs (chiaro e scuro)
- [ ] Dark mode: override presenti

### Sicurezza
- [ ] View protette con `LoginRequiredMixin` dove necessario
- [ ] CSRF token in tutti i form POST
- [ ] Nessun dato personale esposto senza controllo ruolo
- [ ] Path file validati contro MEDIA_ROOT
- [ ] Rate limiting con Django cache (non dict in-memory)

### Flusso dati
- [ ] Matrice visibilita' rispettata (da MASTER-PROMPT sezione 4)
- [ ] `get_visible_name(viewer)` usato per nomi
- [ ] Email mai esposta in template pubblici
- [ ] Permessi derivati da prodotti membership

### Test
- [ ] `pytest apps/ -v` passa al 100%
- [ ] Nessun test skippato senza motivo
- [ ] Coverage delle nuove feature

### WCAG
- [ ] aria-expanded, aria-haspopup su dropdown
- [ ] role=menu, role=menuitem su submenu
- [ ] aria-required su campi obbligatori
- [ ] Label collegati ai campi
- [ ] Navigazione keyboard (Tab, Escape, Enter)
- [ ] Skip-link presente (gia' in base.html)
