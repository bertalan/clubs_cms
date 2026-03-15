#!/usr/bin/env python3
"""
Batch-translate the Italian .po file for ClubCMS.
Handles all untranslated and fuzzy entries.
"""
import re
import sys

# ──────────────────────────────────────────────────────────
#  TRANSLATION DICTIONARY  (English → Italian)
# ──────────────────────────────────────────────────────────
TRANSLATIONS = {
    # ── AppConfig verbose_name ──
    "Core": "Nucleo",
    "Events": "Eventi",
    "Federation": "Federazione",
    "Members": "Soci",
    "Mutual Aid": "Mutuo Soccorso",
    "Notifications": "Notifiche",
    "Website": "Sito Web",

    # ── Model Meta verbose_name / verbose_name_plural ──
    "Federated Club": "Club Federato",
    "Federated Clubs": "Club Federati",
    "External Event": "Evento Esterno",
    "External Events": "Eventi Esterni",
    "External Event Interest": "Interesse Evento Esterno",
    "External Event Interests": "Interessi Eventi Esterni",
    "External Event Comment": "Commento Evento Esterno",
    "External Event Comments": "Commenti Eventi Esterni",
    "Club User": "Utente Club",
    "Club Users": "Utenti Club",
    "Event Registration": "Registrazione Evento",
    "Event Registrations": "Registrazioni Evento",
    "Event Favorite": "Evento Preferito",
    "Event Favorites": "Eventi Preferiti",
    "Event page": "Pagina evento",

    # ── Events / Registration fields ──
    "Confirmed": "Confermato",
    "Waitlist": "Lista d'attesa",
    "Pending": "In attesa",
    "Paid": "Pagato",
    "Refunded": "Rimborsato",
    "Stripe": "Stripe",
    "PayPal": "PayPal",
    "Bank Transfer": "Bonifico Bancario",
    "User": "Utente",
    "Status": "Stato",
    "Number of guests": "Numero di ospiti",
    "Payment status": "Stato pagamento",
    "Payment provider": "Fornitore pagamento",
    "Payment ID": "ID pagamento",
    "External payment reference from the provider.": "Riferimento di pagamento esterno del fornitore.",
    "Payment session ID": "ID sessione pagamento",
    "Checkout Session ID (Stripe) or Order ID (PayPal).": "ID sessione checkout (Stripe) o ID ordine (PayPal).",
    "Payment amount": "Importo pagamento",
    "Unique reference for bank transfers (e.g. EVT-00123-A7B3).": "Riferimento univoco per bonifici bancari (es. EVT-00123-A7B3).",
    "Payment expires at": "Pagamento scade il",
    "Deadline for bank transfer payments.": "Scadenza per i pagamenti con bonifico bancario.",
    "Guest": "Ospite",
    "Days before event": "Giorni prima dell'evento",
    "Hours before event": "Ore prima dell'evento",
    "Minutes before event": "Minuti prima dell'evento",
    "Discount percent": "Percentuale sconto",
    "Label": "Etichetta",
    "Display label for this tier, e.g. 'Early Bird'.": "Etichetta per questa fascia, es. 'Prenotazione anticipata'.",
    "The time offset must be greater than zero.": "L'intervallo di tempo deve essere maggiore di zero.",
    "Added at": "Aggiunto il",
    "Registered": "Registrato",
    "Registered at": "Registrato il",
    "Cancelled": "Annullato",
    "Event": "Evento",
    "Payment reference": "Riferimento pagamento",
    "Is registration deadline": "È scadenza registrazione",

    # ── Events notification messages ──
    "Payment expired: {event}": "Pagamento scaduto: {event}",
    "Your bank transfer for {event} was not received in time. Your registration has been cancelled.":
        "Il tuo bonifico per {event} non è stato ricevuto in tempo. La tua registrazione è stata annullata.",
    "Spot available: {event}": "Posto disponibile: {event}",
    "A spot has opened up! You have been promoted from the waitlist for {event}.":
        "Si è liberato un posto! Sei stato promosso dalla lista d'attesa per {event}.",
    "Your membership does not include event registration. Please upgrade your membership.":
        "La tua iscrizione non include la registrazione agli eventi. Aggiorna la tua iscrizione.",
    "Please wait before toggling again.": "Attendi prima di cambiare di nuovo.",
    "Payment instructions: {event}": "Istruzioni di pagamento: {event}",
    "Please complete the bank transfer of €{amount} with reference {ref} by {expires}.":
        "Completa il bonifico di €{amount} con causale {ref} entro il {expires}.",
    "Payment service temporarily unavailable. Please try again.":
        "Servizio di pagamento temporaneamente non disponibile. Riprova più tardi.",

    # ── Federation model help_text ──
    "Display name of the partner club": "Nome del club partner",
    "URL-safe identifier": "Identificatore URL-safe",
    "Partner site base URL": "URL base del sito partner",
    "Optional logo URL": "URL logo (opzionale)",
    "Their public API key (given to us)": "La loro chiave API pubblica (data a noi)",
    "Our key we gave them (auto-generated)": "La nostra chiave data a loro (auto-generata)",
    "Share our events with this partner": "Condividi i nostri eventi con questo partner",
    "Auto-approve imported events": "Approva automaticamente gli eventi importati",
    "Sanitized HTML": "HTML sanitizzato",

    # ── Member form fields ──
    "Select member": "Seleziona socio",
    "Number of extra people coming with you (not counting yourself or your passenger). Example: 2":
        "Numero di persone extra che vengono con te (esclusi te stesso e il tuo passeggero). Esempio: 2",
    "List each guest on a separate line. Example:\\nMario Rossi\\nLucia Bianchi":
        "Elenca ogni ospite su una riga separata. Esempio:\\nMario Rossi\\nLucia Bianchi",
    "Allergies, dietary needs, special requests, or anything the organizers should know.":
        "Allergie, esigenze alimentari, richieste speciali o qualsiasi cosa gli organizzatori debbano sapere.",
    "Check this if someone will ride with you as a passenger on your motorcycle.":
        "Seleziona se qualcuno viaggerà con te come passeggero sulla tua moto.",
    "If your passenger is already a club member, enable this to select them from the list.":
        "Se il tuo passeggero è già socio del club, attiva questa opzione per selezionarlo dalla lista.",
    "Example: Marco": "Esempio: Marco",
    "Example: Verdi": "Esempio: Verdi",
    "Example: marco.verdi@email.com": "Esempio: marco.verdi@email.com",
    "Italian tax identification code, 16 characters. Example: VRDMRC85M01H501Z":
        "Codice fiscale italiano, 16 caratteri. Esempio: VRDMRC85M01H501Z",
    "Example: 1985-08-01": "Esempio: 1985-08-01",
    "Name and phone number to call in case of emergency. Example: Anna Verdi +39 340 7654321":
        "Nome e numero di telefono da chiamare in caso di emergenza. Esempio: Anna Verdi +39 340 7654321",
    "Your legal first name. Example: Maria": "Il tuo nome legale. Esempio: Maria",
    "Your family name. Example: Rossi": "Il tuo cognome. Esempio: Rossi",
    "Guest names": "Nomi degli ospiti",
    "Passenger first name": "Nome del passeggero",
    "Emergency contact": "Contatto di emergenza",
    "Start typing a name to search registered members.": "Inizia a digitare un nome per cercare i soci registrati.",
    "Include country prefix. Example: +39 333 1234567": "Includi il prefisso internazionale. Esempio: +39 333 1234567",
    "We will send your registration confirmation here.": "Invieremo la conferma di registrazione qui.",

    # ── Admin panels (members) ──
    "Personal": "Personale",
    "Identity": "Identità",
    "Address": "Indirizzo",
    "Membership": "Iscrizione",
    "Privacy": "Privacy",

    # ── Member model fields ──
    "Username": "Nome utente",
    "First name": "Nome",
    "Last name": "Cognome",
    "Email": "Email",
    "Display name": "Nome visualizzato",
    "Phone": "Telefono",
    "Mobile": "Cellulare",
    "Birth date": "Data di nascita",
    "Birth place": "Luogo di nascita",
    "Photo": "Foto",
    "Bio": "Biografia",
    "Fiscal code": "Codice fiscale",
    "Document type": "Tipo documento",
    "Document number": "Numero documento",
    "Document expiry": "Scadenza documento",
    "City": "Città",
    "Province": "Provincia",
    "Postal code": "CAP",
    "Country": "Paese",
    "Card number": "Numero tessera",
    "Membership date": "Data iscrizione",
    "Membership expiry": "Scadenza iscrizione",
    "Is active": "È attivo",
    "Products": "Prodotti",
    "Show in directory": "Mostra nell'elenco",
    "Public profile": "Profilo pubblico",
    "Show real name to members": "Mostra nome reale ai soci",
    "Newsletter": "Newsletter",
    "Email notifications": "Notifiche email",
    "Push notifications": "Notifiche push",
    "News updates": "Aggiornamenti notizie",
    "Event updates": "Aggiornamenti eventi",
    "Event reminders": "Promemoria eventi",
    "Membership alerts": "Avvisi iscrizione",
    "Partner updates": "Aggiornamenti partner",
    "Aid requests": "Richieste di aiuto",
    "Partner events": "Eventi dei partner",
    "Partner event comments": "Commenti eventi partner",
    "Digest frequency": "Frequenza riepilogo",
    "Aid available": "Disponibile per mutuo soccorso",
    "Aid radius km": "Raggio soccorso (km)",
    "Aid location city": "Città posizione soccorso",
    "Aid coordinates": "Coordinate soccorso",
    "Aid notes": "Note soccorso",

    # ── Antispam ──
    "Spam detected. Access denied.": "Spam rilevato. Accesso negato.",
    "This submission looks like spam.": "Questo invio sembra spam.",
    "Too many requests. Please try again later.": "Troppe richieste. Riprova più tardi.",
    "Are you human?": "Sei umano?",
    "Verify": "Verifica",
    "I am human": "Sono umano",
    "Verification failed. Please try again.": "Verifica fallita. Riprova.",
    "Remember me": "Ricordami",

    # ── Website / Page models ──
    "Home Page": "Pagina Iniziale",
    "Content Page": "Pagina Contenuto",
    "News Page": "Pagina Notizie",
    "News Index Page": "Indice Notizie",
    "Gallery Page": "Pagina Galleria",
    "Gallery Index Page": "Indice Galleria",
    "Events Index Page": "Indice Eventi",
    "Contact Page": "Pagina Contatti",
    "Title": "Titolo",
    "Subtitle": "Sottotitolo",
    "Body": "Corpo",
    "Image": "Immagine",
    "Caption": "Didascalia",
    "Author": "Autore",
    "Date": "Data",
    "Published": "Pubblicato",
    "Draft": "Bozza",
    "Summary": "Riepilogo",
    "Tags": "Tag",
    "Category": "Categoria",
    "Categories": "Categorie",
    "Slug": "Slug",
    "SEO Title": "Titolo SEO",
    "Search Description": "Descrizione per la ricerca",
    "Description": "Descrizione",
    "Content": "Contenuto",
    "Location": "Luogo",
    "Start date": "Data inizio",
    "End date": "Data fine",
    "Start time": "Ora inizio",
    "End time": "Ora fine",
    "All day": "Tutto il giorno",
    "Registration required": "Registrazione obbligatoria",
    "Max participants": "Partecipanti massimi",
    "Price": "Prezzo",
    "Free": "Gratuito",
    "Featured": "In evidenza",
    "Promoted": "Promosso",
    "Featured image": "Immagine in evidenza",

    # ── StreamField blocks ──
    "Heading": "Intestazione",
    "Paragraph": "Paragrafo",
    "Quote": "Citazione",
    "Rich Text": "Testo Formattato",
    "Rich text": "Testo formattato",
    "Link": "Link",
    "URL": "URL",
    "Button": "Pulsante",
    "Button text": "Testo pulsante",
    "Button link": "Link pulsante",
    "Call to Action": "Invito all'azione",
    "Background color": "Colore di sfondo",
    "Background image": "Immagine di sfondo",
    "Text color": "Colore del testo",
    "Alignment": "Allineamento",
    "Left": "Sinistra",
    "Center": "Centro",
    "Right": "Destra",
    "Full width": "Larghezza piena",
    "Card": "Scheda",
    "Cards": "Schede",
    "Column": "Colonna",
    "Columns": "Colonne",
    "Section": "Sezione",
    "Hero": "Hero",
    "Hero section": "Sezione Hero",
    "Embed": "Incorporamento",
    "Embed URL": "URL incorporamento",
    "Video": "Video",
    "Document": "Documento",
    "Documents": "Documenti",
    "File": "File",
    "Download": "Scarica",
    "Gallery": "Galleria",
    "Slider": "Slider",
    "Testimonial": "Testimonianza",
    "Testimonials": "Testimonianze",
    "Icon": "Icona",
    "Feature": "Caratteristica",
    "Features": "Caratteristiche",
    "Table": "Tabella",
    "Map": "Mappa",
    "Code": "Codice",
    "Accordion": "Fisarmonica",
    "Tab": "Scheda",
    "Tabs": "Schede",
    "Spacer": "Spaziatore",
    "Divider": "Divisore",
    "HTML": "HTML",
    "Raw HTML": "HTML Grezzo",

    # ── Wagtail / Settings ──
    "Site Settings": "Impostazioni Sito",
    "Site settings": "Impostazioni sito",
    "Site Name": "Nome Sito",
    "Site name": "Nome sito",
    "Tagline": "Slogan",
    "Logo": "Logo",
    "Favicon": "Favicon",
    "Social Media": "Social Media",
    "Facebook": "Facebook",
    "Instagram": "Instagram",
    "Twitter": "Twitter",
    "YouTube": "YouTube",
    "LinkedIn": "LinkedIn",
    "Footer": "Piè di pagina",
    "Footer text": "Testo piè di pagina",
    "Copyright": "Copyright",
    "Analytics": "Analisi",
    "Google Analytics ID": "ID Google Analytics",
    "Theme": "Tema",
    "Color scheme": "Schema colori",
    "Primary color": "Colore primario",
    "Secondary color": "Colore secondario",
    "Accent color": "Colore di accento",
    "Dark mode": "Modalità scura",
    "Light mode": "Modalità chiara",
    "Auto": "Automatico",

    # ── Notifications ──
    "Notification": "Notifica",
    "Notification Type": "Tipo Notifica",
    "Notification type": "Tipo notifica",
    "Message": "Messaggio",
    "Read": "Letto",
    "Unread": "Non letto",
    "Sent": "Inviato",
    "Mark as read": "Segna come letto",
    "Mark all as read": "Segna tutto come letto",
    "Delete": "Elimina",
    "No notifications": "Nessuna notifica",
    "Notification Settings": "Impostazioni Notifiche",
    "Notification settings": "Impostazioni notifiche",
    "Enable email notifications": "Abilita notifiche email",
    "Enable push notifications": "Abilita notifiche push",
    "Notification Preference": "Preferenza Notifica",
    "Notification Preferences": "Preferenze Notifica",
    "Channel": "Canale",
    "Channels": "Canali",

    # ── Mutual Aid ──
    "Aid Request": "Richiesta di Soccorso",
    "Aid Requests": "Richieste di Soccorso",
    "Aid Offer": "Offerta di Soccorso",
    "Aid Offers": "Offerte di Soccorso",
    "Aid Category": "Categoria Soccorso",
    "Aid Categories": "Categorie Soccorso",
    "Urgency": "Urgenza",
    "Low": "Bassa",
    "Medium": "Media",
    "High": "Alta",
    "Critical": "Critica",
    "Open": "Aperto",
    "Closed": "Chiuso",
    "In Progress": "In Corso",
    "Resolved": "Risolto",
    "Latitude": "Latitudine",
    "Longitude": "Longitudine",
    "Radius": "Raggio",
    "Available": "Disponibile",
    "Unavailable": "Non disponibile",
    "Skills": "Competenze",
    "Equipment": "Attrezzatura",
    "Notes": "Note",
    "Active": "Attivo",
    "Inactive": "Inattivo",
    "Expires at": "Scade il",
    "Created at": "Creato il",
    "Updated at": "Aggiornato il",
    "Created by": "Creato da",

    # ── Common actions / UI ──
    "Save": "Salva",
    "Cancel": "Annulla",
    "Edit": "Modifica",
    "Add": "Aggiungi",
    "Remove": "Rimuovi",
    "Search": "Cerca",
    "Filter": "Filtra",
    "Sort": "Ordina",
    "View": "Visualizza",
    "Details": "Dettagli",
    "Back": "Indietro",
    "Next": "Avanti",
    "Previous": "Precedente",
    "Submit": "Invia",
    "Confirm": "Conferma",
    "Close": "Chiudi",
    "Update": "Aggiorna",
    "Yes": "Sì",
    "No": "No",
    "None": "Nessuno",
    "All": "Tutti",
    "Name": "Nome",
    "Type": "Tipo",
    "Actions": "Azioni",
    "Loading...": "Caricamento...",
    "Error": "Errore",
    "Success": "Successo",
    "Warning": "Avviso",
    "Info": "Info",

    # ── Wagtail snippets ──
    "Snippet": "Frammento",
    "Snippets": "Frammenti",
    "Menu item": "Voce di menu",
    "Menu items": "Voci di menu",
    "Navigation": "Navigazione",
    "External link": "Link esterno",
    "Internal link": "Link interno",
    "Page": "Pagina",
    "Pages": "Pagine",
    "Parent page": "Pagina genitore",
    "Order": "Ordine",
    "Sort order": "Ordine di ordinamento",
    "Show in menu": "Mostra nel menu",

    # ── Uploads / Gallery ──
    "Upload": "Caricamento",
    "Uploads": "Caricamenti",
    "Album": "Album",
    "Albums": "Album",
    "Upload date": "Data caricamento",
    "File size": "Dimensione file",
    "File type": "Tipo file",
    "Width": "Larghezza",
    "Height": "Altezza",
    "Alt text": "Testo alternativo",
    "Thumbnail": "Miniatura",

    # ── Partners ──
    "Partner": "Partner",
    "Partners": "Partner",
    "Partner Category": "Categoria Partner",
    "Partner Categories": "Categorie Partner",
    "Discount": "Sconto",
    "Benefit": "Beneficio",
    "Benefits": "Benefici",
    "Valid from": "Valido da",
    "Valid until": "Valido fino a",
    "Terms and conditions": "Termini e condizioni",

    # ── Press Office ──
    "Press Release": "Comunicato Stampa",
    "Press Releases": "Comunicati Stampa",

    # ── Registration form ──
    "Registration": "Registrazione",
    "Register": "Registrati",
    "Login": "Accedi",
    "Logout": "Esci",
    "Sign up": "Registrati",
    "Sign in": "Accedi",
    "Password": "Password",
    "Confirm password": "Conferma password",
    "Forgot password?": "Password dimenticata?",
    "Reset password": "Reimposta password",
    "Change password": "Cambia password",
    "Account": "Account",
    "Profile": "Profilo",
    "Settings": "Impostazioni",
    "Preferences": "Preferenze",

    # ── Event-specific ──
    "Upcoming events": "Prossimi eventi",
    "Past events": "Eventi passati",
    "No upcoming events": "Nessun evento in programma",
    "Event details": "Dettagli evento",
    "Register for event": "Registrati all'evento",
    "Cancel registration": "Annulla registrazione",
    "Registration closed": "Registrazioni chiuse",
    "Event full": "Evento al completo",
    "Spots available": "Posti disponibili",
    "Organizer": "Organizzatore",
    "Route": "Percorso",
    "Route map": "Mappa percorso",
    "Distance": "Distanza",
    "Difficulty": "Difficoltà",
    "Easy": "Facile",
    "Moderate": "Moderata",
    "Hard": "Difficile",
    "Expert": "Esperto",
    "GPX file": "File GPX",
    "Route description": "Descrizione percorso",
    "Waypoints": "Punti tappa",
    "Departure": "Partenza",
    "Arrival": "Arrivo",
    "Duration": "Durata",

    # ── Verification / Moderation ──
    "Verified": "Verificato",
    "Not verified": "Non verificato",
    "Verification": "Verifica",
    "Verification code": "Codice di verifica",
    "Verification token": "Token di verifica",
    "Approved": "Approvato",
    "Rejected": "Rifiutato",
    "Pending review": "In attesa di revisione",
    "Moderation": "Moderazione",
    "Report": "Segnala",
    "Reported": "Segnalato",
    "Ban": "Banna",
    "Banned": "Bannato",

    # ── Interest / Comment ──
    "Interested": "Interessato",
    "Maybe": "Forse",
    "Going": "Partecipo",
    "Interest level": "Livello di interesse",
    "Comment": "Commento",
    "Comments": "Commenti",
    "Add comment": "Aggiungi commento",
    "Edit comment": "Modifica commento",
    "Delete comment": "Elimina commento",
    "Reply": "Rispondi",

    # ── Sync / Federation ──
    "Last sync": "Ultima sincronizzazione",
    "Last error": "Ultimo errore",
    "Is active": "È attivo",
    "Is approved": "È approvato",
    "Source club": "Club di origine",
    "External ID": "ID esterno",
    "Event name": "Nome evento",
    "Location name": "Nome luogo",
    "Location address": "Indirizzo luogo",
    "Event status": "Stato evento",
    "Image URL": "URL immagine",
    "Detail URL": "URL dettaglio",
    "Is hidden": "È nascosto",
    "Fetched at": "Recuperato il",
    "Short code": "Codice breve",
    "Base URL": "URL base",
    "Logo URL": "URL logo",
    "API key": "Chiave API",

    # ── Misc field labels ──
    "Scheduled": "Programmato",
    "Moved Online": "Spostato Online",
    "Postponed": "Posticipato",
    "EventScheduled": "Programmato",
    "EventCancelled": "Annullato",
    "EventPostponed": "Posticipato",
    "EventMovedOnline": "Spostato Online",
    "No": "No",
    "Yes": "Sì",
    "True": "Vero",
    "False": "Falso",
    "Enabled": "Abilitato",
    "Disabled": "Disabilitato",

    # ── SEO / JSON-LD ──
    "Structured data": "Dati strutturati",
    "Schema type": "Tipo schema",
    "JSON-LD": "JSON-LD",
    "Open Graph": "Open Graph",
    "Twitter Card": "Twitter Card",
    "Canonical URL": "URL canonico",
    "Robots": "Robots",
    "Sitemap": "Mappa del sito",
    "sitemap.xml": "sitemap.xml",

    # ── Wagtail admin ──
    "Dashboard": "Pannello di controllo",
    "Explorer": "Esplora",
    "Images": "Immagini",
    "Search terms": "Termini di ricerca",
    "Search promotions": "Promozioni di ricerca",
    "Redirects": "Reindirizzamenti",
    "Users": "Utenti",
    "Groups": "Gruppi",
    "Sites": "Siti",
    "Collections": "Collezioni",
    "Workflows": "Flussi di lavoro",
    "Tasks": "Compiti",
    "Locked pages": "Pagine bloccate",
    "Aging pages": "Pagine datate",
    "Reports": "Report",

    # ── i18n / locale ──
    "Language": "Lingua",
    "English": "Inglese",
    "Italian": "Italiano",
    "French": "Francese",
    "German": "Tedesco",
    "Spanish": "Spagnolo",
    "Select language": "Seleziona lingua",

    # ── Form validations ──
    "This field is required.": "Questo campo è obbligatorio.",
    "Enter a valid email address.": "Inserisci un indirizzo email valido.",
    "Enter a valid URL.": "Inserisci un URL valido.",
    "Enter a valid value.": "Inserisci un valore valido.",
    "Ensure this value is greater than or equal to %(limit_value)s.": "Assicurati che questo valore sia maggiore o uguale a %(limit_value)s.",
    "Ensure this value is less than or equal to %(limit_value)s.": "Assicurati che questo valore sia minore o uguale a %(limit_value)s.",

    # ── Privacy / GDPR ──
    "I accept the <a href='/privacy/' target='_blank' rel='noopener'>terms and conditions</a>":
        "Accetto i <a href='/privacy/' target='_blank' rel='noopener'>termini e condizioni</a>",

    # ── Color Scheme choices ──
    "light": "chiaro",
    "dark": "scuro",
    "auto": "automatico",
    "Light": "Chiaro",
    "Dark": "Scuro",

    # ── PWA / Push ──
    "Install app": "Installa l'app",
    "Subscribe to notifications": "Iscriviti alle notifiche",
    "Unsubscribe from notifications": "Disiscriviti dalle notifiche",
    "Offline": "Offline",
    "Online": "Online",
    "Update available": "Aggiornamento disponibile",
    "Refresh": "Aggiorna",

    # ── Contribution / Moderation ──
    "Contribution": "Contributo",
    "Contributions": "Contributi",
    "Contributor": "Contributore",
    "Contributors": "Contributori",
    "Suggestion": "Suggerimento",
    "Suggestions": "Suggerimenti",
    "Pending approval": "In attesa di approvazione",

    # ── Time-related ──
    "Today": "Oggi",
    "Tomorrow": "Domani",
    "Yesterday": "Ieri",
    "This week": "Questa settimana",
    "Next week": "Prossima settimana",
    "This month": "Questo mese",
    "Next month": "Prossimo mese",
    "Daily": "Giornaliero",
    "Weekly": "Settimanale",
    "Monthly": "Mensile",
    "Never": "Mai",

    # ── Product / membership tiers ──
    "Product": "Prodotto",
    "Product name": "Nome prodotto",
    "Product type": "Tipo prodotto",
    "Includes event registration": "Include registrazione eventi",
    "Annual": "Annuale",

    # ── Email subjects / messages ──
    "Welcome": "Benvenuto",
    "Goodbye": "Arrivederci",
    "Thank you": "Grazie",
    "Confirmation": "Conferma",
    "Reminder": "Promemoria",
    "Alert": "Avviso",
    "Important": "Importante",
    "New": "Nuovo",

    # ── Common model field names as verbose_name ──
    "address": "indirizzo",
    "city": "città",
    "province": "provincia",
    "postal code": "CAP",
    "country": "paese",
    "phone": "telefono",
    "mobile": "cellulare",
    "email": "email",
    "first name": "nome",
    "last name": "cognome",
    "display name": "nome visualizzato",
    "birth date": "data di nascita",
    "birth place": "luogo di nascita",
    "photo": "foto",
    "bio": "biografia",
    "fiscal code": "codice fiscale",
    "document type": "tipo documento",
    "document number": "numero documento",
    "document expiry": "scadenza documento",
    "card number": "numero tessera",
    "membership date": "data iscrizione",
    "membership expiry": "scadenza iscrizione",
    "is active": "è attivo",
    "show in directory": "mostra nell'elenco",
    "public profile": "profilo pubblico",
    "show real name to members": "mostra nome reale ai soci",
    "newsletter": "newsletter",
    "email notifications": "notifiche email",
    "push notifications": "notifiche push",
    "news updates": "aggiornamenti notizie",
    "event updates": "aggiornamenti eventi",
    "event reminders": "promemoria eventi",
    "membership alerts": "avvisi iscrizione",
    "partner updates": "aggiornamenti partner",
    "aid requests": "richieste di aiuto",
    "partner events": "eventi dei partner",
    "partner event comments": "commenti eventi partner",
    "digest frequency": "frequenza riepilogo",
    "aid available": "disponibile per mutuo soccorso",
    "aid radius km": "raggio soccorso (km)",
    "aid location city": "città posizione soccorso",
    "aid coordinates": "coordinate soccorso",
    "aid notes": "note soccorso",
    "products": "prodotti",

    # ── mutual_aid model strings ──
    "request": "richiesta",
    "offer": "offerta",
    "Roadside assistance": "Assistenza stradale",
    "Mechanical help": "Aiuto meccanico",
    "Transport": "Trasporto",
    "Accommodation": "Alloggio",
    "Medical": "Medico",
    "Other": "Altro",
    "other": "altro",
    "Description of the problem or assistance needed": "Descrizione del problema o dell'assistenza necessaria",
    "Title of the aid request": "Titolo della richiesta di soccorso",
    "Aid request": "Richiesta di soccorso",
    "Aid offer": "Offerta di soccorso",
    "Responder": "Soccorritore",
    "Requester": "Richiedente",
    "Response": "Risposta",
    "Responses": "Risposte",
    "Aid Response": "Risposta Soccorso",
    "Aid Responses": "Risposte Soccorso",
    "Response message": "Messaggio di risposta",
    "Estimated arrival": "Arrivo stimato",
    "Can help": "Può aiutare",
    "On the way": "In arrivo",
    "Arrived": "Arrivato",
    "Completed": "Completato",
    "Did not show": "Non presentato",

    # ── Notification types ──
    "event_registration": "registrazione_evento",
    "event_reminder": "promemoria_evento",
    "event_update": "aggiornamento_evento",
    "membership_expiry": "scadenza_iscrizione",
    "aid_request": "richiesta_soccorso",
    "aid_response": "risposta_soccorso",
    "partner_event": "evento_partner",
    "system": "sistema",
    "general": "generale",
    "email": "email",
    "push": "push",
    "in_app": "in_app",
    "both": "entrambi",

    # ── Additional form/template strings ──
    "Are you sure?": "Sei sicuro?",
    "This action cannot be undone.": "Questa azione non può essere annullata.",
    "No results found.": "Nessun risultato trovato.",
    "Showing %(start)s to %(end)s of %(total)s results": "Risultati da %(start)s a %(end)s di %(total)s",
    "Page %(current)s of %(total)s": "Pagina %(current)s di %(total)s",
    "Items per page": "Elementi per pagina",
    "Apply": "Applica",
    "Reset": "Reimposta",
    "Clear": "Cancella",
    "Select all": "Seleziona tutto",
    "Deselect all": "Deseleziona tutto",
    "Export": "Esporta",
    "Import": "Importa",
    "CSV": "CSV",
    "PDF": "PDF",
    "Print": "Stampa",

    # ── Registration flow ──
    "Passenger": "Passeggero",
    "Has passenger": "Ha passeggero",
    "Passenger is member": "Il passeggero è socio",
    "Passenger name": "Nome passeggero",
    "Number of extra guests": "Numero di ospiti extra",
    "Special requests": "Richieste speciali",
    "Total": "Totale", 
    "Subtotal": "Subtotale",
    "Tax": "Tasse",
    "Registration date": "Data registrazione",
    "Registration status": "Stato registrazione",
    "Confirm registration": "Conferma registrazione",
    "cancel": "annulla",
    "Extra content": "Contenuto extra",
    
    # ── More website model strings ──
    "Hero image": "Immagine hero",
    "Intro": "Introduzione",
    "intro": "introduzione",
    "Related pages": "Pagine correlate",
    "Related links": "Link correlati",
    "Sidebar": "Barra laterale",
    "Header": "Intestazione",
    "Main content": "Contenuto principale",
    "Call to action": "Invito all'azione",
    "call to action": "invito all'azione",
    "Banner": "Banner",
    "Promo": "Promozione",
    "Highlight": "In evidenza",
    "Text": "Testo",
    "text": "testo",
    "Block type": "Tipo blocco",

    # ── Error messages ──
    "An error occurred.": "Si è verificato un errore.",
    "Permission denied.": "Permesso negato.",
    "Not found.": "Non trovato.",
    "Page not found": "Pagina non trovata",
    "Server error": "Errore del server",
    "Bad request": "Richiesta non valida",
    "Forbidden": "Vietato",
    "Unauthorized": "Non autorizzato",
    "Service unavailable": "Servizio non disponibile",

    # ── Pricing tiers ──
    "Early Bird": "Prenotazione anticipata",
    "Regular": "Regolare",
    "Late": "Tardivo",
    "VIP": "VIP",
    "Standard": "Standard",
    "Premium": "Premium",
    "Basic": "Base",

    # ── Additional wagtail/website fields ──
    "Published date": "Data pubblicazione",
    "Publish date": "Data di pubblicazione",
    "Expire date": "Data di scadenza",
    "Go live date": "Data di pubblicazione",
    "First published at": "Prima pubblicazione",
    "Last published at": "Ultima pubblicazione",
    "Latest revision created at": "Ultima revisione creata il",
    "Live": "Pubblicato",
    "Has unpublished changes": "Ha modifiche non pubblicate",
    "Locked": "Bloccato",
    "Locked by": "Bloccato da",
    "Locked at": "Bloccato il",

    # ── Menu/admin strings Wagtail ──
    "Menu label": "Etichetta menu",
    "Admin display title": "Titolo visualizzazione admin",

    # ── Additional mutual aid ──
    "Accept": "Accetta",
    "Reject": "Rifiuta",
    "Withdraw": "Ritira",
    "Confirm arrival": "Conferma arrivo",
    "Mark as resolved": "Segna come risolto",
    "Request help": "Richiedi aiuto",
    "Offer help": "Offri aiuto",
    "Your location": "La tua posizione",
    "Distance from you": "Distanza da te",
    "km": "km",

    # ── Additional notification messages ──
    "You have %(count)s new notifications": "Hai %(count)s nuove notifiche",
    "No new notifications": "Nessuna nuova notifica",
    "View all notifications": "Vedi tutte le notifiche",
    "Notification sent": "Notifica inviata",
    "Notification deleted": "Notifica eliminata",

    # ── Choices for document_type ──
    "ID Card": "Carta d'identità",
    "Passport": "Passaporto",
    "Driving License": "Patente di guida",

    # ── Additional registration ──
    "Check-in": "Check-in",
    "Checked in": "Check-in effettuato",
    "Not checked in": "Check-in non effettuato",
    "QR Code": "Codice QR",
    "Scan QR code": "Scansiona codice QR",

    # ── Additional patterns ──
    "per year": "all'anno",
    "per month": "al mese",
    "valid": "valido",
    "invalid": "non valido",
    "required": "obbligatorio",
    "optional": "opzionale",
    "default": "predefinito",
    "custom": "personalizzato",
    "public": "pubblico",
    "private": "privato",
    "visible": "visibile",
    "hidden": "nascosto",
    "enabled": "abilitato",
    "disabled": "disabilitato",
}

