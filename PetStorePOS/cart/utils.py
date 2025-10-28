from .models import Cart

def get_or_create_cart(request):
    """
    Obtiene o crea el carrito para el usuario/sesión actual.
    """
    if request.user.is_authenticated:
        # Usuario logueado
        cart, created = Cart.objects.get_or_create(user=request.user, session_key=None) #
    else:
        # Usuario invitado
        session_key = request.session.session_key
        if not session_key:
            request.session.create() #
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key, user=None) #
    return cart