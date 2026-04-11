"""
Forms for the core app: contribution submission.

Provides forms for submitting different page types from the frontend:
- ContributionForm: generic story / announcement / proposal
- NewsSubmissionForm: creates a real NewsPage
- EventSubmissionForm: creates a real EventDetailPage
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.core.forms_helpers import _apply_wcag_attrs
from apps.core.models import ContributionPage


# ---------------------------------------------------------------------------
# Rate-limit mixin
# ---------------------------------------------------------------------------

class _PendingLimitMixin:
    """Reject submission if user has ≥ 5 pending (unpublished) pages."""

    MAX_PENDING = 5

    def clean(self):
        cleaned = super().clean()
        if self.user:
            from wagtail.models import Page
            pending = (
                Page.objects.filter(owner=self.user, live=False)
                .exclude(depth__lte=1)
                .count()
            )
            if pending >= self.MAX_PENDING:
                raise forms.ValidationError(
                    _("You have too many pending submissions. "
                      "Please wait for moderation before submitting more.")
                )
        return cleaned


# ---------------------------------------------------------------------------
# ContributionForm  (generic story / proposal / announcement)
# ---------------------------------------------------------------------------

class ContributionForm(_PendingLimitMixin, forms.Form):
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


# ---------------------------------------------------------------------------
# NewsSubmissionForm  →  NewsPage
# ---------------------------------------------------------------------------

class NewsSubmissionForm(_PendingLimitMixin, forms.Form):
    """Frontend form that creates a real NewsPage under NewsIndexPage."""

    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-input"}),
        label=_("Title"),
        help_text=_("Headline for your article."),
    )
    intro = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        label=_("Introduction / excerpt"),
        help_text=_("A short summary shown in news listings."),
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-input", "rows": 10}),
        label=_("Article body"),
        help_text=_("The full content of your article. Separate paragraphs with a blank line."),
    )
    category = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Category"),
        help_text=_("Select a category for your article."),
    )
    cover_image = forms.ImageField(
        required=False,
        label=_("Cover image"),
        help_text=_("An image to display with your article (optional)."),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        from apps.website.models.snippets import NewsCategory
        self.fields["category"].queryset = NewsCategory.objects.all()
        _apply_wcag_attrs(self)


# ---------------------------------------------------------------------------
# EventSubmissionForm  →  EventDetailPage
# ---------------------------------------------------------------------------

class EventSubmissionForm(_PendingLimitMixin, forms.Form):
    """Frontend form that creates a real EventDetailPage under EventsPage."""

    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-input"}),
        label=_("Event name"),
        help_text=_("Name of the event."),
    )
    intro = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        label=_("Short description"),
        help_text=_("A brief description shown in event listings."),
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-input", "rows": 8}),
        label=_("Full description"),
        help_text=_("Detailed event description. Separate paragraphs with a blank line."),
    )
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"class": "form-input", "type": "datetime-local"},
        ),
        label=_("Start date & time"),
    )
    end_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={"class": "form-input", "type": "datetime-local"},
        ),
        label=_("End date & time"),
        help_text=_("Leave blank for single-day events."),
    )
    location_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
        label=_("Venue name"),
    )
    location_address = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
        label=_("Address"),
    )
    category = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Category"),
    )
    cover_image = forms.ImageField(
        required=False,
        label=_("Cover image"),
        help_text=_("An image for the event (optional)."),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        from apps.website.models.snippets import EventCategory
        self.fields["category"].queryset = EventCategory.objects.all()
        _apply_wcag_attrs(self)
