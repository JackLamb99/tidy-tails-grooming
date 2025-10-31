from django import forms
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from services.models import Service
from bookings.models import Booking
from contact.models import ContactMessage


def superuser_required(user):
    return user.is_authenticated and user.is_superuser


# Dashboard Views
@login_required
@user_passes_test(superuser_required)
def admin_dashboard(request):
    services = (
        Service.objects
        .all()
        .annotate(
            confirmed_count=Count(
                'bookings',
                filter=Q(bookings__status=Booking.Status.CONFIRMED)
            )
        )
        .order_by("name")
    )

    upcoming = (
        Booking.objects
        .filter(status__in=[Booking.Status.CONFIRMED])
        .order_by("date", "time")
    )
    previous = (
        Booking.objects
        .filter(status__in=[Booking.Status.CANCELLED, Booking.Status.COMPLETED])
        .order_by("-date", "-time")
    )

    messages_qs = ContactMessage.objects.all()
    return render(request, "dashboard/admin.html", {
        "services": services,
        "upcoming": upcoming,
        "previous": previous,
        "messages_qs": messages_qs,
    })


# Services Views
@login_required
@user_passes_test(superuser_required)
@require_POST
def service_toggle_active(request, pk):
    service = get_object_or_404(Service, pk=pk)
    service.is_active = not service.is_active
    service.save(update_fields=["is_active"])
    return redirect("dashboard:admin_dashboard")


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            "name",
            "description",
            "price_small",
            "price_medium",
            "price_large",
            "includes",
            "is_active"
        ]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "description": forms.Textarea(attrs={
                "rows": 3,
                "class": "form-control"
            }),
            "includes": forms.Textarea(attrs={
                "rows": 8,
                "class": "form-control",
                "placeholder": "List each included item on a new line."
            }),
            "price_small": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01"
            }),
            "price_medium": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01"
            }),
            "price_large": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01"
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        qs = Service.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("A service with this name already exists.")
        return name


@login_required
@user_passes_test(superuser_required)
def service_new(request):
    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            try:
                form.save()
            except IntegrityError:
                form.add_error("name", "A service with this name already exists.")
                html = render(
                    request,
                    "dashboard/partials/service_form_inner.html",
                    {
                        "form": form,
                        "title": "New Service",
                        "action_url": request.path,
                        "submit_label": "Create",
                    },
                ).content.decode("utf-8")
                return JsonResponse({"success": False, "html": html}, status=400)

            messages.success(request, "New service created.")
            return JsonResponse({"success": True})

        html = render(
            request,
            "dashboard/partials/service_form_inner.html",
            {
                "form": form,
                "title": "New Service",
                "action_url": request.path,
                "submit_label": "Create",
            },
        ).content.decode("utf-8")
        return JsonResponse({"success": False, "html": html}, status=400)

    form = ServiceForm()
    return render(
        request,
        "dashboard/partials/service_form_inner.html",
        {
            "form": form,
            "title": "New Service",
            "action_url": request.path,
            "submit_label": "Create",
        },
    )


@login_required
@user_passes_test(superuser_required)
def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == "POST":
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            try:
                form.save()
            except IntegrityError:
                form.add_error("name", "A service with this name already exists.")
                html = render(
                    request,
                    "dashboard/partials/service_form_inner.html",
                    {
                        "form": form,
                        "title": f"Edit Service - {service.name}",
                        "action_url": request.path,
                        "submit_label": "Save changes",
                    },
                ).content.decode("utf-8")
                return JsonResponse({"success": False, "html": html}, status=400)

            messages.success(request, "Service updated.")
            return JsonResponse({"success": True})

        html = render(
            request,
            "dashboard/partials/service_form_inner.html",
            {
                "form": form,
                "title": f"Edit Service - {service.name}",
                "action_url": request.path,
                "submit_label": "Save changes",
            },
        ).content.decode("utf-8")
        return JsonResponse({"success": False, "html": html}, status=400)

    form = ServiceForm(instance=service)
    return render(
        request,
        "dashboard/partials/service_form_inner.html",
        {
            "form": form,
            "title": f"Edit Service - {service.name}",
            "action_url": request.path,
            "submit_label": "Save changes",
        },
    )


@login_required
@user_passes_test(superuser_required)
@require_POST
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)

    # If inactive AND no confirmed bookings
    has_confirmed = service.bookings.filter(status=Booking.Status.CONFIRMED).exists()
    if service.is_active or has_confirmed:
        messages.error(request, "Cannot delete: service must be inactive and have no confirmed bookings.")
        return redirect("dashboard:admin_dashboard")

    # Ensure any linked bookings have snapshot filled
    for b in Booking.objects.filter(Q(service=service) | Q(original_service=service), service_name_snapshot=""):
        b.service_name_snapshot = service.name
        b.save(update_fields=["service_name_snapshot"])

    service.delete()
    messages.success(request, f"Service '{service.name}' deleted.")
    return redirect("dashboard:admin_dashboard")


# Bookings Views
@login_required
@user_passes_test(superuser_required)
def booking_view(request, pk):
    b = get_object_or_404(Booking, pk=pk)
    return render(
        request,
        "dashboard/partials/booking_view_inner.html",
        {"b": b}
    )


@login_required
@user_passes_test(superuser_required)
@require_POST
def booking_mark_complete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.status != Booking.Status.COMPLETED:
        booking.status = Booking.Status.COMPLETED
        booking.save(update_fields=["status"])
        messages.success(request, "Booking marked as completed.")
    return redirect("dashboard:admin_dashboard")


@login_required
@user_passes_test(superuser_required)
@require_POST
def booking_mark_cancelled(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.status != Booking.Status.CANCELLED:
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=["status"])
        messages.success(request, "Booking cancelled.")
    return redirect("dashboard:admin_dashboard")


# Messages Views
@login_required
@user_passes_test(superuser_required)
def message_view(request, pk):
    m = get_object_or_404(ContactMessage, pk=pk)
    return render(
        request,
        "dashboard/partials/message_view_inner.html",
        {"m": m}
    )


@login_required
@user_passes_test(superuser_required)
@require_POST
def message_delete(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.delete()
    messages.success(request, "Message deleted.")
    return redirect("dashboard:admin_dashboard")
