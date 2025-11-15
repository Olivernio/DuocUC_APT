from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User 

class Category(models.TextChoices):
    FOOD = "FOOD", _("Alimentos")
    MED = "MED", _("Medicamentos")
    ACC = "ACC", _("Accesorios")


class Product(models.Model):
    sku = models.CharField(_("SKU"), max_length=3, unique=True)
    name = models.CharField(_("Nombre"), max_length=120)
    category = models.CharField(_("Categoría"), max_length=8, choices=Category.choices)
    price = models.DecimalField(_("Precio"), max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(_("Stock"), default=0)
    description = models.TextField(_("Descripción"), blank=True)
    image = models.ImageField(_("Imagen"), upload_to="products/", blank=True, null=True)
    is_active = models.BooleanField(_("Activo"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.sku} · {self.name}"
    
    def get_average_rating(self):
        from django.db.models import Avg
        avg = self.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0
    
    def get_total_reviews(self):
        return self.reviews.filter(is_approved=True).count()

class StockMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="movements")
    delta = models.IntegerField("Cantidad (+ingreso / -salida)")
    note = models.CharField("Nota", max_length=140, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sign = "+" if self.delta >= 0 else ""
        return f"{self.product.sku} {sign}{self.delta}"

#modelo de reseñas poara productos.
class ProductReview(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_("Producto")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Usuario")
    )
    rating = models.PositiveIntegerField(
        _("Calificación"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_("Calificación de 1 a 5 estrellas")
    )
    comment = models.TextField(
        _("Comentario"),
        help_text=_("Tu opinión sobre el producto")
    )
    is_approved = models.BooleanField(
        _("Aprobada"),
        default=False,
        help_text=_("Las reseñas deben ser aprobadas por un administrador")
    )
    created_at = models.DateTimeField(
        _("Fecha de Creación"),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _("Reseña de Producto")
        verbose_name_plural = _("Reseñas de Productos")
        ordering = ['-created_at']
        # Un usuario solo puede dejar una reseña por producto
        unique_together = [['product', 'user']]
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}/5)"
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User 

class Category(models.TextChoices):
    FOOD = "FOOD", _("Alimentos")
    MED = "MED", _("Medicamentos")
    ACC = "ACC", _("Accesorios")


class Product(models.Model):
    sku = models.CharField(_("SKU"), max_length=3, unique=True)
    name = models.CharField(_("Nombre"), max_length=120)
    category = models.CharField(_("Categoría"), max_length=8, choices=Category.choices)
    price = models.DecimalField(_("Precio"), max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(_("Stock"), default=0)
    description = models.TextField(_("Descripción"), blank=True)
    image = models.ImageField(_("Imagen"), upload_to="products/", blank=True, null=True)
    is_active = models.BooleanField(_("Activo"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.sku} · {self.name}"
    
    def get_average_rating(self):
        
        #Calcula el promedio de calificaciones de las reseñas aprobadas.
        #Retorna un número decimal con 1 decimal (ej: 4.5)
        from django.db.models import Avg
        avg = self.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0
    
    def get_total_reviews(self):
        #Cuenta el total de reseñas aprobadas para este producto.
        return self.reviews.filter(is_approved=True).count()

class StockMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="movements")
    delta = models.IntegerField("Cantidad (+ingreso / -salida)")
    note = models.CharField("Nota", max_length=140, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sign = "+" if self.delta >= 0 else ""
        return f"{self.product.sku} {sign}{self.delta}"

#Modelo para reseñas de productos
class ProductReview(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_("Producto")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Usuario")
    )
    rating = models.PositiveIntegerField(
        _("Calificación"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_("Calificación de 1 a 5 estrellas")
    )
    comment = models.TextField(
        _("Comentario"),
        help_text=_("Tu opinión sobre el producto")
    )
    is_approved = models.BooleanField(
        _("Aprobada"),
        default=False,
        help_text=_("Las reseñas deben ser aprobadas por un administrador")
    )
    created_at = models.DateTimeField(
        _("Fecha de Creación"),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _("Reseña de Producto")
        verbose_name_plural = _("Reseñas de Productos")
        ordering = ['-created_at']
        # Un usuario solo puede dejar una reseña por producto
        unique_together = [['product', 'user']]
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}/5)"
