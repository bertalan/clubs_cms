# Event Registration — Gap Analysis & Implementation Plan

> **Scope:** confronto tra specifica (`82-EVENT-REGISTRATIONS.md`) e codice attuale.
> **Obiettivo:** documento compatto per lavoro agentic, context ≤ 50%.

---

## File Map

| Ruolo | Path |
|-------|------|
| Model EventRegistration, PricingTier, EventFavorite | `clubcms/apps/events/models.py` |
| Form auth + guest | `clubcms/apps/events/forms.py` |
| Views (register, cancel, favorites, ICS) | `clubcms/apps/events/views.py` |
| Pricing calc, ICS gen, waitlist | `clubcms/apps/events/utils.py` |
| URLs | `clubcms/apps/events/urls.py` |
| Admin (Wagtail ModelViewSet) | `clubcms/apps/events/admin.py` |
| Hooks (viewset register) | `clubcms/apps/events/wagtail_hooks.py` |
| EventDetailPage (da riga ~579) | `clubcms/apps/website/models/pages.py` |
| Template registrazione | `clubcms/templates/events/register.html` |
| CSS form/base | `clubcms/static/css/base.css` (riga ~373) |
| Specifica registrazioni | `idea/82-EVENT-REGISTRATIONS.md` |
| Specifica transactional models | `idea/83-TRANSACTIONAL-MODELS.md` |
| Specifica federation | `idea/92-EVENT-FEDERATION.md` |

---

## Stato attuale — Cosa funziona

- `EventRegistration` model: campi base, guest (email/nome), passenger completo, status, payment_status
- `PricingTier` model: days/hours/minutes_before, discount_percent, label, is_deadline, total_minutes property
- `EventRegistrationForm`: ModelForm con accept_terms, validazione passenger condizionale
- `GuestRegistrationForm`: estende auth form con first_name, last_name, email required
- `EventRegisterView` (CreateView): GET mostra form + pricing, POST crea registration con check duplicati, capacity, waitlist atomic
- `calculate_price()`: trova tier attivo, applica tier discount + member discount, cap 100%
- `promote_from_waitlist()`: dopo cancellazione, promuove il più vecchio in waitlist
- Admin Wagtail: ModelViewSet con list/filter/search, TabbedInterface (Registration/Guest/Passenger)
- `EventDetailPage`: registration_open, registration_deadline, max_attendees, base_fee, early_bird_discount/deadline, member_discount_percent
- Computed properties: is_registration_open, confirmed_count, spots_remaining, current_price, member_price

---

## GAP — Tecnici

### G1. PricingTier non collegato all'admin EventDetailPage

**Problema:** `InlinePanel("pricing_tiers")` manca nei panel di EventDetailPage. L'admin mostra solo campi piatti `early_bird_discount` + `early_bird_deadline`.

**Fix:**
1. In `clubcms/apps/website/models/pages.py` aggiungere nel `registration_panels`:
   ```python
   InlinePanel("pricing_tiers", label=_("Pricing Tiers"), min_num=0, max_num=10),
   ```
2. Import: `from wagtail.admin.panels import InlinePanel` (verificare che non sia già importato)
3. Deprecare campi `early_bird_discount` e `early_bird_deadline` (non rimuovere subito, servono per migrazione dati)

### G2. Campi mancanti su EventDetailPage

Aggiungere in `clubcms/apps/website/models/pages.py` nella classe `EventDetailPage`:

| Campo | Type | Sezione |
|-------|------|---------|
| `allow_guests` | BooleanField(default=True) | Registration |
| `max_guests` | PositiveIntegerField(default=0) | Registration |
| `require_login` | BooleanField(default=False) | Registration |
| `meeting_point` | CharField(max_length=255, blank=True) | Logistics (nuovo MultiFieldPanel) |
| `meeting_time` | TimeField(null=True, blank=True) | Logistics |
| `difficulty` | CharField(choices=DIFFICULTY_CHOICES, blank=True) | Logistics |
| `requirements` | RichTextField(blank=True) | Logistics |
| `passenger_fee` | DecimalField(max_digits=8, decimal_places=2, default=0) | Pricing |
| `passenger_discount` | PositiveIntegerField(default=0) | Pricing |
| `passenger_included` | BooleanField(default=False) | Pricing |

