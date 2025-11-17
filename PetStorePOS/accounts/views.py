from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django import forms
from formtools.wizard.views import SessionWizardView
from core.forms import PersonalInfoForm, ContactDataForm, PreferencesForm
from .forms import CustomUserCreationForm, EditProfileForm
from cart.models import Cart
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from catalog.models import Product
from django.utils.text import format_lazy

# Lista de formularios usados en el wizard y su orden lógico
FORMS = [
    ("personal", PersonalInfoForm),
    ("contact", ContactDataForm),
    ("preferences", PreferencesForm),
]

# Plantillas usadas para cada paso del wizard
TEMPLATES = {
    "personal": "accounts/signup_step1.html",
    "contact": "accounts/signup_step2.html",
    "preferences": "accounts/signup_step3.html",
}

# Vista para logout
def signout(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")  # Mensaje opcional
    return redirect('home')

# PetStorePOS/accounts/views.py

# (Asegúrate de que estas importaciones están al inicio del archivo)
from django.utils.translation import gettext_lazy as _
from django.utils.text import format_lazy
# ... (las otras importaciones como messages, login, authenticate, etc.)

def login_view(request):
    # Si ya está autenticado, redirige a home
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        # 1. Obtener email y contraseña del formulario
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            # --- MENSAJE CORREGIDO ---
            messages.error(request, _('Por favor, ingresa email y contraseña.'))
            return render(request, 'accounts/login.html')
        
        try:
            # 2. Buscar el usuario por su email para obtener su username
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            # --- MENSAJE CORREGIDO ---
            messages.error(request, _('Usuario o contraseña incorrectos.'))
            return render(request, 'accounts/login.html')
        
        # 3. Autenticar usando el username encontrado y la contraseña
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # --- MENSAJE CORREGIDO (Este ya lo tenías bien, pero lo confirmo) ---
            messages.success(request, format_lazy(_('¡Bienvenido, {}!'), user.username))
            return redirect('home')
        else:
            # --- MENSAJE CORREGIDO ---
            messages.error(request, _('Usuario o contraseña incorrectos.'))
    
    return render(request, 'accounts/login.html')

# Clase wizard para el registro multi-paso
class RegistroWizard(SessionWizardView):
    form_list = FORMS

    # Retorna la plantilla dependiendo del paso actual
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    # Al finalizar el último paso, crea el usuario, fusiona carrito e inicia sesión
    def done(self, form_list, **kwargs):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)
        
        # Validar reCAPTCHA solo cuando se completa el wizard
        recaptcha_value = data.get('recaptcha')
        if not recaptcha_value:
            messages.error(self.request, _("Por favor, completa la verificación reCAPTCHA antes de finalizar el registro."))
            # Volver al último paso del wizard con los datos guardados
            return self.render_goto_step(self.steps.last)
        
        # Validar el reCAPTCHA manualmente usando ReCaptchaField original
        # Esto evita errores de timeout-or-duplicate en pasos intermedios
        from django_recaptcha.fields import ReCaptchaField
        try:
            # Crear una instancia del campo ReCaptchaField para validar
            recaptcha_field = ReCaptchaField()
            recaptcha_field.clean(recaptcha_value)
        except forms.ValidationError as e:
            # --- AÑADE ESTA LÍNEA ---
            print(f"MENSAJE DE ERROR COMPLETO DE RECAPTCHA: {e}")
            # ---------------------
            
            error_msg = ', '.join(e.messages) if hasattr(e, 'messages') else str(e)
            # Si es un error de timeout, dar un mensaje más amigable
            if 'timeout' in error_msg.lower() or 'duplicate' in error_msg.lower():
                messages.error(self.request, _("La verificación reCAPTCHA ha expirado. Por favor, completa el reCAPTCHA nuevamente y envía el formulario inmediatamente."))
            else:
                messages.error(self.request, _("Error en la verificación reCAPTCHA: {}").format(error_msg))
            return self.render_goto_step(self.steps.last)
        
        try:
            user = User.objects.create_user(
                username=data['correo'],
                email=data['correo'],
                password=data['contraseña'],
                first_name=data['nombre'],
                last_name=data['apellidos'],
            )
        except IntegrityError:
            messages.error(self.request, _("Ya existe un usuario con este correo electrónico."))
            return redirect('accounts:registro')
        # Fusionar carrito
        session_key = self.request.session.session_key
        session_cart = None
        if session_key:
            try:
                session_cart = Cart.objects.get(session_key=session_key, user=None)
            except Cart.DoesNotExist:
                pass
        if session_cart and session_cart.items.exists():
            user_cart, created = Cart.objects.get_or_create(user=user, session_key=None)
            for session_item in session_cart.items.all():
                user_item, item_created = user_cart.items.get_or_create(
                    product=session_item.product,
                    defaults={'quantity': session_item.quantity}
                )
                if not item_created:
                    new_quantity = user_item.quantity + session_item.quantity
                    if new_quantity > session_item.product.stock:
                        user_item.quantity = session_item.product.stock
                    else:
                        user_item.quantity = new_quantity
                    user_item.save()
            session_cart.delete()
        login(self.request, user)
        messages.success(self.request, f'¡Bienvenido y gracias por registrarte, {user.first_name}!')
        return redirect('home')

