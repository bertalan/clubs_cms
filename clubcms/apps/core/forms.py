"""
Forms for the core app: contribution submission.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.core.forms_helpers import _apply_wcag_attrs
from apps.core.models import ContributionPage


class ContributionForm(forms.Form):
    """Form for submitting a member contribution (story/proposal/announcement)."""

    contribution_type = forms.ChoiceField(
        choices=ContributionPage.TYPE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Type"),
        help_text=_("Select the type of contribution."),
    )
    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-input"}),
        label=_("Title"),
        help_text=_("A short, descriptive title."),
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-input", "rows": 8}),
        label=_("Content"),
        help_text=_("The full content of your contribution."),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        _apply_wcag_attrs(self)

    def clean(self):
        cleaned = super().clean()
        if self.user:
            pending_count = (
                ContributionPage.objects
                .filter(author=self.user, moderation_status="pending")
                .count()
            )
            if pending_count >= 5:
                raise forms.ValidationError(
                    _("You have too many pending contributions. "
                      "Please wait for moderation before submitting more.")
                )
        return cleaned
