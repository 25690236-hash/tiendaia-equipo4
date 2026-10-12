import sys, time, requests, statistics

if len(sys.argv) < 3:
    print("Uso: python medir_latencia.py <URL> <NUM_PETICIONES>")
    sys.exit(1)

url = sys.argv[1]
n = int(sys.argv[2])

# Primera petición (arranque en frío)
t0 = time.time()
r = requests.get(url)
t1 = time.time()
primera_ms = round((t1 - t0) * 1000)
print(f"Primera petición: {primera_ms} ms (código {r.status_code})")

# Siguientes N peticiones
tiempos = []
errores = 0
for _ in range(n):
    t0 = time.time()
    res = requests.get(url)
    t1 = time.time()
    if res.status_code == 200:
        tiempos.append((t1 - t0) * 1000)
    else:
        errores += 1

p50 = round(statistics.median(tiempos)) if tiempos else 0
p95 = round(statistics.quantiles(tiempos, n=20)[18]) if len(tiempos) >= 20 else round(max(tiempos)) if tiempos else 0
max_t = round(max(tiempos)) if tiempos else 0

print(f"Siguientes {n}: p50={p50} ms, p95={p95} ms, máx={max_t} ms, errores={errores}")
