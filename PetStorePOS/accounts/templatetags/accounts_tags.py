from django import template
from accounts.models import UserProfile

register = template.Library()

@register.simple_tag
def get_user_profile(user):
    """
    Obtiene el perfil de usuario si existe.
    """
    if not user or not user.is_authenticated:
        return None
    try:
        return UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return None


@register.simple_tag
def get_unread_notifications_count(user):
    """
    Obtiene el número de notificaciones no leídas del usuario.
    """
    if not user or not user.is_authenticated:
        return 0
    try:
        from accounts.models import Notification
        return Notification.objects.filter(user=user, is_read=False).count()
    except Exception:
        # Si la tabla no existe aún (migraciones pendientes), retornar 0
        return 0

