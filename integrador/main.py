from fastapi import FastAPI

app = FastAPI(title="Tienda IA - Integrador")

@app.get("/")
def read_root():
    return {"mensaje": "API del Integrador funcionando correctamente"}
