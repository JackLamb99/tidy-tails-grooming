from django.urls import path
from .views import register, EmailLoginView, EmailLogoutView

app_name = "accounts"

urlpatterns = [
    path("register/", register, name="register"),
    path("login/",    EmailLoginView.as_view(),  name="login"),
    path("logout/",   EmailLogoutView.as_view(), name="logout"),
]
