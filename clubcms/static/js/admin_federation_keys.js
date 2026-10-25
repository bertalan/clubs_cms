/**
 * Partner club edit page: "Generate key pair" fills the link key and the
 * shared secret with a fresh pair from the server.
 */
(function () {
    "use strict";

    document.addEventListener("click", function (event) {
        var button = event.target.closest("[data-federation-generate]");
        if (!button) return;

        var box = button.closest("[data-federation-key-tools]");
        var form = button.closest("form");
        var status = box.querySelector("[data-federation-status]");
        var keyInput = form.querySelector('[name="api_key"]');
        var secretInput = form.querySelector('[name="our_key_for_them"]');
        var csrf = form.querySelector('[name="csrfmiddlewaretoken"]');

        if ((keyInput.value || secretInput.value) && !window.confirm(box.dataset.confirmReplace)) {
            return;
        }

        fetch(box.dataset.generateUrl, {
            method: "POST",
            credentials: "same-origin",
            headers: { "X-CSRFToken": csrf ? csrf.value : "" },
        })
            .then(function (response) {
                if (!response.ok) throw new Error(String(response.status));
                return response.json();
            })
            .then(function (data) {
                [[keyInput, data.api_key], [secretInput, data.shared_secret]].forEach(function (pair) {
                    pair[0].value = pair[1];
                    pair[0].dispatchEvent(new Event("change", { bubbles: true }));
                });
                status.textContent = box.dataset.msgDone;
            })
            .catch(function () {
                status.textContent = box.dataset.msgError;
            });
    });
})();
