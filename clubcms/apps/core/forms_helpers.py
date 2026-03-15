"""
Shared WCAG 2.2 form helpers for ClubCMS.

Provides CSS class mapping, autocomplete attributes, and aria-*
enhancements that can be applied to any Django ModelForm.

Extracted from apps/events/forms.py to be reused across all apps.
"""

from django import forms

# ---------------------------------------------------------------------------
# WCAG 2.2 helpers
# ---------------------------------------------------------------------------

# Map field names to HTML autocomplete attribute values
_AUTOCOMPLETE_MAP = {
    # Event registration fields
    "first_name": "given-name",
    "last_name": "family-name",
    "email": "email",
    "passenger_email": "email",
    "passenger_first_name": "given-name",
    "passenger_last_name": "family-name",
    "passenger_phone": "tel",
    "passenger_birth_date": "bday",
    # Member profile fields
    "phone": "tel",
    "mobile": "tel",
    "birth_date": "bday",
    "address": "street-address",
    "city": "address-level2",
    "postal_code": "postal-code",
    "country": "country",
    # Signup / auth fields
    "username": "username",
    "display_name": "nickname",
    "password1": "new-password",
    "password2": "new-password",
    # Identity documents
    "fiscal_code": "off",
    "document_number": "off",
    "passenger_fiscal_code": "off",
    "passenger_emergency_contact": "off",
    # Contact fields (mutual aid)
    "requester_name": "name",
    "requester_phone": "tel",
    "requester_email": "email",
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

        # aria-describedby (help text element id convention)
        if field.help_text:
            attrs["aria-describedby"] = f"help_{name}"

        # aria-required
        if field.required:
            attrs["aria-required"] = "true"

        # autocomplete
        if name in _AUTOCOMPLETE_MAP:
            attrs["autocomplete"] = _AUTOCOMPLETE_MAP[name]

        # CSS classes
        widget_type = type(widget)
        if widget_type in _CSS_CLASS_MAP:
            existing = attrs.get("class", "")
            css_class = _CSS_CLASS_MAP[widget_type]
            if css_class not in existing:
                attrs["class"] = f"{existing} {css_class}".strip()
