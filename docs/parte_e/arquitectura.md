# Parte E: diagrama de arquitectura

Diagrama del despliegue definido en `docker-compose.yml`. Puede visualizarse en
GitHub o en un editor compatible con Mermaid.

```mermaid
flowchart LR
  browser["Navegador"] -->|HTTP :8081| web["web · Nginx"]
  browser -->|HTTP :8080 /api/*| gateway["gateway · FastAPI"]

  subgraph compose["Red interna de Docker Compose"]
    gateway -->|HTTP :8000| clientes["clientes · FastAPI"]
    gateway -->|HTTP :8000| productos["productos · FastAPI"]
    gateway -->|HTTP :8000| ventas["ventas · FastAPI"]
    gateway -->|HTTP :8000| ia["ia · FastAPI"]

    clientes -->|SQL :3306| mysql[("mysql · MySQL")]
    productos -->|MongoDB :27017| mongo[("mongo · MongoDB")]
    ventas -->|Redis :6379| redis[("redis · Redis")]
    ventas -->|HTTP :8000 valida cliente| clientes
    ventas -->|HTTP :8000 valida producto y consulta precio| productos
    ia -->|HTTP :8000 obtiene ventas para entrenar| ventas
    ia -->|guarda/carga modelo.joblib| modelvol[("volumen modelos")]
  end

  gateway -. "POST /ia/train: dispara entrenamiento" .-> ia
  gateway -. "GET /ia/predict: predicción" .-> ia
```

## Puertos publicados

| Puerto del equipo | Servicio | Uso |
|---|---|---|
| 8080 | gateway | API para el navegador, scripts y clientes externos |
| 8081 | web | Sitio estático servido por Nginx |
| Sin publicar | microservicios y bases de datos | Acceso solo por la red interna de Compose |

El entrenamiento ocurre en `ia`: solicita las ventas a `ventas`, entrena el
Random Forest y persiste `modelo.joblib` en el volumen `modelos`. Las
predicciones se sirven desde ese mismo servicio.
