"""
Regression tests for 500 errors found by static analysis (ruff F821/F823).

- VerifyMemberView.form_valid used `render` and `_get_client_ip` without
  importing them (lost in commit 4b4bdab).
- PhotoUploadForm.clean_photos rebound `_` via tuple unpacking, turning the
  gettext alias into an unbound local on every validation error path.
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.members.models import ClubUser
from apps.website.forms import MAX_BATCH_SIZE, PhotoUploadForm
from apps.website.models.verification import VerificationLog


@pytest.mark.django_db
class TestVerifyMemberViewPost(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = ClubUser.objects.create_user(
            username="verifier",
            email="verifier@test.com",
            password="testpass123",
            is_staff=True,
        )

    def test_post_unknown_card_renders_not_found(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("website:verify_member"),
            {
                "card_number": "DOES-NOT-EXIST",
                "verification_type": "display_name",
                "verification_value": "Nobody",
            },
            REMOTE_ADDR="203.0.113.7",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["result"], "not_found")
        log = VerificationLog.objects.get(card_number="DOES-NOT-EXIST")
        self.assertEqual(log.ip_address, "203.0.113.7")


class TestPhotoUploadFormValidation(TestCase):
    def _gif(self, name):
        return SimpleUploadedFile(name, b"GIF89a", content_type="image/gif")

    def test_too_many_files_is_a_validation_error(self):
        files = [self._gif(f"p{i}.gif") for i in range(MAX_BATCH_SIZE + 1)]
        form = PhotoUploadForm(data={}, files={"photos": files})
        form.cleaned_data = {"photos": files}
        with self.assertRaisesMessage(Exception, str(MAX_BATCH_SIZE)) as ctx:
            form.clean_photos()
        self.assertEqual(type(ctx.exception).__name__, "ValidationError")

    def test_disallowed_type_is_a_validation_error(self):
        files = [self._gif("p.gif")]
        form = PhotoUploadForm(data={}, files={"photos": files})
        form.cleaned_data = {"photos": files}
        with self.assertRaises(Exception) as ctx:
            form.clean_photos()
        self.assertEqual(type(ctx.exception).__name__, "ValidationError")
