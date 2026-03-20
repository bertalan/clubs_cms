(function () {
  "use strict";

  const COLOR_HINTS = [
    "color",
    "colour",
    "colore",
    "accent",
    "primary",
    "secondary",
    "background",
    "surface",
    "theme",
  ];

  const HEX6_REGEX = /^#[0-9a-fA-F]{6}$/;

  function isHex6(value) {
    return HEX6_REGEX.test(value || "");
  }

  function normalizeHex(value) {
    if (!value) {
      return null;
    }
    const trimmed = value.trim();
    if (!trimmed.startsWith("#") && /^[0-9a-fA-F]{6}$/.test(trimmed)) {
      return `#${trimmed.toUpperCase()}`;
    }
    if (isHex6(trimmed)) {
      return trimmed.toUpperCase();
    }
    return null;
  }

  function hasColorHint(input) {
    const attrs = [input.name, input.id, input.placeholder]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    if (COLOR_HINTS.some((hint) => attrs.includes(hint))) {
      return true;
    }

    const field = input.closest(".w-field, .field");
    const label = field ? field.querySelector("label") : null;
    const labelText = label ? label.textContent.toLowerCase() : "";
    return COLOR_HINTS.some((hint) => labelText.includes(hint));
  }

  function shouldEnhance(input) {
    if (!input || input.dataset.colorpickerEnhanced === "1") {
      return false;
    }
    if (input.disabled || input.readOnly) {
      return false;
    }
    if (input.type !== "text") {
      return false;
    }

    const current = normalizeHex(input.value);
    if (current) {
      return true;
    }

    const maxLength = Number(input.getAttribute("maxlength") || "0");
    if (maxLength === 7 && hasColorHint(input)) {
      return true;
    }

    return false;
  }

  function emitChange(input) {
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function attachPicker(input) {
    input.dataset.colorpickerEnhanced = "1";
    input.classList.add("admin-colorpicker-source");

    const wrapper = document.createElement("div");
    wrapper.className = "admin-colorpicker-wrap";

    const picker = document.createElement("input");
    picker.type = "color";
    picker.className = "admin-colorpicker-input";
    picker.setAttribute("aria-label", "Color picker");

    const initial = normalizeHex(input.value) || "#000000";
    picker.value = initial;

    picker.addEventListener("input", function () {
      input.value = picker.value.toUpperCase();
      emitChange(input);
    });

    input.addEventListener("input", function () {
      const normalized = normalizeHex(input.value);
      if (normalized) {
        picker.value = normalized;
      }
    });

    wrapper.appendChild(picker);
    input.insertAdjacentElement("afterend", wrapper);
  }

  function enhanceAll(scope) {
    const root = scope || document;
    const inputs = root.querySelectorAll('input[type="text"]');
    inputs.forEach(function (input) {
      if (shouldEnhance(input)) {
        attachPicker(input);
      }
    });
  }

  function init() {
    enhanceAll(document);

    const observer = new MutationObserver(function (mutations) {
      mutations.forEach(function (mutation) {
        mutation.addedNodes.forEach(function (node) {
          if (!(node instanceof HTMLElement)) {
            return;
          }

          if (node.matches && node.matches('input[type="text"]')) {
            if (shouldEnhance(node)) {
              attachPicker(node);
            }
            return;
          }

          if (node.querySelectorAll) {
            enhanceAll(node);
          }
        });
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
