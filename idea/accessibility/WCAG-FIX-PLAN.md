# Piano di Lavoro — Fix WCAG 2.1 AA (Tutte le Pagine)

> Basato su: `first-test-results.txt` (tema **Tricolore**) + audit completo template
> Data: 2026-03-22

---

## Riepilogo Errori

| Tipo    | Criterio WCAG            | Occorrenze | Dove intervenire          |
|---------|--------------------------|:----------:|---------------------------|
| ERROR   | SC 2.4.7 – Focus Indicator | 2        | `base.css` + 6 temi       |
| ERROR   | SC 1.4.3 – Contrasto testo | 14       | 6 temi (colori specifici)  |
| ERROR   | SC 1.1.1 – ARIA label SVG  | 3        | `navbar.html`, `home_page.html` |
| WARNING | SC 1.3.1/2.4.1 – Landmarks | 4        | `base.html`, `navbar.html` |
| WARNING | SC 2.5.3 – Nome accessibile | ~40      | Template (false positivi + veri) |
| WARNING | SC 4.1.2 – ARIA state      | ~12      | `navbar.html`             |
| WARNING | SC 1.4.12 – Line spacing   | ~12      | `base.css`                |
| WARNING | SC 1.4.4/1.4.12 – Em units | 3        | `base.css`                |
| WARNING | SC 4.1.3 – Status message  | 1        | `navbar.html`             |
| WARNING | SC 1.1.1/1.2.1 – Alt text  | 1        | `home_page.html`          |

---

## Fase 1 — Fix Strutturali (base.css + template)

Questi fix si applicano una volta e risolvono il problema per tutti i temi.

### 1.1 Focus Indicator Potenziato ⬤ ERROR SC 2.4.7
**File**: `base.css`
**Problema**: L'outline `:focus-visible` attuale (`3px solid var(--color-accent)`) potrebbe non essere
sufficientemente visibile su tutti i temi perché `--color-accent` può avere basso contrasto sullo sfondo.
**Fix**:
```css
:focus-visible {
  outline: 3px solid var(--color-accent, #0066FF);
  outline-offset: 2px;
  box-shadow: 0 0 0 6px rgba(0, 102, 255, 0.25); /* doppio ring per visibilità */
}
```
**Impatto temi**: Nessun tema ha un override — il fix in `base.css` basta.
Ma serve verifica che `--color-accent` abbia almeno 3:1 di contrasto con lo sfondo in ogni tema:

| Tema       | --color-accent | Sfondo nav  | Contrasto stimato | OK? |
|------------|---------------|-------------|:-----------------:|:---:|
| Tricolore  | `#C9A227`     | `#FFFFFF`   | ~2.2:1 ⚠️        | NO  |
| Velocity   | `#8B5CF6`     | dark navy   | ~4.5:1            | SI  |
| Heritage   | `#8B1538`     | `#1E3A5F`   | ~3.1:1 ⚠️        | NO  |
| Terra      | `#F2C94C`     | `#2D3B2D`   | ~6.5:1            | SI  |
| Zen        | `#FF3366`     | `#0a0a0a`   | ~4.5:1            | SI  |
| Clubs      | `#E02547`     | dark bg     | ~4.5:1            | SI  |

**Azione**: I temi con contrasto insufficiente dell'accent (Tricolore, Heritage) devono definire
una variabile `--color-focus-ring` più scura nei rispettivi `main.css`.

### 1.2 Line Spacing (line-height) ⬤ WARNING SC 1.4.12
**File**: `base.css`
**Problema**: `line-height: 1` su `.page-home__spotlight-stat-value` e `.home-partners__card-initial`.
WCAG 1.4.12 raccomanda `line-height` >= 1.5× per testo corpo.
**Fix**: Portare a `line-height: 1.1` per valori grossi (numeri stats) e `line-height: 1.15` per iniziali partner.
Anche `.home-partners__card-name` (`line-height: 1.25` → `1.4`).
**Impatto temi**: Nessuno, è tutto in `base.css`.

