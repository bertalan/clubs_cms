"""
Forms for the core app: contribution submission.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.core.forms_helpers import _apply_wcag_attrs
from apps.core.models import Contribution


class ContributionForm(forms.ModelForm):
    """Form for submitting a member contribution (story/proposal/announcement)."""

    class Meta:
        model = Contribution
        fields = ["contribution_type", "title", "body"]
        widgets = {
            "contribution_type": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"class": "form-input"}),
            "body": forms.Textarea(attrs={"class": "form-input", "rows": 8}),
        }
        labels = {
            "contribution_type": _("Type"),
            "title": _("Title"),
            "body": _("Content"),
        }
        help_texts = {
            "contribution_type": _("Select the type of contribution."),
            "title": _("A short, descriptive title."),
            "body": _("The full content of your contribution."),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        _apply_wcag_attrs(self)

    def clean(self):
        cleaned = super().clean()
        if self.user:
            pending_count = Contribution.objects.filter(
                user=self.user, status="pending"
            ).count()
            if pending_count >= 5:
                raise forms.ValidationError(
                    _("You have too many pending contributions. "
                      "Please wait for moderation before submitting more.")
                )
        return cleaned
