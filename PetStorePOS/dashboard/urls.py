from django.urls import path
from . import views 
from django.contrib.auth.decorators import login_required, user_passes_test 

app_name = "dashboard"

urlpatterns = [
    # Dashboard principal
    path(
        "", 
        views.index, 
        name="index"
    ),
    
    # Dashboard de Inventario
    path(
        "inventario/", 
        login_required(user_passes_test(lambda u: u.is_staff)(views.DashboardInventoryListView.as_view())), 
        name="inventario"
    ),
    
    # Dashboard de Adopciones (API)
    path(
        "adopciones/", 
        views.dashboard_adopciones_api_view,
        name="adopciones"
    ),
    
    # Dashboard de Punto de Venta (POS)
    path(
        "pos/", 
        login_required(user_passes_test(lambda u: u.is_staff)(views.DashboardPOSView.as_view())), 
        name="pos"
    ),

    # --- AÑADE ESTA URL PARA GESTIÓN DE USUARIOS ---
    path(
        "usuarios/", 
        login_required(user_passes_test(lambda u: u.is_staff)(views.DashboardUserListView.as_view())), 
        name="usuarios"
    ),
    # --- FIN DE LA URL AÑADIDA ---
    
    # Gestión de Reseñas
    path(
        "reseñas/",
        login_required(user_passes_test(lambda u: u.is_staff)(views.reviews_management)),
        name="reviews"
    ),
    
    # Exportación CSV
    path("exportar/productos/", views.export_products_csv, name="export_products_csv"),
    path("exportar/pedidos/", views.export_orders_csv, name="export_orders_csv"),
    path("exportar/usuarios/", views.export_users_csv, name="export_users_csv"),
    
    # Configuración
    path(
        "configuracion/",
        login_required(user_passes_test(lambda u: u.is_staff)(views.configuracion)),
        name="configuracion"
    ),
]