from django.db import models
from django.conf import settings
from catalog.models import Product #

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, #
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='cart' #
    )
    session_key = models.CharField(max_length=40, null=True, blank=True, unique=True, db_index=True) #
    created_at = models.DateTimeField(auto_now_add=True) #
    updated_at = models.DateTimeField(auto_now=True) #

    def __str__(self):
        if self.user:
            return f"Carrito de {self.user.username}" #
        elif self.session_key:
            return f"Carrito invitado (Sesión: {self.session_key[:8]}...)" #
        return f"Carrito ID: {self.id}" #

    @property
    def total_cart_price(self):
        return sum(item.total_price for item in self.items.all()) #

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all()) #

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE) #
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items') #
    quantity = models.PositiveIntegerField(default=1) #
    added_at = models.DateTimeField(auto_now_add=True) #

    class Meta:
        unique_together = ('cart', 'product') #
        ordering = ['added_at'] #

    def __str__(self):
        return f"{self.quantity} x {self.product.name} en carrito {self.cart.id}" #

    @property
    def total_price(self):
        if self.product and self.product.price is not None:
             return self.product.price * self.quantity #
        return 0 #