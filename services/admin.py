from django.contrib import admin
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price_small",
        "price_medium",
        "price_large",
        "is_active",
        "updated_at",
    )
    # Filter sidebar for active status
    list_filter = ("is_active",)

    # Read-only system fields
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Basic info", {"fields": ("name", "description", "is_active")}),
        ("Pricing (GBP)", {"fields": (("price_small", "price_medium", "price_large"),)}),
        ("Includes (one per line)", {"fields": ("includes",)}),
        ("System", {"fields": ("created_at", "updated_at")}),
    )

    ordering = ("price_small",)

    # Only allow superusers to add, edit, or delete
    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
