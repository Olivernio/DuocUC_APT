from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from formtools.wizard.views import SessionWizardView
from core.forms import PersonalInfoForm, ContactDataForm, PreferencesForm
from .forms import CustomUserCreationForm
from cart.models import Cart # Asegúrate de importar Cart

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
    messages.info(request, "Has cerrado sesión correctamente.") # Mensaje opcional
    return redirect('home')

def login_view(request):
    # Si ya está autenticado, redirige a home
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        # 1. Obtener email y contraseña del formulario
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, 'Por favor, ingresa email y contraseña.')
            return render(request, 'accounts/login.html') #

        try:
            # 2. Buscar el usuario por su email para obtener su username
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            # Si el email no existe, falla
            messages.error(request, 'Usuario o contraseña incorrectos.') #
            return render(request, 'accounts/login.html') #

        # 3. Autenticar usando el username encontrado y la contraseña
        user = authenticate(request, username=username, password=password) #

        if user is not None:
            login(request, user) #
            messages.success(request, f'¡Bienvenido, {user.username}!') #
            return redirect('home') #
        else:
            # Si llega aquí, significa que la contraseña era incorrecta
            messages.error(request, 'Usuario o contraseña incorrectos.') #

    return render(request, 'accounts/login.html') #

# Clase wizard para el registro multi-paso
class RegistroWizard(SessionWizardView):
    form_list = FORMS #

    # Retorna la plantilla dependiendo del paso actual
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]] #

    # Al finalizar el último paso, crea el usuario, fusiona carrito e inicia sesión
    def done(self, form_list, **kwargs):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data) #

        # Crear el usuario
        try:
            user = User.objects.create_user(
                username=data['correo'], # Usamos el correo como username
                email=data['correo'], #
                password=data['contraseña'], #
                first_name=data['nombre'], #
                last_name=data['apellidos'], #
            )
        except IntegrityError:
             messages.error(self.request, "Ya existe un usuario con este correo electrónico.")
             # Reiniciar el wizard o redirigir al paso de contacto
             return redirect('accounts:registro') # O redirige a un paso específico

        # **** INICIO: Lógica de Fusión del Carrito ****
        session_key = self.request.session.session_key
        session_cart = None
        if session_key:
            try:
                # Busca carrito de invitado asociado a la sesión
                session_cart = Cart.objects.get(session_key=session_key, user=None) #
            except Cart.DoesNotExist:
                pass # No había carrito de sesión

        if session_cart and session_cart.items.exists(): #
            # Obtiene o crea el carrito del NUEVO usuario
            user_cart, created = Cart.objects.get_or_create(user=user, session_key=None) #
            # Fusiona los items
            for session_item in session_cart.items.all(): #
                user_item, item_created = user_cart.items.get_or_create(
                    product=session_item.product, #
                    defaults={'quantity': session_item.quantity} #
                )
                if not item_created:
                    # Sumar cantidades (con verificación de stock)
                    new_quantity = user_item.quantity + session_item.quantity #
                    if new_quantity > session_item.product.stock: #
                         user_item.quantity = session_item.product.stock #
                    else:
                         user_item.quantity = new_quantity #
                    user_item.save() #
            session_cart.delete() # Elimina el carrito de sesión #
            print(f"Carrito de sesión fusionado para el nuevo usuario {user.username}")
        # **** FIN: Lógica de Fusión del Carrito ****

        # Iniciar sesión automáticamente
        login(self.request, user) #
        messages.success(self.request, f'¡Bienvenido y gracias por registrarte, {user.first_name}!') #

        # Redirigir a 'home' en lugar de a registro_exitoso.html
        return redirect('home') #

def profile_view(request):
    """
    Muestra la página 'Mi Cuenta' si el usuario está logueado.
    Muestra 'Acceso Requerido' si es un invitado.
    """
    if not request.user.is_authenticated:
        # Si no está logueado, muestra la plantilla de "Acceso Requerido"
        return render(request, 'accounts/access_required.html')
    
    # Si está logueado, muestra su perfil
    context = {
        'user': request.user
    }
    return render(request, 'accounts/profile.html', context)