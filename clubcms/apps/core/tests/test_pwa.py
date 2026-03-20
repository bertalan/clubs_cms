"""
T16 + T17 — Test PWA manifest, service worker, offline, push subscription.
"""

import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.notifications.models import PushSubscription

User = get_user_model()


class TestPWAManifest(TestCase):
    """GET /manifest.json must return valid PWA manifest."""

    def test_manifest_returns_200(self):
        resp = self.client.get("/manifest.json")
        self.assertEqual(resp.status_code, 200)

    def test_manifest_is_json(self):
        resp = self.client.get("/manifest.json")
        self.assertEqual(resp["Content-Type"], "application/json")

    def test_manifest_has_required_fields(self):
        resp = self.client.get("/manifest.json")
        data = json.loads(resp.content)
        self.assertIn("name", data)
        self.assertIn("short_name", data)
        self.assertIn("start_url", data)
        self.assertIn("display", data)
        self.assertEqual(data["display"], "standalone")
        self.assertEqual(data["start_url"], "/")

    def test_manifest_has_theme_color(self):
        resp = self.client.get("/manifest.json")
        data = json.loads(resp.content)
        self.assertIn("theme_color", data)
        self.assertTrue(data["theme_color"].startswith("#"))

    def test_manifest_has_icons_list(self):
        resp = self.client.get("/manifest.json")
        data = json.loads(resp.content)
        self.assertIn("icons", data)
        self.assertIsInstance(data["icons"], list)

    def test_manifest_has_scope(self):
        resp = self.client.get("/manifest.json")
        data = json.loads(resp.content)
        self.assertEqual(data.get("scope"), "/")

    def test_manifest_has_orientation(self):
        resp = self.client.get("/manifest.json")
        data = json.loads(resp.content)
        self.assertEqual(data.get("orientation"), "portrait-primary")

    def test_manifest_has_lang(self):
        resp = self.client.get("/manifest.json")
        data = json.loads(resp.content)
        self.assertIn("lang", data)

    def test_manifest_has_categories(self):
        resp = self.client.get("/manifest.json")
        data = json.loads(resp.content)
        self.assertIn("categories", data)
        self.assertIsInstance(data["categories"], list)


class TestPWAServiceWorker(TestCase):
    """GET /sw.js must return valid service worker JavaScript."""

    def test_sw_returns_200(self):
        resp = self.client.get("/sw.js")
        self.assertEqual(resp.status_code, 200)

    def test_sw_content_type(self):
        resp = self.client.get("/sw.js")
        self.assertEqual(resp["Content-Type"], "application/javascript")

    def test_sw_contains_install_handler(self):
        resp = self.client.get("/sw.js")
        content = resp.content.decode()
        self.assertIn("addEventListener('install'", content)

    def test_sw_contains_fetch_handler(self):
        resp = self.client.get("/sw.js")
        content = resp.content.decode()
        self.assertIn("addEventListener('fetch'", content)

    def test_sw_contains_activate_handler(self):
        resp = self.client.get("/sw.js")
        content = resp.content.decode()
        self.assertIn("addEventListener('activate'", content)

    def test_sw_references_offline_url(self):
        resp = self.client.get("/sw.js")
        content = resp.content.decode()
        self.assertIn("/offline/", content)

    def test_sw_contains_push_handler(self):
        resp = self.client.get("/sw.js")
        content = resp.content.decode()
        self.assertIn("addEventListener('push'", content)

    def test_sw_contains_notificationclick_handler(self):
        resp = self.client.get("/sw.js")
        content = resp.content.decode()
        self.assertIn("addEventListener('notificationclick'", content)

    def test_sw_push_shows_notification(self):
        resp = self.client.get("/sw.js")
        content = resp.content.decode()
        self.assertIn("showNotification", content)

    def test_sw_notificationclick_opens_window(self):
        resp = self.client.get("/sw.js")
        content = resp.content.decode()
        self.assertIn("openWindow", content)


class TestPWAOfflinePage(TestCase):
    """GET /offline/ must return fallback page."""

    def test_offline_returns_200(self):
        resp = self.client.get("/offline/")
        self.assertEqual(resp.status_code, 200)

    def test_offline_contains_retry_button(self):
        resp = self.client.get("/offline/")
        content = resp.content.decode()
        self.assertIn("reload()", content)


# ---------------------------------------------------------------------------
# T17 — Push Subscription endpoints
# ---------------------------------------------------------------------------

VALID_SUB = {
    "endpoint": "https://fcm.googleapis.com/fcm/send/abc123",
    "keys": {
        "p256dh": "BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA_0QTpQtUbVlUls0VJXg7A8u-Ts1XbjhazAkj7I99e8p8REfXSo",
        "auth": "tBHItJI5svbpC7-fGlkSog",
    },
}