Choices per difficulty:
```python
DIFFICULTY_CHOICES = [
    ("easy", _("Easy")),
    ("medium", _("Medium")),
    ("challenging", _("Challenging")),
]
```

### G3. Deadline calcolata da PricingTier.is_deadline

**Problema:** `is_registration_open` usa solo `registration_deadline` (campo statico). La spec vuole che il tier con `is_deadline=True` calcoli la deadline automaticamente.

**Fix in `EventDetailPage`:**
```python
@property
def computed_deadline(self):
    """Deadline dal PricingTier is_deadline o fallback a registration_deadline."""
    deadline_tier = self.pricing_tiers.filter(is_deadline=True).first()
    if deadline_tier and self.start_date:
        from datetime import timedelta
        offset = timedelta(
            days=deadline_tier.days_before,
            hours=deadline_tier.hours_before,
            minutes=deadline_tier.minutes_before,
        )
        return self.start_date - offset
    return self.registration_deadline
```

Aggiornare `is_registration_open` per usare `self.computed_deadline`.

### G4. Nessuna email di conferma

**Fix:** In `EventRegisterView.form_valid()`, dopo `registration.save()`, inviare email:
```python
from django.core.mail import send_mail
# oppure creare un signal post_save su EventRegistration
```

Alternativa preferibile: signal in `clubcms/apps/events/signals.py` + `apps.py` ready().

### G5. Pricing passenger non calcolato

**Fix in `utils.py` `calculate_price()`:** Aggiungere parametro `has_passenger=False` e calcolare:
- Se `passenger_included` → 0
- Se passenger è membro → `passenger_fee * (1 - passenger_discount/100)`
- Altrimenti → `passenger_fee`

Restituire anche `passenger_price` nel dict.

### G6. View non valida `allow_guests` / `require_login`

`EventRegisterView.dispatch()` non controlla:
- `require_login` → se True e utente anonimo → redirect a login
- `allow_guests` / `max_guests` → non limitati nel form

**Fix:** In `dispatch()` aggiungere controlli. Nel form, limitare `guests` field con `max_value`.

---

## GAP — UI/UX

### U1. Passenger fields sempre visibili (CRITICO)

Tutti i 10 campi passenger appaiono sempre. La spec richiede progressive disclosure:
1. `has_passenger` checkbox → toggle fieldset
2. `passenger_is_member` → toggle sotto-sezione member vs manual

**Fix:** Aggiungere JS in `register.html` block `extra_js`:
```javascript
document.addEventListener('DOMContentLoaded', function() {
    const hasPassenger = document.getElementById('id_has_passenger');
    const passengerFields = document.querySelector('.passenger-details');
    const isMember = document.getElementById('id_passenger_is_member');
    const memberFields = document.querySelector('.passenger-member-fields');
    const manualFields = document.querySelector('.passenger-manual-fields');
    
    function togglePassenger() {
        passengerFields.hidden = !hasPassenger.checked;
    }
    function toggleMemberType() {
        memberFields.hidden = !isMember.checked;
        manualFields.hidden = isMember.checked;
    }
    
    hasPassenger.addEventListener('change', togglePassenger);
    isMember.addEventListener('change', toggleMemberType);
    togglePassenger();
    toggleMemberType();
});
```

Richiede ristrutturazione del template: wrappare campi passenger in `<div class="passenger-details" hidden>`, con sotto-div per member vs manual.

### U2. Nessun riepilogo pricing visivo

Mancano: posti disponibili, countdown deadline, savings badge, prezzo barrato, CTA "Become a member".

**Fix template `register.html`:**
- Aggiungere `spots_remaining` nel context (già computed su EventDetailPage)
- Sezione "X spots left" con urgency styling
- Prezzo barrato se tier discount attivo: `<del>{{ pricing.base_fee }}€</del> <strong>{{ pricing.final_price }}€</strong>`
- Badge savings: `"Save {{ pricing.total_discount_percent }}%"`
- Se utente non è membro: "Become a member and save €X → /become-member/"
- Deadline countdown con classi urgency

