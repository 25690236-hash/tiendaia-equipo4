FROM python:3.11-slim

WORKDIR /app

ARG SERVICIO

# Copiar todo el proyecto al contenedor
COPY . .

# Cada servicio instala sus propias dependencias, incluidas las del controlador
# de base de datos y las bibliotecas de entrenamiento de IA.
RUN pip install --no-cache-dir -r "${SERVICIO}/requirements.txt"

# Cada servicio compila la misma imagen indicando su módulo (clientes, productos,
# ventas, ia_service o gateway) como argumento SERVICIO.
ENV SERVICIO=${SERVICIO}
ENV PYTHONPATH=/app

CMD ["sh", "-c", "uvicorn ${SERVICIO}.app:app --host 0.0.0.0 --port 8000"]
