from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from cart.utils import get_or_create_cart
from catalog.models import Product
from .models import Order, OrderItem, OrderStatus
from .forms import CheckoutForm


@login_required
def checkout_view(request):
    """
    Vista de checkout: muestra el formulario y procesa la orden.
    
    ¿Qué hace?
    1. Verifica que el usuario tenga productos en el carrito
    2. Muestra el formulario de checkout
    3. Valida el stock antes de crear la orden
    4. Crea la orden y los OrderItems
    5. Reduce el stock de los productos
    6. Limpia el carrito
    7. Redirige a la confirmación
    """
    cart = get_or_create_cart(request)
    
    # Verificar que el carrito no esté vacío
    if not cart.items.exists():
        messages.warning(request, _("Tu carrito está vacío."))
        return redirect('cart:cart_detail')
    
    # Verificar stock antes de mostrar el formulario
    for item in cart.items.all():
        if item.product.stock < item.quantity:
            messages.error(
                request, 
                _("El producto '{}' no tiene suficiente stock. Stock disponible: {}").format(
                    item.product.name, item.product.stock
                )
            )
            return redirect('cart:cart_detail')
    
    # Si es POST, procesar la orden
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        
        if form.is_valid():
            try:
                # Usar transacción para asegurar que todo se guarde o nada
                with transaction.atomic():
                    # Calcular el total del carrito
                    total = sum(item.product.price * item.quantity for item in cart.items.all())
                    
                    # Crear la orden
                    order = Order.objects.create(
                        user=request.user,
                        status=OrderStatus.PENDING,
                        shipping_address=form.cleaned_data['shipping_address'],
                        shipping_city=form.cleaned_data['shipping_city'],
                        shipping_postal_code=form.cleaned_data.get('shipping_postal_code', ''),
                        notes=form.cleaned_data.get('notes', ''),
                        total=total
                    )
                    
                    # Crear los OrderItems y reducir stock
                    for cart_item in cart.items.all():
                        # Verificar stock nuevamente antes de crear
                        if cart_item.product.stock < cart_item.quantity:
                            raise ValueError(
                                _("Stock insuficiente para '{}'").format(cart_item.product.name)
                            )
                        
                        # Crear OrderItem
                        OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            quantity=cart_item.quantity,
                            price=cart_item.product.price
                        )
                        
                        # Reducir stock del producto
                        cart_item.product.stock -= cart_item.quantity
                        cart_item.product.save()
                    
                    # Limpiar el carrito
                    cart.items.all().delete()
                
                # Crear notificación para el usuario
                try:
                    from accounts.utils import notify_order_created
                    notify_order_created(request.user, order)
                except Exception as e:
                    # Si hay error al crear notificación, no fallar la orden
                    if request.user.is_staff:
                        print(f"Error creando notificación: {e}")
                
                # Si todo salió bien, redirigir a confirmación
                messages.success(
                    request, 
                    _("¡Orden creada exitosamente! Número de orden: {}").format(order.order_number)
                )
                return redirect('orders:order_detail', order_id=order.id)
                
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, _("Ocurrió un error al procesar tu orden. Por favor intenta nuevamente."))
                if request.user.is_staff:
                    messages.error(request, f"Error técnico: {str(e)}")
    else:
        # Si es GET, mostrar el formulario
        form = CheckoutForm()
    
    # Calcular totales para mostrar en el template
    context = {
        'form': form,
        'cart': cart,
        'total': sum(item.product.price * item.quantity for item in cart.items.all())
    }
    
    return render(request, 'orders/checkout.html', context)


@login_required
def order_detail_view(request, order_id):
    """
    Vista de detalle de una orden específica.
    Solo el usuario dueño de la orden puede verla.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
        'items': order.items.all()
    }
    
    return render(request, 'orders/order_detail.html', context)


@login_required
def order_list_view(request):
    """
    Vista de historial de pedidos del usuario.
    Muestra todas las órdenes del usuario logueado.
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders
    }
    
    return render(request, 'orders/order_list.html', context)


@login_required
def admin_order_list_view(request):
    """
    Vista de gestión de pedidos para administradores.
    Solo usuarios con is_staff=True pueden acceder.
    """
    from django.contrib.auth.decorators import user_passes_test
    
    if not request.user.is_staff:
        messages.error(request, _("No tienes permisos para acceder a esta página."))
        return redirect('home')
    
    # Filtrar por estado si se proporciona
    status_filter = request.GET.get('status', '')
    orders = Order.objects.all().select_related('user').order_by('-created_at')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Estadísticas rápidas
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status=OrderStatus.PENDING).count()
    confirmed_orders = Order.objects.filter(status=OrderStatus.CONFIRMED).count()
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'status_choices': OrderStatus.choices,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
    }
    
    return render(request, 'orders/admin_order_list.html', context)


@login_required
def admin_order_detail_view(request, order_id):
    """
    Vista de detalle de orden para administradores.
    Permite cambiar el estado de la orden.
    """
    if not request.user.is_staff:
        messages.error(request, _("No tienes permisos para acceder a esta página."))
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id)
    
    # Si es POST, cambiar el estado
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(OrderStatus.choices):
            old_status = order.status
            order.status = new_status
            order.save()
            
            # Crear notificación para el usuario dueño de la orden
            try:
                from accounts.utils import notify_order_updated
                notify_order_updated(order.user, order, old_status, new_status)
            except Exception as e:
                # Si hay error al crear notificación, no fallar el cambio de estado
                if request.user.is_staff:
                    print(f"Error creando notificación: {e}")
            
            messages.success(
                request, 
                _("Estado de la orden #{} cambiado de {} a {}").format(
                    order.order_number,
                    order.get_status_display(),
                    dict(OrderStatus.choices)[new_status]
                )
            )
            return redirect('orders:admin_order_detail', order_id=order.id)
        else:
            messages.error(request, _("Estado inválido."))
    
    context = {
        'order': order,
        'items': order.items.all(),
        'status_choices': OrderStatus.choices,
    }
    
    return render(request, 'orders/admin_order_detail.html', context)