# 99 — Allineamento Template tra Temi

## Stato attuale

Dall'analisi dei 30 file HTML in `theme_examples/`, il tema **Clubs** risulta il più completo e funge da modello di riferimento. Gli altri temi presentano lacune di gravità variabile, sia strutturali (sezioni mancanti) che contenutistiche (immagini placeholder, form incompleti).

### Classifica completezza

| # | Tema | Img reali | Righe totali | Criticità principali |
|---|---|---|---|---|
| 1 | **Clubs** | 23 | 896 | Nessuna — è il riferimento |
| 2 | **Heritage** | 14 | 809 | Nessuna grave, manca qualche feature |
| 3 | **Velocity** | 17 | 651 | gallery.html troppo snella, manca Values |
| 4 | **Tricolore** | 0 | 1301 | events.html deviato in "Routes", 0 immagini |
| 5 | **Terra** | 0 | 924 | 0 immagini, no telefono, footer minimali |
| 6 | **Zen** | 0 | 1082 | Form 3 campi, 3 stats, 0 immagini, il più incompleto |

---

## FASE 1 — Correzioni critiche (temi con problemi strutturali)

### 1.1 Zen: completare le sezioni troncate

**contact.html**
- Aggiungere i campi mancanti al form: Cognome (Last Name), Subject (dropdown con opzioni: General, Membership, Events, Press), Telefono (opzionale)
- Aggiungere una sezione "Office Hours" dedicata con giorni/orari, non solo "by appointment"
- Aggiungere il numero di telefono nelle informazioni di contatto

**index.html**
- Portare le stats da 3 a 4, aggiungendo una quarta statistica (es. "Partner Clubs" o "Years Active") per uniformità con tutti gli altri temi

**gallery.html**
- Sostituire i 7 panel CSS colorati con 9 immagini Unsplash reali a tema (moto, eventi, ritrovi)
- Aggiungere le captions sotto ogni immagine
- Il layout "comic panel" può restare come identità visiva, ma il contenuto deve essere fotografico

**Tutti i file**
- Espandere il footer: aggiungere indirizzo, email, telefono e sezione "Links" con navigazione — attualmente è solo una riga di link

### 1.2 Terra: aggiungere immagini e completare il form

**Tutti i file (index, events, gallery)**
- Inserire immagini Unsplash reali: nessuna delle 5 pagine ne contiene. Servono almeno:
  - index.html: 1 hero background + 3 immagini card eventi
  - events.html: 1 immagine per ogni card evento (4 eventi)
  - gallery.html: sostituire i 6 placeholder emoji con 9 foto reali

**contact.html**
- Aggiungere il campo Cognome (Last Name)
- Aggiungere il campo Subject (dropdown)
- Aggiungere il numero di telefono nella sezione informazioni di contatto

**Footer (tutti i file)**
- Espandere il footer, attualmente minimale: aggiungere sezione "Resources" con link utili e icone social

### 1.3 Tricolore: ripristinare events.html come pagina eventi

**events.html** — INTERVENTO MAGGIORE
- La pagina è stata completamente reinterpretata come "Routes / Itinerari" con km, altitudine e landmarks
- Deve essere convertita in una pagina eventi standard con:
  - Titolo sezione "Upcoming Events" (non "Featured Routes")
  - Card con: data, titolo evento, descrizione, luogo, link dettagli
  - Rimuovere le statistiche percorso (km, dislivello, punti di interesse)
- La sezione "Routes" può diventare una feature aggiuntiva della home o una pagina separata, ma events.html deve mostrare eventi

**index.html**
- La sezione "Featured Routes" nella home va rinominata/convertita in "Featured Events" con card evento standard (data, titolo, descrizione, CTA)

**Tutti i file**
- Inserire immagini Unsplash reali: attualmente 0 su tutte le 5 pagine. Servono:
  - index.html: 1 hero background
  - events.html: 1 immagine per card evento
  - gallery.html: sostituire i 9 gradient+emoji con 9 foto reali

---

## FASE 2 — Completamento Velocity e Heritage

### 2.1 Velocity: espandere le pagine più snelle

**about.html**
- Aggiungere una sezione "Our Values" (4 card con titolo, icona/emoji, descrizione) — è presente in tutti gli altri temi ma qui è sostituita da "What We Offer"
- "What We Offer" può restare, ma Values deve essere aggiunta come sezione separata

**gallery.html** (102 righe — il file più piccolo di tutto il confronto)
- Aggiungere captions sotto ogni immagine (attualmente sono 9 foto senza testo)
- Aggiungere effetto overlay su hover con titolo/descrizione (come Clubs e Tricolore)
- Valutare l'aggiunta di un pulsante "Load More"

