document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.alert[data-autohide="true"]').forEach(function (el) {
        var delay = parseInt(el.getAttribute('data-delay'), 10);
        if (isNaN(delay)) delay = 5000; // default 5s
        setTimeout(function () {
        try {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(el);
            bsAlert.close();
        } catch (e) {
            // fallback if Bootstrap alert isn't available
            el.classList.remove('show');
            el.remove();
        }
        }, delay);
    });
});