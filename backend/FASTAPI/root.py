"""Nodo raiz de la API"""
# Importación de la API
from fastapi import FastAPI
# Importar la clase para poder importar los recursos estáticos
from fastapi.staticfiles import StaticFiles
# Importación de los routers
from routers.products import app as productsRouter
from routers.users import app as usersRouter
# Instancia de la API
app = FastAPI()
# Aplicación de los routers
# Le añadimos un prefijo a cada router para encaminarlos por distintos paths
app.include_router(productsRouter,prefix="/products",)
app.include_router(usersRouter,prefix="/user")
# Para poder servir recursos estáticos (imagenes,HTML...)
app.mount("/static",StaticFiles(directory='static'),name='static')