### 1.3 Em Units per Contenitori Testo ⬤ WARNING SC 1.4.4/1.4.12
**File**: `base.css`
**Problema**: `.home-partners__card-initial` usa `width/height: 56px` (fisso) e `.home-partners__card-visual`
usa `min-height: 100px`.
**Fix**: Convertire a `em`:
- `.home-partners__card-initial`: `width: 3.5em; height: 3.5em;`
- `.home-partners__card-visual`: `min-height: 6.25em;`

### 1.4 SVG Accessible Names ⬤ ERROR SC 1.1.1 (ARIA6)
**File**: `navbar.html`
**Problema**: 3 SVG icon-only senza `<title>` interno — il tool segnala che `aria-label` sul parent
non basta perché l'SVG stesso non ha label accessibile.
**Fix**: Aggiungere `<title>` dentro ogni `<svg>`:
- Search toggle SVG → `<title>{% trans "Cerca" %}</title>`
- Search submit SVG → `<title>{% trans "Cerca" %}</title>`

**File**: `home_page.html`
- Scroll indicator SVG → è `aria-hidden="true"` e il contenitore ha `aria-hidden="true"`,
  quindi è un **falso positivo** — nessun fix necessario.

### 1.5 Landmarks HTML5 ⬤ WARNING SC 1.3.1/2.4.1
**File**: `base.html`, `navbar.html`, `footer.html`
**Problema**: Landmark ridondanti (`role="navigation"` su `<nav>`, `role="contentinfo"` su `<footer>`).
Il checker avvisa che dovrebbe esserci una struttura completa con `<header>`.
**Fix**:
- Rimuovere `role="navigation"` da `<nav>` (implicito in HTML5)
- Rimuovere `role="contentinfo"` da `<footer>` (implicito in HTML5)
- Wrappare la `<nav>` in un `<header>` semantico (se non presente)
- Assicurarsi che `<main>` abbia `role="main"` solo se necessario per AT legacy (opzionale)

### 1.6 Menuitem States ⬤ WARNING SC 4.1.2
**File**: `navbar.html`
**Problema**: I link con `role="menuitem"` non hanno stato corrente (`aria-current="page"`).
**Fix**: Aggiungere `aria-current="page"` al menuitem attivo tramite template logic:
```html
<a href="{{ child.url }}" role="menuitem"
   {% if child.url == request.path %}aria-current="page"{% endif %}>
```

### 1.7 Status Message per Ricerca ⬤ WARNING SC 4.1.3
**File**: `navbar.html`
**Problema**: Dopo submit del form di ricerca, manca un `role="status"` per notificare AT.
**Fix**: Aggiungere un `<div role="status" aria-live="polite" class="sr-only">` vicino al form
che venga popolato con JS dopo submit (o redirect — in quel caso è un falso positivo perché
la pagina dei risultati ha il suo heading).
**Priorità**: Bassa — la ricerca fa redirect a `/cerca/` con heading risultati.

### 1.8 Hero Alt Text ⬤ WARNING SC 1.1.1/1.2.1
**File**: `home_page.html`
**Problema**: L'immagine hero ha `alt=""` — corretto se decorativa, ma il checker la segnala.
**Fix**: L'immagine hero È decorativa (il testo è nell'overlay panel) → `alt=""` è **corretto**.
Tuttavia, se l'immagine ha valore informativo, usare il campo `alt` dal model Wagtail:
```html
alt="{{ self.hero_image.title }}"
```

---

## Fase 2 — Fix Contrasto per Tema ⬤ ERROR SC 1.4.3

Questi sono gli errori più gravi e numerosi. Ogni tema ha le sue combinazioni colore.
L'analisi è basata sul requisito WCAG AA: **4.5:1 per testo normale, 3:1 per testo grande (≥18pt bold / ≥24pt)**.

### Aree con errori di contrasto rilevati:

| Area                          | Selettore CSS                          | Rilevante per |
|-------------------------------|----------------------------------------|---------------|
| A. Nav dropdown text          | `.site-nav__dropdown-toggle`            | Tutti i temi  |
| B. Hero title/subtitle        | `.block-hero-banner__title/subtitle`    | Tutti i temi  |
| C. Partner card initials      | `.home-partners__card-initial`          | Tutti i temi  |
| D. Spotlight stat values      | `.page-home__spotlight-stat-value`      | Tutti i temi  |
| E. CTA title/text/button      | `.page-home__spotlight-cta-*`           | Tutti i temi  |
| F. Footer heading/text        | `.site-footer__heading`, `.site-footer__about` | Tutti i temi |

---

### TRICOLORE 🇮🇹

| Area | Foreground | Background | Ratio stimato | Minimo | Fix proposto |
|------|-----------|------------|:-------------:|:------:|--------------|
| A. Nav dropdown | `#1a1a1a` su `#FFFFFF` | **12.6:1** ✅ | 4.5:1 | — Ma l'errore è sulla freccia `▾`: potrebbe essere piccola e grigia. Verificare che `.site-nav__dropdown-arrow` erediti il colore testo scuro. |
| B. Hero title | `#fff` su overlay verde `rgba(0,146,70,0.75)` | ~3.8:1 ⚠️ | 4.5:1 | Aumentare opacità overlay a 0.85 o aggiungere `text-shadow` |
| B. Hero subtitle | `#fff` su overlay verde | ~3.8:1 ⚠️ | 4.5:1 | Idem |
| C. Partner initial | `#fff` su `#009246` (green) | ~3.9:1 ⚠️ | 3:1 (large) ✅ | Testo grande (1.5rem bold) → passa 3:1 ma non 4.5:1. Se <18pt bold, scurire `--color-primary` a `#007B3D`. |
| D. Stat value | `#1a1a1a` su `#F4F5F0` | ~14.5:1 ✅ | 4.5:1 | OK, ma il checker potrebbe vedere un bg diverso dal CTA box. Verificare colore bg effettivo. |
| E. CTA block | Testo su `data-style="primary"` bg | ⚠️ dipende dal tema | 4.5:1 | Il CTA box usa `background: var(--color-primary)` → `#009246` con testo bianco → ~3.9:1. Scurire bg a `#007B3D` o usare testo `#FFFFFF` con text-shadow. |
| F. Footer | Testo `#ccc`/`#aaa` su `#1a1a1a` | ~10:1 ✅ | 4.5:1 | Verificare heading e about text. Se heading è `#C9A227` (oro) su `#1a1a1a` → ~5.4:1 ✅ |

**Azioni Tricolore**:
1. Overlay hero: opacità `0.85` (o `text-shadow: 0 2px 8px rgba(0,0,0,0.6)`)
2. CTA block: scurire bg primary o aggiungere text-shadow
3. Partner initial: OK se >18pt bold, altrimenti scurire primary

---

### VELOCITY ⚡

| Area | Foreground | Background | Ratio | Fix |
|------|-----------|------------|:-----:|-----|
| A. Nav | `#fff` su `rgba(15,23,42,0.95)` | ~15:1 ✅ | — |
| B. Hero | `#fff` su `rgba(15,23,42,0.7)` | ~8:1 ✅ | Ha text-shadow amber → OK |
| C. Partner initial | `#fff` su `#0F172A` | ~16:1 ✅ | — |
| D. Stat value | `#111` su `#F8FAFC` | ~18:1 ✅ | — |
| E. CTA | `#fff` su `#0F172A` | ~16:1 ✅ | — |
| F. Footer | `#fff/#ccc` su `#0F172A` | ~11:1+ ✅ | — |

**Velocity**: ✅ Nessun fix contrasto necessario.

---

### HERITAGE 🏛️

