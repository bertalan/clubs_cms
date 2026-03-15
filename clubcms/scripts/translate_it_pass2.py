#!/usr/bin/env python3
"""
Batch-translate ALL remaining strings in the Italian .po file for ClubCMS.
This second pass covers all 789 remaining untranslated entries.
"""

# ──────────────────────────────────────────────────────────
#  ADDITIONAL TRANSLATIONS  (English → Italian) – Pass 2
# ──────────────────────────────────────────────────────────
TRANSLATIONS = {
    # ── Membership card / QR ──
    "No membership card available.": "Nessuna tessera associativa disponibile.",
    "QR code generation not available.": "Generazione codice QR non disponibile.",
    "Barcode generation not available.": "Generazione codice a barre non disponibile.",
    "Your name": "Il tuo nome",
    "Phone number": "Numero di telefono",
    "Email address": "Indirizzo email",
    "Your current location": "La tua posizione attuale",
    "Description must be 5000 characters or fewer.": "La descrizione deve contenere al massimo 5000 caratteri.",
    "Why do you need access? (optional)": "Perché hai bisogno dell'accesso? (opzionale)",
    "Role": "Ruolo",
    "Emergency Contact": "Contatto di Emergenza",
    "Introduction": "Introduzione",
    "Emergency contacts": "Contatti di emergenza",
    "Default map radius (km)": "Raggio mappa predefinito (km)",
    "Enable federation": "Abilita la federazione",

    # ── Mutual Aid Pages ──
    "Mutual Aid Page": "Pagina Mutuo Soccorso",
    "Mutual Aid Pages": "Pagine Mutuo Soccorso",
    "Show phone number": "Mostra numero di telefono",
    "Show mobile number": "Mostra numero di cellulare",
    "Show WhatsApp availability": "Mostra disponibilità WhatsApp",
    "Show email address": "Mostra indirizzo email",
    "Show exact location": "Mostra posizione esatta",
    "If disabled, only the city name is shown.": "Se disabilitato, viene mostrato solo il nome della città.",
    "Show profile photo": "Mostra foto profilo",
    "Show bio": "Mostra biografia",
    "Show availability hours": "Mostra orari di disponibilità",
    "Aid Privacy Settings": "Impostazioni Privacy Soccorso",

    # ── Urgency levels ──
    "Low - can wait": "Bassa - può attendere",
    "Medium - within a day": "Media - entro un giorno",
    "High - urgent": "Alta - urgente",
    "Emergency - immediate": "Emergenza - immediato",
    "Accepted": "Accettato",
    "In progress": "In corso",

    # ── Aid issue types ──
    "Breakdown": "Guasto",
    "Flat tire": "Foratura",
    "Out of fuel": "Senza carburante",
    "Accident": "Incidente",
    "Need towing": "Bisogno di traino",
    "Need tools": "Bisogno di attrezzi",
    "Need transport": "Bisogno di trasporto",
    "Need accommodation": "Bisogno di alloggio",
    "Helper": "Soccorritore",
    "Requester name": "Nome del richiedente",
    "Requester phone": "Telefono del richiedente",
    "Requester email": "Email del richiedente",
    "Requester (if member)": "Richiedente (se socio)",
    "Issue type": "Tipo di problema",
    "Where are you? Address or coordinates.": "Dove ti trovi? Indirizzo o coordinate.",

    # ── Federation access ──
    "From federation": "Dalla federazione",
    "Federation access": "Accesso federazione",
    "Can contact helpers": "Può contattare i soccorritori",
    "External user ID": "ID utente esterno",
    "External display name": "Nome visualizzato esterno",
    "Contacts unlocked": "Contatti sbloccati",
    "Access level": "Livello di accesso",
    "Approved by": "Approvato da",
    "Federated Aid Access": "Accesso Soccorso Federato",
    "Federated Aid Access Grants": "Concessioni Accesso Soccorso Federato",
    "Denied": "Negato",
    "Federated access": "Accesso federato",
    "Why are you requesting access?": "Perché stai richiedendo l'accesso?",
    "Reviewed by": "Revisionato da",
    "Reviewed at": "Revisionato il",
    "Federated Aid Access Request": "Richiesta Accesso Soccorso Federato",
    "Federated Aid Access Requests": "Richieste Accesso Soccorso Federato",
    "Contact Unlock": "Sblocco Contatto",
    "Contact Unlocks": "Sblocchi Contatti",
    "Active membership required.": "Iscrizione attiva obbligatoria.",

    # ── Notification types ──
    "News published": "Notizia pubblicata",
    "Event published": "Evento pubblicato",
    "Event reminder": "Promemoria evento",
    "Weekend favorites": "Preferiti del weekend",
    "Registration opens": "Apertura registrazioni",
    "Photo approved": "Foto approvata",
    "Membership expiring": "Iscrizione in scadenza",
    "Partner news": "Notizie partner",
    "Partner event interest": "Interesse evento partner",
    "Partner event comment": "Commento evento partner",
    "Partner event cancelled": "Evento partner annullato",
    "Mutual aid request": "Richiesta mutuo soccorso",
    "Mutual aid access request": "Richiesta accesso mutuo soccorso",
    "Payment instructions": "Istruzioni di pagamento",
    "Payment confirmed": "Pagamento confermato",
    "Payment expired": "Pagamento scaduto",
    "Registration cancelled": "Registrazione annullata",
    "Promoted from waitlist": "Promosso dalla lista d'attesa",
    "Push notification": "Notifica push",
    "In-app notification": "Notifica in-app",
    "Failed": "Fallito",
    "Skipped": "Saltato",

    # ── Notification model fields (lowercase) ──
    "notification type": "tipo notifica",
    "content type": "tipo contenuto",
    "object ID": "ID oggetto",
    "recipient": "destinatario",
    "channel": "canale",
    "status": "stato",
    "title": "titolo",
    "body": "corpo",
    "scheduled for": "programmato per",
    "If set, notification will not be sent before this time.": "Se impostato, la notifica non verrà inviata prima di questo orario.",
    "sent at": "inviato il",
    "created at": "creato il",
    "error message": "messaggio di errore",
    "notification": "notifica",
    "notifications": "notifiche",

    # ── Push subscriptions ──
    "user": "utente",
    "endpoint": "endpoint",
    "Push service URL": "URL servizio push",
    "p256dh key": "chiave p256dh",
    "Client public encryption key": "Chiave pubblica di cifratura del client",
    "auth key": "chiave di autenticazione",
    "Client auth secret": "Segreto di autenticazione del client",
    "active": "attivo",
    "last used": "ultimo utilizzo",
    "user agent": "user agent",
    "push subscription": "sottoscrizione push",
    "push subscriptions": "sottoscrizioni push",
    "token": "token",
    "unsubscribe token": "token di disiscrizione",
    "unsubscribe tokens": "token di disiscrizione",
    "Invalid JSON body": "Corpo JSON non valido",
    "Endpoint is required": "L'endpoint è obbligatorio",
    "Endpoint must use HTTPS": "L'endpoint deve usare HTTPS",
    "Encryption keys are required": "Le chiavi di cifratura sono obbligatorie",

    # ── StreamField blocks – gallery/media ──
    "Article gallery": "Galleria articolo",
    "Event gallery": "Galleria evento",
    "Event location map": "Mappa posizione evento",
    "Card thumbnail image.": "Immagine miniatura scheda.",
    "Optional badge text (e.g. date, category label).": "Testo badge opzionale (es. data, etichetta categoria).",
    "Card title.": "Titolo scheda.",
    "Short description text.": "Breve testo descrittivo.",
    "Link to page": "Link alla pagina",
    "External URL": "URL esterno",
    "Used only if no internal page is selected.": "Usato solo se non è selezionata una pagina interna.",
    "Button / link label.": "Etichetta pulsante / link.",
    "Optional section title above the grid.": "Titolo di sezione opzionale sopra la griglia.",
    "2 columns": "2 colonne",
    "3 columns": "3 colonne",
    "4 columns": "4 colonne",
    "Number of columns on desktop.": "Numero di colonne su desktop.",
    "Default": "Predefinito",
    "Outlined": "Con bordo",
    "Elevated / shadow": "Elevato / ombra",
    "Minimal": "Minimale",
    "Visual style for the cards.": "Stile visivo per le schede.",
    "Cards grid": "Griglia schede",

    # ── CTA block ──
    "CTA headline.": "Titolo CTA.",
    "Supporting text.": "Testo di supporto.",
    "Button label.": "Etichetta pulsante.",
    "Button page link": "Link pagina pulsante",
    "Button external URL": "URL esterno pulsante",
    "Primary colour": "Colore primario",
    "Gradient": "Gradiente",
    "Image background": "Sfondo immagine",
    "Background style for this section.": "Stile di sfondo per questa sezione.",
    "Background image (only used with 'Image background' style).": "Immagine di sfondo (usata solo con lo stile 'Sfondo immagine').",

    # ── Statistics block ──
    "The numeric value or short text (e.g. '1500+').": "Il valore numerico o testo breve (es. '1500+').",
    "Description of the stat (e.g. 'Members').": "Descrizione della statistica (es. 'Soci').",
    "Optional icon class name.": "Nome classe icona opzionale.",
    "Statistic": "Statistica",
    "Optional section title.": "Titolo di sezione opzionale.",
    "Statistics": "Statistiche",

    # ── Testimonial / Quote block ──
    "The quote text.": "Il testo della citazione.",
    "Name of the person quoted.": "Nome della persona citata.",
    "Role or title of the author (e.g. 'President').": "Ruolo o titolo dell'autore (es. 'Presidente').",
    "Optional portrait of the author.": "Ritratto opzionale dell'autore.",

    # ── Timeline block ──
    "Year or date label (e.g. '2015').": "Anno o etichetta data (es. '2015').",
    "Event or milestone title.": "Titolo dell'evento o traguardo.",
    "Detailed description of this event.": "Descrizione dettagliata di questo evento.",
    "Timeline entry": "Voce cronologia",
    "Timeline entries": "Voci cronologia",
    "Timeline": "Cronologia",

    # ── Team block ──
    "Position or title.": "Posizione o titolo.",
    "Short biography.": "Breve biografia.",
    "Team member": "Membro del team",
    "Optional section title (e.g. 'Board of Directors').": "Titolo di sezione opzionale (es. 'Consiglio Direttivo').",
    "Team members": "Membri del team",
    "Team grid": "Griglia team",

    # ── Newsletter block ──
    "Stay updated": "Resta aggiornato",
    "Form heading.": "Intestazione del modulo.",
    "Short text explaining what subscribers will receive.": "Breve testo che spiega cosa riceveranno gli iscritti.",
    "Subscribe": "Iscriviti",
    "Newsletter signup": "Iscrizione newsletter",

    # ── Alert block ──
    "Alert message content.": "Contenuto del messaggio di avviso.",
    "Danger": "Pericolo",
    "Visual style and severity of the alert.": "Stile visivo e gravità dell'avviso.",
    "Allow users to dismiss this alert.": "Consenti agli utenti di chiudere questo avviso.",

    # ── Slider / Hero slider ──
    "Slide background image.": "Immagine di sfondo della slide.",
    "Slide headline.": "Titolo della slide.",
    "Optional subtitle text.": "Testo sottotitolo opzionale.",
    "CTA text": "Testo CTA",
    "CTA page link": "Link pagina CTA",
    "CTA external URL": "URL esterno CTA",
    "Slide": "Slide",
    "Slides": "Slide",
    "Automatically advance slides.": "Avanzamento automatico delle slide.",
    "Time between slides in milliseconds.": "Tempo tra le slide in millisecondi.",
    "Half screen": "Metà schermo",
    "Three-quarter screen": "Tre quarti di schermo",
    "Full screen": "Schermo intero",
    "Slider height.": "Altezza dello slider.",
    "Show navigation arrows.": "Mostra frecce di navigazione.",
    "Show dot indicators.": "Mostra indicatori a punti.",
    "Hero slider": "Slider hero",

    # ── Hero banner ──
    "Hero background image.": "Immagine di sfondo hero.",
    "Small badge text above the title (e.g. 'Est. 2010').": "Piccolo testo badge sopra il titolo (es. 'Est. 2010').",
    "Main headline.": "Titolo principale.",
    "Supporting text below the title.": "Testo di supporto sotto il titolo.",
    "Secondary CTA text": "Testo CTA secondario",
    "Optional secondary button label.": "Etichetta pulsante secondario opzionale.",
    "Secondary CTA page link": "Link pagina CTA secondario",
    "Secondary CTA external URL": "URL esterno CTA secondario",
    "Light overlay": "Sovrapposizione chiara",
    "Dark overlay": "Sovrapposizione scura",
    "Gradient overlay": "Sovrapposizione gradiente",
    "Overlay style over the background image.": "Stile sovrapposizione sull'immagine di sfondo.",
    "Bottom left": "In basso a sinistra",
    "Bottom right": "In basso a destra",
    "Position of the text overlay.": "Posizione del testo sovrapposto.",
    "Hero banner": "Banner hero",

    # ── Hero countdown ──
    "Select an event to count down to.": "Seleziona un evento per il conto alla rovescia.",
    "Optional background image. Falls back to event cover image.": "Immagine di sfondo opzionale. In assenza, usa l'immagine di copertina dell'evento.",
    "Override the event title in the hero.": "Sovrascrivi il titolo dell'evento nell'hero.",
    "Hero countdown": "Conto alla rovescia hero",

    # ── Hero video ──
    "URL to the video file (MP4 recommended).": "URL del file video (MP4 consigliato).",
    "Displayed on mobile or when video cannot play.": "Visualizzata su mobile o quando il video non può essere riprodotto.",
    "Mute the video (required for autoplay on most browsers).": "Silenzia il video (necessario per l'autoplay sulla maggior parte dei browser).",
    "Loop the video.": "Ripeti il video in loop.",
    "Hero video": "Video hero",

    # ── Accordion block ──
    "Accordion panel header.": "Intestazione pannello fisarmonica.",
    "Panel content revealed when expanded.": "Contenuto del pannello mostrato all'espansione.",
    "Accordion item": "Elemento fisarmonica",
    "Optional section title above the accordion.": "Titolo di sezione opzionale sopra la fisarmonica.",
    "Panels": "Pannelli",

    # ── Tab block ──
    "Tab label.": "Etichetta scheda.",
    "Tab panel content.": "Contenuto pannello scheda.",

    # ── Two columns block ──
    "Left column": "Colonna sinistra",
    "Right column": "Colonna destra",
    "50 / 50": "50 / 50",
    "33 / 67": "33 / 67",
    "67 / 33": "67 / 33",
    "25 / 75": "25 / 75",
    "75 / 25": "75 / 25",
    "Column width ratio.": "Rapporto larghezza colonne.",
    "Two columns": "Due colonne",

    # ── Section block ──
    "Optional section heading.": "Intestazione di sezione opzionale.",
    "Section body content.": "Contenuto corpo della sezione.",
    "Secondary colour": "Colore secondario",
    "Light grey": "Grigio chiaro",
    "Background style.": "Stile di sfondo.",
    "Small": "Piccolo",
    "Large": "Grande",
    "Extra large": "Extra grande",
    "Vertical padding.": "Spaziatura verticale.",

    # ── Separator/spacer ──
    "Horizontal line": "Linea orizzontale",
    "Dots": "Punti",
    "Blank space": "Spazio vuoto",
    "Separator visual style.": "Stile visivo del separatore.",
    "Small (1rem)": "Piccolo (1rem)",
    "Medium (2rem)": "Medio (2rem)",
    "Large (4rem)": "Grande (4rem)",
    "Extra large (6rem)": "Extra grande (6rem)",
    "Amount of vertical space.": "Quantità di spazio verticale.",

    # ── Gallery block ──
    "Optional caption displayed below the image.": "Didascalia opzionale visualizzata sotto l'immagine.",
    "Gallery image": "Immagine galleria",
    "Optional gallery title.": "Titolo galleria opzionale.",
    "6 columns": "6 colonne",
    "Enable lightbox for full-size image viewing.": "Abilita lightbox per la visualizzazione a dimensione piena.",
    "Auto (original)": "Automatico (originale)",
    "Square (1:1)": "Quadrato (1:1)",
    "Landscape (4:3)": "Orizzontale (4:3)",
    "Widescreen (16:9)": "Panoramico (16:9)",
    "Portrait (3:4)": "Verticale (3:4)",
    "Thumbnail aspect ratio.": "Rapporto aspetto miniatura.",

    # ── Video embed ──
    "Paste a video URL (YouTube, Vimeo, etc.).": "Incolla un URL video (YouTube, Vimeo, ecc.).",
    "Optional caption displayed below the video.": "Didascalia opzionale visualizzata sotto il video.",
    "Autoplay the video (muted).": "Riproduci automaticamente il video (silenziato).",
    "Video embed": "Incorporamento video",

    # ── Image block ──
    "Centred": "Centrato",
    "Float left": "Allineato a sinistra",
    "Float right": "Allineato a destra",
    "Image alignment within the content area.": "Allineamento immagine nell'area contenuto.",

    # ── Document list ──
    "Optional description of the document.": "Descrizione opzionale del documento.",
    "Section title for the document list.": "Titolo di sezione per l'elenco documenti.",
    "Document list": "Elenco documenti",

    # ── Map block ──
    "Display address (shown in the info popup).": "Indirizzo visualizzato (mostrato nel popup informativo).",
    "Latitude,Longitude (e.g. '45.4642,9.1900').": "Latitudine,Longitudine (es. '45.4642,9.1900').",
    "Map zoom level (1-20).": "Livello di zoom mappa (1-20).",
    "Map height in pixels.": "Altezza mappa in pixel.",
    "Optional marker label.": "Etichetta marcatore opzionale.",

    # ── Route / waypoints ──
    "Waypoint name (e.g. 'Passo dello Stelvio').": "Nome tappa (es. 'Passo dello Stelvio').",
    "Optional address or location description.": "Indirizzo opzionale o descrizione della posizione.",
    "Latitude,Longitude (e.g. '46.5287,10.4531').": "Latitudine,Longitudine (es. '46.5287,10.4531').",
    "Start": "Partenza",
    "Waypoint": "Tappa",
    "Fuel stop": "Rifornimento",
    "Food / restaurant": "Ristorante",
    "Photo spot": "Punto fotografico",
    "End": "Arrivo",
    "Marker icon type on the map.": "Tipo icona marcatore sulla mappa.",
    "Route name.": "Nome percorso.",
    "Brief route description.": "Breve descrizione del percorso.",
    "At least two waypoints (start and end) are required.": "Sono necessarie almeno due tappe (partenza e arrivo).",
    "Scenic ride": "Giro panoramico",
    "Touring": "Turistico",
    "Sport / twisties": "Sportivo / curve",
    "Off-road / adventure": "Fuoristrada / avventura",
    "Commute / practical": "Tragitto / pratico",
    "Type of route.": "Tipo di percorso.",
    "Approximate distance (e.g. '320 km').": "Distanza approssimativa (es. '320 km').",
    "Elevation gain (e.g. '2500 m').": "Dislivello (es. '2500 m').",
    "Estimated riding time (e.g. '5-6 hours').": "Tempo di percorrenza stimato (es. '5-6 ore').",
    "Challenging": "Impegnativo",
    "Route difficulty level.": "Livello di difficoltà del percorso.",

    # ── Verification ──
    "Enter member card number": "Inserisci il numero tessera socio",
    "Verification type": "Tipo di verifica",
    "Select which piece of information to verify against.": "Seleziona quale dato utilizzare per la verifica.",
    "Verification value": "Valore di verifica",
    "Enter the value to verify": "Inserisci il valore da verificare",

    # ── Photo uploads ──
    "Photos": "Foto",
    "Select up to 20 images (JPG, PNG, or WebP, max 10 MB each).": "Seleziona fino a 20 immagini (JPG, PNG o WebP, max 10 MB ciascuna).",
    "Title prefix": "Prefisso titolo",
    "Optional prefix added to each photo title.": "Prefisso opzionale aggiunto ad ogni titolo foto.",
    "e.g. Summer Rally 2025": "es. Raduno Estivo 2025",
    "Optionally link photos to an event.": "Collega facoltativamente le foto a un evento.",
    "-- No event --": "-- Nessun evento --",
    "You can upload a maximum of %(max)d files at a time.": "Puoi caricare un massimo di %(max)d file alla volta.",
    "File '%(name)s' exceeds the maximum size of 10 MB.": "Il file '%(name)s' supera la dimensione massima di 10 MB.",
    "File '%(name)s' is not an allowed format. Only JPG, PNG, and WebP are accepted.": "Il file '%(name)s' non è in un formato consentito. Sono accettati solo JPG, PNG e WebP.",

    # ── Home page ──
    "Hero title": "Titolo hero",
    "Main headline displayed in the hero section.": "Titolo principale visualizzato nella sezione hero.",
    "Hero subtitle": "Sottotitolo hero",
    "Hero background image": "Immagine di sfondo hero",
    "Primary CTA text": "Testo CTA primario",
    "Primary CTA link": "Link CTA primario",
    "Primary CTA external URL": "URL esterno CTA primario",
    "Secondary CTA link": "Link CTA secondario",
    "Featured event": "Evento in evidenza",
    "Select an EventDetailPage to highlight on the homepage.": "Seleziona una pagina evento da evidenziare in homepage.",
    "Call-to-action buttons": "Pulsanti invito all'azione",
    "Featured content": "Contenuto in evidenza",
    "Home page": "Pagina iniziale",
    "Home pages": "Pagine iniziali",
    "Displayed below the page title.": "Visualizzato sotto il titolo della pagina.",
    "Cover image": "Immagine di copertina",

    # ── About page ──
    "About page": "Pagina chi siamo",
    "About pages": "Pagine chi siamo",
    "Use team-member blocks here.": "Usa qui i blocchi membro del team.",

    # ── Board page ──
    "Board page": "Pagina consiglio direttivo",
    "Board pages": "Pagine consiglio direttivo",

    # ── News index ──
    "Optional content displayed above the article listing.": "Contenuto opzionale visualizzato sopra l'elenco degli articoli.",
    "News index page": "Pagina indice notizie",
    "News index pages": "Pagine indice notizie",
    "Introduction / excerpt": "Introduzione / estratto",
    "Short summary shown in listings.": "Breve riepilogo mostrato negli elenchi.",
    "Display date": "Data di visualizzazione",
    "Publication date shown to readers.": "Data di pubblicazione mostrata ai lettori.",
    "Article metadata": "Metadati articolo",
    "Categorisation": "Categorizzazione",
    "News page": "Pagina notizia",
    "News pages": "Pagine notizie",

    # ── Events page ──
    "Optional content above the event listing.": "Contenuto opzionale sopra l'elenco eventi.",
    "Events page": "Pagina eventi",
    "Events pages": "Pagine eventi",
    "Short description shown in listings.": "Breve descrizione mostrata negli elenchi.",
    "Start date & time": "Data e ora di inizio",
    "End date & time": "Data e ora di fine",
    "Venue name": "Nome sede",
    "Coordinates": "Coordinate",
    "Latitude,Longitude (e.g. '45.4642,9.1900')": "Latitudine,Longitudine (es. '45.4642,9.1900')",
    "Registration open": "Registrazione aperta",
    "Registration deadline": "Scadenza registrazione",
    "Max attendees": "Partecipanti massimi",
    "0 = unlimited.": "0 = illimitati.",
    "Event participation cost in EUR.  0 = free.": "Costo di partecipazione in EUR. 0 = gratuito.",
    "Early-bird discount (%)": "Sconto prenotazione anticipata (%)",
    "Early-bird deadline": "Scadenza prenotazione anticipata",
    "Percentage discount for active members.": "Sconto percentuale per i soci attivi.",
    "Allow guest registration": "Consenti registrazione ospiti",
    "Meeting point": "Punto di ritrovo",
    "Where participants should gather before the event start.": "Dove i partecipanti devono radunarsi prima dell'inizio dell'evento.",
    "Difficulty level": "Livello di difficoltà",
    "Schedule": "Programma",
    "Registration settings": "Impostazioni registrazione",
    "Pricing": "Prezzi",
    "Promote": "Promuovi",
    "Event detail page": "Pagina dettaglio evento",
    "Event detail pages": "Pagine dettaglio evento",

    # ── Gallery page ──
    "Root collection": "Collezione radice",
    "Starting collection for gallery display.  Sub-collections become albums.": "Collezione iniziale per la visualizzazione galleria. Le sotto-collezioni diventano album.",
    "Gallery page": "Pagina galleria",
    "Gallery pages": "Pagine galleria",

    # ── Contact page ──
    "Form title": "Titolo modulo",
    "Success message": "Messaggio di successo",
    "Confirmation shown after form submission.": "Conferma mostrata dopo l'invio del modulo.",
    "Enable captcha": "Abilita captcha",
    "Honeypot + Time check": "Honeypot + Controllo tempo",
    "Cloudflare Turnstile": "Cloudflare Turnstile",
    "hCaptcha": "hCaptcha",
    "Captcha provider": "Fornitore captcha",
    "Captcha site key": "Chiave sito captcha",
    "Captcha secret key": "Chiave segreta captcha",
    "Anti-spam settings": "Impostazioni anti-spam",
    "Anti-spam": "Anti-spam",
    "Contact page": "Pagina contatti",
    "Contact pages": "Pagine contatti",

    # ── Privacy page ──
    "Last updated": "Ultimo aggiornamento",
    "Date the policy was last revised.": "Data dell'ultima revisione della politica.",
    "Privacy page": "Pagina privacy",
    "Privacy pages": "Pagine privacy",

    # ── Transparency page ──
    "Use document-list and accordion blocks for organising documents.": "Usa i blocchi elenco documenti e fisarmonica per organizzare i documenti.",
    "Transparency page": "Pagina trasparenza",
    "Transparency pages": "Pagine trasparenza",

    # ── Press page ──
    "Press email": "Email ufficio stampa",
    "Press phone": "Telefono ufficio stampa",
    "Press contact person": "Referente ufficio stampa",
    "Press contact": "Contatto stampa",
    "Press page": "Pagina stampa",
    "Press pages": "Pagine stampa",

    # ── Partner index ──
    "Partner index page": "Pagina indice partner",
    "Partner index pages": "Pagine indice partner",
    "ISO 3166-1 alpha-2 country code.": "Codice paese ISO 3166-1 alpha-2.",
    "Facebook URL": "URL Facebook",
    "Instagram URL": "URL Instagram",
    "LinkedIn URL": "URL LinkedIn",
    "YouTube URL": "URL YouTube",
    "Twitter / X URL": "URL Twitter / X",
    "Partner owner": "Proprietario partner",
    "User account that manages this partner page.": "Account utente che gestisce questa pagina partner.",
    "Owner email": "Email proprietario",
    "Contact email for the partner owner.": "Email di contatto del proprietario partner.",
    "Show this partner prominently.": "Mostra questo partner in evidenza.",
    "Display order": "Ordine di visualizzazione",
    "Lower numbers appear first.": "I numeri più bassi appaiono per primi.",
    "Show on homepage": "Mostra in homepage",
    "Partnership start": "Inizio partnership",
    "Partnership end": "Fine partnership",
    "Leave blank for ongoing partnerships.": "Lascia vuoto per le partnership in corso.",
    "Social media": "Social media",
    "Ownership": "Proprietà",
    "Display settings": "Impostazioni visualizzazione",
    "Social": "Social",
    "Display": "Visualizzazione",
    "Partner page": "Pagina partner",
    "Partner pages": "Pagine partner",

    # ── Theme names ──
    "Velocity": "Velocity",
    "Heritage": "Heritage",
    "Terra / Eco": "Terra / Eco",
    "Zen": "Zen",
    "Clubs": "Clubs",
    "Tricolore": "Tricolore",

    # ── Site settings ──
    "Honeypot (no external service)": "Honeypot (senza servizio esterno)",
    "OpenStreetMap": "OpenStreetMap",
    "Google Maps": "Google Maps",
    "Mapbox": "Mapbox",
    "Human-readable name shown in the header / meta tags.": "Nome leggibile mostrato nell'intestazione / meta tag.",
    "Site description": "Descrizione sito",
    "Default meta description for SEO.": "Meta descrizione predefinita per la SEO.",
    "Colour scheme": "Schema colori",
    "Logo (dark variant)": "Logo (variante scura)",
    "Optional dark-background version of the logo.": "Versione opzionale del logo con sfondo scuro.",
    "Opening hours": "Orari di apertura",
    "TikTok URL": "URL TikTok",
    "Navbar": "Barra di navigazione",
    "PWA name": "Nome PWA",
    "PWA short name": "Nome breve PWA",
    "PWA description": "Descrizione PWA",
    "PWA icon 192x192": "Icona PWA 192x192",
    "PWA icon 512x512": "Icona PWA 512x512",
    "PWA theme colour": "Colore tema PWA",
    "PWA background colour": "Colore sfondo PWA",
    "CAPTCHA provider": "Fornitore CAPTCHA",
    "CAPTCHA site key": "Chiave sito CAPTCHA",
    "CAPTCHA secret key": "Chiave segreta CAPTCHA",
    "Map routing service": "Servizio routing mappa",
    "Map API key": "Chiave API mappa",
    "Required for Google Maps / Mapbox.": "Richiesta per Google Maps / Mapbox.",
    "Default map centre": "Centro mappa predefinito",
    "Default map zoom": "Zoom mappa predefinito",
    "General": "Generale",
    "Branding": "Brand",
    "Progressive Web App": "Progressive Web App",
    "PWA": "PWA",
    "Anti-spam / CAPTCHA": "Anti-spam / CAPTCHA",
    "Forms": "Moduli",
    "Map & routing": "Mappa e percorsi",
    "site settings": "impostazioni sito",

    # ── Payment settings ──
    "Test": "Test",
    "Payment mode": "Modalità pagamento",
    "Only credentials for the selected mode are used at runtime.": "Solo le credenziali della modalità selezionata vengono usate a runtime.",
    "Stripe enabled (test)": "Stripe abilitato (test)",
    "Stripe public key (test)": "Chiave pubblica Stripe (test)",
    "Stripe secret key (test)": "Chiave segreta Stripe (test)",
    "Stripe webhook secret (test)": "Segreto webhook Stripe (test)",
    "PayPal enabled (test)": "PayPal abilitato (test)",
    "PayPal client ID (test)": "ID client PayPal (test)",
    "PayPal secret (test)": "Segreto PayPal (test)",
    "Stripe enabled (live)": "Stripe abilitato (live)",
    "Stripe public key (live)": "Chiave pubblica Stripe (live)",
    "Stripe secret key (live)": "Chiave segreta Stripe (live)",
    "Stripe webhook secret (live)": "Segreto webhook Stripe (live)",
    "PayPal enabled (live)": "PayPal abilitato (live)",
    "PayPal client ID (live)": "ID client PayPal (live)",
    "PayPal secret (live)": "Segreto PayPal (live)",
    "Bank transfer enabled": "Bonifico bancario abilitato",
    "Account holder": "Intestatario conto",
    "IBAN": "IBAN",
    "BIC / SWIFT": "BIC / SWIFT",
    "Bank name": "Nome banca",
    "Bank transfer instructions": "Istruzioni bonifico bancario",
    "Additional instructions shown to the user (e.g. 'Include the reference in the description').": "Istruzioni aggiuntive mostrate all'utente (es. 'Includi il riferimento nella causale').",
    "Bank transfer expiry (days)": "Scadenza bonifico bancario (giorni)",
    "Days allowed for the user to complete the bank transfer.": "Giorni concessi all'utente per completare il bonifico bancario.",
    "Active mode": "Modalità attiva",
    "Mode": "Modalità",
    "Stripe (test)": "Stripe (test)",
    "PayPal (test)": "PayPal (test)",
    "Test configuration": "Configurazione test",
    "Stripe (live)": "Stripe (live)",
    "PayPal (live)": "PayPal (live)",
    "Live configuration": "Configurazione live",
    "Bank transfer": "Bonifico bancario",
    "payment settings": "impostazioni pagamento",

    # ── Colour scheme snippet ──
    "Main brand colour (hex).": "Colore del brand principale (hex).",
    "Secondary/accent brand colour (hex).": "Colore secondario/accento del brand (hex).",
    "Accent colour": "Colore di accento",
    "Accent highlight colour (hex).": "Colore di accento evidenziato (hex).",
    "Surface colour": "Colore superficie",
    "Card/panel background colour (hex).": "Colore sfondo scheda/pannello (hex).",
    "Surface alt colour": "Colore superficie alternativo",
    "Alternate surface colour (hex).": "Colore superficie alternativo (hex).",
    "Text primary": "Testo primario",
    "Main body text colour (hex).": "Colore testo corpo principale (hex).",
    "Text muted": "Testo attenuato",
    "Secondary/lighter text colour (hex).": "Colore testo secondario/chiaro (hex).",
    "Enable if this is a dark colour scheme.": "Attiva se questo è uno schema colori scuro.",
    "Brand colours": "Colori del brand",
    "Surface colours": "Colori superficie",
    "Text colours": "Colori del testo",
    "colour scheme": "schema colori",
    "colour schemes": "schemi colori",

    # ── Navbar snippet ──
    "Show search": "Mostra ricerca",
    "navbar": "barra di navigazione",
    "navbars": "barre di navigazione",
    "Parent item": "Elemento genitore",
    "Leave empty for top-level items. Select a parent for dropdown sub-items.": "Lascia vuoto per le voci di primo livello. Seleziona un genitore per le sotto-voci a tendina.",
    "Link page": "Pagina collegata",
    "Used only when no page is selected.": "Usato solo quando nessuna pagina è selezionata.",
    "Open in new tab": "Apri in una nuova scheda",
    "Is CTA": "È CTA",
    "Render as a highlighted call-to-action button.": "Visualizza come pulsante invito all'azione evidenziato.",

    # ── Footer snippet ──
    "Twitter / X": "Twitter / X",
    "TikTok": "TikTok",
    "Short 'about' text displayed in the footer.": "Breve testo 'chi siamo' visualizzato nel piè di pagina.",
    "Copyright text": "Testo copyright",
    "Contact details": "Dettagli contatto",
    "Social links": "Link social",
    "footer": "piè di pagina",
    "footers": "piè di pagina",

    # ── FAQ snippet ──
    "Platform": "Piattaforma",
    "Question": "Domanda",
    "Answer": "Risposta",
    "Optional grouping label for the FAQ.": "Etichetta di raggruppamento opzionale per le FAQ.",
    "FAQ": "FAQ",
    "FAQs": "FAQ",

    # ── Testimonial snippet ──
    "Author name": "Nome autore",
    "Author role": "Ruolo autore",
    "Author photo": "Foto autore",
    "Show this testimonial more prominently.": "Mostra questa testimonianza in evidenza.",
    "testimonial": "testimonianza",
    "testimonials": "testimonianze",

    # ── Category snippets ──
    "Colour": "Colore",
    "Badge/label colour (hex).": "Colore badge/etichetta (hex).",
    "news category": "categoria notizia",
    "news categories": "categorie notizie",
    "Motorcycle": "Moto",
    "Rally": "Raduno",
    "Meeting": "Incontro",
    "Charity": "Beneficenza",
    "Race": "Gara",
    "event category": "categoria evento",
    "event categories": "categorie eventi",
    "photo tag": "tag foto",
    "photo tags": "tag foto",
    "partner category": "categoria partner",
    "partner categories": "categorie partner",

    # ── Press release snippet ──
    "Attachment": "Allegato",
    "PDF or document attachment.": "Allegato PDF o documento.",
    "Archived": "Archiviato",
    "press release": "comunicato stampa",
    "press releases": "comunicati stampa",

    # ── Brand asset snippet ──
    "Font": "Font",
    "Template": "Modello",
    "Preview image": "Immagine di anteprima",
    "brand asset": "risorsa del brand",
    "brand assets": "risorse del brand",

    # ── Aid skill snippet ──
    "Mechanics": "Meccanica",
    "Logistics": "Logistica",
    "Emergency": "Emergenza",
    "aid skill": "competenza soccorso",
    "aid skills": "competenze soccorso",

    # ── Product snippet ──
    "Inactive products are hidden from the storefront.": "I prodotti inattivi sono nascosti dalla vetrina.",
    "Grants voting rights": "Concede diritto di voto",
    "Grants gallery upload": "Concede caricamento galleria",
    "Grants event access": "Concede accesso eventi",
    "Grants discount": "Concede sconto",
    "Percentage discount on events when grants_discount is on.": "Sconto percentuale sugli eventi quando grants_discount è attivo.",
    "Product info": "Info prodotto",
    "Member privileges": "Privilegi socio",
    "product": "prodotto",

    # ── Photo upload model ──
    "Uploaded by": "Caricato da",
    "Optionally link this photo to an event.": "Collega facoltativamente questa foto a un evento.",
    "Approved at": "Approvato il",
    "Rejection reason": "Motivo del rifiuto",
    "Uploaded at": "Caricato il",
    "photo upload": "caricamento foto",
    "photo uploads": "caricamenti foto",
    "approved": "approvato",
    "pending": "in attesa",

    # ── Verification log ──
    "Not found": "Non trovato",
    "Wrong data": "Dati errati",
    "Expired membership": "Iscrizione scaduta",
    "Partner user": "Utente partner",
    "The partner owner who performed this verification.": "Il proprietario partner che ha effettuato questa verifica.",
    "Which secondary factor was used for verification.": "Quale fattore secondario è stato usato per la verifica.",
    "Result": "Risultato",
    "IP address": "Indirizzo IP",
    "verification log": "registro verifiche",
    "verification logs": "registri verifiche",

    # ── Verification error messages ──
    "Access denied. Only partner owners and staff can verify members.": "Accesso negato. Solo i proprietari partner e lo staff possono verificare i soci.",
    "Rate limit exceeded. Maximum 20 verification attempts per hour.": "Limite richieste superato. Massimo 20 tentativi di verifica all'ora.",
    "Account temporarily locked. Too many failed verification attempts. Please try again in 15 minutes.": "Account temporaneamente bloccato. Troppi tentativi di verifica falliti. Riprova tra 15 minuti.",
    "No member found with this card number.": "Nessun socio trovato con questo numero tessera.",
    "This member's membership has expired.": "L'iscrizione di questo socio è scaduta.",
    "Member verified successfully.": "Socio verificato con successo.",
    "N/A": "N/D",
    "Verification failed. The provided information does not match our records.": "Verifica fallita. Le informazioni fornite non corrispondono ai nostri archivi.",
    "Access denied. Your membership does not include gallery upload privileges.": "Accesso negato. La tua iscrizione non include i privilegi di caricamento galleria.",
    "Rejected by moderator.": "Rifiutato dal moderatore.",

    # ── Membership card template ──
    "Membership Card": "Tessera Associativa",
    "Card No.": "N. Tessera",
    "Expires": "Scadenza",
    "Barcode": "Codice a barre",
    "Download PDF": "Scarica PDF",
    "No membership card has been issued yet. Please contact the club administration.": "Nessuna tessera associativa è stata ancora emessa. Contatta l'amministrazione del club.",

    # ── Member directory template ──
    "Member Directory": "Elenco Soci",
    "Pagination": "Paginazione",
    "No members are currently visible in the directory.": "Nessun socio è attualmente visibile nell'elenco.",

    # ── Auth templates ──
    "Welcome back": "Bentornato",
    "Log in to access your profile, events, and club features.": "Accedi per visualizzare il tuo profilo, gli eventi e le funzionalità del club.",
    "Forgot your password?": "Hai dimenticato la password?",
    "Don't have an account?": "Non hai un account?",
    "Are you sure you want to log out?": "Sei sicuro di voler uscire?",
    "Go back to home": "Torna alla home",
    "Become a member": "Diventa socio",
    "Choose the membership plan that best fits your needs. Combine multiple products to customize your ex": "Scegli il piano di iscrizione più adatto alle tue esigenze. Combina più prodotti per personalizzare la tua esperienza",
    "Your plan": "Il tuo piano",
    "year": "anno",
    "Event registration": "Registrazione eventi",
    "Voting rights": "Diritto di voto",
    "Gallery upload": "Caricamento galleria",
    "%(percent)s%% discount on events": "%(percent)s%% di sconto sugli eventi",
    "Contact the club": "Contatta il club",
    "No membership plans available at this time.": "Nessun piano di iscrizione disponibile al momento.",
    "Reset your password": "Reimposta la tua password",
    "Enter your email address and we'll send you a link to reset your password.": "Inserisci il tuo indirizzo email e ti invieremo un link per reimpostare la password.",
    "Send reset link": "Invia link di reimpostazione",
    "Back to login": "Torna al login",
    "Active Member": "Socio Attivo",
    "Back to Directory": "Torna all'Elenco",
    "Create your account": "Crea il tuo account",
    "Join the club and access events, member directory, and more.": "Unisciti al club e accedi a eventi, elenco soci e altro.",
    "Already have an account?": "Hai già un account?",

    # ── Registration confirmation ──
    "Registration Confirmed": "Registrazione Confermata",

    # ── Payment pages ──
    "Amount": "Importo",
    "Bank Transfer Payment Required": "Pagamento con Bonifico Bancario Richiesto",
    "This is an automatic confirmation email. Please do not reply.": "Questa è un'email di conferma automatica. Si prega di non rispondere.",

    # ── Favorite events ──
    "My Favorite Events": "I Miei Eventi Preferiti",
    "Upcoming": "In programma",
    "Archive": "Archivio",
    "My Registrations": "Le Mie Registrazioni",
    "Events map": "Mappa eventi",
    "Map view of your favorite events": "Vista mappa dei tuoi eventi preferiti",
    "Remove from favorites": "Rimuovi dai preferiti",
    "Download calendar file": "Scarica file calendario",
    "ICS": "ICS",
    "You have not added any events to your favorites yet.": "Non hai ancora aggiunto eventi ai tuoi preferiti.",
    "Events Archive": "Archivio Eventi",
    "No past events in your favorites.": "Nessun evento passato nei tuoi preferiti.",

    # ── Payment flow ──
    "Payment": "Pagamento",
    "Bank Transfer Instructions": "Istruzioni Bonifico Bancario",
    "Transfer Details": "Dettagli Trasferimento",
    "Bank": "Banca",
    "Payment Reference": "Riferimento Pagamento",
    "Copy": "Copia",
    "Deadline": "Scadenza",
    "Back to my registrations": "Torna alle mie registrazioni",
    "Your payment was not completed. You can try again using the link below.": "Il tuo pagamento non è stato completato. Puoi riprovare usando il link qui sotto.",
    "Try again": "Riprova",
    "Choose Payment Method": "Scegli il Metodo di Pagamento",
    "Credit / Debit Card": "Carta di Credito / Debito",
    "Pay securely with Stripe": "Paga in sicurezza con Stripe",
    "Pay with your PayPal account": "Paga con il tuo account PayPal",
    "Pay via SEPA bank transfer": "Paga tramite bonifico bancario SEPA",
    "Payment Confirmed": "Pagamento Confermato",
    "Register for Event": "Registrati all'Evento",
    "Member discount": "Sconto socio",
    "Please correct the highlighted errors below.": "Correggi gli errori evidenziati qui sotto.",
    "Your Information": "Le Tue Informazioni",
    "Registration Details": "Dettagli Registrazione",
    "Registration Summary": "Riepilogo Registrazione",

    # ── Federation / Partner events ──
    "Partner Events": "Eventi dei Partner",
    "Breadcrumb": "Percorso di navigazione",
    "Club": "Club",
    "View on Google Maps": "Vedi su Google Maps",
    "View on partner site": "Vedi sul sito partner",
    "Events from our federated partner clubs.": "Eventi dai nostri club partner federati.",
    "Partner Club": "Club Partner",
    "All clubs": "Tutti i club",
    "Search events...": "Cerca eventi...",
    "No partner events found.": "Nessun evento partner trovato.",
    "Clear filters": "Cancella filtri",
    "Club Discussion": "Discussione del Club",
    "Comments are visible only to our club members. They are not shared with the partner club.": "I commenti sono visibili solo ai soci del nostro club. Non vengono condivisi con il club partner.",
    "Delete this comment?": "Eliminare questo commento?",
    "No comments yet. Be the first to start a discussion!": "Nessun commento ancora. Sii il primo ad avviare una discussione!",
    "Add a comment": "Aggiungi un commento",
    "Share your thoughts with fellow club members...": "Condividi i tuoi pensieri con gli altri soci del club...",
    "Post Comment": "Pubblica Commento",
    "Only active members can post comments.": "Solo i soci attivi possono pubblicare commenti.",
    "Are you interested?": "Sei interessato?",
    "going": "partecipo",
    "interested": "interessato",
    "maybe": "forse",
    "Only active members can express interest in partner events.": "Solo i soci attivi possono esprimere interesse per gli eventi partner.",

    # ── Navbar template ──
    "Main navigation": "Navigazione principale",
    "Toggle navigation": "Attiva/disattiva navigazione",
    "Search...": "Cerca...",
    "Search the site": "Cerca nel sito",
    "Submit search": "Invia ricerca",
    "Membership card": "Tessera associativa",
    "My events": "I miei eventi",
    "Member directory": "Elenco soci",

    # ── Mutual Aid access request ──
    "Request Access": "Richiedi Accesso",
    "Request Access to Mutual Aid": "Richiedi Accesso al Mutuo Soccorso",
    "Submit Request": "Invia Richiesta",
    "radius": "raggio",
    "Send Request": "Invia Richiesta",
    "Availability": "Disponibilità",
    "WhatsApp": "WhatsApp",
    "Send message": "Invia messaggio",
    "Send Aid Request": "Invia Richiesta di Soccorso",
    "Unlock Limit Reached": "Limite Sblocchi Raggiunto",
    "Contact Unlock Limit Reached": "Limite Sblocchi Contatti Raggiunto",
    "Please wait before unlocking more contacts, or use the contacts you have already unlocked.": "Attendi prima di sbloccare altri contatti, o usa i contatti che hai già sbloccato.",
    "Back to Mutual Aid": "Torna al Mutuo Soccorso",
    "Emergency Contacts": "Contatti di Emergenza",
    "Check back later or contact the club directly.": "Ricontrolla più tardi o contatta direttamente il club.",

    # ── Notification digest template ──
    "Notification digest": "Riepilogo notifiche",
    "View details": "Visualizza dettagli",
    "Notification history": "Cronologia notifiche",
    "ago": "fa",
    "No notifications yet.": "Nessuna notifica ancora.",
    "Unsubscribe": "Disiscriviti",
    "Confirm unsubscribe": "Conferma disiscrizione",
    "You can re-enable notifications at any time from your account settings.": "Puoi riattivare le notifiche in qualsiasi momento dalle impostazioni del tuo account.",
    "Invalid link": "Link non valido",
    "Unsubscribed": "Disiscritto",
    "You have been unsubscribed from these notifications. You will no longer receive them.": "Sei stato disiscritto da queste notifiche. Non le riceverai più.",
    "If you change your mind, you can re-enable notifications from your": "Se cambi idea, puoi riattivare le notifiche dalle tue",
    "account settings": "impostazioni account",

    # ── Events filters ──
    "Event period": "Periodo evento",
    "Past": "Passato",
    "Event filters": "Filtri evento",
    "Registration Open": "Registrazione Aperta",
}


