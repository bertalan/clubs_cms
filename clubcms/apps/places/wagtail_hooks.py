from wagtail import hooks


@hooks.register("construct_explorer_page_queryset")
def order_places_by_title(parent_page, pages, request):
    """Ordina i luoghi per titolo nell'explorer di Wagtail."""
    from apps.places.models import PlaceIndexPage

    if isinstance(parent_page, PlaceIndexPage):
        return pages.order_by("title")
    return pages
