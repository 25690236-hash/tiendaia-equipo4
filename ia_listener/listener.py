"""Segundo suscriptor: solicita reentrenar el modelo cada 50 ventas."""

import json
import os
import time

import pika
import redis
import requests

RABBIT = os.getenv("RABBITMQ_HOST", "rabbitmq")
PARAMS = (
    pika.URLParameters(RABBIT)
    if "://" in RABBIT
    else pika.ConnectionParameters(RABBIT)
)
IA_URL = os.getenv("IA_URL", "http://ia:8000").rstrip("/")

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    decode_responses=True
)


def al_recibir(canal, metodo, propiedades, cuerpo):
    try:
        venta = json.loads(cuerpo)
        if not isinstance(venta, dict):
            raise ValueError("El evento debe ser un objeto JSON")
    except Exception as error:
        print(f"Mensaje inválido: {error}", flush=True)
        canal.basic_nack(
            delivery_tag=metodo.delivery_tag,
            requeue=False
        )
        return

    try:
        total = r.incr("ia:listener:ventas")
        print(f"Evento recibido; contador={total}", flush=True)

        if total % 50 == 0:
            respuesta = requests.post(f"{IA_URL}/ia/train", timeout=120)
            print(
                f"Reentrenamiento solicitado: HTTP {respuesta.status_code}",
                flush=True
            )

    except Exception as error:
        print(f"Error al procesar evento: {error}", flush=True)

    canal.basic_ack(delivery_tag=metodo.delivery_tag)


while True:
    try:
        conexion = pika.BlockingConnection(PARAMS)
        canal = conexion.channel()

        canal.exchange_declare(
            exchange="tienda.eventos",
            exchange_type="topic",
            durable=True
        )
        canal.queue_declare(queue="ia_listener", durable=True)
        canal.queue_bind(
            queue="ia_listener",
            exchange="tienda.eventos",
            routing_key="venta.*"
        )
        canal.basic_qos(prefetch_count=1)
        canal.basic_consume(
            queue="ia_listener",
            on_message_callback=al_recibir,
            auto_ack=False
        )

        print("IA-Listener conectado y esperando ventas", flush=True)
        canal.start_consuming()

    except pika.exceptions.AMQPConnectionError as error:
        print(f"RabbitMQ no disponible: {error}. Reintentando...", flush=True)
        time.sleep(3)