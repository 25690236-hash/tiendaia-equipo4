"""Genera clientes, productos y ventas sintéticas a través del API Gateway.

Uso: python scripts/generar_carga.py [URL_GATEWAY] [NUM_VENTAS]
"""
import os
import random
import sys
from datetime import date

import requests

GW = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 400
random.seed(42)
TOKEN = os.getenv("TOKEN")  # Opcional: token de administrador desde el Lab. 6
TIEMPO_ESPERA = 10
sesion = requests.Session()
if TOKEN:
    sesion.headers.update({"Authorization": f"Bearer {TOKEN}"})

for i in range(1, 11):
    sesion.post(
        f"{GW}/api/clientes",
        timeout=TIEMPO_ESPERA,
        json={"nombre": f"Cliente {i}", "correo": f"cliente{i}@ejemplo.com"},
    )

catalogo = {
    "Café de la Huasteca": (120.0, 8),
    "Piloncillo": (35.0, 15),
    "Miel de abeja": (150.0, 5),
    "Zacahuil (porción)": (60.0, 12),
    "Bocoles (docena)": (90.0, 6),
}
existentes = {
    p["nombre"]
    for p in sesion.get(f"{GW}/api/productos", timeout=TIEMPO_ESPERA).json()
}
for nombre, (precio, _) in catalogo.items():
    if nombre not in existentes:
        sesion.post(
            f"{GW}/api/productos",
            timeout=TIEMPO_ESPERA,
            json={"nombre": nombre, "precio": precio},
        )

clientes = sesion.get(f"{GW}/api/clientes", timeout=TIEMPO_ESPERA).json()
productos = [
    p
    for p in sesion.get(f"{GW}/api/productos", timeout=TIEMPO_ESPERA).json()
    if p["nombre"] in catalogo
]
base = {p["id"]: catalogo[p["nombre"]][1] for p in productos}
temporada = {12: 1.8, 11: 1.4, 1: 1.2, 7: 1.3}

errores = 0
for _ in range(N):
    p = random.choice(productos)
    mes = random.randint(1, 12)
    cantidad = max(
        1,
        round(base[p["id"]] * temporada.get(mes, 1.0) + random.gauss(0, 1.5)),
    )
    respuesta = sesion.post(
        f"{GW}/api/ventas",
        timeout=TIEMPO_ESPERA,
        json={
            "cliente_id": random.choice(clientes)["id"],
            "producto_id": p["id"],
            "cantidad": cantidad,
            "fecha": date(2025, mes, random.randint(1, 28)).isoformat(),
        },
    )
    errores += respuesta.status_code != 201

print(
    f"clientes={len(clientes)} productos={len(productos)} "
    f"ventas={N - errores} errores={errores}"
)