| Area | Foreground | Background | Ratio | Fix |
|------|-----------|------------|:-----:|-----|
| A. Nav | `#fff` su `#1E3A5F` | ~8.5:1 ✅ | — |
| B. Hero | `#fff` su `rgba(30,58,95,0.5)` | ~3.5:1 ⚠️ | Aumentare opacità overlay a 0.7+ |
| C. Partner initial | `#fff` su `#1E3A5F` | ~8.5:1 ✅ | — |
| D. Stat value | `#1a1a1a` su `#FDFCF7` | ~15:1 ✅ | — |
| E. CTA | `#fff` su `#1E3A5F` | ~8.5:1 ✅ | — |
| F. Footer | testo chiaro su `#1E3A5F` | ~8:1+ ✅ | — |

**Azioni Heritage**:
1. Overlay hero: da `0.5` a `0.7`

---

### TERRA 🌿

| Area | Foreground | Background | Ratio | Fix |
|------|-----------|------------|:-----:|-----|
| A. Nav | `#fff` su `#2D3B2D` | ~9.5:1 ✅ | — |
| B. Hero | `#fff` su overlay `rgba(45,80,22,0.88)` | ~6:1+ ✅ | Già alto → OK |
| C. Partner initial | `#fff` su `#2D3B2D` | ~9.5:1 ✅ | — |
| D. Stat value | `#1a1a1a` su `#E8DFD0` | ~11:1 ✅ | — |
| E. CTA | `#fff` su `#2D3B2D` | ~9.5:1 ✅ | — |
| F. Footer | testo chiaro su scuro | ✅ | — |

**Terra**: ✅ Nessun fix contrasto necessario.

---

### ZEN 🖤

| Area | Foreground | Background | Ratio | Fix |
|------|-----------|------------|:-----:|-----|
| A. Nav | `#fff` su `#0a0a0a` | ~19:1 ✅ | — |
| B. Hero | `#0a0a0a` su white box | ~19:1 ✅ | No overlay, content box bianco |
| C. Partner initial | `#fff` su `#0a0a0a` | ~19:1 ✅ | — |
| D. Stat value | `#0a0a0a` su `#FFFFFF` | ~19:1 ✅ | — |
| E. CTA | `#0a0a0a` o `#fff` su box | ✅ | Dipende dal data-style, verificare |
| F. Footer | `#0a0a0a` su `#FFFFFF` | ~19:1 ✅ | — |

**Zen**: ✅ Probabilmente nessun fix necessario. Verificare CTA.

---

### CLUBS 🏴

| Area | Foreground | Background | Ratio | Fix |
|------|-----------|------------|:-----:|-----|
| A. Nav | `#fff` su `rgba(10,10,10,0.95)` | ~19:1 ✅ | — |
| B. Hero | `#fff` su `rgba(10,10,10,0.8)` | ~14:1 ✅ | — |
| C. Partner initial | `#fff` su `#0A0A0A` | ~19:1 ✅ | — |
| D. Stat value | `#fff` su `#0A0A0A` | ~19:1 ✅ | — |
| E. CTA | `#fff` su `#C41E3A`? | ~4.6:1 ✅ | Borderline — verificare |
| F. Footer | `#fff` su `#0A0A0A` | ~19:1 ✅ | Heading color? `#A0A0A0`→4.6:1 ✅ |

**Clubs**: ✅ Probabilmente OK. Verificare CTA button se usa rosso su sfondo scuro.

---

## Fase 3 — Focus Ring per Tema

Per i temi dove `--color-accent` ha basso contrasto sullo sfondo nav/page:

| Tema       | Fix nel `main.css` del tema |
|------------|----------------------------|
| Tricolore  | `--color-focus-ring: #7A6310;` (oro scuro) oppure usare outline doppia |
| Heritage   | `--color-focus-ring: #5E1028;` (burgundy scuro) |

Poi in `base.css`: `outline-color: var(--color-focus-ring, var(--color-accent, #0066FF));`

---

## Riepilogo Azioni per File

