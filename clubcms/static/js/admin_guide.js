/**
 * Admin page guide: opens the guide <dialog> rendered by GuidePanel.
 * Native <dialog> handles focus trapping and Escape; a click on the
 * backdrop also closes it.
 */
(function () {
    "use strict";

    document.addEventListener("click", function (event) {
        var opener = event.target.closest("[data-admin-guide-open]");
        if (opener) {
            var dialog = document.getElementById(opener.getAttribute("aria-controls"));
            if (dialog && typeof dialog.showModal === "function") {
                dialog.showModal();
            }
            return;
        }
        if (event.target.matches("dialog.admin-guide__dialog")) {
            event.target.close();
        }
    });
})();
