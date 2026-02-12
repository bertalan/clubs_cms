"""
Wagtail hooks for the members app.

Registers the ClubUser ModelViewSet with the Wagtail admin.
"""

from wagtail import hooks

from apps.members.admin import clubuser_viewset


@hooks.register("register_admin_viewset")
def register_clubuser_viewset():
    return clubuser_viewset
