# Vistas de Adopción - PetStorePOS

import requests
import logging
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

logger = logging.getLogger(__name__)

def mascotas_huachitos_view(request):
    api_url = "https://huachitos.cl/api/animales/"
    species_keys = ["perro", "gato", "conejo", "roedor", "ave"]
    species_for_display = [
        ("perro", _("perro")),
        ("gato", _("gato")),
        ("conejo", _("conejo")),
        ("roedor", _("roedor")),
        ("ave", _("ave")),
    ]
    type_filter = request.GET.get("tipo", "").lower()
    pets = []
    error_message = None

    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        api_data = response.json()
        pets = api_data.get("data", [])
        if not isinstance(pets, list):
            logger.warning(f"La API devolvió un formato inesperado. Esperaba una lista, obtuvo: {type(pets)}")
            pets = []
        if type_filter and type_filter in species_keys:
            pets = [pet for pet in pets if pet and isinstance(pet, dict) and pet.get("tipo", "").lower() == type_filter]
    except requests.exceptions.Timeout:
        logger.error("Timeout al conectar con la API de Huachitos")
        error_message = "La conexión con la API tardó demasiado. Por favor, intenta más tarde."
    except requests.exceptions.ConnectionError:
        logger.error("Error de conexión con la API de Huachitos")
        error_message = "No se pudo conectar con la API de Huachitos. Verifica tu conexión a internet."
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error HTTP de la API de Huachitos: {e}")
        status_code = getattr(e.response, 'status_code', 'desconocido')
        error_message = f"Error al obtener datos de la API (código {status_code}). Por favor, intenta más tarde."
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al obtener datos de la API de Huachitos: {e}", exc_info=True)
        error_message = "No se pudo conectar con la API de Huachitos en este momento. Por favor, intenta más tarde."
    except Exception as e:
        logger.error(f"Error inesperado en mascotas_huachitos_view: {e}", exc_info=True)
        error_message = "Ocurrió un error inesperado. Por favor, intenta más tarde."

    context = {
        "mascotas": pets,
        "especies_disponibles": species_for_display,
        "tipo_filtrado": type_filter,
        "error_message": error_message,
    }
    return render(request, "adoption/list.html", context)

def mascota_detail_view(request, pet_id):
    api_url = f"https://huachitos.cl/api/animal/{pet_id}"
    pet = None
    error_message = None

    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        api_data = response.json()
        pet = api_data.get("data")
    except requests.exceptions.Timeout:
        logger.error(f"Timeout al conectar con la API de Huachitos para mascota {pet_id}")
        error_message = "La conexión con la API tardó demasiado. Por favor, intenta más tarde."
    except requests.exceptions.ConnectionError:
        logger.error(f"Error de conexión con la API de Huachitos para mascota {pet_id}")
        error_message = "No se pudo conectar con la API de Huachitos. Verifica tu conexión a internet."
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error HTTP de la API de Huachitos para mascota {pet_id}: {e}")
        status_code = getattr(e.response, 'status_code', None)
        if status_code == 404:
            error_message = "La mascota solicitada no existe o ya no está disponible."
        else:
            error_message = f"Error al obtener datos de la API (código {status_code}). Por favor, intenta más tarde."
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al obtener datos de la API de Huachitos para mascota {pet_id}: {e}", exc_info=True)
        error_message = "No se pudo cargar la información de la mascota. Es posible que ya no esté disponible."
    except Exception as e:
        logger.error(f"Error inesperado en mascota_detail_view: {e}", exc_info=True)
        error_message = "Ocurrió un error inesperado. Por favor, intenta más tarde."

    context = {
        "mascota": pet,
        "error_message": error_message,
    }
    return render(request, "adoption/detail.html", context)
