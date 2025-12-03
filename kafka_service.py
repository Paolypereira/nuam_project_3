# kafka_service.py
import json
from confluent_kafka import Producer
from kafka_config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC_EMPRESAS

# Crear un solo Producer global (reutilizarlo es buena práctica). [web:177][web:205]
producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})


def publicar_evento_empresa(datos: dict):
    """Publica un JSON de empresa en el topic nuam.empresas.ingreso."""
    value = json.dumps(datos).encode("utf-8")
    producer.produce(KAFKA_TOPIC_EMPRESAS, value=value)
    # flush pequeño para desarrollo; en producción se optimiza. [web:190]
    producer.flush(1)
