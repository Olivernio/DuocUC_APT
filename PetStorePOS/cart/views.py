from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from catalog.models import Product
from .models import Cart, CartItem
from .utils import get_or_create_cart

@require_POST
def add_to_cart(request, product_id):
    cart = get_or_create_cart(request) #
    product = get_object_or_404(Product, id=product_id) #

    if not product.is_active or product.stock <= 0: #
         messages.error(request, f"'{product.name}' no está disponible.") #
         return redirect(request.META.get('HTTP_REFERER', 'catalog:product_list')) #

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, #
        product=product, #
        defaults={'quantity': 1} #
    )

    if not created: #
        if cart_item.quantity < product.stock: #
            cart_item.quantity += 1 #
            cart_item.save() #
            messages.success(request, f"Se añadió otra unidad de '{product.name}' al carrito.")
        else:
            messages.warning(request, f"No puedes añadir más de '{product.name}', stock máximo alcanzado.") #
    else: #
        messages.success(request, f"'{product.name}' añadido al carrito.") #

    return redirect(request.META.get('HTTP_REFERER', 'cart:cart_detail')) #


def cart_detail(request):
    cart = get_or_create_cart(request) #
    context = {'cart': cart} #
    return render(request, 'cart/cart_detail.html', context) #

@require_POST
def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request) #
    item = get_object_or_404(CartItem, id=item_id, cart=cart) #
    product_name = item.product.name #
    item.delete() #
    messages.info(request, f"'{product_name}' eliminado del carrito.") #
    return redirect('cart:cart_detail') #

@require_POST
def update_cart_item(request, item_id):
    cart = get_or_create_cart(request) #
    item = get_object_or_404(CartItem, id=item_id, cart=cart) #

    try:
        quantity = int(request.POST.get('quantity')) #
    except (TypeError, ValueError):
        messages.error(request, "Cantidad inválida.") #
        return redirect('cart:cart_detail') #

    if quantity <= 0: #
        product_name = item.product.name #
        item.delete() #
        messages.info(request, f"'{product_name}' eliminado del carrito.") #
    elif quantity > item.product.stock: #
        item.quantity = item.product.stock #
        item.save() #
        messages.warning(request, f"Stock máximo para '{item.product.name}' es {item.product.stock}. Cantidad ajustada.") #
    else:
        item.quantity = quantity #
        item.save() #
        messages.success(request, f"Cantidad de '{item.product.name}' actualizada.") #

    return redirect('cart:cart_detail') #