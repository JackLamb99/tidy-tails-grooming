from django.shortcuts import render
from .models import Service


def services_list(request):
    services = Service.objects.filter(is_active=True).order_by('price_small')
    return render(request, "services/services.html", {"services": services})