### `base.css` (strutturale — tutti i temi)
- [ ] Focus ring potenziato con `box-shadow` doppio ring
- [ ] `line-height` stats/partner portato a ≥1.1
- [ ] Dimensioni `em` per container partner
- [ ] Variabile `--color-focus-ring` con fallback

### Template HTML
- [ ] `navbar.html`: `<title>` in SVG ricerca; rimuovere `role` ridondanti; `aria-current="page"` su menuitem attivo
- [ ] `base.html`: wrappare nav in `<header>` se mancante
- [ ] `footer.html`: rimuovere `role="contentinfo"`
- [ ] `home_page.html`: verificare hero `alt` (probabilmente OK come decorativa)

### `themes/tricolore/main.css`
- [ ] Overlay hero: opacità da 0.75 → 0.85 + text-shadow
- [ ] CTA block: scurire bg o aggiungere testo con ombra
- [ ] Aggiungere `--color-focus-ring` se accent non passa 3:1

### `themes/heritage/main.css`
- [ ] Overlay hero: opacità da 0.5 → 0.7

### `themes/velocity/main.css`
- ✅ Nessun fix necessario

### `themes/terra/main.css`
- ✅ Nessun fix necessario

### `themes/zen/main.css`
- [ ] Verificare CTA `data-style="primary"` contrasto

### `themes/clubs/main.css`
- [ ] Verificare CTA contrasto (borderline)

---

## Priorità di Esecuzione

1. **P0 — Errori contrasto** (SC 1.4.3): Tricolore hero + CTA, Heritage hero → impatto diretto utente
2. **P0 — Focus indicator** (SC 2.4.7): base.css + Tricolore/Heritage focus ring → requisito tastiera
3. **P1 — SVG labels** (SC 1.1.1): navbar.html → 3 elementi
4. **P1 — Landmarks** (SC 1.3.1): template structure cleanup
5. **P2 — Line spacing** (SC 1.4.12): base.css tweaks
6. **P2 — Menuitem states** (SC 4.1.2): navbar.html
7. **P3 — Em units, status message, alt text**: minor fixes

---

## Stima Impatto

- **File da modificare**: ~8
- **Temi che richiedono fix CSS**: 2 (Tricolore, Heritage) + 2 da verificare (Zen, Clubs)
- **Temi senza problemi**: 2 (Velocity, Terra)
- **Errori da eliminare**: ~19 (14 contrasto + 2 focus + 3 SVG)
- **Warning da ridurre**: ~70 (molti sono falsi positivi SC 2.5.3 su div senza contenuto interattivo)

---

## Fase 4 — Audit Pagine Listing, Ricerca e Dettaglio

Analisi estesa a **tutte le pagine** oltre la homepage. Risultato: la struttura a11y dei
template secondari è **generalmente buona**, con pochi problemi aggiuntivi rispetto alla homepage.

### 4.0 Riepilogo Template Analizzati

| Template | Landmarks | ARIA | Alt img | SVG | Contrasto | Note |
|----------|:---------:|:----:|:-------:|:---:|:---------:|------|
| `events_page.html` | ✅ | ✅ tablist/tab | ✅ | — | ⚠️ 1 issue | CTA button |
| `event_detail_page.html` | ✅ region+aside | ✅✅ | ✅ | ✅ | ✅ | Ottimo |
| `news_index_page.html` | ✅ | ✅ | ✅ | — | ✅ | OK |
| `news_page.html` | ✅ article | ✅ | ✅ | — | ✅ | OK |
| `search_results.html` | ✅ | ⚠️ 2 issue | — | — | ⚠️ 1 issue | Tab semantics + label |
| `gallery_page.html` | ✅ | ✅ lightbox | ✅ figure | — | ✅ | OK |
| `partner_index_page.html` | ✅ | ✅ | ✅ | — | ⚠️ stessa home | Initial card |
| `partner_page.html` | ✅ region+aside | ✅✅ | ✅ | — | ✅ | Ottimo |
| `my_events.html` | ✅ | ✅✅ | — | ✅ | ✅ | Ottimo |
| `pagination.html` | ✅ nav | ✅ current/disabled | — | — | ✅ | Ottimo |
| `breadcrumbs.html` | ✅ nav | ✅ Schema.org | — | — | ✅ | Ottimo |
| `footer.html` | ✅ | ✅ | — | ✅ | ⚠️ 2 issue | Heading + about |

