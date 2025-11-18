from django.urls import path
from .views import (
    ProductListView, ProductCreateView, ProductUpdateView, 
    ProductDeleteView, ProductDetailView, create_review
)

app_name = "catalog"
urlpatterns = [
    path("", ProductListView.as_view(), name="product_list"),
    path("<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path("<int:product_id>/resena/", create_review, name="create_review"),
    path("nuevo/", ProductCreateView.as_view(), name="product_create"),
    path("<int:pk>/editar/", ProductUpdateView.as_view(), name="product_update"),
    path("<int:pk>/eliminar/", ProductDeleteView.as_view(), name="product_delete"),
]
