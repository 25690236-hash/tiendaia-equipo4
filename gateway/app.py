<<<<<<< HEAD
<<<<<<< HEAD

"""API Gateway de TiendaIA - Laboratorio 3.
Punto único de entrada para los microservicios.
=======
"""API Gateway de TiendaIA: punto único de entrada (Laboratorio 2).

Recibe todas las peticiones externas en /api/<servicio>/... y las reenvía
(proxy inverso) al microservicio correspondiente: Clientes, Productos, Ventas o IA.
El usuario solo conoce la dirección del gateway; los microservicios quedan ocultos
en la red interna de Docker. También ofrece /health con el estado de cada servicio.
>>>>>>> b32faee (Lab 2: pruebas)
=======
"""API Gateway de TiendaIA: punto único de entrada a todos los microservicios.

Lab. 2: enrutamiento | Lab. 3: notificaciones | Lab. 4: imágenes
Lab. 6: autenticación (JWT), autorización por roles y API Key hacia los servicios.
>>>>>>> 11b8664fec61a32b07f7ac459b70f95524ff234d
"""
import os
<<<<<<< HEAD
<<<<<<< HEAD
import requests

=======

import requests  # cliente HTTP para reenviar las peticiones a los microservicios
>>>>>>> b32faee (Lab 2: pruebas)
from fastapi import FastAPI, Request, Response
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware

<<<<<<< HEAD
=======

import jwt
import requests
from fastapi import FastAPI, Request, Response
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
>>>>>>> 11b8664fec61a32b07f7ac459b70f95524ff234d

# Configuración de rutas
=======
# ---------------------------------------------------------------- Configuraciones
# Tabla de rutas: prefijo de la URL -> dirección interna del microservicio.
# En Docker Compose cada servicio se llama por su nombre (http://clientes:8000).
>>>>>>> b32faee (Lab 2: pruebas)
RUTAS = {
    "clientes": os.getenv("CLIENTES_URL", "http://clientes:8000"),
    "productos": os.getenv("PRODUCTOS_URL", "http://productos:8000"),
    "ventas": os.getenv("VENTAS_URL", "http://ventas:8000"),
    "ia": os.getenv("IA_URL", "http://ia:8000"),
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    "notificaciones": os.getenv(
        "NOTIFICACIONES_URL",
        "http://notificaciones:8000"
    ),
=======
    "notificaciones": os.getenv("NOTIF_URL", "http://notificaciones:8000"), # Lab. 3
>>>>>>> ee54333 (Lab3: RabbitMQ en Compose, dependencias y ruta de notificaciones)
=======
    "notificaciones": os.getenv("NOTIF_URL", "http://notificaciones:8000"), 
    "imagenes": os.getenv("IMAGENES_URL", "http://imagenes:8000"),# Lab. 3
>>>>>>> f7debb6 (Lab4: Imagen-Service y PUT de Productos)
=======
    "notificaciones": os.getenv("NOTIF_URL", "http://notificaciones:8000"),
    "imagenes": os.getenv("IMAGENES_URL", "http://imagenes:8000"),
    "auth": os.getenv("AUTH_URL", "http://auth:8000"),
>>>>>>> 11b8664fec61a32b07f7ac459b70f95524ff234d
}

JWT_SECRET = os.getenv("JWT_SECRET", "")
API_KEY = os.getenv("API_KEY", "")

# Permisos por roles
PUBLICO = {
    ("GET", "productos"),
    ("GET", "imagenes"),
    ("POST", "auth"),
}

PERMISOS = {
    ("GET", "clientes"): {"vendedor", "analista"},
    ("POST", "clientes"): {"vendedor"},
    ("PUT", "clientes"): {"vendedor"},
    ("GET", "ventas"): {"vendedor", "analista"},
    ("POST", "ventas"): {"vendedor"},
    ("GET", "ia"): {"analista"},
    ("POST", "ia"): {"analista"},
    ("GET", "notificaciones"): {"vendedor"},
}

app = FastAPI(title="TiendaIA - API Gateway")

<<<<<<< HEAD
<<<<<<< HEAD

# Configuración CORS
=======
# CORS
>>>>>>> 11b8664fec61a32b07f7ac459b70f95524ff234d
ORIGENES = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "*").split(",")
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES,
    allow_methods=["*"],
    allow_headers=["*"],
)

sesion = requests.Session()
TIEMPO_ESPERA = 60


# Autorización
def autorizar(metodo: str, svc: str, ruta: str, auth: str | None):
    """Verifica el JWT y los permisos del usuario."""

    if (metodo, svc) in PUBLICO:
        return "anonimo", None

    if not JWT_SECRET:
        return "anonimo", None

    if not auth or not auth.lower().startswith("bearer "):
        return None, JSONResponse(
            {"detail": "Token requerido"}, 401
        )

    try:
        datos = jwt.decode(
            auth[7:],
            JWT_SECRET,
            algorithms=["HS256"]
        )
    except jwt.PyJWTError:
        return None, JSONResponse(
            {"detail": "Token inválido o expirado"}, 401
        )

    roles = set(datos.get("roles", []))
    permitidos = PERMISOS.get((metodo, svc), set())

    if svc == "ia" and ruta.startswith("train"):
        permitidos = set()

    if "admin" in roles or roles & permitidos:
        return datos["sub"], None

    return None, JSONResponse(
        {"detail": "Permiso insuficiente"}, 403
    )


