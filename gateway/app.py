
"""API Gateway de TiendaIA - Laboratorio 3.
Punto único de entrada para los microservicios.
"""

import os
import requests

from fastapi import FastAPI, Request, Response
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware


# Configuración de rutas
RUTAS = {
    "clientes": os.getenv("CLIENTES_URL", "http://clientes:8000"),
    "productos": os.getenv("PRODUCTOS_URL", "http://productos:8000"),
    "ventas": os.getenv("VENTAS_URL", "http://ventas:8000"),
    "ia": os.getenv("IA_URL", "http://ia:8000"),
    "notificaciones": os.getenv(
        "NOTIFICACIONES_URL",
        "http://notificaciones:8000"
    ),
}


app = FastAPI(title="TiendaIA - API Gateway")


# Configuración CORS
ORIGENES = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "*").split(",")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


sesion = requests.Session()

TIEMPO_ESPERA = 60
TIEMPO_SALUD = 3


# Endpoint de salud
@app.get("/health")
async def salud():
    """Consulta el estado de todos los microservicios."""

    estado = {}

    for nombre, url in RUTAS.items():
        try:
            r = await run_in_threadpool(
                sesion.get,
                f"{url}/health",
                timeout=TIEMPO_SALUD
            )

            estado[nombre] = r.status_code == 200

        except requests.RequestException:
            estado[nombre] = False

    return {
        "gateway": "ok",
        "servicios": estado
    }


# Proxy para los microservicios
@app.api_route("/api/{svc}", methods=["GET", "POST"])
@app.api_route(
    "/api/{svc}/{ruta:path}",
    methods=["GET", "POST", "PUT", "DELETE"]
)
async def proxy(svc: str, req: Request, ruta: str = ""):
    """Reenvía las peticiones al microservicio correspondiente."""

    if svc not in RUTAS:
        return Response(status_code=404)

    destino = f"{RUTAS[svc]}/{svc}" + (
        f"/{ruta}" if ruta else ""
    )

    cuerpo = await req.body()

    r = await run_in_threadpool(
        sesion.request,
        req.method,
        destino,
        params=list(req.query_params.multi_items()),
        data=cuerpo,
        headers={
            "content-type": req.headers.get(
                "content-type",
                "application/json"
            )
        },
        timeout=TIEMPO_ESPERA,
        allow_redirects=False
    )

    return Response(
        r.content,
        r.status_code,
        media_type=r.headers.get("content-type")
    )
