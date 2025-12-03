from confluent_kafka import Consumer
from kafka_config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC_EMPRESAS

consumer_conf = {
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
    "group.id": "nuam-consumidores",
    "auto.offset.reset": "earliest",
}

consumer = Consumer(consumer_conf)
consumer.subscribe([KAFKA_TOPIC_EMPRESAS])

if __name__ == "__main__":
    print("Esperando mensajes de Kafka...")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Error en consumidor: {msg.error()}")
                continue

            print("Mensaje recibido:", msg.value().decode("utf-8"))
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
