"""Atenticación y autorización: Seguridad en la API usando JWT"""
from datetime import datetime,timedelta
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from jose import jwt, JWTError
from passlib.context import CryptContext
# Instancia de la API / servicio de recursos
app = FastAPI()
# CONSTANTS
# Ruta en la que se encontrará la función de autenticación
AUTH_PATH = 'login'
# Secreto del JWT (generado con openssl rand -hex 32)
JWT_SECRET = '419ca618d56a580530132fba9d44ebd271ead4df1215aa46cf25c1e55c347634'
# Duración del JWT
JWT_DURATION = 1
# Algoritmo de encriptado
ALG = "HS256"
# Instancia de el servicio de autenticación/autorización
oauth2 = OAuth2PasswordBearer(tokenUrl=AUTH_PATH)
# Contexto de encriptado bcrypt
crypto = CryptContext(schemes=['bcrypt'])

# Clases para el manejo de la db y de los datos pasados por el usuario


class UserGet(BaseModel):
    """Datos del usuario que se podrán mostrar"""
    name: str
    username: str


class UserData(UserGet):
    """Datos de entrada del usuario"""
    password: str


class User(UserData):
    """Usuario que se almacenará en la base de datos"""
    # Contiene datos añadidos desde el backend y que el usuario en sí no podrá modificar
    disabled: bool


class Token(BaseModel):
    """Clase que define como será el token"""
    access_token: str
    token_type: str

# BASE DE DATOS SIMULATORIA
users_db = [
    User(name="jlop", username='jlopy',
         password=crypto.hash('12345'), disabled=False),
    User(name="Antonino", username='Nino',
         password=crypto.hash('6789'), disabled=True),
    User(name="Pepe", username='Portugués',
         password=crypto.hash('13579'), disabled=False),
    User(name="Tomás", username='Cencerro',
         password=crypto.hash('02468'), disabled=True),
    User(name="Adam", username='Smith',
         password=crypto.hash('014569'), disabled=False),
]


def search_user(username: str):
    """Función para obtener un usuario"""
    user_ls = [user for user in users_db if user.username == username]
    if not user_ls:
        return False
    return user_ls[0]


def password_check(db_password: str, input_password):
    """Función para comprobar la coincidencia de las contraseñas"""
    return crypto.verify(input_password, db_password)


@app.get("/users")
async def users():
    """Función para obtener todos los usuarios"""
    users_db_nopassword = [
        UserGet(name=user.name, username=user.username) for user in users_db]
    return users_db_nopassword


@app.get("/user/{username}", status_code=200, response_model=UserGet)
async def get_user(username: str):
    """GET user a partir del username"""
    user = search_user(username)
    if not user:
        raise HTTPException(
            404, f"Usuario con el username {username} no encontrado")
    return UserGet(name=user.name, username=user.username)


@app.post("/user", status_code=200)
async def user_post(user: UserData):
    """Función para añadir un usuario"""
    # Obtener el usuario de la base de datos que tiene los datos ingresados
    if search_user(user.username):
        raise HTTPException(409, f'El usuario {user.username} ya existe')
    # Si no existe un usuario con el username, crearlo
    user_to_db = User(**user.dict(), disabled=False)
    users_db.append(user_to_db)
    return user_to_db


@app.post(f"/{AUTH_PATH}")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    """Función para iniciar sesión"""
    # Obtener los datos del usuario
    user_db = search_user(form.username)
    # Comprobar si el usuario ya existe O si la contraseña es correcta
    if not user_db or not password_check(user_db.password, form.password):
        raise HTTPException(401, "No estás autorizado")
    # access token
    # Para la expiración se usa datetime.utcnow() y no datetime.now() para que no se
    # pueda engañar al sistema camiando la hora, pues UTC es universal y no depende del sistema
    access_token = {
        "sub":form.username, # Subject
        "exp": datetime.utcnow() + timedelta(minutes=JWT_DURATION) # Expiration time
    }
    # Devolver el token
    return Token(access_token=jwt.encode(access_token, JWT_SECRET, ALG), token_type='bearer')


def auth_token(token: str = Depends(oauth2)):
    """Función para autenticar el token"""
    try:
        # Descodificar el token
        decoded_token = jwt.decode(token, JWT_SECRET, ALG)
    except JWTError as err:
        raise HTTPException(401,"Las credenciales no son correctas;Haz login de nuevo") from err
    # Obtener el usuario en el token
    return decoded_token.get('sub')

def current_user(username: str = Depends(auth_token)):
    """Función para obtener el usuario propio"""
    user = search_user(username)
    # Comprobar que el usuario exista en la base de datos
    if not user:
        raise HTTPException(404,"El usuario no se encuentra en la base de datos")
    # Comprobar si el usuario está deshabilitado
    if user.disabled:
        raise HTTPException(401,"Usuario deshabilitado")
    return user


@app.get("/users/me")
async def get_me(user: User = Depends(current_user)):
    """Función para operar con el propio usuario"""
    return user
