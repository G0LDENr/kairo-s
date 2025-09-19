import os
import pymongo

# Configuración MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = pymongo.MongoClient(MONGO_URI)
db = client["kairos"]

# Colecciones
users_col = db["users"]
citas_col = db["citas"]
estilistas_col = db["estilistas"]
servicios_col = db["servicios"]
mensajes_col = db["mensajes"]