class TestPushSubscribeAuth(TestCase):
    """Push subscribe requires login."""

    def test_anonymous_gets_redirect(self):
        resp = self.client.post(
            reverse("notifications:push_subscribe"),
            data=json.dumps(VALID_SUB),
            content_type="application/json",
        )
        self.assertIn(resp.status_code, (302, 403))

    def test_anonymous_unsubscribe_gets_redirect(self):
        resp = self.client.post(
            reverse("notifications:push_unsubscribe"),
            data=json.dumps({"endpoint": "https://example.com/push"}),
            content_type="application/json",
        )
        self.assertIn(resp.status_code, (302, 403))


class TestPushSubscribe(TestCase):
    """POST /notifications/push/subscribe/ creates PushSubscription."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="pushuser", password="testpass123"
        )
        self.client.login(username="pushuser", password="testpass123")
        self.url = reverse("notifications:push_subscribe")

    def test_valid_subscribe_creates_record(self):
        resp = self.client.post(
            self.url,
            data=json.dumps(VALID_SUB),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["ok"])
        self.assertTrue(data["created"])
        self.assertEqual(PushSubscription.objects.filter(user=self.user).count(), 1)

    def test_duplicate_endpoint_updates_instead_of_creating(self):
        self.client.post(
            self.url,
            data=json.dumps(VALID_SUB),
            content_type="application/json",
        )
        # Second call with same endpoint
        resp = self.client.post(
            self.url,
            data=json.dumps(VALID_SUB),
            content_type="application/json",
        )
        data = resp.json()
        self.assertTrue(data["ok"])
        self.assertFalse(data["created"])
        self.assertEqual(PushSubscription.objects.filter(user=self.user).count(), 1)

    def test_invalid_json_returns_400(self):
        resp = self.client.post(
            self.url,
            data="not json",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_missing_endpoint_returns_400(self):
        resp = self.client.post(
            self.url,
            data=json.dumps({"keys": VALID_SUB["keys"]}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_http_endpoint_rejected(self):
        bad = {**VALID_SUB, "endpoint": "http://insecure.com/push"}
        resp = self.client.post(
            self.url,
            data=json.dumps(bad),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_missing_keys_returns_400(self):
        resp = self.client.post(
            self.url,
            data=json.dumps({"endpoint": VALID_SUB["endpoint"], "keys": {}}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_subscription_stores_user_agent(self):
        self.client.post(
            self.url,
            data=json.dumps(VALID_SUB),
            content_type="application/json",
            HTTP_USER_AGENT="TestBrowser/1.0",
        )
        sub = PushSubscription.objects.get(user=self.user)
        self.assertEqual(sub.user_agent, "TestBrowser/1.0")


class TestPushUnsubscribe(TestCase):
    """POST /notifications/push/unsubscribe/ removes PushSubscription."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="pushuser2", password="testpass123"
        )
        self.client.login(username="pushuser2", password="testpass123")
        self.url = reverse("notifications:push_unsubscribe")
        PushSubscription.objects.create(
            user=self.user,
            endpoint=VALID_SUB["endpoint"],
            p256dh_key=VALID_SUB["keys"]["p256dh"],
            auth_key=VALID_SUB["keys"]["auth"],
        )

    def test_unsubscribe_deletes_record(self):
        resp = self.client.post(
            self.url,
            data=json.dumps({"endpoint": VALID_SUB["endpoint"]}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["deleted"], 1)
        self.assertEqual(PushSubscription.objects.filter(user=self.user).count(), 0)

    def test_unsubscribe_nonexistent_returns_zero(self):
        resp = self.client.post(
            self.url,
            data=json.dumps({"endpoint": "https://other.example.com/push"}),
            content_type="application/json",
        )
        data = resp.json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["deleted"], 0)

    def test_unsubscribe_missing_endpoint_returns_400(self):
        resp = self.client.post(
            self.url,
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_user_cannot_delete_other_users_subscription(self):
        other = User.objects.create_user(
            username="otheruser", password="testpass123"
        )
        PushSubscription.objects.create(
            user=other,
            endpoint="https://fcm.googleapis.com/fcm/send/other",
            p256dh_key="key",
            auth_key="auth",
        )
        # Try to delete other user's subscription
        resp = self.client.post(
            self.url,
            data=json.dumps({"endpoint": "https://fcm.googleapis.com/fcm/send/other"}),
            content_type="application/json",
        )
        data = resp.json()
        self.assertEqual(data["deleted"], 0)
        # Other user's sub still exists
        self.assertTrue(
            PushSubscription.objects.filter(user=other).exists()
        )
