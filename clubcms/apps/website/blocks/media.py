"""
Media blocks for the Club CMS website.

Blocks for images, galleries, videos, documents, and maps.
Template convention: website/blocks/{block_name_snake_case}.html
CSS class convention: block-{block-name} (kebab-case)
"""

from django.utils.translation import gettext_lazy as _

from wagtail.blocks import (
    BooleanBlock,
    CharBlock,
    ChoiceBlock,
    IntegerBlock,
    ListBlock,
    StructBlock,
    TextBlock,
)
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

from .common import BlockSettings


# ---------------------------------------------------------------------------
# GalleryImageBlock / GalleryBlock
# ---------------------------------------------------------------------------


class GalleryImageBlock(StructBlock):
    """
    Individual image with caption, used inside a GalleryBlock.
    """

    image = ImageChooserBlock(
        required=True,
        label=_("Image"),
    )
    caption = CharBlock(
        max_length=255,
        required=False,
        label=_("Caption"),
        help_text=_(
            "Shown under the image and read out by screen readers. If empty, "
            "the image title is read out instead."
        ),
    )

    class Meta:
        icon = "image"
        label = _("Gallery image")


class GalleryBlock(StructBlock):
    """
    Image gallery grid with lightbox support.
    """

    title = CharBlock(
        max_length=255,
        required=False,
        label=_("Title"),
    )
    images = ListBlock(
        GalleryImageBlock(),
        min_num=1,
        label=_("Images"),
    )
    columns = ChoiceBlock(
        choices=[
            ("2", _("2 columns")),
            ("3", _("3 columns")),
            ("4", _("4 columns")),
            ("6", _("6 columns")),
        ],
        default="3",
        label=_("Columns"),
    )
    lightbox = BooleanBlock(
        default=True,
        required=False,
        label=_("Link to large version"),
        help_text=_("Each thumbnail links to the image at up to 1600 x 1200 pixels."),
    )
    aspect_ratio = ChoiceBlock(
        choices=[
            ("auto", _("Auto (original)")),
            ("1x1", _("Square (1:1)")),
            ("4x3", _("Landscape (4:3)")),
            ("16x9", _("Widescreen (16:9)")),
            ("3x4", _("Portrait (3:4)")),
        ],
        default="auto",
        label=_("Thumbnail shape"),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

    class Meta:
        template = "website/blocks/gallery_block.html"
        icon = "image"
        label = _("Gallery")


# ---------------------------------------------------------------------------
# VideoEmbedBlock
# ---------------------------------------------------------------------------


class VideoEmbedBlock(StructBlock):
    """
    Embedded video from YouTube, Vimeo, or other supported providers.
    """

    video = EmbedBlock(
        required=True,
        label=_("Video link"),
        help_text=_(
            "Paste the address of the video page, for example "
            "https://www.youtube.com/watch?v=abc123 or a Vimeo link."
        ),
    )
    caption = CharBlock(
        max_length=255,
        required=False,
        label=_("Caption"),
    )
    autoplay = BooleanBlock(
        default=False,
        required=False,
        label=_("Autoplay"),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

    class Meta:
        template = "website/blocks/video_embed_block.html"
        icon = "media"
        label = _("Video embed")


# ---------------------------------------------------------------------------
# ImageBlock
# ---------------------------------------------------------------------------


class ImageBlock(StructBlock):
    """
    Single image with caption and alignment options.
    """

    image = ImageChooserBlock(
        required=True,
        label=_("Image"),
        help_text=_(
            "Resized, not cropped: 1200 pixels wide at full width, 800 when "
            "centred, 600 when floated."
        ),
    )
    caption = CharBlock(
        max_length=255,
        required=False,
        label=_("Caption"),
        help_text=_(
            "Shown under the image and read out "
            "by screen readers as its description."
        ),
    )
    alignment = ChoiceBlock(
        choices=[
            ("full", _("Full width")),
            ("center", _("Centred")),
            ("left", _("Float left")),
            ("right", _("Float right")),
        ],
        default="full",
        label=_("Alignment"),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

    class Meta:
        template = "website/blocks/image_block.html"
        icon = "image"
        label = _("Image")


# ---------------------------------------------------------------------------
# DocumentBlock / DocumentListBlock
# ---------------------------------------------------------------------------


class DocumentBlock(StructBlock):
    """
    Single document download link with an optional description.
    """

    document = DocumentChooserBlock(
        required=True,
        label=_("Document"),
        help_text=_("Visitors see the document title as the download link."),
    )
    description = TextBlock(
        required=False,
        label=_("Description"),
        help_text=_("Shown under the download link."),
    )

    class Meta:
        template = "website/blocks/document_block.html"
        icon = "doc-full"
        label = _("Document")


class DocumentListBlock(StructBlock):
    """
    List of downloadable documents with a section title.
    """

    title = CharBlock(
        max_length=255,
        required=False,
        label=_("Title"),
    )
    documents = ListBlock(
        DocumentBlock(),
        min_num=1,
        label=_("Documents"),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

    class Meta:
        template = "website/blocks/document_list_block.html"
        icon = "doc-full"
        label = _("Document list")


# ---------------------------------------------------------------------------
# MapBlock
# ---------------------------------------------------------------------------


class MapBlock(StructBlock):
    """
    Interactive map block with address and coordinates.
    Uses OpenStreetMap / Leaflet by default for GDPR compliance.
    """

    address = CharBlock(
        max_length=500,
        required=False,
        label=_("Address"),
        help_text=_("Shown as text under the map."),
    )
    coordinates = CharBlock(
        max_length=100,
        required=True,
        label=_("Coordinates"),
        help_text=_(
            "Latitude and longitude separated by a comma, for example "
            "45.4642,9.1900."
        ),
    )
    zoom = IntegerBlock(
        default=14,
        min_value=1,
        max_value=20,
        label=_("Zoom level"),
        help_text=_("Higher numbers zoom in closer, for example 14 for a town."),
    )
    height = IntegerBlock(
        default=400,
        label=_("Map height"),
        help_text=_("In pixels, for example 400."),
    )
    title = CharBlock(
        max_length=255,
        required=False,
        label=_("Title"),
        help_text=_("Shown as a heading above the map."),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

    class Meta:
        template = "website/blocks/map_block.html"
        icon = "site"
        label = _("Map")