def translate_po(input_path):
    """Read .po, fill in translations for remaining untranslated entries."""
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = content.split("\n\n")
    result_blocks = []
    stats = {"translated": 0, "fuzzy_fixed": 0, "skipped": 0, "already": 0}

    for block in blocks:
        lines = block.split("\n")
        
        msgid_lines = []
        msgstr_lines = []
        comment_lines = []
        is_fuzzy = False
        in_msgid = False
        in_msgstr = False
        has_msgid_plural = False
        
        for line in lines:
            if line == "#, fuzzy":
                is_fuzzy = True
                comment_lines.append(line)
            elif line.startswith("#"):
                comment_lines.append(line)
                in_msgid = False
                in_msgstr = False
            elif line.startswith("msgid_plural"):
                has_msgid_plural = True
                in_msgid = False
                in_msgstr = False
            elif line.startswith("msgid "):
                in_msgid = True
                in_msgstr = False
                msgid_lines.append(line[6:].strip('"'))
            elif line.startswith("msgstr"):
                in_msgid = False
                in_msgstr = True
                if line.startswith("msgstr "):
                    msgstr_lines.append(line[7:].strip('"'))
            elif line.startswith('"') and in_msgid:
                msgid_lines.append(line.strip('"'))
            elif line.startswith('"') and in_msgstr:
                msgstr_lines.append(line.strip('"'))
        
        msgid = "".join(msgid_lines)
        msgstr = "".join(msgstr_lines)
        
        # Skip plural forms, header, and empty msgids
        if has_msgid_plural or not msgid:
            result_blocks.append(block)
            continue
        
        needs_translation = (not msgstr) or is_fuzzy
        
        if needs_translation and msgid in TRANSLATIONS:
            new_msgstr = TRANSLATIONS[msgid]
            
            # Rebuild block
            new_lines = [l for l in comment_lines if l != "#, fuzzy"]
            new_lines.append(f'msgid "{msgid}"')
            new_lines.append(f'msgstr "{new_msgstr}"')
            
            result_blocks.append("\n".join(new_lines))
            if is_fuzzy:
                stats["fuzzy_fixed"] += 1
            else:
                stats["translated"] += 1
        elif not needs_translation:
            stats["already"] += 1
            result_blocks.append(block)
        else:
            stats["skipped"] += 1
            result_blocks.append(block)

    with open(input_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(result_blocks))
    
    return stats


if __name__ == "__main__":
    po_file = "locale/it/LC_MESSAGES/django.po"
    stats = translate_po(po_file)
    print("=== Translation Pass 2 Results ===")
    print(f"Already translated:  {stats['already']}")
    print(f"Newly translated:    {stats['translated']}")
    print(f"Fuzzy fixed:         {stats['fuzzy_fixed']}")
    print(f"Still untranslated:  {stats['skipped']}")
    print(f"Total processed:     {sum(stats.values())}")
