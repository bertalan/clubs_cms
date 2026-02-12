"""
Tests for mutual aid access control logic.

Tests ContactUnlock limits, FederatedAidAccess, and AidPrivacySettings.
"""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone

from apps.federation.models import FederatedClub
from apps.mutual_aid.models import (
    AidPrivacySettings,
    ContactUnlock,
    FederatedAidAccess,
)

User = get_user_model()


# ---------------------------------------------------------------------------
# Contact Unlock Limit Tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestContactUnlockLimits:
    """Tests for ContactUnlock.can_unlock() rate limiting."""

    def test_can_unlock_with_no_unlocks(self):
        """First unlock should be allowed when no previous unlocks exist."""
        club = FederatedClub.objects.create(
            name="Test Club",
            short_code="TST",
            base_url="https://example.com",
            api_key="test_api_key_12345",
            is_active=True,
            is_approved=True,
        )
        federated_access = FederatedAidAccess.objects.create(
            source_club=club,
            external_user_id="ext_user_001",
            external_display_name="External User",
            access_level="contact",
        )

        assert ContactUnlock.can_unlock(federated_access) is True

    def test_can_unlock_with_two_unlocks(self):
        """Second and third unlocks should be allowed (under the limit of 3)."""
        club = FederatedClub.objects.create(
            name="Test Club",
            short_code="TST2",
            base_url="https://example.com",
            api_key="test_api_key_12345",
            is_active=True,
            is_approved=True,
        )
        federated_access = FederatedAidAccess.objects.create(
            source_club=club,
            external_user_id="ext_user_002",
            external_display_name="External User",
            access_level="contact",
        )

        # Create two helpers and unlock their contacts
        helper1 = User.objects.create_user(username="helper1", password="testpass123!")
        helper2 = User.objects.create_user(username="helper2", password="testpass123!")

        ContactUnlock.objects.create(federated_access=federated_access, helper=helper1)
        ContactUnlock.objects.create(federated_access=federated_access, helper=helper2)

        # With 2 unlocks, should still be able to unlock one more
        assert ContactUnlock.can_unlock(federated_access) is True

    def test_cannot_unlock_at_limit(self):
        """When 3 unlocks exist in the 30-day window, can_unlock returns False."""
        club = FederatedClub.objects.create(
            name="Test Club",
            short_code="TST3",
            base_url="https://example.com",
            api_key="test_api_key_12345",
            is_active=True,
            is_approved=True,
        )
        federated_access = FederatedAidAccess.objects.create(
            source_club=club,
            external_user_id="ext_user_003",
            external_display_name="External User",
            access_level="contact",
        )

        # Create 3 helpers and unlock their contacts
        helper1 = User.objects.create_user(username="helper3a", password="testpass123!")
        helper2 = User.objects.create_user(username="helper3b", password="testpass123!")
        helper3 = User.objects.create_user(username="helper3c", password="testpass123!")

        ContactUnlock.objects.create(federated_access=federated_access, helper=helper1)
        ContactUnlock.objects.create(federated_access=federated_access, helper=helper2)
        ContactUnlock.objects.create(federated_access=federated_access, helper=helper3)

        # At the limit of 3, should not be able to unlock more
        assert ContactUnlock.can_unlock(federated_access) is False

    def test_can_unlock_after_window_expires(self):
        """Unlocks older than 30 days should not be counted toward the limit."""
        club = FederatedClub.objects.create(
            name="Test Club",
            short_code="TST4",
            base_url="https://example.com",
            api_key="test_api_key_12345",
            is_active=True,
            is_approved=True,
        )
        federated_access = FederatedAidAccess.objects.create(
            source_club=club,
            external_user_id="ext_user_004",
            external_display_name="External User",
            access_level="contact",
        )

        # Create 3 helpers
        helper1 = User.objects.create_user(username="helper4a", password="testpass123!")
        helper2 = User.objects.create_user(username="helper4b", password="testpass123!")
        helper3 = User.objects.create_user(username="helper4c", password="testpass123!")

        # Create unlocks with old timestamps (31 days ago)
        old_time = timezone.now() - timedelta(days=31)

        unlock1 = ContactUnlock.objects.create(
            federated_access=federated_access, helper=helper1
        )
        unlock2 = ContactUnlock.objects.create(
            federated_access=federated_access, helper=helper2
        )
        unlock3 = ContactUnlock.objects.create(
            federated_access=federated_access, helper=helper3
        )

        # Manually update the unlocked_at timestamps to be outside the window
        ContactUnlock.objects.filter(
            pk__in=[unlock1.pk, unlock2.pk, unlock3.pk]
        ).update(unlocked_at=old_time)

        # Old unlocks should not count, so new unlock should be allowed
        assert ContactUnlock.can_unlock(federated_access) is True


