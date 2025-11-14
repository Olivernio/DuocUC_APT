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
    
    #Productos favoritos
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


# ----------Modelo de Notificaciones------------------

#Tipos de notificaciones disponibles en el sistema.
class NotificationType(models.TextChoices):

    ORDER_CREATED = "ORDER_CREATED", "Orden Creada"
    ORDER_UPDATED = "ORDER_UPDATED", "Orden Actualizada"
    REVIEW_APPROVED = "REVIEW_APPROVED", "Reseña Aprobada"
    ADOPTION_APPROVED = "ADOPTION_APPROVED", "Adopción Aprobada"
    GENERAL = "GENERAL", "General"

#Modelo que representa una notificación para un usuario.
class Notification(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        verbose_name="Usuario"
    )
    type = models.CharField(
        max_length=20, 
        choices=NotificationType.choices, 
        default=NotificationType.GENERAL,
        verbose_name="Tipo"
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    message = models.TextField(verbose_name="Mensaje")
    is_read = models.BooleanField(default=False, verbose_name="Leída")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    link = models.URLField(blank=True, null=True, verbose_name="Enlace")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"