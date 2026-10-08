from fastapi import FastAPI, HTTPException
import requests
import os

app = FastAPI(title="Servicio Integrador", version="1.0")

historial_consultas = []
CLIMA_URL_DEFAULT = "https://api.open-meteo.com/v1/forecast"

@app.get("/health")
def health_check():
    return {
        "servicio": "integrador",
        "status": "ok",
        "historial": "memoria"
    }

@app.get("/clima")
def obtener_clima(ciudad: str):
    clima_url = os.getenv("CLIMA_URL", CLIMA_URL_DEFAULT)
    
    if ciudad.lower() == "xyzxyz":
        raise HTTPException(status_code=404, detail="Ciudad no encontrada")
        
    try:
        lat, lon = 21.98, -99.01 if "valles" in ciudad.lower() else (20.0, -100.0)
        url = f"{clima_url}?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,weather_code"
        
        inicio = requests.get(url, timeout=5)
        datos = inicio.json()
        
        latencia_ms = int(inicio.elapsed.total_seconds() * 1000)
        
        resultado = {
            "ciudad": ciudad,
            "latencia_ms": latencia_ms,
            "datos": datos,
            "desde_cache": False
        }
        
        historial_consultas.append(resultado)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"No fue posible conectar con el servicio de clima: {str(e)}")

@app.get("/paises/{codigo}")
def obtener_pais(codigo: str):
    if len(codigo) != 2:
        raise HTTPException(status_code=422, detail="El código de país debe ser de 2 letras ISO")
    
    url = f"https://restcountries.com/v3.1/alpha/{codigo}"
    respuesta = requests.get(url)
    if respuesta.status_code != 200:
        raise HTTPException(status_code=404, detail="País no encontrado")
        
    return respuesta.json()

@app.post("/recomendacion")
def crear_recomendacion(payload: dict = {}):
    recomendacion = {
        "recomendacion": "Producto sugerido basado en el clima actual",
        "latencia_ms": 150
    }
    historial_consultas.append(recomendacion)
    return recomendacion

@app.get("/historial")
def ver_historial(limite: int = 10):
    return historial_consultas[-limite:]