from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from catalog.models import Product
from .models import Cart, CartItem
from .utils import get_or_create_cart
from django.utils.translation import gettext_lazy as _ # <--- 1. IMPORTAMOS
from django.utils.text import format_lazy # <--- 2. IMPORTAMOS

@require_POST
def add_to_cart(request, product_id):
    cart = get_or_create_cart(request) 
    product = get_object_or_404(Product, id=product_id) 

    if not product.is_active or product.stock <= 0: 
         messages.error(request, format_lazy(_("'{}' no está disponible."), product.name)) # <--- TRADUCIDO
         return redirect(request.META.get('HTTP_REFERER', 'catalog:product_list')) 

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product, 
        defaults={'quantity': 1} 
    )

    if not created: 
        if cart_item.quantity < product.stock: 
            cart_item.quantity += 1 
            cart_item.save() 
            messages.success(request, format_lazy(_("Se añadió otra unidad de '{}' al carrito."), product.name)) # <--- TRADUCIDO
        else:
            messages.warning(request, format_lazy(_("No puedes añadir más de '{}', stock máximo alcanzado."), product.name)) # <--- TRADUCIDO
    else: 
        messages.success(request, format_lazy(_("'{}' añadido al carrito."), product.name)) # <--- TRADUCIDO

    return redirect(request.META.get('HTTP_REFERER', 'cart:cart_detail')) 


def cart_detail(request):
    cart = get_or_create_cart(request) 
    context = {'cart': cart} 
    return render(request, 'cart/cart_detail.html', context) 

@require_POST
def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request) 
    item = get_object_or_404(CartItem, id=item_id, cart=cart) 
    product_name = item.product.name 
    item.delete() 
    messages.info(request, format_lazy(_("'{}' eliminado del carrito."), product_name)) # <--- TRADUCIDO
    return redirect('cart:cart_detail') 

@require_POST
def update_cart_item(request, item_id):
    cart = get_or_create_cart(request) 
    item = get_object_or_404(CartItem, id=item_id, cart=cart) 

    try:
        quantity = int(request.POST.get('quantity')) 
    except (TypeError, ValueError):
        messages.error(request, _("Cantidad inválida.")) # <--- TRADUCIDO
        return redirect('cart:cart_detail') 

    if quantity <= 0: 
        product_name = item.product.name 
        item.delete() 
        messages.info(request, format_lazy(_("'{}' eliminado del carrito."), product_name)) # <--- TRADUCIDO (reutilizado)
    elif quantity > item.product.stock: 
        item.quantity = item.product.stock 
        item.save() 
        messages.warning(request, format_lazy(_("Stock máximo para '{}' es {}. Cantidad ajustada."), item.product.name, item.product.stock)) # <--- TRADUCIDO
    else:
        item.quantity = quantity 
        item.save() 
        messages.success(request, format_lazy(_("Cantidad de '{}' actualizada."), item.product.name)) # <--- TRADUCIDO

    return redirect('cart:cart_detail')