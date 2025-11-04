from django.shortcuts import render

def about(request):
    return render(request, "acerca/about.html")

# --- AÑADE ESTO ---
def accessibility(request):
    # Simplemente renderiza la plantilla que crearemos en el Paso 3
    return render(request, "accessibility/accessibility.html")
# --- FIN DE LO AÑADIDO ---