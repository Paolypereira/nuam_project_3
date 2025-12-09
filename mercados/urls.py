from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    EmpresaViewSet,
    PaisViewSet,
    TopEmpresasPorPais,
    empresas_sin_paginacion,
    convertir_moneda,
)

router = DefaultRouter()
router.register(r"empresas", EmpresaViewSet, basename="empresa")
router.register(r"paises", PaisViewSet, basename="pais")

urlpatterns = [
    path("top-empresas/", TopEmpresasPorPais.as_view(), name="top-empresas"),
    path("empresas-sin-paginacion/", empresas_sin_paginacion,
         name="empresas-sin-paginacion"),
    path("convertir/", convertir_moneda, name="convertir-moneda"),
]

urlpatterns += router.urls
