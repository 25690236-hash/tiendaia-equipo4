
import json
import logging
import os

import pika

logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")


def publicar(tipo_evento: str, datos: dict) -> bool:
    """Publica un evento en RabbitMQ."""

    conexion = None

    try:
        parametros = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            connection_attempts=3,
            retry_delay=2,
            socket_timeout=5
        )

        conexion = pika.BlockingConnection(parametros)
        canal = conexion.channel()

        canal.exchange_declare(
            exchange="tienda.eventos",
            exchange_type="topic",
            durable=True
        )

        canal.basic_publish(
            exchange="tienda.eventos",
            routing_key=tipo_evento,
            body=json.dumps(datos),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json"
            )
        )

        logger.info("Evento publicado: %s", tipo_evento)
        return True

    except pika.exceptions.AMQPError:
        logger.exception("No se pudo publicar el evento: %s", tipo_evento)
        return False

    except Exception:
        logger.exception("Error inesperado al publicar el evento")
        return False

    finally:
        if conexion is not None and conexion.is_open:
            conexion.close()
