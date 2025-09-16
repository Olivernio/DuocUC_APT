from django.db import models


class EstadoMascota(models.TextChoices):
    Disponible = "AVAILABLE", "Disponible"
    Pendiente = "PENDING", "En Proceso"
    Adoptado = "ADOPTED", "Adoptado"


class Especies(models.TextChoices):
    DOG = "DOG", "Perro"
    CAT = "CAT", "Gato"
    Hamsters = "HAMSTERS", "Hamsters"
    OTHER = "OTHER", "Otro"


class Mascota(models.Model):
    Nombre = models.CharField("Nombre", max_length=80)
    Especie = models.CharField(
        "Especie", max_length=10, choices=Especies.choices, default=Especies.DOG)
    Raza = models.CharField("Raza", max_length=80, blank=True)
    Edad_Años = models.PositiveIntegerField("Edad (años)", default=0)
    description = models.TextField("Descripción", blank=True)
    is_Vacunado = models.BooleanField("Vacunado", default=False)
    is_castrado = models.BooleanField("Esterilizado", default=False)
    Estado = models.CharField(
        "Estado", max_length=12, choices=EstadoMascota.choices, default=EstadoMascota.Disponible)
    Imagen = models.ImageField(
        "Foto", upload_to="pets/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


    def __str__(self):
        return f"{self.Nombre} ({self.get_Especie_display()})"


class AdoptionRequest(models.Model):
    Mascota = models.ForeignKey(
        Mascota, on_delete=models.CASCADE, related_name="requests")
    full_name = models.CharField("Nombre completo", max_length=120)
    email = models.EmailField("Email")
    Telefono = models.CharField("Teléfono", max_length=30, blank=True)
    Mensaje = models.TextField("Mensaje", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField("Procesada", default=False)

    def __str__(self):
        return f"Solicitud {self.full_name} → {self.pet.name}"
