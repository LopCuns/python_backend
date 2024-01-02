"""Modelo de usuario de db"""

from models.user import User # pylint: disable=E0401


def user_schema(user_model) -> User:
    """Transformar el user que llega desde la db a un 
    usuario de nuestra app"""
    return User(
        id=str(user_model["_id"]),
        name=user_model["name"],
        username=user_model["username"],
        password=user_model["password"],
        email=user_model["email"],
        disabled=user_model["disabled"],
        created_at=user_model["created_at"]
    )

def user_schema_public(user_model):
    """Devolver los datos del user depurados (no password, no id)"""
    # Transformar los datos modelo -> esquema
    user = user_schema(user_model)
    # Recojer todos los datos menor el password y el id
    # Devolver los datos
    return user.model_dump(exclude={'password','id'})
