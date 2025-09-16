from django.urls import path
from . import views

app_name = "adoption"

urlpatterns = [
    path("", views.list_Mascotas, name="lista"),
    path("<int:pk>/", views.Detalle_Mascota, name="detalle"),
    path("<int:pk>/Solicitud/", views.Enviar_Solicitud, name="solicitud"),
]