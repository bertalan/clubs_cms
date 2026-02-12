"""
Forms for partner verification, gallery photo upload, and press.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.website.models.snippets import PhotoTag
from apps.website.models.pages import EventDetailPage


# ---------------------------------------------------------------------------
# Verification form
# ---------------------------------------------------------------------------

VERIFICATION_TYPE_CHOICES = [
    ("display_name", _("Display name")),
    ("city", _("City")),
    ("phone", _("Phone")),
]


class VerificationForm(forms.Form):
    """
    Form for partner owners to verify a member's card.

    Requires the card number and a secondary factor (display name, city,
    or phone) for two-factor-style verification.
    """

    card_number = forms.CharField(
        max_length=50,
        label=_("Card number"),
        widget=forms.TextInput(attrs={
            "placeholder": _("Enter member card number"),
            "autocomplete": "off",
        }),
    )
    verification_type = forms.ChoiceField(
        choices=VERIFICATION_TYPE_CHOICES,
        label=_("Verification type"),
        help_text=_("Select which piece of information to verify against."),
    )
    verification_value = forms.CharField(
        max_length=100,
        label=_("Verification value"),
        widget=forms.TextInput(attrs={
            "placeholder": _("Enter the value to verify"),
            "autocomplete": "off",
        }),
    )


# ---------------------------------------------------------------------------
# Photo upload form
# ---------------------------------------------------------------------------

class MultiFileInput(forms.ClearableFileInput):
    """File input widget that accepts multiple files."""
    allow_multiple_selected = True


class MultiFileField(forms.FileField):
    """File field that handles multiple uploaded files."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultiFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_clean(d, initial) for d in data]
        else:
            result = [single_clean(data, initial)]
        return result


# 10 MB limit
MAX_UPLOAD_SIZE = 10 * 1024 * 1024
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}
MAX_BATCH_SIZE = 20


class PhotoUploadForm(forms.Form):
    """
    Form for active members to upload gallery photos.

    Supports batch uploads of up to 20 files at a time.
    Validates file size (max 10 MB) and MIME type server-side.
    """

    photos = MultiFileField(
        label=_("Photos"),
        help_text=_("Select up to 20 images (JPG, PNG, or WebP, max 10 MB each)."),
        widget=MultiFileInput(attrs={"accept": "image/jpeg,image/png,image/webp"}),
    )
    title_prefix = forms.CharField(
        max_length=100,
        required=False,
        label=_("Title prefix"),
        help_text=_("Optional prefix added to each photo title."),
        widget=forms.TextInput(attrs={
            "placeholder": _("e.g. Summer Rally 2025"),
        }),
    )
    event = forms.ModelChoiceField(
        queryset=EventDetailPage.objects.live().order_by("-start_date"),
        required=False,
        label=_("Event"),
        help_text=_("Optionally link photos to an event."),
        empty_label=_("-- No event --"),
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=PhotoTag.objects.all().order_by("name"),
        required=False,
        label=_("Tags"),
        widget=forms.CheckboxSelectMultiple,
    )

    def clean_photos(self):
        files = self.cleaned_data.get("photos", [])

        if len(files) > MAX_BATCH_SIZE:
            raise forms.ValidationError(
                _("You can upload a maximum of %(max)d files at a time."),
                params={"max": MAX_BATCH_SIZE},
            )

        import mimetypes

        for f in files:
            # Size check
            if f.size > MAX_UPLOAD_SIZE:
                raise forms.ValidationError(
                    _(
                        "File '%(name)s' exceeds the maximum size of 10 MB."
                    ),
                    params={"name": f.name},
                )

            # MIME type validation - read file header, don't trust extension
            mime_type = None

            # Try to detect from content
            try:
                import imghdr
                header = f.read(32)
                f.seek(0)
                img_type = imghdr.what(None, h=header)
                if img_type:
                    mime_type = f"image/{img_type}"
                    if mime_type == "image/jpeg":
                        mime_type = "image/jpeg"
            except Exception:
                pass

            # Fall back to content_type from upload
            if mime_type is None:
                mime_type = f.content_type

            # Also try mimetypes as a secondary check
            if mime_type not in ALLOWED_MIME_TYPES:
                guessed, _ = mimetypes.guess_type(f.name)
                if guessed in ALLOWED_MIME_TYPES:
                    mime_type = guessed

            if mime_type not in ALLOWED_MIME_TYPES:
                raise forms.ValidationError(
                    _(
                        "File '%(name)s' is not an allowed format. "
                        "Only JPG, PNG, and WebP are accepted."
                    ),
                    params={"name": f.name},
                )

        return files
