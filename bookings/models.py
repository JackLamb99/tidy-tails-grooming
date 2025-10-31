from datetime import time, datetime, timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from services.models import Service


def hour_choices(start=6, end=19):
    '''
    Generate hourly time choices between start and end hours (inclusive).
    For 06:00-19:00 starts (the last slot runs 19:00-20:00).
    '''
    return [(time(h, 0), f"{h:02d}:00") for h in range(start, end + 1)]


class Booking(models.Model):
    '''
    Model representing a booking.
    - One booking per date and time slot (no double-booking).
    - Slots are 1 hour, with start times 06:00-19:00.
    - Only active services may be selected.
    '''
    class BreedSize(models.TextChoices):
        SMALL = "small", "Small"
        MEDIUM = "medium", "Medium"
        LARGE = "large", "Large"

    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="bookings",
    )

    # Capture the service originally chosen at booking time
    original_service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="original_bookings",
    )

    service_name_snapshot = models.CharField(
        max_length=120, editable=False, blank=True, default=""
    )

    date = models.DateField()
    time = models.TimeField(choices=hour_choices(6, 19))  # 06:00-19:00 starts
    breed_size = models.CharField(
        max_length=10,
        choices=BreedSize.choices,
    )
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.CONFIRMED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_service_display_name(self) -> str:
        """Safe service name for admin when FK may be null after deletion."""
        if self.service_id and self.service:
            return self.service.name
        return self.service_name_snapshot or "Service (deleted)"

    def clean(self):
        errors = {}

        # Only active services can be selected
        # Except reverting to their original service even if it's now inactive
        if self.service_id:
            if not self.pk:
                # Creating a new booking (must be active)
                if not self.service.is_active:
                    errors["service"] = (
                        "This service is not active and cannot be booked. "
                        "Please choose a different service."
                    )
            else:
                # Editing an existing booking
                try:
                    current_service_id = Booking.objects.only("service_id").get(pk=self.pk).service_id
                except Booking.DoesNotExist:
                    current_service_id = None

                if self.service_id != current_service_id:
                    # Allow reverting to original_service (even if inactive)
                    original_allowed_id = self.original_service_id
                    if not self.service.is_active and self.service_id != original_allowed_id:
                        errors["service"] = (
                            "This service is not active and cannot be selected. "
                            "Please choose a different service."
                        )

        # Ensure time is an allowed choice
        allowed = {choice[0] for choice in self._meta.get_field("time").choices}
        if self.time and self.time not in allowed:
            errors["time"] = (
                "This time is not available. "
                "Please choose an available slot between 06:00 and 19:00."
            )

        # Prevent double-booking for non-cancelled bookings
        if self.date and self.time:
            clash_qs = Booking.objects.filter(
                date=self.date,
                time=self.time,
            ).exclude(status=Booking.Status.CANCELLED)

            if self.pk:
                clash_qs = clash_qs.exclude(pk=self.pk)

            if clash_qs.exists():
                errors["time"] = (
                    "This time slot is already booked. "
                    "Please choose a different time."
                )

        # Block booking of past or too-soon slots
        if self.date and self.time and "time" not in errors:
            is_new = not bool(self.pk)
            date_time_changed = False
            if not is_new:
                try:
                    original = Booking.objects.only("date", "time").get(pk=self.pk)
                    date_time_changed = (self.date != original.date) or (self.time != original.time)
                except Booking.DoesNotExist:
                    is_new = True

            if is_new or date_time_changed:
                now = timezone.localtime(timezone.now())
                threshold = now + timedelta(hours=1)

                # Compare aware datetimes
                if self.starts_at < threshold:
                    errors["time"] = (
                        "This time has passed or is no longer available. "
                        "Please choose a later slot."
                    )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Capture original_service on first save
        if not self.pk and self.service_id and not self.original_service_id:
            self.original_service_id = self.service_id

        # Ensure service name snapshot is set
        if not self.service_name_snapshot and self.service_id:
            # Record name at time of booking
            self.service_name_snapshot = self.service.name

        super().save(*args, **kwargs)

    @property
    def starts_at(self):
        tz = timezone.get_current_timezone()
        naive = datetime.combine(self.date, self.time)
        return timezone.make_aware(naive, tz)

    @property
    def ends_at(self):
        return self.starts_at + timedelta(hours=1)

    @property
    def is_past(self):
        return timezone.localtime(timezone.now()) >= self.ends_at

    def __str__(self):
        return (
            f"{self.user} | {self.get_service_display_name()} | "
            f"{self.date} @ {self.time.strftime('%H:%M')} "
            f"[{self.get_status_display()}]"
        )

    class Meta:
        # Orders by date ascending, then time ascending
        ordering = ("date", "time")
        # Allow only one non-cancelled booking per date and time
        constraints = [
            models.UniqueConstraint(
                fields=("date", "time"),
                condition=Q(status__in=["confirmed", "completed"]),
                name="uniq_active_booking_per_date_time",
            )
        ]
        # Indexes to optimize filtering by date/time and status
        indexes = [
            models.Index(fields=["date", "time"]),
            models.Index(fields=["status"]),
        ]
