from .models import Notification, NotificationType
from django.urls import reverse
from orders.models import OrderStatus


#Crea una notificacion para un usuario|Cliente
def create_notification(user, title, message, notification_type=NotificationType.GENERAL, link=None):
    return Notification.objects.create(
        user=user, #Cliente que recibira la notifiacion
        type=notification_type, #De que sera la notificacion.
        title=title,# titulo de notificacion
        message=message, #Mensaje de notificacion
        link=link #Esto es realmente opcional ya que la persona al darle click tipo a un url dependera de que sera si es una notifiacion de oferta o etc.
    )

#Crea una notificación cuando se crea una orden.
def notify_order_created(user, order):
    from django.urls import reverse
    
    try:
        order_detail_url = reverse('orders:order_detail', args=[order.id])
        full_url = f"{order_detail_url}"  # Django construirá la URL completa
    except:
        full_url = None
    
    return create_notification(
        user=user,
        title=f"Orden #{order.order_number} creada",
        message=f"Tu orden ha sido creada exitosamente. Total: ${order.total}",
        notification_type=NotificationType.ORDER_CREATED,
        link=full_url
    )

#Crea una notificación cuando se actualiza el estado de una orden.
def notify_order_updated(user, order, old_status, new_status):

    try:
        order_detail_url = reverse('orders:order_detail', args=[order.id])
        full_url = f"{order_detail_url}"
    except:
        full_url = None
    
    # Obtener los nombres legibles de los estados 
    status_choices = dict(OrderStatus.choices)
    old_status_display = status_choices.get(old_status, old_status)
    new_status_display = status_choices.get(new_status, new_status)
    
    return create_notification(
        user=user,
        title=f"Orden #{order.order_number} actualizada",
        message=f"El estado de tu orden cambió de '{old_status_display}' a '{new_status_display}'",
        notification_type=NotificationType.ORDER_UPDATED,
        link=full_url
    )

