from django.contrib.auth.signals import user_logged_in #
from django.dispatch import receiver #
from cart.models import Cart, CartItem #

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from .models import UserProfile

@receiver(user_logged_in) #
def merge_session_cart_on_login(sender, request, user, **kwargs): #
    session_key = request.session.session_key #
    session_cart = None

    if session_key:
        try:
            session_cart = Cart.objects.get(session_key=session_key, user=None) #
        except Cart.DoesNotExist: #
            session_cart = None

    if not session_cart or not session_cart.items.exists(): #
        return

    user_cart, created = Cart.objects.get_or_create(user=user, session_key=None) #

    for session_item in session_cart.items.all(): #
        user_item, item_created = user_cart.items.get_or_create(
            product=session_item.product, #
            defaults={'quantity': session_item.quantity} #
        )
        if not item_created: #
            new_quantity = user_item.quantity + session_item.quantity #
            if new_quantity > session_item.product.stock: #
                 user_item.quantity = session_item.product.stock #
            else:
                 user_item.quantity = new_quantity #
            user_item.save() #

    session_cart.delete() #
    print(f"Carrito de sesión fusionado para el usuario {user.username}") #

# --- AÑADE ESTE CÓDIGO QUE MOVIERON DE MODELS.PY ---
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, **kwargs):
    """
    Crea o actualiza el UserProfile automáticamente cuando
    un User es guardado.
    """
    UserProfile.objects.get_or_create(user=instance)