from django.urls import path
from . import views

urlpatterns = [
    path('ping/', views.ping, name='ping'),
    path('convertir-moneda/', views.convertir_moneda, name='convertir-moneda'),
]
