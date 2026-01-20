📖 This document is available in: [🇮🇹 IT](README-it.md) | [🇬🇧 EN](README.md) | [🇩🇪 DE](README-de.md) | [🇫🇷 FR](README-fr.md) | [🇪🇸 ES](README-es.md)

---

# Motorcycle Club Website - Documentation

> **🏍️ A complete Wagtail 7.x CMS for motorcycle clubs**

## 📚 For Developers

This repository contains the complete documentation and specifications for building a motorcycle club website using **Wagtail 7.x** and **Django**.

### Quick Start

1. **Start here:** [00-INDEX.md](00-INDEX.md) — Complete index of all documentation files
2. **Project structure:** [01-PROJECT-STRUCTURE.md](01-PROJECT-STRUCTURE.md)
3. **Dependencies:** [02-DEPENDENCIES.md](02-DEPENDENCIES.md)

### 🎨 Live Theme Previews

You can preview all 6 themes directly in your browser using GitHub Pages:

| Theme | Style | Live Preview |
|-------|-------|--------------|
| **Velocity** | Modern/Tailwind | [🔗 View](https://bertalan.github.io/motoclubsite_prj/theme_examples/velocity/) |
| **Heritage** | Classic/Bootstrap | [🔗 View](https://bertalan.github.io/motoclubsite_prj/theme_examples/heritage/) |
| **Terra** | Eco-friendly | [🔗 View](https://bertalan.github.io/motoclubsite_prj/theme_examples/terra/) |
| **Zen** | Minimal/Comic | [🔗 View](https://bertalan.github.io/motoclubsite_prj/theme_examples/zen/) |
| **Clubs** | Premium Italian | [🔗 View](https://bertalan.github.io/motoclubsite_prj/theme_examples/clubs/) |
| **Tricolore** | Italian Pride 🇮🇹 | [🔗 View](https://bertalan.github.io/motoclubsite_prj/theme_examples/tricolore/) |

> **Note:** To enable GitHub Pages, go to repository Settings → Pages → Source: "Deploy from a branch" → Branch: `main` / `docs/rebuild`

### Alternative: View HTML files directly

If GitHub Pages is not enabled, you can still view the HTML source:

1. Navigate to [`theme_examples/`](theme_examples/) folder
2. Click on any theme folder (e.g., `velocity/`)
3. Click on `index.html`
4. Click the **Raw** button to see the source, or use [htmlpreview.github.io](https://htmlpreview.github.io/):
   ```
   https://htmlpreview.github.io/?https://github.com/bertalan/motoclubsite_prj/blob/main/docs/rebuild/theme_examples/velocity/index.html
   ```

### Documentation Structure

| Section | Files | Description |
|---------|-------|-------------|
| **Setup** | 01-03 | Project structure, dependencies, settings |
| **Page Models** | 10-14 | Wagtail pages: Home, Content, News, Events, Gallery |
| **Blocks** | 20-24 | StreamField blocks: Hero, Content, Media, Layout |
| **Themes** | 30-39 | Template system and 6 themes |
| **SEO & i18n** | 40-42 | JSON-LD, multilingual, snippets |
| **Deploy** | 50-70 | Docker, production, checklist, migration |
| **Member Features** | 80-92 | Membership, events, gallery, PWA, notifications, federation |

See [00-INDEX.md](00-INDEX.md) for the complete file list with descriptions.

---

# User Guide - Motorcycle Club

## What is this site?

The Motorcycle Club website is the digital home of our club. Here you will find everything you need to make the most of the club experience.

### What you can do

| # | Feature | Description |
| --- | --- | --- |
| 1 | [📰 News](#1--reading-the-news) | Read articles and club announcements |
| 2 | [📅 Events](#2--viewing-and-booking-events) | Discover and sign up for rallies, trips, and meet-ups |
| 3 | [📸 Gallery](#3--the-photo-gallery) | Browse and upload photos from our rides |
| 4 | [👤 Profile](#4--your-member-profile) | Manage your personal details |
| 5 | [🪪 Card](#5--the-digital-membership-card) | Your membership card, always in your pocket |
| 6 | [❤️ Favourites](#6-️-your-favourite-events) | Save the events that interest you |
| 7 | [🌍 Languages](#7--changing-language) | Choose from 5 available languages |
| 8 | [📧 Contact](#8--contacting-us) | Write to the club |
| 9 | [📰 Press](#9--press-office) | Materials for journalists and partners |
| 10 | [🤝 Partners](#10--partners-and-discounts) | Exclusive discounts from our partners |
| 11 | [🛠️ Support](#11-️-mutual-aid-network) | Assistance network among members on the road |
| 12 | [📬 Newsletter](#12--newsletter-and-notifications) | Receive updates via email or push notification |
| 13 | [🌐 Partner Events](#13--partner-events) | Events from partner clubs in the network |

---

## The 5 Fundamental Questions

### 🧑 WHO can use the site?

| Type of visitor | What they can do |
| --- | --- |
| **Anyone** | Read news, view events, browse the gallery, sign up for events |
| **Registered Member** | All of the above + event discounts, upload photos, manage profile |
| **Active Member (Cardholder)** | All of the above + vote, higher discounts, favourite events |

### 📌 WHAT can I do on the site?

| Feature | Simple description |
| --- | --- |
| Read the news | Articles and club communications |
| View events | Rallies, trips, and meetings in the programme |
| Sign up for an event | Book your spot with just a few clicks |
| Upload photos | Share photos from rides and outings |
| Manage my profile | Edit my personal details |
| View my card | Digital membership card with QR code |

### ⏰ WHEN can I use these functions?

| Function | Availability |
| --- | --- |
| Site navigation | Always, 24/7 |
| Event registration | Until the indicated deadline |
| Photo upload | Only members with active permission |
| Digital card | Only members with a valid membership |

### 📍 WHERE do I find the various sections?

| Section | How to get there |
| --- | --- |
| Home | Click on the logo or "Home" in the menu |
| About Us | Menu → About Us |
| Events | Menu → Events |
| Gallery | Menu → Gallery |
| News | Menu → News |
| My Profile | User icon at the top right |
| My Card | Profile → My Membership Card |

### ❓ WHY should I register?

| Benefit | Description |
| --- | --- |
| Event discounts | Reduced prices reserved for members |
| Upload photos | Share your snaps with the club |
| Favourite events | Save the events that interest you |
| Digital card | Always in your pocket on your phone |
| Newsletter | Receive updates via email |

---

## Features in Detail

### 1. 📰 Reading the News

**What it is:** Articles and official club communications.

**How it works:**

1. Go to the "News" section from the menu.
2. Browse articles in chronological order.
3. Click on a title to read the full article.

**Tip:** You can filter by category (e.g., "Announcements", "Reports", "Technical").

---

### 2. 📅 Viewing and Booking Events

**What it is:** The calendar of all club rallies, trips, and meetings.

**Who can sign up:** Everyone! Event registration is open to anyone, member or not.

**How it works:**

1. Go to the "Events" section from the menu.
2. View the list of scheduled events.
3. Click on an event for details.
4. Click "Register" (or "Sign Up") to book your spot.
5. Fill in the required details and confirm.

**Information you will find:**

* Date and time
* Location with map
* The day's programme
* Cost (if applicable)
* Available spaces

**💡 Member Discount:** Members are entitled to reduced prices! During registration you will see:

* The standard price for everyone
* The discounted price reserved for members
* A link to become a member and get the discount

**Early Bird Discount:** By signing up in advance you can get an additional discount!

* 60+ days prior: 20% discount
* 30-59 days prior: 10% discount
* Less than 30 days: Full price

**Bringing a pillion/passenger:** During registration, you can add a companion. If they are a member, search for them by name. Otherwise, enter their details.

---

### 3. 📸 The Photo Gallery

**What it is:** All the photos from our rides and activities.

**How it works:**

1. Go to the "Gallery" section from the menu.
2. Browse albums by event or date.
3. Click on a photo to view it in full size.
4. Use the arrows to scroll.

**Uploading your photos (members only):**

1. Go to your profile → "Upload photos".
2. Select up to 20 photos at once.
3. Write a title (e.g., "Spring Rally 2026").
4. Add a description.
5. Choose tags (e.g., "rally", "trip", "vintage-bikes").
6. Click "Upload".

**Note:** Photos are vetted before publication.

---

### 4. 👤 Your Member Profile

**What it is:** Your personal area where you manage your details.

**How to access:**

1. Click on the user icon at the top right.
2. Log in with your email and password.
3. Go to "My Profile".

**What you can edit:**

* Profile picture
* Phone number
* Address
* Newsletter preferences
* Bio (if you want a public profile)

**Public Profile:** If you activate this option, others will be able to see your name, photo, bio, and the content you have posted.

---

### 5. 🪪 The Digital Membership Card

**What it is:** Your motorcycle club card, always available on your phone.

**How to view it:**

1. Go to your profile.
2. Click on "My Membership Card".

**What it contains:**

* Your name and photo
* Membership number
* Expiry date
* QR code (for quick verification)
* Barcode

**Printing it:** Click "Print Card" to get a credit card-sized PDF.

---

### 6. ❤️ Your Favourite Events

**What it is:** A personal list of events you are interested in.

**How it works:**

1. When you see an event you like, click the little heart ❤️.
2. The event is saved to your favourites.
3. Go to "My Events" to view the list.

**Extra functions:**

* **Map:** See all your favourite events on a map.
* **Export:** Download events to your calendar (Google, Apple, Outlook).
* **Share:** Send the list to your friends.

---

### 7. 🌍 Changing Language

**What it is:** The site is available in 5 languages.

**Available languages:**

* 🇬🇧 English (default)
* 🇮🇹 Italiano
* 🇩🇪 Deutsch
* 🇫🇷 Français
* 🇪🇸 Español

**How to change:**

1. Look for the language selector (usually at the top right).
2. Click on the flag or code for the desired language.
3. The site updates automatically.

---

### 8. 📧 Contacting Us

**What it is:** How to get in touch with the club.

**How to do it:**

1. Go to the "Contact" section from the menu.
2. Fill out the form with:
   * Your name
   * Your email
   * Your message
3. Click "Send".

**Other options:**

* Direct email: info@motoclub.it
* Phone: see contact page
* Social: links to Facebook, Instagram

---

### 9. 📰 Press Office

**What it is:** Official materials for journalists and partners.

**What you find:**

* Club logo in various formats
* Official photos of the HQ and events
* Press releases
* Press contacts

**How to access:**

1. Go to the "Press" section (usually in the footer).
2. Download the materials you need.

---

### 10. 🤝 Partners and Discounts

**What it is:** Club partners offer exclusive discounts to members.

**How it works:**

1. Go to the "Partners" section from the menu or footer.
2. Browse partners by category (garages, spares, clothing/gear...).
3. Click on a partner to see the reserved discount.

**Getting the discount:**

1. Visit the partner with your digital card.
2. The partner verifies your card by entering the number.
3. You receive the stated discount!

**Note:** The partner only sees your display name and the validity of the card — your personal data remains private.

---

### 11. 🛠️ Mutual Aid Network

**What it is:** A network of members available to help in case of problems whilst travelling.

**How to see who can help you:**

1. Go to the "Mutual Aid" section (in the menu or footer).
2. Use the map to see who is available in your area.
3. Filter by skill: mechanics, transport, logistics, emergency.
4. Click on a helper to see how to contact them.

**Offering your help:**

1. Go to your profile → "Mutual Aid".
2. Activate availability.
3. Choose your skills (mechanics, van transport, etc.).
4. Define your coverage area (km from home).
5. **Important:** Choose what to show other members:
   * Display name (always visible)
   * Phone / WhatsApp / Email (you decide)
   * Exact location or just the city
   * Availability hours

**Total Privacy:** Every field is controlled by you. You can even use just the contact form, so no one sees your private details.

**Visiting from a partner club?** You can view our helpers and use the contact form. To see direct contact details (phone, WhatsApp), you have 3 free unlocks. After that, request full access and our admin will review it.

---

### 12. 📬 Newsletter and Notifications

**What it is:** Receive club updates via email or push notifications on your phone.

**What you can receive:**

* Newly published news
* New scheduled events
* Reminders before events you are registered for
* **Weekend Round-up:** every Thursday, a list of the events taking place that weekend which you have saved ❤️
* Membership expiry notice

**How to manage preferences:**

1. Go to your profile → "Notifications".
2. Toggle the types of notifications you want on/off.
3. Choose frequency: instant, daily summary, weekly summary.
4. **Choose when:** you can decide the day and time to receive notifications.
5. Enable push notifications if you have installed the app.

**Weekend Reminder (default: Thursday at 9 am):**

* If you have saved events happening over the weekend, you will receive a summary.
* You can change the day and time as you wish.
* No saved events = no useless emails.

**Unsubscribing from an email:**

1. At the bottom of every email there is an "Unsubscribe" link.
2. Click it and you will reach a confirmation page.
3. You can leave a message (optional).
4. Click "Confirm" — no login required!

**Why am I receiving this email?**
Every email clearly explains why you are receiving it (e.g., "You are receiving this email because you are subscribed to News").

---

### 13. 🌐 Partner Events

**What it is:** Events organized by partner clubs in our network. Our club exchanges events with trusted partners so you can discover more activities.

**How it works:**

1. Go to "Events" → "Partner Events" (or integrated in main events page).
2. Browse events from partner clubs.
3. Click on an event for details.
4. Show your interest: "Interested", "Maybe", or "Going!".
5. Use comments to organize with other members ("Who's driving from Milan?").

**What you can do:**

| Action | Description |
|--------|-------------|
| Show interest | Express if you're going, maybe, or interested |
| Organize | Comment to coordinate with other members |
| View on map | See event location |
| Visit original | Link to partner club's event page |

**Privacy:**

* Your name is **never shared** with partner clubs.
* Only anonymous counts are shared (e.g., "3 members from Our Club interested").
* Comments are visible only to our members.

**Notifications:**

You can receive alerts about:
* New partner events added
* Comments on events you're interested in
* Event updates or cancellations

Manage these in Profile → Notifications → "Partner Events".

---

## Frequently Asked Questions

### How do I register?

1. Click on "Register" or "Become a Member".
2. Fill out the form with your details.
3. You will receive a confirmation email.
4. The club will contact you regarding the membership card.

### I forgot my password

1. Click on "Login".
2. Click on "Forgot password?".
3. Enter your email.
4. You will receive a link to reset it.

### My membership card is about to expire

You will receive a reminder email 30 and 7 days before expiry. Contact the club for renewal.

### I can't sign up for an event

Check that:

* Your membership card is still valid.
* The event is not sold out.
* The registration deadline has not passed.

### My photos aren't appearing in the gallery

Photos are vetted before publication. Please wait a few days. If the problem persists, contact the club.

### How do I get the discount from partners?

Show your digital card to the partner. They will enter the card number to verify you are an active member. They do not need to know your personal details.

### How can I help other members in difficulty?

1. Go to Profile → Mutual Aid.
2. Activate availability.
3. Choose the skills you offer.
4. Decide which contact details to show (only what you want).

### I don't want my details visible in Mutual Aid

No problem! You can:

* Activate only the contact form (no details visible).
* Show only your display name and city.
* Choose field by field what to make visible.

### How do I unsubscribe from the newsletter?

At the bottom of every email, there is an "Unsubscribe" link. Click it, confirm on the page that opens, and you're done! No need to log in.

### I receive too many emails

Go to notification preferences and choose "Weekly summary" instead of "Instant". You will receive just one email a week with all the updates.

### How do I enable push notifications?

1. Install the app on your phone (Add to Home Screen).
2. Go to Profile → Notifications.
3. Enable "Push notifications".
4. The browser will ask for permission — accept it.

---

## Need help?

If something isn't working or you have doubts:

1. **Email:** info@motoclub.it
2. **Phone:** see contact page
3. **In person:** come to the HQ during opening hours

---

*Last updated: January 2026*

---

📖 This document is available in: [🇮🇹 IT](README-it.md) | [🇬🇧 EN](README.md) | [🇩🇪 DE](README-de.md) | [🇫🇷 FR](README-fr.md) | [🇪🇸 ES](README-es.md)
