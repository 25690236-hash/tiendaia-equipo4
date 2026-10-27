
"""Microservicio Ventas de TiendaIA - Laboratorio 3."""

import json
import os
from datetime import date

import redis
<<<<<<< HEAD
import requests
=======
import requests # cliente HTTP para llamar a otros microservicios
>>>>>>> 792bb31 (Lab3: Ventas publica el evento venta.creada)
from fastapi import FastAPI, HTTPException
from eventos import publicar # publicación de eventos en RabbitMQ (Lab. 3)
from pydantic import BaseModel, Field

<<<<<<< HEAD
from eventos import publicar


# Configuración
r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    decode_responses=True
)

=======
# ---------------------------------------------------------------- Configuración
# Conexión a Redis. "redis" es el nombre del contenedor en docker-compose.yml.
# decode_responses=True hace que Redis devuelva str en lugar de bytes.
r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), decode_responses=True)
# Las URL se leen de variables de entorno: en Docker Compose cada servicio se
# llama por su nombre (http://clientes:8000); fuera de Docker se pueden cambiar.
>>>>>>> 792bb31 (Lab3: Ventas publica el evento venta.creada)
CLIENTES_URL = os.getenv("CLIENTES_URL", "http://clientes:8000")
PRODUCTOS_URL = os.getenv("PRODUCTOS_URL", "http://productos:8000")
app = FastAPI(title="TiendaIA - Ventas")

<<<<<<< HEAD
TIEMPO_ESPERA = 5
sesion = requests.Session()
=======
TIEMPO_ESPERA = 5 # segundos: nunca esperar para siempre a otro servicio
sesion = requests.Session() # reutiliza conexiones TCP entre peticiones (más rápido)
>>>>>>> 792bb31 (Lab3: Ventas publica el evento venta.creada)

# ---------------------------------------------------------------- Modelo de entrada
class VentaIn(BaseModel):
    cliente_id: int = Field(gt=0)
    producto_id: int = Field(gt=0)
    cantidad: int = Field(gt=0, le=1000)
<<<<<<< HEAD
    fecha: date | None = None

=======
    fecha: date | None = None # si no se envía: hoy
>>>>>>> 792bb31 (Lab3: Ventas publica el evento venta.creada)

def consultar(url: str):
    """Consulta otro microservicio por HTTP."""
    resp = sesion.get(url, timeout=TIEMPO_ESPERA)
<<<<<<< HEAD

    if resp.status_code == 404:
        return None

    resp.raise_for_status()
=======
    if resp.status_code == 404: # el recurso no existe: no es un error del sistema
        return None
    resp.raise_for_status() # cualquier otro error (500, 503...) lanza excepción
>>>>>>> 792bb31 (Lab3: Ventas publica el evento venta.creada)
    return resp.json()
# ---------------------------------------------------------------- Endpoints
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
<<<<<<< HEAD

=======
>>>>>>> 792bb31 (Lab3: Ventas publica el evento venta.creada)
    producto = consultar(f"{PRODUCTOS_URL}/productos/{v.producto_id}")

    if producto is None:
        raise HTTPException(422, "El producto no existe")
<<<<<<< HEAD

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

=======
    
    # INCR: suma 1 a la clave de forma atómica y devuelve el nuevo valor.
    # Sirve como id autoincremental sin repetidos, aun con peticiones simultáneas.
    venta_id = r.incr("venta:siguiente_id")
    # Se guarda el precio del momento de la venta (si después cambia el precio
    # del producto, la venta conserva el valor original).
    venta = {"id": venta_id, **v.model_dump(mode="json"),
        "fecha": (v.fecha or date.today()).isoformat(),
        "precio": producto["precio"],
        "total": round(producto["precio"] * v.cantidad, 2)}
    # Cada venta es una clave de texto "venta:<id>" con el JSON como valor
    r.set(f"venta:{venta_id}", json.dumps(venta))
    r.rpush("ventas", venta_id) # lista ordenada de ids
    venta["evento_publicado"] = publicar("venta.creada", venta) # Lab. 3
>>>>>>> 792bb31 (Lab3: Ventas publica el evento venta.creada)
    return venta

@app.get("/ventas")
def listar():
<<<<<<< HEAD
    """Devuelve todas las ventas."""
    ids = r.lrange("ventas", 0, -1)

    if not ids:
        return []

    return [
        json.loads(v)
        for v in r.mget([f"venta:{i}" for i in ids])
        if v
    ]


=======
    """Devuelve todas las ventas en orden de registro (200)."""
    ids = r.lrange("ventas", 0, -1) # LRANGE 0 -1: toda la lista de ids
    if not ids:
        return []
    # MGET trae muchas claves en una sola ida y vuelta a Redis (más eficiente
    # que un GET por venta). "if v" descarta claves que ya no existan.
    return [json.loads(v) for v in r.mget([f"venta:{i}" for i in ids]) if v]
>>>>>>> 792bb31 (Lab3: Ventas publica el evento venta.creada)
@app.get("/ventas/{venta_id}")
def obtener(venta_id: int):
    """Devuelve una venta por su id."""
    v = r.get(f"venta:{venta_id}")

    if v is None:
        raise HTTPException(404, "Venta no encontrada")
<<<<<<< HEAD

    return json.loads(v)


=======
    return json.loads(v) # el valor se guardó como texto JSON
>>>>>>> 792bb31 (Lab3: Ventas publica el evento venta.creada)
@app.delete("/ventas/{venta_id}", status_code=204)
def eliminar(venta_id: int):
    """Elimina una venta."""
    if r.delete(f"venta:{venta_id}") == 0:
        raise HTTPException(404, "Venta no encontrada")
<<<<<<< HEAD

    r.lrem("ventas", 0, venta_id)
=======
    r.lrem("ventas", 0, venta_id) # también se quita su id de la lista
>>>>>>> 792bb31 (Lab3: Ventas publica el evento venta.creada)