### U3. Nessun riepilogo pre-submit

Aggiungere sezione riepilogo prima del bottone submit con totale calcolato (rider + passenger + guests).

---

## GAP — WCAG / W3C

### W1. `novalidate` senza JS validation

Il form ha `novalidate` ma nessuna validazione client-side. O rimuovere `novalidate` o aggiungere JS.

**Fix consigliato:** Rimuovere `novalidate` e lasciare la validazione nativa HTML5 come primo livello, mantenendo la validazione server-side.

### W2. Mancano `aria-describedby`

Collegare help text e messaggi errore ai campi:
```html
<input id="{{ field.id_for_label }}" aria-describedby="{{ field.id_for_label }}_help {{ field.id_for_label }}_errors">
<small id="{{ field.id_for_label }}_help">{{ field.help_text }}</small>
<ul id="{{ field.id_for_label }}_errors" role="alert">...</ul>
```

**Fix form Django:** Override widget attrs nel `__init__` del form, oppure usare un custom template tag.

### W3. Mancano `aria-required`

Aggiungere `aria-required="true"` ai campi required + indicatore visivo `*`.

**Fix form `__init__`:**
```python
for field_name, field in self.fields.items():
    if field.required:
        field.widget.attrs['aria-required'] = 'true'
```

### W4. Input senza classi CSS

I widget Django non hanno `class="form-input"`. Il CSS base definisce stili per `.form-input`, `.form-select`, `.form-textarea` ma non sono applicati.

**Fix form `__init__`:**
```python
for field_name, field in self.fields.items():
    widget = field.widget
    if isinstance(widget, forms.TextInput):
        widget.attrs.setdefault('class', 'form-input')
    elif isinstance(widget, forms.Select):
        widget.attrs.setdefault('class', 'form-select')
    elif isinstance(widget, forms.Textarea):
        widget.attrs.setdefault('class', 'form-textarea')
    elif isinstance(widget, forms.EmailInput):
        widget.attrs.setdefault('class', 'form-input')
    elif isinstance(widget, forms.NumberInput):
        widget.attrs.setdefault('class', 'form-input')
    elif isinstance(widget, forms.DateInput):
        widget.attrs.setdefault('class', 'form-input')
```

### W5. Mancano `autocomplete`

| Campo | autocomplete |
|-------|-------------|
| first_name | `given-name` |
| last_name | `family-name` |
| email | `email` |
| passenger_phone | `tel` |

### W6. Checkbox accept_terms senza link

Aggiungere URL ai termini: `_("I accept the <a href='/terms/'>terms and conditions</a>")` con `mark_safe`.

---

## Piano di implementazione (ordine consigliato)

### Fase 1 — Form UX + Accessibilità (nessuna migration)

1. **`forms.py`**: Aggiungere `__init__` con CSS classes, aria-required, autocomplete attrs
2. **`register.html`**: Ristrutturare template — progressive disclosure passenger, aria-describedby, rimuovere novalidate, prezzo barrato, spots remaining, link termini
3. **`register.html` (JS)**: Aggiungere script toggle passenger/member fields
4. **`views.py`**: Passare `spots_remaining` e `computed_deadline` nel context

### Fase 2 — Model + Admin (richiede migration)

5. **`pages.py`**: Aggiungere campi G2 a EventDetailPage
6. **`pages.py`**: Aggiungere `InlinePanel("pricing_tiers")` nei registration_panels
7. **`pages.py`**: Aggiungere property `computed_deadline`, aggiornare `is_registration_open`
8. **`makemigrations` + `migrate`**

### Fase 3 — Business Logic

9. **`utils.py`**: Estendere `calculate_price()` con passenger pricing
10. **`views.py`**: Aggiungere check `require_login`, `allow_guests`, `max_guests` in dispatch/form_valid
11. **Signals/email**: Conferma registrazione post-save

### Fase 4 — Cleanup

12. Data migration: copiare `early_bird_discount`/`early_bird_deadline` esistenti in PricingTier
13. Deprecare/rimuovere campi piatti dopo migrazione
14. Test automatici per pricing, registration flow, edge cases
