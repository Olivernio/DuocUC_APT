"""
Funciones helper para crear notificaciones.
"""
from .models import Notification, NotificationType


def create_notification(user, title, message, notification_type=NotificationType.GENERAL):
    """
    Crea una notificación para un usuario.
    
    Args:
        user: Usuario que recibirá la notificación
        title: Título de la notificación
        message: Mensaje de la notificación
        notification_type: Tipo de notificación (default: GENERAL)
    
    Returns:
        Notification: La notificación creada
    """
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        type=notification_type
    )


def notify_order_created(user, order):
    """
    Crea una notificación cuando se crea una orden.
    """
    return create_notification(
        user=user,
        title="Orden Creada",
        message=f"Tu orden #{order.order_number} ha sido creada exitosamente. Total: ${order.total}",
        notification_type=NotificationType.ORDER_CREATED
    )


def notify_order_status_changed(user, order):
    """
    Crea una notificación cuando cambia el estado de una orden.
    """
    from orders.models import OrderStatus
    status_display = dict(OrderStatus.choices).get(order.status, order.status)
    return create_notification(
        user=user,
        title="Estado de Orden Actualizado",
        message=f"Tu orden #{order.order_number} ahora está: {status_display}",
        notification_type=NotificationType.ORDER_STATUS_CHANGED
    )


def notify_review_created(user, review):
    """
    Crea una notificación cuando se crea una reseña (para el admin).
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    # Notificar a todos los admins
    admins = User.objects.filter(is_staff=True)
    notifications = []
    for admin in admins:
        notifications.append(create_notification(
            user=admin,
            title="Nueva Reseña Pendiente",
            message=f"{user.username} ha dejado una reseña para {review.product.name}. Requiere aprobación.",
            notification_type=NotificationType.REVIEW_CREATED
        ))
    return notifications


def notify_review_approved(user, review):
    """
    Crea una notificación cuando se aprueba una reseña.
    """
    return create_notification(
        user=user,
        title="Reseña Aprobada",
        message=f"Tu reseña para {review.product.name} ha sido aprobada y está visible en el sitio.",
        notification_type=NotificationType.REVIEW_APPROVED
    )

