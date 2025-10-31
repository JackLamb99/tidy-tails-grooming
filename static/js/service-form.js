document.addEventListener('DOMContentLoaded', function () {
    var modalEl = document.getElementById('serviceFormModal');
    if (!modalEl) return;

    var container = modalEl.querySelector('#serviceFormContainer');

    // Load partial when opening modal
    modalEl.addEventListener('show.bs.modal', function (event) {
        var btn = event.relatedTarget;
        if (!btn) return;

        var url = btn.getAttribute('data-load-url');
        if (!url) return;

        container.innerHTML = '<div class="modal-body p-5 text-center">Loading…</div>';

        fetch(url, { credentials: 'same-origin' })
            .then(function (resp) { return resp.text(); })
            .then(function (html) { container.innerHTML = html; })
            .catch(function () {
                container.innerHTML = '<div class="modal-body p-5 text-danger text-center">Failed to load form.</div>';
            });
    });

    // Submit via AJAX
    modalEl.addEventListener('submit', function (e) {
        var form = e.target;
        if (!form || form.id !== 'serviceForm') return;

        e.preventDefault();

        var action = form.getAttribute('action') || window.location.href;
        var formData = new FormData(form);

        fetch(action, {
            method: 'POST',
            body: formData,
            credentials: 'same-origin'
        })
        .then(function (resp) { return resp.text(); })
        .then(function (text) {
            // Try to parse JSON, if it fails, treat as HTML
            var data;
            try { data = JSON.parse(text); } catch (_) { data = null; }

            if (data && typeof data === 'object') {
                if (data.success) {
                    window.location.reload();
                    return;
                }
                if (data.html) {
                    container.innerHTML = data.html;
                    return;
                }
                // Unexpected JSON structure
                container.innerHTML = '<div class="modal-body p-5 text-danger text-center">Submission failed. Please try again.</div>';
                return;
            }

            // Not JSON, assume server sent raw HTML
            container.innerHTML = text;
        })
        .catch(function () {
            container.innerHTML = '<div class="modal-body p-5 text-danger text-center">Submission failed. Please try again.</div>';
        });
    });
});
