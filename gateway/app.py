"""API Gateway de TiendaIA: punto único de entrada (Laboratorio 2).
Recibe todas las peticiones externas en /api/<servicio>/... y las reenvía
(proxy inverso) al microservicio correspondiente: Clientes, Productos, Ventas o IA.
El usuario solo conoce la dirección del gateway; los microservicios quedan ocultos
en la red interna de Docker. También ofrece /health con el estado de cada servicio.
"""
import os
import requests  # cliente HTTP para reenviar las peticiones a los microservicios
from fastapi import FastAPI, Request, Response
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware

# Configuración
# Tabla de ruteo: prefijo de la URL -> dirección interna del microservicio.
# En Docker Compose cada servicio se llama por su nombre (http://clientes:8000).
RUTAS = {
    "clientes": os.getenv("CLIENTES_URL", "http://clientes:8000"),
    "productos": os.getenv("PRODUCTOS_URL", "http://productos:8000"),
    "ventas": os.getenv("VENTAS_URL", "http://ventas:8000"),
    "ia": os.getenv("IA_URL", "http://ia:8000"),
}

app = FastAPI(title="TiendaIA - API Gateway")

# CORS (Cross-Origin Resource Sharing)
ORIGENES = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES,
    allow_methods=["*"],
    allow_headers=["*"]
)

sesion = requests.Session()  # conexiones persistentes
TIEMPO_ESPERA = 60  # generoso porque entrenar el modelo tarda
TIEMPO_SALUD = 3   # /health debe contestar rápido


# Endpoints
@app.get("/health")
async def salud():
    """Consulta /health de cada microservicio y resume su estado (200)."""
    estado = {}
    for nombre, url in RUTAS.items():
        try:
            r = await run_in_threadpool(sesion.get, f"{url}/health", timeout=TIEMPO_SALUD)
            estado[nombre] = r.status_code == 200
        except requests.RequestException:
            estado[nombre] = False
    return {"gateway": "ok", "servicios": estado}


@app.api_route("/api/{svc}", methods=["GET", "POST"])
@app.api_route("/api/{svc}/{ruta:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(svc: str, req: Request, ruta: str = ""):
    """Reenvía la petición al microservicio indicado y devuelve su respuesta tal cual."""
    if svc not in RUTAS:
        return Response(status_code=404)

    destino = f"{RUTAS[svc]}/{svc}" + (f"/{ruta}" if ruta else "")
    cuerpo = await req.body()

    r = await run_in_threadpool(
        sesion.request,
        req.method,
        destino,
        params=list(req.query_params.multi_items()),
        data=cuerpo,
        headers={"content-type": req.headers.get("content-type", "application/json")},
        timeout=TIEMPO_ESPERA,
        allow_redirects=False
    )

    return Response(r.content, r.status_code, media_type=r.headers.get("content-type"))