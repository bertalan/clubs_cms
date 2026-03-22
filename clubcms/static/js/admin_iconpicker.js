/**
 * Admin Icon Picker — Font Awesome 6 icon selector for Wagtail admin.
 *
 * Auto-detects input fields with "icon" in name/id/label and injects
 * a searchable dropdown with preview. Follows the colorpicker pattern
 * with MutationObserver for dynamic StreamField rows.
 *
 * Stores the FA class name (e.g. "fa-solid fa-motorcycle") in the field.
 */
(function () {
  'use strict';

  /* ── Popular FA 6 icon set (curated for club/event/social context) ── */
  var ICONS = [
    /* Transport & Vehicles */
    'fa-solid fa-motorcycle', 'fa-solid fa-car', 'fa-solid fa-car-side',
    'fa-solid fa-van-shuttle', 'fa-solid fa-truck', 'fa-solid fa-bicycle',
    'fa-solid fa-bus', 'fa-solid fa-plane', 'fa-solid fa-ship',
    'fa-solid fa-helicopter', 'fa-solid fa-gas-pump', 'fa-solid fa-road',
    'fa-solid fa-route', 'fa-solid fa-gauge-high', 'fa-solid fa-trailer',
    /* Events & Activities */
    'fa-solid fa-calendar', 'fa-solid fa-calendar-days', 'fa-solid fa-calendar-check',
    'fa-solid fa-clock', 'fa-solid fa-trophy', 'fa-solid fa-medal',
    'fa-solid fa-award', 'fa-solid fa-flag', 'fa-solid fa-flag-checkered',
    'fa-solid fa-champagne-glasses', 'fa-solid fa-cake-candles',
    'fa-solid fa-gift', 'fa-solid fa-ticket', 'fa-solid fa-star',
    /* Social & Communication */
    'fa-solid fa-users', 'fa-solid fa-user', 'fa-solid fa-user-group',
    'fa-solid fa-people-group', 'fa-solid fa-handshake',
    'fa-solid fa-comments', 'fa-solid fa-comment', 'fa-solid fa-envelope',
    'fa-solid fa-phone', 'fa-solid fa-share-nodes', 'fa-solid fa-bullhorn',
    'fa-solid fa-bell', 'fa-solid fa-at', 'fa-solid fa-hashtag',
    /* Social Brands */
    'fa-brands fa-facebook', 'fa-brands fa-instagram', 'fa-brands fa-x-twitter',
    'fa-brands fa-youtube', 'fa-brands fa-tiktok', 'fa-brands fa-whatsapp',
    'fa-brands fa-telegram', 'fa-brands fa-linkedin', 'fa-brands fa-discord',
    'fa-brands fa-github', 'fa-brands fa-strava', 'fa-brands fa-flickr',
    'fa-brands fa-pinterest', 'fa-brands fa-reddit', 'fa-brands fa-threads',
    'fa-brands fa-mastodon', 'fa-brands fa-spotify',
    /* Location & Maps */
    'fa-solid fa-location-dot', 'fa-solid fa-map', 'fa-solid fa-map-pin',
    'fa-solid fa-map-location-dot', 'fa-solid fa-compass',
    'fa-solid fa-mountain', 'fa-solid fa-mountain-sun', 'fa-solid fa-tree',
    'fa-solid fa-earth-europe', 'fa-solid fa-globe',
    /* Food & Drink */
    'fa-solid fa-utensils', 'fa-solid fa-mug-hot', 'fa-solid fa-wine-glass',
    'fa-solid fa-beer-mug-empty', 'fa-solid fa-pizza-slice',
    'fa-solid fa-burger', 'fa-solid fa-ice-cream',
    /* Aid & Medical */
    'fa-solid fa-hand-holding-heart', 'fa-solid fa-heart',
    'fa-solid fa-kit-medical', 'fa-solid fa-stethoscope',
    'fa-solid fa-bandage', 'fa-solid fa-suitcase-medical',
    'fa-solid fa-wheelchair', 'fa-solid fa-cross',
    'fa-solid fa-circle-plus', 'fa-solid fa-life-ring',
    /* Tools & Work */
    'fa-solid fa-wrench', 'fa-solid fa-screwdriver-wrench',
    'fa-solid fa-gears', 'fa-solid fa-gear', 'fa-solid fa-hammer',
    'fa-solid fa-toolbox', 'fa-solid fa-bolt',
    /* Media & Content */
    'fa-solid fa-camera', 'fa-solid fa-image', 'fa-solid fa-images',
    'fa-solid fa-video', 'fa-solid fa-music', 'fa-solid fa-newspaper',
    'fa-solid fa-podcast', 'fa-solid fa-microphone',
    'fa-solid fa-photo-film', 'fa-solid fa-film',
    /* Commerce & Finance */
    'fa-solid fa-shop', 'fa-solid fa-cart-shopping', 'fa-solid fa-tag',
    'fa-solid fa-tags', 'fa-solid fa-money-bill', 'fa-solid fa-credit-card',
    'fa-solid fa-euro-sign', 'fa-solid fa-receipt', 'fa-solid fa-barcode',
    /* Weather & Nature */
    'fa-solid fa-sun', 'fa-solid fa-cloud', 'fa-solid fa-cloud-sun',
    'fa-solid fa-umbrella', 'fa-solid fa-snowflake',
    'fa-solid fa-temperature-high', 'fa-solid fa-wind',
    /* Objects & Misc */
    'fa-solid fa-house', 'fa-solid fa-building', 'fa-solid fa-tent',
    'fa-solid fa-campground', 'fa-solid fa-fire',
    'fa-solid fa-shield', 'fa-solid fa-lock', 'fa-solid fa-key',
    'fa-solid fa-link', 'fa-solid fa-qrcode', 'fa-solid fa-book',
    'fa-solid fa-graduation-cap', 'fa-solid fa-lightbulb',
    'fa-solid fa-puzzle-piece', 'fa-solid fa-palette',
    'fa-solid fa-circle-info', 'fa-solid fa-circle-question',
    'fa-solid fa-circle-check', 'fa-solid fa-circle-exclamation',
    'fa-solid fa-triangle-exclamation', 'fa-solid fa-ban',
    'fa-solid fa-check', 'fa-solid fa-xmark', 'fa-solid fa-plus',
    'fa-solid fa-minus', 'fa-solid fa-arrows-rotate',
    /* Arrows & Navigation */
    'fa-solid fa-arrow-right', 'fa-solid fa-arrow-left',
    'fa-solid fa-arrow-up', 'fa-solid fa-arrow-down',
    'fa-solid fa-chevron-right', 'fa-solid fa-chevron-left',
    'fa-solid fa-angles-right', 'fa-solid fa-angles-left',
    /* Regular (outlined) variants */
    'fa-regular fa-heart', 'fa-regular fa-star', 'fa-regular fa-bell',
    'fa-regular fa-calendar', 'fa-regular fa-clock', 'fa-regular fa-envelope',
    'fa-regular fa-comment', 'fa-regular fa-image', 'fa-regular fa-user',
    'fa-regular fa-eye', 'fa-regular fa-thumbs-up', 'fa-regular fa-bookmark',
    'fa-regular fa-file', 'fa-regular fa-folder',
  ];

  /* Extract short name for search (e.g. "fa-solid fa-motorcycle" → "motorcycle") */
  function shortName(cls) {
    var parts = cls.split(' ');
    var last = parts[parts.length - 1] || '';
    return last.replace('fa-', '');
  }

  /* ── Field detection ─────────────────────────────────────────── */
  var ICON_HINTS = ['icon'];

  function hasIconHint(input) {
    var attrs = [input.name, input.id, input.placeholder]
      .filter(Boolean).join(' ').toLowerCase();
    if (ICON_HINTS.some(function (h) { return attrs.indexOf(h) !== -1; })) return true;
    var field = input.closest('.w-field, .field');
    var label = field ? field.querySelector('label') : null;
    var text = label ? label.textContent.toLowerCase() : '';
    return ICON_HINTS.some(function (h) { return text.indexOf(h) !== -1; });
  }

  function shouldEnhance(input) {
    if (!input || input.dataset.iconpickerEnhanced === '1') return false;
    if (input.disabled || input.readOnly) return false;
    if (input.type !== 'text') return false;
    /* Skip color fields */
    if (input.dataset.colorpickerEnhanced === '1') return false;
    return hasIconHint(input);
  }

  /* ── Build picker UI ─────────────────────────────────────────── */
  function enhance(input) {
    input.dataset.iconpickerEnhanced = '1';

    var wrapper = document.createElement('div');
    wrapper.className = 'iconpicker';

    /* Preview */
    var preview = document.createElement('span');
    preview.className = 'iconpicker__preview';
    updatePreview(preview, input.value);

    /* Toggle button */
    var toggleBtn = document.createElement('button');
    toggleBtn.type = 'button';
    toggleBtn.className = 'iconpicker__toggle';
    toggleBtn.textContent = 'Browse icons';
    toggleBtn.setAttribute('aria-expanded', 'false');

    /* Clear button */
    var clearBtn = document.createElement('button');
    clearBtn.type = 'button';
    clearBtn.className = 'iconpicker__clear';
    clearBtn.innerHTML = '&times;';
    clearBtn.title = 'Clear icon';
    clearBtn.hidden = !input.value;

    /* Top bar */
    var bar = document.createElement('div');
    bar.className = 'iconpicker__bar';
    bar.appendChild(preview);
    bar.appendChild(toggleBtn);
    bar.appendChild(clearBtn);

    /* Dropdown panel */
    var dropdown = document.createElement('div');
    dropdown.className = 'iconpicker__dropdown';
    dropdown.hidden = true;

    /* Search */
    var search = document.createElement('input');
    search.type = 'text';
    search.className = 'iconpicker__search';
    search.placeholder = 'Search icons…';
    search.setAttribute('autocomplete', 'off');
    dropdown.appendChild(search);

    /* Grid */
    var grid = document.createElement('div');
    grid.className = 'iconpicker__grid';
    dropdown.appendChild(grid);

    buildGrid(grid, '', input, preview, dropdown, clearBtn);

    /* Insert into DOM */
    input.parentNode.insertBefore(wrapper, input.nextSibling);
    wrapper.appendChild(bar);
    wrapper.appendChild(dropdown);

    /* ── Events ─────────────────────────────────────────────── */
    toggleBtn.addEventListener('click', function () {
      var open = !dropdown.hidden;
      dropdown.hidden = open;
      toggleBtn.setAttribute('aria-expanded', String(!open));
      if (!open) {
        search.value = '';
        buildGrid(grid, '', input, preview, dropdown, clearBtn);
        setTimeout(function () { search.focus(); }, 50);
      }
    });

    clearBtn.addEventListener('click', function () {
      input.value = '';
      updatePreview(preview, '');
      clearBtn.hidden = true;
      input.dispatchEvent(new Event('change', { bubbles: true }));
    });

    search.addEventListener('input', function () {
      buildGrid(grid, search.value.trim().toLowerCase(), input, preview, dropdown, clearBtn);
    });

    /* Close on click outside */
    document.addEventListener('click', function (e) {
      if (!wrapper.contains(e.target)) {
        dropdown.hidden = true;
        toggleBtn.setAttribute('aria-expanded', 'false');
      }
    });

    /* Sync if input changes externally */
    input.addEventListener('change', function () {
      updatePreview(preview, input.value);
      clearBtn.hidden = !input.value;
    });
  }

  function buildGrid(grid, filter, input, preview, dropdown, clearBtn) {
    grid.innerHTML = '';
    var shown = 0;
    ICONS.forEach(function (cls) {
      var name = shortName(cls);
      if (filter && name.indexOf(filter) === -1) return;
      shown++;

      var cell = document.createElement('button');
      cell.type = 'button';
      cell.className = 'iconpicker__cell';
      cell.title = name;
      if (cls === input.value) cell.classList.add('iconpicker__cell--active');

      var icon = document.createElement('i');
      icon.className = cls;
      cell.appendChild(icon);

      cell.addEventListener('click', function () {
        input.value = cls;
        updatePreview(preview, cls);
        dropdown.hidden = true;
        clearBtn.hidden = false;
        input.dispatchEvent(new Event('change', { bubbles: true }));
        /* Remove previous active */
        grid.querySelectorAll('.iconpicker__cell--active').forEach(function (c) {
          c.classList.remove('iconpicker__cell--active');
        });
        cell.classList.add('iconpicker__cell--active');
      });

      grid.appendChild(cell);
    });

    if (shown === 0) {
      var empty = document.createElement('div');
      empty.className = 'iconpicker__empty';
      empty.textContent = 'No icons found';
      grid.appendChild(empty);
    }
  }

  function updatePreview(el, value) {
    el.innerHTML = '';
    if (value) {
      var i = document.createElement('i');
      i.className = value;
      el.appendChild(i);
    }
  }

  /* ── Scan & observe ──────────────────────────────────────────── */
  function scanAll() {
    document.querySelectorAll('input[type="text"]').forEach(function (input) {
      if (shouldEnhance(input)) enhance(input);
    });
  }

  /* Initial pass */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', scanAll);
  } else {
    setTimeout(scanAll, 150);
  }

  /* Watch for dynamic StreamField additions */
  var observer = new MutationObserver(function (mutations) {
    var hasNew = mutations.some(function (m) { return m.addedNodes.length > 0; });
    if (hasNew) setTimeout(scanAll, 200);
  });
  observer.observe(document.body, { childList: true, subtree: true });
})();