# Endpoints
@app.get("/health")
async def salud():
    """Revisa el estado de cada microservicio."""

=======
# CORS (Cross-Origin Resource Sharing): el navegador bloquea las peticiones de una
# página a OTRO origen (esquema + host + puerto) salvo que el servidor lo autorice.
# El cliente web vive en otro origen (http://localhost:8081, Render ...), por eso el
# gateway responde con las cabeceras Access-Control-Allow-*. CORS_ORIGINS es una
# lista separada por comas; "*" permite cualquier origen (en producción, ponga
# solo la URL de su frontend).
ORIGENES = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]
app.add_middleware(CORSMiddleware, allow_origins=ORIGENES, allow_methods=[""], allow_headers=[""])

# Reutiliza conexiones persistentes (no se abre una conexión TCP nueva cada vez)
sesion = requests.Session()
TIEMPO_ESPERA = 60  # segundos; generoso porque entrenar el modelo tarda
TIEMPO_SALUD = 3  # /health debe contestar rápido o se considera caído


# ----------------------------------------------------------------- Endpoints
@app.get("/health")
async def salud():
    """Consulta /health de cada microservicio y resume su estado (200).

    Devuelve {"gateway": "ok", "servicios": {"clientes": true, ...}}; un servicio
    aparece en false si no responde 200 o no se pudo conectar con él.
    """
>>>>>>> b32faee (Lab 2: pruebas)
    estado = {}

    for nombre, url in RUTAS.items():
        try:
<<<<<<< HEAD
            r = await run_in_threadpool(
                sesion.get,
                f"{url}/health",
                timeout=3
            )
            estado[nombre] = r.status_code == 200

        except requests.RequestException:
=======
            # requests es bloqueante: run_in_threadpool lo ejecuta en otro hilo
            # para que el gateway siga atendiendo otras peticiones mientras espera.
            r = await run_in_threadpool(sesion.get, f"{url}/health", timeout=TIEMPO_SALUD)
            estado[nombre] = r.status_code == 200
        except requests.RequestException:  # caído, sin red o tardó demasiado
>>>>>>> b32faee (Lab 2: pruebas)
            estado[nombre] = False

    return {
        "gateway": "ok",
        "servicios": estado
    }


@app.api_route("/api/{svc}", methods=["GET", "POST"])
@app.api_route(
    "/api/{svc}/{ruta:path}",
    methods=["GET", "POST", "PUT", "DELETE"]
)
async def proxy(svc: str, req: Request, ruta: str = ""):
<<<<<<< HEAD
    """Reenvía las peticiones al microservicio correspondiente."""

    if svc not in RUTAS:
        return Response(status_code=404)

    usuario, error = autorizar(
        req.method,
        svc,
        ruta,
        req.headers.get("authorization")
    )

    if error:
        return error

    cabeceras = {
        "content-type": req.headers.get(
            "content-type",
            "application/json"
        ),
        "x-api-key": API_KEY,
        "x-usuario": usuario
    }

    if svc == "auth" and req.headers.get("authorization"):
        cabeceras["authorization"] = req.headers["authorization"]

    destino = f"{RUTAS[svc]}/{svc}"

    if ruta:
        destino += f"/{ruta}"

=======
    """Reenvía la petición al microservicio indicado y devuelve su respuesta tal cual.

    Ejemplo: GET /api/clientes/3 -> GET http://clientes:8000/clientes/3.
    Se copian el método, los parámetros de consulta, el cuerpo y el content-type;
    el código HTTP de respuesta (200, 201, 204, 404, 422...) es el del servicio.
    Responde 404 si el servicio no está en la tabla RUTAS.
    """
    if svc not in RUTAS:
        return Response(status_code=404)  # prefijo desconocido
    destino = f"{RUTAS[svc]}/{svc}" + (f"/{ruta}" if ruta else "")
    cuerpo = await req.body()  # bytes del cuerpo (vacío en GET)
    # requests es BLOQUEANTE: si se llamara directamente, el gateway (asíncrono)
    # se congelaría mientras espera al microservicio y no atendería a nadie más.
    # run_in_threadpool ejecuta la llamada en un hilo aparte y await espera su
    # resultado sin bloquear el ciclo de eventos.
>>>>>>> b32faee (Lab 2: pruebas)
    r = await run_in_threadpool(
        sesion.request,
        req.method,
        destino,
        # multi_items() conserva parámetros repetidos (?a=1&a=2)
        params=list(req.query_params.multi_items()),
        data=await req.body(),
        headers=cabeceras,
        timeout=TIEMPO_ESPERA,
        # No seguir redirecciones: el gateway devuelve la respuesta tal cual
        allow_redirects=False,
    )
<<<<<<< HEAD

    return Response(
        r.content,
        r.status_code,
        media_type=r.headers.get("content-type")
<<<<<<< HEAD
    )
=======
    # Se devuelve el cuerpo, el código y el tipo de contenido del microservicio
    return Response(r.content, r.status_code, media_type=r.headers.get("content-type"))
>>>>>>> b32faee (Lab 2: pruebas)
=======
    )
>>>>>>> 11b8664fec61a32b07f7ac459b70f95524ff234d
