(function () {
    const form = document.getElementById('booking-form');
    if (!form) return;

    const dateInput = form.querySelector('input[name="date"]');
    if (!dateInput) return;

    dateInput.addEventListener('change', function () {
        // Update only the 'date' query param and trigger a clean reload
        const url = new URL(window.location);
        if (dateInput.value) {
            url.searchParams.set('date', dateInput.value);
        } else {
            url.searchParams.delete('date');
        }
        window.location.replace(url.toString());
    });
})();
