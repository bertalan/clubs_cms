/**
 * Geo-search: browser geolocation + Nominatim reverse geocoding.
 *
 * Provides "Near me" button to detect user's position and populate
 * hidden lat/lng fields in the search form, then auto-submit.
 */
(function () {
  'use strict';

  var form       = document.getElementById('search-form');
  var locateBtn  = document.getElementById('geo-locate-btn');
  var clearBtn   = document.getElementById('geo-clear-btn');
  var controls   = document.getElementById('geo-controls');
  var status     = document.getElementById('geo-status');
  var latInput   = document.getElementById('geo-lat');
  var lngInput   = document.getElementById('geo-lng');

  if (!form || !locateBtn) return;

  // ── "Near me" button click ──────────────────────────────────────
  locateBtn.addEventListener('click', function () {
    if (!navigator.geolocation) {
      status.textContent = 'Geolocation not supported';
      return;
    }

    status.textContent = '⏳ Detecting location…';
    locateBtn.disabled = true;

    navigator.geolocation.getCurrentPosition(
      function onSuccess(pos) {
        latInput.value = pos.coords.latitude.toFixed(6);
        lngInput.value = pos.coords.longitude.toFixed(6);

        // Show controls
        controls.classList.remove('search-geo__controls--hidden');
        locateBtn.classList.add('search-geo__btn--active');

        // Reverse geocode for friendly name (Nominatim)
        reverseGeocode(pos.coords.latitude, pos.coords.longitude);

        // Auto-submit
        form.submit();
      },
      function onError(err) {
        locateBtn.disabled = false;
        if (err.code === err.PERMISSION_DENIED) {
          status.textContent = '⚠ Location access denied';
        } else {
          status.textContent = '⚠ Could not detect location';
        }
      },
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 }
    );
  });

  // ── Clear location ──────────────────────────────────────────────
  if (clearBtn) {
    clearBtn.addEventListener('click', function () {
      latInput.value = '';
      lngInput.value = '';
      controls.classList.add('search-geo__controls--hidden');
      locateBtn.classList.remove('search-geo__btn--active');
      status.textContent = '';
      form.submit();
    });
  }

  // ── Radius chip change → auto-submit ────────────────────────────
  var radioBtns = document.querySelectorAll('input[name="radius"]');
  radioBtns.forEach(function (radio) {
    radio.addEventListener('change', function () {
      if (latInput.value && lngInput.value) {
        form.submit();
      }
    });
  });

  // ── Nominatim reverse geocode (best-effort, no API key) ─────────
  function reverseGeocode(lat, lng) {
    var url = 'https://nominatim.openstreetmap.org/reverse?format=json&lat=' +
              lat + '&lon=' + lng + '&zoom=12&addressdetails=1';

    fetch(url, { headers: { 'Accept-Language': document.documentElement.lang || 'en' } })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data && data.address) {
          var place = data.address.city || data.address.town || data.address.village || data.address.county || '';
          if (place) {
            status.textContent = '📍 ' + place;
          }
        }
      })
      .catch(function () { /* silent fail */ });
  }
})();
