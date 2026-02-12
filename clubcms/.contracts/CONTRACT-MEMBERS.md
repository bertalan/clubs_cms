# CONTRACT-MEMBERS

Interface contract for the AUTH-MEMBERS system (`apps.members`).

---

## ClubUser Model (`apps.members.models.ClubUser`)

Extends `django.contrib.auth.models.AbstractUser`.

### Fields

| Field | Type | Notes |
|---|---|---|
| **Display name system** | | |
| `display_name` | CharField(100) | Public nickname |
| `show_real_name_to_members` | BooleanField | Allow active members to see real name |
| **Personal data** | | |
| `phone` | CharField(30) | |
| `mobile` | CharField(30) | |
| `birth_date` | DateField | nullable |
| `birth_place` | CharField(100) | |
| `photo` | FK(wagtailimages.Image) | nullable |
| **Identity document** | | |
| `fiscal_code` | CharField(16) | |
| `document_type` | CharField(20) | choices: id_card, license, passport |
| `document_number` | CharField(50) | |
| `document_expiry` | DateField | nullable |
| **Address** | | |
| `address` | CharField(255) | |
| `city` | CharField(100) | |
| `province` | CharField(2) | |
| `postal_code` | CharField(5) | |
| `country` | CharField(2) | default "IT" |
| **Membership card** | | |
| `card_number` | CharField(50) | unique, nullable, auto-generated YYYY-NNNN |
| `membership_date` | DateField | nullable |
| `membership_expiry` | DateField | nullable |
| **Preferences** | | |
| `newsletter` | BooleanField | default False |
| `show_in_directory` | BooleanField | default False |
| `public_profile` | BooleanField | default False |
| `bio` | TextField | |
| **Mutual aid** | | |
| `aid_available` | BooleanField | default False |
| `aid_radius_km` | PositiveIntegerField | default 25 |
| `aid_location_city` | CharField(100) | |
| `aid_coordinates` | CharField(50) | lat,lon format |
| `aid_notes` | TextField | |
| **Notification preferences** | | |
| `email_notifications` | BooleanField | default True |
| `push_notifications` | BooleanField | default False |
| `news_updates` | BooleanField | default True |
| `event_updates` | BooleanField | default True |
| `event_reminders` | BooleanField | default True |
| `membership_alerts` | BooleanField | default True |
| `partner_updates` | BooleanField | default False |
| `aid_requests` | BooleanField | default True |
| `partner_events` | BooleanField | default True |
| `partner_event_comments` | BooleanField | default True |
| `digest_frequency` | CharField(10) | choices: immediate, daily, weekly |
| **Products (composable membership)** | | |
| `products` | ParentalManyToManyField(website.Product) | related_name="members" |

### Methods

| Method | Returns | Description |
|---|---|---|
| `__str__()` | str | Returns `get_visible_name()` |
| `get_visible_name(viewer=None)` | str | Context-aware display name |

### Properties

| Property | Returns | Description |
|---|---|---|
| `is_active_member` | bool | True if membership_expiry >= today |
| `is_expired` | bool | Inverse of is_active_member |
| `days_to_expiry` | int or None | Days until membership expires |
| `can_vote` | bool | True if any product grants_vote |
| `can_upload` | bool | True if any product grants_upload |
| `can_register_events` | bool | True if any product grants_events |
| `max_discount_percent` | int | Max discount_percent from products with grants_discount |

---

## Product Permission System

Products (`apps.website.models.Product`) have privilege flags:
- `grants_vote` — enables voting rights
- `grants_upload` — enables gallery uploads
- `grants_events` — enables event registration
- `grants_discount` — enables discount (with `discount_percent`)

A user's permissions are the **union** of all their assigned product privileges.

---

## URL Patterns

### Account URLs (`app_name="account"`, prefix `/account/`)

| URL | Name | View | Method |
|---|---|---|---|
| `/account/profile/` | `account:profile` | ProfileView | GET, POST |
| `/account/card/` | `account:card` | CardView | GET |
| `/account/card/pdf/` | `account:card_pdf` | CardPDFView | GET |
| `/account/card/qr/` | `account:card_qr` | QRCodeView | GET |
| `/account/card/barcode/` | `account:card_barcode` | BarcodeView | GET |
| `/account/privacy/` | `account:privacy` | PrivacySettingsView | GET, POST |
| `/account/notifications/` | `account:notifications` | NotificationPrefsView | GET, POST |
| `/account/aid/` | `account:aid` | AidAvailabilityView | GET, POST |
| `/account/directory/` | `account:directory` | MemberDirectoryView | GET |

### Public Profile URL (root urlconf)

| URL | Name | View |
|---|---|---|
| `/members/<username>/` | `public_profile` | PublicProfileView |

---

## Decorators (`apps.members.decorators`)

### `active_member_required`

```python
from apps.members.decorators import active_member_required

@active_member_required
def my_view(request):
    ...
```

- Unauthenticated: redirect to LOGIN_URL
- Authenticated but not active member: 403 Forbidden

### `member_with_product(product_slug)`

```python
from apps.members.decorators import member_with_product

@member_with_product("premium")
def premium_view(request):
    ...
```

- Unauthenticated: redirect to LOGIN_URL
- Missing product: 403 Forbidden

---

## Forms (`apps.members.forms`)

| Form | Fields | Notes |
|---|---|---|
| `RegistrationForm` | first_name, last_name, display_name, email, newsletter + auth fields | Extends allauth SignupForm or Django UserCreationForm |
| `ProfileForm` | Personal data + address (13 fields) | ModelForm |
| `PrivacySettingsForm` | show_in_directory, public_profile, show_real_name_to_members, newsletter | ModelForm |
| `NotificationPreferencesForm` | All notification booleans + digest_frequency (11 fields) | ModelForm |
| `AidAvailabilityForm` | aid_available, aid_radius_km, aid_location_city, aid_coordinates, aid_notes | ModelForm |

---

## Signals (`apps.members.signals`)

- **post_save on ClubUser**: Auto-generates `card_number` in YYYY-NNNN format when `membership_date` is set and `card_number` is empty. Regenerates QR code and barcode when card_number is present.

---

## Utilities (`apps.members.utils`)

| Function | Description |
|---|---|
| `generate_card_number(user)` | Returns YYYY-NNNN card number |
| `build_vcard(user)` | Returns vCard 3.0 string (non-sensitive data only) |
| `generate_qr_code(user)` | Saves QR to media/members/qr/, returns relative path |
| `generate_barcode(user)` | Saves barcode to media/members/barcode/, returns relative path |

---

## Wagtail Admin

ClubUser is managed via `ClubUserViewSet` (ModelViewSet) registered through `wagtail_hooks.py`. Accessible from the Wagtail sidebar under "Members".

Tabbed interface: Personal, Identity, Address, Membership, Privacy, Notifications, Mutual Aid.

---

## Templates

All in `templates/account/`, extending `base.html`, using `{% load i18n %}`.

| Template | View |
|---|---|
| `profile.html` | ProfileView |
| `card.html` | CardView |
| `privacy.html` | PrivacySettingsView |
| `notifications.html` | NotificationPrefsView |
| `aid.html` | AidAvailabilityView |
| `directory.html` | MemberDirectoryView |
| `public_profile.html` | PublicProfileView |

---

## Settings (`clubcms/settings/base.py`)

- `AUTH_USER_MODEL = "members.ClubUser"`
- `LOGIN_REDIRECT_URL = "/my-profile/"`
- `LOGOUT_REDIRECT_URL = "/"`
- django-allauth integration (conditional on import availability)