# ──────────────────────────────────────────────────────────

def translate_po(input_path, output_path):
    """Read .po, fill in translations, write output."""
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into blocks separated by blank lines
    blocks = content.split("\n\n")
    result_blocks = []
    stats = {"translated": 0, "fuzzy_fixed": 0, "skipped": 0, "already": 0}

    for block in blocks:
        lines = block.split("\n")
        
        # Parse the block
        msgid_lines = []
        msgstr_lines = []
        other_lines = []
        is_fuzzy = False
        in_msgid = False
        in_msgstr = False
        msgid_start = -1
        msgstr_start = -1
        
        for i, line in enumerate(lines):
            if line == "#, fuzzy":
                is_fuzzy = True
                other_lines.append((i, line))
            elif line.startswith("msgid "):
                in_msgid = True
                in_msgstr = False
                msgid_start = i
                val = line[6:].strip('"')
                msgid_lines.append(val)
            elif line.startswith("msgstr "):
                in_msgid = False
                in_msgstr = True
                msgstr_start = i
                val = line[7:].strip('"')
                msgstr_lines.append(val)
            elif line.startswith('"') and in_msgid:
                msgid_lines.append(line.strip('"'))
            elif line.startswith('"') and in_msgstr:
                msgstr_lines.append(line.strip('"'))
            elif line.startswith("#"):
                other_lines.append((i, line))
                in_msgid = False
                in_msgstr = False
            else:
                other_lines.append((i, line))
                in_msgid = False
                in_msgstr = False

        msgid = "".join(msgid_lines)
        msgstr = "".join(msgstr_lines)

        # Skip header block
        if not msgid and msgstr_start >= 0:
            result_blocks.append(block)
            continue
        
        if not msgid:
            result_blocks.append(block)
            continue

        # Check if we have a translation
        needs_translation = (not msgstr) or is_fuzzy
        
        if needs_translation and msgid in TRANSLATIONS:
            new_msgstr = TRANSLATIONS[msgid]
            
            # Rebuild the block
            new_lines = []
            for idx, line in other_lines:
                if line != "#, fuzzy":  # Remove fuzzy flag
                    new_lines.append(line)
            
            # Add msgid
            new_lines.append(f'msgid "{msgid}"')
            # Add msgstr
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

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(result_blocks))

    return stats

if __name__ == "__main__":
    po_file = "locale/it/LC_MESSAGES/django.po"
    stats = translate_po(po_file, po_file)
    print(f"=== Translation Results ===")
    print(f"Already translated: {stats['already']}")
    print(f"Newly translated:   {stats['translated']}")
    print(f"Fuzzy fixed:        {stats['fuzzy_fixed']}")
    print(f"Still untranslated: {stats['skipped']}")
    print(f"Total processed:    {sum(stats.values())}")
