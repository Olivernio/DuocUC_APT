import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView 
from django.db.models import Sum, F, Value, DecimalField, Q
from django.db.models.functions import Coalesce 
from django.db import models 
from django.utils.translation import gettext_lazy as _

# --- Importaciones de Modelos ---
from django.contrib.auth.models import User # <-- ¡IMPORTANTE! Importamos el modelo User
from catalog.models import Product, Category
from adoption.models import Mascota, Especies, EstadoMascota, AdoptionRequest
from accounts.models import UserProfile
# --- Fin de Importaciones ---


# Vista del Dashboard Principal
@login_required
@user_passes_test(lambda u: u.is_staff)
def index(request):
    context = {
        'ventas_mes': 720000,
        'productos_vendidos': 200,
        'stock_bajo': Product.objects.filter(stock__lte=10, is_active=True).count(),
        'adopciones_count': Mascota.objects.filter(Estado=EstadoMascota.Adoptado).count()
    }
    return render(request, "dashboard/index.html", context)


# Vista de Inventario para el Dashboard
class DashboardInventoryListView(ListView):
    model = Product
    template_name = "dashboard/inventario.html" 
    context_object_name = "products"
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category_pk = self.request.GET.get('cat')
        if category_pk:
            queryset = queryset.filter(category=category_pk)
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                models.Q(name__icontains=query) |
                models.Q(sku__icontains=query)
            )
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = [
            {'pk': choice[0], 'name': choice[1]} 
            for choice in Category.choices
        ]
        context['category_selected'] = self.request.GET.get('cat', '')
        queryset = self.get_queryset() 
        total_value = queryset.aggregate(
            total=Coalesce(
                Sum(F('price') * F('stock')), 
                Value(0), 
                output_field=DecimalField()
            )
        )['total']
        low_stock_count = queryset.filter(stock__lte=10, is_active=True).count()
        context['total_inventory_value'] = total_value
        context['low_stock_count'] = low_stock_count
        return context


# Vista de Adopciones (API Huachitos) para el Dashboard
@login_required
@user_passes_test(lambda u: u.is_staff)
def dashboard_adopciones_api_view(request):
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
    query = request.GET.get("q", "").lower() 
    pets = []
    error_message = None

    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()  
        api_data = response.json()
        pets = api_data.get("data", [])

        if type_filter and type_filter in species_keys:
            pets = [pet for pet in pets if pet.get("tipo", "").lower() == type_filter]
        if query:
            pets = [
                pet for pet in pets 
                if query in pet.get("nombre", "").lower() or query in pet.get("raza", "").lower()
            ]
    except requests.exceptions.RequestException as e:
        print(f"ERROR fetching from Huachitos API (Dashboard): {e}")
        error_message = "No se pudo conectar con la API de Huachitos en este momento. Por favor, intenta más tarde."

    context = {
        "mascotas": pets,
        "especies_disponibles": species_for_display,
        "tipo_filtrado": type_filter,
        "query": query,
        "error_message": error_message,
        "disponibles_count": len(pets) 
    }
    return render(request, "dashboard/adopciones.html", context)


# Vista de Punto de Venta (POS)
class DashboardPOSView(ListView):
    model = Product
    template_name = "dashboard/pos.html"
    context_object_name = "products"
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True, stock__gt=0)
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                models.Q(name__icontains=query) |
                models.Q(sku__icontains=query)
            )
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# --- NUEVA VISTA DE GESTIÓN DE USUARIOS ---
class DashboardUserListView(ListView):
    model = User 
    template_name = "dashboard/usuarios.html" 
    context_object_name = "users"
    
    def get_queryset(self):
        queryset = super().get_queryset().order_by('username')
        
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                models.Q(username__icontains=query) |
                models.Q(email__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_users = self.model.objects.all()

        # --- Estadísticas Globales (de la captura) ---
        context['global_total_pedidos'] = 2
        context['global_ingresos_totales'] = 166
        context['global_adopciones'] = 1
        context['global_reseñas'] = 3
        
        # Estadísticas de la lista
        context['total_users'] = all_users.count()
        context['staff_users'] = all_users.filter(is_staff=True).count()
        context['active_users'] = all_users.filter(is_active=True).count()

        # --- Lógica para el Usuario Seleccionado ---
        selected_user_id = self.request.GET.get('selected')
        
        if selected_user_id:
            try:
                selected_user = get_object_or_404(User, pk=selected_user_id)
                
                # Esta línea necesita la importación de UserProfile para funcionar
                user_profile, created = UserProfile.objects.get_or_create(user=selected_user)
                
                context['selected_user'] = selected_user
                
                context['selected_user_stats'] = {
                    'pedidos': 1,
                    'total_gastado': 76,
                    'adopciones': 1,
                    'reseñas': 2,
                }
            except Exception as e:
                # Si faltaba la importación, aquí es donde saltaba el error
                print(f"ERROR al obtener el perfil del usuario: {e}") # Añadimos un print para depurar
                context['selected_user'] = None
        
        return context
# --- FIN DE LA VISTA DE USUARIOS ---