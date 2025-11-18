from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from catalog.models import Product
import uuid
from datetime import datetime


class OrderStatus(models.TextChoices):
    """Estados posibles de una orden"""
    PENDING = "PENDING", _("Pendiente")
    CONFIRMED = "CONFIRMED", _("Confirmada")
    PROCESSING = "PROCESSING", _("En Proceso")
    SHIPPED = "SHIPPED", _("Enviada")
    DELIVERED = "DELIVERED", _("Entregada")
    CANCELLED = "CANCELLED", _("Cancelada")


class Order(models.Model):
    """
    Modelo que representa una orden/pedido de compra.
    
    Relaciones:
    - user: Usuario que realizó la orden (ForeignKey a User)
    - items: Items de la orden (OrderItem, related_name='items')
    - applied_coupons: Cupones aplicados a la orden (OrderCoupon)
    
    Estados posibles (OrderStatus):
    - PENDING: Orden creada pero no confirmada
    - CONFIRMED: Orden confirmada
    - PROCESSING: Orden en proceso de preparación
    - SHIPPED: Orden enviada
    - DELIVERED: Orden entregada
    - CANCELLED: Orden cancelada
    
    El número de orden se genera automáticamente al guardar si no existe,
    usando el formato: ORD-YYYYMMDD-XXXXX
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_("Usuario")
    )
    order_number = models.CharField(
        _("Número de Orden"),
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    status = models.CharField(
        _("Estado"),
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    total = models.DecimalField(
        _("Total"),
        max_digits=10,
        decimal_places=2,
        default=0
    )
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
    notes = models.TextField(
        _("Notas"),
        max_length=500,
        blank=True
    )
    created_at = models.DateTimeField(_("Fecha de Creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de Actualización"), auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Orden")
        verbose_name_plural = _("Órdenes")

    def __str__(self):
        return f"Orden {self.order_number} - {self.user.username}"

    def save(self, *args, **kwargs):
        """Genera número de orden único si no existe"""
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_order_number():
        """
        Genera un número de orden único en formato: ORD-YYYYMMDD-XXXXX
        """
        date_str = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:5].upper()
        order_number = f"ORD-{date_str}-{unique_id}"
        
        # Asegurar unicidad
        while Order.objects.filter(order_number=order_number).exists():
            unique_id = str(uuid.uuid4())[:5].upper()
            order_number = f"ORD-{date_str}-{unique_id}"
        
        return order_number

    @property
    def total_items(self):
        """Retorna el total de items en la orden"""
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    """
    Modelo que representa un item individual dentro de una orden.
    """
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
        """Calcula el subtotal del item"""
        return self.price * self.quantity


class DiscountType(models.TextChoices):
    """Tipos de descuento para cupones"""
    PERCENTAGE = "PERCENTAGE", _("Porcentaje")
    FIXED = "FIXED", _("Monto Fijo")


class Coupon(models.Model):
    """
    Modelo para cupones de descuento.
    """
    code = models.CharField(
        _("Código"),
        max_length=50,
        unique=True,
        db_index=True,
        help_text=_("Código único del cupón (ej: DESCUENTO20)")
    )
    discount_type = models.CharField(
        _("Tipo de Descuento"),
        max_length=20,
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE
    )
    discount_value = models.DecimalField(
        _("Valor del Descuento"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Si es porcentaje: 10 = 10%. Si es fijo: 1000 = $1000")
    )
    valid_from = models.DateTimeField(_("Válido Desde"))
    valid_to = models.DateTimeField(_("Válido Hasta"))
    is_active = models.BooleanField(_("Activo"), default=True)
    usage_limit = models.PositiveIntegerField(
        _("Límite de Uso"),
        null=True,
        blank=True,
        help_text=_("Número máximo de veces que se puede usar. Dejar vacío para ilimitado.")
    )
    used_count = models.PositiveIntegerField(_("Veces Usado"), default=0)
    created_at = models.DateTimeField(_("Fecha de Creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de Actualización"), auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Cupón")
        verbose_name_plural = _("Cupones")

    def __str__(self):
        return f"{self.code} - {self.get_discount_type_display()}"

    def is_valid(self):
        """Verifica si el cupón es válido (fechas, activo, límite de uso)"""
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return False
        
        if now < self.valid_from or now > self.valid_to:
            return False
        
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        
        return True

    def calculate_discount(self, total):
        """
        Calcula el descuento aplicado a un total.
        
        Args:
            total: El total al que aplicar el descuento
            
        Returns:
            tuple: (descuento, total_con_descuento)
        """
        if not self.is_valid():
            return 0, total
        
        if self.discount_type == DiscountType.PERCENTAGE:
            discount = (total * self.discount_value) / 100
        else:  # FIXED
            discount = min(self.discount_value, total)  # No puede ser mayor que el total
        
        final_total = max(0, total - discount)  # No puede ser negativo
        return discount, final_total

    def apply(self):
        """Incrementa el contador de uso del cupón"""
        self.used_count += 1
        self.save(update_fields=['used_count', 'updated_at'])


class OrderCoupon(models.Model):
    """
    Modelo para relacionar órdenes con cupones aplicados.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='applied_coupons',
        verbose_name=_("Orden")
    )
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.PROTECT,
        related_name='order_applications',
        verbose_name=_("Cupón")
    )
    discount_amount = models.DecimalField(
        _("Monto del Descuento"),
        max_digits=10,
        decimal_places=2
    )
    applied_at = models.DateTimeField(_("Fecha de Aplicación"), auto_now_add=True)

    class Meta:
        verbose_name = _("Cupón Aplicado")
        verbose_name_plural = _("Cupones Aplicados")
        unique_together = [['order', 'coupon']]

    def __str__(self):
        return f"{self.coupon.code} aplicado a {self.order.order_number}"