@login_required
def profile_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    edit_mode = request.GET.get('edit', 'false') == 'true'
    tab = request.GET.get('tab', 'perfil')  # Pestaña activa: perfil, pedidos, mascotas, reseñas
    
    if request.method == "POST":
        if "cancel" in request.POST:
            return redirect('accounts:profile')
        form = EditProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            request.user.first_name = form.cleaned_data["first_name"]
            request.user.last_name = form.cleaned_data["last_name"]
            request.user.email = form.cleaned_data["email"]
            request.user.save()
            messages.success(request, "¡Perfil actualizado correctamente!")
            return redirect("accounts:profile")
        edit_mode = True
    else:
        form = EditProfileForm(instance=user_profile, initial={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
        })
    
    # Obtener datos reales
    from orders.models import Order
    from catalog.models import ProductReview
    from adoption.models import AdoptionRequest
    from django.db.models import Sum, Count
    
    # Pedidos
    user_orders = Order.objects.filter(user=request.user).count()
    total_spent = Order.objects.filter(user=request.user).aggregate(
        total=Sum('total')
    )['total'] or 0
    
    # Adopciones (buscamos por email ya que AdoptionRequest no tiene ForeignKey a User)
    adoptions = AdoptionRequest.objects.filter(email=request.user.email).count()
    
    # Reseñas
    reviews = ProductReview.objects.filter(user=request.user, is_approved=True).count()
    
    # Datos para las pestañas
    orders_list = []
    adoptions_list = []
    reviews_list = []
    
    if tab == 'pedidos':
        from django.core.paginator import Paginator
        orders_list = Order.objects.filter(user=request.user).select_related('user').prefetch_related('items__product').order_by('-created_at')
        paginator = Paginator(orders_list, 10)
        page_number = request.GET.get('page')
        orders_list = paginator.get_page(page_number)
    
    elif tab == 'mascotas':
        adoptions_list = AdoptionRequest.objects.filter(email=request.user.email).select_related('Mascota').order_by('-created_at')
    
    elif tab == 'reseñas':
        reviews_list = ProductReview.objects.filter(user=request.user).select_related('product').order_by('-created_at')

    context = {
        "user": request.user,
        "form": form,
        "user_orders": user_orders,
        "total_spent": total_spent,
        "adoptions": adoptions,
        "reviews": reviews,
        "edit_mode": edit_mode,
        "active_tab": tab,
        "orders_list": orders_list,
        "adoptions_list": adoptions_list,
        "reviews_list": reviews_list,
    }
    return render(request, "accounts/profile.html", context)


#Esto sirve para poder agregar o quitar productos a favoritos o si ya esta , lo podra quitar o agregar , pocas palabras 
# AGREGA | QUITA | 
@login_required
def toggle_favorite(request, product_id):
    """
    Vista para agregar/quitar un producto de favoritos.
    Soporta tanto AJAX como requests normales.
    """
    if request.method != 'POST':
        messages.error(request, _("Método no permitido"))
        return redirect('catalog:product_list')
    
    try:
        product = get_object_or_404(Product, id=product_id)
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if product in user_profile.favorite_products.all():
            user_profile.favorite_products.remove(product)
            is_favorite = False
            message = _("Producto eliminado de favoritos")
        else:
            user_profile.favorite_products.add(product)
            is_favorite = True
            message = _("Producto agregado a favoritos")
        
        favorite_count = product.favorited_by.count()
    except Exception as e:
        # Si las migraciones no se han ejecutado, retornar error
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': _('Las migraciones no se han ejecutado. Por favor ejecuta: python manage.py migrate')
            }, status=500)
        messages.error(request, _("Error: Las migraciones no se han ejecutado. Por favor ejecuta: python manage.py migrate"))
        return redirect('catalog:product_list')
    
    # Si es una petición AJAX, retornar JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'message': str(message),
            'favorite_count': favorite_count
        })
    
    # Si no es AJAX, redirigir con mensaje
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'catalog:product_list'))


#Muestra la lista o las cosas que marco el usuario como favoritas
@login_required
def favorites_list(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    favorites = user_profile.favorite_products.filter(is_active=True)
    
    context = {
        'favorites': favorites,
        'favorites_count': favorites.count(),
    }
    return render(request, 'accounts/favorites.html', context)

#mostrara las notifacaciones al usuario
@login_required
def notifications_list(request):
    from .models import Notification
    
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/notifications.html', context)


#Marca una notificacion leida si no me equivoco manual o automatica
@login_required
def mark_notification_read(request, notification_id):
    from .models import Notification
    
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, _("Notificación marcada como leída"))
    return redirect('accounts:notifications')


#Este def funciona principalmente para marcas todas las notificaciones del usuario como leidas o cosas asi.
@login_required
def mark_all_notifications_read(request):
    from .models import Notification
    
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, _("Todas las notificaciones han sido marcadas como leídas"))
    return redirect('accounts:notifications')
