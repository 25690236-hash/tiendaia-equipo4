from app import app
@app.get("/")
def read_root():
    return {"mensaje": "¡Servidor de Tienda IA activo!"}