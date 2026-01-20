📖 Questo documento è disponibile in: [🇮🇹 IT](README-it.md) | [🇬🇧 EN](README.md) | [🇩🇪 DE](README-de.md) | [🇫🇷 FR](README-fr.md) | [🇪🇸 ES](README-es.md)

---

# Sito Web Motoclub - Documentazione

> **🏍️ Un CMS completo basato su Wagtail 7.x per motoclub**

## 📚 Per gli Sviluppatori

Questo repository contiene la documentazione completa e le specifiche per costruire un sito web per motoclub usando **Wagtail 7.x** e **Django**.

### Inizia da qui

1. **Indice completo:** [00-INDEX.md](00-INDEX.md) — Indice di tutti i file di documentazione
2. **Struttura progetto:** [01-PROJECT-STRUCTURE.md](01-PROJECT-STRUCTURE.md)
3. **Dipendenze:** [02-DEPENDENCIES.md](02-DEPENDENCIES.md)

### 🎨 Anteprima Temi Online

Puoi visualizzare tutti i 6 temi direttamente nel browser usando GitHub Pages:

| Tema | Stile | Anteprima |
|------|-------|-----------|
| **Velocity** | Moderno/Tailwind | [🔗 Vedi](https://bertalan.github.io/motoclubsite_prj/theme_examples/velocity/) |
| **Heritage** | Classico/Bootstrap | [🔗 Vedi](https://bertalan.github.io/motoclubsite_prj/theme_examples/heritage/) |
| **Terra** | Eco-friendly | [🔗 Vedi](https://bertalan.github.io/motoclubsite_prj/theme_examples/terra/) |
| **Zen** | Minimal/Fumetto | [🔗 Vedi](https://bertalan.github.io/motoclubsite_prj/theme_examples/zen/) |
| **Clubs** | Premium Italiano | [🔗 Vedi](https://bertalan.github.io/motoclubsite_prj/theme_examples/clubs/) |
| **Tricolore** | Orgoglio Italiano 🇮🇹 | [🔗 Vedi](https://bertalan.github.io/motoclubsite_prj/theme_examples/tricolore/) |

> **Nota:** Per abilitare GitHub Pages, vai in Settings del repository → Pages → Source: "Deploy from a branch" → Branch: `main` / `docs/rebuild`

### Alternativa: Visualizzare i file HTML direttamente

Se GitHub Pages non è abilitato, puoi comunque vedere i file HTML:

1. Naviga nella cartella [`theme_examples/`](theme_examples/)
2. Clicca su una cartella tema (es. `velocity/`)
3. Clicca su `index.html`
4. Clicca il pulsante **Raw** per vedere il sorgente, oppure usa [htmlpreview.github.io](https://htmlpreview.github.io/):
   ```
   https://htmlpreview.github.io/?https://github.com/bertalan/motoclubsite_prj/blob/main/docs/rebuild/theme_examples/velocity/index.html
   ```

### Struttura della Documentazione

| Sezione | File | Descrizione |
|---------|------|-------------|
| **Setup** | 01-03 | Struttura progetto, dipendenze, settings |
| **Page Models** | 10-14 | Pagine Wagtail: Home, Content, News, Events, Gallery |
| **Blocks** | 20-24 | Blocchi StreamField: Hero, Content, Media, Layout |
| **Temi** | 30-39 | Sistema template e 6 temi |
| **SEO & i18n** | 40-42 | JSON-LD, multilingua, snippets |
| **Deploy** | 50-70 | Docker, produzione, checklist, migrazione |
| **Funzionalità Soci** | 80-91 | Tesseramento, eventi, galleria, PWA, notifiche |

Vedi [00-INDEX.md](00-INDEX.md) per la lista completa dei file con descrizioni.

---

# Guida Utente - Motoclub

## Cos'è questo sito?

Il sito del Motoclub è la casa digitale del nostro club. Qui trovi tutto ciò che ti serve per vivere al meglio l'esperienza del club.

### Cosa puoi fare

| # | Funzionalità | Descrizione |
|---|--------------|-------------|
| 1 | [📰 News](#1--leggere-le-news) | Leggi articoli e comunicazioni del club |
| 2 | [📅 Eventi](#2--vedere-e-iscriversi-agli-eventi) | Scopri e iscriviti a raduni, gite, incontri |
| 3 | [📸 Galleria](#3--la-galleria-fotografica) | Sfoglia e carica le foto delle uscite |
| 4 | [👤 Profilo](#4--il-tuo-profilo-socio) | Gestisci i tuoi dati personali |
| 5 | [🪪 Tessera](#5--la-tessera-digitale) | La tua tessera sempre in tasca |
| 6 | [❤️ Preferiti](#6-️-i-tuoi-eventi-preferiti) | Salva gli eventi che ti interessano |
| 7 | [🌍 Lingue](#7--cambiare-lingua) | Scegli tra 5 lingue disponibili |
| 8 | [📧 Contatti](#8--contattarci) | Scrivi al club |
| 9 | [📰 Stampa](#9--ufficio-stampa) | Materiali per giornalisti e partner |
| 10 | [🤝 Partner](#10--partner-e-sconti) | Sconti esclusivi dai nostri partner |
| 11 | [🛠️ Soccorso](#11-️-rete-di-mutuo-soccorso) | Rete di aiuto tra soci in viaggio |
| 12 | [📬 Newsletter](#12--newsletter-e-notifiche) | Ricevi le novità via email o push |

---

## Le 5 Domande Fondamentali

### 🧑 CHI può usare il sito?

| Tipo di visitatore | Cosa può fare |
|-------------------|---------------|
| **Chiunque** | Leggere news, vedere eventi, sfogliare la galleria, iscriversi agli eventi |
| **Socio registrato** | Tutto sopra + sconti eventi, caricare foto, gestire profilo |
| **Socio con tessera attiva** | Tutto sopra + votare, sconti maggiori, eventi preferiti |

### 📌 COSA posso fare sul sito?

| Funzionalità | Descrizione semplice |
|--------------|---------------------|
| Leggere le news | Articoli e comunicazioni del club |
| Vedere gli eventi | Raduni, gite, incontri in programma |
| Iscrivermi a un evento | Prenotare il posto con pochi click |
| Caricare foto | Condividere le foto delle uscite |
| Gestire il mio profilo | Modificare i miei dati personali |
| Vedere la mia tessera | Tessera digitale con QR code |

### ⏰ QUANDO posso usare queste funzioni?

| Funzione | Disponibilità |
|----------|---------------|
| Navigazione sito | Sempre, 24/7 |
| Iscrizione eventi | Fino alla data di scadenza indicata |
| Caricamento foto | Solo soci con permesso attivo |
| Tessera digitale | Solo soci con tessera valida |

### 📍 DOVE trovo le varie sezioni?

| Sezione | Come arrivarci |
|---------|----------------|
| Home | Clicca sul logo o "Home" nel menu |
| Chi Siamo | Menu → Chi Siamo |
| Eventi | Menu → Eventi |
| Galleria | Menu → Galleria |
| News | Menu → News |
| Il mio profilo | Icona utente in alto a destra |
| La mia tessera | Profilo → La mia tessera |

### ❓ PERCHÉ dovrei registrarmi?

| Vantaggio | Descrizione |
|-----------|-------------|
| Sconti sugli eventi | Prezzi ridotti riservati ai soci |
| Caricare foto | Condividi i tuoi scatti con il club |
| Eventi preferiti | Salva gli eventi che ti interessano |
| Tessera digitale | Sempre in tasca sul telefono |
| Newsletter | Ricevi le novità via email |

---

## Funzionalità nel Dettaglio

### 1. 📰 Leggere le News

**Cos'è:** Gli articoli e le comunicazioni ufficiali del club.

**Come funziona:**
1. Vai alla sezione "News" dal menu
2. Sfoglia gli articoli in ordine cronologico
3. Clicca su un titolo per leggere l'articolo completo

**Suggerimento:** Puoi filtrare per categoria (es. "Comunicazioni", "Resoconti", "Tecnica").

---

### 2. 📅 Vedere e Iscriversi agli Eventi

**Cos'è:** Il calendario di tutti i raduni, gite e incontri del club.

**Chi può iscriversi:** Tutti! L'iscrizione agli eventi è aperta a chiunque, socio o meno.

**Come funziona:**
1. Vai alla sezione "Eventi" dal menu
2. Vedi la lista degli eventi in programma
3. Clicca su un evento per i dettagli
4. Clicca "Iscriviti" per prenotare il tuo posto
5. Compila i dati richiesti e conferma

**Informazioni che trovi:**
- Data e ora
- Luogo con mappa
- Programma della giornata
- Costo (se previsto)
- Posti disponibili

**💡 Sconto Soci:** I soci hanno diritto a prezzi ridotti! Durante l'iscrizione vedrai:
- Il prezzo standard per tutti
- Il prezzo scontato riservato ai soci
- Un link per diventare socio e ottenere lo sconto

**Sconto Early Booking:** Iscrivendoti in anticipo puoi avere uno sconto aggiuntivo!
- 60+ giorni prima: 20% di sconto
- 30-59 giorni prima: 10% di sconto
- Meno di 30 giorni: prezzo pieno

**Portare un passeggero:** Durante l'iscrizione puoi aggiungere un accompagnatore. Se è socio, cercalo per nome. Altrimenti, inserisci i suoi dati.

---

### 3. 📸 La Galleria Fotografica

**Cos'è:** Tutte le foto delle nostre uscite e attività.

**Come funziona:**
1. Vai alla sezione "Galleria" dal menu
2. Sfoglia gli album per evento o data
3. Clicca su una foto per vederla grande
4. Usa le frecce per scorrere

**Caricare le tue foto (solo soci):**
1. Vai al tuo profilo → "Carica foto"
2. Seleziona fino a 20 foto insieme
3. Scrivi un titolo (es. "Raduno Primavera 2026")
4. Aggiungi una descrizione
5. Scegli i tag (es. "raduno", "gita", "moto-storiche")
6. Clicca "Carica"

**Nota:** Le foto vengono controllate prima della pubblicazione.

---

### 4. 👤 Il Tuo Profilo Socio

**Cos'è:** La tua area personale dove gestisci i tuoi dati.

**Come accedere:**
1. Clicca sull'icona utente in alto a destra
2. Fai il login con email e password
3. Vai su "Il mio profilo"

**Cosa puoi modificare:**
- Foto profilo
- Numero di telefono
- Indirizzo
- Preferenze newsletter
- Biografia (se vuoi un profilo pubblico)

**Profilo pubblico:** Se attivi questa opzione, altri potranno vedere il tuo nome, foto, bio e i contenuti che hai pubblicato.

---

### 5. 🪪 La Tessera Digitale

**Cos'è:** La tua tessera del motoclub, sempre disponibile sul telefono.

**Come vederla:**
1. Vai al tuo profilo
2. Clicca su "La mia tessera"

**Cosa contiene:**
- Il tuo nome e foto
- Numero di tessera
- Data di scadenza
- QR code (per verifiche rapide)
- Codice a barre

**Stamparla:** Clicca "Stampa tessera" per avere un PDF formato carta di credito.

---

### 6. ❤️ I Tuoi Eventi Preferiti

**Cos'è:** Una lista personale degli eventi che ti interessano.

**Come funziona:**
1. Quando vedi un evento che ti interessa, clicca il cuoricino ❤️
2. L'evento viene salvato nei tuoi preferiti
3. Vai su "I miei eventi" per vedere la lista

**Funzioni extra:**
- **Mappa:** Vedi tutti i tuoi eventi preferiti su una mappa
- **Esporta:** Scarica gli eventi nel tuo calendario (Google, Apple, Outlook)
- **Condividi:** Invia la lista ai tuoi amici

---

### 7. 🌍 Cambiare Lingua

**Cos'è:** Il sito è disponibile in 5 lingue.

**Lingue disponibili:**
- 🇬🇧 English (predefinita)
- 🇮🇹 Italiano
- 🇩🇪 Deutsch
- 🇫🇷 Français
- 🇪🇸 Español

**Come cambiare:**
1. Cerca il selettore lingua (solitamente in alto a destra)
2. Clicca sulla bandiera o sigla della lingua desiderata
3. Il sito si aggiorna automaticamente

---

### 8. 📧 Contattarci

**Cos'è:** Come mettersi in contatto con il club.

**Come fare:**
1. Vai alla sezione "Contatti" dal menu
2. Compila il modulo con:
   - Il tuo nome
   - La tua email
   - Il messaggio
3. Clicca "Invia"

**Altre opzioni:**
- Email diretta: info@motoclub.it
- Telefono: vedi pagina contatti
- Social: link a Facebook, Instagram

---

### 9. 📰 Ufficio Stampa

**Cos'è:** Materiali ufficiali per giornalisti e partner.

**Cosa trovi:**
- Logo del club in vari formati
- Foto ufficiali della sede e degli eventi
- Comunicati stampa
- Contatti per la stampa

**Come accedere:**
1. Vai alla sezione "Stampa" (solitamente nel footer)
2. Scarica i materiali che ti servono

---

### 10. 🤝 Partner e Sconti

**Cos'è:** I partner del club offrono sconti esclusivi ai soci.

**Come funziona:**
1. Vai alla sezione "Partner" dal menu o footer
2. Sfoglia i partner per categoria (officine, ricambi, abbigliamento...)
3. Clicca su un partner per vedere lo sconto riservato

**Ottenere lo sconto:**
1. Vai dal partner con la tua tessera digitale
2. Il partner verifica la tua tessera inserendo il numero
3. Ricevi lo sconto comunicato!

**Nota:** Il partner vede solo il tuo nome visualizzato e la validità della tessera - i tuoi dati personali restano privati.

---

### 11. 🛠️ Rete di Mutuo Soccorso

**Cos'è:** Una rete di soci disponibili ad aiutare in caso di problemi in viaggio.

**Come vedere chi può aiutarti:**
1. Vai alla sezione "Mutuo Soccorso" (nel menu o footer)
2. Usa la mappa per vedere chi è disponibile nella tua zona
3. Filtra per competenza: meccanica, trasporto, logistica, emergenza
4. Clicca su un helper per vedere come contattarlo

**Offrire il tuo aiuto:**
1. Vai al tuo profilo → "Mutuo Soccorso"
2. Attiva la disponibilità
3. Scegli le tue competenze (meccanica, trasporto furgone, ecc.)
4. Definisci la tua zona di copertura (km da casa)
5. **Importante:** Scegli cosa mostrare agli altri soci:
   - Nome visualizzato (sempre visibile)
   - Telefono / WhatsApp / Email (tu decidi)
   - Posizione esatta o solo città
   - Orari di disponibilità

**Privacy totale:** Ogni campo è controllato da te. Puoi anche usare solo il modulo di contatto, così nessuno vede i tuoi dati.

---

### 12. 📬 Newsletter e Notifiche

**Cos'è:** Ricevi le novità del club via email o notifiche push sul telefono.

**Cosa puoi ricevere:**
- Nuove news pubblicate
- Nuovi eventi in programma
- Promemoria prima degli eventi a cui sei iscritto
- **Riepilogo weekend:** ogni giovedì, la lista degli eventi del fine settimana che hai salvato ❤️
- Avviso scadenza tessera

**Come gestire le preferenze:**
1. Vai al tuo profilo → "Notifiche"
2. Attiva/disattiva i tipi di notifica che ti interessano
3. Scegli la frequenza: immediato, riepilogo giornaliero, riepilogo settimanale
4. **Scegli quando:** puoi decidere giorno e ora in cui ricevere le notifiche
5. Attiva le notifiche push se hai installato l'app

**Promemoria Weekend (default: giovedì ore 9):**
- Se hai salvato eventi che si svolgono nel fine settimana, ricevi un riepilogo
- Puoi cambiare giorno e ora a tuo piacimento
- Nessun evento salvato = nessuna email inutile

**Disiscriversi da un'email:**
1. In fondo a ogni email c'è un link "Disiscriviti"
2. Clicca e arrivi a una pagina di conferma
3. Puoi lasciare un messaggio (opzionale)
4. Clicca "Conferma" - non serve fare login!

**Perché ricevo questa email?**
Ogni email spiega chiaramente perché la ricevi (es. "Ricevi questa email perché sei iscritto alle News").

---

## Domande Frequenti

### Come mi registro?

1. Clicca su "Registrati" o "Diventa socio"
2. Compila il modulo con i tuoi dati
3. Riceverai un'email di conferma
4. Il club ti contatterà per la tessera

### Ho dimenticato la password

1. Clicca su "Login"
2. Clicca su "Password dimenticata?"
3. Inserisci la tua email
4. Riceverai un link per reimpostarla

### La mia tessera sta per scadere

Riceverai un'email di promemoria 30 e 7 giorni prima della scadenza. Contatta il club per il rinnovo.

### Non riesco a iscrivermi a un evento

Verifica che:
- La tua tessera sia ancora valida
- L'evento non sia esaurito
- Non sia passata la scadenza iscrizioni

### Le mie foto non compaiono nella galleria

Le foto vengono controllate prima della pubblicazione. Attendi qualche giorno. Se il problema persiste, contatta il club.

### Come ottengo lo sconto dai partner?

Mostra la tua tessera digitale al partner. Lui inserirà il numero tessera per verificare che sei socio attivo. Non deve conoscere i tuoi dati personali.

### Come posso aiutare altri soci in difficoltà?

1. Vai al profilo → Mutuo Soccorso
2. Attiva la disponibilità
3. Scegli le competenze che offri
4. Decidi quali contatti mostrare (solo ciò che vuoi)

### Non voglio che si vedano i miei dati nel Mutuo Soccorso

Nessun problema! Puoi:
- Attivare solo il modulo di contatto (nessun dato visibile)
- Mostrare solo il nome visualizzato e la città
- Scegliere campo per campo cosa rendere visibile

### Come mi disiscrivo dalla newsletter?

In fondo a ogni email c'è un link "Disiscriviti". Cliccalo, conferma sulla pagina che si apre, fatto! Non serve fare login.

### Ricevo troppe email

Vai nelle preferenze notifiche e scegli "Riepilogo settimanale" invece di "Immediato". Riceverai una sola email a settimana con tutte le novità.

### Come attivo le notifiche push?

1. Installa l'app sul telefono (Aggiungi a Home)
2. Vai al profilo → Notifiche
3. Attiva "Notifiche push"
4. Il browser chiederà il permesso - accetta

---

## Hai bisogno di aiuto?

Se qualcosa non funziona o hai dubbi:

1. **Email:** info@motoclub.it
2. **Telefono:** vedi pagina contatti
3. **Di persona:** vieni in sede durante gli orari di apertura

---

*Ultimo aggiornamento: Gennaio 2026*

---

📖 Questo documento è disponibile in: [🇮🇹 IT](README-it.md) | [🇬🇧 EN](README.md) | [🇩🇪 DE](README-de.md) | [🇫🇷 FR](README-fr.md) | [🇪🇸 ES](README-es.md)