### 2.2 Heritage: piccole integrazioni

**about.html**
- Aggiungere una sezione "What We Offer" / servizi, per completare il quadro (ha Values ma non servizi)

**gallery.html**
- Portare le immagini da 6 a 9 per uniformità con gli altri temi

---

## FASE 3 — Feature comuni mancanti in tutti i 6 temi

Queste sezioni non sono presenti in nessuno dei 6 temi. Decidere quali implementare come standard e aggiungerle a tutti.

### 3.1 index.html — Home Page

**Newsletter signup**
- Aggiungere una sezione con titolo, testo invito e form (email + pulsante "Subscribe")
- Posizionarla prima del footer o dopo il CTA membership

**Partners / Sponsors**
- Griglia di loghi partner (4-6 loghi) con link esterni
- Posizionarla dopo la sezione eventi o prima del footer

**Gallery preview**
- Griglia 3-4 foto con link "View Full Gallery"
- Posizionarla tra gli eventi e il CTA

### 3.2 contact.html — Contatti

**FAQ section**
- 4-5 domande frequenti in formato accordion (espandi/chiudi)
- Domande tipo: Come iscriversi, Quote associative, Orari sede, Come partecipare agli eventi, Politica cancellazione
- Posizionarla dopo il form e le info di contatto

**Mappa**
- Inserire un placeholder per mappa OpenStreetMap (iframe o div segnaposto)
- Attualmente solo Clubs ha un placeholder mappa, gli altri 5 nulla

**GDPR / Privacy checkbox**
- Aggiungere checkbox privacy obbligatorio al form di contatto in tutti i temi
- Attualmente solo Clubs lo ha

### 3.3 events.html — Eventi

**Prezzo evento**
- Aggiungere il campo prezzo in ogni card evento (es. "€25 / Free for members")
- Nessun tema lo mostra attualmente

**Filtri / Tab**
- Aggiungere tab o pulsanti filtro (Tutti, Prossimi, Passati, Per categoria)
- Attualmente solo Clubs ha questa funzionalità

**CTA finale**
- Aggiungere una sezione CTA in fondo (es. "Want to organize an event? Contact us")

### 3.4 about.html — Chi siamo

**CTA finale**
- Aggiungere sezione CTA membership in fondo alla pagina ("Join Our Community")
- Nessun tema about.html ha un CTA di chiusura

### 3.5 gallery.html — Galleria

**Lightbox**
- Aggiungere funzionalità lightbox (click su foto → visualizzazione a tutto schermo)
- Nessun tema la implementa attualmente

**Upload CTA**
- Sezione invito ai soci per caricare le proprie foto ("Share Your Memories")
- Con link o pulsante che rimanda al sistema di upload

**Filtri / Categorie**
- Tab o pulsanti per filtrare per categoria (Events, Club Life, Rides, Members)
- Attualmente solo Clubs ha filtri nella galleria

---

## FASE 4 — Uniformità estetica (senza perdere identità)

Ogni tema mantiene il proprio stile visivo, ma deve rispettare queste regole strutturali:

### Footer
Tutti i footer devono contenere almeno:
- Logo/nome club
- Indirizzo fisico
- Email e telefono
- Navigazione (5 link: Home, About, Events, Gallery, Contact)
- Link social (almeno 3 icone)
- Copyright

Attualmente non conformi: **Zen** (solo link), **Terra** (minimale senza social)

### Nav
Tutti i nav devono contenere:
- Logo/nome a sinistra
- 5 link navigazione (Home, About, Events, Gallery, Contact)
- CTA button a destra ("Join" o "Membership")

Attualmente senza CTA button: **Terra**, **Zen**, **Tricolore**

### Form di contatto — Campi e helper

Tutti i form di contatto devono avere la stessa struttura di campi e di helper:

**Campi obbligatori standard** (6 + checkbox):
1. First Name (text) — con `*` nel label
2. Last Name (text) — con `*` nel label
3. Email (email) — con `*` nel label
4. Subject (select/dropdown) — con `*` nel label
5. Phone (tel) — opzionale, senza `*`
6. Message (textarea, rows=5) — con `*` nel label
7. Privacy/GDPR checkbox — con `*`, testo: "I have read and accept the privacy policy."

**Opzioni standard per il dropdown Subject:**
- General Inquiry
- Membership
- Events
- Partnership
- Other

