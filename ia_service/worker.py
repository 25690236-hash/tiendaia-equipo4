
"""Worker de inferencia de TiendaIA (Laboratorio 3).

Consume solicitudes de RabbitMQ, realiza predicciones con el modelo
entrenado y guarda los resultados en Redis.
"""

import json
import os
import socket
import time

import joblib
import pandas as pd
import pika
import redis


# --------------------------------------------------------- Configuración

RABBIT = os.getenv("RABBITMQ_HOST", "rabbitmq")

PARAMS = (
    pika.URLParameters(RABBIT)
    if "://" in RABBIT
    else pika.ConnectionParameters(RABBIT)
)

MODELO = os.getenv("MODELO_PATH", "/modelos/modelo.joblib")

RETARDO = float(os.getenv("RETARDO_MS", "200")) / 1000

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    decode_responses=True
)

# El modelo se carga una sola vez por worker
modelo = None


# --------------------------------------------------------- Procesamiento

def procesar(canal, metodo, propiedades, cuerpo):
    """Procesa una solicitud recibida desde RabbitMQ."""

    global modelo

    try:
        solicitud = json.loads(cuerpo)

        # Cargar el modelo solamente la primera vez
        if modelo is None:
            modelo = joblib.load(MODELO)

        # Preparar los datos para la predicción
        x = pd.DataFrame(
            [[
                solicitud["producto_id"],
                solicitud["mes"],
                solicitud["precio"]
            ]],
            columns=["producto_id", "mes", "precio"]
        )

        # Simular el tiempo de procesamiento
        time.sleep(RETARDO)

        resultado = {
            "estado": "listo",
            "worker": f"{socket.gethostname()}:{os.getpid()}",
            "cantidad_estimada": round(
                float(modelo.predict(x)[0]),
                1
            )
        }

    except Exception as e:
        print("Error al procesar:", e, flush=True)

        # Registrar el error en Redis si la solicitud tiene ID
        if isinstance(locals().get("solicitud"), dict):
            if "id" in solicitud:
                r.set(
                    f"solicitud:{solicitud['id']}",
                    json.dumps({
                        "estado": "error",
                        "detalle": str(e)
                    }),
                    ex=3600
                )

        # Rechazar el mensaje sin volver a encolarlo
        canal.basic_nack(
            delivery_tag=metodo.delivery_tag,
            requeue=False
        )
        return

    # Guardar el resultado en Redis
    r.set(
        f"solicitud:{solicitud['id']}",
        json.dumps(resultado),
        ex=3600
    )

    # Confirmar el mensaje al terminar
    canal.basic_ack(
        delivery_tag=metodo.delivery_tag
    )


# --------------------------------------------------------- Ciclo principal

while True:
    try:
        conexion = pika.BlockingConnection(PARAMS)
        canal = conexion.channel()

        # Declarar la cola compartida con cola.py
        canal.queue_declare(
            queue="inferencias",
            durable=True
        )

        # Reparto justo: un mensaje a la vez por worker
        canal.basic_qos(prefetch_count=1)

        canal.basic_consume(
            queue="inferencias",
            on_message_callback=procesar
        )

        print("worker listo", flush=True)

        canal.start_consuming()

    except pika.exceptions.AMQPConnectionError:
        print("RabbitMQ no disponible. Reintentando...", flush=True)
        time.sleep(3)
