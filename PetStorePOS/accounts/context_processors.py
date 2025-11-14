#Context processors para hacer disponible información de notificaciones
#en todos los templates.
from django.db.utils import OperationalError


def notifications_context(request):
 #Agrega el contador de notificaciones no leídas al contexto.
    if request.user.is_authenticated:
        try:
            from .models import Notification
            unread_count = Notification.objects.filter(
                user=request.user,
                is_read=False
            ).count()
            return {'unread_notifications_count': unread_count}
        except OperationalError:
            # Si la tabla no existe aún (migraciones pendientes)
            return {'unread_notifications_count': 0}
    return {'unread_notifications_count': 0}