**Helper richiesti per ogni campo:**
- `<label>` esplicito sempre presente (mai solo placeholder)
- `placeholder` su ogni input e textarea (testo guida es. "Your first name", "your@email.com", "Tell us more...")
- Indicatore obbligatorio `*` nel testo della label per i campi required
- Attributo `required` nell'HTML su tutti i campi obbligatori
- Attributo `for`/`id` che colleghi label e input (attualmente nessun tema lo fa correttamente tranne Clubs sul checkbox privacy)
- `aria-label` o `aria-describedby` per accessibilità (attualmente assente in tutti i temi)

**Stato attuale per tema:**

| Attributo | Velocity | Heritage | Terra | Zen | Clubs | Tricolore |
|---|---|---|---|---|---|---|
| **Label** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Placeholder** | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| **Indicatore `*`** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Attributo `required`** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **`for`/`id` link** | ❌ | ❌ | ❌ | ❌ | ⚠️ solo privacy | ❌ |
| **`aria-*`** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **First Name** | ✅ | ✅ | ❌ (solo "Name") | ❌ (solo "Name") | ✅ | ✅ |
| **Last Name** | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ |
| **Email** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Phone** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Subject dropdown** | ✅ | ✅ | ✅ (Interest) | ❌ | ✅ | ✅ |
| **Message** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Privacy checkbox** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |

**Interventi per tema:**
- **Velocity**: aggiungere placeholder a tutti i campi, aggiungere `*`, `required`, `for`/`id`, `aria-label`, campo Phone, checkbox privacy
- **Heritage**: aggiungere placeholder a tutti i campi, aggiungere `*`, `required`, `for`/`id`, `aria-label`, campo Phone, checkbox privacy
- **Terra**: rinominare "Name" in "First Name" + aggiungere "Last Name", rinominare "Interest" in "Subject" con opzioni standard, aggiungere `*`, `required`, `for`/`id`, `aria-label`, campo Phone, checkbox privacy
- **Zen**: aggiungere campi Last Name, Subject, Phone; aggiungere `*`, `required`, `for`/`id`, `aria-label`, checkbox privacy
- **Clubs**: aggiungere placeholder a tutti i campi, aggiungere attributo `required`, completare `for`/`id` link su tutti i campi, aggiungere `aria-label`
- **Tricolore**: aggiungere `*`, `required`, `for`/`id`, `aria-label`, campo Phone, checkbox privacy

### Card eventi
Formato standard per le card evento in tutti i temi:
- Data (badge o testo formattato)
- Categoria/tag
- Titolo
- Descrizione (2-3 righe)
- Luogo
- Prezzo (da aggiungere)
- CTA link ("Details" o "Register")

### Immagini
- Ogni tema deve usare immagini Unsplash reali almeno per: hero, card eventi, gallery
- I placeholder CSS (emoji, gradienti) sono accettabili solo come fallback, non come contenuto principale
- Quantità minima: index 4, events 4, gallery 9, about 0 (ok senza), contact 0 (ok senza)

---

## Riepilogo priorità

| Priorità | Attività | Temi coinvolti |
|---|---|---|
| 🔴 Alta | Ripristinare events.html come pagina eventi | Tricolore |
| 🔴 Alta | Inserire immagini Unsplash reali | Terra, Zen, Tricolore |
| 🔴 Alta | Completare form contatto (campi mancanti) | Zen, Terra |
| 🟡 Media | Espandere footer minimali | Zen, Terra |
| 🟡 Media | Aggiungere CTA button al nav | Terra, Zen, Tricolore |
| 🟡 Media | Portare stats a 4 in Zen | Zen |
| 🟡 Media | Aggiungere Values in about.html | Velocity |
| 🟡 Media | Espandere gallery.html | Velocity, Heritage |
| 🟢 Bassa | Aggiungere Newsletter a tutti | Tutti |
| 🟢 Bassa | Aggiungere Partners a tutti | Tutti |
| 🟢 Bassa | Aggiungere FAQ a contact | Tutti |
| 🟢 Bassa | Aggiungere prezzo eventi | Tutti |
| 🟢 Bassa | Aggiungere filtri eventi/gallery | Tutti tranne Clubs |
| 🟢 Bassa | Aggiungere lightbox gallery | Tutti |
| 🟢 Bassa | Aggiungere GDPR checkbox | Tutti tranne Clubs |
| 🟡 Media | Aggiungere placeholder a tutti i campi form | Velocity, Heritage, Clubs |
| 🟡 Media | Aggiungere `*` obbligatorietà + `required` attr | Tutti |
| 🟡 Media | Aggiungere `for`/`id` link label↔input | Tutti |
| 🟢 Bassa | Aggiungere `aria-label` / `aria-describedby` | Tutti |
| 🟡 Media | Aggiungere campo Phone al form | Velocity, Heritage, Terra, Zen, Tricolore |
