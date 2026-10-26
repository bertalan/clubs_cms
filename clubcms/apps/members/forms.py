"""
Django ModelForms for the members app.

Provides forms for:
1. RegistrationForm — new member sign-up (allauth or fallback)
2. ProfileForm — edit personal data and address fields
3. PrivacySettingsForm — privacy and directory preferences
4. NotificationPreferencesForm — email/push notification toggles
5. AidAvailabilityForm — mutual-aid availability settings
"""

from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from apps.core.forms_helpers import _apply_wcag_attrs


# ---------------------------------------------------------------------------
# 1. Registration Form
# ---------------------------------------------------------------------------

try:
    from allauth.account.forms import SignupForm as _BaseSignupForm

    class RegistrationForm(_BaseSignupForm):
        """
        Registration form extending allauth's SignupForm with
        additional fields for the motorcycle club.
        """

        first_name = forms.CharField(
            max_length=150,
            label=_("First name"),
            help_text=_("Your given name as it appears on official documents."),
            required=True,
        )
        last_name = forms.CharField(
            max_length=150,
            label=_("Last name"),
            help_text=_("Your family name as it appears on official documents."),
            required=True,
        )
        display_name = forms.CharField(
            max_length=100,
            label=_("Display name (nickname)"),
            help_text=_("The name shown publicly. Leave blank to use your real name."),
            required=False,
        )
        newsletter = forms.BooleanField(
            label=_("Subscribe to newsletter"),
            help_text=_("Receive club news and updates by email."),
            required=False,
        )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            _apply_wcag_attrs(self)

        def save(self, request):
            user = super().save(request)
            user.first_name = self.cleaned_data["first_name"]
            user.last_name = self.cleaned_data["last_name"]
            user.display_name = self.cleaned_data.get("display_name", "")
            user.newsletter = self.cleaned_data.get("newsletter", False)
            user.save()
            return user

except ImportError:
    from django.contrib.auth.forms import UserCreationForm

    class RegistrationForm(UserCreationForm):
        """
        Fallback registration form using Django's UserCreationForm
        when allauth is not installed.
        """

        first_name = forms.CharField(
            max_length=150,
            label=_("First name"),
            help_text=_("Your given name as it appears on official documents."),
            required=True,
        )
        last_name = forms.CharField(
            max_length=150,
            label=_("Last name"),
            help_text=_("Your family name as it appears on official documents."),
            required=True,
        )
        display_name = forms.CharField(
            max_length=100,
            label=_("Display name (nickname)"),
            help_text=_("The name shown publicly. Leave blank to use your real name."),
            required=False,
        )
        email = forms.EmailField(
            label=_("Email"),
            help_text=_("We will send your login credentials to this address."),
            required=True,
        )
        newsletter = forms.BooleanField(
            label=_("Subscribe to newsletter"),
            help_text=_("Receive club news and updates by email."),
            required=False,
        )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            _apply_wcag_attrs(self)

        class Meta:
            model = get_user_model()
            fields = (
                "username",
                "email",
                "first_name",
                "last_name",
                "display_name",
                "password1",
                "password2",
            )

        def save(self, commit=True):
            user = super().save(commit=False)
            user.email = self.cleaned_data["email"]
            user.first_name = self.cleaned_data["first_name"]
            user.last_name = self.cleaned_data["last_name"]
            user.display_name = self.cleaned_data.get("display_name", "")
            user.newsletter = self.cleaned_data.get("newsletter", False)
            if commit:
                user.save()
            return user


# ---------------------------------------------------------------------------
# 2. Profile Form
# ---------------------------------------------------------------------------

