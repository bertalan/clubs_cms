"""
URL patterns for the website app.

Registered with app_name="website" and included in the root URL conf
before the Wagtail catch-all.
"""

from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.website import views

app_name = "website"

urlpatterns = [
    # Newsletter subscribe
    path(
        "newsletter/subscribe/",
        views.NewsletterSubscribeView.as_view(),
        name="newsletter-subscribe",
    ),
    # Newsletter unsubscribe
    path(
        "newsletter/unsubscribe/",
        views.NewsletterUnsubscribeView.as_view(),
        name="newsletter-unsubscribe",
    ),
    # Newsletter archive
    path(
        "newsletter/",
        views.NewsletterArchiveView.as_view(),
        name="newsletter-archive",
    ),
    # Newsletter detail
    path(
        "newsletter/<int:pk>/",
        views.NewsletterDetailView.as_view(),
        name="newsletter-detail",
    ),
    # Partner member verification
    path(
        _("partners/verify-member/"),
        views.VerifyMemberView.as_view(),
        name="verify_member",
    ),
]
