"""Router de usuarios"""

from os import getenv
from datetime import datetime, timedelta
from lib.purify_dict import purify_dict # pylint: disable=E0401,E0611
from models.user import User, UserInputData, UserGet,UserPut  # pylint: disable=E0401
from schemas.user import user_schema, user_schema_public  # pylint: disable=E0401
from schemas.token import Token # pylint: disable=E0401
from client import DB  # pylint: disable=E0401
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv
from bson import ObjectId
from pymongo import ReturnDocument

# ESTRUCTURA MONGODB (carpeta concept/images/hierarchy_mongodb.png)
# Mongodb es una base de datos no relacional estructurada de la siguiente manera:
# --* DB (la base de datos)
# --* Collections (cada uno de los tipos de documentos que se almacenan)
# --* Documents (Entidades o conjuntos de datos almacenados conjuntamente)
# Para poder acceder a estos datos desde un lenguaje de programación se necesita de una
# libreria (en este caso pymongo o mongoose en el caso de JavaScript) que nos permita interactuar
# con ella. Esta libreria nos proporciona:
# * Una forma de conectarnos con la base de datos (client o connection) a partir de la cual
# acceder a las diferentes colecciones y documentos de la DB.
# ---(carpeta concep/images/schema_model.png)---
# * Una manera de crear los esquemas de documento (entidades que representan
# los documentos de la DB) pero en un tipo de dato propio del lenguaje (en este caso pydantic)
# * Si es necesario, una manera de convertir los esquemas en modelos(entidades de la DB)
# antes de enviarlos o para convertir los modelos en esquemas (para poder trabajar
# con ellos desde el lenguaje de programación)

# Permitir acceso a las variables de entorno
load_dotenv()

# Path del servicio de autenticación
OAUTH_PATH = getenv('OAUTH_PATH')

# Tiempo de expiración del jwt (en minutos)

TOKEN_EXP_TIME = int(getenv('TOKEN_EXP_TIME'))

# Secreto del jwt

TOKEN_SECRET = getenv('TOKEN_SECRET')

# Algoritmo de encriptado

CRYPT_ALG = getenv('CRYPTO_ALG')

# Servicio de autenticación
oauth = OAuth2PasswordBearer(tokenUrl=OAUTH_PATH)

# Instancia de fastAPI
router = APIRouter()

# Contexto de encriptado
crypto = CryptContext(schemes=['bcrypt'])

# Obtener la colección de usuarios
user_collection = DB[getenv("DB_USERS_COLLECTION_NAME")]


def return_encrypted_user_data(user_data: UserInputData):
    """Encriptar los datos antes de crear el usuario"""
    # Hashear la contraseña
    data = user_data.model_dump()
    data['password'] = crypto.hash(data['password'])
    return data


def get_user_by(key: str, value):
    """Función para obtener un usuario a partir de un par llave-valor"""
    return user_collection.find_one({key: value})


def check_if_user_exist(key: str,value: str) -> bool:
    """Función para comprobar que un usuario exista"""
    return bool(get_user_by(key,value))

def check_password(input_password: str, encrypted_password: str):
    """Comprobar que las contraseñas coincidan"""
    return crypto.verify(input_password, encrypted_password)



# Creación de usuario


@router.post("/register", response_model=User, status_code=201)
async def post(user_data: UserInputData):
    """Función para registrarse"""
    # Comprobar que no exista ya un usuario con ese username
    username_exist = check_if_user_exist('username',user_data.username)
    if username_exist:
        raise HTTPException(
            409, f"El usuario con el username '{user_data.username}' ya existe")
    # Comprobar que no exista ya un usuario con ese username
    email_exist = check_if_user_exist('email',user_data.email)
    if email_exist:
        raise HTTPException(
            409, f"El usuario con el email '{user_data.email}' ya existe")
    # Si no existe el usuario, crearlo
    # Antes encriptar los datos
    user_to_db = {**return_encrypted_user_data(
        user_data), "disabled": False, "created_at": datetime.utcnow().timestamp()}
    doc_id = user_collection.insert_one(user_to_db).inserted_id
    new_user = user_collection.find_one({"_id": doc_id})
    return user_schema(new_user)


