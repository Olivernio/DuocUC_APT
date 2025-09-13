from django.contrib import admin
from django.urls import path, include
from django.conf import settings             
from django.conf.urls.static import static    
from core.views import home 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name="home"),
    path("accounts/", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("catalog/", include("catalog.urls")),  
    path("adopcion/", include("adoption.urls")),


]

# Para servir archivos de media en modo DEBUG 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