### 4.1 Nuovo problema: Event Card CTA Button ⬤ ERROR SC 1.4.3
**File**: `base.css`
**Problema**: `.event-card__cta` usa `color: var(--color-primary)` su `background: var(--color-secondary)`.
Nel tema Tricolore questo è verde `#009246` su rosso `#CE2B37` → **rapporto 1.29:1 — FAIL grave**.
Il tema Tricolore ha già un fix locale (`color: #fff`), ma il default in `base.css` è pericoloso
per qualsiasi tema dove primary e secondary sono cromaticamente vicini.
**Fix**: In `base.css`, cambiare il default a `color: #fff` (bianco su sfondo colorato è più sicuro).
**Impatto**: Tutti i temi — ma Velocity/Heritage/Terra/Zen/Clubs usano combinazioni safe.

### 4.2 Search Results — Tab Semantics ⬤ WARNING SC 4.1.2
**File**: `search_results.html`
**Problema**: I filtri per tipo risultato usano `role="tablist"` con `aria-label="Result type"`,
ma i singoli tab sono `<a>` link (non `<button>` con `role="tab"`). Un link dentro un tablist
non è semanticamente corretto.
**Fix**: Cambiare i link in `<button role="tab" aria-selected="true/false">` oppure rimuovere
`role="tablist"` e usare semplicemente `role="navigation"` con link (pattern più semplice).
**Priorità**: P2

### 4.3 Search Results — Per-page Label ⬤ WARNING SC 1.3.1
**File**: `search_results.html`
**Problema**: Il selettore "risultati per pagina" non ha un `<label>` associato chiaramente.
**Fix**: Aggiungere `<label for="per-page-select" class="sr-only">{% trans "Results per page" %}</label>`.
**Priorità**: P3

### 4.4 Gallery Block — Alt Text Vuoto ⬤ WARNING SC 1.1.1
**File**: `gallery_block.html`
**Problema**: `alt="{{ item.value.caption|default:'' }}"` — se nessuna caption, `alt=""` rende
l'immagine decorativa. Per una galleria fotografica, le immagini hanno valore informativo.
**Fix**: Usare `alt="{{ item.value.caption|default:item.value.image.title }}"` come fallback
al titolo dell'immagine Wagtail.
**Priorità**: P2

### 4.5 Gallery Lightbox — Focus Trap ⬤ WARNING SC 2.4.3
**File**: `gallery_page.html`
**Problema**: Il lightbox modal ha `role="dialog" aria-modal="true"` ma potrebbe non avere
un focus trap completo (il codice JS va verificato).
**Fix**: Assicurarsi che il focus resti nel dialog quando aperto, e che Escape chiuda + restituisca
focus all'elemento che ha aperto il lightbox.
**Priorità**: P2

### 4.6 Partner Index — Stessi problemi della Homepage
**File**: `partner_index_page.html` + `base.css`
**Problema**: Le card partner con `.partner-card__initial` hanno lo stesso problema di contrasto
della homepage (testo su `--color-primary` background).
**Fix**: Già coperto dal fix 1.3 / Fase 2 (partner initial). Nessuna azione aggiuntiva.

### 4.7 Event Page — Hero Subtitle Opacity ⬤ WARNING SC 1.4.3
**File**: `base.css`
**Problema**: `.page-events__hero-subtitle` usa `rgba(255,255,255,0.8)` su `var(--color-primary)`.
L'80% opacity del bianco riduce il contrasto.
Per Tricolore: `rgba(255,255,255,0.8)` ≈ `#CCE0D4` su `#009246` → ~2.7:1 ⚠️
Per Heritage: su `#1E3A5F` → ~5.5:1 ✅
**Fix**: Portare a `rgba(255,255,255,0.9)` o `color: #fff` pieno.
**Priorità**: P1

