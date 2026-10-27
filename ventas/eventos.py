<<<<<<< HEAD

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
        if "://" in RABBITMQ_HOST:
            parametros = pika.URLParameters(RABBITMQ_HOST)
        else:
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
=======
"""Publicación de eventos de dominio en RabbitMQ (Laboratorio 3).
Módulo del microservicio Ventas. Cada vez que ocurre algo importante (p. ej. una
venta creada) se publica un evento en el exchange tipo topic "tienda.eventos".
Ventas no sabe quién escucha: cualquier servicio (como Notificaciones) puede
suscribirse sin que Ventas cambie (bajo acoplamiento).
"""
import json
import logging
import os
import pika # cliente de RabbitMQ (protocolo AMQP)
# ---------------------------------------------------------------- Configuración
RABBIT = os.getenv("RABBITMQ_HOST", "rabbitmq")
# Nombre del host (local) o URL amqp(s):// de un servicio administrado (CloudAMQP)
PARAMS = (pika.URLParameters(RABBIT) if "://" in RABBIT
else pika.ConnectionParameters(RABBIT))
EXCHANGE = "tienda.eventos"
def publicar(clave: str, datos: dict) -> bool:
    """Publica un evento; si el broker no responde, la venta NO se pierde.
    Recibe la routing key (p. ej. "venta.creada") y los datos del evento.
    Devuelve True si se publicó y False si RabbitMQ no estaba disponible.
    """
    try:
        con = pika.BlockingConnection(PARAMS)
        canal = con.channel()
        # Declarar el exchange es idempotente; durable=True sobrevive a reinicios
        canal.exchange_declare(EXCHANGE, exchange_type="topic", durable=True)
        # El exchange compara la routing key con los bindings de cada cola
        # (p. ej. "venta.*") y entrega una copia a cada cola que coincida.
        canal.basic_publish(exchange=EXCHANGE, routing_key=clave,

            body=json.dumps(datos),
            # delivery_mode=2: mensaje persistente (en disco)
            properties=pika.BasicProperties(
            delivery_mode=2, content_type="application/json"))

        con.close()
        return True
    except pika.exceptions.AMQPError as e:
        # La venta ya se guardó en Redis: un fallo del broker solo se registra
        logging.warning("No se publicó %s: %s", clave, e)
        return False
>>>>>>> 792bb31 (Lab3: Ventas publica el evento venta.creada)
