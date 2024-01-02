"""Cliente para conectarnos a mongodb"""

from os import getenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Establecer el dotenv para poder acceder a las variabled de entorno
load_dotenv()

# Instancia del cliente de mongodb
# Obtener la uri de la base de datos
DB_URI = getenv('DB_URI')
# Si hay uri,conectarse a la db en el atlas
if DB_URI:
    client = MongoClient(DB_URI,server_api=ServerApi('1'))
else:  # si no hay uri, conectarse a una base de datos local
    client = MongoClient()
# Comprobar que la conexión haya sido realizada correctamente
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
# Obtener la base de datos
DB = client[getenv('DB_NAME')]