### 4.8 Footer — Contrasto Heading/Text ⬤ ERROR SC 1.4.3
**File**: Tutti i 6 temi
**Problema**: Già rilevato nella homepage. I footer usano testo chiaro su sfondo scuro.
In Tricolore il heading usa `--tricolore-oro` (`#C9A227`) su `#1a1a1a` → ~5.4:1 ✅.
Ma `.site-footer__about` potrebbe usare un grigio troppo chiaro.
**Fix**: Verificare che il testo about abbia almeno 4.5:1 in ogni tema.
**Priorità**: P1

---

## Riepilogo Aggiornato — Problemi Cross-Page

### Problemi che si ripetono su TUTTE le pagine (ereditati da base/navbar/footer)

| Problema | Pagine affette | Fix location |
|----------|:-------------:|--------------|
| Focus indicator insufficiente | Tutte | `base.css` |
| Role ridondanti su nav/footer | Tutte | `navbar.html`, `footer.html` |
| SVG senza `<title>` nel nav | Tutte | `navbar.html` |
| Footer contrasto (tema-specifico) | Tutte | 6 temi |
| Menuitem senza `aria-current` | Tutte (su link attivo) | `navbar.html` |

### Problemi specifici per pagina

| Problema | Pagina | Fix location | Priorità |
|----------|--------|--------------|:--------:|
| Event CTA: primary su secondary | Events listing | `base.css` | P0 |
| Hero subtitle opacity 0.8 | Events listing | `base.css` | P1 |
| Search tab semantics | Search results | `search_results.html` | P2 |
| Search per-page label | Search results | `search_results.html` | P3 |
| Gallery alt fallback | Gallery block | `gallery_block.html` | P2 |
| Gallery lightbox focus trap | Gallery page | `gallery_page.html` JS | P2 |
| Partner initial contrasto | Partner listing + home | `base.css` / temi | P1 |

---

## Priorità di Esecuzione (Aggiornata)

1. **P0 — Errori contrasto gravi** (SC 1.4.3):
   - Tricolore/Heritage hero overlay
   - Tricolore CTA spotlight
   - Event card CTA `base.css` (default pericoloso)

2. **P0 — Focus indicator** (SC 2.4.7):
   - `base.css` doppio ring
   - Tricolore/Heritage focus ring color

3. **P1 — Contrasto secondario**:
   - Event hero subtitle opacity
   - Footer heading/text tutti i temi
   - Partner initial card (temi con primary chiaro)
   - SVG labels navbar

4. **P1 — Landmarks** (SC 1.3.1):
   - Rimuovere role ridondanti
   - Aggiungere `<header>` wrapper

5. **P2 — Semantica e ricerca**:
   - Search tab → navigation pattern
   - Gallery alt fallback
   - Gallery lightbox focus trap
   - Line spacing base.css

6. **P2 — Menuitem states** (SC 4.1.2):
   - `aria-current="page"` su menuitem attivo

7. **P3 — Fix minori**:
   - Em units per container partner
   - Search per-page label
   - Status message ricerca (falso positivo — redirect)

---

## Stima Impatto Aggiornata

- **File da modificare**: ~12
- **Temi che richiedono fix CSS**: 2 certi (Tricolore, Heritage) + 2 da verificare (Zen, Clubs)
- **Temi senza problemi**: 2 (Velocity, Terra)
- **Errori da eliminare**: ~22 (homepage originali + event CTA + hero subtitle)
- **Warning da ridurre**: ~75
- **Template con a11y già eccellente**: `event_detail_page`, `partner_page`, `my_events`, `pagination`, `breadcrumbs`
