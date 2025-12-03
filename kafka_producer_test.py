import json
from confluent_kafka import Producer
from kafka_config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC_EMPRESAS

producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})

def delivery_report(err, msg):
    if err is not None:
        print(f"Fallo al enviar mensaje: {err}")
    else:
        print(
            f"Mensaje enviado a {msg.topic()} [partición {msg.partition()}] offset {msg.offset()}"
        )

if __name__ == "__main__":
    datos = {
        "ticker": "NUAM",
        "nombre": "Holding Bursátil Regional",
        "pais": "CL",
        "moneda": "CLP",
        "capitalizacion": 457.86,
    }

    value = json.dumps(datos).encode("utf-8")
    producer.produce(
        topic=KAFKA_TOPIC_EMPRESAS,
        value=value,
        callback=delivery_report,
    )
    producer.flush()
