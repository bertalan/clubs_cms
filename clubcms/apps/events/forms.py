"""
Forms for the events app.

Provides EventRegistrationForm for authenticated users and
GuestRegistrationForm for non-logged-in visitors.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.events.models import EventRegistration


# ---------------------------------------------------------------------------
# WCAG 2.2 helpers (GAP-11..15)
# ---------------------------------------------------------------------------

# Map field names to HTML autocomplete attribute values
_AUTOCOMPLETE_MAP = {
    "first_name": "given-name",
    "last_name": "family-name",
    "email": "email",
    "passenger_email": "email",
    "passenger_first_name": "given-name",
    "passenger_last_name": "family-name",
    "passenger_phone": "tel",
    "passenger_birth_date": "bday",
}

# CSS class for each widget type
_CSS_CLASS_MAP = {
    forms.TextInput: "form-input",
    forms.EmailInput: "form-input",
    forms.NumberInput: "form-input",
    forms.DateInput: "form-input",
    forms.Textarea: "form-textarea",
    forms.Select: "form-select",
    forms.CheckboxInput: "form-check-input",
}


def _apply_wcag_attrs(form):
    """
    Apply WCAG 2.2 attributes to all fields in a form.

    - aria-describedby pointing to the help-text element
    - aria-required="true" on required fields
    - autocomplete on personal-data fields
    - CSS classes on widgets
    """
    for name, field in form.fields.items():
        widget = field.widget
        attrs = widget.attrs

        # GAP-11: aria-describedby (help text element id convention)
        if field.help_text:
            attrs["aria-describedby"] = f"help_{name}"

        # GAP-12: aria-required
        if field.required:
            attrs["aria-required"] = "true"

        # GAP-14: autocomplete
        if name in _AUTOCOMPLETE_MAP:
            attrs["autocomplete"] = _AUTOCOMPLETE_MAP[name]

        # GAP-13: CSS classes
        widget_type = type(widget)
        if widget_type in _CSS_CLASS_MAP:
            existing = attrs.get("class", "")
            css_class = _CSS_CLASS_MAP[widget_type]
            if css_class not in existing:
                attrs["class"] = f"{existing} {css_class}".strip()


# ---------------------------------------------------------------------------
# 1. EventRegistrationForm — for authenticated users
# ---------------------------------------------------------------------------


class EventRegistrationForm(forms.ModelForm):
    """
    Form for authenticated users to register for an event.

    Includes optional passenger/companion fields and a required
    accept_terms checkbox (not persisted to the model).
    """

    accept_terms = forms.BooleanField(
        required=True,
        label=_("I accept the <a href='/privacy/' target='_blank' rel='noopener'>terms and conditions</a>"),
        help_text=_("You must accept the terms to register."),
    )

    class Meta:
        model = EventRegistration
        fields = [
            "guests",
            "guest_names",
            "notes",
            "has_passenger",
            "passenger_is_member",
            "passenger_member",
            "passenger_first_name",
            "passenger_last_name",
            "passenger_email",
            "passenger_phone",
            "passenger_fiscal_code",
            "passenger_birth_date",
            "passenger_emergency_contact",
        ]
        labels = {
            "guests": _("Additional guests"),
            "guest_names": _("Guest names"),
            "notes": _("Notes"),
            "has_passenger": _("I have a passenger / companion"),
            "passenger_is_member": _("Passenger is a club member"),
            "passenger_member": _("Select member"),
            "passenger_first_name": _("Passenger first name"),
            "passenger_last_name": _("Passenger last name"),
            "passenger_email": _("Passenger email"),
            "passenger_phone": _("Passenger phone"),
            "passenger_fiscal_code": _("Fiscal code (Codice Fiscale)"),
            "passenger_birth_date": _("Passenger date of birth"),
            "passenger_emergency_contact": _("Emergency contact"),
        }
        help_texts = {
            "guests": _(
                "Number of extra people coming with you (not counting yourself "
                "or your passenger). Example: 2"
            ),
            "guest_names": _(
                "List each guest on a separate line. "
                "Example:\nMario Rossi\nLucia Bianchi"
            ),
            "notes": _(
                "Allergies, dietary needs, special requests, or anything the "
                "organizers should know."
            ),
            "has_passenger": _(
                "Check this if someone will ride with you as a passenger on "
                "your motorcycle."
            ),
            "passenger_is_member": _(
                "If your passenger is already a club member, enable this to "
                "select them from the list."
            ),
            "passenger_member": _(
                "Start typing a name to search registered members."
            ),
            "passenger_first_name": _("Example: Marco"),
            "passenger_last_name": _("Example: Verdi"),
            "passenger_email": _("Example: marco.verdi@email.com"),
            "passenger_phone": _(
                "Include country prefix. Example: +39 333 1234567"
            ),
            "passenger_fiscal_code": _(
                "Italian tax identification code, 16 characters. "
                "Example: VRDMRC85M01H501Z"
            ),
            "passenger_birth_date": _("Example: 1985-08-01"),
            "passenger_emergency_contact": _(
                "Name and phone number to call in case of emergency. "
                "Example: Anna Verdi +39 340 7654321"
            ),
        }
        widgets = {
            "guests": forms.NumberInput(attrs={
                "min": "0",
                "max": "20",
                "placeholder": "0",
            }),
            "guest_names": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Mario Rossi\nLucia Bianchi",
            }),
            "notes": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "e.g. vegetarian meal, wheelchair access...",
            }),
            "passenger_birth_date": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "passenger_phone": forms.TextInput(attrs={
                "placeholder": "+39 333 1234567",
            }),
            "passenger_fiscal_code": forms.TextInput(attrs={
                "maxlength": "16",
                "placeholder": "VRDMRC85M01H501Z",
                "style": "text-transform: uppercase;",
            }),
            "passenger_emergency_contact": forms.TextInput(attrs={
                "placeholder": "Anna Verdi +39 340 7654321",
            }),
        }

    def __init__(self, *args, **kwargs):
        self.event_page = kwargs.pop("event_page", None)
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Passenger fields are not required by default
        passenger_fields = [
            "passenger_is_member",
            "passenger_member",
            "passenger_first_name",
            "passenger_last_name",
            "passenger_email",
            "passenger_phone",
            "passenger_fiscal_code",
            "passenger_birth_date",
            "passenger_emergency_contact",
        ]
        for field_name in passenger_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False

        # --- WCAG 2.2 enhancements (GAP-11..16) ---
        _apply_wcag_attrs(self)

    def clean(self):
        cleaned_data = super().clean()
        has_passenger = cleaned_data.get("has_passenger", False)

        if has_passenger:
            is_member = cleaned_data.get("passenger_is_member", False)
            if is_member:
                if not cleaned_data.get("passenger_member"):
                    self.add_error(
                        "passenger_member",
                        _("Please select the member who will be your passenger."),
                    )
            else:
                if not cleaned_data.get("passenger_first_name"):
                    self.add_error(
                        "passenger_first_name",
                        _("Passenger first name is required."),
                    )
                if not cleaned_data.get("passenger_last_name"):
                    self.add_error(
                        "passenger_last_name",
                        _("Passenger last name is required."),
                    )

        return cleaned_data


# ---------------------------------------------------------------------------
# 2. GuestRegistrationForm — for non-authenticated users
# ---------------------------------------------------------------------------


class GuestRegistrationForm(EventRegistrationForm):
    """
    Extended registration form for guest (non-authenticated) users.

    Adds required first_name, last_name, and email fields that are
    stored directly on the EventRegistration record.
    """

    first_name = forms.CharField(
        max_length=150,
        required=True,
        label=_("First name"),
        help_text=_("Your legal first name. Example: Maria"),
        widget=forms.TextInput(attrs={"placeholder": "Maria"}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label=_("Last name"),
        help_text=_("Your family name. Example: Rossi"),
        widget=forms.TextInput(attrs={"placeholder": "Rossi"}),
    )
    email = forms.EmailField(
        required=True,
        label=_("Email"),
        help_text=_("We will send your registration confirmation here."),
        widget=forms.EmailInput(attrs={"placeholder": "maria.rossi@email.com"}),
    )

    class Meta(EventRegistrationForm.Meta):
        fields = [
            "first_name",
            "last_name",
            "email",
        ] + EventRegistrationForm.Meta.fields

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        if not email:
            raise forms.ValidationError(_("Email is required for guest registrations."))
        return email
