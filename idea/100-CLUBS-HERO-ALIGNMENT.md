# 100 — Allineamento Home Page Clubs: Copertina e Sezioni

## Obiettivo

Allineare la home page del progetto ClubCMS al template di riferimento **Clubs** (`theme_examples/clubs/index.html`), con focus sulla **copertina (hero)** e sulle sezioni mancanti. Tutte le modifiche devono rispettare l'architettura multilingua del progetto (i18n con `{% trans %}` / `{% blocktrans %}`).

---

## 1. Differenze nella Copertina (Hero)

### 1.1 Badge/Pre-titolo mancante nella HomePage

**Template di riferimento** (riga 44):
```html
<p class="text-red font-bold uppercase tracking-[0.3em] mb-4">Since 1985</p>
```

**Progetto attuale** — `home_page.html`:
Il template della HomePage usa direttamente i campi `hero_title` e `hero_subtitle`, ma **non ha un campo badge/pre-titolo** (es. "Since 1985").

Il blocco `hero_banner_block.html` supporta già `self.badge` con la classe `.block-hero-banner__badge`, e il CSS Clubs lo stila correttamente (riga 383 di `main.css`).

**Problema**: Il modello `HomePage` (`apps/website/models/pages.py` riga 67) non ha un campo `hero_badge`.

**Soluzione proposta**:

| File | Modifica |
|------|----------|
| `apps/website/models/pages.py` | Aggiungere `hero_badge = models.CharField(max_length=120, blank=True, verbose_name=_("Hero badge"), help_text=_("Pre-title text displayed above hero title, e.g. 'Since 1985'."))` |
| `apps/website/models/pages.py` | Aggiungere `FieldPanel("hero_badge")` nel `MultiFieldPanel` "Hero section" |
| `templates/website/pages/home_page.html` | Aggiungere rendering del badge prima di `<h1>` |
| Migrazione | `python manage.py makemigrations website && python manage.py migrate` |

**Aggiornamento template** (`home_page.html`, dentro `block-hero-banner__content`):
```django-html
{% if page.hero_badge %}
    <span class="block-hero-banner__badge">{{ page.hero_badge }}</span>
{% endif %}
```

**Traduzioni**: Il valore del badge è inserito dall'admin (campo CharField), quindi è automaticamente gestito dal sistema di traduzione delle pagine Wagtail (wagtail-localize). Non serve tag `{% trans %}`.

---

### 1.2 Scroll Indicator (freccia animata in basso) mancante

**Template di riferimento** (riga 51-53):
```html
<div class="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce">
  <svg ...>...</svg>
</div>
```

**Progetto attuale**: Nessun indicatore di scroll nella homepage hero.

**Soluzione proposta**:

| File | Modifica |
|------|----------|
| `templates/website/pages/home_page.html` | Aggiungere SVG freccia dopo `block-hero-banner__content` |
| `static/css/themes/clubs/main.css` | Aggiungere classi `.block-hero-banner__scroll-indicator` e `@keyframes bounce` |

**CSS da aggiungere** (in `main.css` dopo il blocco hero, ~riga 475):
```css
/* Scroll indicator */
.block-hero-banner__scroll-indicator {
  position: absolute;
  bottom: 2.5rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 3;
  animation: hero-bounce 2s infinite;
  opacity: 0.7;
  transition: opacity var(--clubs-transition);
}

.block-hero-banner__scroll-indicator:hover {
  opacity: 1;
}

.block-hero-banner__scroll-indicator svg {
  width: 24px;
  height: 24px;
  stroke: #fff;
  fill: none;
}

@keyframes hero-bounce {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50% { transform: translateX(-50%) translateY(10px); }
}
```

**Template HTML** (dentro `<section class="block-hero-banner">`):
```django-html
<div class="block-hero-banner__scroll-indicator" aria-hidden="true">
    <svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M19 14l-7 7m0 0l-7-7m7 7V3"/>
    </svg>
</div>
```

---

### 1.3 Overlay gradient differente

**Template di riferimento**:
```html
<div class="absolute inset-0 bg-gradient-to-b from-[#0A0A0A]/80 via-[#0A0A0A]/50 to-[#0A0A0A]"></div>
```
Gradient a 3 stop: 80% in alto → 50% centro → 100% in basso.

**Progetto attuale** (`main.css` riga 402):
```css
background: linear-gradient(to bottom,
    rgba(10, 10, 10, 0.8) 0%,
    rgba(10, 10, 10, 0.5) 50%,
    rgba(10, 10, 10, 1) 100%
);
```

**Stato**: ✅ **Già allineato**. Nessuna modifica necessaria.

---

### 1.4 Tipografia Hero

