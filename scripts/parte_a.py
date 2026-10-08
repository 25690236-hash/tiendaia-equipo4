import time
import requests  # librería para hacer peticiones HTTP

print("--- 1. Geocodificación (Ciudad Valles) ---")
t = time.perf_counter()
r = requests.get(
    "https://geocoding-api.open-meteo.com/v1/search",
    params={"name": "Ciudad Valles", "count": 1, "language": "es"},
    timeout=10
)
ms = (time.perf_counter() - t) * 1000
print(f"URL: {r.url}")
print(f"Método: GET | Código: {r.status_code} | Tiempo: {ms:.0f} ms | Bytes: {len(r.content)}")
print("Uso (resultados):", r.json().get("results"))
print("-" * 50)

print("--- 2. Clima actual (Coordenadas de Ciudad Valles) ---")
t = time.perf_counter()
r = requests.get(
    "https://api.open-meteo.com/v1/forecast",
    params={
        "latitude": 21.98,
        "longitude": -99.01,
        "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code"
    },
    timeout=10
)
ms = (time.perf_counter() - t) * 1000
print(f"URL: {r.url}")
print(f"Método: GET | Código: {r.status_code} | Tiempo: {ms:.0f} ms | Bytes: {len(r.content)}")
print("Uso (clima actual):", r.json().get("current"))
print("-" * 50)

print("--- 3. Crear recurso de prueba (POST) ---")
t = time.perf_counter()
r = requests.post(
    "https://jsonplaceholder.typicode.com/posts",
    json={"title": "hola", "body": "desde python", "userId": 1},
    timeout=10
)
ms = (time.perf_counter() - t) * 1000
print(f"URL: {r.request.url}")
print(f"Método: POST | Código: {r.status_code} | Tiempo: {ms:.0f} ms | Bytes: {len(r.content)}")
print("Uso (respuesta JSON):", r.json())
print("-" * 50)

print("--- 4. Recurso que no existe (Error 404) ---")
t = time.perf_counter()
r = requests.get("https://pokeapi.co/api/v2/pokemon/no-existe", timeout=10)
ms = (time.perf_counter() - t) * 1000
print(f"URL: {r.url}")
print(f"Método: GET | Código: {r.status_code} | Tiempo: {ms:.0f} ms | Bytes: {len(r.content)}")
if r.status_code == 200:
    print("Respuesta:", r.json())
else:
    print("Respuesta (Texto por error 404):", r.text[:100], "...") # Imprime un fragmento del texto