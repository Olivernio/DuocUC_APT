# Vistas DjangoCRUD - PetStorePOS

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.conf import settings

def about(request):
    return render(request, "acerca/about.html")

def favicon_view(request):
    favicon_path = settings.STATIC_URL + 'img/png/Icono1.png'
    return HttpResponseRedirect(favicon_path)

def accessibility(request):
    return render(request, "accessibility/accessibility.html")
