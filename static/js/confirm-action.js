document.addEventListener('DOMContentLoaded', function () {
    var modalEl = document.getElementById('confirmActionModal');
    if (!modalEl) return;

    modalEl.addEventListener('show.bs.modal', function (event) {
        var triggerBtn = event.relatedTarget;
        if (!triggerBtn) return;

        var url = triggerBtn.getAttribute('data-action-url');
        var title = triggerBtn.getAttribute('data-action-title') || 'Confirm Action';
        var text = triggerBtn.getAttribute('data-action-text') || 'Are you sure?';
        var label = triggerBtn.getAttribute('data-action-label') || '';
        var btnText = triggerBtn.getAttribute('data-action-btn-text') || 'Confirm';
        var btnCls = triggerBtn.getAttribute('data-action-btn-class') || 'btn-primary';

        var form = modalEl.querySelector('#confirmActionForm');
        var hTitle = modalEl.querySelector('#confirmActionLabel');
        var pText = modalEl.querySelector('#confirmActionText');
        var pMeta = modalEl.querySelector('#confirmActionMeta');
        var submit = modalEl.querySelector('#confirmActionSubmit');

        form.setAttribute('action', url);

        hTitle.textContent = title;
        pText.textContent = text;
        pMeta.textContent = label;

        submit.className = 'btn ' + btnCls;
        submit.textContent = btnText;
    });
});
