from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Booking, hour_choices
from services.models import Service


class BookingCreateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ("date", "time", "service", "breed_size", "notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["service"].queryset = Service.objects.filter(is_active=True)
        self.fields["date"].widget = forms.DateInput(attrs={"type": "date"})

        # Date input - don't allow past dates
        today = timezone.localdate()
        self.fields["date"].widget.attrs["min"] = today.isoformat()

        selected_date = None
        date_str = self.data.get("date") or self.initial.get("date")
        if date_str:
            try:
                selected_date = timezone.datetime.fromisoformat(str(date_str)).date()
            except Exception:
                selected_date = None

        times = hour_choices(6, 19)
        if selected_date:
            # Remove taken (non-cancelled) times for selected date
            taken = set(
                Booking.objects
                .filter(date=selected_date)
                .exclude(status=Booking.Status.CANCELLED)
                .values_list("time", flat=True)
            )
            times = [(t, label) for (t, label) in times if t not in taken]

            # Remove past times
            now = timezone.localtime(timezone.now())
            # Threshold = one hour from 'now'
            threshold = now + timedelta(hours=1)

            # No times in the past
            if selected_date < today:
                times = []
            # Only allow slots an hour or more from 'now'
            elif selected_date == today:
                allowed_hour = threshold.hour
                times = [(t, label) for (t, label) in times if t.hour >= allowed_hour]

        self.fields["time"].choices = times

    def save(self, user, commit=True):
        obj = super().save(commit=False)
        obj.user = user
        if commit:
            obj.full_clean()
            obj.save()
        return obj


class BookingUpdateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ("service", "breed_size", "notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow active, current and original service
        # Update form can be saved even if current service is inactive
        # Users can return to their originally booked service even if inactive
        qs = Service.objects.filter(is_active=True)
        if self.instance and self.instance.pk:
            ids = [
                sid for sid in
                [self.instance.service_id, self.instance.original_service_id]
                if sid
            ]
            if ids:
                qs = qs | Service.objects.filter(pk__in=ids)
        self.fields["service"].queryset = qs.distinct()
