from django.contrib import admin


from django.contrib import admin
from .models import Mascota, AdoptionRequest

@admin.register(Mascota)
class PetAdmin(admin.ModelAdmin):
    list_display = ("Nombre", "Especie", "Edad_Años", "Estado", "is_Vacunado", "is_castrado")
    list_filter = ("Especie", "Estado", "is_Vacunado", "is_castrado")
    search_fields = ("Nombre", "Raza")

@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = ("Mascota", "full_name", "email", "Telefono", "processed", "created_at")
    list_filter = ("processed",)
    search_fields = ("full_name", "email", "Mascota__Nombre")
