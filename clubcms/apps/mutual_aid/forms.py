"""
Mutual Aid forms.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.core.forms_helpers import _apply_wcag_attrs
from apps.mutual_aid.models import AidPrivacySettings, AidRequest


class AidRequestForm(forms.ModelForm):
    """
    Form for creating a mutual aid request.

    Excludes fields managed by the system (helper, status,
    federation fields).
    """

    class Meta:
        model = AidRequest
        fields = [
            "requester_name",
            "requester_phone",
            "requester_email",
            "issue_type",
            "description",
            "location",
            "urgency",
        ]
        widgets = {
            "requester_name": forms.TextInput(attrs={
                "placeholder": _("Your name"),
            }),
            "requester_phone": forms.TextInput(attrs={
                "placeholder": _("Phone number"),
            }),
            "requester_email": forms.EmailInput(attrs={
                "placeholder": _("Email address"),
            }),
            "description": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": _("Describe what you need help with..."),
            }),
            "location": forms.TextInput(attrs={
                "placeholder": _("Your current location"),
            }),
        }
        help_texts = {
            "requester_name": _("Name the helper will see in the request."),
            "requester_phone": _("A phone number where you can be reached."),
            "requester_email": _("Email for follow-up communication."),
            "issue_type": _("Select the category that best matches your need."),
            "description": _("Describe your situation. Max 5 000 characters."),
            "location": _("Approximate location where you need help."),
            "urgency": _("How quickly do you need assistance?"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_wcag_attrs(self)

    def clean_description(self):
        description = self.cleaned_data.get("description", "")
        if len(description) > 5000:
            raise forms.ValidationError(
                _("Description must be 5000 characters or fewer.")
            )
        return description


class AidPrivacyForm(forms.ModelForm):
    """
    Form for editing mutual aid privacy settings.
    """

    class Meta:
        model = AidPrivacySettings
        fields = [
            "show_phone_on_aid",
            "show_mobile_on_aid",
            "show_whatsapp_on_aid",
            "show_email_on_aid",
            "show_exact_location",
            "show_photo_on_aid",
            "show_bio_on_aid",
            "show_hours_on_aid",
        ]
        help_texts = {
            "show_phone_on_aid": _("Show your phone number to people requesting help."),
            "show_mobile_on_aid": _("Show your mobile number in the helper directory."),
            "show_whatsapp_on_aid": _("Allow helpers to contact you via WhatsApp."),
            "show_email_on_aid": _("Show your email address to requesters."),
            "show_exact_location": _("Show your precise coordinates instead of just the city."),
            "show_photo_on_aid": _("Display your profile photo in the helper listing."),
            "show_bio_on_aid": _("Show your bio/notes to people browsing helpers."),
            "show_hours_on_aid": _("Display your availability hours."),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_wcag_attrs(self)


class FederatedAccessRequestForm(forms.Form):
    """
    Form for a federated user to request access to the helpers directory.
    """

    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 3,
            "placeholder": _("Why do you need access? (optional)"),
        }),
        max_length=1000,
        label=_("Message"),
        help_text=_("Optional message to the administrators explaining your request."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_wcag_attrs(self)


class GeoSearchForm(forms.Form):
    """Geolocation search form for the mutual aid helpers page."""

    location = forms.CharField(
        required=False,
        label=_("Location"),
        widget=forms.TextInput(attrs={
            "placeholder": _("City or address…"),
            "autocomplete": "off",
        }),
    )
    lat = forms.FloatField(required=False, widget=forms.HiddenInput())
    lng = forms.FloatField(required=False, widget=forms.HiddenInput())
    radius = forms.IntegerField(
        required=False,
        label=_("Radius (km)"),
        min_value=5,
        max_value=500,
    )
