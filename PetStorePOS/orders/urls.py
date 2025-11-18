from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.checkout_view, name="checkout"),
    path("mis-pedidos/", views.order_list, name="order_list"),
    path("pedido/<int:order_id>/", views.order_detail, name="order_detail"),
    # URLs para admin
    path("admin/", views.admin_order_list, name="admin_order_list"),
    path("admin/<int:order_id>/", views.admin_order_detail, name="admin_order_detail"),
]

