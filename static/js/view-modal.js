document.addEventListener('DOMContentLoaded', function () {
    var modalEl = document.getElementById('viewModal');
    if (!modalEl) return;

    var container = document.getElementById('viewModalContainer');

    modalEl.addEventListener('show.bs.modal', function (event) {
        var btn = event.relatedTarget;
        if (!btn) return;

        var url = btn.getAttribute('data-load-url');
        if (!url) return;

        container.innerHTML = '<div class="modal-body p-5 text-center">Loading...</div>';

        fetch(url, { credentials: 'same-origin' })
            .then(resp => resp.text())
            .then(html => { container.innerHTML = html; })
            .catch(() => { container.innerHTML = '<div class="modal-body p-5 text-danger text-center">Failed to load.</div>'; });
    });
});
