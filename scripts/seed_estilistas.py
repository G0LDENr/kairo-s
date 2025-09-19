import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import users_col
from faker import Faker
from datetime import datetime
import random
from auth.authentication import hash_password  # Importar la función de hashing

fake = Faker("es_MX")

sexos = ["M", "F"]
dominios = ["gmail.com", "hotmail.com"]

usuarios = []

for _ in range(5000):
    nombre_completo = f"{fake.first_name()} {fake.last_name()} {fake.last_name()}"
    correo = f"{fake.user_name()}{random.randint(100,999)}@{random.choice(dominios)}"
    telefono = fake.msisdn()[:10]
    contraseña_plana = fake.password(length=10)
    contraseña_hash = hash_password(contraseña_plana)  # Hashear la contraseña
    
    usuario = {
        "nombre": nombre_completo,
        "correo": correo,
        "contraseña": contraseña_hash,  # Guardar el hash en lugar del texto plano
        "telefono": telefono,
        "sexo": random.choice(sexos),
        "role": "cliente",
        "fecha_registro": datetime.now()
    }
    usuarios.append(usuario)

users_col.insert_many(usuarios)
print("✅ 5000 usuarios de prueba insertados correctamente.")