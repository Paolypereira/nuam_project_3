from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    EmpresaViewSet,
    PaisViewSet,
    TopEmpresasPorPais,
    demo_empresas,
    convertir_moneda,
    home,
    empresas_sin_paginacion,
    mer_view,
)

router = DefaultRouter()
router.register(r"empresas", EmpresaViewSet, basename="empresa")
router.register(r"paises", PaisViewSet, basename="pais")

urlpatterns = [
    path("", home, name="home"),
    path("catalogo/", demo_empresas, name="catalogo"),
    path("catalogo-data/", empresas_sin_paginacion, name="catalogo-data"),
    path("mer/", mer_view, name="mer"),

    path("top-empresas/", TopEmpresasPorPais.as_view(), name="top-empresas"),
    path("api/convertir/", convertir_moneda, name="convertir-moneda"),
]

urlpatterns += router.urls

