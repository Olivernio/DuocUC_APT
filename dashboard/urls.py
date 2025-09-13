from django.urls import path
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import TemplateView
app_name= "dashboard"

#Con esta Funcion es que solo usuario que tenga staff puedan entrar
staff_required = user_passes_test(lambda u: u.is_staff)

urlpatterns = [
    path(
        "",
        staff_required(  # verifica que sea staff
            login_required(  # verifica que esté logeado
                TemplateView.as_view(template_name="dashboard/index.html")
            )
        ),
        name="index",
    ),
]