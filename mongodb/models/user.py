"""Schema de usuario"""

from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    """Definición atributos usuario en la DB
    *id : int-------> identificador del usuario ObjectId
    *username: str--> nombre de usuario en la plataforma
    *name: str------> nombre del usuario
    *password: str -> contraseña
    *email: str-----> dirección de correo electrónico
    *disabled: bool-> ¿El usuario está deshabilitado?
    *created_at: int> Timestamp del momento de creación del usuario
    """
    id: str
    username: str
    name: str
    password: str
    email: str
    disabled: bool
    created_at: float

class UserInputData(BaseModel):
    """Definición atributos usuario en la request
    *username: str--> nombre de usuario en la plataforma
    *name: str------> nombre del usuario
    *password: str -> contraseña
    *email: str-----> dirección de correo electrónico
    """
    username: str
    name: str
    password: str
    email: str

class UserGet(BaseModel):
    """Definición atributos usuario en la response pública
    *username: str--> nombre de usuario en la plataforma
    *name: str------> nombre del usuario
    *email: str-----> dirección de correo electrónico
    *disabled: bool-> ¿El usuario está deshabilitado?
    *created_at: int> Timestamp del momento de creación del usuario
    """
    username: str
    name: str
    email: str
    disabled: bool
    created_at: float

class UserPut(BaseModel):
    """Actualización atributos usuario en la DB
    *username: str--> nombre de usuario en la plataforma
    *name: str------> nombre del usuario
    *email: str-----> dirección de correo electrónico
    *disabled: bool-> ¿El usuario está deshabilitado?
    *created_at: int> Timestamp del momento de creación del usuario
    """
    username: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
