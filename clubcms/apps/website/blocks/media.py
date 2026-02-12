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


# ---------------------------------------------------------------------------
# GalleryImageBlock / GalleryBlock
# ---------------------------------------------------------------------------


class GalleryImageBlock(StructBlock):
    """
    Individual image with caption, used inside a GalleryBlock.
    """

    image = ImageChooserBlock(
        required=True,
    )
    caption = CharBlock(
        max_length=255,
        required=False,
        help_text=_("Optional caption displayed below the image."),
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
        help_text=_("Optional gallery title."),
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
        help_text=_("Number of columns on desktop."),
    )
    lightbox = BooleanBlock(
        default=True,
        required=False,
        help_text=_("Enable lightbox for full-size image viewing."),
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
        help_text=_("Thumbnail aspect ratio."),
    )

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
        help_text=_("Paste a video URL (YouTube, Vimeo, etc.)."),
    )
    caption = CharBlock(
        max_length=255,
        required=False,
        help_text=_("Optional caption displayed below the video."),
    )
    autoplay = BooleanBlock(
        default=False,
        required=False,
        help_text=_("Autoplay the video (muted)."),
    )

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
    )
    caption = CharBlock(
        max_length=255,
        required=False,
    )
    alignment = ChoiceBlock(
        choices=[
            ("full", _("Full width")),
            ("center", _("Centred")),
            ("left", _("Float left")),
            ("right", _("Float right")),
        ],
        default="full",
        help_text=_("Image alignment within the content area."),
    )

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
    )
    description = TextBlock(
        required=False,
        help_text=_("Optional description of the document."),
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
        help_text=_("Section title for the document list."),
    )
    documents = ListBlock(
        DocumentBlock(),
        min_num=1,
        label=_("Documents"),
    )

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
        help_text=_("Display address (shown in the info popup)."),
    )
    coordinates = CharBlock(
        max_length=100,
        required=True,
        help_text=_("Latitude,Longitude (e.g. '45.4642,9.1900')."),
    )
    zoom = IntegerBlock(
        default=14,
        min_value=1,
        max_value=20,
        help_text=_("Map zoom level (1-20)."),
    )
    height = IntegerBlock(
        default=400,
        help_text=_("Map height in pixels."),
    )
    title = CharBlock(
        max_length=255,
        required=False,
        help_text=_("Optional marker label."),
    )

    class Meta:
        template = "website/blocks/map_block.html"
        icon = "site"
        label = _("Map")
