"""
Federation frontend URL patterns.

Included at /eventi/partner/ when FEDERATION_ENABLED is True.
"""

from django.urls import path

from apps.federation.views import (
    AddCommentView,
    DeleteCommentView,
    ExternalEventDetailView,
    ExternalEventsListView,
    SetInterestView,
)

app_name = "federation_frontend"

urlpatterns = [
    path("", ExternalEventsListView.as_view(), name="list"),
    path(
        "<str:club_code>/<uuid:event_id>/",
        ExternalEventDetailView.as_view(),
        name="detail",
    ),
    path(
        "<str:club_code>/<uuid:event_id>/interest/",
        SetInterestView.as_view(),
        name="set_interest",
    ),
    path(
        "<str:club_code>/<uuid:event_id>/comment/",
        AddCommentView.as_view(),
        name="add_comment",
    ),
    path(
        "<str:club_code>/<uuid:event_id>/comment/delete/",
        DeleteCommentView.as_view(),
        name="delete_comment",
    ),
]
