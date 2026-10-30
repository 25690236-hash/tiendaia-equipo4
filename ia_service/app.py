"""Microservicio de IA de TiendaIA: predicción de demanda (Laboratorio 3).

Entrena un modelo RandomForest y permite realizar predicciones normales
y solicitudes de inferencia asíncronas mediante RabbitMQ y Redis.
"""

import os
from pathlib import Path

import joblib
import pandas as pd
import requests
from fastapi import FastAPI, HTTPException, Query
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

# Importar las rutas de inferencia asíncrona del Laboratorio 3
from cola import router as cola_router


# --------------------------------------------------------- Configuración

VENTAS_URL = os.getenv("VENTAS_URL", "http://ventas:8000")

# Ruta del modelo guardado en el volumen de Docker
MODELO = Path(os.getenv("MODELO_PATH", "/modelos/modelo.joblib"))

COLUMNAS = ["producto_id", "mes", "precio"]


# --------------------------------------------------------- Aplicación

app = FastAPI(title="TiendaIA - Servicio de IA")

# Agregar las rutas asíncronas de cola.py
app.include_router(cola_router)


# --------------------------------------------------------- Preparación de datos

def preparar(ventas: list[dict]) -> pd.DataFrame:
    """Convierte las ventas en un DataFrame y obtiene el mes de cada fecha."""
    df = pd.DataFrame(ventas)
    df["mes"] = pd.to_datetime(df["fecha"]).dt.month
    return df


# --------------------------------------------------------- Endpoints

@app.get("/health")
def salud():
    """Verifica el estado del servicio y si existe un modelo entrenado."""
    return {
        "servicio": "ia",
        "status": "ok",
        "modelo_entrenado": MODELO.exists()
    }


@app.post("/ia/train")
def entrenar():
    """Entrena el modelo utilizando las ventas del microservicio Ventas."""

    try:
        respuesta = requests.get(f"{VENTAS_URL}/ventas", timeout=30)
        respuesta.raise_for_status()
        ventas = respuesta.json()

    except requests.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"No se pudieron obtener las ventas: {str(e)}"
        )

    if len(ventas) < 30:
        raise HTTPException(
            status_code=400,
            detail=f"Se requieren al menos 30 ventas (hay {len(ventas)})"
        )

    df = preparar(ventas)

    X = df[COLUMNAS]
    y = df["cantidad"]

    # Separar datos de entrenamiento y prueba
    X_tr, X_te, y_tr, y_te = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    # Pipeline de transformación y modelo
    modelo = make_pipeline(
        ColumnTransformer(
            [
                (
                    "prod",
                    OneHotEncoder(handle_unknown="ignore"),
                    ["producto_id"]
                )
            ],
            remainder="passthrough"
        ),
        RandomForestRegressor(
            n_estimators=200,
            random_state=42
        )
    )

    # Entrenar y evaluar
    modelo.fit(X_tr, y_tr)
    pred = modelo.predict(X_te)

    # Guardar el modelo en el volumen compartido
    MODELO.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(modelo, MODELO)

    return {
        "mensaje": "Modelo entrenado",
        "ventas": len(df),
        "mae": round(mean_absolute_error(y_te, pred), 2),
        "r2": round(r2_score(y_te, pred), 3)
    }


@app.get("/ia/predict")
def predecir(
    producto_id: int,
    mes: int = Query(ge=1, le=12),
    precio: float = Query(gt=0)
):
    """Realiza una predicción inmediata de la demanda."""

    if not MODELO.exists():
        raise HTTPException(
            status_code=409,
            detail="Modelo no entrenado: ejecute POST /api/ia/train"
        )

    modelo = joblib.load(MODELO)

    x = pd.DataFrame(
        [[producto_id, mes, precio]],
        columns=COLUMNAS
    )

    return {
        "producto_id": producto_id,
        "mes": mes,
        "precio": precio,
        "cantidad_estimada": round(float(modelo.predict(x)[0]), 1)
    }
