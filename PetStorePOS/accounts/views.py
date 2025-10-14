from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from formtools.wizard.views import SessionWizardView
from core.forms import PersonalInfoForm, ContactDataForm, PreferencesForm
from .forms import CustomUserCreationForm

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

# Vista tradicional para registro clásico con formulario único
def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:login')
        else:
            return render(request, "accounts/signup.html", {"form": form})
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})

# Vista personalizada para login
def login_view(request):
    # Si ya está autenticado, redirige a home o donde quieras
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'accounts/login.html')

# Vista para logout
def signoout(request):
    logout(request)
    return redirect('home')

# Clase wizard para el registro multi-paso
class RegistroWizard(SessionWizardView):
    form_list = FORMS

    # Retorna la plantilla dependiendo del paso actual
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    # Al finalizar el último paso, crea el usuario y muestra la plantilla de éxito
    def done(self, form_list, **kwargs):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)
        user = User.objects.create_user(
            username=data['correo'],
            email=data['correo'],
            password=data['contraseña'],
            first_name=data['nombre'],
            last_name=data['apellidos'],
        )
        return render(self.request, 'accounts/registro_exitoso.html', {'user': user})