class ProfileForm(forms.ModelForm):
    """Form for editing personal data and address fields."""

    class Meta:
        model = get_user_model()
        fields = [
            "first_name",
            "last_name",
            "display_name",
            "phone",
            "mobile",
            "birth_date",
            "birth_place",
            "bio",
            # Address fields
            "address",
            "city",
            "province",
            "postal_code",
            "country",
        ]
        widgets = {
            "birth_date": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "bio": forms.Textarea(attrs={"rows": 4}),
            "province": forms.TextInput(attrs={"maxlength": 2}),
            "postal_code": forms.TextInput(attrs={"maxlength": 5}),
            "country": forms.TextInput(attrs={"maxlength": 2}),
        }
        # Member-facing help, kept here so the model help can address staff.
        help_texts = {
            "display_name": _(
                "Choose a nickname that will be shown publicly instead of your real "
                "name."
            ),
            "phone": _("Landline number with country prefix. Example: +39 02 1234567"),
            "mobile": _("Mobile number with country prefix. Example: +39 333 1234567"),
            "birth_date": _(
                "Your date of birth. Used for birthday greetings and age-restricted "
                "events."
            ),
            "birth_place": _("City or town where you were born."),
            "bio": _(
                "A short description about yourself. Visible on your profile page."
            ),
            "address": _("Street address. Example: Via Roma 42"),
            "city": _("City or town of residence."),
            "province": _("Two-letter province code. Example: MI"),
            "postal_code": _("5-digit postal code. Example: 20100"),
            "country": _("Two-letter country code (ISO 3166-1). Example: IT"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_wcag_attrs(self)


# ---------------------------------------------------------------------------
# 3. Privacy Settings Form
# ---------------------------------------------------------------------------

class PrivacySettingsForm(forms.ModelForm):
    """Form for privacy and directory visibility preferences."""

    class Meta:
        model = get_user_model()
        fields = [
            "show_in_directory",
            "public_profile",
            "show_real_name_to_members",
            "newsletter",
        ]
        # Member-facing help, kept here so the model help can address staff.
        help_texts = {
            "show_in_directory": _(
                "When enabled, your display name appears in the member directory "
                "visible to other members."
            ),
            "public_profile": _(
                "When enabled, your profile page is visible to anyone, including "
                "non-members."
            ),
            "show_real_name_to_members": _(
                "When enabled, active members can see your real first and last name."
            ),
            "newsletter": _(
                "Receive our periodic newsletter with club news and upcoming events."
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["show_in_directory"].label = _("Show me in the member directory")
        self.fields["public_profile"].label = _("Make my profile public")
        self.fields["show_real_name_to_members"].label = _(
            "Show my real name to other members"
        )
        self.fields["newsletter"].label = _("Subscribe to newsletter")
        _apply_wcag_attrs(self)


# ---------------------------------------------------------------------------
# 4. Notification Preferences Form
# ---------------------------------------------------------------------------

class NotificationPreferencesForm(forms.ModelForm):
    """Form for email/push notification toggles and digest frequency."""

    class Meta:
        model = get_user_model()
        fields = [
            "email_notifications",
            "push_notifications",
            "news_updates",
            "event_updates",
            "event_reminders",
            "membership_alerts",
            "partner_updates",
            "aid_requests",
            "partner_events",
            "partner_event_comments",
            "digest_frequency",
        ]
        # Member-facing help, kept here so the model help can address staff.
        help_texts = {
            "email_notifications": _("Receive notifications via email."),
            "push_notifications": _(
                "Receive push notifications in your browser (requires PWA support)."
            ),
            "news_updates": _(
                "Get notified when new articles or announcements are published."
            ),
            "event_updates": _(
                "Get notified about new events and changes to events you registered "
                "for."
            ),
            "event_reminders": _(
                "Receive a reminder before events you are registered for."
            ),
            "membership_alerts": _(
                "Alerts about membership expiry, renewal, and card updates."
            ),
            "partner_updates": _("News and promotions from partner clubs."),
            "aid_requests": _("Notifications when someone nearby requests mutual aid."),
            "partner_events": _("Events published by federated partner clubs."),
            "partner_event_comments": _(
                "Comments on partner events you showed interest in."
            ),
            "digest_frequency": _(
                "How often to receive a digest email summarising your notifications."
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email_notifications"].label = _("Email notifications")
        self.fields["push_notifications"].label = _("Push notifications")
        self.fields["news_updates"].label = _("News updates")
        self.fields["event_updates"].label = _("Event updates")
        self.fields["event_reminders"].label = _("Event reminders")
        self.fields["membership_alerts"].label = _("Membership alerts")
        self.fields["partner_updates"].label = _("Partner updates")
        self.fields["aid_requests"].label = _("Mutual aid requests")
        self.fields["partner_events"].label = _("Partner events")
        self.fields["partner_event_comments"].label = _("Partner event comments")
        self.fields["digest_frequency"].label = _("Digest frequency")
        _apply_wcag_attrs(self)


# ---------------------------------------------------------------------------
# 5. Aid Availability Form
# ---------------------------------------------------------------------------

class AidAvailabilityForm(forms.ModelForm):
    """Form for mutual-aid availability settings."""

    class Meta:
        model = get_user_model()
        fields = [
            "aid_available",
            "aid_radius_km",
            "aid_location_city",
            "aid_coordinates",
            "aid_notes",
        ]
        widgets = {
            "aid_notes": forms.Textarea(attrs={"rows": 3}),
            "aid_coordinates": forms.HiddenInput(),
        }
        # Member-facing help, kept here so the model help can address staff.
        help_texts = {
            "aid_available": _(
                "Enable this to appear in the mutual aid helper directory."
            ),
            "aid_radius_km": _(
                "Maximum distance in km you are willing to travel to help. Example: "
                "25"
            ),
            "aid_location_city": _(
                "The city where you are usually based for mutual aid."
            ),
            "aid_coordinates": _(
                "Latitude and longitude, comma-separated. Example: 45.4642,9.1900"
            ),
            "aid_notes": _(
                "Additional information: tools, skills, vehicle type, availability "
                "hours."
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["aid_available"].label = _("I am available for mutual aid")
        self.fields["aid_radius_km"].label = _("Radius (km)")
        self.fields["aid_location_city"].label = _("City")
        self.fields["aid_coordinates"].label = _("Coordinates (lat,lon)")
        self.fields["aid_notes"].label = _("Notes")
        _apply_wcag_attrs(self)
