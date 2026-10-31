# Parte C: resultados de carga y pruebas

Pruebas iniciales realizadas antes de generar datos:

| Petición | Resultado observado |
|---|---|
| `GET /api/ia/predict?producto_id=1&mes=12&precio=35` | HTTP 409 Conflict: modelo no entrenado |
| `POST /api/ia/train` | HTTP 400 Bad Request: se requieren al menos 30 ventas (hay 0) |

Carga ejecutada desde el equipo local con `python scripts/generar_carga.py
http://localhost:8080 400`. Resultado: `clientes=10 productos=5 ventas=400
errores=0`. Después se confirmó `ventas=400` consultando `/api/ventas`.

Entrenamiento: `{"mensaje":"Modelo entrenado","ventas":400,"mae":1.37,
"r2":0.91}`. El archivo `/modelos/modelo.joblib` quedó persistido en el volumen
`modelos`.

| Producto | Mes | Precio | Cantidad estimada |
|---|---:|---:|---:|
| Piloncillo (id 2) | Diciembre (12) | 35 | 27.4 |
| Piloncillo (id 2) | Mayo (5) | 35 | 13.3 |

Las respuestas cumplen los resultados esperados en la guía. Guarda capturas de
las dos respuestas iniciales y del entrenamiento/predicciones para adjuntarlas
al reporte.
