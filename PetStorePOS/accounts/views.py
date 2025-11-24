# Vistas de Cuentas - PetStorePOS

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django import forms
from formtools.wizard.views import SessionWizardView
from core.forms import PersonalInfoForm, ContactDataForm, PreferencesForm
from .forms import CustomUserCreationForm, EditProfileForm
from cart.models import Cart
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from catalog.models import Product
from django.http import JsonResponse
from django.contrib.auth.views import (
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.urls import reverse_lazy
from .forms import PasswordRecoveryVerificationForm, PasswordRecoveryChangeForm
from django.contrib.auth import update_session_auth_hash
from django import forms

FORMS = [
    ("personal", PersonalInfoForm),
    ("contact", ContactDataForm),
    ("preferences", PreferencesForm),
]

TEMPLATES = {
    "personal": "accounts/signup_step1.html",
    "contact": "accounts/signup_step2.html",
    "preferences": "accounts/signup_step3.html",
}

def signout(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('home')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not email or not password:
            messages.error(request, 'Por favor, ingresa email y contraseña.')
            return render(request, 'accounts/login.html')
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return render(request, 'accounts/login.html')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'accounts/login.html')

class RegistroWizard(SessionWizardView):
    form_list = FORMS

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)
        recaptcha_value = data.get('recaptcha')
        if not recaptcha_value:
            messages.error(self.request, "Por favor, completa la verificación reCAPTCHA antes de finalizar el registro.")
            return self.render_goto_step(self.steps.last)
        from django_recaptcha.fields import ReCaptchaField
        try:
            recaptcha_field = ReCaptchaField()
            recaptcha_field.clean(recaptcha_value)
        except forms.ValidationError as e:
            error_msg = ', '.join(e.messages) if hasattr(e, 'messages') else str(e)
            if 'timeout' in error_msg.lower() or 'duplicate' in error_msg.lower():
                messages.error(self.request, "La verificación reCAPTCHA ha expirado. Por favor, completa el reCAPTCHA nuevamente y envía el formulario inmediatamente.")
            else:
                messages.error(self.request, f"Error en la verificación reCAPTCHA: {error_msg}")
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
            messages.error(self.request, "Ya existe un usuario con este correo electrónico.")
            return redirect('accounts:registro')
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
    tab = request.GET.get('tab', 'perfil')
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
    from orders.models import Order
    from catalog.models import ProductReview
    from adoption.models import AdoptionRequest
    from django.db.models import Sum, Count
    user_orders = Order.objects.filter(user=request.user).count()
    total_spent = Order.objects.filter(user=request.user).aggregate(
        total=Sum('total')
    )['total'] or 0
    adoptions = AdoptionRequest.objects.filter(email=request.user.email).count()
    reviews = ProductReview.objects.filter(user=request.user, is_approved=True).count()
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

@login_required
def toggle_favorite(request, product_id):
    if request.method != 'POST':
        messages.error(request, "Método no permitido")
        return redirect('catalog:product_list')
    try:
        product = get_object_or_404(Product, id=product_id)
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        if product in user_profile.favorite_products.all():
            user_profile.favorite_products.remove(product)
            is_favorite = False
            message = "Producto eliminado de favoritos"
        else:
            user_profile.favorite_products.add(product)
            is_favorite = True
            message = "Producto agregado a favoritos"
        try:
            favorite_count = product.favorited_by.count()
        except Exception:
            favorite_count = user_profile.favorite_products.count()
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error en toggle_favorite: {str(e)}", exc_info=True)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar favoritos: {str(e)}. Por favor verifica que las migraciones se hayan ejecutado.'
            }, status=500)
        messages.error(request, f"Error: {str(e)}. Por favor ejecuta: python manage.py migrate")
        return redirect('catalog:product_list')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'message': message,
            'favorite_count': favorite_count
        })
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'catalog:product_list'))

@login_required
def favorites_list(request):
    try:
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        favorites = user_profile.favorite_products.all()
        favorites_count = favorites.count()
    except Exception:
        favorites = []
        favorites_count = 0
    context = {
        'favorites': favorites,
        'favorites_count': favorites_count,
    }
    return render(request, 'accounts/favorites.html', context)

@login_required
def notifications_list(request):
    from django.db.utils import OperationalError
    try:
        from .models import Notification
        notifications = Notification.objects.filter(user=request.user)
        unread_count = notifications.filter(is_read=False).count()
    except OperationalError:
        notifications = []
        unread_count = 0
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/notifications.html', context)

