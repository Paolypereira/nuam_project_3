from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.http import HttpResponseRedirect
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from mercados.views import (
    home,
    mer_view,
    demo_empresas,
    empresas_sin_paginacion,
    signup_view,
    mi_cuenta,
    editar_cuenta,
    eliminar_cuenta,
    convertidor_view,
    convertir_moneda,
)

def redirect_to_site(request):
    return HttpResponseRedirect(settings.ADMIN_SITE_URL)

urlpatterns = [
    path("ver-sitio/", redirect_to_site, name="ver-sitio"),

    path("", home, name="home"),
    path("catalogo/", demo_empresas, name="catalogo"),
    path("catalogo-data/", empresas_sin_paginacion, name="catalogo-data"),
    path("mer/", mer_view, name="mer"),

    path("convertir-moneda/", convertidor_view, name="convertidor"),
    path("api/convertir-moneda/", convertir_moneda, name="convertir-moneda-api"),

    path(
        "cuenta/login/",
        auth_views.LoginView.as_view(template_name="cuenta/login.html"),
        name="login",
    ),
    path(
        "cuenta/logout/",
        auth_views.LogoutView.as_view(next_page="home"),
        name="logout",
    ),
    path("cuenta/registro/", signup_view, name="signup"),
    path("cuenta/", mi_cuenta, name="mi-cuenta"),
    path("cuenta/editar/", editar_cuenta, name="editar-cuenta"),
    path("cuenta/eliminar/", eliminar_cuenta, name="eliminar-cuenta"),

    path("api/", include("mercados.urls")),   # <‑‑ aquí se engancha la API REST

    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
]

schema_view = get_schema_view(
    openapi.Info(
        title="NUAM API",
        default_version="v1",
        description="API REST de empresas, países y conversor NUAM",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns += [
    path("docs/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

handler404 = "mercados.views.error_404"
handler500 = "mercados.views.error_500"
