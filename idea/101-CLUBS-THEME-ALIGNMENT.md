# 101 - Allineamento UI/UX Tema Clubs

Documento di riferimento per uniformare il tema **Clubs** al template di partenza Tailwind.

## File di Riferimento

- **Template originale**: `idea/theme_examples/clubs/contact.html`
- **CSS tema**: `clubcms/static/css/themes/clubs/main.css`
- **CSS base**: `clubcms/static/css/base.css`
- **Template Wagtail**: `clubcms/templates/website/pages/contact_page.html`

---

## Analisi Comparativa

### 1. Spaziature e Padding

| Elemento | Template Riferimento | Implementazione Pre-Fix | Post-Fix |
|----------|---------------------|------------------------|----------|
| Padding sezione principale | `py-24` (6rem = 96px) | `4rem` (64px) | `6rem` ✅ |
| Gap tra colonne layout | `gap-16` (4rem) | `gap: 4rem` | ✅ OK |
| Padding info cards | `p-8` (2rem) | `padding: 2rem` | ✅ OK |
| Gap sidebar cards | `space-y-8` (2rem) | `gap: 1.5rem` | `2rem` ✅ |
| Container max-width | `max-w-7xl` (1280px) | `1200px` | Mantenuto 1200px |

### 2. Struttura Componenti

| Componente | Template | Stato Attuale | Note |
|------------|----------|---------------|------|
| Hero con immagine sfondo | ✅ `h-[40vh]` con gradient overlay | ❌ Solo header testuale | Fase futura |
| Form nome/cognome affiancati | ✅ `grid md:grid-cols-2 gap-6` | ❌ Full-width | **Fase 2** |
| Campo telefono | ✅ Presente | ❌ Mancante | Richiede modifica modello |
| Subject come dropdown | ✅ `<select>` | ❌ Input testo | Richiede modifica modello |
| CTA card rossa (membership) | ✅ Box `bg-red` | ⚠️ CSS esiste, non usato | Attivabile |
| Sezione FAQ accordion | ✅ Presente | ❌ Non implementata | Fase futura |
| Mappa placeholder | ✅ Sezione full-width | ⚠️ In sidebar | OK per ora |

### 3. Differenze Stilistiche Dettagliate

```
TEMPLATE TAILWIND                       CSS CLUBS ATTUALE
─────────────────────────────────────────────────────────────────
Label: tracking-[0.2em] = 0.2em         letter-spacing: 0.08em   → da verificare
Input bg: bg-[#1A1A1A]                  var(--color-surface-alt) ✅
Input border: border-white/20           rgba(255,255,255,0.2)    ✅
Focus: border-color red                 var(--color-secondary)   ✅
Button: bg-red px-10 py-4               .btn-primary             ✅
```

---

## Piano di Implementazione

### Fase 1: Allineamento Spaziature ✅

**File**: `clubcms/static/css/themes/clubs/main.css`

**Modifiche**:
```css
/* Da */
.page-contact { padding: 4rem 0; }
.page-contact__sidebar { gap: 1.5rem; }

/* A */
.page-contact { padding: 6rem 0; }
.page-contact__sidebar { gap: 2rem; }
```

**Impatto altri temi**: Nessuno (modifiche solo in clubs/main.css)

---

### Fase 2: Layout Form 2 Colonne ✅

**File**: `clubcms/static/css/themes/clubs/main.css`

**Nuove classi**:
```css
/* Form field row per affiancare campi */
.page-contact__field-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

@media (max-width: 767px) {
  .page-contact__field-row {
    grid-template-columns: 1fr;
  }
}
```

**Modifica template**: `contact_page.html` - avvolgere nome + email in div con classe `page-contact__field-row`

**Impatto altri temi**: Minimo - la classe è opzionale e theme-specific

---

### Fase 3: Hero Contact Page ✅

Aggiunto supporto per hero opzionale nel modello ContactPage con:
- Campo `hero_image` (ForeignKey a wagtailimages.Image)
- Campo `hero_badge` (CharField) - piccolo testo sopra il titolo
- Overlay gradient automatico (da 70% a 100% nero)

**File modificati**:
- `apps/website/models/pages.py` - nuovi campi
- `apps/website/migrations/0008_add_contact_hero_and_membership.py`
- `templates/website/pages/contact_page.html` - sezione hero condizionale
- `static/css/themes/clubs/main.css` - stili hero

**Impatto altri temi**: Minimo - l'hero è opzionale e gli stili sono in clubs/main.css

---

### Fase 4: CTA Card Membership ✅

Attivato box membership nella sidebar contact:
- Nuovi campi in **ContactPage** (traducibili):
  - `membership_title` - titolo card
  - `membership_description` - descrizione benefici
  - `membership_price` - prezzo (es. "Quota annuale €80")
  - `membership_cta_text` - testo pulsante
  - `membership_cta_url` - link al form iscrizione
- Template aggiornato con card condizionale (`page.membership_*`)
- CSS già presente (`.page-contact__cta-card`) + nuovi stili

**Note**: I campi sono nella Page (non in SiteSettings) per supportare traduzioni multilingua.

**Impatto altri temi**: Nullo - il CSS specifico è in clubs/main.css

---

## Checklist di Verifica

- [x] Padding pagina contact = 6rem verticale
- [x] Gap sidebar cards = 2rem
- [x] Campi nome/email affiancati su desktop
- [x] Stack verticale su mobile (< 768px)
- [x] Hero opzionale con immagine + badge
- [x] CTA membership card nella sidebar
- [ ] Nessuna regressione su altri temi
- [ ] Test in Docker container

---

## Note Tecniche

### Variabili CSS Clubs

```css
:root {
  --color-primary: #0A0A0A;
  --color-secondary: #C41E3A;      /* Rosso brand */
  --color-accent: #E02547;         /* Rosso hover */
  --color-surface: #0A0A0A;
  --color-surface-alt: #1A1A1A;    /* Cards, inputs */
  --color-text-primary: #FFFFFF;
  --color-text-muted: #A0A0A0;
  --clubs-border: 1px solid rgba(255, 255, 255, 0.1);
  --clubs-transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
```

### Breakpoints

| Nome | Valore | Uso |
|------|--------|-----|
| Mobile | < 768px | Stack verticale |
| Tablet | 768px - 1023px | 2 colonne dove serve |
| Desktop | ≥ 1024px | Layout completo |

---

## Storico Modifiche

| Data | Fase | Descrizione |
|------|------|-------------|
| 2026-02-13 | 1 | Allineamento spaziature padding/gap |
| 2026-02-13 | 2 | Layout form 2 colonne |
| 2026-02-13 | 3 | Hero Contact Page con immagine + badge |
| 2026-02-13 | 4 | CTA Card Membership in sidebar |
| 2026-02-13 | 4b | Spostato campi membership da SiteSettings a ContactPage (traduzione) |
| 2026-02-14 | 5 | About Page: timeline orizzontale con divider rosso, spaziatura 6rem |
| 2026-02-14 | 6 | Navbar: rimosso Registrati, Accedi come CTA, Storia + Contatti sotto Chi Siamo |
| 2026-02-14 | 7 | Login page: CTA signup evidenziato |
| 2026-02-14 | 8 | Partner Page: CSS Clubs completo (cards scure, hover rosso, sidebar), i18n strings |
