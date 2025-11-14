from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # URLs para usuarios
    path('checkout/', views.checkout_view, name='checkout'),
    path('pedido/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('mis-pedidos/', views.order_list_view, name='order_list'),
    
    # URLs para administradores
    path('admin/pedidos/', views.admin_order_list_view, name='admin_order_list'),
    path('admin/pedido/<int:order_id>/', views.admin_order_detail_view, name='admin_order_detail'),
]