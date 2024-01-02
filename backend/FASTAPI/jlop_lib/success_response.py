"""Respuesta exitosa"""
from pydantic import BaseModel
class SuccessResponse(BaseModel):
    """Clase que define la respuesta exitosa"""
    successMsg: str
def success_res(status_code = 200,detail="Operación realizada con éxito"):
    """Función para devolver los mensajes de éxito"""
    return { "successMsg":f"{status_code}: {detail}" }
