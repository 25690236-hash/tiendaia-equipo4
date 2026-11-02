import json
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

gateway = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080").rstrip("/")
cantidad = int(sys.argv[2]) if len(sys.argv) > 2 else 200
workers = int(sys.argv[3]) if len(sys.argv) > 3 else 1


def solicitar(method, url, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detalle = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {error.code}: {detalle}") from error


def consultar_estado(solicitud_id):
    respuesta = solicitar(
        "GET",
        f"{gateway}/api/ia/solicitudes/{solicitud_id}",
    )
    return respuesta.get("estado", "desconocido")


inicio = time.monotonic()
ids = []

try:
    for _ in range(cantidad):
        respuesta = solicitar(
            "POST",
            f"{gateway}/api/ia/solicitudes",
            {"producto_id": 1, "mes": 12, "precio": 90},
        )
        ids.append(respuesta["id"])

    pendientes = set(ids)
    errores = 0
    limite = time.monotonic() + max(180, cantidad * 2)

    with ThreadPoolExecutor(max_workers=32) as pool:
        while pendientes and time.monotonic() < limite:
            resultados = list(pool.map(consultar_estado, pendientes))
            nuevos_pendientes = set()

            for solicitud_id, estado in zip(pendientes, resultados):
                if estado == "pendiente":
                    nuevos_pendientes.add(solicitud_id)
                elif estado == "error":
                    errores += 1
                elif estado != "listo":
                    nuevos_pendientes.add(solicitud_id)

            pendientes = nuevos_pendientes
            if pendientes:
                time.sleep(0.5)

    total = time.monotonic() - inicio
    terminadas = cantidad - len(pendientes) - errores
    rendimiento = terminadas / total if total else 0

    print(
        f"N={cantidad} workers={workers} total={total:.2f}s "
        f"rendimiento={rendimiento:.2f} sol/s "
        f"por_worker={rendimiento / workers:.2f} "
        f"errores={errores} pendientes={len(pendientes)}"
    )

    if pendientes:
        print("Aviso: algunas solicitudes no terminaron antes del límite de espera.")
except Exception as error:
    print(f"Error durante la prueba: {error}")
    sys.exit(1)