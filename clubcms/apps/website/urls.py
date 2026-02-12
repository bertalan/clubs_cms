"""
URL patterns for the website app.

Registered with app_name="website" and included in the root URL conf
before the Wagtail catch-all.
"""

from django.urls import path

from apps.website import views

app_name = "website"

urlpatterns = [
    # Partner member verification
    path(
        "partners/verify-member/",
        views.VerifyMemberView.as_view(),
        name="verify_member",
    ),
    # Gallery photo upload
    path(
        "upload-photo/",
        views.PhotoUploadView.as_view(),
        name="upload_photo",
    ),
    # My uploads
    path(
        "my-uploads/",
        views.MyUploadsView.as_view(),
        name="my_uploads",
    ),
    # Moderation queue (staff only)
    path(
        "moderation/",
        views.ModerationQueueView.as_view(),
        name="moderation_queue",
    ),
    # Approve / reject photos (staff only, POST)
    path(
        "moderation/approve/<int:pk>/",
        views.ApprovePhotoView.as_view(),
        name="approve_photo",
    ),
    path(
        "moderation/reject/<int:pk>/",
        views.RejectPhotoView.as_view(),
        name="reject_photo",
    ),
]
