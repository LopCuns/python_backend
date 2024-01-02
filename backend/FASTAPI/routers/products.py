"""Ejemplo de uso de los routers"""
from fastapi import APIRouter

app = APIRouter()


@app.get("/")
def get_products():
    """Función para obtener productos"""
    return ['manzana', 'pera', 'melocotón']
