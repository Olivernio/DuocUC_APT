"""
Template tags para breadcrumbs (migas de pan).
"""
from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()


@register.inclusion_tag('core/breadcrumbs.html', takes_context=True)
def breadcrumbs(context, *args):
    """
    Genera breadcrumbs basado en la URL actual y argumentos opcionales.
    
    Uso:
        {% load breadcrumbs %}
        {% breadcrumbs "Inicio" "Productos" "Detalle" %}
    
    O automático basado en la URL:
        {% breadcrumbs %}
    """
    request = context.get('request')
    breadcrumb_items = []
    
    # Si se proporcionan argumentos, usarlos
    if args:
        for i, item in enumerate(args):
            breadcrumb_items.append({
                'name': item,
                'url': None if i == len(args) - 1 else '#',  # Último sin URL
                'active': i == len(args) - 1
            })
    else:
        # Generar automáticamente basado en la URL
        if request:
            path_parts = request.path.strip('/').split('/')
            current_path = ''
            
            for i, part in enumerate(path_parts):
                if part:
                    current_path += '/' + part
                    is_last = i == len(path_parts) - 1
                    
                    # Nombres amigables
                    name = part.replace('-', ' ').replace('_', ' ').title()
                    
                    # Mapeo de nombres comunes
                    name_mapping = {
                        'catalog': 'Catálogo',
                        'product': 'Producto',
                        'orders': 'Pedidos',
                        'order': 'Pedido',
                        'accounts': 'Cuenta',
                        'favorites': 'Favoritos',
                        'notifications': 'Notificaciones',
                        'adoption': 'Adopción',
                        'dashboard': 'Panel',
                        'cart': 'Carrito',
                        'checkout': 'Checkout',
                    }
                    
                    if part in name_mapping:
                        name = name_mapping[part]
                    
                    breadcrumb_items.append({
                        'name': name,
                        'url': current_path if not is_last else None,
                        'active': is_last
                    })
    
    # Agregar "Inicio" al principio si no está
    if not breadcrumb_items or breadcrumb_items[0]['name'].lower() != 'inicio':
        try:
            home_url = reverse('home')
            breadcrumb_items.insert(0, {
                'name': 'Inicio',
                'url': home_url,
                'active': False
            })
        except NoReverseMatch:
            breadcrumb_items.insert(0, {
                'name': 'Inicio',
                'url': '/',
                'active': False
            })
    
    return {
        'breadcrumb_items': breadcrumb_items
    }





