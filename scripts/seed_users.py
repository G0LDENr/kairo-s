import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import users_col
# Removemos la importación de hash_password
from faker import Faker
from datetime import datetime
import random
from tqdm import tqdm  # Para la barra de progreso (opcional)

fake = Faker("es_MX")

sexos = ["M", "F"]
dominios = ["gmail.com", "hotmail.com"]

def generar_usuarios_masivo(cantidad=5000):
    """Genera usuarios de prueba con contraseñas en texto plano"""
    print(f"🚀 Generando {cantidad} usuarios con contraseñas en texto plano...")
    
    usuarios = []
    batch_size = 1000  # Insertar en lotes para mejor rendimiento
    
    # Usar tqdm para barra de progreso (opcional: pip install tqdm)
    for i in tqdm(range(cantidad), desc="Creando usuarios"):
        nombre_completo = f"{fake.first_name()} {fake.last_name()} {fake.last_name()}"
        correo = f"{fake.user_name()}{random.randint(100,999)}@{random.choice(dominios)}"
        telefono = fake.msisdn()[:10]
        contraseña_plana = fake.password(length=10)
        
        # CONTRASEÑA EN TEXTO PLANO (sin encriptar)
        usuario = {
            "nombre": nombre_completo,
            "correo": correo,
            "contraseña": contraseña_plana,  # Texto plano
            "telefono": telefono,
            "sexo": random.choice(sexos),
            "role": "cliente",
            "fecha_registro": datetime.now()
        }
        usuarios.append(usuario)
        
        # Insertar por lotes para mejor rendimiento
        if len(usuarios) >= batch_size:
            users_col.insert_many(usuarios)
            usuarios = []
    
    # Insertar los últimos usuarios si quedan
    if usuarios:
        users_col.insert_many(usuarios)
    
    print(f"✅ {cantidad} usuarios creados con contraseñas en texto plano correctamente.")

if __name__ == "__main__":
    generar_usuarios_masivo(995000)