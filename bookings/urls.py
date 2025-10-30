from django.urls import path
from . import views

app_name = "bookings"

urlpatterns = [
    path("", views.booking_create_page, name="booking_create_page"),
    path("<int:pk>/cancel/", views.booking_cancel, name="booking_cancel"),
]