# Obtención de un usuario por su username

@router.get("/username/{username}", response_model=UserGet, status_code=200)
async def get_username(username: str):
    """Obtener los datos públicos del usuario por su username"""
    user_db = user_collection.find_one({"username": username})
    # Comprobar si el usuario existe
    if not user_db:
        raise HTTPException(
            404, f"El usuario {username} no ha sido encontrado")
    # Devolver el usuario con sus datos depurados
    return user_schema_public(user_db)

@router.get("/id/{user_id}",response_model=UserGet,status_code=200)
async def get_id(user_id: str):
    """Función para obtener un usuario por su id"""
    # Buscar el usuario por id (necesario usar el ObjectId de bson)
    user_db = get_user_by("_id",ObjectId(user_id))
    # Comprobar que el usuario existe
    if not user_db:
        raise HTTPException(404,f'No existe el usuario con el id {id}')
    # Pasar el usuario a esquema
    # Devolver el usuario
    return user_schema_public(user_db)

@router.post(f"/{OAUTH_PATH}",response_model=Token ,status_code=200)
async def post_login(form: OAuth2PasswordRequestForm = Depends()):
    """Función para iniciar sesión y obtener un jwt"""
    # Obtener el usuario por username
    user_db = get_user_by("username", form.username)
    # Comprobar que exista el usuario
    if not user_db:
        raise HTTPException(401, "Credenciales incorrectas")
    # Obtener el esquema del usuario
    user = user_schema(user_db)
    # Comprobar que las contraseñas coincidan
    if not check_password(form.password, user.password):
        raise HTTPException(401, "Credenciales incorrectas")
    # Comprobar que el usuario esté habilitado
    if user.disabled:
        raise HTTPException(401, "Tu cuenta ha sido deshabilitada")
    # Crear el token
    # Momento en el que expira
    exp_time = timedelta(minutes=TOKEN_EXP_TIME)
    # Crear el contenido del token
    access_token = {
        "sub": user.id,
        "exp": datetime.utcnow() + exp_time
    }
    # Devolver el token
    return {"access_token": jwt.encode(access_token, TOKEN_SECRET, CRYPT_ALG),
            "token_type": "Bearer"}


def validate_token(token: Token = Depends(oauth)):
    """Función para validar el jwt"""
    # Descodificar el token
    try:
        payload = jwt.decode(token,TOKEN_SECRET)
    except JWTError as e: # Si el token ha expirado lanzará un error
        raise HTTPException(400,'Puede que el token haya expirado;Inicie sesión de nuevo') from e
    # Obtener el id
    user_id = payload['sub']
    # Comprobar que ha sido entregado un username
    if not user_id:
        raise HTTPException(400,"El token no contiene ningún username")
    # Devolver el username
    return user_id

@router.get("/me",response_model=User,status_code=200)
async def get_me(user_id: str = Depends(validate_token)):
    """Obtener los datos personales"""
    # Obtener el usuario de la base de datos
    user_db = get_user_by('_id',ObjectId(user_id))
    # Comprobar que el username sea correcto
    if not user_db:
        raise HTTPException(404,'Usuario no encontrado')
    # Convertirlo a un schema y devolverlo
    return user_schema(user_db)

@router.put("/me/update",status_code=200)
async def put_me_update(user_new: UserPut,user_id: str = Depends(validate_token)):
    """Función para actualizar los datos del usuario"""
    user_objid = ObjectId(user_id)
    # Si el usuario no existe, enviar un error
    if not check_if_user_exist('_id',user_objid):
        raise HTTPException(404,'Usuario no encontrado')
    # Obtener los datos del usuario que no sean none
    purified_data = purify_dict(user_new.model_dump())
    # Actualizar el documento
    replaced_user = user_collection.find_one_and_update(
        { '_id': user_objid },
        {"$set":purified_data},
        return_document=ReturnDocument.AFTER)
    # Devolver el usuario con los datos actualizados
    return user_schema(replaced_user)
