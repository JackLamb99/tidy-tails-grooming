from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path(
        "admin/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),
    # Services
    path(
        "admin/services/toggle/<int:pk>/",
        views.service_toggle_active,
        name="service_toggle"
    ),
    path(
        "admin/services/new/",
        views.service_new,
        name="service_new"
    ),
    path(
        "admin/services/edit/<int:pk>/",
        views.service_edit,
        name="service_edit"
    ),
    path(
        "admin/services/delete/<int:pk>/",
        views.service_delete,
        name="service_delete"
    ),
    # Bookings
    path(
        "admin/bookings/complete/<int:pk>/",
        views.booking_mark_complete,
        name="booking_complete"
    ),
    path(
        "admin/bookings/cancel/<int:pk>/",
        views.booking_mark_cancelled,
        name="booking_cancel"
    ),
    path(
        "admin/bookings/view/<int:pk>/",
        views.booking_view,
        name="booking_view"
    ),
    # Messages
    path(
        "admin/messages/delete/<int:pk>/",
        views.message_delete,
        name="message_delete"
    ),
    path(
        "admin/messages/view/<int:pk>/",
        views.message_view,
        name="message_view"
    ),
]
