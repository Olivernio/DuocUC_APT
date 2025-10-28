from django.contrib import admin
from django.urls import path, include
from django.conf import settings             
from django.conf.urls.static import static    
from core.views import home
from djangocrud.views import about
from django.conf.urls.i18n import i18n_patterns

urlpatterns_trans = i18n_patterns(
    path('', home, name="home"),
    path("accounts/", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("catalog/", include("catalog.urls")),  
    path('adoption/', include('adoption.urls')),
    path("acerca/", about, name="about"),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')), # La vista para cambiar idioma
]

urlpatterns += urlpatterns_trans

# Para servir archivos de media en modo DEBUG 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
