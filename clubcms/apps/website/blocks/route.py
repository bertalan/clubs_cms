"""
Route and waypoint blocks for the Club CMS website.

Blocks for motorcycle route maps with waypoints and elevation.
Template convention: website/blocks/{block_name_snake_case}.html
CSS class convention: block-{block-name} (kebab-case)
"""

from django.utils.translation import gettext_lazy as _

from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    IntegerBlock,
    ListBlock,
    StructBlock,
    TextBlock,
)


# ---------------------------------------------------------------------------
# WaypointBlock
# ---------------------------------------------------------------------------


class WaypointBlock(StructBlock):
    """
    A single waypoint along a motorcycle route.
    """

    name = CharBlock(
        max_length=255,
        required=True,
        help_text=_("Waypoint name (e.g. 'Passo dello Stelvio')."),
    )
    address = CharBlock(
        max_length=500,
        required=False,
        help_text=_("Optional address or location description."),
    )
    coordinates = CharBlock(
        max_length=100,
        required=True,
        help_text=_("Latitude,Longitude (e.g. '46.5287,10.4531')."),
    )
    icon_type = ChoiceBlock(
        choices=[
            ("start", _("Start")),
            ("waypoint", _("Waypoint")),
            ("fuel", _("Fuel stop")),
            ("food", _("Food / restaurant")),
            ("photo", _("Photo spot")),
            ("warning", _("Warning / caution")),
            ("end", _("End")),
        ],
        default="waypoint",
        help_text=_("Marker icon type on the map."),
    )
    notes = TextBlock(
        required=False,
        help_text=_("Optional notes about this waypoint."),
    )

    class Meta:
        icon = "site"
        label = _("Waypoint")


# ---------------------------------------------------------------------------
# RouteBlock
# ---------------------------------------------------------------------------


class RouteBlock(StructBlock):
    """
    Full motorcycle route with multiple waypoints and metadata.
    Rendered as an interactive map with the route path.
    """

    title = CharBlock(
        max_length=255,
        required=True,
        help_text=_("Route name."),
    )
    description = TextBlock(
        required=False,
        help_text=_("Brief route description."),
    )
    waypoints = ListBlock(
        WaypointBlock(),
        min_num=2,
        label=_("Waypoints"),
        help_text=_("At least two waypoints (start and end) are required."),
    )
    route_type = ChoiceBlock(
        choices=[
            ("scenic", _("Scenic ride")),
            ("touring", _("Touring")),
            ("sport", _("Sport / twisties")),
            ("offroad", _("Off-road / adventure")),
            ("commute", _("Commute / practical")),
        ],
        default="touring",
        help_text=_("Type of route."),
    )
    distance = CharBlock(
        max_length=50,
        required=False,
        help_text=_("Approximate distance (e.g. '320 km')."),
    )
    elevation = CharBlock(
        max_length=50,
        required=False,
        help_text=_("Elevation gain (e.g. '2500 m')."),
    )
    estimated_duration = CharBlock(
        max_length=50,
        required=False,
        help_text=_("Estimated riding time (e.g. '5-6 hours')."),
    )
    difficulty = ChoiceBlock(
        choices=[
            ("easy", _("Easy")),
            ("moderate", _("Moderate")),
            ("challenging", _("Challenging")),
            ("expert", _("Expert")),
        ],
        default="moderate",
        help_text=_("Route difficulty level."),
    )
    map_height = IntegerBlock(
        default=500,
        help_text=_("Map height in pixels."),
    )

    class Meta:
        template = "website/blocks/route_block.html"
        icon = "site"
        label = _("Route map")
