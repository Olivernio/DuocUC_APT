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
    """
    Dashboard principal con estadísticas reales calculadas desde la base de datos.
    """
    from datetime import datetime
    from orders.models import Order, OrderItem, OrderStatus
    
    # Obtener el primer día del mes actual
    today = datetime.now()
    first_day_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # 1. VENTAS DEL MES ACTUAL (suma de todas las órdenes confirmadas/entregadas)
    try:
        sales_this_month = Order.objects.filter(
            created_at__gte=first_day_month,  # Desde el primer día del mes
            status__in=[
                OrderStatus.CONFIRMED,
                OrderStatus.PROCESSING,
                OrderStatus.SHIPPED,
                OrderStatus.DELIVERED
            ]
        ).aggregate(total=Sum('total'))['total'] or 0
    except Exception as e:
        # Si hay error (por ejemplo, si no existe la tabla), usar 0
        sales_this_month = 0
        if request.user.is_staff and request.user.is_superuser:
            print(f"Error calculando ventas: {e}")
    
    # 2. PRODUCTOS VENDIDOS ESTE MES (suma de cantidades de OrderItems)
    try:
        products_sold_this_month = OrderItem.objects.filter(
            order__created_at__gte=first_day_month,
            order__status__in=[
                OrderStatus.CONFIRMED,
                OrderStatus.PROCESSING,
                OrderStatus.SHIPPED,
                OrderStatus.DELIVERED
            ]
        ).aggregate(total=Sum('quantity'))['total'] or 0
    except Exception as e:
        products_sold_this_month = 0
        if request.user.is_staff and request.user.is_superuser:
            print(f"Error calculando productos vendidos: {e}")
    
    # 3. STOCK BAJO (ya lo tenías, pero lo mantenemos)
    stock_bajo = Product.objects.filter(stock__lte=10, is_active=True).count()
    
    # 4. ADOPCIONES (ya lo tenías)
    adopciones_count = Mascota.objects.filter(Estado=EstadoMascota.Adoptado).count()
    
    # 5. PRODUCTOS MÁS VENDIDOS (top 5 para mostrar en el dashboard)
    try:
        top_products = OrderItem.objects.values(
            'product__name',  # Nombre del producto
            'product__sku'    # SKU del producto
        ).annotate(
            total_sold=Sum('quantity')  # Suma las cantidades
        ).order_by('-total_sold')[:5]  # Ordena descendente, toma 5
    except Exception as e:
        top_products = []
        if request.user.is_staff and request.user.is_superuser:
            print(f"Error calculando top productos: {e}")
    
    # 6. ÓRDENES RECIENTES (últimas 5 órdenes)
    try:
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    except Exception as e:
        recent_orders = []
        if request.user.is_staff and request.user.is_superuser:
            print(f"Error obteniendo órdenes recientes: {e}")
    
    # 7. PRODUCTOS CON STOCK BAJO (lista completa, no solo el count)
    low_stock_products = Product.objects.filter(
        stock__lte=10,
        is_active=True
    ).order_by('stock')[:10]  # Los 10 con menos stock
    
    context = {
        'ventas_mes': sales_this_month,
        'productos_vendidos': products_sold_this_month,
        'stock_bajo': stock_bajo,
        'adopciones_count': adopciones_count,
        'top_products': top_products,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
        'month_name': today.strftime('%B %Y'),  # Nombre del mes para mostrar
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