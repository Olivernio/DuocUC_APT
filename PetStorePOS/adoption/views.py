from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from .models import Mascota, EstadoMascota, Especies
from .forms import AdoptionRequestForm


def list_Mascotas(request):
    qs = Mascota.objects.all()
    Especie = request.GET.get("Especie")
    status  = request.GET.get("Estado", EstadoMascota.Disponible)

    if Especie in dict(Especies.choices):
        qs = qs.filter(Especie=Especie)
    if status in dict(EstadoMascota.choices):
        qs = qs.filter(Estado=status)

    context = {
        "Mascota": qs,
        "Especie": Especie,
        "status": status,
        "Especies": Especies,
        "EstadoMascota": EstadoMascota,
    }
    return render(request, "adoption/list.html", context)



def Detalle_Mascota(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    form = AdoptionRequestForm()
    return render(request, "adoption/detail.html", {"Mascota": mascota, "form": form})


def Enviar_Solicitud(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    if request.method == "POST":
        form = AdoptionRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.Mascota = mascota
            req.save()
            messages.success(request, "¡Solicitud enviada! Te contactaremos pronto.")
            return redirect(reverse("adoption:detalle", args=[mascota.pk]))
    else:
        form = AdoptionRequestForm()
    return render(request, "adoption/detail.html", {"Mascota": mascota, "form": form})

