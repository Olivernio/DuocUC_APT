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
    
    # URLs de favoritos
    path("favoritos/", views.favorites_list, name="favorites"),
    path("favoritos/toggle/<int:product_id>/", views.toggle_favorite, name="toggle_favorite"),
    
    # URLs de notificaciones
    path("notificaciones/", views.notifications_list, name="notifications"),
    path("notificaciones/<int:notification_id>/marcar-leida/", views.mark_notification_read, name="mark_notification_read"),
    path("notificaciones/marcar-todas-leidas/", views.mark_all_notifications_read, name="mark_all_notifications_read"),
]