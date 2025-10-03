from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from formtools.wizard.views import SessionWizardView
from core.forms import PersonalInfoForm, ContactDataForm, PreferencesForm
from .forms import CustomUserCreationForm

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


def login_view(request):
    # Si el usuario ya está autenticado, lo redirigimos
    if request.user.is_authenticated:
        return redirect('home')  # Reemplaza 'home' con la URL a la que quieras redirigir

    # Manejar la solicitud POST (cuando el formulario se envía)
    if request.method == 'POST':
        # Capturar los datos del formulario
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Autenticar al usuario
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Si el usuario es válido, iniciar sesión
            login(request, user)
            messages.success(request, f'¡Bienvenido, {username}!')
            return redirect('home')  # Redirigir a una página de inicio
        else:
            # Si las credenciales son inválidas, mostrar un mensaje de error
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    # Manejar la solicitud GET (cuando se accede a la página por primera vez)
    return render(request, 'accounts/login.html')

def signoout(request):
    logout(request)
    return redirect('home')

class RegistroWizard(SessionWizardView):
    form_list = FORMS

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

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