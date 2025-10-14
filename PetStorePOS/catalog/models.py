from django.db import models

class Category(models.TextChoices):
    FOOD = "FOOD", "Alimentos"
    MED = "MED", "Medicamentos"
    ACC = "ACC", "Accesorios"


class Product(models.Model):
    sku = models.CharField("SKU", max_length=3, unique=True)
    name = models.CharField("Nombre", max_length=120)
    category = models.CharField("Categoría", max_length=8, choices=Category.choices)
    price = models.DecimalField("Precio", max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField("Stock", default=0)
    description = models.TextField("Descripción", blank=True)
    image = models.ImageField("Imagen", upload_to="products/", blank=True, null=True)  # requiere Pillow Installar y agregar en requeriments
    is_active = models.BooleanField("Activo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.sku} · {self.name}"

class StockMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="movements")
    delta = models.IntegerField("Cantidad (+ingreso / -salida)")
    note = models.CharField("Nota", max_length=140, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sign = "+" if self.delta >= 0 else ""
        return f"{self.product.sku} {sign}{self.delta}"
