"""Raíz del proyecto"""

# from client import user_collection
from fastapi import FastAPI
from routers.user import router as user_router


app = FastAPI()
app.include_router(user_router,prefix="/user",tags=['user'])
