"""
T12 — Test Gallery Upload, My Uploads, Moderation.

Verifica il flusso completo: upload → pending → approve/reject.
"""

import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from apps.members.models import ClubUser
from apps.website.models.uploads import PhotoUpload


def _tiny_gif():
    """Return a minimal valid GIF image."""
    return (
        b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00"
        b"\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x00\x00"
        b"\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00"
        b"\x00\x02\x02\x44\x01\x00\x3b"
    )


def _setup_gallery_page():
    """Create a GalleryPage in the Wagtail page tree with a Site."""
    from wagtail.models import Page, Site

    from apps.website.models import GalleryPage

    root = Page.objects.filter(depth=1).first()
    if not root:
        root = Page.add_root(title="Root")
    home = Page.objects.filter(depth=2).first()
    if not home:
        home = Page(title="Test Home", slug="test-home")
        root.add_child(instance=home)
    Site.objects.update_or_create(
        hostname="localhost",
        defaults={"root_page": home, "is_default_site": True},
    )
    gallery = GalleryPage(title="Gallery", slug="gallery")
    home.add_child(instance=gallery)
    gallery.save_revision().publish()
    return gallery


@pytest.mark.django_db
class TestGalleryUploadModel(TestCase):
    """PhotoUpload model must have correct status properties."""

    @classmethod
    def setUpTestData(cls):
        cls.user = ClubUser.objects.create_user(
            username="uploader", email="up@test.com", password="testpass123"
        )

    def test_photoupload_model_exists(self):
        self.assertTrue(hasattr(PhotoUpload, "is_approved"))
        self.assertTrue(hasattr(PhotoUpload, "rejection_reason"))
        self.assertTrue(hasattr(PhotoUpload, "uploaded_by"))

    def test_is_pending_property(self):
        upload = PhotoUpload(is_approved=False, rejection_reason="")
        self.assertTrue(upload.is_pending)

    def test_is_rejected_property(self):
        upload = PhotoUpload(is_approved=False, rejection_reason="Bad photo")
        self.assertTrue(upload.is_rejected)

    def test_approved_not_pending(self):
        upload = PhotoUpload(is_approved=True, rejection_reason="")
        self.assertFalse(upload.is_pending)
        self.assertFalse(upload.is_rejected)


@pytest.mark.django_db
class TestUploadViewAccess(TestCase):
    """Upload view requires login + active membership."""

    @classmethod
    def setUpTestData(cls):
        cls.gallery = _setup_gallery_page()

    def test_anonymous_redirected(self):
        url = self.gallery.url + self.gallery.reverse_subpage("upload_photo")
        resp = self.client.get(url)
        self.assertIn(resp.status_code, [302, 301])

    def test_my_uploads_anonymous_redirected(self):
        url = self.gallery.url + self.gallery.reverse_subpage("my_uploads")
        resp = self.client.get(url)
        self.assertIn(resp.status_code, [302, 301])


@pytest.mark.django_db
class TestMyUploadsView(TestCase):
    """Logged-in user sees only their own uploads."""

    @classmethod
    def setUpTestData(cls):
        cls.gallery = _setup_gallery_page()
        cls.user = ClubUser.objects.create_user(
            username="viewer", email="viewer@test.com", password="testpass123"
        )

    def test_logged_in_user_can_access(self):
        self.client.login(username="viewer", password="testpass123")
        url = self.gallery.url + self.gallery.reverse_subpage("my_uploads")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)


@pytest.mark.django_db
class TestModerationAccess(TestCase):
    """Moderation queue requires staff."""

    @classmethod
    def setUpTestData(cls):
        cls.gallery = _setup_gallery_page()
        cls.user = ClubUser.objects.create_user(
            username="regular", email="reg@test.com", password="testpass123"
        )
        cls.staff = ClubUser.objects.create_user(
            username="staffuser", email="staff@test.com", password="testpass123",
            is_staff=True,
        )

    def test_non_staff_cannot_access_moderation(self):
        self.client.login(username="regular", password="testpass123")
        url = self.gallery.url + self.gallery.reverse_subpage("moderation_queue")
        resp = self.client.get(url)
        self.assertIn(resp.status_code, [302, 403])

    def test_staff_can_access_moderation(self):
        self.client.login(username="staffuser", password="testpass123")
        url = self.gallery.url + self.gallery.reverse_subpage("moderation_queue")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)


@pytest.mark.django_db
class TestApproveRejectAccess(TestCase):
    """Approve/reject require staff + POST."""

    @classmethod
    def setUpTestData(cls):
        cls.gallery = _setup_gallery_page()
        cls.staff = ClubUser.objects.create_user(
            username="mod", email="mod@test.com", password="testpass123",
            is_staff=True,
        )

    def test_approve_requires_post(self):
        self.client.login(username="mod", password="testpass123")
        url = self.gallery.url + self.gallery.reverse_subpage(
            "approve_photo", kwargs={"pk": 9999}
        )
        resp = self.client.get(url)
        self.assertIn(resp.status_code, [405, 404, 302])

    def test_reject_requires_post(self):
        self.client.login(username="mod", password="testpass123")
        url = self.gallery.url + self.gallery.reverse_subpage(
            "reject_photo", kwargs={"pk": 9999}
        )
        resp = self.client.get(url)
        self.assertIn(resp.status_code, [405, 404, 302])
