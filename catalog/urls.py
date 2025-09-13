from django.urls import path
from .views import (
    ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView
)

app_name = "catalog"

urlpatterns = [
    path("",        ProductListView.as_view(),  name="product_list"),
    path("nuevo/",  ProductCreateView.as_view(), name="product_create"),
    path("<int:pk>/editar/", ProductUpdateView.as_view(), name="product_update"),
    path("<int:pk>/eliminar/", ProductDeleteView.as_view(), name="product_delete"),
]
