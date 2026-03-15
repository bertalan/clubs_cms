/**
 * Aid Map — Leaflet map with helpers markers + Nominatim geo-search.
 *
 * Reads data from the helpers API endpoint and renders markers.
 * Provides address autocomplete and browser geolocation for the search form.
 */
(function () {
  'use strict';

  var NOMINATIM_SEARCH = 'https://nominatim.openstreetmap.org/search';
  var NOMINATIM_REVERSE = 'https://nominatim.openstreetmap.org/reverse';
  var DEBOUNCE_MS = 400;
  var MIN_QUERY_LEN = 3;

  var mapContainer = document.getElementById('aid-map');
  if (!mapContainer || typeof L === 'undefined') return;

  /**
   * Parse a coordinate string that might use comma as decimal separator
   * (Italian/European locale).  "45,6395418" → 45.6395418
   */
  function parseCoord(s) {
    if (!s) return null;
    var v = s.trim().replace(',', '.');
    var n = parseFloat(v);
    return isNaN(n) ? null : n;
  }

  var apiUrl = mapContainer.dataset.apiUrl;
  var searchLat = parseCoord(mapContainer.dataset.searchLat);
  var searchLng = parseCoord(mapContainer.dataset.searchLng);
  var searchRadius = parseInt(mapContainer.dataset.searchRadius, 10) || 50;
  var lang = document.documentElement.lang || 'it';

  // Form elements
  var form = document.getElementById('aid-search-form');
  var locationInput = document.getElementById('aid-search-location');
  var latInput = document.getElementById('aid-search-lat');
  var lngInput = document.getElementById('aid-search-lng');
  var locateBtn = document.getElementById('aid-locate-btn');
  var statusEl = document.getElementById('aid-search-status');
  var suggestionsEl = document.getElementById('aid-search-suggestions');
  var radiusSelect = document.getElementById('aid-search-radius');

  // Normalize existing hidden field values (fix comma-as-decimal from URL)
  if (latInput && latInput.value) latInput.value = latInput.value.replace(',', '.');
  if (lngInput && lngInput.value) lngInput.value = lngInput.value.replace(',', '.');

  // ── Leaflet Map ─────────────────────────────────────────────
  var defaultCenter = [44.5, 11.0]; // Italy center
  var defaultZoom = 6;
  var center = (searchLat && searchLng) ? [searchLat, searchLng] : defaultCenter;
  var zoom = (searchLat && searchLng) ? 10 : defaultZoom;

  var map = L.map(mapContainer, { center: center, zoom: zoom, scrollWheelZoom: true });

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 19,
  }).addTo(map);

  var markersGroup = L.featureGroup().addTo(map);

  // Search radius circle
  var searchCircle = null;
  if (searchLat && searchLng) {
    searchCircle = L.circle([searchLat, searchLng], {
      radius: searchRadius * 1000,
      color: 'var(--color-primary, #1a73e8)',
      fillColor: 'var(--color-primary, #1a73e8)',
      fillOpacity: 0.08,
      weight: 1,
      dashArray: '6 4',
    }).addTo(map);

    // User position marker
    L.circleMarker([searchLat, searchLng], {
      radius: 8,
      color: '#e53935',
      fillColor: '#e53935',
      fillOpacity: 0.9,
      weight: 2,
    }).addTo(map).bindPopup('<b>' + (locationInput ? locationInput.value || 'You' : 'You') + '</b>');
  }

  // ── Load helpers from API ───────────────────────────────────
  function loadHelpers() {
    var url = apiUrl;
    var params = [];
    if (searchLat && searchLng) {
      params.push('lat=' + searchLat, 'lng=' + searchLng, 'radius=' + searchRadius);
    }
    if (params.length) url += '?' + params.join('&');

    fetch(url, { credentials: 'same-origin' })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        renderMarkers(data.helpers || [], 'local');
        renderMarkers(data.federated_helpers || [], 'federated');

        // Fit bounds if we have markers and no geo search
        if (!searchLat && !searchLng && markersGroup.getLayers().length > 0) {
          map.fitBounds(markersGroup.getBounds().pad(0.1));
        }
      })
      .catch(function (err) {
        console.error('Failed to load helpers:', err);
      });
  }

  function renderMarkers(helpers, type) {
    var color = type === 'federated' ? '#f57c00' : '#1565c0';

    helpers.forEach(function (h) {
      var lat = h.lat || h.latitude;
      var lon = h.lon || h.longitude;
      if (!lat || !lon) return;

      var marker = L.circleMarker([lat, lon], {
        radius: 7,
        color: color,
        fillColor: color,
        fillOpacity: 0.7,
        weight: 2,
      });

      var popup = '<div class="aid-popup">';
      popup += '<b class="aid-popup__name">' + escapeHtml(h.display_name) + '</b>';
      popup += '<div class="aid-popup__meta">' + escapeHtml(h.city || '');
      if (h.radius_km) popup += ' &middot; ' + h.radius_km + ' km';
      if (h.distance_km != null) popup += ' &middot; <strong>' + h.distance_km + ' km</strong>';
      popup += '</div>';
      if (h.notes) popup += '<div class="aid-popup__notes">' + escapeHtml(h.notes).substring(0, 80) + '</div>';
      if (type === 'federated' && h.source_club) {
        popup += '<div class="aid-popup__badge">' + escapeHtml(h.source_club) + '</div>';
      }
      popup += '<div class="aid-popup__actions">';
      if (type === 'local' && h.id) {
        popup += '<a href="helper/' + h.id + '/" class="aid-popup__link">' + gettext('Details') + '</a>';
        popup += '<a href="helper/' + h.id + '/contact/" class="aid-popup__link aid-popup__link--primary">' + gettext('Request Help') + '</a>';
      }
      popup += '</div></div>';

      marker.bindPopup(popup);
      markersGroup.addLayer(marker);
    });
  }

  loadHelpers();

  // ── Nominatim Address Autocomplete ──────────────────────────
  var debounceTimer = null;

  function setSuggestionsVisible(visible) {
    suggestionsEl.hidden = !visible;
    if (locationInput) {
      locationInput.setAttribute('aria-expanded', visible ? 'true' : 'false');
    }
  }

  if (locationInput) {
    locationInput.addEventListener('input', function () {
      clearTimeout(debounceTimer);
      var q = locationInput.value.trim();
      if (q.length < MIN_QUERY_LEN) {
        setSuggestionsVisible(false);
        return;
      }
      debounceTimer = setTimeout(function () { searchNominatim(q); }, DEBOUNCE_MS);
    });

    locationInput.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') setSuggestionsVisible(false);
      if (e.key === 'ArrowDown' && !suggestionsEl.hidden) {
        e.preventDefault();
        var first = suggestionsEl.querySelector('li');
        if (first) first.focus();
      }
    });

    document.addEventListener('click', function (e) {
      if (!e.target.closest('.aid-search')) setSuggestionsVisible(false);
    });
  }

  function searchNominatim(query) {
    var url = NOMINATIM_SEARCH + '?format=json&limit=5&addressdetails=1&q=' +
              encodeURIComponent(query);

    fetch(url, { headers: { 'Accept-Language': lang } })
      .then(function (r) { return r.json(); })
      .then(function (results) {
        suggestionsEl.innerHTML = '';
        if (!results.length) { setSuggestionsVisible(false); return; }

        results.forEach(function (item) {
          var li = document.createElement('li');
          li.className = 'aid-search__suggestion';
          li.textContent = item.display_name;
          li.setAttribute('role', 'option');
          li.setAttribute('tabindex', '0');

          function select() {
            latInput.value = item.lat;
            lngInput.value = item.lon;
            locationInput.value = item.display_name;
            setSuggestionsVisible(false);
            form.submit();
          }

          li.addEventListener('click', select);
          li.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') { e.preventDefault(); select(); }
            if (e.key === 'ArrowDown' && li.nextElementSibling) { e.preventDefault(); li.nextElementSibling.focus(); }
            if (e.key === 'ArrowUp') { e.preventDefault(); li.previousElementSibling ? li.previousElementSibling.focus() : locationInput.focus(); }
            if (e.key === 'Escape') { setSuggestionsVisible(false); locationInput.focus(); }
          });

          suggestionsEl.appendChild(li);
        });
        setSuggestionsVisible(true);
      })
      .catch(function () { setSuggestionsVisible(false); });
  }

  // ── Browser Geolocation ─────────────────────────────────────
  if (locateBtn) {
    locateBtn.addEventListener('click', function () {
      if (!navigator.geolocation) {
        statusEl.textContent = gettext('Geolocation not supported');
        return;
      }

      statusEl.textContent = gettext('Detecting position…');
      locateBtn.disabled = true;

      navigator.geolocation.getCurrentPosition(
        function (pos) {
          locateBtn.disabled = false;
          latInput.value = pos.coords.latitude.toFixed(6);
          lngInput.value = pos.coords.longitude.toFixed(6);
          statusEl.textContent = '';

          // Reverse geocode for location name
          var revUrl = NOMINATIM_REVERSE + '?format=json&lat=' + pos.coords.latitude +
                       '&lon=' + pos.coords.longitude + '&zoom=12&addressdetails=1';
          fetch(revUrl, { headers: { 'Accept-Language': lang } })
            .then(function (r) { return r.json(); })
            .then(function (data) {
              if (data && data.address) {
                var place = data.address.city || data.address.town ||
                            data.address.village || data.address.county || '';
                if (place) locationInput.value = place;
              }
              form.submit();
            })
            .catch(function () { form.submit(); });
        },
        function (err) {
          locateBtn.disabled = false;
          statusEl.textContent = err.code === err.PERMISSION_DENIED
            ? gettext('Location access denied')
            : gettext('Could not detect position');
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
      );
    });
  }

  // ── Radius change auto-submit ───────────────────────────────
  if (radiusSelect) {
    radiusSelect.addEventListener('change', function () {
      if (latInput.value && lngInput.value) {
        form.submit();
      } else if (locationInput.value.trim().length >= MIN_QUERY_LEN) {
        geocodeAndSubmit(locationInput.value.trim());
      }
    });
  }

  // ── Form submit: geocode if location text but no coords ────
  if (form) {
    form.addEventListener('submit', function (e) {
      // Always normalise comma → dot before any submit
      if (latInput.value) latInput.value = latInput.value.replace(',', '.');
      if (lngInput.value) lngInput.value = lngInput.value.replace(',', '.');

      if (latInput.value && lngInput.value) return; // coords present, submit normally
      var q = locationInput.value.trim();
      if (q.length < MIN_QUERY_LEN) return; // no query, submit normally (shows all)

      e.preventDefault();
      geocodeAndSubmit(q);
    });
  }

  /**
   * Forward-geocode a query string, populate lat/lng, then submit.
   */
  function geocodeAndSubmit(query) {
    statusEl.textContent = gettext('Searching…');
    var url = NOMINATIM_SEARCH + '?format=json&limit=1&q=' + encodeURIComponent(query);

    fetch(url, { headers: { 'Accept-Language': lang } })
      .then(function (r) { return r.json(); })
      .then(function (results) {
        statusEl.textContent = '';
        if (results.length) {
          latInput.value = results[0].lat;
          lngInput.value = results[0].lon;
          locationInput.value = results[0].display_name;
        }
        form.submit();
      })
      .catch(function () {
        statusEl.textContent = '';
        form.submit();
      });
  }

  // ── Helpers ─────────────────────────────────────────────────
  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function gettext(s) {
    return (typeof window.gettext === 'function') ? window.gettext(s) : s;
  }
})();
