from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "time",
        "user",
        "service",
        "breed_size",
        "status",
        "created_at"
    )

    # Filters & search
    list_filter = (
        "status",
        "breed_size",
        "service",
        ("date", admin.DateFieldListFilter)
    )
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "service__name"
    )
    date_hierarchy = "date"

    # Show upcoming first (chronological)
    ordering = ("date", "time")

    # Everything is read-only to prevent accidental manual edits
    readonly_fields = (
        "user",
        "service",
        "date", "time",
        "breed_size",
        "notes",
        "status",
        "created_at",
        "updated_at"
    )

    fieldsets = (
        (None, {
            "fields": ("user", "service", ("date", "time"), "breed_size", "notes")
        }),
        ("Status", {
            "fields": ("status",),
        }),
        ("Timestamps", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at"),
        }),
    )

    # Bulk actions
    actions = ("mark_completed", "cancel_bookings")

    def mark_completed(self, request, queryset):
        queryset.update(status=Booking.Status.COMPLETED)
    mark_completed.short_description = "Mark selected bookings as Completed"

    def cancel_bookings(self, request, queryset):
        queryset.update(status=Booking.Status.CANCELLED)
    cancel_bookings.short_description = "Cancel selected bookings"

    # Permissions
    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    # No adds from admin to prevent duplicate bookings
    # Bookings are created via the user-facing site
    def has_add_permission(self, request):
        return False

    # Keep change permission for superusers so actions are available
    # But fields are read-only so they can't edit records manually
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    # No deletes from admin to prevent loss of booking history
    # Use Cancel action instead
    def has_delete_permission(self, request, obj=None):
        return False
