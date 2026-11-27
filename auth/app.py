"""Auth-Service de TiendaIA (Laboratorio 6)."""
import hashlib
import hmac
import os
import secrets
import sqlite3
import time

import jwt
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

# Configuración
JWT_SECRET = os.getenv("JWT_SECRET", "")
if len(JWT_SECRET) < 32:
    raise RuntimeError("JWT_SECRET falta o es muy corto (mínimo 32 caracteres)")

DB = sqlite3.connect(
    os.getenv("AUTH_DB", "/data/auth.db"),
    check_same_thread=False
)

DB.executescript("""
CREATE TABLE IF NOT EXISTS usuarios
    (usuario TEXT PRIMARY KEY, sal TEXT, hash TEXT, roles TEXT);
CREATE TABLE IF NOT EXISTS servicios
    (servicio TEXT PRIMARY KEY, hash_clave TEXT, creado REAL);
""")

app = FastAPI(title="TiendaIA - Auth")
bearer = HTTPBearer()


# Contraseñas
def hash_contrasena(contrasena: str, sal: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        contrasena.encode(),
        bytes.fromhex(sal),
        200_000
    ).hex()


def crear_usuario(usuario: str, contrasena: str, roles: list[str]):
    """Crea o reemplaza un usuario con una sal nueva y sus roles."""
    sal = secrets.token_hex(16)
    DB.execute(
        "INSERT OR REPLACE INTO usuarios VALUES (?,?,?,?)",
        (usuario, sal, hash_contrasena(contrasena, sal), ",".join(roles))
    )
    DB.commit()


# Administrador inicial
if os.getenv("ADMIN_PASSWORD"):
    crear_usuario("admin", os.environ["ADMIN_PASSWORD"], ["admin"])


# Autorización
def requiere_admin(
    cred: HTTPAuthorizationCredentials = Depends(bearer)
):
    """Exige un JWT válido con el rol admin."""
    try:
        datos = jwt.decode(
            cred.credentials,
            JWT_SECRET,
            algorithms=["HS256"]
        )
    except jwt.PyJWTError:
        raise HTTPException(401, "Token inválido o expirado")

    if "admin" not in datos["roles"]:
        raise HTTPException(403, "Se requiere rol admin")

    return datos


# Modelos
class Login(BaseModel):
    usuario: str
    contrasena: str


class UsuarioIn(Login):
    contrasena: str = Field(min_length=8)
    roles: list[str] = Field(min_length=1)


class ServicioIn(BaseModel):
    servicio: str = Field(pattern=r"^[a-z][a-z0-9-]{1,30}$")


# Endpoints
@app.get("/health")
def salud():
    return {"servicio": "auth", "status": "ok"}


@app.post("/auth/login")
def login(d: Login):
    fila = DB.execute(
        "SELECT sal, hash, roles FROM usuarios WHERE usuario=?",
        (d.usuario,)
    ).fetchone()

    if not fila or not hmac.compare_digest(
        hash_contrasena(d.contrasena, fila[0]),
        fila[1]
    ):
        raise HTTPException(401, "Usuario o contraseña incorrectos")

    token = jwt.encode(
        {
            "sub": d.usuario,
            "roles": fila[2].split(","),
            "exp": int(time.time()) + 30 * 60
        },
        JWT_SECRET,
        algorithm="HS256"
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "expira_en_s": 1800
    }


@app.post("/auth/usuarios", status_code=201)
def registrar_usuario(
    u: UsuarioIn,
    _=Depends(requiere_admin)
):
    crear_usuario(u.usuario, u.contrasena, u.roles)
    return {"usuario": u.usuario, "roles": u.roles}


@app.post("/auth/servicios", status_code=201)
def registrar_servicio(
    s: ServicioIn,
    _=Depends(requiere_admin)
):
    clave = "tia_" + secrets.token_urlsafe(32)

    DB.execute(
        "INSERT OR REPLACE INTO servicios VALUES (?,?,?)",
        (
            s.servicio,
            hashlib.sha256(clave.encode()).hexdigest(),
            time.time()
        )
    )
    DB.commit()

    return {
        "servicio": s.servicio,
        "api_key": clave,
        "aviso": "Guárdela ahora: no se puede volver a consultar"
    }


@app.get("/auth/validar-clave")
def validar_clave(
    x_api_key: str | None = Header(default=None)
):
    if not x_api_key:
        raise HTTPException(401, "API Key requerida")

    h = hashlib.sha256(x_api_key.encode()).hexdigest()

    fila = DB.execute(
        "SELECT servicio FROM servicios WHERE hash_clave=?",
        (h,)
    ).fetchone()

    if not fila:
        raise HTTPException(403, "API Key inválida")

    return {"valida": True, "servicio": fila[0]}