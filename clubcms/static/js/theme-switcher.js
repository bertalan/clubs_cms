/**
 * Theme Switcher
 * Allows users to preview different themes without server reload.
 * Stores preference in localStorage.
 */
(function () {
  'use strict';

  const STORAGE_KEY = 'clubcms_theme_preview';
  const THEMES = ['velocity', 'heritage', 'zen', 'terra', 'tricolore', 'clubs'];

  /**
   * Get current theme from stylesheet link or default
   */
  function getCurrentTheme() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && THEMES.includes(saved)) return saved;

    const link = document.querySelector('link[href*="/css/themes/"]');
    if (link) {
      const match = link.href.match(/\/themes\/([^/]+)\//);
      if (match && THEMES.includes(match[1])) return match[1];
    }
    return 'velocity';
  }

  /**
   * Apply theme by swapping CSS file
   */
  function applyTheme(theme) {
    const link = document.querySelector('link[href*="/css/themes/"]');
    if (!link) return;

    const currentHref = link.href;
    const newHref = currentHref.replace(/\/themes\/[^/]+\//, `/themes/${theme}/`);

    if (currentHref !== newHref) {
      link.href = newHref;
      localStorage.setItem(STORAGE_KEY, theme);
    }
  }

  /**
   * Initialize switcher
   */
  function init() {
    const select = document.getElementById('theme-switcher-select');
    if (!select) return;

    const current = getCurrentTheme();
    select.value = current;

    // Apply saved theme on page load
    applyTheme(current);

    // Handle change
    select.addEventListener('change', function () {
      applyTheme(this.value);
    });
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