**Template di riferimento**: `text-5xl md:text-7xl font-black uppercase` → circa `3rem / 4.5rem`, `font-weight: 900`.

**Progetto attuale** (`main.css` riga 418):
```css
font-size: clamp(2.5rem, 8vw, 6rem);
font-weight: 900;
text-transform: uppercase;
```

**Stato**: ✅ **Coerente** (responsive con clamp). Nessuna modifica necessaria.

---

## 2. Sezioni mancanti nella Home Page

La home page del template Clubs ha **8 sezioni**. Il progetto attualmente ne gestisce **3** (Hero, Upcoming Events, Body StreamField). Le sezioni mancanti possono essere aggiunte come blocchi StreamField nel body.

### 2.1 Sezione Stats (già disponibile come blocco)

**Template di riferimento**: Barra con 4 statistiche (anni di storia, membri, eventi, capitoli regionali).

**Progetto**: Il blocco `StatsBlock` e la classe CSS `.block-stats` sono già presenti e stilati nel CSS Clubs.

**Azione**: Nessuna modifica al codice. **Solo documentazione/guida admin**: aggiungere un blocco Stats nel body della HomePage dal pannello Wagtail.

---

### 2.2 Sezione Heritage/About Preview (già possibile)

**Template di riferimento**: Sezione a 2 colonne con testo + immagine + badge anno fondazione.

**Progetto**: Il blocco `TwoColumnBlock` con RichText + Image block permette di replicare questa sezione.

**Azione**: Nessuna modifica al codice. Guida admin.

---

### 2.3 Gallery Preview (non disponibile come sezione della home)

**Template di riferimento** (riga ~130-175): Griglia asimmetrica con 6 foto, hover overlay con caption, link "View Full Gallery".

**Progetto**: Il blocco `GalleryBlock` esiste, ma non produce un layout asimmetrico (4 colonne con 1 large).

**Soluzione proposta**: Aggiungere un attributo `data-layout` al blocco Gallery per supportare il layout "masonry" o "featured" usato nella home.

| File | Modifica |
|------|----------|
| `static/css/themes/clubs/main.css` | Aggiungere variante `.block-gallery[data-layout="featured"]` con layout griglia asimmetrica |

```css
/* Gallery featured layout (home preview) */
.block-gallery[data-layout="featured"] .block-gallery__grid {
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: auto auto;
}

.block-gallery[data-layout="featured"] .block-gallery__item:first-child {
  grid-column: span 2;
  grid-row: span 2;
}

.block-gallery[data-layout="featured"] .block-gallery__item img {
  height: 100%;
}
```

---

### 2.4 Partners/Sponsors (non disponibile)

**Template di riferimento** (riga ~178-230): Griglia 6 card partner con nome e tipo.

**Progetto**: Non esiste un blocco Partner/Sponsor.

**Soluzione proposta**: Creare un nuovo blocco `PartnersGridBlock`.

| File | Modifica |
|------|----------|
| `apps/website/blocks/content.py` | Aggiungere `PartnerBlock` e `PartnersGridBlock` |
| `apps/website/blocks/__init__.py` | Esportare e includere in `CONTENT_BLOCKS` e `HOME_BLOCKS` |
| `templates/website/blocks/partners_grid_block.html` | Nuovo template |
| `static/css/themes/clubs/main.css` | Aggiungere stili `.block-partners-grid` |

**Impatto multilingua**: I campi del blocco usano `label=_("...")` per le etichette nel pannello admin. Il contenuto (nomi partner) è inserito nell'admin ed è coperto dalla localizzazione pagine Wagtail.

---

### 2.5 CTA Membership (già disponibile)

**Template di riferimento** (riga ~235): Sezione full-width rosso con CTA "Become a Member".

**Progetto**: Il blocco `CTABlock` con `data-style="primary"` produce esattamente questo risultato.

**Azione**: Nessuna modifica al codice.

---

### 2.6 Newsletter Signup (già disponibile)

**Template di riferimento** (riga ~244-254): Form email + pulsante "Subscribe".

**Progetto**: Il blocco `NewsletterSignupBlock` e le classi CSS `.block-newsletter-signup` sono già implementati.

**Azione**: Nessuna modifica al codice.

---

## 3. Impatto Traduzioni (i18n)

### 3.1 Nuovi campi modello HomePage

| Campo | Tipo | Gestione traduzione |
|-------|------|---------------------|
| `hero_badge` | CharField | Wagtail-localize (traduzione pagina) |

Nessun nuovo tag `{% trans %}` necessario nel template, perché il contenuto viene dall'admin.

### 3.2 Testo statico nel template

