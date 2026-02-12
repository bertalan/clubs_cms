/**
 * Push Subscription Manager for ClubCMS.
 *
 * Handles:
 *  - Requesting notification permission
 *  - Subscribing to the push service with VAPID public key
 *  - Sending subscription to server
 *  - Unsubscribing
 *
 * Usage:
 *   <script src="{% static 'js/push-manager.js' %}"></script>
 *   <script>
 *     PushManager.init({
 *       vapidPublicKey: "{{ WEBPUSH_SETTINGS.VAPID_PUBLIC_KEY }}",
 *       subscribeUrl: "/notifications/push/subscribe/",
 *       unsubscribeUrl: "/notifications/push/unsubscribe/",
 *       csrfToken: "{{ csrf_token }}",
 *     });
 *   </script>
 */

(function (global) {
  "use strict";

  const ClubPushManager = {
    config: {
      vapidPublicKey: "",
      subscribeUrl: "/notifications/push/subscribe/",
      unsubscribeUrl: "/notifications/push/unsubscribe/",
      csrfToken: "",
      serviceWorkerUrl: "/static/js/service-worker.js",
    },

    /**
     * Initialise with options.
     */
    init: function (options) {
      Object.assign(this.config, options || {});
    },

    /**
     * Convert a base64 VAPID key to a Uint8Array for the subscribe call.
     */
    _urlBase64ToUint8Array: function (base64String) {
      const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
      const base64 = (base64String + padding)
        .replace(/-/g, "+")
        .replace(/_/g, "/");
      const rawData = atob(base64);
      const outputArray = new Uint8Array(rawData.length);
      for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
      }
      return outputArray;
    },

    /**
     * Check if push notifications are supported.
     */
    isSupported: function () {
      return (
        "serviceWorker" in navigator &&
        "PushManager" in window &&
        "Notification" in window
      );
    },

    /**
     * Request notification permission from the user.
     * Returns a Promise resolving to the permission state.
     */
    requestPermission: async function () {
      if (!this.isSupported()) {
        console.warn("Push notifications are not supported in this browser.");
        return "denied";
      }
      const permission = await Notification.requestPermission();
      return permission;
    },

    /**
     * Subscribe to push notifications.
     * Returns the PushSubscription on success, null on failure.
     */
    subscribe: async function () {
      if (!this.isSupported()) {
        console.warn("Push not supported.");
        return null;
      }

      const permission = await this.requestPermission();
      if (permission !== "granted") {
        console.warn("Notification permission denied.");
        return null;
      }

      try {
        const registration = await navigator.serviceWorker.ready;
        const applicationServerKey = this._urlBase64ToUint8Array(
          this.config.vapidPublicKey
        );

        const subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: applicationServerKey,
        });

        // Send subscription to server
        await this._sendToServer(subscription);

        return subscription;
      } catch (err) {
        console.error("Failed to subscribe to push:", err);
        return null;
      }
    },

    /**
     * Send subscription data to the server.
     */
    _sendToServer: async function (subscription) {
      const subJSON = subscription.toJSON();
      const body = {
        endpoint: subJSON.endpoint,
        keys: {
          p256dh: subJSON.keys.p256dh,
          auth: subJSON.keys.auth,
        },
      };

      const response = await fetch(this.config.subscribeUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.config.csrfToken,
        },
        body: JSON.stringify(body),
        credentials: "same-origin",
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error || "Server rejected subscription");
      }

      return response.json();
    },

    /**
     * Unsubscribe from push notifications.
     */
    unsubscribe: async function () {
      if (!this.isSupported()) return false;

      try {
        const registration = await navigator.serviceWorker.ready;
        const subscription =
          await registration.pushManager.getSubscription();

        if (!subscription) {
          console.warn("No active push subscription found.");
          return false;
        }

        // Notify server
        await fetch(this.config.unsubscribeUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": this.config.csrfToken,
          },
          body: JSON.stringify({ endpoint: subscription.endpoint }),
          credentials: "same-origin",
        });

        // Unsubscribe from push service
        await subscription.unsubscribe();

        return true;
      } catch (err) {
        console.error("Failed to unsubscribe:", err);
        return false;
      }
    },

    /**
     * Get the current subscription state.
     * Returns the PushSubscription or null.
     */
    getSubscription: async function () {
      if (!this.isSupported()) return null;
      try {
        const registration = await navigator.serviceWorker.ready;
        return registration.pushManager.getSubscription();
      } catch (err) {
        return null;
      }
    },
  };

  // Export
  global.ClubPushManager = ClubPushManager;
})(typeof window !== "undefined" ? window : this);
