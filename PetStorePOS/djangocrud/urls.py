# URLs DjangoCRUD - PetStorePOS

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import home, chatbot
from djangocrud import views as djangocrud_views
from djangocrud.views import about, accessibility
from django.conf.urls.i18n import i18n_patterns

urlpatterns_trans = i18n_patterns(
    path('', home, name="home"),
    path("accounts/", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("catalog/", include("catalog.urls")),
    path('adoption/', include('adoption.urls')),
    path("acerca/", about, name="about"),
    path("cart/", include("cart.urls")),
    path("orders/", include("orders.urls")),
    path("accesibilidad/", accessibility, name="accessibility"),
    path("chatbot/", chatbot, name="chatbot"),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('favicon.ico', djangocrud_views.favicon_view, name='favicon'),
]

urlpatterns += urlpatterns_trans

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
