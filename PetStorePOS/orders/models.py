from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from catalog.models import Product
import uuid
from datetime import datetime


#Estados posibles de una orden.
#Esto es como un enum: define opciones predefinidas.
class OrderStatus(models.TextChoices):

    PENDING = "PENDING", _("Pendiente")
    CONFIRMED = "CONFIRMED", _("Confirmada")
    PROCESSING = "PROCESSING", _("En Proceso")
    SHIPPED = "SHIPPED", _("Enviada")
    DELIVERED = "DELIVERED", _("Entregada")
    CANCELLED = "CANCELLED", _("Cancelada")


class Order(models.Model):
    """
    Modelo que representa una orden/pedido de compra.
    """
    # Relación con el usuario
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_("Usuario")
    )
    
    # Número único de orden
    order_number = models.CharField(
        _("Número de Orden"),
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    
    # Estado de la orden
    status = models.CharField(
        _("Estado"),
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    
    # Total de la orden
    total = models.DecimalField(
        _("Total"),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    # Información de envío
    shipping_address = models.TextField(
        _("Dirección de Envío"),
        max_length=500,
        blank=True
    )
    shipping_city = models.CharField(
        _("Ciudad"),
        max_length=100,
        blank=True
    )
    shipping_postal_code = models.CharField(
        _("Código Postal"),
        max_length=20,
        blank=True
    )
    
    # Notas adicionales
    notes = models.TextField(
        _("Notas"),
        max_length=500,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(_("Fecha de Creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de Actualización"), auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Orden")
        verbose_name_plural = _("Órdenes")


    def __str__(self):
        return f"Orden {self.order_number} - {self.user.username}"

    def save(self, *args, **kwargs):
        """Genera número de orden si no existe"""
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_order_number():
        """Genera número único: ORD-YYYYMMDD-XXXXX"""
        date_str = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:5].upper()
        order_number = f"ORD-{date_str}-{unique_id}"
        
        # Asegurar unicidad
        while Order.objects.filter(order_number=order_number).exists():
            unique_id = str(uuid.uuid4())[:5].upper()
            order_number = f"ORD-{date_str}-{unique_id}"
        
        return order_number

#    Representa un producto dentro de una orden.
class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_("Orden")
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name=_("Producto")
    )
    
    quantity = models.PositiveIntegerField(_("Cantidad"), default=1)
    
    price = models.DecimalField(
        _("Precio Unitario"),
        max_digits=10,
        decimal_places=2
    )
    
    created_at = models.DateTimeField(_("Fecha de Creación"), auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = _("Item de Orden")
        verbose_name_plural = _("Items de Orden")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} - Orden {self.order.order_number}"

    @property
    def subtotal(self):
        """Calcula precio × cantidad"""
        return self.price * self.quantity