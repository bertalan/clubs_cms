/**
 * Geocoder Widget — Assisted geocoding with Leaflet map picker.
 *
 * Provides:
 * - Address search via Nominatim (OpenStreetMap, no API key)
 * - Interactive Leaflet map with draggable marker
 * - "Use my position" browser geolocation button
 * - Manual lat/lng input fields
 * - Auto-populates a hidden coordinates field and optional city field
 *
 * Usage:
 *   Attach to any element with [data-geocoder-widget]:
 *     <div data-geocoder-widget
 *          data-target-coordinates="#id_aid_coordinates"
 *          data-target-city="#id_aid_location_city"
 *          data-initial-lat="45.4642"
 *          data-initial-lng="9.1900">
 *     </div>
 *
 *   Requires Leaflet CSS+JS loaded before this script.
 */
(function () {
  'use strict';

  var NOMINATIM_SEARCH = 'https://nominatim.openstreetmap.org/search';
  var NOMINATIM_REVERSE = 'https://nominatim.openstreetmap.org/reverse';
  var DEFAULT_LAT = 45.4642;
  var DEFAULT_LNG = 9.1900;
  var DEFAULT_ZOOM = 6;
  var MARKER_ZOOM = 14;
  var DEBOUNCE_MS = 400;
  var MIN_QUERY_LEN = 3;

  var lang = document.documentElement.lang || 'it';

  document.querySelectorAll('[data-geocoder-widget]').forEach(initWidget);

  /* Allow dynamic re-initialization for admin bridge */
  window._initGeocoderWidgets = function () {
    document.querySelectorAll('[data-geocoder-widget]:not([data-geocoder-ready])').forEach(initWidget);
  };
  document.addEventListener('geocoder:init', window._initGeocoderWidgets);

  function initWidget(container) {
    container.setAttribute('data-geocoder-ready', '1');
    // Resolve target fields
    var coordsSelector = container.dataset.targetCoordinates;
    var citySelector = container.dataset.targetCity;
    var coordsInput = coordsSelector ? document.querySelector(coordsSelector) : null;
    var cityInput = citySelector ? document.querySelector(citySelector) : null;

    // Parse initial coordinates
    var initialLat = parseFloat(container.dataset.initialLat) || null;
    var initialLng = parseFloat(container.dataset.initialLng) || null;
    var hasInitial = initialLat !== null && initialLng !== null
                     && !isNaN(initialLat) && !isNaN(initialLng);

    // ── Build DOM ──────────────────────────────────────────────────
    container.innerHTML = '';
    container.classList.add('geocoder');

    // Search row
    var searchRow = el('div', 'geocoder__search-row');
    var searchInput = el('input', 'geocoder__search-input form-input');
    searchInput.type = 'text';
    searchInput.placeholder = container.dataset.searchPlaceholder || gettext('Search address…');
    searchInput.setAttribute('autocomplete', 'off');
    searchInput.setAttribute('aria-label', gettext('Search address'));

    var locateBtn = el('button', 'geocoder__locate-btn btn btn-secondary');
    locateBtn.type = 'button';
    locateBtn.setAttribute('aria-label', gettext('Use my position'));
    locateBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v4m0 12v4m10-10h-4M6 12H2"/></svg>';

    searchRow.appendChild(searchInput);
    searchRow.appendChild(locateBtn);
    container.appendChild(searchRow);

    // Suggestions dropdown
    var suggestions = el('ul', 'geocoder__suggestions');
    suggestions.setAttribute('role', 'listbox');
    suggestions.hidden = true;
    container.appendChild(suggestions);

    // Status message
    var statusEl = el('div', 'geocoder__status');
    statusEl.setAttribute('aria-live', 'polite');
    container.appendChild(statusEl);

    // Map container
    var mapDiv = el('div', 'geocoder__map');
    container.appendChild(mapDiv);

    // Manual coordinate row
    var manualRow = el('div', 'geocoder__manual-row');
    var latField = createManualField('lat', gettext('Latitude'), initialLat);
    var lngField = createManualField('lng', gettext('Longitude'), initialLng);
    manualRow.appendChild(latField.wrap);
    manualRow.appendChild(lngField.wrap);
    container.appendChild(manualRow);

    // Manual toggle link
    var manualToggle = el('button', 'geocoder__manual-toggle');
    manualToggle.type = 'button';
    manualToggle.textContent = gettext('Enter coordinates manually');
    manualToggle.setAttribute('aria-expanded', 'false');
    container.insertBefore(manualToggle, manualRow);
    manualRow.hidden = true;

    // ── Leaflet map ────────────────────────────────────────────────
    var startLat = hasInitial ? initialLat : DEFAULT_LAT;
    var startLng = hasInitial ? initialLng : DEFAULT_LNG;
    var startZoom = hasInitial ? MARKER_ZOOM : DEFAULT_ZOOM;

    var map = L.map(mapDiv, {
      center: [startLat, startLng],
      zoom: startZoom,
      scrollWheelZoom: true,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(map);

    var marker = null;
    if (hasInitial) {
      marker = L.marker([initialLat, initialLng], { draggable: true }).addTo(map);
      bindMarkerDrag(marker);
    }

    // Fix Leaflet size when tab/accordion reveals container
    setTimeout(function () { map.invalidateSize(); }, 200);

    // ── Map click → place marker ───────────────────────────────────
    map.on('click', function (e) {
      setPosition(e.latlng.lat, e.latlng.lng, true);
    });

    // ── Address search (Nominatim) ─────────────────────────────────
    var debounceTimer = null;
    searchInput.addEventListener('input', function () {
      clearTimeout(debounceTimer);
      var q = searchInput.value.trim();
      if (q.length < MIN_QUERY_LEN) {
        suggestions.hidden = true;
        return;
      }
      debounceTimer = setTimeout(function () { searchNominatim(q); }, DEBOUNCE_MS);
    });

    searchInput.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        suggestions.hidden = true;
      }
      if (e.key === 'ArrowDown' && !suggestions.hidden) {
        e.preventDefault();
        var first = suggestions.querySelector('li');
        if (first) first.focus();
      }
    });

    // Close suggestions on click outside
    document.addEventListener('click', function (e) {
      if (!container.contains(e.target)) {
        suggestions.hidden = true;
      }
    });

    function searchNominatim(query) {
      var url = NOMINATIM_SEARCH + '?format=json&limit=5&addressdetails=1&q=' +
                encodeURIComponent(query);

      fetch(url, { headers: { 'Accept-Language': lang } })
        .then(function (r) { return r.json(); })
        .then(function (results) {
          suggestions.innerHTML = '';
          if (!results.length) {
            suggestions.hidden = true;
            return;
          }
          results.forEach(function (item) {
            var li = el('li', 'geocoder__suggestion');
            li.textContent = item.display_name;
            li.setAttribute('role', 'option');
            li.setAttribute('tabindex', '0');

            function select() {
              var lat = parseFloat(item.lat);
              var lng = parseFloat(item.lon);
              setPosition(lat, lng, true);
              searchInput.value = item.display_name;
              suggestions.hidden = true;

              // Extract city from address details
              if (cityInput && item.address) {
                var city = item.address.city || item.address.town ||
                           item.address.village || item.address.municipality || '';
                if (city) cityInput.value = city;
              }
            }

            li.addEventListener('click', select);
            li.addEventListener('keydown', function (e) {
              if (e.key === 'Enter') { e.preventDefault(); select(); }
              if (e.key === 'ArrowDown') { e.preventDefault(); if (li.nextElementSibling) li.nextElementSibling.focus(); }
              if (e.key === 'ArrowUp') { e.preventDefault(); if (li.previousElementSibling) li.previousElementSibling.focus(); else searchInput.focus(); }
              if (e.key === 'Escape') { suggestions.hidden = true; searchInput.focus(); }
            });

            suggestions.appendChild(li);
          });
          suggestions.hidden = false;
        })
        .catch(function () { suggestions.hidden = true; });
    }

    // ── Browser geolocation ────────────────────────────────────────
    locateBtn.addEventListener('click', function () {
      if (!navigator.geolocation) {
        statusEl.textContent = gettext('Geolocation not supported by your browser');
        return;
      }

      statusEl.textContent = gettext('Detecting position…');
      locateBtn.disabled = true;

      navigator.geolocation.getCurrentPosition(
        function (pos) {
          locateBtn.disabled = false;
          var lat = pos.coords.latitude;
          var lng = pos.coords.longitude;
          setPosition(lat, lng, true);
          statusEl.textContent = '';

          // Reverse geocode to get city name
          reverseGeocode(lat, lng);
        },
        function (err) {
          locateBtn.disabled = false;
          if (err.code === err.PERMISSION_DENIED) {
            statusEl.textContent = gettext('Location access denied');
          } else {
            statusEl.textContent = gettext('Could not detect position');
          }
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
      );
    });

    // ── Manual coordinate toggle ───────────────────────────────────
    manualToggle.addEventListener('click', function () {
      var isHidden = manualRow.hidden;
      manualRow.hidden = !isHidden;
      manualToggle.setAttribute('aria-expanded', String(isHidden));
      manualToggle.textContent = isHidden
        ? gettext('Hide manual coordinates')
        : gettext('Enter coordinates manually');
    });

    // Manual input → update map
    latField.input.addEventListener('change', applyManual);
    lngField.input.addEventListener('change', applyManual);

    function applyManual() {
      var lat = parseFloat(latField.input.value);
      var lng = parseFloat(lngField.input.value);
      if (!isNaN(lat) && !isNaN(lng) && lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
        setPosition(lat, lng, true);
      }
    }

    // ── Core: set position ─────────────────────────────────────────
    function setPosition(lat, lng, panMap) {
      lat = Math.round(lat * 1000000) / 1000000;
      lng = Math.round(lng * 1000000) / 1000000;

      // Update marker
      if (marker) {
        marker.setLatLng([lat, lng]);
      } else {
        marker = L.marker([lat, lng], { draggable: true }).addTo(map);
        bindMarkerDrag(marker);
      }

      if (panMap) {
        map.setView([lat, lng], Math.max(map.getZoom(), MARKER_ZOOM));
      }

      // Update manual fields
      latField.input.value = lat;
      lngField.input.value = lng;

      // Update hidden coordinates field
      if (coordsInput) {
        coordsInput.value = lat + ',' + lng;
      }
    }

    function bindMarkerDrag(m) {
      m.on('dragend', function () {
        var pos = m.getLatLng();
        setPosition(pos.lat, pos.lng, false);
        reverseGeocode(pos.lat, pos.lng);
      });
    }

    // ── Reverse geocode (city name) ────────────────────────────────
    function reverseGeocode(lat, lng) {
      var url = NOMINATIM_REVERSE + '?format=json&lat=' + lat + '&lon=' + lng +
                '&zoom=12&addressdetails=1';

      fetch(url, { headers: { 'Accept-Language': lang } })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data && data.address) {
            var city = data.address.city || data.address.town ||
                       data.address.village || data.address.municipality || '';
            if (city) {
              if (cityInput) cityInput.value = city;
              searchInput.value = data.display_name || city;
            }
          }
        })
        .catch(function () { /* silent */ });
    }

    // ── Helpers ────────────────────────────────────────────────────
    function el(tag, cls) {
      var e = document.createElement(tag);
      if (cls) e.className = cls;
      return e;
    }

    function createManualField(name, label, initial) {
      var wrap = el('div', 'geocoder__manual-field');
      var lbl = el('label', 'form-label');
      lbl.textContent = label;
      var input = el('input', 'geocoder__coord-input form-input');
      input.type = 'number';
      input.step = 'any';
      input.name = '_geocoder_' + name;
      input.setAttribute('aria-label', label);
      if (initial !== null && !isNaN(initial)) input.value = initial;
      lbl.setAttribute('for', input.name);
      wrap.appendChild(lbl);
      wrap.appendChild(input);
      return { wrap: wrap, input: input };
    }

    // gettext fallback if django i18n JS not loaded
    function gettext(s) {
      return (typeof window.gettext === 'function') ? window.gettext(s) : s;
    }
  }
})();