@login_required
def mark_notification_read(request, notification_id):
    from django.db.utils import OperationalError
    try:
        from .models import Notification
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        messages.success(request, "Notificación marcada como leída")
        return redirect('accounts:notifications')
    except OperationalError:
        messages.error(request, "Las migraciones no se han ejecutado. Por favor ejecuta: python manage.py migrate")
        return redirect('home')

@login_required
def mark_all_notifications_read(request):
    from django.db.utils import OperationalError
    try:
        from .models import Notification
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        messages.success(request, "Todas las notificaciones han sido marcadas como leídas")
        return redirect('accounts:notifications')
    except OperationalError:
        messages.error(request, "Las migraciones no se han ejecutado. Por favor ejecuta: python manage.py migrate")
        return redirect('home')


# ============================================================================
# VISTAS DE RECUPERACIÓN DE CONTRASEÑA
# ============================================================================

class CustomPasswordResetView(PasswordResetView):
    """
    Vista para solicitar el reset de contraseña.
    El usuario ingresa su email y recibe un link para resetear.
    """
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            "Si existe una cuenta con ese email, recibirás un enlace para restablecer tu contraseña."
        )
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """
    Vista que se muestra después de solicitar el reset.
    Confirma que se envió el email.
    """
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Vista donde el usuario ingresa su nueva contraseña.
    Se accede a través del link recibido por email.
    """
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')
    
    def form_valid(self, form):
        messages.success(self.request, "Tu contraseña ha sido restablecida exitosamente.")
        return super().form_valid(form)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """
    Vista final que confirma que la contraseña fue cambiada.
    """
    template_name = 'accounts/password_reset_complete.html'


def simple_password_recovery(request):
    """
    Vista simplificada de recuperación de contraseña.
    Pide email y algo que recuerden, verifica similitud 60%+, luego permite cambiar contraseña.
    """
    verified_user_id = request.session.get('password_recovery_user_id')
    verified_user = None
    
    if verified_user_id:
        try:
            verified_user = User.objects.get(pk=verified_user_id)
        except User.DoesNotExist:
            # Si el usuario no existe, limpiar la sesión
            request.session.pop('password_recovery_user_id', None)
            verified_user = None
    
    # Si ya está verificado, mostrar formulario de cambio de contraseña
    if verified_user:
        if request.method == 'POST':
            form = PasswordRecoveryChangeForm(request.POST)
            if form.is_valid():
                # Validar reCAPTCHA
                recaptcha_value = form.cleaned_data.get('recaptcha')
                if not recaptcha_value:
                    messages.error(request, "Por favor, completa la verificación reCAPTCHA.")
                else:
                    from django_recaptcha.fields import ReCaptchaField
                    try:
                        recaptcha_field = ReCaptchaField()
                        recaptcha_field.clean(recaptcha_value)
                    except forms.ValidationError as e:
                        error_msg = ', '.join(e.messages) if hasattr(e, 'messages') else str(e)
                        messages.error(request, f"Error en la verificación reCAPTCHA: {error_msg}")
                    else:
                        # Cambiar la contraseña
                        new_password = form.cleaned_data['new_password1']
                        verified_user.set_password(new_password)
                        verified_user.save()
                        
                        # Limpiar la sesión
                        request.session.pop('password_recovery_user_id', None)
                        
                        messages.success(request, "Tu contraseña ha sido restablecida exitosamente. Ahora puedes iniciar sesión.")
                        return redirect('accounts:login')
        else:
            form = PasswordRecoveryChangeForm()
        
        return render(request, 'accounts/password_recovery.html', {
            'form': form,
            'verified_user': verified_user,
            'step': 'change_password'
        })
    
    # Si no está verificado, mostrar formulario de verificación
    if request.method == 'POST':
        form = PasswordRecoveryVerificationForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['verified_user']
            # Guardar el usuario verificado en la sesión
            request.session['password_recovery_user_id'] = user.pk
            messages.success(request, f"¡Verificación exitosa! Ahora puedes cambiar tu contraseña.")
            return redirect('accounts:password_reset')
    else:
        form = PasswordRecoveryVerificationForm()
    
    return render(request, 'accounts/password_recovery.html', {
        'form': form,
        'step': 'verification'
    })
