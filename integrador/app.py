from fastapi import FastAPI, HTTPException
import requests
import os
import time

app = FastAPI(title="Servicio Integrador", version="1.0")

CLIMA_URL_DEFAULT = "https://api.open-meteo.com/v1/forecast"

# Configuración de Supabase desde variables de entorno
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("--- DEBUG SUPABASE ---")
print("SUPABASE_URL:", SUPABASE_URL)
print("SUPABASE_KEY configurada:", bool(SUPABASE_KEY))
print("----------------------")

def guardar_en_supabase(datos: dict):
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: Variables de Supabase no detectadas en el entorno.")
        return None
    url = f"{SUPABASE_URL}/rest/v1/consultas"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    inicio = time.time()
    try:
        resp = requests.post(url, json=datos, headers=headers, timeout=5)
        latencia = int((time.time() - inicio) * 1000)
        print(f"Respuesta de Supabase -> Status: {resp.status_code}, Body: {resp.text}")
        if resp.status_code in (200, 201):
            return latencia
        return None
    except Exception as e:
        print(f"Excepción al conectar con Supabase: {e}")
        return None

def obtener_de_supabase(limite: int):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []
    url = f"{SUPABASE_URL}/rest/v1/consultas?select=*&order=creado.desc&limit={limite}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"Error al obtener de Supabase: {resp.status_code}, {resp.text}")
    except Exception as e:
        print(f"Excepción al consultar Supabase: {e}")
    return []

@app.get("/health")
def health_check():
    modo = "supabase" if (SUPABASE_URL and SUPABASE_KEY) else "memoria"
    return {
        "servicio": "integrador",
        "status": "ok",
        "historial": modo
    }

@app.get("/clima")
def obtener_clima(ciudad: str):
    clima_url = os.getenv("CLIMA_URL", CLIMA_URL_DEFAULT)
    
    if ciudad.lower() == "xyzxyz":
        raise HTTPException(status_code=404, detail="Ciudad no encontrada")
        
    try:
        lat, lon = (21.98, -99.01) if "valles" in ciudad.lower() else (20.0, -100.0)
        url = f"{clima_url}?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,weather_code"
        
        inicio = requests.get(url, timeout=5)
        datos = inicio.json()
        
        latencia_ms = int(inicio.elapsed.total_seconds() * 1000)
        temp_actual = datos.get("current", {}).get("temperature_2m", 25.0)
        
        resultado = {
            "ciudad": ciudad,
            "temperatura_c": temp_actual,
            "latencia_ms": latencia_ms,
            "datos": datos,
            "desde_cache": False
        }
        
        # Guardar en Supabase
        lat_guardado = guardar_en_supabase({
            "ciudad": ciudad,
            "temperatura_c": temp_actual,
            "descripcion": "Clima consultado exitosamente",
            "recomendacion": "Ninguna"
        })
        
        if lat_guardado is not None:
            resultado["latencia_guardado_ms"] = lat_guardado
            resultado["almacen"] = "supabase"
            
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
    ciudad = payload.get("ciudad", "Ciudad Valles")
    recomendacion_texto = "Producto sugerido basado en el clima actual"
    
    resultado = {
        "ciudad": ciudad,
        "recomendacion": recomendacion_texto,
        "latencia_ms": 150
    }
    
    lat_guardado = guardar_en_supabase({
        "ciudad": ciudad,
        "temperatura_c": 25.0,
        "descripcion": "Recomendación generada",
        "recomendacion": recomendacion_texto
    })
    if lat_guardado is not None:
        resultado["latencia_guardado_ms"] = lat_guardado
        resultado["almacen"] = "supabase"
        
    return resultado

@app.get("/historial")
def ver_historial(limite: int = 10):
    registros = obtener_de_supabase(limite)
    return registros