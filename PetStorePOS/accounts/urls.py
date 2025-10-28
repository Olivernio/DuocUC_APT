from django.urls import path
from . import views
from .views import RegistroWizard
# Asegúrate que los imports de forms sean correctos si los necesitas aquí
from core.forms import PersonalInfoForm, ContactDataForm, PreferencesForm

app_name = "accounts"

urlpatterns = [
    path("login/",  views.login_view, name="login"),
    path("logout/", views.signout, name="logout"), # <- Esta línea debe estar así
    # path("signup/", views.signup, name="signup"), # Comentado como antes
    path(
        "registro/",
        RegistroWizard.as_view(views.FORMS), # Usamos FORMS de views.py
        name="registro"
    ),
]