"""Laboratorio 4: capacidad, velocidad y confiabilidad del almacenamiento de objetos.

Sube y baja archivos grandes (MB/s), muchos archivos pequeños (latencia por
archivo) y verifica la integridad con SHA-256. Sirve para SeaweedFS, Supabase
Storage, Backblaze B2 o Amazon S3 porque todos hablan el mismo API S3.

Uso:
DESTINO=seaweedfs S3_ENDPOINT=http://localhost:8333
S3_ACCESS_KEY=... S3_SECRET_KEY=...
BUCKET=bench-equipo python scripts/bench_almacenamiento.py

Para Amazon S3, omita S3_ENDPOINT.
Los resultados se agregan a resultados_almacenamiento.csv.
"""

import csv
import hashlib
import os
import statistics as st
import time
from datetime import datetime

import boto3  # SDK de AWS para Python: cliente del API S3

# Configuración
DESTINO = os.getenv("DESTINO", "sin-nombre")
BUCKET = os.environ["BUCKET"]

# Si S3_ENDPOINT no está definido, se usa Amazon S3.
s3 = boto3.client(
    "s3",
    endpoint_url=os.getenv("S3_ENDPOINT"),
    aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
    region_name=os.getenv("S3_REGION", "us-east-1"),
)

try:
    s3.head_bucket(Bucket=BUCKET)
except Exception:
    s3.create_bucket(Bucket=BUCKET)

filas = []


def registrar(prueba, valores, unidad, errores=0):
    """Calcula media y desviación estándar, imprime y guarda los resultados."""
    fila = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "destino": DESTINO,
        "prueba": prueba,
        "media": round(st.mean(valores), 2),
        "desv": round(st.pstdev(valores), 2) if len(valores) > 1 else 0,
        "unidad": unidad,
        "n": len(valores),
        "errores": errores,
    }
    filas.append(fila)
    print(
        f"{DESTINO:>12} | {prueba:<22} | "
        f"{fila['media']:>9.2f} {unidad} errores={errores}"
    )


def archivos_grandes(mb, reps=5):
    """Mide velocidad de subida y bajada (MB/s) de archivos grandes."""
    datos = os.urandom(mb * 1024 * 1024)
    huella = hashlib.sha256(datos).hexdigest()
    sub, baj, err = [], [], 0

    for k in range(reps):
        key = f"bench/{mb}MB-{k}"

        t = time.perf_counter()
        s3.put_object(Bucket=BUCKET, Key=key, Body=datos)
        sub.append(mb / (time.perf_counter() - t))

        t = time.perf_counter()
        leido = s3.get_object(Bucket=BUCKET, Key=key)["Body"].read()
        baj.append(mb / (time.perf_counter() - t))

        err += hashlib.sha256(leido).hexdigest() != huella
        s3.delete_object(Bucket=BUCKET, Key=key)

    registrar(f"subida {mb} MB", sub, "MB/s", err)
    registrar(f"bajada {mb} MB", baj, "MB/s", err)


def archivos_pequenos(n=200, kb=10):
    """Mide latencia por archivo y archivos por segundo."""
    datos, lat, err = os.urandom(kb * 1024), [], 0
    t0 = time.perf_counter()

    for i in range(n):
        t = time.perf_counter()
        try:
            s3.put_object(
                Bucket=BUCKET,
                Key=f"bench/peq-{i}",
                Body=datos,
            )
        except Exception:
            err += 1
        lat.append((time.perf_counter() - t) * 1000)

    total = time.perf_counter() - t0
    registrar(f"{n} archivos de {kb} KB", lat, "ms/archivo", err)
    registrar("rendimiento pequeños", [n / total], "archivos/s", err)

    for i in range(n):
        s3.delete_object(Bucket=BUCKET, Key=f"bench/peq-{i}")


# Ejecución: 5 archivos de cada tamaño y 200 archivos pequeños.
for mb in (1, 10, 25):
    archivos_grandes(mb)

archivos_pequenos()

# Agrega los resultados al CSV. Escribe encabezados solo si el archivo es nuevo.
nuevo = not os.path.exists("resultados_almacenamiento.csv")
with open("resultados_almacenamiento.csv", "a", newline="") as f:
    w = csv.DictWriter(f, fieldnames=filas[0].keys())
    if nuevo:
        w.writeheader()
    w.writerows(filas)