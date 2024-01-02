'''Fast api para backend'''
from fastapi import FastAPI

# Creación del contexto general de FastAPI
app = FastAPI()

# Aprovecha los decoradores de python para indicar la operación
# De esta forma podemos definir las funcionalidades usando las funciones
# nativas de python y no métodos de la libreria, pues el decorador añade esta
# funcionalidad externa sin que nosotros nos tengamos que preocupar.
@app.get("/") # El decorador está contenido en nuestra instancia de FastAPI
async def root():
    '''Root'''
    return {"message": "hello world"}

# LA DOCUMENTACIÓN PUEDE SER ENCONTRADA EN /docs ; Están hechas con SWAGGER
# TAMBIÉN se puede acceder a la documentacion con /redoc; Están hechas con REDOC

@app.get("/social_media")
async def social_media():
    """Función GET con otra ruta"""
    return {
        "instagram": "@jorge_lopcuns",
        "youtube": "@jorgelopezcuns"
    }
