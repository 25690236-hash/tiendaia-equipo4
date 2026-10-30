"""Solicitudes de inferencia asíncronas de TiendaIA (Laboratorio 3).

POST /ia/solicitudes: registra y envía una solicitud a RabbitMQ.
GET /ia/solicitudes/{id}: consulta su estado o resultado en Redis.
"""

import json
import os
import uuid

import pika
import redis
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# --------------------------------------------------------- Configuración

RABBIT = os.getenv("RABBITMQ_HOST", "rabbitmq")

PARAMS = (
    pika.URLParameters(RABBIT)
    if "://" in RABBIT
    else pika.ConnectionParameters(RABBIT)
)

COLA = "inferencias"

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    decode_responses=True
)

router = APIRouter()


# --------------------------------------------------------- Datos de entrada

class Solicitud(BaseModel):
    producto_id: int = Field(gt=0)
    mes: int = Field(ge=1, le=12)
    precio: float = Field(gt=0)


# --------------------------------------------------------- Crear solicitud

@router.post("/ia/solicitudes", status_code=202)
def crear_solicitud(solicitud: Solicitud):

    solicitud_id = uuid.uuid4().hex

    datos = {
        "id": solicitud_id,
        **solicitud.model_dump()
    }

    # Guardar estado inicial en Redis
    r.set(
        f"solicitud:{solicitud_id}",
        json.dumps({
            "estado": "pendiente"
        }),
        ex=3600
    )

    try:
        conexion = pika.BlockingConnection(PARAMS)
        canal = conexion.channel()

        # Crear cola durable
        canal.queue_declare(
            queue=COLA,
            durable=True
        )

        # Publicar mensaje persistente en RabbitMQ
        canal.basic_publish(
            exchange="",
            routing_key=COLA,
            body=json.dumps(datos),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json"
            )
        )

        conexion.close()

    except pika.exceptions.AMQPError as e:
        r.set(
            f"solicitud:{solicitud_id}",
            json.dumps({
                "estado": "error",
                "detalle": "No se pudo enviar la solicitud a RabbitMQ"
            }),
            ex=3600
        )

        raise HTTPException(
            status_code=503,
            detail=f"Error al conectar con RabbitMQ: {str(e)}"
        )

    return {
        "id": solicitud_id,
        "estado": "pendiente"
    }


# --------------------------------------------------------- Consultar solicitud

@router.get("/ia/solicitudes/{solicitud_id}")
def consultar_solicitud(solicitud_id: str):

    resultado = r.get(f"solicitud:{solicitud_id}")

    if resultado is None:
        raise HTTPException(
            status_code=404,
            detail="Solicitud no encontrada o expirada"
        )

    return {
        "id": solicitud_id,
        **json.loads(resultado)
    }