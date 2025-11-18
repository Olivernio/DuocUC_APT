"""
Funciones helper reutilizables para el proyecto.
Incluye utilidades para queries optimizadas, cálculos comunes, etc.
"""
from django.core.cache import cache
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import timedelta


def get_cached_or_compute(cache_key, compute_func, timeout=300):
    """
    Obtiene un valor del caché o lo calcula si no existe.
    
    Args:
        cache_key: Clave única para el caché
        compute_func: Función que calcula el valor si no está en caché
        timeout: Tiempo de expiración en segundos (default: 5 minutos)
    
    Returns:
        El valor calculado o desde caché
    """
    value = cache.get(cache_key)
    if value is None:
        value = compute_func()
        cache.set(cache_key, value, timeout)
    return value


def get_month_sales_stats(month_start=None):
    """
    Obtiene estadísticas de ventas del mes.
    Optimiza queries usando select_related y agregaciones.
    
    Args:
        month_start: Fecha de inicio del mes (default: mes actual)
    
    Returns:
        dict con 'total_sales' y 'total_items'
    """
    from orders.models import Order, OrderItem
    
    if month_start is None:
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Optimizar query con select_related
    orders = Order.objects.filter(
        created_at__gte=month_start,
        status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']
    ).select_related('user')
    
    total_sales = orders.aggregate(total=Sum('total'))['total'] or 0
    
    # Optimizar query de items
    items = OrderItem.objects.filter(
        order__created_at__gte=month_start,
        order__status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']
    ).select_related('order', 'product')
    
    total_items = items.aggregate(total=Sum('quantity'))['total'] or 0
    
    return {
        'total_sales': float(total_sales),
        'total_items': int(total_items)
    }


def get_top_products(limit=10):
    """
    Obtiene los productos más vendidos.
    Optimiza la query usando select_related.
    
    Args:
        limit: Número de productos a retornar (default: 10)
    
    Returns:
        QuerySet optimizado con productos y cantidad vendida
    """
    from orders.models import OrderItem
    
    return OrderItem.objects.filter(
        order__status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']
    ).select_related('product', 'order').values(
        'product__name', 'product__id'
    ).annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:limit]


def get_low_stock_products(threshold=10):
    """
    Obtiene productos con stock bajo.
    Optimiza la query.
    
    Args:
        threshold: Umbral de stock bajo (default: 10)
    
    Returns:
        QuerySet de productos con stock bajo
    """
    from catalog.models import Product
    
    return Product.objects.filter(
        stock__lte=threshold,
        is_active=True
    ).select_related('category').order_by('stock')


def calculate_product_rating_stats(product):
    """
    Calcula estadísticas de rating para un producto.
    Optimiza usando agregaciones.
    
    Args:
        product: Instancia de Product
    
    Returns:
        dict con 'avg_rating', 'total_reviews', 'rating_distribution'
    """
    from catalog.models import ProductReview
    
    reviews = product.reviews.filter(is_approved=True)
    
    stats = reviews.aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id')
    )
    
    # Distribución de ratings
    rating_distribution = reviews.values('rating').annotate(
        count=Count('id')
    ).order_by('rating')
    
    return {
        'avg_rating': round(stats['avg_rating'] or 0, 1),
        'total_reviews': stats['total_reviews'] or 0,
        'rating_distribution': list(rating_distribution)
    }


def get_sales_by_period(start_date, end_date):
    """
    Obtiene ventas agrupadas por período.
    
    Args:
        start_date: Fecha de inicio
        end_date: Fecha de fin
    
    Returns:
        QuerySet optimizado con ventas por período
    """
    from orders.models import Order
    
    return Order.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date,
        status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']
    ).select_related('user').aggregate(
        total=Sum('total'),
        count=Count('id')
    )


def invalidate_cache_pattern(pattern):
    """
    Invalida todas las claves de caché que coincidan con un patrón.
    Útil para invalidar cachés relacionados.
    
    Args:
        pattern: Patrón de clave a invalidar (ej: 'dashboard_stats_*')
    
    Note:
        Esta función es básica. En producción, considera usar django-redis
        o similar para mejor soporte de patrones.
    """
    # Implementación básica - en producción usar django-redis
    # Por ahora, simplemente limpiamos todo el caché
    cache.clear()


def format_currency(amount, currency='CLP'):
    """
    Formatea un monto como moneda.
    
    Args:
        amount: Monto a formatear
        currency: Código de moneda (default: 'CLP')
    
    Returns:
        String formateado (ej: "$1.000")
    """
    if currency == 'CLP':
        return f"${int(amount):,}".replace(',', '.')
    return f"{currency} {amount:,.2f}"





