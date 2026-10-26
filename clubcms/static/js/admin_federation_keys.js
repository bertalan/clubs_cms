/**
 * Partner club edit page: copy and show the access credential we issued,
 * and confirm before replacing it.
 */
(function () {
    "use strict";

    function announce(button, message) {
        var box = button.closest("[data-federation-tools]");
        var status = box && box.querySelector("[data-federation-status]");
        if (status) status.textContent = message;
    }

    function valueInput(button) {
        return button.closest(".federation-tools__row").querySelector("[data-federation-value]");
    }

    document.addEventListener("click", function (event) {
        var copy = event.target.closest("[data-federation-copy]");
        if (copy) {
            var box = copy.closest("[data-federation-tools]");
            var value = valueInput(copy).value;
            if (!navigator.clipboard) {
                announce(copy, box.dataset.msgCopyFailed);
                return;
            }
            navigator.clipboard.writeText(value).then(
                function () { announce(copy, box.dataset.msgCopied); },
                function () { announce(copy, box.dataset.msgCopyFailed); }
            );
            return;
        }

        var reveal = event.target.closest("[data-federation-reveal]");
        if (reveal) {
            var input = valueInput(reveal);
            var shown = input.type === "password";
            input.type = shown ? "text" : "password";
            reveal.setAttribute("aria-pressed", shown ? "true" : "false");
            reveal.textContent = shown ? reveal.dataset.labelHide : reveal.dataset.labelShow;
            return;
        }

        var confirmButton = event.target.closest("[data-federation-confirm]");
        if (confirmButton && !window.confirm(confirmButton.dataset.federationConfirm)) {
            event.preventDefault();
        }
    });
})();
