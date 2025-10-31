from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("email", "subject", "created_at")
    list_filter = ("created_at",)
    search_fields = ("email", "first_name", "last_name")
    ordering = ("created_at",)  # oldest first in admin list
    readonly_fields = ("created_at",)
