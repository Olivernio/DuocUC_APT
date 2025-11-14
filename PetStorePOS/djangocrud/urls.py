from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import home
from djangocrud.views import about, accessibility
from django.conf.urls.i18n import i18n_patterns

# Define aquí las URLs que quieres traducir
urlpatterns_trans = i18n_patterns(
    path('', home, name="home"), # <- path ahora está definido
    path("accounts/", include("accounts.urls")), # <- path ahora está definido
    path("dashboard/", include("dashboard.urls")), # <- path ahora está definido
    path("catalog/", include("catalog.urls")), # <- path ahora está definido
    path('adoption/', include('adoption.urls')), # <- path ahora está definido
    path("acerca/", about, name="about"), # <- path ahora está definido
    path("cart/", include("cart.urls")), # <- path ahora está definido
    path("accesibilidad/", accessibility, name="accessibility"),
    path('orders/', include('orders.urls')),
)

# Define aquí las URLs que NO quieres traducir (como admin o i18n)
urlpatterns = [
    path('admin/', admin.site.urls), # <- path ahora está definido
    path('i18n/', include('django.conf.urls.i18n')), # <- path ahora está definido
]

# Añade las URLs traducibles al final
urlpatterns += urlpatterns_trans

# Servir archivos de media en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)