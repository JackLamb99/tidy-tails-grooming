from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ContactMessageForm


def contact_view(request):
    if request.method == "POST":
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks! Your message has been sent.")
            return redirect("contact:contact")
    else:
        # Prefill for logged-in users
        initial = {}
        if request.user.is_authenticated:
            initial = {
                "email": getattr(request.user, "email", "") or "",
                "first_name": getattr(request.user, "first_name", "") or "",
                "last_name": getattr(request.user, "last_name", "") or "",
            }
        form = ContactMessageForm(initial=initial)

    return render(request, "contact/contact.html", {"form": form})
