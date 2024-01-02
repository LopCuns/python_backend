"""Atenticación y autorización: Seguridad en la API"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel

# Instancia de la API / servicio de recursos
app = FastAPI()

# Instancia de el servicio de autenticación/autorización
AUTH_PATH = 'login'
oauth2 = OAuth2PasswordBearer(tokenUrl=AUTH_PATH)
# ENLACE A LA DOCUMENTACIÓN (https://oauth.net/2)
# OAUTH SIGUE EL SIGUIENTE ESQUEMA (mirar en "concept/images" el diagrama ilustrado)
# app -> user // La aplicación pide los datos al usuario a través de un FORM
# user -> app // El usuario envia los datos a través de un FORM (Authorization Grant)
# app -> Authorization Service // La app envia el Grant del usuario a autenticar
# Authorization Service -> app // EL servicion de autenticación le devuelve un access token a la app
# app -> Resource Service // La app envía el token al servicio de recursos
# Resource Service -> app // El servicio de recursos entrega información a la app
# Creación de la clase de usuario para definir los tipos de datos


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

# BASE DE DATOS SIMULATORIA
users_db = [
    User(name="jlop", username='jlopy', password='12345', disabled=False),
    User(name="Antonino", username='Nino', password='6789', disabled=True),
    User(name="Pepe", username='Portugués', password='13579', disabled=False),
    User(name="Tomás", username='Cencerro', password='02468', disabled=True),
    User(name="Adam", username='Smith', password='014569', disabled=False),
]


def search_user(username: str):
    """Función para obtener un usuario"""
    user_ls = [user for user in users_db if user.username == username]
    if not user_ls:
        return False
    return user_ls[0]

def encrypt(password:str):
    """función para encriptar la contraseña"""
    return f"__{password[::-1]}__"

def decrypt(password:str):
    """Función para desencriptar la contraseña"""
    return password[2:-2][::-1]

def password_check(db_password: str, input_password):
    """Función para comprobar la coincidencia de las contraseñas"""
    if db_password == input_password:
        return True
    return False


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

# EL token se obtiene a través del sistema de autenticación (oauth2), por lo que
# lo señalamos como dependencia
async def current_user(token: str = Depends(oauth2)):
    """Obtener el usuario a través del token"""
    # Obtener el token (username encriptado en este caso)
    # Obtener el username a partir del token
    username = decrypt(token)
    # Obtener el usuario por username
    user = search_user(username)
    # Si el usuario no existe, devolver un 401 unathorized
    if not user:
        raise HTTPException(401,'No estás autorizado',headers={"WWW-Authenticate":"Bearer"})
    # Ver si el usuario está deshabilitado
    if user.disabled:
        raise HTTPException(401,"Usuario deshabilitado")
    return user

@app.post(f"/{AUTH_PATH}")
# Es necesario indicar las dependencias aunque estén vacías
async def login(form: OAuth2PasswordRequestForm = Depends()):
    """Petición de token guard app-user -> auth_service-app"""
    # Obtener los datos del usuario
    user_db = search_user(form.username)
    # Comprobar si existe el usuario;de lo contrario mandar un 401 Unautorized
    if not search_user(form.username):
        raise HTTPException(401, 'No estás autorizado')
    # Comprobar la coincidencia de las constraseñas
    if not password_check(user_db.password, form.password):
        raise HTTPException(401, 'No estás autorizado')
    # Devolver el token
    return {"access_token": encrypt(form.username), "token_type": "bearer"}


@app.get("/users/me")
# El usser se obtiene por la validación del token, por lo que
# lo señalamos como dependencia
async def get_user_me(user: User = Depends(current_user)):
    """Función para obtener todos los datos del usuario
        Requiere autorización app-auth_service"""
    return user
