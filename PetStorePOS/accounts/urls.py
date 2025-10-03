from django.urls import path
from . import views
from .views import RegistroWizard
from core.forms import PersonalInfoForm, ContactDataForm, PreferencesForm

app_name = "accounts"

urlpatterns = [
    path("login/",  views.login_view, name="login"),
    path("logout/", views.signoout, name="logout"),
    path("signup/", views.signup, name="signup"),
    path(
        "registro/",
        RegistroWizard.as_view([
           ("personal", PersonalInfoForm),
           ("contact", ContactDataForm),
           ("preferences", PreferencesForm),
        ]),
        name="registro"
    ),
]