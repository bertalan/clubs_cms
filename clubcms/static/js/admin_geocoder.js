/**
 * Admin Geocoder Bridge — Injects geocoder-widget into Wagtail admin
 * for EventDetailPage location fields.
 *
 * Detects the "Location" tab, hides the raw coordinates field,
 * and inserts a [data-geocoder-widget] container that the
 * geocoder-widget.js will initialise automatically.
 */
(function () {
  'use strict';

  /* Field IDs used by Wagtail for EventDetailPage */
  var ADDR_ID   = 'id_location_address';
  var COORDS_ID = 'id_location_coordinates';

  function init() {
    var addrField   = document.getElementById(ADDR_ID);
    var coordsField = document.getElementById(COORDS_ID);

    /* Only act on pages that have both fields (EventDetailPage) */
    if (!addrField || !coordsField) return;

    /* Parse existing coordinates for initial marker position */
    var initialLat = '';
    var initialLng = '';
    var val = (coordsField.value || '').trim();
    if (val && val.indexOf(',') !== -1) {
      var parts = val.split(',');
      var lat = parseFloat(parts[0]);
      var lng = parseFloat(parts[1]);
      if (!isNaN(lat) && !isNaN(lng)) {
        initialLat = lat;
        initialLng = lng;
      }
    }

    /* ── Build the geocoder container ─────────────────────────── */
    var widget = document.createElement('div');
    widget.setAttribute('data-geocoder-widget', '');
    widget.setAttribute('data-target-coordinates', '#' + COORDS_ID);
    widget.setAttribute('data-search-placeholder', 'Search address…');
    if (initialLat !== '' && initialLng !== '') {
      widget.setAttribute('data-initial-lat', String(initialLat));
      widget.setAttribute('data-initial-lng', String(initialLng));
    }

    /* Insert the widget after the address field's panel wrapper */
    var addrPanel = addrField.closest('[data-field-wrapper]')
                 || addrField.closest('.w-field');
    if (addrPanel && addrPanel.parentNode) {
      addrPanel.parentNode.insertBefore(widget, addrPanel.nextSibling);
    } else {
      /* Fallback: insert before the coordinates field */
      var coordsPanel = coordsField.closest('[data-field-wrapper]')
                     || coordsField.closest('.w-field');
      if (coordsPanel && coordsPanel.parentNode) {
        coordsPanel.parentNode.insertBefore(widget, coordsPanel);
      }
    }

    /* Pre-fill search box with address value so user sees context */
    if (addrField.value) {
      /* The geocoder-widget will create the search input;
         we store the value and patch it after init */
      widget.setAttribute('data-prefill-search', addrField.value);
    }

    /* ── Initialise the geocoder widget ───────────────────────── */
    if (typeof window._initGeocoderWidgets === 'function') {
      window._initGeocoderWidgets();
    } else {
      /* geocoder-widget.js uses querySelectorAll on load, but we
         added the element dynamically — re-trigger init */
      var evt = new CustomEvent('geocoder:init');
      document.dispatchEvent(evt);
    }

    /* ── Wire address field sync ──────────────────────────────── */
    /* When user selects an address from geocoder suggestions,
       also update the address field */
    var observer = new MutationObserver(function () {
      var searchInput = widget.querySelector('.geocoder__search-input');
      if (!searchInput) return;
      observer.disconnect();

      /* Prefill search from existing address */
      if (widget.dataset.prefillSearch) {
        searchInput.value = widget.dataset.prefillSearch;
      }

      /* When a suggestion is selected, sync to address field */
      searchInput.addEventListener('change', function () {
        if (searchInput.value) {
          addrField.value = searchInput.value;
        }
      });

      /* Also watch for programmatic value changes via suggestions */
      var origSetValue = Object.getOwnPropertyDescriptor(
        HTMLInputElement.prototype, 'value'
      );
      /* Use a lighter approach: poll after suggestion clicks */
      widget.addEventListener('click', function () {
        setTimeout(function () {
          if (searchInput.value && searchInput.value !== addrField.value) {
            addrField.value = searchInput.value;
          }
        }, 300);
      });
    });
    observer.observe(widget, { childList: true, subtree: true });
  }

  /* Wait for DOM + Wagtail tab system to be ready */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    /* Small delay to let Wagtail render panels */
    setTimeout(init, 100);
  }
})();
