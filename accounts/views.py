from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from .forms import RegistrationForm, EmailAuthenticationForm, ProfileUpdateForm, DeleteAccountForm
from bookings.forms import BookingUpdateForm
from bookings.models import Booking


def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


class EmailLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True


class EmailLogoutView(LogoutView):
    next_page = reverse_lazy("home")


@login_required
def account_dashboard(request):
    user = request.user

    # Base forms
    profile_form = ProfileUpdateForm(instance=user)
    password_form = PasswordChangeForm(user=user)
    delete_form = DeleteAccountForm()

    # Split bookings
    # now = timezone.localtime(timezone.now())

    # Upcoming - confirmed & not past (chronological)
    upcoming_qs = Booking.objects.filter(user=user, status=Booking.Status.CONFIRMED).order_by("date", "time")
    upcoming = [b for b in upcoming_qs if not b.is_past]

    # Previous & Cancelled - completed or cancelled (newest first)
    previous_cancelled = Booking.objects.filter(
        user=user,
        status__in=[Booking.Status.COMPLETED, Booking.Status.CANCELLED]
    ).order_by("-date", "-time")

    # Handle GET edit modal
    edit_id = request.GET.get("edit")
    editing = None
    edit_form = None
    if edit_id:
        editing = get_object_or_404(Booking, pk=edit_id, user=user)
        edit_form = BookingUpdateForm(instance=editing)

    # Handle POST actions by form_name switch
    if request.method == "POST":
        form_name = request.POST.get("form_name")

        if form_name == "profile":
            profile_form = ProfileUpdateForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Details updated.", extra_tags="account")
                return redirect("accounts:account")

        elif form_name == "password":
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed.", extra_tags="account")
                return redirect("accounts:account")

        elif form_name == "delete":
            delete_form = DeleteAccountForm(request.POST)
            if delete_form.is_valid() and delete_form.cleaned_data.get("confirm"):
                user_to_delete = request.user
                logout(request)
                user_to_delete.delete()
                messages.success(request, "Account deleted.", extra_tags="account")
                return redirect("home")

        elif form_name == "edit_booking":
            edit_id = request.POST.get("booking_id")
            editing = get_object_or_404(Booking, pk=edit_id, user=user)
            if editing.is_past:
                messages.error(request, "This booking has already passed and cannot be edited.", extra_tags="bookings")
                return redirect("accounts:account")
            edit_form = BookingUpdateForm(request.POST, instance=editing)
            if edit_form.is_valid():
                edit_form.save()
                messages.success(request, "Booking updated." , extra_tags="bookings")
                return redirect("accounts:account")

    return render(request, "accounts/account.html", {
        "profile_form": profile_form,
        "password_form": password_form,
        "delete_form": delete_form,
        "upcoming": upcoming,
        "previous_cancelled": previous_cancelled,
        "editing": editing,
        "edit_form": edit_form,
    })
