# mercados/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Empresa, empresa_a_dict
from kafka_service import publicar_evento_empresa


@receiver(post_save, sender=Empresa)
def enviar_evento_empresa(sender, instance, created, **kwargs):
    """Envía un evento a Kafka cuando se crea o actualiza una Empresa."""
    datos = empresa_a_dict(instance)
    datos["accion"] = "CREAR" if created else "EDITAR"
    publicar_evento_empresa(datos)
