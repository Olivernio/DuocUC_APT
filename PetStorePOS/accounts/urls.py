from django.urls import path
from . import views
from .views import RegistroWizard
from core.forms import PersonalInfoForm, ContactDataForm, PreferencesForm

app_name = "accounts"

urlpatterns = [
    path("login/",  views.login_view, name="login"),
    path("logout/", views.signout, name="logout"), 
    path(
        "registro/",
        RegistroWizard.as_view(views.FORMS), 
        name="registro"
    ),
    
    path("mi-cuenta/", views.profile_view, name="profile"),
]