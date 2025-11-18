from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from cart.models import Cart, CartItem
from catalog.models import Product
from .models import Order, OrderItem, OrderStatus
from .forms import CheckoutForm, OrderStatusUpdateForm

# Importaciones opcionales para cupones (pueden no existir si las migraciones no se han aplicado)
# Los modelos siempre están definidos, pero las tablas pueden no existir
try:
    from .models import Coupon, OrderCoupon
    from .forms import CouponForm
    COUPONS_AVAILABLE = True
except (ImportError, AttributeError):
    # Si hay error al importar, crear formulario fallback
    from django import forms
    class CouponForm(forms.Form):
        coupon_code = forms.CharField(required=False, widget=forms.HiddenInput())
    COUPONS_AVAILABLE = False


@login_required
def checkout_view(request):
    """
    Vista para mostrar el formulario de checkout y procesar la orden.
    """
    cart = get_or_create_cart(request)
    
    # Verificar que el carrito tenga items
    if not cart.items.exists():
        messages.warning(request, _("Tu carrito está vacío. Agrega productos antes de proceder al pago."))
        return redirect('cart:cart_detail')
    
    # Validar stock antes de mostrar checkout
    errors = []
    for item in cart.items.all():
        if item.quantity > item.product.stock:
            errors.append(_("El producto '{}' no tiene suficiente stock. Stock disponible: {}").format(
                item.product.name, item.product.stock
            ))
        if not item.product.is_active:
            errors.append(_("El producto '{}' no está disponible.").format(item.product.name))
    
    if errors:
        for error in errors:
            messages.error(request, error)
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        
        # Intentar crear el formulario de cupón, pero si falla (tabla no existe), usar uno vacío
        if COUPONS_AVAILABLE:
            try:
                coupon_form = CouponForm(request.POST)
            except Exception:
                # Si hay error al crear el formulario (tabla no existe), crear uno vacío
                from django.forms import Form
                coupon_form = Form(request.POST)
        else:
            from django.forms import Form
            coupon_form = Form(request.POST)
        
        if form.is_valid():
            # Validar cupón ANTES del bloque atómico para evitar errores dentro de la transacción
            discount_amount = 0
            applied_coupon = None
            
            if COUPONS_AVAILABLE:
                try:
                    if hasattr(coupon_form, 'is_valid') and coupon_form.is_valid():
                        coupon_code = coupon_form.cleaned_data.get('coupon_code')
                        if coupon_code:
                            applied_coupon = coupon_code
                except Exception:
                    # Error al validar cupón, continuar sin cupón
                    pass
            
            try:
                with transaction.atomic():
                    # Calcular total inicial
                    total = sum(item.product.price * item.quantity for item in cart.items.all())
                    
                    # Aplicar descuento del cupón si existe
                    if applied_coupon:
                        try:
                            discount_amount, total = applied_coupon.calculate_discount(total)
                        except Exception:
                            # Error al calcular descuento, continuar sin descuento
                            discount_amount = 0
                            applied_coupon = None
                    
                    # Crear la orden
                    order = Order.objects.create(
                        user=request.user,
                        status=OrderStatus.PENDING,
                        shipping_address=form.cleaned_data['shipping_address'],
                        shipping_city=form.cleaned_data['shipping_city'],
                        shipping_postal_code=form.cleaned_data.get('shipping_postal_code', ''),
                        notes=form.cleaned_data.get('notes', ''),
                        total=total  # Total con descuento aplicado
                    )
                    
                    # Crear los items de la orden y reducir stock
                    for cart_item in cart.items.all():
                        # Validar stock nuevamente antes de crear la orden
                        if cart_item.quantity > cart_item.product.stock:
                            raise ValueError(_("El producto '{}' no tiene suficiente stock.").format(cart_item.product.name))
                        
                        # Crear OrderItem
                        OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            quantity=cart_item.quantity,
                            price=cart_item.product.price
                        )
                        
                        # Reducir stock
                        cart_item.product.stock -= cart_item.quantity
                        cart_item.product.save()
                    
                    # Aplicar cupón si existe (dentro de la transacción)
                    if applied_coupon and COUPONS_AVAILABLE:
                        try:
                            from django.db.utils import OperationalError
                            if OrderCoupon:
                                OrderCoupon.objects.create(
                                    order=order,
                                    coupon=applied_coupon,
                                    discount_amount=discount_amount
                                )
                                applied_coupon.apply()  # Incrementar contador de uso
                        except (OperationalError, Exception):
                            # Si la tabla no existe o hay otro error, continuar sin guardar el cupón
                            pass
                    
                    # Limpiar carrito (dentro de la transacción)
                    cart.items.all().delete()
                
                # Crear notificación FUERA del bloque atómico para evitar problemas
                try:
                    from accounts.utils import notify_order_created
                    notify_order_created(request.user, order)
                except Exception:
                    # Si hay error con notificaciones, continuar sin crear notificación
                    pass
                
                success_msg = _("¡Orden creada exitosamente! Número de orden: {}").format(order.order_number)
                if applied_coupon:
                    success_msg += _(" Descuento aplicado: ${}").format(discount_amount)
                messages.success(request, success_msg)
                return redirect('orders:order_detail', order_id=order.id)
                    
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('cart:cart_detail')
            except Exception as e:
                # En modo DEBUG, mostrar el error real para diagnóstico
                from django.conf import settings
                error_msg = _("Ocurrió un error al procesar tu orden. Por favor, intenta nuevamente.")
                if settings.DEBUG:
                    error_msg += f" Error: {str(e)}"
                    # También imprimir en consola para debugging
                    import traceback
                    print("=" * 50)
                    print("ERROR EN CHECKOUT:")
                    print(traceback.format_exc())
                    print("=" * 50)
                messages.error(request, error_msg)
                # Log del error para debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error en checkout: {str(e)}", exc_info=True)
                return redirect('cart:cart_detail')
    else:
        form = CheckoutForm()
        # Intentar crear el formulario de cupón, pero si falla, usar uno vacío
        if COUPONS_AVAILABLE:
            try:
                coupon_form = CouponForm()
            except Exception:
                # Si hay error (tabla no existe), crear un formulario vacío
                from django.forms import Form
                coupon_form = Form()
        else:
            from django.forms import Form
            coupon_form = Form()
    
    # Calcular totales para mostrar en el template
    subtotal = sum(item.product.price * item.quantity for item in cart.items.all())
    
    context = {
        'form': form,
        'coupon_form': coupon_form,
        'cart': cart,
        'subtotal': subtotal,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def order_list(request):
    """
    Vista para listar las órdenes del usuario actual.
    """
    orders = Order.objects.filter(user=request.user).select_related('user').prefetch_related('items__product')
    
    # Paginación
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'orders': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail(request, order_id):
    """
    Vista para ver el detalle de una orden específica.
    """
    from django.db.utils import OperationalError
    
    # Intentar obtener la orden con prefetch de cupones
    try:
        order = get_object_or_404(
            Order.objects.select_related('user').prefetch_related('items__product', 'applied_coupons__coupon'),
            id=order_id,
            user=request.user
        )
    except OperationalError:
        # Si la tabla de cupones no existe, obtener sin prefetch de cupones
        order = get_object_or_404(
            Order.objects.select_related('user').prefetch_related('items__product'),
            id=order_id,
            user=request.user
        )
    
    # Calcular subtotal (total + descuento si existe)
    subtotal = order.total
    discount_amount = 0
    try:
        if hasattr(order, 'applied_coupons') and order.applied_coupons.exists():
            coupon_applied = order.applied_coupons.first()
            discount_amount = coupon_applied.discount_amount
            subtotal = order.total + discount_amount
    except (OperationalError, AttributeError):
        # Si la tabla no existe o no hay relación, usar valores por defecto
        pass
    
    context = {
        'order': order,
        'subtotal': subtotal,
        'discount_amount': discount_amount,
    }
    return render(request, 'orders/order_detail.html', context)


@staff_member_required
def admin_order_list(request):
    """
    Vista para que el admin gestione todas las órdenes.
    """
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
    return render(request, 'orders/admin_order_list.html', context)


@staff_member_required
def admin_order_detail(request, order_id):
    """
    Vista para que el admin vea el detalle completo de una orden.
    """
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('items__product'),
        id=order_id
    )
    
    if request.method == 'POST':
        form = OrderStatusUpdateForm(request.POST)
        if form.is_valid():
            old_status = order.status
            order.status = form.cleaned_data['status']
            order.save()
            
            # Crear notificación si el estado cambió
            if old_status != order.status:
                from accounts.utils import notify_order_status_changed
                notify_order_status_changed(order.user, order)
            
            messages.success(
                request,
                _("Estado de la orden {} actualizado de '{}' a '{}'.").format(
                    order.order_number,
                    dict(OrderStatus.choices)[old_status],
                    dict(OrderStatus.choices)[order.status]
                )
            )
            return redirect('orders:admin_order_detail', order_id=order.id)
    else:
        form = OrderStatusUpdateForm(initial={'status': order.status})
    
    context = {
        'order': order,
        'form': form,
    }
    return render(request, 'orders/admin_order_detail.html', context)


def get_or_create_cart(request):
    """
    Helper function para obtener o crear el carrito.
    Importada desde cart.utils para evitar dependencias circulares.
    """
    from cart.utils import get_or_create_cart
    return get_or_create_cart(request)
