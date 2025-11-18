# olivernio/duocuc_apt/DuocUC_APT-bb304ab59ba5f574e81b5de8fd8f201960969018/PetStorePOS/accounts/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    
    # Preferencias de comunicación
    receive_newsletter = models.BooleanField(default=True)
    receive_adoption_alerts = models.BooleanField(default=True)
    receive_product_recommendations = models.BooleanField(default=True)
    
    # Favoritos/Wishlist
    favorite_products = models.ManyToManyField(
        'catalog.Product',
        related_name='favorited_by',
        blank=True,
        verbose_name="Productos Favoritos"
    )

    def __str__(self):
        return f"Profile of {self.user.username}"

# Señales para crear/actualizar UserProfile automáticamente
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, **kwargs):
    UserProfile.objects.get_or_create(user=instance)


class NotificationType(models.TextChoices):
    """Tipos de notificaciones"""
    ORDER_CREATED = "ORDER_CREATED", "Orden Creada"
    ORDER_STATUS_CHANGED = "ORDER_STATUS_CHANGED", "Estado de Orden Cambiado"
    REVIEW_CREATED = "REVIEW_CREATED", "Reseña Creada"
    REVIEW_APPROVED = "REVIEW_APPROVED", "Reseña Aprobada"
    GENERAL = "GENERAL", "General"


class Notification(models.Model):
    """
    Modelo para notificaciones del usuario.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Usuario"
    )
    title = models.CharField("Título", max_length=200)
    message = models.TextField("Mensaje", max_length=500)
    type = models.CharField(
        "Tipo",
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL
    )
    is_read = models.BooleanField("Leída", default=False)
    created_at = models.DateTimeField("Fecha de Creación", auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"