# ---------------------------------------------------------------------------
# Federated Access Tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestFederatedAidAccess:
    """Tests for FederatedAidAccess model."""

    def test_federated_access_creation(self):
        """Successfully create a FederatedAidAccess record."""
        club = FederatedClub.objects.create(
            name="Test Club",
            short_code="TST5",
            base_url="https://example.com",
            api_key="test_api_key_12345",
            is_active=True,
            is_approved=True,
        )
        approver = User.objects.create_user(
            username="approver", password="testpass123!"
        )

        access = FederatedAidAccess.objects.create(
            source_club=club,
            external_user_id="ext_user_005",
            external_display_name="John Doe",
            access_level="contact",
            is_active=True,
            approved_by=approver,
        )

        assert access.pk is not None
        assert access.source_club == club
        assert access.external_user_id == "ext_user_005"
        assert access.external_display_name == "John Doe"
        assert access.access_level == "contact"
        assert access.is_active is True
        assert access.approved_by == approver
        assert access.contacts_unlocked == 0
        assert access.expires_at is None

    def test_federated_access_unique_constraint(self):
        """Duplicate (source_club, external_user_id) should raise IntegrityError."""
        club = FederatedClub.objects.create(
            name="Test Club",
            short_code="TST6",
            base_url="https://example.com",
            api_key="test_api_key_12345",
            is_active=True,
            is_approved=True,
        )

        FederatedAidAccess.objects.create(
            source_club=club,
            external_user_id="ext_user_006",
            external_display_name="User One",
        )

        with pytest.raises(IntegrityError):
            FederatedAidAccess.objects.create(
                source_club=club,
                external_user_id="ext_user_006",
                external_display_name="User Two",
            )

    def test_federated_access_expiry(self):
        """Access with past expires_at should be stored correctly."""
        club = FederatedClub.objects.create(
            name="Test Club",
            short_code="TST7",
            base_url="https://example.com",
            api_key="test_api_key_12345",
            is_active=True,
            is_approved=True,
        )

        past_time = timezone.now() - timedelta(days=1)

        access = FederatedAidAccess.objects.create(
            source_club=club,
            external_user_id="ext_user_007",
            external_display_name="Expired User",
            expires_at=past_time,
        )

        assert access.expires_at is not None
        assert access.expires_at < timezone.now()


# ---------------------------------------------------------------------------
# Privacy Settings Tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAidPrivacySettings:
    """Tests for AidPrivacySettings model."""

    def test_privacy_defaults_all_false(self):
        """All show_* fields should default to False."""
        user = User.objects.create_user(
            username="privacyuser", password="testpass123!"
        )
        privacy = AidPrivacySettings.objects.create(user=user)

        assert privacy.show_phone_on_aid is False
        assert privacy.show_mobile_on_aid is False
        assert privacy.show_whatsapp_on_aid is False
        assert privacy.show_email_on_aid is False
        assert privacy.show_exact_location is False
        assert privacy.show_photo_on_aid is False
        assert privacy.show_bio_on_aid is False
        assert privacy.show_hours_on_aid is False

    def test_privacy_one_to_one_with_user(self):
        """Each user can have at most one privacy settings record."""
        user = User.objects.create_user(
            username="onetooneuser", password="testpass123!"
        )
        AidPrivacySettings.objects.create(user=user)

        with pytest.raises(IntegrityError):
            AidPrivacySettings.objects.create(user=user)
