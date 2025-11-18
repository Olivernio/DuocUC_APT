from django.db import models
from django.utils.translation import gettext_lazy as _ 

class Category(models.TextChoices):
    FOOD = "FOOD", _("Alimentos")
    MED = "MED", _("Medicamentos")
    ACC = "ACC", _("Accesorios")


class Product(models.Model):
    """
    Modelo que representa un producto en el catálogo.
    
    Relaciones:
    - reviews: Reseñas del producto (ProductReview)
    - favorited_by: Usuarios que han marcado este producto como favorito (ManyToMany)
    - movements: Movimientos de stock (StockMovement)
    - order_items: Items de órdenes que incluyen este producto (OrderItem)
    
    Campos importantes:
    - sku: Código único del producto (máx 3 caracteres)
    - category: Categoría del producto (FOOD, MED, ACC)
    - stock: Cantidad disponible en inventario
    - is_active: Si el producto está activo y visible en el catálogo
    """
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
        verbose_name = _("Producto")
        verbose_name_plural = _("Productos")
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        return f"{self.sku} · {self.name}"
    
    def get_average_rating(self):
        """
        Calcula el promedio de rating de las reseñas aprobadas.
        
        Returns:
            float: Promedio de rating (0-5) o 0 si no hay reseñas
        """
        from django.db.models import Avg
        avg = self.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0
    
    def get_total_reviews(self):
        """
        Obtiene el número total de reseñas aprobadas.
        
        Returns:
            int: Número de reseñas aprobadas
        """
        return self.reviews.filter(is_approved=True).count()

class StockMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="movements")
    delta = models.IntegerField("Cantidad (+ingreso / -salida)")
    note = models.CharField("Nota", max_length=140, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sign = "+" if self.delta >= 0 else ""
        return f"{self.product.sku} {sign}{self.delta}"


class ProductReview(models.Model):
    """
    Modelo para reseñas de productos.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_("Producto")
    )
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='product_reviews',
        verbose_name=_("Usuario")
    )
    rating = models.PositiveIntegerField(
        _("Calificación"),
        choices=[(i, i) for i in range(1, 6)],
        help_text=_("Calificación de 1 a 5 estrellas")
    )
    comment = models.TextField(
        _("Comentario"),
        max_length=1000,
        blank=True
    )
    is_approved = models.BooleanField(
        _("Aprobado"),
        default=False,
        help_text=_("Las reseñas deben ser aprobadas por un administrador antes de mostrarse")
    )
    created_at = models.DateTimeField(_("Fecha de Creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de Actualización"), auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = [['product', 'user']]
        verbose_name = _("Reseña de Producto")
        verbose_name_plural = _("Reseñas de Productos")

    def __str__(self):
        return f"Reseña de {self.user.username} para {self.product.name} - {self.rating} estrellas"