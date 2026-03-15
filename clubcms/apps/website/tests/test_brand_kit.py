"""
T20 — Test Brand Kit: BrandAsset snippet, PressRelease snippet, PressPage model.
"""

from datetime import date

from django.test import TestCase

from apps.website.models.snippets import BrandAsset, PressRelease


class TestBrandAssetModel(TestCase):
    """BrandAsset snippet fields and ordering."""

    def test_create_brand_asset(self):
        asset = BrandAsset.objects.create(
            name="Club Logo",
            category="logo",
            description="Official logo in SVG format.",
            order=1,
        )
        self.assertEqual(asset.name, "Club Logo")
        self.assertEqual(asset.category, "logo")

    def test_str_representation(self):
        asset = BrandAsset.objects.create(
            name="Main Font", category="font", order=0
        )
        self.assertEqual(str(asset), "Main Font")

    def test_ordering_by_order_then_name(self):
        BrandAsset.objects.create(name="Z Asset", category="photo", order=1)
        BrandAsset.objects.create(name="A Asset", category="logo", order=2)
        BrandAsset.objects.create(name="M Asset", category="font", order=1)
        assets = list(BrandAsset.objects.all())
        self.assertEqual(assets[0].name, "M Asset")  # order=1, name M
        self.assertEqual(assets[1].name, "Z Asset")  # order=1, name Z
        self.assertEqual(assets[2].name, "A Asset")  # order=2

    def test_category_choices(self):
        for cat in ("logo", "font", "photo", "template"):
            asset = BrandAsset(name=f"Test {cat}", category=cat)
            asset.full_clean()  # Should not raise


class TestPressReleaseModel(TestCase):
    """PressRelease snippet fields and ordering."""

    def test_create_press_release(self):
        pr = PressRelease.objects.create(
            title="New Partnership Announced",
            date=date(2026, 3, 1),
            body="<p>We are excited to announce...</p>",
        )
        self.assertEqual(pr.title, "New Partnership Announced")
        self.assertFalse(pr.is_archived)

    def test_str_representation(self):
        pr = PressRelease.objects.create(
            title="Annual Report",
            date=date(2026, 1, 15),
            body="Report content",
        )
        self.assertIn("Annual Report", str(pr))
        self.assertIn("2026-01-15", str(pr))

    def test_ordering_newest_first(self):
        PressRelease.objects.create(
            title="Old", date=date(2025, 6, 1), body="Old content"
        )
        PressRelease.objects.create(
            title="New", date=date(2026, 3, 1), body="New content"
        )
        releases = list(PressRelease.objects.all())
        self.assertEqual(releases[0].title, "New")
        self.assertEqual(releases[1].title, "Old")

    def test_archived_flag(self):
        pr = PressRelease.objects.create(
            title="Archived Release",
            date=date(2024, 1, 1),
            body="Old content",
            is_archived=True,
        )
        self.assertTrue(pr.is_archived)


class TestPressPageModel(TestCase):
    """PressPage page model exists and has correct config."""

    def test_press_page_class_exists(self):
        from apps.website.models.pages import PressPage
        self.assertTrue(hasattr(PressPage, "press_email"))
        self.assertTrue(hasattr(PressPage, "press_phone"))
        self.assertTrue(hasattr(PressPage, "press_contact"))
        self.assertTrue(hasattr(PressPage, "intro"))

    def test_press_page_max_count_is_one(self):
        from apps.website.models.pages import PressPage
        self.assertEqual(PressPage.max_count, 1)
