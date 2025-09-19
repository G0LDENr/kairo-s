import bcrypt
from bson.binary import Binary
from database.config import users_col
from datetime import datetime

def hash_password(password: str) -> Binary:
    # Convertir a Binary para almacenamiento eficiente en MongoDB
    return Binary(bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()))

def check_password(password: str, password_hash: Binary) -> bool:
    # password_hash es un objeto Binary, necesitamos extraer los bytes
    return bcrypt.checkpw(password.encode('utf-8'), password_hash)

def register_user(nombre, correo, password, telefono, sexo, role="cliente"):
    if not nombre or not correo or not password:
        return False, "Todos los campos requeridos"
    if users_col.find_one({"correo": correo}):
        return False, "El correo ya está registrado"
    phash = hash_password(password)
    users_col.insert_one({
        "nombre": nombre,
        "correo": correo,
        "contraseña": phash,
        "telefono": telefono,
        "sexo": sexo,
        "role": role,
        "fecha_registro": datetime.now()
    })
    return True, "Usuario registrado exitosamente"

def authenticate_user(correo, password):
    user = users_col.find_one({"correo": correo})
    if not user:
        return None
    if check_password(password, user["contraseña"]):
        return user
    return None