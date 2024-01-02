"""Primera API"""
from fastapi import APIRouter, HTTPException
# Usamos el BaseModel de pydantic para poder manejar el JSON como clases de python
from pydantic import BaseModel
# IMPORTANTE IMPORTAR SIEMPRE LOS MODULES DESDE RUTAS ABSOLUTAS
from jlop_lib.success_response import success_res,SuccessResponse

# Respuesta satisfactoria
# class SuccessResponse(BaseModel):
#     """Clase que define la respuesta exitosa"""
#     successMsg: str
# def success_res(status_code = 200,detail="Operación realizada con éxito"):
#     """Función para devolver los mensajes de éxito"""
#     return { "successMsg":f"{status_code}: {detail}" }

# BaseModel entre corchetes para indicar herencia


class User(BaseModel):
    """Clase que define la estructura de un User"""
    name: str
    username: str
    gmail: str
    web: str

# "base de datos" en la que almacenaremos los usuarios
usersDB = [
    User(name='jlopy', username='jlop_cuns',
         gmail='jlopcuns@gmail.com', web="jlopcunsdev.netlify.app")
]

# Creamos la instancia de nuestra API
app = APIRouter(responses={
    404:{ "msg":"Recurso no encontrado"}, # responses establece las respuestas que se deben enviar por código
    200:{"msg":"Respuesta satisfactoria"}
},
tags=['users'] # tags sirve para hacer divisiones en la documentación
)

# Las peticiones siempre son asíncronas para no bloquear el servidor


def search_username(username: str):
    """Función para obtener el usuario a partir del username"""
    user = [user for user in usersDB if user.username == username][0]
    if not user:
        return {"errorMsg": f"El usuario con el username {username} no ha sido encontrado"}
    return user


@app.get("/all", status_code=200)
async def users():
    """Función para devolver todos los usuarios"""
    return usersDB


@app.get("/{username}", status_code=200,response_model=User)
def user_by_username(username: str):
    """Función para obtener un usuario a partir de su username"""
    user = search_username(username)
    if not isinstance(user, User):
        # Lanzamos una excepción HTTP, integrada ya en FastAPI
        raise HTTPException(404, detail=f'el usuario {username} no ha sido encontrado')
    return user

# La misma función que la anterior pero esta funciona con query params


@app.get("/",status_code=200,response_model=User)
async def user_by_username_query(username: str):
    """Función para obtener un usuario a partir de su username"""
    user = search_username(username)
    if not isinstance(user, User):
        # Lanzamos una excepción HTTP, integrada ya en FastAPI
        raise HTTPException(404, detail=f'el usuario {username} no ha sido encontrado')
    return user


@app.post("/",status_code=201,response_model=SuccessResponse)
async def new_user(user: User):
    """Función para añadir un usuario a la lista"""
    # Comprobar si ya existe un usuario con ese username
    user_already_exists = bool(
        [userdb for userdb in usersDB if userdb.username == user.username])
    if user_already_exists:
        raise HTTPException(409,detail=f"Ya existe un usuario con el username {user.username}")
    # Añadir el usuario a la DB
    usersDB.append(user)
    # Enviar un mesaje de satisfacción
    return success_res(201,"Usuario añadido con éxito")

# PARA PODER USAR EL BODY de la petición necesitamos crear una clase que defina ese body y luego
# introducir en la petición un parámetro que tenga el tipo de esa clase y que
# representará justamente a ese body


class UserName(BaseModel):
    """Clase para definir el body del patch"""
    username: str


@app.patch('/{c_username}',status_code=200,response_model=SuccessResponse)
# En este caso es el parámetro items el que representa el body
async def update_user_name(c_username: str, items: UserName):
    """Ejemplo de la función UPDATE para cambiar el username"""
    userdata = search_username(c_username)
    if isinstance(userdata, User):
        raise HTTPException(404,detail="El usuario no existe")
    [user for user in usersDB if user.username ==
        c_username][0].username = items.username
    return success_res(detail="Información actualizada")



@app.delete("/{username}",status_code=200,response_model=SuccessResponse)
async def delete(username: str):
    """función para eliminar un usuario"""
    global usersDB
    exist_user = username in list(map(lambda u: u.username,usersDB))
    if not exist_user:
        raise HTTPException(404,f"El usuario {username} no existe")
    usersDB = [user for user in usersDB if user.username != username]
    return success_res(detail="El usuario ha sido eliminado")
