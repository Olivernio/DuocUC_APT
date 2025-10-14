from django.urls import path
from . import views

app_name = "adoption"

urlpatterns = [
    path("", views.mascotas_huachitos_view, name="list"),
    path("<int:pet_id>/", views.mascota_detail_view, name="mascota_detail"),
]
