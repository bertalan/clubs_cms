"""
Common block settings shared by all section-level StreamField blocks.

Every top-level block gets a ``settings`` field (collapsed in the editor)
with: custom_id, custom_class, background, padding.
"""

from django.utils.translation import gettext_lazy as _

from wagtail.blocks import CharBlock, ChoiceBlock, StructBlock


BACKGROUND_CHOICES = [
    ("default", _("Default")),
    ("light", _("Light")),
    ("dark", _("Dark")),
    ("primary", _("Primary colour")),
]

PADDING_CHOICES = [
    ("md", _("Medium")),
    ("sm", _("Small")),
    ("lg", _("Large")),
    ("none", _("None")),
]


class BlockSettings(StructBlock):
    """
    Common settings panel for all section-level blocks.

    Adds custom HTML id, extra CSS classes, background variant,
    and padding size.
    """

    custom_id = CharBlock(
        max_length=100,
        required=False,
        label=_("Anchor ID"),
        help_text=_(
            "Lets you link straight to this section, for example "
            "/about/#opening-hours. Use only letters, numbers, hyphens "
            "and underscores."
        ),
    )
    custom_class = CharBlock(
        max_length=255,
        required=False,
        label=_("Extra CSS classes"),
        help_text=_(
            "Leave empty unless your web designer gives you a class name. "
            "Separate several classes with spaces."
        ),
    )
    background = ChoiceBlock(
        choices=BACKGROUND_CHOICES,
        default="default",
        label=_("Background"),
    )
    padding = ChoiceBlock(
        choices=PADDING_CHOICES,
        default="md",
        label=_("Padding"),
    )

    class Meta:
        icon = "cog"
        label = _("Advanced settings")
        form_classname = "struct-block block-settings collapsed"
