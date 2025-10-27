from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db import IntegrityError

from .forms import RegistrationForm, EmailAuthenticationForm


def register(request):
    if request.user.is_authenticated:
        return redirect("home")  # redirect logged-in users to home

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login after successful registration
            return redirect("home")  # redirect to home page after registration
    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


class EmailLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True


class EmailLogoutView(LogoutView):
    next_page = reverse_lazy("home")
