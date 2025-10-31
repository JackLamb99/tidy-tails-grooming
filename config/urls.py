from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render


def home(request):
    return render(request, "index.html")


urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("services/", include("services.urls", namespace="services")),
    path("bookings/", include("bookings.urls", namespace="bookings")),
    path("contact/", include("contact.urls", namespace="contact")),
    path("dashboard/", include("dashboard.urls", namespace="dashboard")),
]
