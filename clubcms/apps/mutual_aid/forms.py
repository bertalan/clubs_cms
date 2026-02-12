"""
Mutual Aid forms.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

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
                "class": "form-control",
                "placeholder": _("Your name"),
            }),
            "requester_phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": _("Phone number"),
            }),
            "requester_email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": _("Email address"),
            }),
            "issue_type": forms.Select(attrs={
                "class": "form-control",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": _("Describe what you need help with..."),
            }),
            "location": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": _("Your current location"),
            }),
            "urgency": forms.Select(attrs={
                "class": "form-control",
            }),
        }

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


class FederatedAccessRequestForm(forms.Form):
    """
    Form for a federated user to request access to the helpers directory.
    """

    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "placeholder": _("Why do you need access? (optional)"),
        }),
        max_length=1000,
        label=_("Message"),
    )
