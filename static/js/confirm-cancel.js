document.addEventListener('DOMContentLoaded', function () {
    var modalEl = document.getElementById('confirmCancelModal');
    if (!modalEl) return;

    modalEl.addEventListener('show.bs.modal', function (event) {
        var triggerBtn = event.relatedTarget;
        if (!triggerBtn) return;

        var url = triggerBtn.getAttribute('data-cancel-url');
        var label = triggerBtn.getAttribute('data-cancel-label') || 'this booking';

        var form = modalEl.querySelector('#cancelForm');
        form.setAttribute('action', url);

        var text = modalEl.querySelector('#confirmCancelText');
        text.textContent = 'Are you sure you want to cancel your booking for ' + label + '?';
    });
});