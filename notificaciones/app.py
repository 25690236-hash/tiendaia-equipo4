
import json
import logging
import os
import threading
import time
from contextlib import asynccontextmanager

import pika
import redis
from fastapi import FastAPI, Query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBIT_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")

r = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    decode_responses=True
)


def al_recibir(canal, metodo, propiedades, cuerpo):
    """Procesa los eventos de ventas y guarda las notificaciones."""
    try:
        venta = json.loads(cuerpo)

        if not isinstance(venta, dict):
            raise ValueError("El mensaje no es un objeto JSON")

        campos = ["id", "cliente_id", "producto_id", "cantidad", "total"]

        for campo in campos:
            if campo not in venta:
                raise ValueError(f"Falta el campo obligatorio: {campo}")

        mensaje = (
            f"Venta {venta['id']}: cliente {venta['cliente_id']} "
            f"compro {venta['cantidad']} unidades del producto "
            f"{venta['producto_id']}. Total: ${venta['total']}"
        )

        notificacion = {
            "evento": metodo.routing_key,
            "mensaje": mensaje
        }

        r.lpush("notificaciones", json.dumps(notificacion))
        r.ltrim("notificaciones", 0, 99)

        canal.basic_ack(delivery_tag=metodo.delivery_tag)

        logger.info("Notificacion guardada: %s", mensaje)

    except (ValueError, KeyError, TypeError) as error:
        logger.warning("Mensaje invalido: %s", error)

        canal.basic_nack(
            delivery_tag=metodo.delivery_tag,
            requeue=False
        )


def consumir():
    """Conecta con RabbitMQ y consume eventos."""

    while True:
        conexion = None

        try:
            parametros = pika.ConnectionParameters(
                host=RABBIT_HOST,
                heartbeat=30,
                blocked_connection_timeout=10
            )

            conexion = pika.BlockingConnection(parametros)
            canal = conexion.channel()

            canal.exchange_declare(
                exchange="tienda.eventos",
                exchange_type="topic",
                durable=True
            )

            canal.queue_declare(
                queue="notificaciones",
                durable=True
            )

            canal.queue_bind(
                queue="notificaciones",
                exchange="tienda.eventos",
                routing_key="venta.*"
            )

            logger.info("Consumidor de notificaciones iniciado")

            canal.basic_consume(
                queue="notificaciones",
                on_message_callback=al_recibir,
                auto_ack=False
            )

            canal.start_consuming()

        except pika.exceptions.AMQPConnectionError as error:
            logger.warning("RabbitMQ no disponible: %s", error)
            time.sleep(3)

        except Exception:
            logger.exception("Error en el consumidor")
            time.sleep(3)

        finally:
            if conexion is not None and conexion.is_open:
                conexion.close()


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    hilo = threading.Thread(target=consumir, daemon=True)
    hilo.start()
    yield


app = FastAPI(
    title="TiendaIA - Notificaciones",
    lifespan=ciclo_de_vida
)


@app.get("/health")
def health():
    return {
        "servicio": "notificaciones",
        "status": "ok"
    }


@app.get("/notificaciones")
def obtener_notificaciones(
    limite: int = Query(default=20, ge=1, le=100)
):
    datos = r.lrange("notificaciones", 0, limite - 1)

    return [json.loads(item) for item in datos]
