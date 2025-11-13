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

    def __str__(self):
        return f"Profile of {self.user.username}"

# Señales para crear/actualizar UserProfile automáticamente
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, **kwargs):
    UserProfile.objects.get_or_create(user=instance)