Il template `home_page.html` contiene un fallback:
```django-html
{{ page.events_section_title|default:"Upcoming Events" }}
```

Questo **non** è avvolto in `{% trans %}`. Si dovrebbe correggere:

```django-html
{% trans "Upcoming Events" as default_events_title %}
{{ page.events_section_title|default:default_events_title }}
```

**File da aggiornare per le traduzioni**:

| File locale | Stringa da aggiungere |
|-------------|----------------------|
| `locale/it/LC_MESSAGES/django.po` | `"Upcoming Events"` → `"Prossimi Eventi"` |
| `locale/de/LC_MESSAGES/django.po` | `"Upcoming Events"` → `"Kommende Veranstaltungen"` |
| `locale/es/LC_MESSAGES/django.po` | `"Upcoming Events"` → `"Próximos Eventos"` |
| `locale/fr/LC_MESSAGES/django.po` | `"Upcoming Events"` → `"Événements à Venir"` |

Inoltre le nuove label del modello:

| Stringa | it | de | es | fr |
|---------|----|----|----|----|
| `"Hero badge"` | `"Badge hero"` | `"Hero-Badge"` | `"Insignia hero"` | `"Badge hero"` |
| `"Pre-title text displayed above hero title, e.g. 'Since 1985'."` | `"Testo pre-titolo visualizzato sopra il titolo hero, es. 'Dal 1985'."` | `"Vortext über dem Hero-Titel, z.B. 'Seit 1985'."` | `"Texto previo al título hero, ej. 'Desde 1985'."` | `"Texte pré-titre affiché au-dessus du titre hero, ex. 'Depuis 1985'."` |

### 3.3 Nuovo blocco PartnersGrid (se implementato)

Le label del blocco devono usare `gettext_lazy`:
```python
from django.utils.translation import gettext_lazy as _

class PartnerBlock(StructBlock):
    name = CharBlock(label=_("Partner name"))
    description = CharBlock(label=_("Description"), required=False)
    logo = ImageChooserBlock(label=_("Logo"), required=False)
    url = URLBlock(label=_("Website URL"), required=False)
```

---

## 4. Riepilogo Interventi

### Priorità ALTA (differenze visive copertina)

| # | Intervento | File coinvolti | Migrazione DB |
|---|-----------|----------------|---------------|
| 1 | Aggiungere campo `hero_badge` al modello `HomePage` | `models/pages.py` | ✅ Sì |
| 2 | Rendere il badge nel template home | `home_page.html` | No |
| 3 | Aggiungere scroll indicator (CSS + HTML) | `main.css`, `home_page.html` | No |
| 4 | Correggere fallback `"Upcoming Events"` con `{% trans %}` | `home_page.html` | No |
| 5 | Aggiornare file `.po` per le nuove stringhe | `locale/*/django.po` | No (solo `compilemessages`) |

### Priorità MEDIA (sezioni mancanti)

| # | Intervento | File coinvolti | Migrazione DB |
|---|-----------|----------------|---------------|
| 6 | Aggiungere layout "featured" per Gallery nella home | `main.css` | No |
| 7 | Creare blocco `PartnersGridBlock` | `blocks/content.py`, `__init__.py`, template, CSS | No |

### Priorità BASSA (guida admin)

| # | Intervento | Note |
|---|-----------|------|
| 8 | Documentare uso blocchi Stats nella home | Solo manuale |
| 9 | Documentare uso CTABlock "primary" per membership | Solo manuale |
| 10 | Documentare uso NewsletterSignupBlock | Solo manuale |

---

## 5. Comandi da eseguire dopo le modifiche

```bash
# 1. Migrazione per hero_badge
cd clubcms
python manage.py makemigrations website
python manage.py migrate

# 2. Aggiornare file traduzioni
python manage.py makemessages -l it -l de -l es -l fr -l en
# Tradurre le nuove stringhe nei file .po
python manage.py compilemessages

# 3. Raccogliere static files (se in produzione)
python manage.py collectstatic --noinput
```

---

## 6. Note di compatibilità

- **Tutti i temi**: Lo scroll indicator e il badge hero usano classi CSS prefissate con `.block-hero-banner__`. Se altri temi vogliono supportarli, basta aggiungere le classi CSS corrispondenti nel loro `main.css`. Attualmente il badge è già stilato in tutti i 6 temi.
- **Retrocompatibilità**: Il campo `hero_badge` è `blank=True`, quindi le home page esistenti non vengono impattate. Lo scroll indicator è puro CSS/HTML senza dipendenze JS.
- **Accessibilità**: Lo scroll indicator ha `aria-hidden="true"` perché è puramente decorativo. Il badge hero è testo semantico, quindi leggibile dagli screen reader.
