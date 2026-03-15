/**
 * Admin Field Help Tooltip
 *
 * Transforms Wagtail's .w-field__help text into interactive tooltips with
 * an info icon (ℹ). Supports hover (desktop) and click/tap (mobile).
 *
 * Uses MutationObserver to catch dynamically added fields (InlinePanel,
 * StreamField).
 *
 * ARIA: role="button", aria-expanded, aria-describedby, role="tooltip".
 */
(function () {
    "use strict";

    var PROCESSED_ATTR = "data-help-tooltip-ready";
    var tooltipCounter = 0;

    /**
     * Transform a single .w-field__help element into a tooltip.
     */
    function enhanceHelpElement(helpEl) {
        if (helpEl.hasAttribute(PROCESSED_ATTR)) return;
        helpEl.setAttribute(PROCESSED_ATTR, "true");

        var text = helpEl.textContent.trim();
        if (!text) return;

        // Mark for CSS hiding
        helpEl.classList.add("has-tooltip");

        // Unique ID for ARIA
        tooltipCounter++;
        var tooltipId = "field-help-tip-" + tooltipCounter;

        // Create trigger button
        var trigger = document.createElement("button");
        trigger.type = "button";
        trigger.className = "field-help-trigger";
        trigger.setAttribute("role", "button");
        trigger.setAttribute("aria-expanded", "false");
        trigger.setAttribute("aria-describedby", tooltipId);
        trigger.setAttribute("aria-label", "Info");
        trigger.textContent = "i";

        // Create tooltip
        var tooltip = document.createElement("span");
        tooltip.className = "field-help-tooltip";
        tooltip.id = tooltipId;
        tooltip.setAttribute("role", "tooltip");
        tooltip.setAttribute("aria-hidden", "true");
        tooltip.textContent = text;

        helpEl.appendChild(trigger);
        helpEl.appendChild(tooltip);

        // --- Interaction handlers ---

        function show() {
            tooltip.setAttribute("aria-hidden", "false");
            trigger.setAttribute("aria-expanded", "true");
        }

        function hide() {
            tooltip.setAttribute("aria-hidden", "true");
            trigger.setAttribute("aria-expanded", "false");
        }

        function toggle(e) {
            e.preventDefault();
            e.stopPropagation();
            var isVisible = tooltip.getAttribute("aria-hidden") === "false";
            if (isVisible) {
                hide();
            } else {
                closeAllTooltips();
                show();
            }
        }

        trigger.addEventListener("click", toggle);

        // Desktop: hover open/close
        helpEl.addEventListener("mouseenter", function () {
            closeAllTooltips();
            show();
        });
        helpEl.addEventListener("mouseleave", function () {
            hide();
        });
    }

    /**
     * Close all open tooltips.
     */
    function closeAllTooltips() {
        var openTips = document.querySelectorAll('.field-help-tooltip[aria-hidden="false"]');
        for (var i = 0; i < openTips.length; i++) {
            openTips[i].setAttribute("aria-hidden", "true");
            var trigger = openTips[i].previousElementSibling;
            if (trigger && trigger.classList.contains("field-help-trigger")) {
                trigger.setAttribute("aria-expanded", "false");
            }
        }
    }

    /**
     * Process all unprocessed .w-field__help elements.
     */
    function processAll() {
        var helpEls = document.querySelectorAll(
            ".w-field__help:not([" + PROCESSED_ATTR + "])"
        );
        for (var i = 0; i < helpEls.length; i++) {
            enhanceHelpElement(helpEls[i]);
        }
    }

    // --- Global listeners ---

    // Close on Escape
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            closeAllTooltips();
        }
    });

    // Close on click outside
    document.addEventListener("click", function (e) {
        if (!e.target.closest(".field-help-trigger") && !e.target.closest(".field-help-tooltip")) {
            closeAllTooltips();
        }
    });

    // --- Init ---

    // Process existing fields
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", processAll);
    } else {
        processAll();
    }

    // MutationObserver for dynamically added fields (InlinePanel, StreamField)
    var observer = new MutationObserver(function (mutations) {
        var shouldProcess = false;
        for (var i = 0; i < mutations.length; i++) {
            if (mutations[i].addedNodes.length > 0) {
                shouldProcess = true;
                break;
            }
        }
        if (shouldProcess) {
            processAll();
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
    });
})();
