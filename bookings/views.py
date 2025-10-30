from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from .forms import BookingCreateForm
from .models import Booking


def booking_create_page(request):
    # Block POSTs from guests (but allow them to view the page)
    if request.method == "POST" and not request.user.is_authenticated:
        messages.info(request, "Please log in to make a booking.")
        # either redirect to login, or back to the same page - your choice
        return redirect(f"{reverse('accounts:login')}?next={request.path}")

    if request.method == "POST":
        form = BookingCreateForm(request.POST)
        if form.is_valid():
            try:
                form.save(user=request.user)
            except Exception as e:
                messages.error(request, str(e))
            else:
                messages.success(request, "Booking created.")
                return redirect("bookings:booking_create_page")
    else:
        initial = {}
        if "date" in request.GET:
            initial["date"] = request.GET["date"]
        form = BookingCreateForm(initial=initial)

    return render(request, "bookings/bookings.html", {"form": form})


@login_required
def booking_cancel(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden("Invalid method")
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.is_past:
        messages.error(request, "This booking has already passed and cannot be cancelled.", extra_tags="bookings")
        return redirect("accounts:account")
    booking.status = Booking.Status.CANCELLED
    booking.save(update_fields=["status"])
    messages.success(request, "Booking cancelled.", extra_tags="bookings")
    return redirect("accounts:account")
