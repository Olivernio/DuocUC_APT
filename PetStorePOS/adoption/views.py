import requests
import re # <--- AÑADIDO
import time # <--- AÑADIDO
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _, ngettext_lazy, ngettext # <--- MODIFICADO
from django.core.cache import cache # <--- AÑADIDO
from core.utils import traducir_texto # <--- ¡NUESTRA FUNCIÓN!

# --- Vista de Lista (Modificada para usar la lógica de filtros de tus compañeros) ---

def mascotas_huachitos_view(request):
    """
    Muestra las mascotas de la API.
    (No traduce la lista por rendimiento)
    """
    api_url = "https://huachitos.cl/api/animales/"
    
    # Claves de la API (siempre en español)
    species_keys = ["perro", "gato", "conejo", "roedor", "ave"]
    
    # Texto para mostrar al usuario (traducible)
    species_for_display = [
        ("perro", _("perro")), ("gato", _("gato")), ("conejo", _("conejo")),
        ("roedor", _("roedor")), ("ave", _("ave")),
    ]
    
    type_filter = request.GET.get("tipo", "").lower()
    pets = []
    error_message = None

    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        
        api_data = response.json()
        pets = api_data.get("data", [])

        if type_filter and type_filter in species_keys: 
            pets = [pet for pet in pets if pet.get("tipo", "").lower() == type_filter]
        
    except requests.exceptions.RequestException as e:
        print(f"ERROR fetching from Huachitos API: {e}")
        error_message = _("No se pudo conectar con la API de Huachitos en este momento. Por favor, intenta más tarde.")

    context = {
        "mascotas": pets,
        "especies_disponibles": species_for_display,
        "tipo_filtrado": type_filter,
        "error_message": error_message,
    }
    return render(request, "adoption/list.html", context)


# --- Vista de Detalles (Reemplazada con nuestra lógica Híbrida) ---

def mascota_detail_view(request, pet_id):
    """
    Muestra el detalle de una mascota.
    Traduce texto corto localmente (con Django i18n).
    Traduce descripciones largas con la API de MyMemory.
    """
    api_url = f"https://huachitos.cl/api/animal/{pet_id}"
    pet = None
    error_message = None
    current_language = request.LANGUAGE_CODE 

    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        api_data = response.json()
        pet = api_data.get("data")
        
        if pet and current_language != 'es':
            
            # --- TRADUCCIÓN LOCAL (RÁPIDA Y FIABLE) ---
            
            # 1. Traducir TIPO
            tipo_key = pet.get('tipo', '').lower()
            if tipo_key == 'perro':
                pet['tipo'] = _("perro")
            elif tipo_key == 'gato':
                pet['tipo'] = _("gato")
            elif tipo_key == 'conejo':
                pet['tipo'] = _("conejo")
            elif tipo_key == 'roedor':
                pet['tipo'] = _("roedor")
            elif tipo_key == 'ave':
                pet['tipo'] = _("ave")

            # 2. Traducir EDAD (usando ngettext NO-LAZY)
            try:
                parts = pet['edad'].split(' ')
                number = int(parts[0])
                unit_translated = ngettext("Año", "Años", number) # Traduce inmediatamente
                pet['edad'] = f"{number} {unit_translated}"
            except Exception:
                pass # Si falla (ej. "Cachorro"), deja el original

            # 3. Traducir GÉNERO (usando gettext_lazy)
            genero_key = pet.get('genero', '').lower()
            if genero_key == 'macho':
                pet['genero'] = _("Macho")
            elif genero_key == 'hembra':
                pet['genero'] = _("Hembra")

            # --- TRADUCCIÓN API (LENTA, SOLO PARA DESCRIPCIONES) ---
            campos_desc_a_traducir = ['desc_fisica', 'desc_personalidad', 'desc_adicional']
            
            for campo in campos_desc_a_traducir:
                if pet.get(campo):
                    # Llamamos a la API pidiendo las etiquetas <p>
                    pet[campo] = traducir_texto(pet[campo], current_language, add_p_tags=True) 

    except requests.exceptions.RequestException as e:
        print(f"ERROR fetching from Huachitos API for pet {pet_id}: {e}")
        error_message = _("No se pudo cargar la información de la mascota. Es posible que ya no esté disponible.")

    context = {
        "mascota": pet,
        "error_message": error_message,
    }
    return render(request, "adoption/detail.html", context)