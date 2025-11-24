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
    path("favoritos/", views.favorites_list, name="favorites"),
    path("favoritos/toggle/<int:product_id>/", views.toggle_favorite, name="toggle_favorite"),
    path("notificaciones/", views.notifications_list, name="notifications"),
    path("notificaciones/<int:notification_id>/marcar-leida/", views.mark_notification_read, name="mark_notification_read"),
    path("notificaciones/marcar-todas-leidas/", views.mark_all_notifications_read, name="mark_all_notifications_read"),
    
    # URLs de recuperación de contraseña (sistema simplificado)
    path("password-reset/", views.simple_password_recovery, name="password_reset"),
    
    # URLs antiguas (comentadas, por si se necesitan más adelante)
    # path("password-reset/", views.CustomPasswordResetView.as_view(), name="password_reset"),
    # path("password-reset/done/", views.CustomPasswordResetDoneView.as_view(), name="password_reset_done"),
    # path("password-reset-confirm/<uidb64>/<token>/", views.CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    # path("password-reset-complete/", views.CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),
]