FROM python:3.11-slim

WORKDIR /app

# Copiar todo el proyecto al contenedor
COPY . .

# Instalar las dependencias globales de los microservicios
RUN pip install --no-cache-dir fastapi uvicorn pydantic requests pymongo redis mysql-connector-python sqlalchemy

# Forzar la ruta del módulo integrador en el PYTHONPATH para que Python encuentre los archivos
ENV PYTHONPATH=/app/integrador:/app

# Ejecutar la aplicación app:app dentro de la carpeta integrador
CMD ["uvicorn", "integrador.app:app", "--host", "0.0.0.0", "--port", "8000"]