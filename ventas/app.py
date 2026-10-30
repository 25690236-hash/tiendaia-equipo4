
"""Microservicio Ventas de TiendaIA - Laboratorio 3."""

import json
import os
from datetime import date

import redis
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from eventos import publicar


# Configuración
r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    decode_responses=True
)

CLIENTES_URL = os.getenv("CLIENTES_URL", "http://clientes:8000")
PRODUCTOS_URL = os.getenv("PRODUCTOS_URL", "http://productos:8000")

app = FastAPI(title="TiendaIA - Ventas")

TIEMPO_ESPERA = 5
sesion = requests.Session()


# Modelo de entrada
class VentaIn(BaseModel):
    cliente_id: int = Field(gt=0)
    producto_id: int = Field(gt=0)
    cantidad: int = Field(gt=0, le=1000)
    fecha: date | None = None


def consultar(url: str):
    """Consulta otro microservicio por HTTP."""
    resp = sesion.get(url, timeout=TIEMPO_ESPERA)

    if resp.status_code == 404:
        return None

    resp.raise_for_status()
    return resp.json()


# Endpoints
@app.get("/health")
def salud():
    return {
        "servicio": "ventas",
        "status": "ok",
        "redis": r.ping()
    }


@app.post("/ventas", status_code=201)
def crear(v: VentaIn):
    """Registra una venta y publica su evento en RabbitMQ."""

    if consultar(f"{CLIENTES_URL}/clientes/{v.cliente_id}") is None:
        raise HTTPException(422, "El cliente no existe")

    producto = consultar(f"{PRODUCTOS_URL}/productos/{v.producto_id}")

    if producto is None:
        raise HTTPException(422, "El producto no existe")

    venta_id = r.incr("venta:siguiente_id")

    venta = {
        "id": venta_id,
        **v.model_dump(mode="json"),
        "fecha": (v.fecha or date.today()).isoformat(),
        "precio": producto["precio"],
        "total": round(producto["precio"] * v.cantidad, 2)
    }

    # Guardar la venta en Redis
    r.set(f"venta:{venta_id}", json.dumps(venta))
    r.rpush("ventas", venta_id)

    # Publicar el evento en RabbitMQ
    venta["evento_publicado"] = publicar("venta.creada", venta)

    return venta


@app.get("/ventas")
def listar():
    """Devuelve todas las ventas."""
    ids = r.lrange("ventas", 0, -1)

    if not ids:
        return []

    return [
        json.loads(v)
        for v in r.mget([f"venta:{i}" for i in ids])
        if v
    ]


@app.get("/ventas/{venta_id}")
def obtener(venta_id: int):
    """Devuelve una venta por su id."""
    v = r.get(f"venta:{venta_id}")

    if v is None:
        raise HTTPException(404, "Venta no encontrada")

    return json.loads(v)


@app.delete("/ventas/{venta_id}", status_code=204)
def eliminar(venta_id: int):
    """Elimina una venta."""
    if r.delete(f"venta:{venta_id}") == 0:
        raise HTTPException(404, "Venta no encontrada")

    r.lrem("ventas", 0, venta_id)
