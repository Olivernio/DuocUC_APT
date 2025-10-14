import requests
from django.shortcuts import render

def mascotas_huachitos_view(request):
    """
    Fetches pet data from the Huachitos.cl API and displays it.
    Allows filtering by animal type (especie).
    """
    api_url = "https://huachitos.cl/api/animales/"
    
    # Available species for filtering
    available_species = ["perro", "gato", "conejo", "roedor", "ave"]
    
    # Get the animal type from the query string
    type_filter = request.GET.get("tipo", "").lower()

    pets = []
    error_message = None

    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()  # Raise an error for 4xx/5xx responses
        
        api_data = response.json()
        pets = api_data.get("data", [])

        # Filter pets if a valid type is specified
        if type_filter and type_filter in available_species:
            pets = [pet for pet in pets if pet.get("tipo", "").lower() == type_filter]

    except requests.exceptions.RequestException as e:
        # In case of an API error, show an empty list and a message
        print(f"ERROR fetching from Huachitos API: {e}")
        error_message = "No se pudo conectar con la API de Huachitos en este momento. Por favor, intenta más tarde."

    context = {
        "mascotas": pets,
        "especies_disponibles": available_species,
        "tipo_filtrado": type_filter,
        "error_message": error_message,
    }
    return render(request, "adoption/list.html", context)


def mascota_detail_view(request, pet_id):
    """
    Fetches detailed data for a single pet from the Huachitos.cl API.
    """
    api_url = f"https://huachitos.cl/api/animal/{pet_id}"
    
    pet = None
    error_message = None

    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        
        api_data = response.json()
        pet = api_data.get("data")

    except requests.exceptions.RequestException as e:
        print(f"ERROR fetching from Huachitos API for pet {pet_id}: {e}")
        error_message = "No se pudo cargar la información de la mascota. Es posible que ya no esté disponible."

    context = {
        "mascota": pet,
        "error_message": error_message,
    }
    return render(request, "adoption/detail.html", context)