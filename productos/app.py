"""Microservicio Productos de TiendaIA (Laboratorio 2).
Expone un CRUD de productos (nombre, precio, categoría) con FastAPI y guarda los
datos en MongoDB, una base de datos de documentos (cada producto es un JSON)[span_3](start_span)[span_3](end_span).
No llama a otros servicios: Ventas lo consulta por HTTP para obtener el precio y
validar que el producto exista; el API Gateway le reenvía las peticiones externas[span_4](start_span)[span_4](end_span).
"""
import os
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from pymongo import MongoClient, ReturnDocument

# Base de datos
# MONGO_URL llega por variable de entorno (p. ej. mongodb://mongo:27017)[span_5](start_span)[span_5](end_span).
db = MongoClient(os.environ["MONGO_URL"])["tienda"]

# Extensión del equipo: Índice único sobre 'id' al iniciar el servicio
# Evita IDs duplicados en MongoDB y acelera las búsquedas por ID
db.productos.create_index("id", unique=True)

app = FastAPI(title="TiendaIA - Productos")


# Modelo de entrada
class ProductoIn(BaseModel):
    """Datos de un producto enviados en el cuerpo JSON.
    Si no cumplen las reglas, FastAPI responde 422 automáticamente[span_6](start_span)[span_6](end_span).
    """
    nombre: str = Field(min_length=1, max_length=100)
    # Field(gt=0): "greater than 0", el precio debe ser estrictamente positivo[span_7](start_span)[span_7](end_span)
    precio: float = Field(gt=0)
    categoria: str = "general"  # valor por omisión si no se envía[span_8](start_span)[span_8](end_span)


def siguiente_id() -> int:
    """Id entero autoincremental (MongoDB no lo tiene: usamos un contador)[span_9](start_span)[span_9](end_span)."""
    # $inc suma 1 de forma ATÓMICA en el servidor: aunque lleguen dos
    # peticiones al mismo tiempo, nunca reciben el mismo id[span_10](start_span)[span_10](end_span).
    doc = db.contadores.find_one_and_update(
        {"_id": "productos"},
        {"$inc": {"valor": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    return doc["valor"]


# Endpoints
@app.get("/health")
def salud():
    """Verificación de salud usada por el gateway; responde 200[span_11](start_span)[span_11](end_span)."""
    return {"servicio": "productos", "status": "ok"}


@app.get("/productos")
def listar(
    categoria: str | None = None,
    precio_max: float | None = Query(default=None, gt=0)
):
    """Devuelve los productos (200), permitiendo filtros opcionales de categoría y precio máximo[span_12](start_span)[span_12](end_span)[span_13](start_span)[span_13](end_span)."""
    filtro = {}
    if categoria is not None:
        filtro["categoria"] = categoria
    if precio_max is not None:
        filtro["precio"] = {"$lte": precio_max}

    # {"_id": 0} es una proyección: excluye el campo _id interno de MongoDB[span_14](start_span)[span_14](end_span)
    return list(db.productos.find(filtro, {"_id": 0}))


@app.get("/productos/{producto_id}")
def obtener(producto_id: int):
    """Devuelve un producto por su id (200) o 404 si no existe[span_15](start_span)[span_15](end_span)."""
    p = db.productos.find_one({"id": producto_id}, {"_id": 0})
    if p is None:
        # Ventas interpreta este 404 como "el producto no existe[span_16](start_span)"[span_16](end_span)
        raise HTTPException(404, "Producto no encontrado")
    return p


@app.post("/productos", status_code=201)
def crear(p: ProductoIn):
    """Crea un producto con id nuevo. Responde 201 (Created) o 422 si es inválido[span_17](start_span)[span_17](end_span)."""
    doc = {"id": siguiente_id(), **p.model_dump()}
    db.productos.insert_one(dict(doc))
    return doc


@app.put("/productos/{producto_id}")
def actualizar(producto_id: int, p: ProductoIn):
    """Actualiza los campos de un producto (200) o responde 404 si no existe[span_18](start_span)[span_18](end_span)."""
    # $set reemplaza solo los campos indicados y conserva el resto del documento[span_19](start_span)[span_19](end_span)
    r = db.productos.update_one({"id": producto_id}, {"$set": p.model_dump()})
    if r.matched_count == 0:
        raise HTTPException(404, "Producto no encontrado")
    return {"id": producto_id, **p.model_dump()}


@app.delete("/productos/{producto_id}", status_code=204)
def eliminar(producto_id: int):
    """Borra un producto. Responde 204 (sin contenido) o 404 si no existe[span_20](start_span)[span_20](end_span)."""
    if db.productos.delete_one({"id": producto_id}).deleted_count == 0:
        raise HTTPException(404, "Producto no encontrado")