# Dashboard Views - PetStorePOS

import requests
import json
import csv
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView 
from django.db.models import Sum, F, Value, DecimalField, Q, Count
from django.db.models.functions import Coalesce 
from django.db import models
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)
from django.http import HttpResponse

from django.contrib.auth.models import User 
from catalog.models import Product, Category, ProductReview
from adoption.models import Mascota, Especies, EstadoMascota, AdoptionRequest
from accounts.models import UserProfile
from django.core.paginator import Paginator

@login_required
@user_passes_test(lambda u: u.is_staff)
def index(request):
    from orders.models import Order, OrderItem
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Sum, Count, Q
    from catalog.models import ProductReview
    from core.utils import get_cached_or_compute, get_month_sales_stats, get_top_products, get_low_stock_products
    
    # Fecha actual y hace 6 meses
    now = timezone.now()
    six_months_ago = now - timedelta(days=180)
    
    # Ventas del mes actual (con caché)
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    def compute_month_stats():
        return get_month_sales_stats(current_month_start)
    
    month_stats = get_cached_or_compute(
        f'dashboard_month_stats_{current_month_start.strftime("%Y%m")}',
        compute_month_stats,
        timeout=300  # 5 minutos
    )
    
    ventas_mes = month_stats['total_sales']
    productos_vendidos = month_stats['total_items']
    
    # Stock bajo (con caché)
    def compute_low_stock():
        return get_low_stock_products(threshold=10).count()
    
    stock_bajo = get_cached_or_compute(
        'dashboard_low_stock_count',
        compute_low_stock,
        timeout=600  # 10 minutos
    )
    
    # Adopciones (solicitudes procesadas - más preciso que contar mascotas con estado "Adoptado")
    def compute_adoptions():
        return AdoptionRequest.objects.filter(processed=True).count()
    
    adopciones_count = get_cached_or_compute(
        'dashboard_adoptions_count',
        compute_adoptions,
        timeout=600  # 10 minutos
    )
    
    # Datos para gráficos
    # Ventas por mes (últimos 6 meses)
    sales_by_month = []
    months_labels = []
    for i in range(5, -1, -1):  # Últimos 6 meses
        month_start = (now - timedelta(days=30*i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i == 0:
            month_end = now
        else:
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        month_sales = Order.objects.filter(
            created_at__gte=month_start,
            created_at__lte=month_end,
            status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']
        ).aggregate(total=Sum('total'))['total'] or 0
        
        sales_by_month.append(float(month_sales))
        months_labels.append(month_start.strftime('%b %Y'))
    
    # Productos más vendidos (top 10) - optimizado con helper
    def compute_top_products():
        products = get_top_products(limit=10)
        return {
            'names': [p['product__name'] for p in products],
            'quantities': [p['total_sold'] for p in products]
        }
    
    top_products_data = get_cached_or_compute(
        'dashboard_top_products',
        compute_top_products,
        timeout=600  # 10 minutos
    )
    
    top_products_names = top_products_data.get('names', [])
    top_products_quantities = top_products_data.get('quantities', [])
    
    # Adopciones por especie (basado en solicitudes procesadas)
    adopciones_por_especie = AdoptionRequest.objects.filter(
        processed=True
    ).select_related('Mascota').values('Mascota__Especie').annotate(
        count=Count('id')
    )
    
    # Obtener el display name de cada especie
    from adoption.models import Especies
    especies_dict = dict(Especies.choices)
    especies_labels = []
    especies_counts = []
    for a in adopciones_por_especie:
        especie_key = a.get('Mascota__Especie', '')
        if especie_key:
            especies_labels.append(str(especies_dict.get(especie_key, especie_key)))
            especies_counts.append(int(a.get('count', 0)))
    
    # Stock por categoría
    stock_por_categoria = Product.objects.filter(is_active=True).values('category').annotate(
        total_stock=Sum('stock')
    )
    
    categorias_dict = dict(Category.choices)
    categorias_labels = []
    categorias_stock = []
    for s in stock_por_categoria:
        categoria_key = s.get('category', '')
        if categoria_key:
            categorias_labels.append(str(categorias_dict.get(categoria_key, categoria_key)))
            categorias_stock.append(int(s.get('total_stock', 0)))
    
    try:
        context = {
            'ventas_mes': float(ventas_mes),
            'productos_vendidos': int(productos_vendidos),
            'stock_bajo': stock_bajo,
            'adopciones_count': adopciones_count,
            'sales_by_month': json.dumps(sales_by_month) if sales_by_month else '[]',
            'months_labels': json.dumps([str(m) for m in months_labels]) if months_labels else '[]',
            'top_products_names': json.dumps([str(n) for n in top_products_names]) if top_products_names else '[]',
            'top_products_quantities': json.dumps([int(q) for q in top_products_quantities]) if top_products_quantities else '[]',
            'especies_labels': json.dumps(especies_labels) if especies_labels else '[]',
            'especies_counts': json.dumps([int(c) for c in especies_counts]) if especies_counts else '[]',
            'categorias_labels': json.dumps(categorias_labels) if categorias_labels else '[]',
            'categorias_stock': json.dumps(categorias_stock) if categorias_stock else '[]',
        }
        return render(request, "dashboard/index.html", context)
    except Exception as e:
        logger.error(f"Error en dashboard index: {str(e)}", exc_info=True)
        from django.contrib import messages
        messages.error(request, f"Error al cargar el dashboard: {str(e)}")
        context = {
            'ventas_mes': 0,
            'productos_vendidos': 0,
            'stock_bajo': 0,
            'adopciones_count': 0,
            'sales_by_month': '[]',
            'months_labels': '[]',
            'top_products_names': '[]',
            'top_products_quantities': '[]',
            'especies_labels': '[]',
            'especies_counts': '[]',
            'categorias_labels': '[]',
            'categorias_stock': '[]',
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
        # Obtener el carrito del usuario
        from cart.utils import get_or_create_cart
        cart = get_or_create_cart(self.request)
        context['cart'] = cart
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
        
        # Anotar estadísticas para cada usuario
        from orders.models import Order
        from django.db.models import Sum, Count, Q
        
        queryset = queryset.annotate(
            total_orders=Count('orders', filter=Q(orders__status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED'])),
            total_spent=Sum('orders__total', filter=Q(orders__status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']))
        )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener la pestaña activa desde los parámetros GET
        context['active_tab'] = self.request.GET.get('tab', 'resumen')
        all_users = self.model.objects.all()

        # --- Estadísticas Globales (calculadas en tiempo real) ---
        from orders.models import Order
        from adoption.models import AdoptionRequest
        
        # Total de pedidos
        context['global_total_pedidos'] = Order.objects.count()
        
        # Ingresos totales (suma de todos los pedidos confirmados/completados)
        total_revenue = Order.objects.filter(
            status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']
        ).aggregate(total=Sum('total'))['total'] or 0
        context['global_ingresos_totales'] = int(total_revenue)
        
        # Total de adopciones (solicitudes procesadas)
        context['global_adopciones'] = AdoptionRequest.objects.filter(
            processed=True
        ).count()
        
        # Total de reseñas
        context['global_reseñas'] = ProductReview.objects.count()
        
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
                
                # Calcular estadísticas reales del usuario
                from orders.models import Order, OrderItem
                
                # Pedidos del usuario
                user_orders = Order.objects.filter(user=selected_user)
                total_orders = user_orders.filter(
                    status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']
                ).count()
                
                # Total gastado
                total_spent = user_orders.filter(
                    status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']
                ).aggregate(total=Sum('total'))['total'] or 0
                
                # Adopciones del usuario
                user_adoptions = AdoptionRequest.objects.filter(
                    email=selected_user.email,
                    processed=True
                ).count()
                
                # Reseñas del usuario
                user_reviews = ProductReview.objects.filter(user=selected_user).count()
                
                context['selected_user_stats'] = {
                    'pedidos': total_orders,
                    'total_gastado': int(total_spent),
                    'adopciones': user_adoptions,
                    'reseñas': user_reviews,
                }
                
                # Datos para las pestañas
                # Compras
                context['user_orders'] = user_orders.select_related().order_by('-created_at')[:20]
                
                # Reseñas
                context['user_reviews'] = ProductReview.objects.filter(
                    user=selected_user
                ).select_related('product').order_by('-created_at')
                
                # Mascotas (adopciones)
                context['user_adoptions'] = AdoptionRequest.objects.filter(
                    email=selected_user.email
                ).select_related('Mascota').order_by('-created_at')
            except Exception as e:
                # Si faltaba la importación, aquí es donde saltaba el error
                print(f"ERROR al obtener el perfil del usuario: {e}") # Añadimos un print para depurar
                context['selected_user'] = None
        
        return context
# --- FIN DE LA VISTA DE USUARIOS ---


# --- EXPORTACIÓN DE DATOS A CSV ---
@login_required
@user_passes_test(lambda u: u.is_staff)
def export_products_csv(request):
    """Exporta todos los productos a CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="productos_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['SKU', 'Nombre', 'Categoría', 'Precio', 'Stock', 'Activo', 'Fecha Creación'])
    
    products = Product.objects.all().order_by('name')
    for product in products:
        writer.writerow([
            product.sku,
            product.name,
            product.get_category_display(),
            product.price,
            product.stock,
            'Sí' if product.is_active else 'No',
            product.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response


@login_required
@user_passes_test(lambda u: u.is_staff)
def export_orders_csv(request):
    """Exporta todas las órdenes a CSV"""
    from orders.models import Order
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="pedidos_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Número de Orden', 'Usuario', 'Email', 'Total', 'Estado', 'Fecha Creación'])
    
    orders = Order.objects.select_related('user').all().order_by('-created_at')
    for order in orders:
        writer.writerow([
            order.order_number,
            order.user.username,
            order.user.email,
            order.total,
            order.get_status_display(),
            order.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response


@login_required
@user_passes_test(lambda u: u.is_staff)
def export_users_csv(request):
    """Exporta todos los usuarios a CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="usuarios_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Nombre', 'Apellido', 'Fecha Registro', 'Es Staff', 'Activo'])
    
    users = User.objects.all().order_by('username')
    for user in users:
        writer.writerow([
            user.username,
            user.email,
            user.first_name,
            user.last_name,
            user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
            'Sí' if user.is_staff else 'No',
            'Sí' if user.is_active else 'No'
        ])
    
    return response
# --- FIN DE EXPORTACIÓN CSV ---


# --- VISTA DE GESTIÓN DE RESEÑAS ---
@login_required
@user_passes_test(lambda u: u.is_staff)
def reviews_management(request):
    """
    Vista para gestionar reseñas desde el dashboard.
    Permite aprobar/rechazar reseñas pendientes.
    """
    from django.contrib import messages
    from django.shortcuts import redirect
    from accounts.utils import notify_review_approved
    
    # Manejar acciones POST
    if request.method == 'POST':
        action = request.POST.get('action')
        review_id = request.POST.get('review_id')
        
        if action and review_id:
            try:
                review = get_object_or_404(ProductReview, id=review_id)
                
                if action == 'approve':
                    review.is_approved = True
                    review.save()
                    # Notificar al usuario
                    try:
                        notify_review_approved(review.user, review)
                    except Exception as e:
                        logger.warning(f"Error al notificar aprobación de reseña: {str(e)}")
                    messages.success(request, f"Reseña de {review.user.username} aprobada exitosamente.")
                elif action == 'reject':
                    review.is_approved = False
                    review.save()
                    messages.success(request, f"Reseña de {review.user.username} rechazada.")
                elif action == 'delete':
                    product_name = review.product.name
                    review.delete()
                    messages.success(request, f"Reseña eliminada exitosamente.")
                
            except Exception as e:
                messages.error(request, f"Error al procesar la acción: {str(e)}")
        
        return redirect('dashboard:reviews')
    
    # Obtener filtros
    filter_status = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '')
    
    # Construir queryset
    reviews = ProductReview.objects.select_related('product', 'user').all()
    
    # Aplicar filtros
    if filter_status == 'pending':
        reviews = reviews.filter(is_approved=False)
    elif filter_status == 'approved':
        reviews = reviews.filter(is_approved=True)
    
    # Búsqueda
    if search_query:
        reviews = reviews.filter(
            Q(product__name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(comment__icontains=search_query)
        )
    
    # Ordenar por fecha (más recientes primero)
    reviews = reviews.order_by('-created_at')
    
    # Estadísticas
    total_reviews = ProductReview.objects.count()
    pending_reviews = ProductReview.objects.filter(is_approved=False).count()
    approved_reviews = ProductReview.objects.filter(is_approved=True).count()
    
    context = {
        'reviews': reviews,
        'total_reviews': total_reviews,
        'pending_reviews': pending_reviews,
        'approved_reviews': approved_reviews,
        'filter_status': filter_status,
        'search_query': search_query,
    }
    
    return render(request, 'dashboard/reviews.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def configuracion(request):
    """
    Vista de configuración del sistema
    """
    import sys
    from django.conf import settings
    from django import get_version as django_get_version
    from catalog.models import Product, Category
    from orders.models import Order
    from accounts.models import UserProfile
    from adoption.models import AdoptionRequest
    
    # Estadísticas del sistema
    total_products = Product.objects.count()
    total_categories = len(Category.choices)
    total_orders = Order.objects.count()
    total_users = UserProfile.objects.count()
    total_adoptions = AdoptionRequest.objects.filter(processed=True).count()
    
    # Configuración del sistema
    system_config = {
        'debug_mode': settings.DEBUG,
        'timezone': settings.TIME_ZONE,
        'language_code': settings.LANGUAGE_CODE,
        'allowed_languages': [lang[0] for lang in settings.LANGUAGES],
    }
    
    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_orders': total_orders,
        'total_users': total_users,
        'total_adoptions': total_adoptions,
        'system_config': system_config,
        'django_version': django_get_version(),
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }
    
    return render(request, 'dashboard/configuracion.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def dashboard_accessibility(request):
    """
    Vista de accesibilidad integrada en el Dashboard
    """
    return render(request, 'dashboard/accessibility.html')


@login_required
@user_passes_test(lambda u: u.is_staff)
def dashboard_pedidos(request):
    """
    Vista para gestionar pedidos dentro del Dashboard.
    """
    from orders.models import Order, OrderStatus
    
    orders = Order.objects.all().select_related('user').prefetch_related('items__product')
    
    # Filtros
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Búsqueda por número de orden o usuario
    search = request.GET.get('search', '')
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    # Ordenar por fecha más reciente primero
    orders = orders.order_by('-created_at')
    
    # Paginación
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'orders': page_obj,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search': search,
        'status_choices': OrderStatus.choices,
    }
    return render(request, 'dashboard/pedidos.html', context)