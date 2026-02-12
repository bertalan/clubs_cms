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
            required=True,
        )
        last_name = forms.CharField(
            max_length=150,
            label=_("Last name"),
            required=True,
        )
        display_name = forms.CharField(
            max_length=100,
            label=_("Display name (nickname)"),
            required=False,
        )
        newsletter = forms.BooleanField(
            label=_("Subscribe to newsletter"),
            required=False,
        )

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
            required=True,
        )
        last_name = forms.CharField(
            max_length=150,
            label=_("Last name"),
            required=True,
        )
        display_name = forms.CharField(
            max_length=100,
            label=_("Display name (nickname)"),
            required=False,
        )
        email = forms.EmailField(
            label=_("Email"),
            required=True,
        )
        newsletter = forms.BooleanField(
            label=_("Subscribe to newsletter"),
            required=False,
        )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["show_in_directory"].label = _("Show me in the member directory")
        self.fields["public_profile"].label = _("Make my profile public")
        self.fields["show_real_name_to_members"].label = _(
            "Show my real name to other members"
        )
        self.fields["newsletter"].label = _("Subscribe to newsletter")


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
            "aid_coordinates": forms.TextInput(
                attrs={"placeholder": "45.4642,9.1900"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["aid_available"].label = _("I am available for mutual aid")
        self.fields["aid_radius_km"].label = _("Radius (km)")
        self.fields["aid_location_city"].label = _("City")
        self.fields["aid_coordinates"].label = _("Coordinates (lat,lon)")
        self.fields["aid_notes"].label = _("Notes")
